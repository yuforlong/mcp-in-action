import asyncio
from typing import Dict, List, Any, Optional, Union
from loguru import logger
import json

from app.mcp_client import MCPClient
from app.llm_client import LLMClient
from app.config import MAX_SEARCH_RESULTS

class KnowledgeRetriever:
    """Knowledge retriever for performing RAG queries against the knowledge base."""
    
    def __init__(self, max_search_results: int = MAX_SEARCH_RESULTS):
        """Initialize the knowledge retriever.
        
        Args:
            max_search_results: Maximum number of search results to return
        """
        self.max_search_results = max_search_results
        self.mcp_client = MCPClient()
        self.llm_client = LLMClient()
        logger.info(f"Initialized KnowledgeRetriever with max_search_results={max_search_results}")
        
    async def query(self, question: str) -> str:
        """Query the knowledge base and return an answer.
        
        Args:
            question: The question to answer
            
        Returns:
            The answer to the question
        """
        # Connect to MCP server if needed
        if not hasattr(self.mcp_client, '_connected') or not self.mcp_client._connected:
            await self.mcp_client.connect()
            
        # Step 1: Rewrite and decompose the question
        sub_questions = await self._decompose_question(question)
        logger.info(f"Decomposed question into {len(sub_questions)} sub-questions")
        
        # Step 2: Search for relevant content for each sub-question
        all_context = []
        
        for sub_q in sub_questions:
            # Search knowledge base
            try:
                knowledge_results = await self.mcp_client.search_knowledge(
                    query=sub_q,
                    size=self.max_search_results
                )
                all_context.extend([{"type": "knowledge", "content": item} for item in knowledge_results])
            except Exception as e:
                logger.error(f"Error searching knowledge base: {str(e)}")
                
            # Search FAQ base
            try:
                faq_results = await self.mcp_client.search_faq(
                    query=sub_q,
                    size=self.max_search_results
                )
                all_context.extend([{"type": "faq", "content": item} for item in faq_results])
            except Exception as e:
                logger.error(f"Error searching FAQ base: {str(e)}")
                
        # Step 3: Filter and rank the search results
        filtered_context = await self._filter_context(question, all_context)
        logger.info(f"Filtered {len(all_context)} context items to {len(filtered_context)}")
        
        # Step 4: Generate answer using filtered context
        answer = await self._generate_answer(question, filtered_context)
        
        return answer
        
    async def _decompose_question(self, question: str) -> List[str]:
        """Decompose a complex question into simpler sub-questions.
        
        Args:
            question: The question to decompose
            
        Returns:
            List of sub-questions
        """
        system_prompt = """你是一位问题分析专家。你的任务是将复杂问题分解为更简单的子问题，以便更好地检索相关信息。

请遵循以下规则：
1. 分析用户的问题，识别其中包含的不同方面或概念
2. 将复杂问题拆分成更简单、更具体的子问题
3. 确保子问题覆盖原始问题的所有关键方面
4. 提供2-4个子问题，具体数量取决于原始问题的复杂度
5. 子问题应该是明确的、有针对性的
6. 子问题之间应该尽量避免重复

输出格式必须是一个JSON数组，包含所有子问题的字符串，例如：
["子问题1", "子问题2", "子问题3"]

如果原始问题已经足够简单，不需要分解，则返回只包含原始问题的JSON数组：
["原始问题"]

只输出JSON格式，不要有任何其他文本。"""

        user_prompt = f"""请将以下问题分解为更简单的子问题以便检索：

{question}"""

        try:
            # Generate sub-questions
            response = self.llm_client.sync_generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.3
            )
            
            # Parse the response as JSON
            try:
                # Try to find JSON array in the response
                start_idx = response.find('[')
                end_idx = response.rfind(']') + 1
                
                if start_idx >= 0 and end_idx > start_idx:
                    json_str = response[start_idx:end_idx]
                    sub_questions = json.loads(json_str)
                    return sub_questions
                else:
                    logger.warning(f"No valid JSON found in LLM response, using original question")
                    return [question]
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON from LLM response: {str(e)}")
                return [question]
                
        except Exception as e:
            logger.error(f"Error decomposing question: {str(e)}")
            return [question]
            
    async def _filter_context(self, question: str, context_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter context items based on relevance to the question.
        
        Args:
            question: The original question
            context_items: List of context items from search
            
        Returns:
            Filtered list of context items
        """
        # Simple filtering: deduplication and truncation
        seen_contents = set()
        filtered_items = []
        
        # Prioritize FAQ types
        faq_items = [item for item in context_items if item["type"] == "faq"]
        knowledge_items = [item for item in context_items if item["type"] == "knowledge"]
        
        # Process FAQs first
        for item in faq_items:
            content_key = None
            if item["type"] == "faq":
                content = item["content"]
                content_key = f"faq:{content['question']}"
            
            if content_key and content_key not in seen_contents:
                seen_contents.add(content_key)
                filtered_items.append(item)
        
        # Then process knowledge items
        for item in knowledge_items:
            content_key = None
            if item["type"] == "knowledge":
                content = item["content"]
                content_key = f"knowledge:{content['content'][:100]}"  # Use first 100 chars as key
            
            if content_key and content_key not in seen_contents:
                seen_contents.add(content_key)
                filtered_items.append(item)
        
        # Limit the total number of context items
        max_context_items = 6  # Adjusted based on context capacity
        if len(filtered_items) > max_context_items:
            filtered_items = filtered_items[:max_context_items]
            
        return filtered_items
        
    async def _generate_answer(self, question: str, context_items: List[Dict[str, Any]]) -> str:
        """Generate an answer based on the question and context.
        
        Args:
            question: The original question
            context_items: Filtered context items
            
        Returns:
            The generated answer
        """
        # Prepare context text
        context_text = ""
        
        # Add knowledge contents
        knowledge_items = [item for item in context_items if item["type"] == "knowledge"]
        if knowledge_items:
            context_text += "【知识库内容】\n"
            for i, item in enumerate(knowledge_items, 1):
                content = item["content"]["content"]
                context_text += f"{i}. {content}\n\n"
                
        # Add FAQ contents
        faq_items = [item for item in context_items if item["type"] == "faq"]
        if faq_items:
            context_text += "【FAQ内容】\n"
            for i, item in enumerate(faq_items, 1):
                question = item["content"]["question"]
                answer = item["content"]["answer"]
                context_text += f"{i}. 问: {question}\n   答: {answer}\n\n"
                
        # If no context was found
        if not context_text:
            return "抱歉，我没有找到与您问题相关的信息。请尝试用不同的方式提问，或者提供更多的上下文信息。"
            
        # Prepare system prompt
        system_prompt = """你是一个专业的问答助手。你的任务是基于提供的上下文信息，回答用户的问题。请遵循以下规则：

1. 仔细阅读上下文中提供的所有信息。
2. 只使用上下文中的信息来回答问题，不要添加未在上下文中提及的信息。
3. 如果上下文中没有足够的信息回答问题，诚实地表明你无法基于给定信息回答。
4. 提供全面、准确且简洁的回答。
5. 当引用上下文中的事实时，尽可能保持原文的准确性。
6. 不要在回答中直接引用"上下文"或"知识库"这样的词语。
7. 回答应该流畅自然，像是直接回应用户的问题。
8. 如果问题涉及多个方面，确保你的回答涵盖所有相关方面。"""

        user_prompt = f"""基于以下上下文信息，请回答问题：

{context_text}

问题：{question}"""

        try:
            # Generate answer
            response = self.llm_client.sync_generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.5
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            return "抱歉，在生成回答时发生了错误。请稍后再试。" 