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


class AuthConfig(BaseModel):
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
        alias="passHeaders",
    )
    pass_query_params: List[str] = Field(
        default=["api-key", "api_key", "apikey"],
        description="Query parameters to pass through from MCP clients to the upstream API",
        alias="passQueryParams",
    )
    pass_json_body_params: List[str] = Field(
        default=[],
        description="JSON body parameters to extract and pass to the upstream API",
        alias="passJsonBodyParams",
    )
    pass_form_data_params: List[str] = Field(
        default=[],
        description="Form data parameters to extract and pass to the upstream API",
        alias="passFormDataParams",
    )

    model_config = ConfigDict(populate_by_name=True)


class UpsertDeploymentRequest(BaseModel):
    """Request to deploy or update an MCP server."""

    open_api_spec: OpenAPISpec = Field(..., description="The OpenAPI specification", alias="openApiSpec")
    name: Optional[str] = Field(None, description="Optional name for the deployment")
    base_url: Optional[str] = Field(None, description="Base URL of the API to proxy requests to", alias="baseUrl")
    auth_config: AuthConfig = Field(
        default_factory=AuthConfig, description="Configuration for authentication handling", alias="authConfig"
    )

    model_config = ConfigDict(populate_by_name=True)


class DeploymentResponseData(BaseModel):
    """Deployment data in a successful response."""

    id: str
    created_at: Optional[datetime] = Field(None, alias="createdAt")
    created_by: Optional[str] = Field(None, alias="createdBy")
    updated_by: Optional[str] = Field(None, alias="updatedBy")
    mcp_server_id: Optional[str] = Field(None, alias="mcpServerId")
    open_api_spec_hash: Optional[str] = Field(None, alias="openAPISpecHash")
    mcp_spec_hash: Optional[str] = Field(None, alias="mcpSpecHash")
    status: Optional[str] = Field(None)

    model_config = ConfigDict(populate_by_name=True, extra="allow")


class UpsertDeploymentResponseData(BaseModel):
    """Data for a successful deployment response."""

    updated: bool
    deployment: DeploymentResponseData

    model_config = ConfigDict(populate_by_name=True)


class DeploymentResponse(ApiResponse):
    """API response for deployment operations."""

    data: Optional[UpsertDeploymentResponseData] = None
