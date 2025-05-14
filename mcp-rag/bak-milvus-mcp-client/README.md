# Milvus MCP 客户端

基于 MCP（模型上下文协议）的 Milvus 知识库客户端，用于知识库的构建、检索和问答。

## 功能概述

该客户端实现了以下核心功能：

1. **知识库构建**：将文档（Markdown、PDF等）导入到 Milvus 向量数据库中，自动处理文本分块和FAQ生成。
2. **知识库检索**：基于语义相似度在知识库中查找相关内容。
3. **智能问答**：利用大模型和检索到的知识进行智能问答。

## 系统架构

客户端基于 MCP（模型上下文协议）实现，与 Milvus MCP 服务器交互。整体架构分为三部分：

1. **知识库**：
   - Knowledge Store：存储文本内容，支持向量检索
   - FAQ Store：存储问答对，支持向量检索

2. **MCP 服务器**：提供 4 个工具（Tools）
   - `storeKnowledge`：存储知识到 Knowledge Store
   - `searchKnowledge`：在 Knowledge Store 中检索知识
   - `storeFAQ`：存储 FAQ 到 FAQ Store
   - `searchFAQ`：在 FAQ Store 中检索 FAQ

3. **MCP 客户端**：
   - 与大模型交互
   - 通过 MCP 协议使用 Tools 完成知识库的构建、检索和问答

## 安装与配置

### 环境要求

- Python 3.8+
- Milvus MCP 服务器已启动（默认地址：http://localhost:8080/sse）
- 有效的大模型 API 密钥

### 安装依赖

1. 克隆代码库并进入目录：
```bash
cd mcp-rag/milvus-mcp-client
```

2. 创建虚拟环境（可选）：
```bash
cd ..
python -m venv env-mcp-rag
source env-mcp-rag/bin/activate  # Linux/Mac
# 或
.\env-mcp-rag\Scripts\activate  # Windows
```

3. 安装依赖：
```bash
cd milvus-mcp-client
pip install -r requirements.txt
```

### 配置

配置可以通过环境变量或 `.env` 文件设置：

```bash
# MCP服务器地址
MCP_SERVER_HOST=http://localhost:8080/sse

# 大模型API配置
LLM_API_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
LLM_MODEL=qwen-max
LLM_API_KEY=your_api_key_here

# 日志级别
LOG_LEVEL=INFO
```

## 使用方法

### 导入知识

导入Markdown文件到知识库：

```bash
./run.sh import path/to/document.md
```

或者使用Python直接调用：

```bash
python knowledge_manager.py import path/to/document.md
```

### PDF文件转换

将PDF文件转换为Markdown格式，然后可以导入到知识库：

```bash
./run.sh pdf2md path/to/document.pdf
./run.sh import path/to/document.md  # 转换后自动生成的markdown文件
```

### 知识库检索

搜索知识库中的内容：

```bash
./run.sh search "你的搜索查询"
```

### 基于知识库的问答

使用大模型结合知识库进行智能问答：

```bash
./run.sh chat "你的问题"
```

## 开发和扩展

### 代码结构

- `knowledge_manager.py`：主要功能实现，包括导入知识、检索和问答
- `client_config.py`：客户端配置和提示词模板
- `client_chunk.py`：文本分块工具
- `import_file.py`：文件导入工具
- `run.sh`：便捷运行脚本

### 自定义提示词

可以在 `client_config.py` 中修改各功能的提示词模板，调整知识库构建、检索和问答的行为。

## 常见问题

### 连接问题

如果无法连接到MCP服务器，请检查：
- Milvus MCP服务器是否已启动
- MCP_SERVER_HOST 环境变量是否设置正确
- 网络连接是否正常

### API密钥问题

如果遇到API调用失败，请检查：
- LLM_API_KEY 是否设置正确
- API密钥是否有效
- 模型是否可用

## 许可证

本项目遵循 Apache 2.0 许可证。 