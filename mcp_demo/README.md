# MCP 实战

Model Context Protocol (MCP) 入门示例项目，包含服务器和客户端实现。

## 项目介绍

本项目是一个基于 MCP（Model Context Protocol）的入门级 Demo，用于帮助开发者理解和使用 MCP 技术。项目展示了如何创建 MCP 服务器和客户端，以及如何实现服务器与客户端之间的交互。

MCP 是一种开放协议，允许大语言模型（如 Claude）与外部系统安全地交互，提供工具、数据访问以及环境信息。通过 MCP，AI 模型可以更加安全、高效地处理需要与外部系统集成的任务。

### 项目特点

- 简单易懂的 MCP 服务器实现
- 功能完整的 MCP 客户端示例
- 基于天气信息 API 的实际应用场景
- 详细的代码注释和文档说明
- 完整的部署和使用指南

## 项目架构

项目分为两个主要部分：

1. **MCP 服务器**：提供天气相关工具，包括获取天气预警和天气预报功能
2. **MCP 客户端**：连接服务器，发送工具调用请求，处理返回结果
3. **MCP Inspector**：用于调试和测试 MCP 服务器，提供可视化界面

### 技术栈

- **编程语言**：Python 3.10.12 ; Nodejs 22.14.0 ; NPM 10.9.2
- **部署环境**：Ubuntu 22.04
- **核心依赖**：
  - MCP SDK 1.5.0
  - HTTPX 库（HTTP 客户端）
  - 异步编程（asyncio）
- **调试工具**：
  - MCP Inspector (Node.js)

### 项目结构

```
mcp_demo/
│
├── server/                    # 服务器实现
│   └── weather_server.py      # 天气信息服务器
│
├── client/                    # 客户端实现
│   └── mcp_client.py          # MCP 客户端
│
├── requirements.txt           # 项目依赖
├── run.sh                     # 运行脚本
└── README.md                  # 项目文档
```

### 系统交互图

```
┌─────────────┐     stdio     ┌─────────────┐
│             │◄────────────►│             │
│  MCP 客户端  │              │  MCP 服务器  │
│             │              │             │
└─────────────┘              └─────────────┘
                                   ▲
                                   │
                              调试 │
                                   │
                                   ▼
                            ┌─────────────┐
                            │             │
                            │MCP Inspector│
                            │             │
                            └─────────────┘
```

## 业务流程

MCP 的基本工作流程如下：

1. **服务器注册工具**：MCP 服务器定义并注册工具，提供工具的元数据信息（名称、描述、参数等）
2. **客户端连接服务器**：客户端通过传输层（如 STDIO）连接到服务器
3. **客户端获取工具定义**：客户端从服务器获取可用工具的定义
4. **用户选择工具**：用户通过客户端界面选择要使用的工具和参数
5. **客户端发送执行请求**：客户端发送工具执行请求到服务器
6. **服务器执行工具**：服务器处理请求，执行相应的工具函数
7. **服务器返回结果**：服务器将执行结果返回给客户端
8. **客户端展示结果**：客户端处理并展示执行结果

### 服务器实现说明

服务器实现提供了两个主要工具：

- **get_alerts**：获取美国某州的天气预警信息
- **get_forecast**：获取指定经纬度位置的天气预报

这些工具通过美国国家气象局（National Weather Service）的 API 获取实时数据。

### 客户端实现说明

客户端提供了一个简单的命令行界面，支持以下操作：

- 列出可用工具及其描述
- 调用工具并传递参数
- 显示工具执行结果
- 提供帮助信息

## 部署说明

### 环境要求

- Python 3.10.12 或更高版本
- Ubuntu 22.04 操作系统（也可在其他 Linux 发行版上运行）

### 安装步骤

1. **克隆项目**：

```bash
git clone https://github.com/your-username/mcp-in-action.git
cd mcp-in-action/mcp_demo
```

2. **创建并激活虚拟环境**：

```bash
python -m venv venv_mcp_demo
source venv_mcp_demo/bin/activate
```

3. **安装依赖**：

```bash
pip install -r requirements.txt
```

### 使用说明

#### 运行服务器（独立模式）：

```bash
python server/weather_server.py
```

服务器将启动并等待客户端连接，通过 STDIO 传输层通信。

#### 运行客户端：

```bash
python client/mcp_client.py
```

客户端会自动启动服务器并连接。

#### 使用脚本一键启动：

```bash
chmod +x run.sh  # 确保脚本可执行
./run.sh
```

此脚本会自动创建虚拟环境、安装依赖并启动客户端。

#### 使用 MCP Inspector 进行调试：

MCP Inspector 是一个可视化工具，可帮助调试和测试 MCP 服务器。要使用 MCP Inspector：

1. **安装 MCP Inspector**：

```bash
npm install -g @modelcontextprotocol/inspector
```

2. **使用 MCP Inspector 调试服务器**：

推荐使用简化命令 `mcp dev`：

```bash
mcp dev server/weather_server.py
```

或者使用 npx（如果未全局安装）：

```bash
npx @modelcontextprotocol/inspector python server/weather_server.py
```

3. **在浏览器中访问 Inspector**：

默认情况下，Inspector UI 运行在 http://localhost:6274，而 MCP 代理服务器运行在端口 6277。

4. **通过 Inspector 调试**：
   - 查看可用工具及其描述
   ![查看可用工具及其描述](./doc/img/MCP%20Inspector01.png)
   - 填写参数并执行工具
   
   - 查看执行结果和错误信息
   - 检查请求历史和服务器响应

> **提示**：MCP Inspector 提供了更直观的界面来测试和调试 MCP 服务器，特别适合开发和调试复杂工具。

#### 客户端命令：

- `help` - 显示帮助信息
- `list` - 列出可用工具
- `call <工具名> <参数>` - 调用工具
  - 例如：`call get_alerts CA`
  - 例如：`call get_forecast 37.7749 -122.4194`
- `exit` - 退出程序

## 示例

### 获取加州天气预警：

```
> call get_alerts CA
正在调用工具...

结果:
当前 CA 州没有活动预警。
```

### 获取旧金山天气预报：

```
> call get_forecast 37.7749 -122.4194
正在调用工具...

结果:
今天:
温度: 75°F
风况: 5 to 10 mph W
预报: 晴朗。最高温度接近 75°F。西风 5 到 10 mph。

---
今晚:
温度: 58°F
风况: 5 to 10 mph W
预报: 多云。最低温度接近 58°F。西风 5 到 10 mph。

---
周二:
温度: 70°F
风况: 5 to 10 mph W
预报: 多云转晴。最高温度接近 70°F。西风 5 到 10 mph。
```

## 常见问题

### 服务器无法启动

- 确保已安装所有依赖
- 检查 Python 版本是否 3.10 或更高版本
- 检查服务器文件权限是否正确

### API 请求失败

- 确保网络连接正常
- 美国国家气象局 API 可能有请求限制，如果频繁请求可能会被限制
- 只支持美国境内的位置信息查询

## 使用 MCP Inspector 调试与故障排除

MCP Inspector 是开发和调试 MCP 服务器的重要工具，提供了直观的可视化界面，帮助开发者理解和解决问题。

### Inspector 的主要功能

1. **实时工具调用**：
   - 通过界面直接调用 MCP 工具
   - 可视化参数表单，避免语法错误
   - 查看格式化的执行结果

2. **请求历史记录**：
   - 跟踪所有工具调用历史
   - 复制和重放之前的请求
   - 对比不同参数下的执行结果

3. **错误分析**：
   - 详细的错误消息和堆栈跟踪
   - 突出显示参数验证错误
   - 显示请求/响应时间，帮助性能分析

4. **流式响应可视化**：
   - 查看支持流式传输的工具的实时输出
   - 分析流式传输过程中的延迟

### 常见调试场景

#### 1. 参数验证错误

当工具参数格式不正确时：

```bash
npx @modelcontextprotocol/inspector python server/weather_server.py
```

在 Inspector 中：
1. 选择工具（如 `get_forecast`）
2. 故意提供错误格式的参数（如字符串而非数字）
3. 执行后，Inspector 会显示详细的验证错误

#### 2. API 集成问题

当外部 API 调用失败时：

```bash
npx @modelcontextprotocol/inspector python server/weather_server.py
```

在 Inspector 中：
1. 调用 `get_alerts` 或 `get_forecast` 工具
2. 检查网络请求错误信息
3. 分析响应码和错误消息

#### 3. 性能分析

分析工具执行时间：

```bash
npx @modelcontextprotocol/inspector python server/weather_server.py
```

在 Inspector 中：
1. 调用目标工具多次，使用不同参数
2. 分析每次调用的执行时间
3. 识别性能瓶颈

### 调试最佳实践

1. **先用 Inspector，再集成客户端**：
   - 在开发新工具时，先用 Inspector 测试和完善
   - 确保工具正常工作后再集成到客户端

2. **保存常用测试用例**：
   - 使用 Inspector 的"保存请求"功能
   - 创建不同场景的测试用例集

3. **使用 CLI 模式进行自动化测试**：
   ```bash
   npx @modelcontextprotocol/inspector --cli python server/weather_server.py --method tools/call --tool-name get_alerts --tool-arg state=CA
   ```

4. **对比服务器版本**：
   - 使用相同参数测试不同版本的服务器实现
   - 分析性能和行为差异

通过有效使用 MCP Inspector，可以显著提高开发效率，减少调试时间，并确保 MCP 服务器的稳定性和可靠性。

## 扩展与优化

1. **添加更多工具**：可以扩展服务器添加更多工具，如历史天气数据查询、未来几天预报等
2. **支持更多数据源**：集成其他天气 API，提供全球天气信息
3. **改进用户界面**：开发图形用户界面，提供更直观的操作体验
4. **添加用户认证**：增加安全措施，实现用户认证和权限控制
5. **优化性能**：添加缓存机制，减少 API 请求次数

## 联系与贡献

欢迎贡献代码或提出改进建议，可以通过以下方式联系：

- 提交 Issue
- 发送 Pull Request
- 发送邮件至：fly910905@sina.com

## 许可证

本项目采用 MIT 许可证，详情请参阅 LICENSE 文件。
