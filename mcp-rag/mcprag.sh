#!/bin/bash

# Stop any running server instances
echo "Stopping existing MCP server instances..."
pkill -f "python -m app.main" || true

# Start the Milvus MCP server
echo "Starting Milvus MCP Server..."
cd milvus-mcp-server
./run.sh &

# Give the server some time to initialize
echo "Waiting for server initialization (10 seconds)..."
sleep 30

# Back to original directory
cd ..

# Now run the client command
echo "Starting client with command: $*"
cd mcp-client
./run.sh "$@" 