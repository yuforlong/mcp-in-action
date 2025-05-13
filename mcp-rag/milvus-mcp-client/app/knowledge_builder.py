"""
知识库构建模块
功能：负责处理文档和构建向量知识库
作用：将文本内容切分、处理并存储到Milvus知识库，并提取文档中的常见问题(FAQ)
主要功能：
1. 文本切分：将长文本按照语义边界切分成较小的片段
2. 知识库存储：将文本片段存储到向量知识库中
3. FAQ提取：使用LLM从文本中自动提取常见问题和答案
4. 文件处理：读取文件并提取元数据
"""
import os
import asyncio
from typing import Dict, List, Any, Optional, Union
from loguru import logger

from app.mcp_client import MCPClient
from app.llm_client import LLMClient
from app.config import DEFAULT_CHUNK_SIZE, DEFAULT_CHUNK_OVERLAP

class KnowledgeBuilder:
    """知识库构建器，用于处理文档并将其存储到知识库中"""
    
    def __init__(
        self,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
        chunk_overlap: int = DEFAULT_CHUNK_OVERLAP
    ):
        """
        初始化知识库构建器
        
        参数:
            chunk_size: 文本块的大小
            chunk_overlap: 文本块之间的重叠大小
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
        """
        从文本构建知识库
        
        参数:
            text: 文本内容
            metadata: 文档的可选元数据
            extract_faq: 是否从文本中提取FAQ
            
        返回:
            包含处理结果的字典
        """
        # 连接到MCP服务器
        if not hasattr(self.mcp_client, '_connected') or not self.mcp_client._connected:
            await self.mcp_client.connect()
            
        # 将文本处理成块
        chunks = self._chunk_text(text)
        logger.info(f"Split text into {len(chunks)} chunks")
        
        # 将块存储到知识库中
        stored_count = 0
        for i, chunk in enumerate(chunks):
            chunk_metadata = metadata.copy() if metadata else {}
            chunk_metadata["chunk_index"] = i
            chunk_metadata["total_chunks"] = len(chunks)
            
            # 将块存储到知识库中
            try:
                await self.mcp_client.store_knowledge(content=chunk, metadata=chunk_metadata)
                stored_count += 1
            except Exception as e:
                logger.error(f"Failed to store chunk {i}: {str(e)}")
                
        # 如果需要，提取并存储FAQ
        faqs = []
        if extract_faq:
            faqs = await self._extract_faqs(text)
            logger.info(f"Extracted {len(faqs)} FAQs from text")
            
            # 存储FAQ
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
        """
        从文件构建知识库
        
        参数:
            file_path: 文件路径
            metadata: 文档的可选元数据
            extract_faq: 是否从文本中提取FAQ
            
        返回:
            包含处理结果的字典
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # 读取文件内容
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        # 如果未提供元数据，则添加文件元数据
        if metadata is None:
            metadata = {}
        
        metadata["file_name"] = os.path.basename(file_path)
        metadata["file_path"] = file_path
        metadata["file_size"] = os.path.getsize(file_path)
        
        # 处理文件内容
        return await self.build_from_text(text, metadata, extract_faq)
    
    def _chunk_text(self, text: str) -> List[str]:
        """
        将文本划分为带有重叠的块
        
        参数:
            text: 要划分的文本
            
        返回:
            文本块列表
        """
        # 简单的基于字符的分块
        chunks = []
        
        # 简单情况：文本小于块大小
        if len(text) <= self.chunk_size:
            chunks.append(text)
            return chunks
            
        # 划分为带有重叠的块
        start = 0
        while start < len(text):
            # 获取块的结束位置
            end = start + self.chunk_size
            
            # 调整结束位置，尽量不在句子中间切断
            if end < len(text):
                # 查找句子边界(句号、问号、感叹号)
                sentence_end = max(
                    text.rfind('. ', start, end),
                    text.rfind('? ', start, end),
                    text.rfind('! ', start, end)
                )
                
                # 如果找到句子结尾，将其作为块的结束
                if sentence_end > start:
                    end = sentence_end + 1  # 包括句号
            
            # 添加块
            chunks.append(text[start:min(end, len(text))])
            
            # 移动起始位置到下一个块，考虑重叠
            start = end - self.chunk_overlap
            
            # 确保有进展
            if start >= len(text) or start <= 0:
                break
                
        return chunks
        
    async def _extract_faqs(self, text: str) -> List[Dict[str, str]]:
        """
        使用LLM从文本中提取FAQ
        
        参数:
            text: 要提取FAQ的文本
            
        返回:
            提取的FAQ列表
        """
        # 如果文本太长，拆分并从每个部分提取FAQ
        if len(text) > 8000:
            chunks = self._chunk_text(text)
            faqs = []
            for chunk in chunks:
                chunk_faqs = await self._extract_faqs(chunk)
                faqs.extend(chunk_faqs)
            return faqs
            
        # FAQ提取的提示模板
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
            # 生成FAQ
            response = self.llm_client.sync_generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.2
            )
            
            # 将响应解析为JSON
            import json
            try:
                # 尝试在响应中查找JSON数组
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
            logger.error(f"Failed to extract FAQs: {str(e)}")
            return [] 