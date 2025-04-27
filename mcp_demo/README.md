# MCP 天气工具演示

这个项目演示了如何使用 Model Context Protocol (MCP) 创建一个客户端-服务器架构，让 AI 模型可以通过工具获取实时天气信息。

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

项目分为以下主要部分：

1. **MCP 服务器**：提供天气相关工具，包括获取天气预警和天气预报功能
2. **MCP 客户端**：连接服务器，发送工具调用请求，处理返回结果
3. **MCP Inspector**：用于调试和测试 MCP 服务器，提供可视化界面

### 技术栈

- **编程语言**：Python 3.10.12 ; Nodejs 22.14.0 ; Npm 10.9.2
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
┌─────────────┐     stdio    ┌──────────────┐
│             │◄────────────►│              │
│  MCP 客户端  │                MCP 服务器   │
│             │              │              │
└─────────────┘              └──────────────┘
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

## 功能介绍

本项目提供以下功能：

1. **天气预警查询**：获取美国各州的天气预警信息
2. **天气预报查询**：根据经纬度获取详细的天气预报

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

## 运行方式

### 方法一：使用Python启动

```bash
python client/mcp_client.py
```
#### 调用示例
```bash
(venv_mcp_demo) root@fly:~/AI-Box/code/rag/mcp-in-action/mcp_demo/client# python mcp_client.py 
启动 MCP 服务器进程...
已连接到服务器，可用工具: 2
  - get_alerts: 
    获取美国某州的天气预警
    
    参数:
        state: 美国州的两字母代码 (例如 CA, NY)
        
    返回:
        格式化的预警信息字符串
    
  - get_forecast: 
    获取指定经纬度位置的天气预报
    
    参数:
        latitude: 位置的纬度
        longitude: 位置的经度
        
    返回:
        格式化的天气预报字符串
    

使用 'help' 查看帮助，使用 'exit' 退出

> help

可用命令:
  help - 显示此帮助信息
  list - 列出可用工具
  call <工具名> <参数JSON> - 调用工具
  exit - 退出程序

示例:
  call get_alerts CA
  call get_forecast 37.7749 -122.4194
```

##### 天气预警查询
```bash
> call get_alerts CA
正在调用工具...

结果:
[TextContent(type='text', text='\n事件: Beach Hazards Statement\n区域: Orange County Coastal\n严重程度: Moderate\n描述: * WHAT...Elevated surf of 4 to 6 ft, with sets to 7 ft expected.\n\n* WHERE...Orange County Beaches.\n\n* WHEN...From Sunday morning through Wednesday evening.\n\n* IMPACTS...Strong rip currents will create hazardous swimming\nconditions.\n\n* ADDITIONAL DETAILS...A 2 to 3 ft swell from 190 to 200 degrees\nwith a 16 to 18 second period. Highest surf will occur on\nsouth/southwest facing beaches.\n指导意见: Remain out of the water to avoid hazardous swimming conditions.\n\n---\n\n事件: High Wind Warning\n区域: Mojave Desert Slopes\n严重程度: Severe\n描述: * WHAT...Southwest winds 30 to 40 mph with gusts up to 60 mph.\n\n* WHERE...Mojave Desert Slopes.\n\n* WHEN...Until 5 AM PDT Sunday.\n\n* IMPACTS...Damaging winds will blow down trees and power lines.\nWidespread power outages are expected. Travel will be difficult,\nespecially for high profile vehicles.\n\n* ADDITIONAL DETAILS...The greatest impact will be along US highway\n395, and State Routes 14, 58, and 178.\n指导意见: Remain in the lower levels of your home during the windstorm, and\navoid windows. Watch for falling debris and tree limbs. Use caution\nif you must drive.\n\n---\n\n事件: Wind Advisory\n区域: Indian Wells Valley; Mojave Desert\n严重程度: Moderate\n描述: * WHAT...Southwest winds 15 to 25 mph with gusts up to 45 mph.\n\n* WHERE...Indian Wells Valley and Mojave Desert.\n\n* WHEN...Until 11 AM PDT Sunday.\n\n* IMPACTS...Gusty winds will blow around unsecured objects. Tree\nlimbs could be blown down and a few power outages may result.\n指导意见: Winds this strong can make driving difficult, especially for high\nprofile vehicles. Use extra caution.\n\n---\n\n事件: Winter Weather Advisory\n区域: South End of the Upper Sierra; Piute Walker Basin; Tehachapi; Grapevine; Frazier Mountain Communities\n严重程度: Moderate\n描述: * WHAT...Snow expected, mainly above 5,000 feet. Additional snow\naccumulations up to 5 inches.\n\n* WHERE...Frazier Mountain Communities, Grapevine, Piute Walker\nBasin, South End of the Upper Sierra, and Tehachapi.\n\n* WHEN...Until 11 AM PDT Sunday.\n\n* IMPACTS...Plan on slippery road conditions. Gusty winds could\nbring down tree branches.\n指导意见: Slow down and use caution while traveling. The latest road\nconditions for the state you are calling from can be obtained by\ncalling 5 1 1.\n\n---\n\n事件: Winter Weather Advisory\n区域: Yosemite NP outside of the valley; San Joaquin River Canyon; Upper San Joaquin River; Kaiser to Rodgers Ridge; Kings Canyon NP; Grant Grove Area; Sequoia NP\n严重程度: Moderate\n描述: * WHAT...Snow. Additional snow accumulations up to 6 inches.\n\n* WHERE...Sierra Nevada above 5,000 feet.\n\n* WHEN...Until 11 AM PDT Sunday.\n\n* IMPACTS...Travel could be very difficult.\n指导意见: Plan on slippery road conditions. Gusty winds could bring down tree\nbranches. Slow down and use caution while traveling. The latest road\nconditions for the state you are calling from can be obtained by\ncalling 5 1 1.\n\n---\n\n事件: Winter Weather Advisory\n区域: Mono\n严重程度: Moderate\n描述: * WHAT...Snow. Additional snow accumulations 1 to 4 inches, with up\nto 6 inches near the Sierra crest. Ridge wind gusts up to 45 mph.\n\n* WHERE...Mono County.\n\n* WHEN...Until 11 AM PDT Sunday.\n\n* IMPACTS...Snow will produce poor visibility and difficult driving\nconditions at times, especially for higher elevation sections of\nHighway 395.\n\n* ADDITIONAL DETAILS...While snow is less likely to accumulate on\nroads during the daytime hours, some roads could become snow\ncovered or slushy late tonight into early Sunday morning.\n指导意见: Slow down and use caution while traveling. The latest road\nconditions for the state you are calling from can be obtained by\ncalling 5 1 1.\n\n---\n\n事件: Winter Weather Advisory\n区域: Greater Lake Tahoe Area; Greater Lake Tahoe Area\n严重程度: Moderate\n描述: * WHAT...Snow. Additional snow accumulation 2 to 6 inches, with up\nto 9 inches for higher peaks. Ridge wind gusts up to 50 mph.\n\n* WHERE...Greater Lake Tahoe Area.\n\n* WHEN...Until 11 AM PDT Sunday.\n\n* IMPACTS...Snow will produce poor visibility and difficult driving\nconditions at times in and near the Tahoe basin. Scattered snow\nshowers continue through this evening, then another round of\nsteady snow is likely overnight into Sunday morning.\n\n* ADDITIONAL DETAILS...While snow is less likely to accumulate on\nroads during the daytime hours, some roads could become snow\ncovered or slushy late tonight into early Sunday morning.\n指导意见: Slow down and use caution while traveling. The latest road\nconditions for the state you are calling from can be obtained by\ncalling 5 1 1.\n\n---\n\n事件: Winter Weather Advisory\n区域: Western Plumas County/Lassen Park; West Slope Northern Sierra Nevada\n严重程度: Moderate\n描述: * WHAT...Moderate snow expected above 6000 feet. Additional snow\naccumulations of 5 to 10 inches. Winds gusting up to 35 mph.\n\n* WHERE...West Slope Northern Sierra Nevada and Western Plumas\nCounty/Lassen Park Counties.\n\n* WHEN...Until 11 AM PDT Sunday.\n\n* IMPACTS...Plan on slippery road conditions. The hazardous\nconditions could impact weekend travel.\n\n* ADDITIONAL DETAILS...Snow levels around 5000-6000 feet. Light\nsnowfall accumulations possible down to around 5500 feet.\n指导意见: Check the latest road conditions from Caltrans online at\nquickmap.dot.ca.gov or dial 5 1 1.\n\n---\n\n事件: Wind Advisory\n区域: Imperial County Southwest\n严重程度: Moderate\n描述: * WHAT...West winds 25 to 35 mph with gusts up to 55 mph.\n\n* WHERE...Southwest corner of Imperial County.\n\n* WHEN...Until 5 AM PDT Sunday.\n\n* IMPACTS...Difficult driving conditions, especially for larger\nvehicles traveling along roads with crosswinds. Light, unsecured\nobjects may become airborne.\n指导意见: A Wind Advisory means that sustained wind speeds of between 30 and\n40 mph are expected, or wind gusts of between 40 and 58 mph. Winds\nthis strong can make driving difficult, especially for high profile\nvehicles.\n\n---\n\n事件: Beach Hazards Statement\n区域: Malibu Coast; Los Angeles County Beaches\n严重程度: Moderate\n描述: * WHAT...Breaking waves up to 6 feet for south facing beaches and\ndangerous rip currents due to a long lived, long period south\nswell. Minor nuisance flooding may occur Monday and Tuesday\nbetween 6 PM and 3 AM during high tide.\n\n* WHERE...Malibu Coast and Los Angeles County Beaches.\n\n* WHEN...From Sunday morning through Wednesday evening.\n\n* IMPACTS...There is an increased risk of ocean drowning. Rip\ncurrents can pull swimmers and surfers out to sea. Waves can\nwash people off beaches and rocks, and capsize small boats\nnearshore.\n指导意见: Remain out of the water due to hazardous swimming conditions, or\nstay near occupied lifeguard towers. Rock jetties can be deadly\nin such conditions, stay off the rocks.\n', annotations=None)]
```

##### 天气预报查询
```bash
> call get_forecast 37.7749 -122.4194
正在调用工具...

结果:
[TextContent(type='text', text='\nTonight:\n温度: 50°F\n风况: 7 mph W\n预报: A chance of rain before 5am. Mostly cloudy, with a low around 50. West wind around 7 mph. Chance of precipitation is 30%.\n\n---\n\nSunday:\n温度: 60°F\n风况: 6 to 10 mph W\n预报: Partly sunny, with a high near 60. West wind 6 to 10 mph.\n\n---\n\nSunday Night:\n温度: 49°F\n风况: 2 to 10 mph SW\n预报: Patchy fog after 3am. Mostly clear, with a low around 49. Southwest wind 2 to 10 mph.\n\n---\n\nMonday:\n温度: 65°F\n风况: 1 to 10 mph SW\n预报: Patchy fog before 8am. Mostly sunny, with a high near 65. Southwest wind 1 to 10 mph.\n\n---\n\nMonday Night:\n温度: 51°F\n风况: 2 to 10 mph WSW\n预报: Patchy fog after 4am. Mostly clear, with a low around 51. West southwest wind 2 to 10 mph.\n', annotations=None)]

```

### 方法二： 使用 MCP Inspector调试：

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
   - 填写参数并执行工具
   - 查看执行结果和错误信息
   - 检查请求历史和服务器响应
   ![查看可用工具及其描述](./doc/img/MCP%20Inspector01.png)
   ![获取旧金山天气预报](./doc/img/MCP%20Inspector02.png)

> **提示**：MCP Inspector 提供了更直观的界面来测试和调试 MCP 服务器，特别适合开发和调试复杂工具。


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
