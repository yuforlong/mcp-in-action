"""
# 集成 DeepSeek 的 MCP 客户端
#参考官方案例：https://github.com/modelcontextprotocol/python-sdk/blob/main/examples/clients/simple-chatbot/mcp_simple_chatbot/main.py


# 本模块实现了一个模型上下文协议（MCP）客户端，该客户端使用 DeepSeek 的 API
# 来处理查询并与 MCP 工具进行交互。它演示了如何：
# 1. 连接到 MCP 服务器
# 2. 使用 DeepSeek 的 API 来处理查询
# 3. 处理工具调用和响应
# 4. 维护一个交互式聊天循环

# 所需环境变量：
# DEEPSEEK_API_KEY：DeepSeek API 密钥 (格式：sk-xxxx...)
# DEEPSEEK_BASE_URL：DeepSeek API 基础 URL (https://api.deepseek.com)
# DEEPSEEK_MODEL：DeepSeek 模型名称 (例如 deepseek-chat)

Author: FlyAIBox
Date: 2025.05.03
"""

import json
import asyncio
import logging
import os
from typing import Optional, Dict, Any, List, Tuple
from contextlib import AsyncExitStack

from openai import OpenAI
from dotenv import load_dotenv

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()


class Configuration:
    """配置管理类，负责管理和验证环境变量"""
    
    def __init__(self) -> None:
        """初始化配置并加载环境变量"""
        self.load_env()
        self._validate_env()
        
    @staticmethod
    def load_env() -> None:
        """从.env文件加载环境变量"""
        load_dotenv()
        
    def _validate_env(self) -> None:
        """验证必需的环境变量是否存在"""
        required_vars = ["DEEPSEEK_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            raise ValueError(f"缺少必需的环境变量: {', '.join(missing_vars)}")
    
    @property
    def api_key(self) -> str:
        """获取 DeepSeek API 密钥"""
        return os.getenv("DEEPSEEK_API_KEY", "")
    
    @property
    def base_url(self) -> str:
        """获取 DeepSeek API 基础 URL"""
        return os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    
    @property
    def model(self) -> str:
        """获取 DeepSeek 模型名称"""
        return os.getenv("DEEPSEEK_MODEL", "deepseek-chat")

class Tool:
    """MCP 工具类，表示一个具有属性的工具"""
    
    def __init__(self, name: str, description: str, input_schema: Dict[str, Any]) -> None:
        """
        初始化工具
        
        Args:
            name: 工具名称
            description: 工具描述
            input_schema: 输入参数模式
        """
        self.name = name
        self.description = description
        self.input_schema = input_schema
        
    def to_openai_format(self) -> Dict[str, Any]:
        """将工具转换为 OpenAI API 格式"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.input_schema
            }
        }

class MCPServer:
    """MCP 服务器管理类，处理服务器连接和工具执行"""
    
    def __init__(self, server_path: str) -> None:
        """
        初始化服务器管理器
        
        Args:
            server_path: 服务器脚本路径
        """
        self.server_path = server_path
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._cleanup_lock = asyncio.Lock()
        
    async def initialize(self) -> None:
        """初始化服务器连接，包含重试机制"""
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                if not os.path.exists(self.server_path):
                    raise FileNotFoundError(f"找不到服务器文件: {self.server_path}")
                
                server_params = StdioServerParameters(
                    command='python',
                    args=[self.server_path],
                    env=None
                )
                
                stdio_transport = await self.exit_stack.enter_async_context(
                    stdio_client(server_params)
                )
                stdio, write = stdio_transport
                
                self.session = await self.exit_stack.enter_async_context(
                    ClientSession(stdio, write)
                )
                await self.session.initialize()
                logger.info("成功连接到 MCP 服务器")
                break
                
            except Exception as e:
                logger.error(f"第 {attempt + 1}/{max_retries} 次尝试失败: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay)
                else:
                    raise
                    
    async def list_tools(self) -> List[Tool]:
        """获取服务器提供的可用工具列表"""
        if not self.session:
            raise RuntimeError("服务器未初始化")
            
        response = await self.session.list_tools()
        return [
            Tool(tool.name, tool.description, tool.inputSchema)
            for tool in response.tools
        ]
        
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        retries: int = 2,
        delay: float = 1.0
    ) -> Any:
        """
        执行工具，包含重试机制
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            retries: 重试次数
            delay: 重试延迟时间（秒）
            
        Returns:
            工具执行结果
        """
        if not self.session:
            raise RuntimeError("服务器未初始化")
            
        for attempt in range(retries):
            try:
                logger.info(f"执行工具 {tool_name}，参数: {arguments}")
                result = await self.session.call_tool(tool_name, arguments)
                return result
                
            except Exception as e:
                logger.error(f"工具执行失败 (第 {attempt + 1}/{retries} 次尝试): {str(e)}")
                if attempt < retries - 1:
                    await asyncio.sleep(delay)
                else:
                    raise
                    
    async def cleanup(self) -> None:
        """清理服务器资源"""
        async with self._cleanup_lock:
            try:
                await self.exit_stack.aclose()
                self.session = None
                logger.info("服务器资源清理完成")
            except Exception as e:
                logger.error(f"清理过程中出错: {str(e)}")

class MCPClient:
    """MCP 客户端实现，集成了 DeepSeek API"""
    
    def __init__(self, config: Configuration) -> None:
        """
        初始化 MCP 客户端
        
        Args:
            config: 配置对象
        """
        self.config = config
        self.server: Optional[MCPServer] = None
        self.client = OpenAI(
            api_key=config.api_key,
            base_url=config.base_url
        )
        
    async def initialize(self) -> None:
        """初始化客户端并连接到服务器"""
        server_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "server",
            "weather_server.py"
        )
        self.server = MCPServer(server_path)
        await self.server.initialize()
        
    async def process_query(self, query: str) -> str:
        """
        处理用户查询，集成工具调用
        
        Args:
            query: 用户查询字符串
            
        Returns:
            处理后的响应结果
        """
        if not self.server:
            raise RuntimeError("客户端未初始化")
            
        system_prompt = (
            "You are a helpful assistant specializing in weather information.\n"
            "You have access to the MCP Weather Server tool with the following functions:\n"
            "- get_weather_warning(city_id=None, latitude=None, longitude=None): Retrieves weather disaster warnings for a specified city ID or coordinates.\n"
            "- get_daily_forecast(city_id=None, latitude=None, longitude=None): Retrieves the daily weather forecast for a specified city ID or coordinates.\n"
            "\n"
            "For any user query related to weather, you MUST utilize these specific weather tools to find the necessary information before formulating a response. Select the appropriate tool based on whether the user is asking for warnings or forecasts.\n"
            "\n"
            "When using the tools, retain the full context of the user's original question. If the query includes a specific date for a forecast, use the get_daily_forecast tool to search for that date's information directly, and PROHIBIT inserting specific times of day into the search query or your response unless explicitly requested by the user."
        )
                
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        tools = await self.server.list_tools()
        available_tools = [tool.to_openai_format() for tool in tools]
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                tools=available_tools
            )
            
            content = response.choices[0]
            if content.finish_reason == "tool_calls":
                tool_call = content.message.tool_calls[0]
                tool_name = tool_call.function.name
                tool_args = json.loads(tool_call.function.arguments)
                
                result = await self.server.execute_tool(tool_name, tool_args)
                logger.info(f"工具执行完成: {tool_name}")
                
                messages.extend([
                    content.message.model_dump(),
                    {
                        "role": "tool",
                        "content": result.content[0].text,
                        "tool_call_id": tool_call.id,
                    }
                ])
                
                final_response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=messages
                )
                return final_response.choices[0].message.content
                
            return content.message.content
            
        except Exception as e:
            logger.error(f"处理查询时出错: {str(e)}")
            return f"处理您的查询时发生错误: {str(e)}"
            
    async def chat_loop(self) -> None:
        """运行交互式聊天循环"""
        logger.info("开始聊天会话...")
        
        while True:
            try:
                query = input("\n请输入您的问题 (输入 'quit' 或 'exit' 退出): ").strip()
                
                if query.lower() in ['quit', 'exit']:
                    logger.info("结束聊天会话...")
                    break
                    
                response = await self.process_query(query)
                print(f"\n助手: {response}")
                
            except KeyboardInterrupt:
                logger.info("\n收到键盘中断，结束会话...")
                break
            except Exception as e:
                logger.error(f"聊天循环中出错: {str(e)}")
                print(f"\n发生错误: {str(e)}")
                
    async def cleanup(self) -> None:
        """清理客户端资源"""
        if self.server:
            await self.server.cleanup()

async def main() -> None:
    """主程序入口"""
    try:
        config = Configuration()
        client = MCPClient(config)
        
        await client.initialize()
        await client.chat_loop()
        
    except Exception as e:
        logger.error(f"致命错误: {str(e)}")
        raise
        
    finally:
        if 'client' in locals():
            await client.cleanup()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("程序被用户终止")
    except Exception as e:
        logger.error(f"程序因错误终止: {str(e)}")
        raise
