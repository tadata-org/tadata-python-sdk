# Tadata Python SDK

The Tadata Python SDK provides an easy-to-use interface for deploying Model Context Protocol (MCP) servers from OpenAPI specifications.

## Installation

```bash
# Install with pip
pip install tadata-sdk

# Or with uv (recommended)
uv pip install tadata-sdk
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

## OpenAPI Specification Sources

The SDK supports multiple ways to provide your OpenAPI specification:

```python
# From a file (JSON or YAML)
result = deploy(
    openapi_spec_path="./openapi.json",  # or .yaml
    api_key="your-tadata-api-key",
)

# From a URL
result = deploy(
    openapi_spec_url="https://example.com/openapi.json",  # or .yaml
    api_key="your-tadata-api-key",
)

# From a dictionary
result = deploy(
    openapi_spec={
        "openapi": "3.0.0",
        "info": {"title": "My API", "version": "1.0.0"},
        "paths": {"/hello": {"get": {"responses": {"200": {"description": "OK"}}}}},
    },
    api_key="your-tadata-api-key",
)

# From an OpenAPISpec object
spec = OpenAPISpec.from_file("./openapi.json")
result = deploy(
    openapi_spec=spec,
    api_key="your-tadata-api-key",
)
```

## Authentication Handling

You can configure how authentication is handled between the MCP server and your API:

```python
result = deploy(
    openapi_spec_path="./openapi.json",
    api_key="your-tadata-api-key",
    auth_config={
        "pass_headers": ["authorization", "x-api-key"],  # Headers to pass through
        "pass_query_params": ["api_key"],  # Query parameters to pass through
        "pass_json_body_params": [],  # JSON body parameters to extract
        "pass_form_data_params": [],  # Form data parameters to extract
    }
)
```

## Error Handling

The SDK provides specific error classes for better error handling:

```python
from tadata_sdk import deploy, SpecInvalidError, AuthError, ApiError, NetworkError

try:
    result = deploy(
        openapi_spec_path="./openapi.json",
        api_key="your-tadata-api-key",
    )
    print(f"Deployed MCP server: {result.id}")
except SpecInvalidError as e:
    print(f"Invalid OpenAPI spec: {e}")
    print(f"Details: {e.details}")
except AuthError as e:
    print(f"Authentication failed: {e}")
except ApiError as e:
    print(f"API error: {e}, Status: {e.status_code}")
except NetworkError as e:
    print(f"Network error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Advanced Usage

### Custom Logging

You can provide your own logger implementation:

```python
import logging
from tadata_sdk import deploy

# Configure a custom logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("tadata-example")

# Use the custom logger
result = deploy(
    openapi_spec_path="./openapi.json",
    api_key="your-tadata-api-key",
    logger=logger,
)
```

### Development Environment

For testing purposes, you can use the development environment:

```python
result = deploy(
    openapi_spec_path="./openapi.json",
    api_key="your-tadata-api-key",
    dev=True,  # Use development environment
)
```

## License

MIT