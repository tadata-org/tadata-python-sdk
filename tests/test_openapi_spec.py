import json
import tempfile

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
