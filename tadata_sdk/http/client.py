import logging
from typing import Any, Dict, Literal, Optional
from typing_extensions import Annotated, Doc

import httpx

from ..errors.exceptions import ApiError, AuthError, NetworkError
from .schemas import DeploymentResponse, UpsertDeploymentRequest


logger = logging.getLogger(__name__)


class ApiClient:
    """HTTP client for the Tadata API.

    This client handles communication with the Tadata API, including authentication,
    request formatting, and error handling.
    """

    def __init__(
        self,
        api_key: Annotated[str, Doc("The Tadata API key for authentication")],
        version: Annotated[Literal["05-2025", "latest"], Doc("The API version to use")] = "latest",
        timeout: Annotated[int, Doc("Request timeout in seconds")] = 30,
    ) -> None:
        self.api_key = api_key
        self.base_url = "https://api.tadata.com"
        self.version = version
        self.timeout = timeout

        self.client = httpx.Client(
            timeout=timeout,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "x-api-version": version,
            },
        )

    def _handle_request_error(self, error: httpx.RequestError, message: str = "Network error occurred") -> None:
        """Handle request errors by raising appropriate domain exceptions.

        Args:
            error: The original request error.
            message: Custom error message to include.

        Raises:
            NetworkError: For network-related errors.
        """
        logger.error(f"Request error: {error}")
        raise NetworkError(f"{message}: {str(error)}", cause=error)

    def _handle_response_error(self, response: httpx.Response) -> None:
        """Handle error responses by raising appropriate domain exceptions.

        Args:
            response: The HTTP response object.

        Raises:
            AuthError: For authentication errors (401, 403).
            ApiError: For all other API errors.
        """
        status_code = response.status_code
        try:
            error_data = response.json()
            error_msg = (
                error_data.get("error", {}).get("message", f"API error: {status_code}")
                if isinstance(error_data, dict)
                else f"API error: {status_code}"
            )
        except Exception:
            error_data = {"body": response.text}
            error_msg = f"API error: {status_code}"

        if status_code in (401, 403):
            logger.error(f"Authentication error: {status_code}")
            raise AuthError(error_msg, cause=Exception(str(error_data)))

        logger.error(f"API error: {status_code} - {error_msg}\n{error_data}")
        raise ApiError(error_msg, status_code, error_data)

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> httpx.Response:
        """Make an HTTP request to the Tadata API.

        Args:
            method: HTTP method (GET, POST, etc.).
            path: API endpoint path.
            data: Optional request body data.
            params: Optional query parameters.
            headers: Optional additional headers.

        Returns:
            The HTTP response.

        Raises:
            NetworkError: For network-related errors.
            AuthError: For authentication errors.
            ApiError: For API errors.
        """
        url = f"{self.base_url}{path}"
        request_params = {} if params is None else params.copy()
        request_params["apiKey"] = self.api_key
        request_headers = {} if headers is None else headers.copy()

        logger.debug(f"Making request: {method} {url}")

        try:
            if data is not None:
                json_data = data
                response = self.client.request(
                    method,
                    url,
                    json=json_data,
                    params=request_params,
                    headers=request_headers,
                )
            else:
                response = self.client.request(method, url, params=request_params, headers=request_headers)

            if response.is_error:
                self._handle_response_error(response)

            return response

        except httpx.RequestError as e:
            self._handle_request_error(e)
            raise  # This will never be reached, but makes type checking happy

    def deploy_from_openapi(self, request: UpsertDeploymentRequest) -> DeploymentResponse:
        """Deploy or update an MCP server from an OpenAPI specification.

        Args:
            request: The deployment request with OpenAPI spec and configuration.

        Returns:
            The deployment response containing details about the deployed MCP server.

        Raises:
            NetworkError: For network-related errors.
            AuthError: For authentication errors.
            ApiError: For API errors.
        """
        logger.info("Deploying MCP server from OpenAPI spec")

        response = self._request(
            "POST", "/api/deployments/from-openapi", data=request.model_dump(by_alias=True, exclude_none=True)
        )

        try:
            result = DeploymentResponse.model_validate(response.json())
            return result
        except Exception as e:
            logger.error(f"Failed to parse deployment response: {e}")
            raise ApiError(
                "Failed to parse deployment response",
                response.status_code,
                response.json(),
                cause=e,
            )
