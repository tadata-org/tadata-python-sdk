"""Core SDK functionality for the Tadata Platform."""

import logging
import urllib.parse
from datetime import datetime
from typing import Any, Dict, Literal, Optional, Union, overload
from typing_extensions import Annotated, Doc

from ..errors.exceptions import SpecInvalidError
from ..http.client import ApiClient
from ..http.schemas import DeploymentResponse, AuthConfig, UpsertDeploymentRequest
from ..openapi.source import OpenAPISpec


logger = logging.getLogger(__name__)


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
    auth_config: Optional[AuthConfig] = None,
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
) -> DeploymentResult: ...


@overload
def deploy(
    *,
    openapi_spec_url: str,
    api_key: str,
    base_url: Optional[str] = None,
    name: Optional[str] = None,
    auth_config: Optional[AuthConfig] = None,
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
) -> DeploymentResult: ...


@overload
def deploy(
    *,
    openapi_spec: Union[Dict[str, Any], OpenAPISpec],
    api_key: str,
    base_url: Optional[str] = None,
    name: Optional[str] = None,
    auth_config: Optional[AuthConfig] = None,
    api_version: Literal["05-2025", "latest"] = "latest",
    timeout: int = 30,
) -> DeploymentResult: ...


def deploy(
    *,
    openapi_spec_path: Annotated[Optional[str], Doc("Path to an OpenAPI specification file (JSON or YAML)")] = None,
    openapi_spec_url: Annotated[Optional[str], Doc("URL to an OpenAPI specification")] = None,
    openapi_spec: Annotated[
        Optional[Union[Dict[str, Any], OpenAPISpec]], Doc("OpenAPI specification as a dictionary or OpenAPISpec object")
    ] = None,
    base_url: Annotated[
        Optional[str],
        Doc("Base URL of the API to proxy requests to. If not provided, will try to extract from the OpenAPI spec"),
    ] = None,
    name: Annotated[Optional[str], Doc("Optional name for the deployment")] = None,
    auth_config: Annotated[
        Optional[AuthConfig], Doc("Configuration for authentication handling between the MCP and your API")
    ] = None,
    api_key: Annotated[str, Doc("Tadata API key for authentication")],
    api_version: Annotated[Literal["05-2025", "latest"], Doc("Tadata API version")] = "latest",
    timeout: Annotated[int, Doc("Request timeout in seconds")] = 30,
) -> DeploymentResult:
    """Deploy a Model Context Protocol (MCP) server from an OpenAPI specification.

    You must provide exactly one of: openapi_spec_path, openapi_spec_url, or openapi_spec.

    Returns:
        A DeploymentResult object containing details of the deployment.

    Raises:
        ValueError: If no OpenAPI specification source is provided, or if multiple sources are provided.
        SpecInvalidError: If the OpenAPI specification is invalid or cannot be processed.
        AuthError: If authentication with the Tadata API fails.
        ApiError: If the Tadata API returns an error.
        NetworkError: If a network error occurs.
    """
    logger.info("Deploying MCP server from OpenAPI spec")

    # Validate input - must have exactly one openapi_spec source
    source_count = sum(1 for x in [openapi_spec_path, openapi_spec_url, openapi_spec] if x is not None)
    if source_count == 0:
        raise ValueError("One of openapi_spec_path, openapi_spec_url, or openapi_spec must be provided")
    if source_count > 1:
        raise ValueError("Only one of openapi_spec_path, openapi_spec_url, or openapi_spec should be provided")

    # Process OpenAPI spec from the provided source
    spec: Optional[OpenAPISpec] = None
    if openapi_spec_path is not None:
        logger.info(f"Loading OpenAPI spec from file: {openapi_spec_path}")
        spec = OpenAPISpec.from_file(openapi_spec_path)
    elif openapi_spec_url is not None:
        logger.info(f"Loading OpenAPI spec from URL: {openapi_spec_url}")
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
        logger.info("Using provided OpenAPI spec dictionary")
        spec = OpenAPISpec.from_dict(openapi_spec)
    elif openapi_spec is not None:
        # Must be OpenAPISpec instance
        logger.info("Using provided OpenAPISpec instance")
        spec = openapi_spec

    # At this point, spec should be defined
    if spec is None:
        # This should never happen due to our validation above, but make type checker happy
        raise ValueError("Unable to obtain OpenAPI specification from provided sources")

    mcp_auth_config = AuthConfig()
    if auth_config is not None:
        mcp_auth_config = AuthConfig.model_validate(auth_config.model_dump())

    # Create API client
    client = ApiClient(
        api_key=api_key,
        version=api_version,
        timeout=timeout,
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
