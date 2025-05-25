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

## Django Support

You can deploy Django REST Framework applications directly using drf-spectacular:

```python
import os
import tadata_sdk

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
import django
django.setup()

# Your Django settings should include:
# INSTALLED_APPS = [
#     # ... your apps
#     'rest_framework',
#     'drf_spectacular',
# ]
# REST_FRAMEWORK = {
#     'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
# }

# Deploy using Django schema extraction
result = tadata_sdk.deploy(
    use_django=True,  # Extract schema from configured Django application
    api_key="TADATA_API_KEY",
    base_url="https://api.myservice.com",
    name="My Django Deployment"
)

print(f"Deployed Django app: {result.id}")
```

**Note:** Django, Django REST Framework, and drf-spectacular are not required dependencies. If you want to use Django support, install them separately:

```bash
pip install django djangorestframework drf-spectacular
```
