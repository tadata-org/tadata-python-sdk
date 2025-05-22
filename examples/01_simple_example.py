import logging
import tadata_sdk

import os

# Configure logging to display SDK logs
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

tadata_sdk.deploy(
    api_key=os.getenv("TADATA_API_KEY", ""),
    openapi_spec_path="examples/petstore_openapi.json",
    base_url="https://petstore3.swagger.io/api/v3",
)
