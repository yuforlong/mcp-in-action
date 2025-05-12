import asyncio
from typing import Dict, List, Any, Optional, Union, Callable
from loguru import logger
from mcp.client.sse import sse_client 
from mcp import ClientSession
from contextlib import AsyncExitStack
from app.config import MCP_SERVER_URL, TOOLS
import json

class MCPClient:
    """Client for interacting with the MCP server."""
    
    def __init__(self, server_url: str = MCP_SERVER_URL):
        """Initialize the MCP client.
        
        Args:
            server_url: URL of the MCP server
        """
        self.server_url = server_url
        self.client = None
        self.tools = {}
        self._connected = False
        self.exit_stack = AsyncExitStack()
        self.session = None
        logger.info(f"Initialized MCP client with server URL: {server_url}")
        
    async def __aenter__(self):
        """Async context manager entry method."""
        if not self._connected:
            await self.connect()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit method."""
        await self.close()
        
    async def connect(self) -> None:
        """Connect to the MCP server and get available tools."""
        try:
            logger.info(f"Connecting to MCP server at {self.server_url}...")
            self.client = sse_client(self.server_url)
            
            # Initialize the client connection using async context manager
            stdio_transport = await self.exit_stack.enter_async_context(self.client)
            read, write = stdio_transport
            
            # Create client session
            self.session = await self.exit_stack.enter_async_context(ClientSession(read, write))
            
            # Initialize the session
            await self.session.initialize()
            
            # Get available tools
            tools_response = await self.session.list_tools()
            available_tools = tools_response.tools
            
            # Check if our required tools are available
            for tool_name in TOOLS:
                logger.info(f"Checking for tool: {tool_name}")
                tool_found = False
                for tool in available_tools:
                    if tool.name == tool_name:
                        # Create a closure to capture the tool name
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
        """Store knowledge content in the MCP server.
        
        Args:
            content: The text content to store
            metadata: Optional metadata associated with the content
            
        Returns:
            Response from the server
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
        """Search for knowledge content in the MCP server.
        
        Args:
            query: The search query
            size: Maximum number of results to return
            
        Returns:
            List of matching knowledge content
        """
        if not self._connected:
            await self.connect()
            
        tool = self.tools.get("searchKnowledge")
        if not tool:
            raise Exception("searchKnowledge tool not available")
            
        try:
            response = await tool(query=query, size=size)
            
            # Handle the CallToolResult object
            # Extract results from the response content
            results = []
            if hasattr(response, "content") and response.content:
                # Try to parse the content as JSON if it's a string
                for part in response.content:
                    if hasattr(part, "text") and part.text:
                        try:
                            result_data = json.loads(part.text)
                            if isinstance(result_data, dict) and "results" in result_data:
                                results = result_data["results"]
                            elif isinstance(result_data, list):
                                results = result_data
                        except json.JSONDecodeError:
                            # If not valid JSON, use the text as is
                            logger.warning(f"Could not parse JSON from searchKnowledge response: {part.text}")
            
            logger.info(f"Found {len(results)} knowledge results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search knowledge: {str(e)}")
            raise Exception(f"Failed to search knowledge: {str(e)}")
            
    async def store_faq(self, question: str, answer: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Store FAQ content in the MCP server.
        
        Args:
            question: The FAQ question
            answer: The FAQ answer
            metadata: Optional metadata associated with the FAQ
            
        Returns:
            Response from the server
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
        """Search for FAQ content in the MCP server.
        
        Args:
            query: The search query
            size: Maximum number of results to return
            
        Returns:
            List of matching FAQ content
        """
        if not self._connected:
            await self.connect()
            
        tool = self.tools.get("searchFAQ")
        if not tool:
            raise Exception("searchFAQ tool not available")
            
        try:
            response = await tool(query=query, size=size)
            
            # Handle the CallToolResult object
            # Extract results from the response content
            results = []
            if hasattr(response, "content") and response.content:
                # Try to parse the content as JSON if it's a string
                for part in response.content:
                    if hasattr(part, "text") and part.text:
                        try:
                            result_data = json.loads(part.text)
                            if isinstance(result_data, dict) and "results" in result_data:
                                results = result_data["results"]
                            elif isinstance(result_data, list):
                                results = result_data
                        except json.JSONDecodeError:
                            # If not valid JSON, use the text as is
                            logger.warning(f"Could not parse JSON from searchFAQ response: {part.text}")
            
            logger.info(f"Found {len(results)} FAQ results for query: {query}")
            return results
        except Exception as e:
            logger.error(f"Failed to search FAQ: {str(e)}")
            raise Exception(f"Failed to search FAQ: {str(e)}")
            
    async def close(self) -> None:
        """Close the connection to the MCP server."""
        if self._connected:
            try:
                # First clear the tools dictionary
                self.tools = {}
                
                # Explicitly set connected flag to False before closing
                self._connected = False
                
                # Close the exit stack which will handle all the async context managers
                try:
                    await self.exit_stack.aclose()
                    logger.info("Closed connection to MCP server")
                except RuntimeError as e:
                    # Ignore specific RuntimeError about generator exit
                    if "generator didn't stop after athrow()" in str(e) or "unhandled errors in a TaskGroup" in str(e):
                        logger.warning(f"Ignoring known SSE connection cleanup issue: {str(e)}")
                    else:
                        # Re-raise if it's not the specific error we're handling
                        raise
            except Exception as e:
                logger.error(f"Error closing MCP connection: {str(e)}")
            finally:
                # Ensure these are set to None even if exceptions occur
                self.session = None
                self.client = None 