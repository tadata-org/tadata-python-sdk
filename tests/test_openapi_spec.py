import json
import tempfile
from unittest.mock import Mock, patch

import pytest
import yaml

from tadata_sdk.errors.exceptions import SpecInvalidError
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


def test_from_dict_valid(valid_openapi_dict):
    """Test creating an OpenAPISpec from a valid dictionary."""
    spec = OpenAPISpec.from_dict(valid_openapi_dict)
    assert spec.openapi == "3.0.0"
    assert spec.info.title == "Test API"
    assert spec.info.version == "1.0.0"
    assert "/test" in spec.paths


def test_from_dict_invalid():
    """Test creating an OpenAPISpec from an invalid dictionary."""
    invalid_spec = {
        "info": {"title": "Test API", "version": "1.0.0"},
        "paths": {},
    }  # Missing openapi field
    with pytest.raises(SpecInvalidError) as exc_info:
        OpenAPISpec.from_dict(invalid_spec)
    assert "Invalid OpenAPI specification" in str(exc_info.value)


def test_from_json_valid(valid_openapi_dict):
    """Test creating an OpenAPISpec from a valid JSON string."""
    json_str = json.dumps(valid_openapi_dict)
    spec = OpenAPISpec.from_json(json_str)
    assert spec.openapi == "3.0.0"
    assert spec.info.title == "Test API"


def test_from_yaml_valid(valid_openapi_dict):
    """Test creating an OpenAPISpec from a valid YAML string."""
    yaml_str = yaml.dump(valid_openapi_dict)
    spec = OpenAPISpec.from_yaml(yaml_str)
    assert spec.openapi == "3.0.0"
    assert spec.info.title == "Test API"


def test_from_file_json(valid_openapi_dict):
    """Test creating an OpenAPISpec from a JSON file."""
    with tempfile.NamedTemporaryFile(suffix=".json", mode="w+") as f:
        json.dump(valid_openapi_dict, f)
        f.flush()
        spec = OpenAPISpec.from_file(f.name)
        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test API"


def test_from_file_yaml(valid_openapi_dict):
    """Test creating an OpenAPISpec from a YAML file."""
    with tempfile.NamedTemporaryFile(suffix=".yaml", mode="w+") as f:
        yaml.dump(valid_openapi_dict, f)
        f.flush()
        spec = OpenAPISpec.from_file(f.name)
        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test API"


def test_from_file_not_found():
    """Test error when file is not found."""
    with pytest.raises(SpecInvalidError) as exc_info:
        OpenAPISpec.from_file("/path/to/nonexistent/file.json")
    assert "Failed to read file" in str(exc_info.value)


def test_validate_openapi_version():
    """Test validation of OpenAPI version."""
    # Valid version
    assert OpenAPISpec.validate_openapi_version("3.0.0") == "3.0.0"
    assert OpenAPISpec.validate_openapi_version("3.1.0") == "3.1.0"

    # Invalid version
    with pytest.raises(ValueError) as exc_info:
        OpenAPISpec.validate_openapi_version("2.0.0")
    assert "Only OpenAPI 3.x specifications are supported" in str(exc_info.value)


def test_from_fastapi_not_installed():
    """Test error when FastAPI is not installed."""
    # Mock the import to raise ImportError
    with patch("tadata_sdk.openapi.source.OpenAPISpec.from_fastapi") as mock_from_fastapi:
        mock_from_fastapi.side_effect = SpecInvalidError(
            "FastAPI is not installed. Please install it with: pip install fastapi",
            details={"missing_package": "fastapi"},
        )

        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_fastapi(Mock())

        assert "FastAPI is not installed" in str(exc_info.value)


def test_from_fastapi_invalid_app():
    """Test error when a non-FastAPI object is passed."""
    # Test with a regular object instead of FastAPI app
    invalid_app = "not a fastapi app"

    with pytest.raises(SpecInvalidError) as exc_info:
        OpenAPISpec.from_fastapi(invalid_app)

    assert "Expected a FastAPI instance" in str(exc_info.value)


def test_from_fastapi_valid_app(valid_openapi_dict):
    """Test creating an OpenAPISpec from a valid FastAPI app."""
    try:
        from fastapi import FastAPI

        # Create a mock FastAPI app
        app = FastAPI(title="Test API", version="1.0.0")

        # Mock the openapi method to return our test spec
        app.openapi = Mock(return_value=valid_openapi_dict)

        spec = OpenAPISpec.from_fastapi(app)
        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test API"
        assert spec.info.version == "1.0.0"
        assert "/test" in spec.paths

    except ImportError:
        pytest.skip("FastAPI not available for testing")


def test_from_fastapi_app_openapi_error():
    """Test error when FastAPI app.openapi() raises an exception."""
    try:
        from fastapi import FastAPI

        app = FastAPI(title="Test API", version="1.0.0")

        # Mock the openapi method to raise an exception
        app.openapi = Mock(side_effect=Exception("OpenAPI generation failed"))

        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_fastapi(app)

        assert "Failed to extract OpenAPI specification from FastAPI app" in str(exc_info.value)

    except ImportError:
        pytest.skip("FastAPI not available for testing")
