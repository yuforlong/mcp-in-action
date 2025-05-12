import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Milvus configuration
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))

# Embedding model configuration
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")  # Default to all-MiniLM-L6-v2
VECTOR_DIMENSION = int(os.getenv("VECTOR_DIMENSION", "384"))  # Default to 384 for all-MiniLM-L6-v2

# Collection names
KNOWLEDGE_COLLECTION = os.getenv("KNOWLEDGE_COLLECTION", "knowledge_store")
FAQ_COLLECTION = os.getenv("FAQ_COLLECTION", "faq_store")

# Fields
TEXT_FIELD = "text"
VECTOR_FIELD = "embedding"
FAQ_QUESTION_FIELD = "question"
FAQ_ANSWER_FIELD = "answer"
METADATA_FIELD = "metadata" 