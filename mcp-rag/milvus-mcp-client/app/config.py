"""
Milvus MCP 客户端配置文件
功能：定义MCP客户端的全局配置参数
作用：加载环境变量，配置日志系统，设置默认参数
主要配置项：
1. MCP服务器URL配置
2. LLM API配置（使用OpenAI兼容接口）
3. 日志系统配置
4. 知识库分块和检索参数配置
5. MCP工具定义
"""
import os
import sys
from dotenv import load_dotenv
from loguru import logger

# 从.env文件加载环境变量
load_dotenv()

# MCP服务器配置
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

# LLM API配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")

# 配置日志系统
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger.remove()
logger.add(
    sink=sys.stdout,
    level=LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# 知识库配置参数
DEFAULT_CHUNK_SIZE = int(os.getenv("DEFAULT_CHUNK_SIZE", "1000"))  # 默认文本分块大小
DEFAULT_CHUNK_OVERLAP = int(os.getenv("DEFAULT_CHUNK_OVERLAP", "200"))  # 默认分块重叠大小
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))  # 默认最大检索结果数

# 定义MCP服务器可用的工具
TOOLS = {
    "storeKnowledge": "将文档存储到知识库中以便日后检索",
    "searchKnowledge": "在知识库中搜索相似文档",
    "storeFAQ": "将文档存储到常见问题解答库中以便日后检索",
    "searchFAQ": "在常见问题解答库中搜索相似文档"
} 