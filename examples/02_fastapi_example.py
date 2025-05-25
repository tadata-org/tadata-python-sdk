import logging
import os

import tadata_sdk

# Configure logging to display SDK logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

try:
    from fastapi import FastAPI

    # Create a simple FastAPI app
    app = FastAPI(title="My API", version="1.0.0", description="A simple API example for Tadata deployment")

    @app.get("/")
    def read_root():
        """Root endpoint that returns a greeting."""
        return {"message": "Hello World"}

    @app.get("/items/{item_id}")
    def read_item(item_id: int, q: str | None = None):
        """Get an item by ID with optional query parameter."""
        return {"item_id": item_id, "q": q}

    @app.post("/items/")
    def create_item(item: dict):
        """Create a new item."""
        return {"item": item, "status": "created"}

    # Deploy the FastAPI app directly
    result = tadata_sdk.deploy(
        api_key=os.getenv("TADATA_API_KEY", ""),
        fastapi_app=app,
        base_url="https://my-api.example.com",  # Your actual API base URL
        name="My FastAPI Deployment",
    )

    print(f"Deployment successful! ID: {result.id}")
    print(f"Created at: {result.created_at}")
    print(f"Updated: {result.updated}")

except ImportError:
    print("FastAPI is not installed.")
    print("This example demonstrates how to deploy a FastAPI app using tadata-sdk.")
