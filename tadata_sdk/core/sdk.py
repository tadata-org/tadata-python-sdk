"""Core SDK functionality for the Tadata Platform."""

import urllib.parse
from datetime import datetime
from typing import Any, Dict, Literal, Optional, Union, overload

from ..errors.exceptions import SpecInvalidError
from ..http.client import ApiClient, Logger
from ..http.schemas import DeploymentResponse, MCPAuthConfig, UpsertDeploymentRequest
from ..openapi.source import OpenAPISpec
from .logger import create_default_logger


class DeploymentResult:
    """Result of a successful MCP deployment."""

    def __init__(self, response: DeploymentResponse) -> None:
        """Initialize a deployment result.

        Args:
            response: The raw API response from a successful deployment.

        Raises:
            SpecInvalidError: If the response data is missing or invalid.
        """
        if not response.ok or response.data is None:
            raise SpecInvalidError("Unexpected response format", details={"response": response})

        data = response.data
        self.deployment = data.deployment
        self.id = data.deployment.id
        self.updated = data.updated
        self.created_at = data.deployment.created_at or datetime.now()


@overload
def deploy(
    *,
    openapi_spec_path: str,
    api_key: str,
    base_url: Optional[str] = None,
    name: Optional[str] = None,
    auth_config: Optional[Dict[str, Any]] = None,
    api_base_url: str = "https://api.tadata.com",
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
    logger: Optional[Logger] = None,
    dev: bool = False,
) -> DeploymentResult: ...


@overload
def deploy(
    *,
    openapi_spec_url: str,
    api_key: str,
    base_url: Optional[str] = None,
    name: Optional[str] = None,
    auth_config: Optional[Dict[str, Any]] = None,
    api_base_url: str = "https://api.tadata.com",
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
    logger: Optional[Logger] = None,
    dev: bool = False,
) -> DeploymentResult: ...


@overload
def deploy(
    *,
    openapi_spec: Union[Dict[str, Any], OpenAPISpec],
    api_key: str,
    base_url: Optional[str] = None,
    name: Optional[str] = None,
    auth_config: Optional[Dict[str, Any]] = None,
    api_base_url: str = "https://api.tadata.com",
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
    logger: Optional[Logger] = None,
    dev: bool = False,
) -> DeploymentResult: ...


def deploy(
    *,
    openapi_spec_path: Optional[str] = None,
    openapi_spec_url: Optional[str] = None,
    openapi_spec: Optional[Union[Dict[str, Any], OpenAPISpec]] = None,
    base_url: Optional[str] = None,
    name: Optional[str] = None,
    auth_config: Optional[Dict[str, Any]] = None,
    api_key: str,
    api_base_url: str = "https://api.tadata.com",
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
    logger: Optional[Logger] = None,
    dev: bool = False,
) -> DeploymentResult:
    """Deploy a Model Context Protocol (MCP) server from an OpenAPI specification.

    You must provide exactly one of: openapi_spec_path, openapi_spec_url, or openapi_spec.

    Args:
        openapi_spec_path: Path to an OpenAPI specification file (JSON or YAML).
        openapi_spec_url: URL to an OpenAPI specification.
        openapi_spec: OpenAPI specification as a dictionary or OpenAPISpec object.
        base_url: Base URL of the API to proxy requests to. If not provided, will try to extract
            from the OpenAPI spec.
        name: Optional name for the deployment.
        auth_config: Configuration for authentication handling.
        api_key: Tadata API key for authentication.
        api_base_url: Tadata API base URL. Defaults to production API.
        api_version: Tadata API version.
        timeout: Request timeout in seconds.
        logger: Optional logger to use for SDK logs.
        dev: Whether to use the development environment.

    Returns:
        A DeploymentResult object containing details of the deployment.

    Raises:
        ValueError: If no OpenAPI specification source is provided, or if multiple sources are provided.
        SpecInvalidError: If the OpenAPI specification is invalid or cannot be processed.
        AuthError: If authentication with the Tadata API fails.
        ApiError: If the Tadata API returns an error.
        NetworkError: If a network error occurs.
    """
    # Set up logger
    log = logger or create_default_logger()
    log.info("Deploying MCP server from OpenAPI spec")

    # Use development API if requested
    if dev:
        api_base_url = "https://api.stage.tadata.com"

    # Validate input - must have exactly one openapi_spec source
    source_count = sum(1 for x in [openapi_spec_path, openapi_spec_url, openapi_spec] if x is not None)
    if source_count == 0:
        raise ValueError("One of openapi_spec_path, openapi_spec_url, or openapi_spec must be provided")
    if source_count > 1:
        raise ValueError("Only one of openapi_spec_path, openapi_spec_url, or openapi_spec should be provided")

    # Process OpenAPI spec from the provided source
    spec: Optional[OpenAPISpec] = None
    if openapi_spec_path is not None:
        log.info(f"Loading OpenAPI spec from file: {openapi_spec_path}")
        spec = OpenAPISpec.from_file(openapi_spec_path)
    elif openapi_spec_url is not None:
        log.info(f"Loading OpenAPI spec from URL: {openapi_spec_url}")
        # We'll use httpx to fetch the URL
        import httpx

        try:
            response = httpx.get(openapi_spec_url, timeout=timeout)
            response.raise_for_status()

            # Parse based on content-type or URL extension
            content_type = response.headers.get("content-type", "")
            if "json" in content_type:
                spec = OpenAPISpec.from_json(response.text)
            elif "yaml" in content_type or "yml" in content_type:
                spec = OpenAPISpec.from_yaml(response.text)
            else:
                # Try to infer from URL extension
                url_path = urllib.parse.urlparse(openapi_spec_url).path
                if url_path.lower().endswith((".json")):
                    spec = OpenAPISpec.from_json(response.text)
                elif url_path.lower().endswith((".yaml", ".yml")):
                    spec = OpenAPISpec.from_yaml(response.text)
                else:
                    # Default to trying JSON
                    spec = OpenAPISpec.from_json(response.text)
        except httpx.HTTPError as e:
            raise SpecInvalidError(
                f"Failed to fetch OpenAPI spec from URL: {str(e)}",
                details={"url": openapi_spec_url},
                cause=e,
            )
    elif isinstance(openapi_spec, dict):
        log.info("Using provided OpenAPI spec dictionary")
        spec = OpenAPISpec.from_dict(openapi_spec)
    elif openapi_spec is not None:
        # Must be OpenAPISpec instance
        log.info("Using provided OpenAPISpec instance")
        spec = openapi_spec

    # At this point, spec should be defined
    if spec is None:
        # This should never happen due to our validation above, but make type checker happy
        raise ValueError("Unable to obtain OpenAPI specification from provided sources")

    # Process auth config
    mcp_auth_config = MCPAuthConfig()
    if auth_config is not None:
        mcp_auth_config = MCPAuthConfig.model_validate(auth_config)

    # Create API client
    client = ApiClient(
        api_key=api_key,
        base_url=api_base_url,
        version=api_version,
        timeout=timeout,
        logger=log,
    )

    # Create deployment request
    request = UpsertDeploymentRequest(
        open_api_spec=spec,
        name=name,
        base_url=base_url,
        auth_config=mcp_auth_config,
    )

    # Make API request to deploy
    api_response: DeploymentResponse = client.deploy_from_openapi(request)

    # Process response
    return DeploymentResult(api_response)
