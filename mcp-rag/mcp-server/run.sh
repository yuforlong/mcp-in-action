#!/bin/bash

# Set environment variables if needed
export HOST="0.0.0.0"
export PORT="8080"

# Ensure PYTHONPATH includes the current directory
export PYTHONPATH=$PYTHONPATH:$(pwd)

# Check for Milvus connection
echo "Checking Milvus connection..."
if nc -z localhost 19530; then
    echo "Milvus is running on localhost:19530"
else
    echo "Warning: Milvus does not appear to be running on localhost:19530"
    echo "Please make sure Milvus is running before starting the server"
    echo "You can continue anyway, but the server may not function correctly"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Start the server
echo "Starting Milvus MCP Server..."
python -m milvus_mcp_server.main --host $HOST --port $PORT 