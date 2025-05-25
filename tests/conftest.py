import pytest
import tempfile
from unittest.mock import Mock, patch

# Configure Django for testing
import os
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY="test-secret-key-for-testing-only",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "django.contrib.auth",
            "rest_framework",
            "drf_spectacular",
        ],
        REST_FRAMEWORK={
            "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
        },
        SPECTACULAR_SETTINGS={
            "TITLE": "Test API",
            "DESCRIPTION": "Test API for tadata-sdk",
            "VERSION": "1.0.0",
        },
        USE_TZ=True,
    )
    django.setup()


@pytest.fixture
def mock_api_client():
    """Mock the API client for testing."""
    with patch("tadata_sdk.core.sdk.ApiClient") as mock_client_class:
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock the response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.data = Mock()
        mock_response.data.deployment = Mock()
        mock_response.data.deployment.id = "test-deployment-id"
        mock_response.data.deployment.created_at = None
        mock_response.data.updated = False

        mock_client.deploy_from_openapi.return_value = mock_response

        yield mock_client


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        yield f
    os.unlink(f.name)
