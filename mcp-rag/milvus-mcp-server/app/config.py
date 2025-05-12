from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Milvus Configuration
    MILVUS_HOST: str = "localhost"
    MILVUS_PORT: int = 19530
    VECTOR_DIMENSION: int = 384
    KNOWLEDGE_COLLECTION: str = "knowledge_store"
    FAQ_COLLECTION: str = "faq_store"
    
    # Model Configuration
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_BATCH_SIZE: int = 32  # Batch size for embedding generation
    MAX_CONNECTION_POOL_SIZE: int = 10  # Maximum number of connections in the pool
    
    # Performance Optimization
    CACHE_SIZE: int = 1024  # Cache size in MB
    NUM_WORKERS: int = 4  # Number of worker processes
    BATCH_PROCESSING_SIZE: int = 100  # Batch size for processing documents
    
    # API Configuration
    PORT: int = 8080
    LOG_LEVEL: str = "INFO"
    
    # Resource Limits
    MAX_REQUEST_SIZE: int = 10 * 1024 * 1024  # 10MB
    REQUEST_TIMEOUT: int = 300  # seconds
    
    class Config:
        env_file = ".env"

settings = Settings() 