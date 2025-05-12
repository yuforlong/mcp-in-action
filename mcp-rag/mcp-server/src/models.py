from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class KnowledgeContent(BaseModel):
    """The document stored in knowledge store for later retrieval."""
    content: str = Field(..., description="a natural language document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="a dictionary with strings as keys, which can store some meta data related to this document")


class SearchResult(BaseModel):
    """Search result model"""
    content: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self):
        return {
            "content": self.content,
            "score": self.score,
            "metadata": self.metadata
        }


class FAQContent(BaseModel):
    """The document stored in FAQ store for later retrieval."""
    question: str = Field(..., description="a natural language document content")
    answer: str = Field(..., description="a natural language document content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="a dictionary with strings as keys, which can store some meta data related to this document")


class FAQSearchResult(BaseModel):
    """FAQ search result model"""
    question: str
    answer: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def dict(self):
        return {
            "question": self.question,
            "answer": self.answer,
            "score": self.score,
            "metadata": self.metadata
        }


class MCPTool(BaseModel):
    """MCP Tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPTools(BaseModel):
    """MCP Tools response"""
    tools: List[MCPTool] 