# Milvus MCP Client

基于 Milvus 向量数据库的 MCP（模型上下文协议）客户端的 Python 实现。

## 功能概述

Milvus MCP Client 提供了与 Milvus MCP Server 交互的客户端能力，通过 MCP 协议与大模型进行交互，实现以下功能：

1. **知识库构建**：
   - 文本切段：对长文本进行切段，保证文本完整性和语义完整性
   - 提取 FAQ：根据文本内容自动提取 FAQ
   - 导入知识库：将文本和 FAQ 导入到 Milvus 向量数据库中

2. **知识检索（RAG）**：
   - 问题拆解：对用户问题进行拆解和重写，拆解为更原子的子问题
   - 检索：对每个子问题分别检索相关文本和 FAQ
   - 知识库内容筛选：筛选检索内容，保留最相关的内容进行回答

## 环境要求

- Python 3.10+
- 已部署并启动的 Milvus MCP Server

## 安装与配置

1. 克隆项目并进入目录：
```bash
cd milvus-mcp-client
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件，添加以下配置：
```
# MCP服务器配置
MCP_SERVER_URL=http://localhost:8080/sse

# LLM API配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_BASE=your_openai_api_base_url  # 可选，适用于自建API服务
OPENAI_MODEL=qwen2-72b-instruct  # 或其他通过OpenAI API访问的Qwen模型名称

# 日志级别
LOG_LEVEL=INFO
```

## 使用方式

### 运行示例

```bash
# 构建知识库
python -m app.main build --file path/to/your/document.txt

# 基于知识库进行问答
python -m app.main query --question "您的问题"
```

## API参考

### 知识库构建
```python
from app.knowledge_builder import KnowledgeBuilder

# 初始化知识库构建器
builder = KnowledgeBuilder()

# 从文件构建知识库
builder.build_from_file("path/to/your/document.txt")

# 从文本构建知识库
builder.build_from_text("您的文本内容")
```

### 知识检索与问答
```python
from app.knowledge_retriever import KnowledgeRetriever

# 初始化知识检索器
retriever = KnowledgeRetriever()

# 提问并获取回答
answer = retriever.query("您的问题")
print(answer)
```

## 与Milvus MCP Server的集成

本客户端通过 MCP 协议与 Milvus MCP Server 进行通信，使用 Server 提供的以下工具：

1. `storeKnowledge`: 存储文本到知识库
2. `searchKnowledge`: 在知识库中搜索相似文档
3. `storeFAQ`: 存储FAQ到FAQ库
4. `searchFAQ`: 在FAQ库中搜索相似问答对

## 许可证

MIT License 