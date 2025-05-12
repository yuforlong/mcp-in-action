from pydantic_settings import BaseSettings
from typing import Optional

class MilvusSettings(BaseSettings):
    """Milvus connection and collection settings"""
    HOST: str = "localhost"
    PORT: int = 19530
    VECTOR_DIMENSION: int = 384
    KNOWLEDGE_COLLECTION: str = "knowledge_store"
    FAQ_COLLECTION: str = "faq_store"
    
class EmbeddingProviderSettings(BaseSettings):
    """Embedding model settings"""
    MODEL: str = "all-MiniLM-L6-v2"
    BATCH_SIZE: int = 32  # Batch size for embedding generation
    
class PerformanceSettings(BaseSettings):
    """Performance optimization settings"""
    CACHE_SIZE: int = 1024  # Cache size in MB
    NUM_WORKERS: int = 4  # Number of worker processes
    BATCH_PROCESSING_SIZE: int = 100  # Batch size for processing documents
    MAX_CONNECTION_POOL_SIZE: int = 10  # Maximum number of connections in the pool
    
class ServerSettings(BaseSettings):
    """Server configuration settings"""
    HOST: str = "0.0.0.0"
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"
    
class ResourceLimitSettings(BaseSettings):
    """Resource limitation settings"""
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT: int = 300  # seconds

class ToolSettings(BaseSettings):
    """Tool descriptions for MCP"""
    TOOL_STORE_KNOWLEDGE_DESCRIPTION: str = "Store document into knowledge store for later retrieval."
    TOOL_SEARCH_KNOWLEDGE_DESCRIPTION: str = "Search for similar documents on natural language descriptions from knowledge store."
    TOOL_STORE_FAQ_DESCRIPTION: str = "Store document into FAQ store for later retrieval."
    TOOL_SEARCH_FAQ_DESCRIPTION: str = "Search for similar documents on natural language descriptions from FAQ store."
    
    class Config:
        env_prefix = "TOOL_"

# Initialize settings objects
milvus_settings = MilvusSettings()
embedding_settings = EmbeddingProviderSettings()
performance_settings = PerformanceSettings()
server_settings = ServerSettings()
resource_settings = ResourceLimitSettings()
tool_settings = ToolSettings()

# For backward compatibility
settings = ServerSettings() 