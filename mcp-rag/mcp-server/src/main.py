import argparse
import logging
import os
import signal
import sys
from server import mcp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def handle_shutdown(sig, frame):
    """Handle graceful shutdown on signals"""
    logger.info(f"Received signal {sig}, shutting down MCP server...")
    sys.exit(0)


def main():
    """Entry point for the milvus-mcp-server"""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="milvus-mcp-server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="sse",
    )
    parser.add_argument(
        "--host",
        type=str,
        help="Host to bind the server to",
    )
    parser.add_argument(
        "--port",
        type=int,
        help="Port to bind the server to",
    )
    args = parser.parse_args()
    
    # Override settings with command line arguments if provided
    if args.host:
        mcp.settings.host = args.host
    if args.port:
        mcp.settings.port = args.port
    
    # Log startup info
    logger.info(f"Starting milvus-mcp-server with transport: {args.transport}")
    logger.info(f"Server will listen on {mcp.settings.host}:{mcp.settings.port}")
    
    # Run the server
    try:
        mcp.run(transport=args.transport)
    except Exception as e:
        logger.error(f"Error running server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 