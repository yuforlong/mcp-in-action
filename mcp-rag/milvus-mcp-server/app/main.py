import os
import asyncio
import signal
import sys
from loguru import logger
import uvicorn
from app.utils.logging import get_logger
from app.mcp_server import MilvusMCPServer

# Configure logging
logger = get_logger()

# Global server instance for graceful shutdown
mcp_server = None
# Flag to indicate initialization completion
initialization_complete = False

async def initialize_server():
    """Initialize MCP server with proper settings"""
    global mcp_server, initialization_complete
    # Create MCP server instance and initialize it
    mcp_server = MilvusMCPServer()
    
    # Get server port from environment variable or use default
    port = int(os.getenv("PORT", "8080"))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Configure server settings
    mcp_server.settings.host = host
    mcp_server.settings.port = port
    
    # Indicate that initialization is complete
    initialization_complete = True
    logger.info("MCP server initialization complete")
    
    # Return initialized server
    return mcp_server, host, port

def handle_shutdown(sig, frame):
    """Handle graceful shutdown on signals"""
    logger.info(f"Received signal {sig}, shutting down MCP server...")
    if mcp_server:
        # Close any open connections
        logger.info("Closing MCP server connections...")
    sys.exit(0)

def start_server():
    """Start the MCP server with proper initialization"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Get server settings
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Initialize server
        mcp_server, host, port = loop.run_until_complete(initialize_server())
        
        # Log startup
        logger.info(f"Starting Milvus MCP Server on {host}:{port}")
        
        # Run server with SSE transport
        mcp_server.run(transport='sse')
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_server() 