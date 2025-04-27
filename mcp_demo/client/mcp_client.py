#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MCP 客户端示例

用于与 MCP 服务器交互，调用工具并处理结果
"""

import asyncio
import json
import os
import subprocess
import sys
from typing import Dict, Any, List, Optional

from mcp.client import ExecutionRequest, ToolCallResult, ToolCall, ToolDefinition
from mcp.transport.stdio import StdioTransport
from mcp.client.hosted import HostedClient

class SimpleClientApp:
    """简单的 MCP 客户端应用"""
    
    def __init__(self, server_command: List[str]):
        """
        初始化 MCP 客户端应用
        
        参数:
            server_command: 启动服务器的命令列表
        """
        self.server_command = server_command
        self.server_process = None
        self.client = None
        self.tool_definitions = []
    
    async def start(self):
        """启动 MCP 客户端并连接到服务器"""
        print("启动 MCP 服务器进程...")
        
        # 启动服务器进程
        self.server_process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # 创建 STDIO 传输器
        transport = StdioTransport(
            self.server_process.stdout,
            self.server_process.stdin
        )
        
        # 创建 MCP 客户端
        self.client = HostedClient(transport)
        await self.client.start()
        
        # 获取工具定义
        self.tool_definitions = await self.client.get_tool_definitions()
        print(f"已连接到服务器，可用工具: {len(self.tool_definitions)}")
        
        for tool in self.tool_definitions:
            print(f"  - {tool.name}: {tool.description}")
        
        print("\n使用 'help' 查看帮助，使用 'exit' 退出")
    
    async def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Optional[str]:
        """
        执行工具调用
        
        参数:
            tool_name: 要调用的工具名称
            params: 工具参数字典
            
        返回:
            工具执行结果或错误消息
        """
        # 检查工具是否存在
        tool_def = next((t for t in self.tool_definitions if t.name == tool_name), None)
        if not tool_def:
            return f"错误: 未找到工具 '{tool_name}'"
        
        # 创建工具调用
        tool_call = ToolCall(name=tool_name, parameters=params)
        
        # 创建执行请求
        request = ExecutionRequest(tool_calls=[tool_call])
        
        try:
            # 发送请求并等待结果
            result = await self.client.execute_tools(request)
            
            # 处理结果
            if result.results and len(result.results) > 0:
                tool_result = result.results[0]
                if tool_result.error:
                    return f"工具执行错误: {tool_result.error}"
                return tool_result.result
            else:
                return "工具执行未返回任何结果"
        
        except Exception as e:
            return f"执行过程中出错: {str(e)}"
    
    async def stop(self):
        """停止客户端和服务器"""
        print("正在关闭 MCP 客户端...")
        if self.client:
            await self.client.stop()
        
        if self.server_process:
            print("正在关闭服务器进程...")
            self.server_process.terminate()
            try:
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server_process.kill()
        
        print("已关闭")
    
    def print_help(self):
        """打印帮助信息"""
        print("\n可用命令:")
        print("  help - 显示此帮助信息")
        print("  list - 列出可用工具")
        print("  call <工具名> <参数JSON> - 调用工具")
        print("  exit - 退出程序")
        print("\n示例:")
        print("  call get_alerts CA")
        print("  call get_forecast 37.7749 -122.4194")
    
    def print_tools(self):
        """打印工具列表和描述"""
        print("\n可用工具:")
        for tool in self.tool_definitions:
            print(f"  {tool.name} - {tool.description}")
            if tool.parameters:
                print("    参数:")
                for param in tool.parameters:
                    print(f"      {param.name} ({param.type}): {param.description}")

async def main():
    """主函数"""
    # 确定服务器路径
    server_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "server",
        "weather_server.py"
    )
    
    # 检查服务器文件是否存在
    if not os.path.exists(server_path):
        print(f"错误: 服务器文件不存在: {server_path}")
        return
    
    # 创建客户端应用
    app = SimpleClientApp(["python", server_path])
    
    try:
        # 启动客户端
        await app.start()
        
        # 主循环
        while True:
            try:
                # 获取用户输入
                command = input("\n> ").strip()
                
                # 处理命令
                if command == "exit":
                    break
                
                elif command == "help":
                    app.print_help()
                
                elif command == "list":
                    app.print_tools()
                
                elif command.startswith("call "):
                    # 解析命令
                    parts = command[5:].strip().split(" ", 1)
                    if len(parts) < 1:
                        print("错误: 缺少工具名")
                        continue
                    
                    tool_name = parts[0]
                    
                    # 解析参数
                    params = {}
                    if len(parts) > 1:
                        params_str = parts[1]
                        
                        # 尝试解析为 JSON
                        try:
                            params = json.loads(params_str)
                        except json.JSONDecodeError:
                            # 如果不是 JSON，尝试简单解析
                            try:
                                # 对于 get_alerts，只需要一个状态参数
                                if tool_name == "get_alerts":
                                    params = {"state": params_str}
                                
                                # 对于 get_forecast，需要纬度和经度
                                elif tool_name == "get_forecast":
                                    lat_lon = params_str.split()
                                    if len(lat_lon) != 2:
                                        print("错误: get_forecast 需要两个参数: 纬度 经度")
                                        continue
                                    
                                    params = {
                                        "latitude": float(lat_lon[0]),
                                        "longitude": float(lat_lon[1])
                                    }
                                else:
                                    print(f"错误: 无法解析 {tool_name} 的参数")
                                    continue
                            
                            except Exception as e:
                                print(f"参数解析错误: {str(e)}")
                                continue
                    
                    # 执行工具调用
                    print("正在调用工具...")
                    result = await app.execute_tool(tool_name, params)
                    print("\n结果:")
                    print(result)
                
                else:
                    print(f"未知命令: {command}")
                    print("使用 'help' 查看可用命令")
            
            except KeyboardInterrupt:
                print("\n操作被中断")
                break
            
            except Exception as e:
                print(f"错误: {str(e)}")
    
    except Exception as e:
        print(f"客户端错误: {str(e)}")
    
    finally:
        # 停止客户端
        await app.stop()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序被中断")
        sys.exit(0) 