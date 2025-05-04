#!/bin/bash

# Set environment variables
export LLM_API_KEY="sk-666814d1fbc447e4f2ab401be341a9a7598"
export MCP_SERVER_HOST="http://localhost:8080/sse"
export LLM_API_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export LLM_MODEL="qwen-max"

# Function to check if server is running
check_server() {
    echo "Checking if MCP server is ready at $MCP_SERVER_HOST..."
    # Try a simple curl to see if the server responds
    curl -s -o /dev/null -w "%{http_code}" "$MCP_SERVER_HOST" | grep -q "200"
    return $?
}

# Wait for server with retry
wait_for_server() {
    local max_attempts=10
    local wait_seconds=2
    local attempt=1
    
    echo "Waiting for MCP server to become ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if check_server; then
            echo "MCP server is ready!"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: Server not ready yet, waiting ${wait_seconds}s..."
        sleep $wait_seconds
        attempt=$((attempt + 1))
    done
    
    echo "Warning: Could not confirm server is ready after $max_attempts attempts"
    echo "Continuing anyway, but operation may fail..."
    return 1
}

# Wait for server to be ready
wait_for_server

# Run the knowledge manager with arguments
echo "Starting knowledge manager..."
python knowledge_manager.py "$@" 