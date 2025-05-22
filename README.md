# Tadata Python SDK

The Tadata Python SDK provides an easy-to-use interface for deploying Model Context Protocol (MCP) servers from OpenAPI specifications.

## Installation

```bash
# With uv (recommended)
uv add tadata-sdk

# With pip
pip install tadata-sdk
```

## Quickstart

Deploy a Model Context Protocol (MCP) server with your OpenAPI specification:

```python
from tadata_sdk import deploy, OpenAPISpec

# Deploy from a dictionary
result = deploy(
    openapi_spec={
        "openapi": "3.0.0",
        "info": {"title": "My API", "version": "1.0.0"},
        "paths": {"/hello": {"get": {"responses": {"200": {"description": "OK"}}}}},
    },
    api_key="your-tadata-api-key",
    name="My MCP Deployment",  # Optional
    base_url="https://api.myservice.com",  # Optional
)

print(f"Deployed MCP server: {result.id}")
print(f"Created at: {result.created_at}")
```
