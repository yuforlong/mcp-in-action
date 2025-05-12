import asyncio
import logging
from typing import Dict, Any, List
from mcp.server import FastMCP

from embedding import EmbeddingService
from milvus_connector import MilvusConnector
from models import KnowledgeContent, FAQContent
from settings import server_settings, tool_settings

logger = logging.getLogger(__name__)

# Initialize services
embedding_service = EmbeddingService()
milvus_connector = MilvusConnector(embedding_service)

# Initialize FastMCP server
mcp = FastMCP(
    name="milvus-mcp-server",
    host=server_settings.HOST,
    port=server_settings.PORT,
)


@mcp.tool(name="storeKnowledge", description=tool_settings.TOOL_STORE_KNOWLEDGE_DESCRIPTION)
async def store_knowledge(content: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Store knowledge content in Milvus."""
    try:
        knowledge_content = KnowledgeContent(
            content=content,
            metadata=metadata or {}
        )
        milvus_connector.store_knowledge(knowledge_content)
        return {"status": "success", "message": "Knowledge stored successfully"}
    except Exception as e:
        logger.error(f"Error storing knowledge: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool(name="searchKnowledge", description=tool_settings.TOOL_SEARCH_KNOWLEDGE_DESCRIPTION)
async def search_knowledge(query: str, size: int = 5) -> Dict[str, Any]:
    """Search knowledge content in Milvus."""
    try:
        results = milvus_connector.search_knowledge(query, size)
        return {
            "status": "success",
            "results": [result.dict() for result in results]
        }
    except Exception as e:
        logger.error(f"Error searching knowledge: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool(name="storeFAQ", description=tool_settings.TOOL_STORE_FAQ_DESCRIPTION)
async def store_faq(question: str, answer: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """Store FAQ content in Milvus."""
    try:
        content = FAQContent(
            question=question,
            answer=answer,
            metadata=metadata or {}
        )
        milvus_connector.store_faq(content)
        return {"status": "success", "message": "FAQ stored successfully"}
    except Exception as e:
        logger.error(f"Error storing FAQ: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool(name="searchFAQ", description=tool_settings.TOOL_SEARCH_FAQ_DESCRIPTION)
async def search_faq(query: str, size: int = 5) -> Dict[str, Any]:
    """Search FAQ content in Milvus."""
    try:
        results = milvus_connector.search_faq(query, size)
        return {
            "status": "success",
            "results": [result.dict() for result in results]
        }
    except Exception as e:
        logger.error(f"Error searching FAQ: {e}")
        return {"status": "error", "message": str(e)} 