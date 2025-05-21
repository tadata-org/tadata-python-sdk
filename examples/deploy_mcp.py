#!/usr/bin/env python3
import os
import sys

# Add the project root to the Python path if running from examples directory
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import logging
from typing import Dict, Any

from tadata_sdk import deploy


# Sample simple OpenAPI spec
SAMPLE_SPEC: Dict[str, Any] = {
    "openapi": "3.0.0",
    "info": {
        "title": "Sample API",
        "version": "1.0.0",
        "description": "A sample API specification for Tadata SDK example",
    },
    "paths": {
        "/hello": {
            "get": {
                "summary": "Say hello",
                "operationId": "sayHello",
                "responses": {
                    "200": {
                        "description": "A hello message",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                    },
                                }
                            }
                        },
                    }
                },
            }
        }
    },
    "servers": [{"url": "https://example.com/api"}],
}


def main() -> None:
    """Run the example."""
    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Get API key from environment variable
    api_key = os.environ.get("TADATA_API_KEY")
    if not api_key:
        print("Error: TADATA_API_KEY environment variable is required")
        sys.exit(1)

    print("Deploying MCP server from OpenAPI spec...")

    # Method 1: Using a dictionary directly
    result = deploy(
        openapi_spec=SAMPLE_SPEC,
        api_key=api_key,
        # Optional: specify a different base URL for the API
        base_url="https://my-actual-api.example.com/v1",
        name="Sample API Deployment",
    )

    print("Successfully deployed MCP server!")
    print(f"  ID: {result.id}")
    print(f"  Created at: {result.created_at}")
    print(f"  Updated: {result.updated}")

    # Method 2: Using an OpenAPISpec object
    # spec = OpenAPISpec.from_dict(SAMPLE_SPEC)
    # result = deploy(openapi_spec=spec, api_key=api_key)

    # Method 3: Loading from a file
    # result = deploy(openapi_spec_path="./openapi.json", api_key=api_key)

    # Method 4: Loading from a URL
    # result = deploy(openapi_spec_url="https://example.com/openapi.json", api_key=api_key)


if __name__ == "__main__":
    main()
