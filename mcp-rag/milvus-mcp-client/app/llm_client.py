import json
from typing import Dict, List, Any, Optional, Union
from loguru import logger
import os
from openai import OpenAI, AsyncOpenAI

from app.config import OPENAI_API_KEY, OPENAI_API_BASE, OPENAI_MODEL

class LLMClient:
    """Client for interacting with LLM models via OpenAI API."""
    
    def __init__(self, model: str = OPENAI_MODEL):
        """Initialize the LLM client.
        
        Args:
            model: The model name to use
        """
        self.model = model
        self.api_key = OPENAI_API_KEY
        self.api_base = OPENAI_API_BASE
        
        # Initialize sync and async clients
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
        """Generate a response from the LLM model using the OpenAI API.
        
        Args:
            messages: List of message objects with role and content
            temperature: The sampling temperature to use
            max_tokens: The maximum number of tokens to generate
            tools: Optional list of tools to provide to the model
            
        Returns:
            The response from the model
        """
        try:
            # Log the request (excluding sensitive information)
            debug_messages = [f"{m['role']}: <content>" for m in messages]
            logger.debug(f"Sending request to LLM API with {len(messages)} messages: {debug_messages}")
            
            # Prepare additional parameters if tools are provided
            kwargs = {}
            if tools:
                kwargs["tools"] = tools
                kwargs["tool_choice"] = "auto"
            
            # Send the request using the async client
            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            
            # Convert the response object to a dictionary
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
            
            # Add tool_calls if present
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
        """Synchronous generation for simpler use cases.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            temperature: The sampling temperature
            
        Returns:
            The generated text response
        """
        try:
            messages = []
            
            # Add system message if provided
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
                
            # Add user message
            messages.append({"role": "user", "content": prompt})
            
            # Call the model using the sync client
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature
            )
            
            # Return the content of the first choice's message
            return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Error in sync_generate: {str(e)}")
            return f"Error generating response: {str(e)}" 