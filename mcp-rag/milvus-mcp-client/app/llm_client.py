"""
LLM 客户端模块
功能：提供与大型语言模型(LLM)的交互接口
作用：使用OpenAI兼容API调用LLM模型，用于生成文本、问题拆解和FAQ提取
主要功能：
1. 异步和同步调用LLM模型生成文本
2. 支持工具调用功能(Function Calling)
3. 处理模型响应并转换为适当的数据结构
"""
import json
from typing import Dict, List, Any, Optional, Union
from loguru import logger
import os
from openai import OpenAI, AsyncOpenAI

from app.config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL

class LLMClient:
    """通过OpenAI API与LLM模型交互的客户端"""
    
    def __init__(self, model: str = OPENAI_MODEL):
        """
        初始化LLM客户端
        
        参数:
            model: 要使用的模型名称
        """
        self.model = model
        self.api_key = OPENAI_API_KEY
        self.api_base = OPENAI_API_BASE
        
        # 初始化同步和异步客户端
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_base if self.api_base else None
        )
        
        self.async_client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.api_base if self.api_base else None
        )
        
        logger.info(f"Initialized LLM client with model: {model}")
        
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 1500,
        tools: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        使用OpenAI API从LLM模型生成响应
        
        参数:
            messages: 包含角色和内容的消息对象列表
            temperature: 采样温度
            max_tokens: 生成的最大token数量
            tools: 提供给模型的可选工具列表
            
        返回:
            模型的响应结果
        """
        try:
            # 记录请求信息(不包括敏感信息)
            debug_messages = [f"{m['role']}: <content>" for m in messages]
            logger.debug(f"Sending request to LLM API with {len(messages)} messages: {debug_messages}")
            
            # 如果提供了工具，准备额外参数
            kwargs = {}
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            # 使用异步客户端发送请求
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # 将响应对象转换为字典
            response_dict = {
                "id": response.id,
                "object": "chat.completion",
                "created": response.created,
                "model": response.model,
                "choices": [
                    {
                        "index": choice.index,
                        "message": {
                            "role": choice.message.role,
                            "content": choice.message.content,
                        },
                        "finish_reason": choice.finish_reason
                    }
                    for choice in response.choices
                ]
            }
            
            # 如果存在工具调用，添加工具调用信息
            if hasattr(response.choices[0].message, "tool_calls") and response.choices[0].message.tool_calls:
                response_dict["choices"][0]["message"]["tool_calls"] = [
                    {
                        "id": tool_call.id,
                        "type": tool_call.type,
                        "function": {
                            "name": tool_call.function.name,
                            "arguments": tool_call.function.arguments
                        }
                    }
                    for tool_call in response.choices[0].message.tool_calls
                ]
            
            logger.debug(f"Received response from LLM API")
            return response_dict
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            raise Exception(f"Failed to generate response: {str(e)}")
            
    def sync_generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        用于简单使用场景的同步生成方法
        
        参数:
            prompt: 用户提示
            system_prompt: 可选的系统提示
            temperature: 采样温度
            
        返回:
            生成的文本响应
        """
        try:
            messages = []
            
            # 如果提供了系统提示，添加系统消息
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            # 添加用户消息
            messages.append({"role": "user", "content": prompt})
            
            # 使用同步客户端调用模型
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            # 返回第一个选择项消息的内容
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error in sync_generate: {str(e)}")
            return f"Error generating response: {str(e)}" 