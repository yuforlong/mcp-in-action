import os
import sys
from dotenv import load_dotenv
from loguru import logger

# Load environment variables from .env file
load_dotenv()

# MCP Server configuration
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")

# LLM API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "sk-paSHgQoVeKag1rou9d81Fa2f534940C1Ba394f02C45aF3D2")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE", "https://vip.apiyi.com/v1")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "qwen3-32b")

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(
    sink=sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# Knowledge base configuration
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

# Define the tools available from the MCP server
TOOLS = {
    "storeKnowledge": "将文档存储到知识库中以便日后检索",
    "searchKnowledge": "在知识库中搜索相似文档",
    "storeFAQ": "将文档存储到常见问题解答库中以便日后检索",
    "searchFAQ": "在常见问题解答库中搜索相似文档"
} 