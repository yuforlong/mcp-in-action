import json
from mcp import ClientSession
from mcp.client.sse import sse_client
from typing import Any, List, Dict
from contextlib import AsyncExitStack
import asyncio
import os
from loguru import logger

import client_chunk as chunk
from client_config import *
import sys

class MCPClient:
    """
    一个用于与MCP（模型上下文协议）服务器交互的客户端类。
    此类管理与Milvus向量数据库的MCP连接和通信。
    """

    def __init__(self, host: str):
        """
        使用服务器参数初始化MCP客户端
        
        Args:
            host: MCP服务器主机地址
        """
        self.host = host  # MCP服务器主机地址
        self.exit_stack = AsyncExitStack()  # 异步上下文管理器栈，用于管理异步资源
        self.session = None  # MCP会话对象
        self._client = None  # MCP客户端对象
        logger.info(f"Initializing MCP client with host: {host}")

    async def __aenter__(self):
        """
        异步上下文管理器入口，进入时自动连接服务器
        """
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        异步上下文管理器出口，退出时自动关闭连接
        """
        if self.session:
            await self.session.__aexit__(exc_type, exc_val, exc_tb)
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def connect(self):
        """
        建立与MCP服务器的连接，包含重试机制
        """
        max_retries = 5
        retry_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Connecting to MCP server (attempt {attempt + 1}/{max_retries})...")
                self._client = sse_client(self.host, timeout=10)  # 创建SSE客户端，设置超时时间为10秒
                # 使用异步上下文管理器栈(exit_stack)进入SSE客户端的异步上下文
                stdio_transport = await self.exit_stack.enter_async_context(self._client)  # 进入异步上下文并获取传输对象
                read, write = stdio_transport  # 解包获取读写通道
                
                # 添加短暂延迟以确保服务器初始化完成
                await asyncio.sleep(1)
                
                self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))  # 创建并进入客户端会话
                
                # 测试连接，列出可用工具
                tools = await self.get_available_tools()
                logger.info(f"Successfully connected to MCP server on attempt {attempt + 1}")
                logger.info(f"Available tools: {', '.join([tool.name for tool in tools])}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.error(f"Connection attempt {attempt + 1} failed: {e}")
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Failed to connect after {max_retries} attempts: {e}")
                    raise

    async def get_available_tools(self) -> List[Any]:
        """
        从MCP服务器获取可用工具列表
        
        Returns:
            可用工具列表
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")  # 如果会话未建立，抛出运行时错误

        tools = await self.session.list_tools()  # 异步获取工具列表
        return tools.tools  # 返回可用工具

    async def call_tool(self, tool_name: str, args) -> Any:
        """
        为特定工具创建可调用函数并执行。
        这允许我们通过MCP服务器执行数据库操作。

        Args:
            tool_name: 要创建可调用函数的工具名称
            args: 传递给工具的参数

        Returns:
            工具执行结果
        """
        if not self.session:
            raise RuntimeError("Not connected to MCP server")  # 如果会话未建立，抛出运行时错误

        try:
            logger.debug(f"Calling tool '{tool_name}' with arguments: {args}")
            result = await self.session.call_tool(tool_name, args)  # 调用指定工具并传递参数
            return result
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}': {e}")
            raise


async def agent_loop(mcp_client, query: str, tools, messages: List[Dict] = None):
    """
    主要交互循环，使用LLM和可用工具处理用户查询。

    此函数:
    1. 将用户查询发送给LLM，并提供可用工具的上下文
    2. 处理LLM的响应，包括任何工具调用
    3. 向用户返回最终响应

    Args:
        mcp_client: MCP客户端实例
        query: 用户的输入问题或命令
        tools: 可用数据库工具列表
        messages: 传递给LLM的消息列表，默认为None
    
    Returns:
        LLM的最终文本响应
    """
    # 将工具列表转换为LLM可用的格式
    available_tools = [{
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    } for tool in tools]

    # 创建消息列表，包含用户查询
    if messages is None:
        messages = []
    
    messages.append({
        "role": "user",
        "content": query
    })

    # 使用系统提示、用户查询和可用工具查询LLM
    logger.info(f"Sending query to LLM: {query[:100]}{'...' if len(query) > 100 else ''}")
    response = await llm_client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
        tools=available_tools
    )

    final_text = []  # 用于存储最终文本响应
    message = response.choices[0].message  # 获取LLM响应的第一个选项
    if message.content:
        final_text.append(message.content)  # 添加LLM响应内容到最终文本
        logger.debug(f"LLM initial response: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")

    # 当LLM响应包含工具调用时，处理工具调用
    while message.tool_calls:
        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name  # 获取工具名称
            tool_args = json.loads(tool_call.function.arguments)  # 解析工具参数
            
            logger.info(f"LLM requested tool: {tool_name}")
            logger.debug(f"Tool args: {tool_args}")

            # 调用指定工具并获取结果
            result = await mcp_client.call_tool(tool_name, tool_args)
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")  # 记录工具调用信息
            
            logger.debug(f"Tool result: {str(result.content)[:100]}{'...' if len(str(result.content)) > 100 else ''}")

            # 将工具调用添加到消息历史中
            messages.append({
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": json.dumps(tool_args)
                        }
                    }
                ]
            })

            # 将工具调用结果添加到消息历史中
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": str(result.content)
            })

        # 再次查询LLM，包含工具调用结果
        logger.info("Sending follow-up query to LLM with tool results")
        response = await llm_client.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            tools=available_tools
        )

        message = response.choices[0].message  # 获取LLM的新响应
        if message.content:
            final_text.append(message.content)  # 将新响应添加到最终文本
            logger.debug(f"LLM follow-up response: {message.content[:100]}{'...' if len(message.content) > 100 else ''}")

    result = "\n".join(final_text)  # 将所有文本拼接
    logger.info("Agent loop completed successfully")
    return result


async def import_knowledge(path):
    """
    导入知识库文件，将文本内容分块并存储到数据库中
    
    Args:
        path: 知识库文件路径
    """
    # 读取知识文本内容
    try:
        logger.info(f"Reading file: {path}")
        with open(path, 'r', encoding='utf-8') as f:
            knowledge_text = f.read()
        logger.info(f"File read successfully, size: {len(knowledge_text)} characters")
    except Exception as e:
        logger.error(f"Error reading file {path}: {e}")
        return

    # 将文本切分成每块不超过2000字符的块
    logger.info("Chunking text...")
    chunks = chunk.to_chunks(knowledge_text, 2000)
    logger.info(f"Text chunked into {len(chunks)} chunks")
    
    # 创建并连接MCP客户端
    logger.info(f"Connecting to MCP server at {MCP_SERVER_HOST}")
    
    try:
        async with MCPClient(MCP_SERVER_HOST) as mcp_client:
            # 尝试访问服务器，确保连接正常
            try:
                # 获取可用数据库工具
                tools = await mcp_client.get_available_tools()
                if not tools:
                    logger.warning("Warning: No tools available from the server")
                    return
            except Exception as e:
                logger.error(f"Error communicating with MCP server: {e}")
                return

            logger.info(f'Total Chunks: {len(chunks)}')
            # 处理每一个文本块
            for i, c in enumerate(chunks):
                logger.info(f'Processing chunk {i+1}/{len(chunks)}')
                try:
                    # 根据模板构建分析内容的提示
                    query = analysis_content_prompt_template % c
                    # 调用agent_loop处理分析任务
                    response = await agent_loop(mcp_client, query, tools)
                    try:
                        # 尝试将响应解析为JSON
                        j = json.loads(response)
                        logger.info(f"Chunk {i+1} analysis completed: {len(j.get('Chunks', []))} knowledge chunks, {len(j.get('FAQs', []))} FAQs")
                    except Exception as e:
                        logger.error(f"Error parsing response: {e}")
                        logger.debug(f"Response: {response}")
                        continue

                    # 处理解析出的文本块，存储到知识库
                    for kc in j.get('Chunks', []):
                        try:
                            # 根据模板构建存储知识的提示
                            q = store_knowledge_prompt_template % kc
                            # 调用agent_loop处理存储任务
                            response = await agent_loop(mcp_client, q, tools)
                            logger.info(f"Knowledge chunk stored: {kc[:50]}...")
                        except Exception as e:
                            logger.error(f"Error storing knowledge chunk: {e}")

                    # 处理解析出的FAQ对，存储到FAQ库
                    for faq in j.get('FAQs', []):
                        try:
                            question = faq.get('Question', '')
                            answer = faq.get('Answer', '')
                            q = store_faq_prompt_template % (question, answer)
                            response = await agent_loop(mcp_client, q, tools)
                            logger.info(f"FAQ stored: {question[:50]}...")
                        except Exception as e:
                            logger.error(f"Error storing FAQ: {e}")
                except Exception as e:
                    logger.error(f"Error processing chunk {i+1}: {e}")
            
            logger.info("Knowledge import completed successfully")
    except Exception as e:
        logger.error(f"Connection error: {e}")


async def search_knowledge(query):
    """
    搜索知识库中的内容
    
    Args:
        query: 搜索查询
    """
    # 根据模板构建搜索提示
    formatted_query = search_prompt_template % query
    logger.info(f"Searching knowledge with query: {query}")
    
    # 创建并连接MCP客户端
    try:
        async with MCPClient(MCP_SERVER_HOST) as mcp_client:
            # 获取可用数据库工具
            tools = await mcp_client.get_available_tools()
            
            # 调用agent_loop处理搜索任务
            response = await agent_loop(mcp_client, formatted_query, tools)
            logger.info("Knowledge search completed")
            print(response)  # 打印搜索结果
    except Exception as e:
        logger.error(f"Knowledge search error: {e}")


async def chat(query):
    """
    基于知识库的智能问答
    
    Args:
        query: 用户问题
    """
    # 根据模板构建聊天提示
    formatted_query = chat_prompt_template % query
    logger.info(f"Processing chat query: {query}")
    
    # 创建并连接MCP客户端
    try:
        async with MCPClient(MCP_SERVER_HOST) as mcp_client:
            # 获取可用数据库工具
            tools = await mcp_client.get_available_tools()
            
            # 调用agent_loop处理聊天任务
            response = await agent_loop(mcp_client, formatted_query, tools)
            logger.info("Chat query completed")
            print(response)  # 打印聊天响应
    except Exception as e:
        logger.error(f"Chat error: {e}")


async def main():
    """
    主函数，处理命令行参数并执行相应操作
    """
    # 设置日志级别
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    logger.remove()
    logger.add(sys.stderr, level=log_level)
    
    logger.info("Milvus MCP Client starting...")
    
    # 读取sys.argv中的参数，如果参数数量少于2则返回错误
    if len(sys.argv) < 3:
        logger.error("Usage: python knowledge_manager.py import/search/chat <args>")
        return

    command = sys.argv[1]  # 获取命令（import/search/chat）
    args = sys.argv[2]  # 获取命令参数

    # 根据命令执行相应操作
    if command == 'import':
        logger.info(f"Import command received with path: {args}")
        await import_knowledge(args)  # 导入知识
    elif command == 'search':
        logger.info(f"Search command received with query: {args}")
        await search_knowledge(args)  # 搜索知识
    elif command == 'chat':
        logger.info(f"Chat command received with query: {args}")
        await chat(args)  # 基于知识库聊天
    else:
        # 命令无效，打印使用说明
        logger.error(f"Invalid command: {command}")
        logger.error("Usage: python knowledge_manager.py import/search/chat <args>")
        return

if __name__ == "__main__":
    # 运行主函数
    asyncio.run(main()) 