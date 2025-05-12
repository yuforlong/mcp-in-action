# Milvus MCP Server

MCP (Machine Chat Protocol) server implementation for retrieving context from a Milvus vector database. This server provides tools for storing and searching knowledge documents and FAQs.

## Features

- Store and search knowledge documents in Milvus vector database
- Store and search FAQs in Milvus vector database
- RESTful API for accessing vector search capabilities
- MCP protocol support for AI agent integration

## Project Structure

```
mcp-server/
├── src/
│   └── milvus_mcp_server/
│       ├── __init__.py
│       ├── embedding.py        # Embedding service for text-to-vector conversion
│       ├── main.py             # Entry point for the server
│       ├── milvus_connector.py # Milvus database connector
│       ├── models.py           # Data models
│       ├── server.py           # MCP server implementation
│       └── settings.py         # Configuration settings
├── docker-compose.yml          # Docker composition for local development
├── Dockerfile                  # Docker image definition
├── pyproject.toml              # Project metadata and dependencies
├── README.md                   # Project documentation
├── requirements.txt            # Python dependencies
└── run.sh                      # Convenience script for running the server
```

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Milvus 2.0 or higher

### Installation

1. Clone the repository
2. Install the package:

```bash
pip install -e .
```

### Running the Server

You can run the server using the provided script:

```bash
./run.sh
```

Or directly with Python:

```bash
python -m milvus_mcp_server.main
```

### Docker Deployment

Build and run with Docker:

```bash
docker build -t milvus-mcp-server .
docker run -p 8080:8080 milvus-mcp-server
```

Or using Docker Compose:

```bash
docker-compose up
```

## Configuration

Configuration is handled through environment variables:

- `HOST`: Server host (default: "0.0.0.0")
- `PORT`: Server port (default: 8080)
- `MILVUS_HOST`: Milvus server host (default: "localhost")
- `MILVUS_PORT`: Milvus server port (default: 19530)

## MCP Tools

The server provides the following MCP tools:

- `storeKnowledge`: Store document into knowledge store for later retrieval
- `searchKnowledge`: Search for similar documents on natural language descriptions from knowledge store
- `storeFAQ`: Store document into FAQ store for later retrieval
- `searchFAQ`: Search for similar documents on natural language descriptions from FAQ store

## Development

### Project Structure

The project follows a standard Python package structure with the actual module code in the `src/milvus_mcp_server` directory. This makes it easier to debug and develop compared to the previous app-based structure.

### Running Tests

```bash
pytest
``` 