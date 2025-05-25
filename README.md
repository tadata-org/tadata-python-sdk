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
import tadata_sdk

# Deploy from a dictionary
result = tadata_sdk.deploy(
    openapi_spec={
        "openapi": "3.0.0",
        "info": {"title": "My API", "version": "1.0.0"},
        "paths": {"/hello": {"get": {"responses": {"200": {"description": "OK"}}}}},
    },
    api_key="TADATA_API_KEY",  # Required
    name="My MCP Deployment",  # Optional
    base_url="https://api.myservice.com",  # Required if no valid and absolute base url is found in the openapi spec
)

print(f"Deployed MCP server: {result.id}")
print(f"Created at: {result.created_at}")
```

## FastAPI Support

You can deploy FastAPI applications directly without manually extracting the OpenAPI specification:

```python
import tadata_sdk
from fastapi import FastAPI

# Create your FastAPI app
app = FastAPI(title="My API", version="1.0.0")

@app.get("/hello")
def hello():
    return {"message": "Hello World"}

# Deploy the FastAPI app directly
result = tadata_sdk.deploy(
    fastapi_app=app,
    api_key="TADATA_API_KEY",
    base_url="https://api.myservice.com",
    name="My FastAPI Deployment"
)

print(f"Deployed FastAPI app: {result.id}")
```

**Note:** FastAPI is not a required dependency. If you want to use FastAPI support, install it separately:

```bash
pip install fastapi
```
