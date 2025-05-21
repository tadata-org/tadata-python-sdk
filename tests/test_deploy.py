from unittest.mock import MagicMock, patch

import pytest

from tadata_sdk import deploy
from tadata_sdk.errors.exceptions import ApiError
from tadata_sdk.http.schemas import DeploymentResponse, UpsertDeploymentResponseData
from tadata_sdk.openapi.source import OpenAPISpec


@pytest.fixture
def valid_openapi_dict():
    """Fixture with a valid OpenAPI spec as a dictionary."""
    return {
        "openapi": "3.0.0",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
        },
        "paths": {
            "/test": {
                "get": {
                    "responses": {
                        "200": {
                            "description": "OK",
                        }
                    }
                }
            }
        },
    }


@pytest.fixture
def mock_api_client():
    """Fixture that returns a mock ApiClient."""
    with patch("tadata_sdk.core.sdk.ApiClient") as mock_client_class:
        # Create a mock instance
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        # Create a successful response
        mock_response = DeploymentResponse(
            ok=True,
            status=201,
            data=UpsertDeploymentResponseData.model_validate(
                {
                    "updated": False,
                    "deployment": {
                        "id": "test-deployment-id",
                        "created_at": "2023-01-01T00:00:00Z",
                        "created_by": "test-user",
                        "updated_by": "test-user",
                        "mcp_server_id": "test-server-id",
                        "open_api_spec_hash": "test-hash",
                        "mcp_spec_hash": "test-hash",
                        "status": "active",
                    },
                }
            ),
        )

        # Set up the mock to return our response
        mock_client.deploy_from_openapi.return_value = mock_response

        yield mock_client


def test_deploy_with_spec_dict(valid_openapi_dict, mock_api_client):
    """Test deploying with a spec dictionary."""
    result = deploy(
        openapi_spec=valid_openapi_dict,
        api_key="test-api-key",
    )

    # Check that the client was used correctly
    mock_api_client.deploy_from_openapi.assert_called_once()

    # Check the result
    assert result.id == "test-deployment-id"
    assert result.updated is False


def test_deploy_error_handling(mock_api_client):
    """Test error handling during deployment."""
    # Set up the mock to raise an error
    mock_api_client.deploy_from_openapi.side_effect = ApiError("API error", 400, {"error": "Invalid spec"})

    # Test that the error is propagated
    with pytest.raises(ApiError) as exc_info:
        deploy(
            openapi_spec={"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}},
            api_key="test-api-key",
        )

    assert "API error" in str(exc_info.value)


def test_deploy_invalid_input():
    """Test that providing invalid inputs raises appropriate errors."""
    # No spec source
    with pytest.raises(ValueError) as exc_info:
        deploy(api_key="test-api-key")
    assert "must be provided" in str(exc_info.value)

    # Multiple spec sources
    with pytest.raises(ValueError) as exc_info:
        deploy(
            openapi_spec={"openapi": "3.0.0", "info": {"title": "Test", "version": "1.0.0"}, "paths": {}},
            openapi_spec_path="test.json",
            api_key="test-api-key",
        )
    assert "Only one of" in str(exc_info.value)


@patch("tadata_sdk.core.sdk.OpenAPISpec.from_file")
def test_deploy_from_file(mock_from_file, mock_api_client):
    """Test deploying from a file."""
    # Set up the mock to return a valid spec
    mock_spec = OpenAPISpec.model_validate(
        {
            "openapi": "3.0.0",
            "info": {"title": "Test API", "version": "1.0.0"},
            "paths": {},
        }
    )
    mock_from_file.return_value = mock_spec

    # Call deploy with a file path
    result = deploy(
        openapi_spec_path="test.json",
        api_key="test-api-key",
    )

    # Check that the file was loaded
    mock_from_file.assert_called_once_with("test.json")

    # Check that the client was used correctly
    mock_api_client.deploy_from_openapi.assert_called_once()

    # Check the result
    assert result.id == "test-deployment-id"
