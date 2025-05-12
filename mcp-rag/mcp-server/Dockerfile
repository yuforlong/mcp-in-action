FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install the package in development mode
COPY . .
RUN pip install -e .

# Set default environment variables
ENV HOST="0.0.0.0"
ENV PORT="8080"

# Expose the port
EXPOSE 8080

# Set health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python -c "import socket; socket.socket().connect((\"localhost\", 8080))" || exit 1

# Set entrypoint
ENTRYPOINT ["python", "-m", "milvus_mcp_server.main"]
CMD ["--transport", "sse"] 