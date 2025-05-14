"""
Milvus MCP 客户端
功能：与 Milvus MCP Server 交互的客户端实现
作用：提供与 MCP 服务器通信的接口，用于存储和检索知识库内容和FAQ
主要功能：
1. 连接 MCP 服务器并获取可用的工具列表
2. 存储和检索文本知识内容
3. 存储和检索 FAQ 问答对
4. 处理 MCP 协议的会话管理和数据交换
"""
import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from loguru import logger
from mcp.client.sse import sse_client 
from mcp import ClientSession
from contextlib import AsyncExitStack
from app.config import MCP_SERVER_URL, TOOLS
import json

class MCPClient:
    """MCP服务器交互客户端，负责与Milvus MCP服务器的通信"""
    
    def __init__(self, server_url: str = MCP_SERVER_URL):
        """
        初始化MCP客户端
        
        参数:
            server_url: MCP服务器的URL地址
        """
        self.server_url = server_url
        self.client = None
        self.tools = {}
        self._connected = False
        self.exit_stack = AsyncExitStack()
        self.session = None
        logger.info(f"Initialized MCP client with server URL: {server_url}")
        
    async def __aenter__(self):
        """异步上下文管理器的进入方法"""
        if not self._connected:
            await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器的退出方法"""
        await self.close()
        
    async def connect(self) -> None:
        """
        连接到MCP服务器并获取可用的工具
        建立服务器连接，初始化会话，并加载可用的MCP工具
        """
        try:
            logger.info(f"Connecting to MCP server at {self.server_url}...")
            self.client = sse_client(self.server_url)
            
            # 使用异步上下文管理器初始化客户端连接
            stdio_transport = await self.exit_stack.enter_async_context(self.client)
            read, write = stdio_transport
            
            # 创建客户端会话
            self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            
            # 初始化会话
            await self.session.initialize()
            
            # 获取可用工具
            tools_response = await self.session.list_tools()
            available_tools = tools_response.tools
            
            # 检查我们需要的工具是否可用
            for tool_name in TOOLS:
                logger.info(f"Checking for tool: {tool_name}")
                tool_found = False
                for tool in available_tools:
                    if tool.name == tool_name:
                        # 创建一个闭包来捕获工具名称
                        async def tool_caller(tn=tool_name, **kwargs):
                            return await self.session.call_tool(tn, kwargs)
                        self.tools[tool_name] = tool_caller
                        logger.info(f"Successfully loaded tool: {tool_name}")
                        tool_found = True
                        break
                
                if not tool_found:
                    logger.error(f"Tool not available: {tool_name}")
            
            if not self.tools:
                logger.error("No tools available from the MCP server")
                raise Exception("No tools available from the MCP server")
                
            self._connected = True
            logger.info(f"Successfully connected to MCP server. Available tools: {list(self.tools.keys())}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MCP server: {str(e)}")
            raise Exception(f"Failed to connect to MCP server: {str(e)}")
            
    async def store_knowledge(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        存储知识内容到MCP服务器
        
        参数:
            content: 要存储的文本内容
            metadata: 与内容关联的可选元数据
            
        返回:
            服务器的响应结果
        """
        if not self._connected:
            await self.connect()
            
        tool = self.tools.get("storeKnowledge")
        if not tool:
            raise Exception("storeKnowledge tool not available")
            
        try:
            metadata = metadata or {}
            response = await tool(content=content, metadata=metadata)
            logger.info(f"Successfully stored knowledge content")
            return response
        except Exception as e:
            logger.error(f"Failed to store knowledge: {str(e)}")
            raise Exception(f"Failed to store knowledge: {str(e)}")
            
    async def search_knowledge(self, query: str, size: int = 5) -> List[Dict[str, Any]]:
        """
        在MCP服务器中搜索知识内容
        
        参数:
            query: 搜索查询
            size: 返回结果的最大数量
            
        返回:
            匹配的知识内容列表
        """
        if not self._connected:
            await self.connect()
            
        tool = self.tools.get("searchKnowledge")
        if not tool:
            raise Exception("searchKnowledge tool not available")
            
        try:
            response = await tool(query=query, size=size)
            
            # 处理CallToolResult对象
            # 从响应内容中提取结果
            results = []
            if hasattr(response, "content") and response.content:
                # 如果是字符串，尝试将内容解析为JSON
                for part in response.content:
                    if hasattr(part, "text") and part.text:
                        try:
                            result_data = json.loads(part.text)
                            if isinstance(result_data, dict) and "results" in result_data:
                                results = result_data["results"]
                            elif isinstance(result_data, list):
                                results = result_data
                        except json.JSONDecodeError:
                            # 如果不是有效的JSON，按原样使用文本
                            logger.warning(f"Could not parse JSON from searchKnowledge response: {part.text}")
            
            logger.info(f"Found {len(results)} knowledge results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search knowledge: {str(e)}")
            raise Exception(f"Failed to search knowledge: {str(e)}")
            
    async def store_faq(self, question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        存储FAQ内容到MCP服务器
        
        参数:
            question: FAQ问题
            answer: FAQ答案
            metadata: 与FAQ关联的可选元数据
            
        返回:
            服务器的响应结果
        """
        if not self._connected:
            await self.connect()
            
        tool = self.tools.get("storeFAQ")
        if not tool:
            raise Exception("storeFAQ tool not available")
            
        try:
            metadata = metadata or {}
            response = await tool(question=question, answer=answer, metadata=metadata)
            logger.info(f"Successfully stored FAQ content")
            return response
        except Exception as e:
            logger.error(f"Failed to store FAQ: {str(e)}")
            raise Exception(f"Failed to store FAQ: {str(e)}")
            
    async def search_faq(self, query: str, size: int = 5) -> List[Dict[str, Any]]:
        """
        在MCP服务器中搜索FAQ内容
        
        参数:
            query: 搜索查询
            size: 返回结果的最大数量
            
        返回:
            匹配的FAQ内容列表
        """
        if not self._connected:
            await self.connect()
            
        tool = self.tools.get("searchFAQ")
        if not tool:
            raise Exception("searchFAQ tool not available")
            
        try:
            response = await tool(query=query, size=size)
            
            # 处理CallToolResult对象
            # 从响应内容中提取结果
            results = []
            if hasattr(response, "content") and response.content:
                # 如果是字符串，尝试将内容解析为JSON
                for part in response.content:
                    if hasattr(part, "text") and part.text:
                        try:
                            result_data = json.loads(part.text)
                            if isinstance(result_data, dict) and "results" in result_data:
                                results = result_data["results"]
                            elif isinstance(result_data, list):
                                results = result_data
                        except json.JSONDecodeError:
                            # 如果不是有效的JSON，按原样使用文本
                            logger.warning(f"Could not parse JSON from searchFAQ response: {part.text}")
            
            logger.info(f"Found {len(results)} FAQ results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search FAQ: {str(e)}")
            raise Exception(f"Failed to search FAQ: {str(e)}")
            
    async def close(self) -> None:
        """关闭与MCP服务器的连接"""
        if self._connected:
            try:
                # 首先清除工具字典
                self.tools = {}
                
                # 在关闭之前显式地将连接标志设置为False
                self._connected = False
                
                # 关闭exit stack，它将处理所有异步上下文管理器
                try:
                    await self.exit_stack.aclose()
                    logger.info("Closed connection to MCP server")
                except RuntimeError as e:
                    # 忽略特定的生成器退出相关的RuntimeError
                    if "generator didn't stop after athrow()" in str(e) or "unhandled errors in a TaskGroup" in str(e):
                        logger.warning(f"Ignoring known SSE connection cleanup issue: {str(e)}")
                    else:
                        # 如果不是我们处理的特定错误，则重新抛出
                        raise
            except Exception as e:
                logger.error(f"Error closing MCP connection: {str(e)}")
            finally:
                # 确保即使在发生异常的情况下也将这些设置为None
                self.session = None
                self.client = None 