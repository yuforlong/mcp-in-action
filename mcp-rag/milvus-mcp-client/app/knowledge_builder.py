import os
import asyncio
from typing import Dict, List, Any, Optional, Union
from loguru import logger

from app.mcp_client import MCPClient
from app.llm_client import LLMClient
from app.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class KnowledgeBuilder:
    """Knowledge builder for processing and storing documents in the knowledge base."""
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ):
        """Initialize the knowledge builder.
        
        Args:
            chunk_size: The size of text chunks
            chunk_overlap: The overlap between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.mcp_client = MCPClient()
        self.llm_client = LLMClient()
        logger.info(f"Initialized KnowledgeBuilder with chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        
    async def build_from_text(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None,
        extract_faq: bool = True
    ) -> Dict[str, Any]:
        """Build knowledge base from text.
        
        Args:
            text: The text content
            metadata: Optional metadata for the document
            extract_faq: Whether to extract FAQs from the text
            
        Returns:
            Dictionary with processing results
        """
        # Connect to MCP server
        if not hasattr(self.mcp_client, '_connected') or not self.mcp_client._connected:
            await self.mcp_client.connect()
            
        # Process text into chunks
        chunks = self._chunk_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # Store chunks in knowledge base
        stored_count = 0
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            
            # Store chunk in knowledge base
            try:
                await self.mcp_client.store_knowledge(content=chunk, metadata=chunk_metadata)
                stored_count += 1
            except Exception as e:
                logger.error(f"Failed to store chunk {i}: {str(e)}")
                
        # Extract and store FAQs if requested
        faqs = []
        if extract_faq:
            faqs = await self._extract_faqs(text)
            logger.info(f"Extracted {len(faqs)} FAQs from text")
            
            # Store FAQs
            for faq in faqs:
                try:
                    await self.mcp_client.store_faq(
                        question=faq["question"],
                        answer=faq["answer"],
                        metadata=metadata
                    )
                except Exception as e:
                    logger.error(f"Failed to store FAQ: {str(e)}")
                    
        return {
            "stored_chunks": stored_count,
            "total_chunks": len(chunks),
            "extracted_faqs": len(faqs),
            "faqs": faqs
        }
        
    async def build_from_file(
        self, 
        file_path: str, 
        metadata: Optional[Dict[str, Any]] = None,
        extract_faq: bool = True
    ) -> Dict[str, Any]:
        """Build knowledge base from file.
        
        Args:
            file_path: Path to the file
            metadata: Optional metadata for the document
            extract_faq: Whether to extract FAQs from the text
            
        Returns:
            Dictionary with processing results
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # Add file metadata if not provided
        if metadata is None:
            metadata = {}
        
        metadata["file_name"] = os.path.basename(file_path)
        metadata["file_path"] = file_path
        metadata["file_size"] = os.path.getsize(file_path)
        
        # Process the file content
        return await self.build_from_text(text, metadata, extract_faq)
    
    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks with overlap.
        
        Args:
            text: The text to split
            
        Returns:
            List of text chunks
        """
        # Simple character-based chunking
        chunks = []
        
        # Trivial case: text is smaller than chunk size
        if len(text) <= self.chunk_size:
            chunks.append(text)
            return chunks
            
        # Split into chunks with overlap
        start = 0
        while start < len(text):
            # Get chunk end position
            end = start + self.chunk_size
            
            # Adjust end to not cut in the middle of a sentence if possible
            if end < len(text):
                # Look for sentence boundaries (period, question mark, exclamation mark)
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('! ', start, end)
                )
                
                # If found a sentence end, use it as chunk end
                if sentence_end > start:
                    end = sentence_end + 1  # Include the period
            
            # Add chunk
            chunks.append(text[start:min(end, len(text))])
            
            # Move start position for next chunk, considering overlap
            start = end - self.chunk_overlap
            
            # Ensure progress is made
            if start >= len(text) or start <= 0:
                break
                
        return chunks
        
    async def _extract_faqs(self, text: str) -> List[Dict[str, str]]:
        """Extract FAQs from text using LLM.
        
        Args:
            text: The text to extract FAQs from
            
        Returns:
            List of extracted FAQs
        """
        # If text is too long, split it and extract FAQs from each part
        if len(text) > 8000:
            chunks = self._chunk_text(text)
            faqs = []
            for chunk in chunks:
                chunk_faqs = await self._extract_faqs(chunk)
                faqs.extend(chunk_faqs)
            return faqs
            
        # Prompt template for FAQ extraction
        system_prompt = """你是一位专业的知识提取专家。你的任务是从文本中提取可能的常见问题(FAQ)。这些问题应该是用户可能会问的关于文本内容的自然问题，答案应该能在文本中找到。提取的FAQ应该覆盖文本中最重要的概念和信息。

请遵循以下规则：
1. 每个FAQ由一个问题和一个答案组成
2. 问题应该简短明了，直接针对主题
3. 答案应该全面但简洁，提供文本中的相关信息
4. 提取的FAQ数量应该基于文本长度和内容丰富度，通常不超过10个
5. 确保提取的FAQ相互之间不重复
6. 按照重要性排序，最重要的问题应该放在前面

输出格式必须是一个JSON数组，每个FAQ是一个包含"question"和"answer"字段的对象，例如：
[
  {
    "question": "问题1?",
    "answer": "答案1"
  },
  {
    "question": "问题2?",
    "answer": "答案2"
  }
]
只输出JSON格式，不要有任何其他文本。"""

        user_prompt = f"""从以下文本中提取常见问题(FAQ)：

```
{text}
```

请提取最相关、最有价值的FAQ，并按JSON格式返回。"""

        try:
            # Generate FAQs
            response = self.llm_client.sync_generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            # Parse the response as JSON
            import json
            try:
                # Try to find JSON array in the response
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    faqs = json.loads(json_str)
                    return faqs
                else:
                    logger.error(f"No valid JSON found in LLM response: {response}")
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
                return []
                
        except Exception as e:
            logger.error(f"Error extracting FAQs: {str(e)}")
            return [] 