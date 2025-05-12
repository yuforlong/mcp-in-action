from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class KnowledgeContent(BaseModel):
    """The document stored in knowledge store for later retrieval."""
    content: str = Field(..., description="a natural language document content")
    meta_data: Dict[str, Any] = Field(default_factory=dict, description="a dictionary with strings as keys, which can store some meta data related to this document")


class SearchKnowledgeQuery(BaseModel):
    """The query request to search similar documents from knowledge store"""
    query: str = Field(..., description="describe what you're looking for, and the tool will return the most relevant documents")
    size: int = Field(default=20, description="the number of similar documents to be returned")


class FAQContent(BaseModel):
    """The document stored in FAQ store for later retrieval."""
    question: str = Field(..., description="a natural language document content")
    answer: str = Field(..., description="a natural language document content")


class SearchFAQQuery(BaseModel):
    """The query request to search similar documents from faq store"""
    query: str = Field(..., description="describe what you're looking for, and the tool will return the most relevant documents")
    size: int = Field(default=20, description="the number of similar documents to be returned")


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPTools(BaseModel):
    """MCP Tools response"""
    tools: List[MCPTool] 