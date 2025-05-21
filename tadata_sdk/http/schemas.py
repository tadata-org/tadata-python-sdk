from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field

from ..openapi.source import OpenAPISpec


class ErrorCode(str, Enum):
    """Standard error codes returned by the Tadata API."""

    VALIDATION_ERROR = "VALIDATION_ERROR"
    SERVICE_VALIDATION_ERROR = "SERVICE_VALIDATION_ERROR"
    JSON_PARSE_ERROR = "JSON_PARSE_ERROR"
    INVALID_CONTENT_TYPE = "INVALID_CONTENT_TYPE"
    AUTH_ERROR = "AUTH_ERROR"
    NOT_FOUND = "NOT_FOUND"
    INTERNAL_ERROR = "INTERNAL_ERROR"


class ValidationError(BaseModel):
    """Validation error details."""

    field: str
    message: str
    source: Optional[str] = None


class ApiError(BaseModel):
    """API error details."""

    code: ErrorCode
    message: str
    errors: Optional[List[ValidationError]] = None
    details: Optional[Any] = None


class ApiResponse(BaseModel):
    """Generic API response envelope.

    Provides consistent structure for all API responses, whether success or error.
    """

    ok: bool
    status: int
    data: Optional[Any] = None
    error: Optional[ApiError] = None
    model_config = ConfigDict(extra="forbid")


class MCPAuthConfig(BaseModel):
    """Configuration for MCP authentication handling."""

    pass_headers: List[str] = Field(
        default=[
            "authorization",
            "api-key",
            "api_key",
            "apikey",
            "x-api-key",
            "x-apikey",
        ],
        description="Headers to pass through from MCP clients to the upstream API",
    )
    pass_query_params: List[str] = Field(
        default=["api-key", "api_key", "apikey"],
        description="Query parameters to pass through from MCP clients to the upstream API",
    )
    pass_json_body_params: List[str] = Field(
        default=[],
        description="JSON body parameters to extract and pass to the upstream API",
    )
    pass_form_data_params: List[str] = Field(
        default=[],
        description="Form data parameters to extract and pass to the upstream API",
    )


class UpsertDeploymentRequest(BaseModel):
    """Request to deploy or update an MCP server."""

    open_api_spec: OpenAPISpec = Field(..., description="The OpenAPI specification")
    name: Optional[str] = Field(None, description="Optional name for the deployment")
    base_url: Optional[str] = Field(None, description="Base URL of the API to proxy requests to")
    auth_config: MCPAuthConfig = Field(
        default_factory=MCPAuthConfig,
        description="Configuration for authentication handling",
    )


class DeploymentResponseData(BaseModel):
    """Deployment data in a successful response."""

    id: str
    created_at: Optional[datetime] = None
    created_by: str
    updated_by: str
    mcp_server_id: str
    open_api_spec_hash: str
    mcp_spec_hash: str
    status: str


class UpsertDeploymentResponseData(BaseModel):
    """Data for a successful deployment response."""

    updated: bool
    deployment: DeploymentResponseData


class DeploymentResponse(ApiResponse):
    """API response for deployment operations."""

    data: Optional[UpsertDeploymentResponseData] = None
