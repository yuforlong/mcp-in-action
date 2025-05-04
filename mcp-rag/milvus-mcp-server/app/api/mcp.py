from fastapi import APIRouter, Depends
from typing import List
from pydantic import json_schema

from app.models.models import (
    KnowledgeContent, 
    SearchKnowledgeQuery, 
    FAQContent, 
    SearchFAQQuery,
    MCPTools,
    MCPTool
)
from app.services.milvus_service import MilvusService
from app.dependencies import get_milvus_service_dependency

# 创建API路由，前缀为"/api/v1"
router = APIRouter(prefix="/api/v1")


def get_tools() -> MCPTools:
    """Get the available MCP tools.
    
    Returns:
        The tools response object
        
    获取可用的MCP工具。
    
    返回:
        工具响应对象
    """
    tools = [
        MCPTool(
            name="storeKnowledge",
            description="Store document into knowledge store for later retrieval.",
            input_schema=json_schema.model_json_schema(KnowledgeContent)
        ),
        MCPTool(
            name="searchKnowledge",
            description="Search for similar documents on natural language descriptions from knowledge store.",
            input_schema=json_schema.model_json_schema(SearchKnowledgeQuery)
        ),
        MCPTool(
            name="storeFAQ",
            description="Store document into FAQ store for later retrieval.",
            input_schema=json_schema.model_json_schema(FAQContent)
        ),
        MCPTool(
            name="searchFAQ",
            description="Search for similar documents on natural language descriptions from FAQ store.",
            input_schema=json_schema.model_json_schema(SearchFAQQuery)
        )
    ]
    return MCPTools(tools=tools)


@router.get("/tools")
async def tools() -> MCPTools:
    """Get the available MCP tools.
    
    Returns:
        The tools response
        
    获取可用的MCP工具。
    
    返回:
        工具响应
    """
    return get_tools()


@router.post("/storeKnowledge", status_code=201)
async def store_knowledge(
    content: KnowledgeContent,
    milvus_service: MilvusService = Depends(get_milvus_service_dependency)
) -> None:
    """Store a document in the knowledge store.
    
    Args:
        content: The knowledge content to store
        milvus_service: The Milvus service
        
    在知识库中存储文档。
    
    参数:
        content: 要存储的知识内容
        milvus_service: Milvus服务对象
    """
    milvus_service.store_knowledge(content)


@router.post("/searchKnowledge")
async def search_knowledge(
    query: SearchKnowledgeQuery,
    milvus_service: MilvusService = Depends(get_milvus_service_dependency)
) -> List[KnowledgeContent]:
    """Search for documents in the knowledge store.
    
    Args:
        query: The search query
        milvus_service: The Milvus service
        
    Returns:
        List of matching documents
        
    在知识库中搜索文档。
    
    参数:
        query: 搜索查询
        milvus_service: Milvus服务对象
        
    返回:
        匹配文档的列表
    """
    return milvus_service.search_knowledge(query.query, query.size)


@router.post("/storeFAQ", status_code=201)
async def store_faq(
    content: FAQContent,
    milvus_service: MilvusService = Depends(get_milvus_service_dependency)
) -> None:
    """Store an FAQ in the FAQ store.
    
    Args:
        content: The FAQ content to store
        milvus_service: The Milvus service
        
    在FAQ库中存储常见问题。
    
    参数:
        content: 要存储的FAQ内容
        milvus_service: Milvus服务对象
    """
    milvus_service.store_faq(content)


@router.post("/searchFAQ")
async def search_faq(
    query: SearchFAQQuery,
    milvus_service: MilvusService = Depends(get_milvus_service_dependency)
) -> List[FAQContent]:
    """Search for FAQs in the FAQ store.
    
    Args:
        query: The search query
        milvus_service: The Milvus service
        
    Returns:
        List of matching FAQs
        
    在FAQ库中搜索常见问题。
    
    参数:
        query: 搜索查询
        milvus_service: Milvus服务对象
        
    返回:
        匹配FAQ的列表
    """
    return milvus_service.search_faq(query.query, query.size) 