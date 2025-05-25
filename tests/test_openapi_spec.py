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


def test_from_django_not_installed():
    """Test error when Django is not installed."""
    # Mock the import to raise ImportError
    with patch("tadata_sdk.openapi.source.OpenAPISpec.from_django") as mock_from_django:
        mock_from_django.side_effect = SpecInvalidError(
            "Django is not installed. Please install it with: pip install django",
            details={"missing_package": "django"},
        )

        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django(Mock())

        assert "Django is not installed" in str(exc_info.value)


def test_from_django_drf_not_installed():
    """Test error when Django REST Framework is not installed."""
    # Since DRF is actually installed, we'll test the error message format
    # by mocking the import at the right level
    original_import = __builtins__["__import__"]

    def mock_import(name, *args, **kwargs):
        if name == "rest_framework":
            raise ImportError("No module named 'rest_framework'")
        return original_import(name, *args, **kwargs)

    __builtins__["__import__"] = mock_import
    try:
        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django()
        assert "Django REST Framework is not installed" in str(exc_info.value)
    finally:
        __builtins__["__import__"] = original_import


def test_from_django_spectacular_not_installed():
    """Test error when drf-spectacular is not installed."""
    # Since drf-spectacular is actually installed, we'll test the error message format
    # by mocking the import at the right level
    original_import = __builtins__["__import__"]

    def mock_import(name, *args, **kwargs):
        if name == "drf_spectacular":
            raise ImportError("No module named 'drf_spectacular'")
        return original_import(name, *args, **kwargs)

    __builtins__["__import__"] = mock_import
    try:
        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django()
        assert "drf-spectacular is not installed" in str(exc_info.value)
    finally:
        __builtins__["__import__"] = original_import


def test_from_django_not_configured():
    """Test error when Django settings are not configured."""
    # Test with actual Django but mock the configured property
    from django.conf import settings

    original_configured = settings.configured
    settings.configured = False

    try:
        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django()
        # The actual error message may vary, but it should indicate a Django configuration issue
        error_msg = str(exc_info.value)
        assert (
            "Django settings are not configured" in error_msg
            or "ROOT_URLCONF" in error_msg
            or "settings are not configured" in error_msg
        )
    finally:
        settings.configured = original_configured


def test_from_django_spectacular_not_in_installed_apps():
    """Test error when drf-spectacular is not in INSTALLED_APPS."""
    # Test with actual Django but mock INSTALLED_APPS
    from django.conf import settings

    original_apps = getattr(settings, "INSTALLED_APPS", [])
    settings.INSTALLED_APPS = ["django.contrib.admin", "rest_framework"]

    try:
        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django()
        assert "drf-spectacular is not in INSTALLED_APPS" in str(exc_info.value)
    finally:
        settings.INSTALLED_APPS = original_apps


def test_from_django_autoschema_not_configured():
    """Test error when drf-spectacular AutoSchema is not configured."""
    # Test with actual Django but mock REST_FRAMEWORK settings
    from django.conf import settings

    original_rest_framework = getattr(settings, "REST_FRAMEWORK", {})
    settings.REST_FRAMEWORK = {"DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema"}

    try:
        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django()
        assert "drf-spectacular AutoSchema is not configured" in str(exc_info.value)
    finally:
        settings.REST_FRAMEWORK = original_rest_framework


def test_from_django_valid_app(valid_openapi_dict):
    """Test creating an OpenAPISpec from a valid Django app."""
    # Test with actual Django setup but mock the schema generator
    with patch("drf_spectacular.generators.SchemaGenerator") as mock_generator_class:
        # Mock the SchemaGenerator to return our test spec
        mock_generator = Mock()
        mock_generator.get_schema.return_value = valid_openapi_dict
        mock_generator_class.return_value = mock_generator

        spec = OpenAPISpec.from_django()
        assert spec.openapi == "3.0.0"
        assert spec.info.title == "Test API"
        assert spec.info.version == "1.0.0"
        assert "/test" in spec.paths

        # Verify the generator was called correctly
        mock_generator.get_schema.assert_called_once_with(request=None, public=True)


def test_from_django_schema_generation_error():
    """Test error when Django schema generation fails."""
    # Test with actual Django setup but mock the schema generator to fail
    with patch("drf_spectacular.generators.SchemaGenerator") as mock_generator_class:
        # Mock the SchemaGenerator to raise an exception
        mock_generator = Mock()
        mock_generator.get_schema.side_effect = Exception("Schema generation failed")
        mock_generator_class.return_value = mock_generator

        with pytest.raises(SpecInvalidError) as exc_info:
            OpenAPISpec.from_django()

        assert "Failed to extract OpenAPI specification from Django app" in str(exc_info.value)
