# MCP In Action

![GitHub stars](https://img.shields.io/github/stars/FlyAIBox/mcp-in-action?style=social)
![GitHub forks](https://img.shields.io/github/forks/FlyAIBox/mcp-in-action?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/FlyAIBox/mcp-in-action?style=social)
![GitHub repo size](https://img.shields.io/github/repo-size/FlyAIBox/mcp-in-action)
![GitHub language count](https://img.shields.io/github/languages/count/FlyAIBox/mcp-in-action)
![GitHub top language](https://img.shields.io/github/languages/top/FlyAIBox/mcp-in-action)
![GitHub last commit](https://img.shields.io/github/last-commit/FlyAIBox/mcp-in-action?color=red)

## 简介

MCP In Action 是一个实战项目，旨在帮助开发者快速掌握 Model Context Protocol (MCP) 的开发与应用。本项目通过实际案例展示如何构建基于 MCP 的应用，使大语言模型能够与外部工具和数据源进行交互，从而增强模型的能力范围。

## 文档
1. [MCP实战入门：让AI模型获取实时天气信息](https://mp.weixin.qq.com/s/cJhHf7caaezehEff2GSY_A)
2. [MCP实战进阶：集成DeepSeek模型与MCP的天气信息助手](https://mp.weixin.qq.com/s/1YIYRVw8yF1zeeLtmnhtYQ)
3. [MCP实战高阶：借助LangChain快速打造MCP天气助手](https://mp.weixin.qq.com/s/Qq3C85Bi3NHDQ9MnnBZvZQ)
4. [RAG不好用？试试MCP这个“知识库优化大师”]()

## 项目架构

本仓库包含以下主要项目：

### 项目1：[mcp_opensource](https://github.com/FlyAIBox/mcp-in-action/tree/main/mcp_opensource)
这个项目展示了 MCP 的开源工具，平台等。

### 项目2：[mcp_demo](https://github.com/FlyAIBox/mcp-in-action/tree/main/mcp_demo)

这个项目展示了 MCP 的基础应用，通过搭建客户端-服务器架构，让 AI 模型能够访问实时天气信息。

#### 核心功能

- **MCP 服务器开发**：从零构建符合 MCP 规范的服务器
- **MCP 服务器调试**：提供调试方法和最佳实践
- **MCP 客户端开发**：实现与服务器通信的客户端
- **Sampling 实现**：展示如何利用 MCP 进行采样
- **Desktop 加载**：将 MCP 服务集成到桌面应用程序

#### MCP Server 进阶功能

- **Prompt 管理**：优化和管理模型提示
- **Resource 处理**：外部资源调用与管理
- **生命周期管理**：控制 MCP 服务的完整生命周期
- **LangChain 集成**：在 LangChain 框架中使用 MCP 服务器
- **云端部署**：将 MCP 服务部署到云端(阿里云/mcp.so)

### 项目3：[mcp_rag](https://github.com/FlyAIBox/mcp-in-action/tree/main/mcp_rag)

这个项目专注于将 MCP 与检索增强生成 (RAG) 技术结合，展示如何通过 MCP 实现更高级的知识检索和信息整合能力。


## MCP 开发指南

### MCP 服务器开发流程

1. **定义工具接口**：明确工具的功能和参数
2. **实现 MCP 协议**：遵循 MCP 规范实现请求响应机制
3. **配置运行环境**：设置服务器监听和处理机制
4. **测试与调试**：验证服务器功能正常

### MCP 客户端开发流程

1. **建立连接**：实现与 MCP 服务器的通信
2. **构造请求**：按照 MCP 规范创建请求
3. **处理响应**：解析和处理 MCP 服务器返回的数据
4. **错误处理**：实现健壮的错误处理机制

## 项目结构

```
mcp-in-action/
├── mcp_demo/              # 基础 MCP 示例项目
│   ├── server.py          # MCP 服务器实现
│   ├── client.py          # MCP 客户端示例
│   ├── tools/             # 工具集合
│   │   ├── weather.py     # 天气查询工具
│   │   └── ...
│   ├── utils/             # 工具函数
│   └── configs/           # 配置文件
├── mcp_rag/               # MCP RAG 项目
│   ├── server.py          # RAG 服务器实现
│   ├── client.py          # RAG 客户端
│   ├── indexer/           # 索引构建器
│   └── retriever/         # 检索实现
└── README.md              # 项目文档
```

## 核心概念

### Model Context Protocol (MCP)

MCP 是一个允许大语言模型与外部工具和服务进行通信的协议。它定义了模型与外部系统之间的标准化接口，使模型能够：

- 调用外部 API 和服务
- 获取实时数据
- 执行特定的功能和计算
- 返回结构化的响应

### MCP 的优势

- **能力扩展**：让模型具备超越其训练数据的能力
- **实时性**：访问最新的信息和数据
- **专业工具集成**：与已有的专业工具和服务整合
- **标准化**：提供统一的接口标准
- **安全性**：可控的权限和访问管理

## 最佳实践

### 服务器设计

- 实现健壮的错误处理
- 添加详细的日志记录
- 设计合理的超时机制
- 考虑并发请求处理

### 客户端实现

- 优化请求批处理
- 实现重试机制
- 缓存常用请求结果
- 处理不同类型的响应

### 安全性考虑

- 实现身份验证和授权
- 限制资源使用
- 监控异常请求
- 敏感数据处理

## 高级应用场景

- **定制化助手**：结合专有数据和工具创建行业特定的 AI 助手
- **知识库增强**：通过 RAG 实现动态知识更新和检索
- **多模态交互**：集成图像处理、音频分析等多模态能力
- **自动化工作流**：构建基于 MCP 的自动化业务流程

## 贡献指南

欢迎通过以下方式为项目做出贡献：

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

贡献是使开源社区成为学习、激励和创造的惊人之处。非常感谢你所做的任何贡献。如果你有任何建议或功能请求，请先开启一个议题讨论你想要改变的内容。

<a href='https://github.com/repo-reviews/repo-reviews.github.io/blob/main/create.md' target="_blank"><img alt='Github' src='https://img.shields.io/badge/review_me-100000?style=flat&logo=Github&logoColor=white&labelColor=888888&color=555555'/></a>


## 许可证
该项目根据Apache-2.0许可证的条款进行许可。详情请参见[LICENSE](LICENSE)文件。

本项目采用 [Apache 许可证](LICENSE)。

## 联系方式

- 项目维护者：[FlyAIBox](https://github.com/FlyAIBox)
- 问题反馈：请使用 [GitHub Issues](https://github.com/FlyAIBox/mcp-in-action/issues)

---

**Model Context Protocol** - 让 AI 模型拥有与世界交互的能力

# ⭐️⭐️⭐️⭐️⭐️

<a href="https://star-history.com/#FlyAIBox/mcp-in-action&Date">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=FlyAIBox/mcp-in-action&type=Date&theme=dark" />
    <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=FlyAIBox/mcp-in-action&type=Date" />
    <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=FlyAIBox/mcp-in-action&type=Date" />
  </picture>
</a>