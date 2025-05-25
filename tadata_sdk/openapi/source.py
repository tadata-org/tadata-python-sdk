import json
from pathlib import Path
from typing import Any, Dict, Optional, Union, TYPE_CHECKING

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..errors.exceptions import SpecInvalidError

if TYPE_CHECKING:
    from fastapi import FastAPI


class OpenAPIInfo(BaseModel):
    """OpenAPI info object."""

    title: str
    version: str
    description: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class OpenAPISpec(BaseModel):
    """Represents a validated OpenAPI specification.

    This class handles loading, validating, and accessing OpenAPI specifications
    from various sources such as files, JSON strings, or dictionaries.
    """

    openapi: str = Field(..., description="OpenAPI version string")
    info: OpenAPIInfo = Field(..., description="Information about the API")
    paths: Dict[str, Any] = Field(..., description="API paths")
    model_config = ConfigDict(extra="allow", populate_by_name=True)

    @field_validator("openapi")
    @classmethod
    def validate_openapi_version(cls, v: str) -> str:
        """Validate the OpenAPI version string.

        Args:
            v: The version string to validate.

        Returns:
            The validated version string.

        Raises:
            ValueError: If the version is not a supported OpenAPI 3.x version.
        """
        if not v.startswith("3."):
            raise ValueError("Only OpenAPI 3.x specifications are supported")
        return v

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OpenAPISpec":
        """Create an OpenAPISpec instance from a dictionary.

        Args:
            data: A dictionary representing an OpenAPI specification.

        Returns:
            An OpenAPISpec instance.

        Raises:
            SpecInvalidError: If the dictionary is not a valid OpenAPI specification.
        """
        try:
            return cls.model_validate(data)
        except Exception as e:
            raise SpecInvalidError(f"Invalid OpenAPI specification: {str(e)}", details=data, cause=e)

    @classmethod
    def from_json(cls, json_str: str) -> "OpenAPISpec":
        """Create an OpenAPISpec instance from a JSON string.

        Args:
            json_str: A JSON string representing an OpenAPI specification.

        Returns:
            An OpenAPISpec instance.

        Raises:
            SpecInvalidError: If the JSON string is not valid JSON or not a valid OpenAPI specification.
        """
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            raise SpecInvalidError(f"Invalid JSON: {str(e)}", details={"json_str": json_str[:100]}, cause=e)

    @classmethod
    def from_yaml(cls, yaml_str: str) -> "OpenAPISpec":
        """Create an OpenAPISpec instance from a YAML string.

        Args:
            yaml_str: A YAML string representing an OpenAPI specification.

        Returns:
            An OpenAPISpec instance.

        Raises:
            SpecInvalidError: If the YAML string is not valid YAML or not a valid OpenAPI specification.
        """
        try:
            data = yaml.safe_load(yaml_str)
            return cls.from_dict(data)
        except yaml.YAMLError as e:
            raise SpecInvalidError(f"Invalid YAML: {str(e)}", details={"yaml_str": yaml_str[:100]}, cause=e)

    @classmethod
    def from_file(cls, file_path: Union[str, Path]) -> "OpenAPISpec":
        """Create an OpenAPISpec instance from a file.

        The file can be either JSON or YAML, determined by the file extension.

        Args:
            file_path: Path to a JSON or YAML file containing an OpenAPI specification.

        Returns:
            An OpenAPISpec instance.

        Raises:
            SpecInvalidError: If the file cannot be read, is not valid JSON/YAML,
                or not a valid OpenAPI specification.
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)

        try:
            file_path = file_path.resolve()
            content = file_path.read_text(encoding="utf-8")

            # Determine parser to use based on file extension
            if file_path.suffix.lower() in (".json",):
                return cls.from_json(content)
            elif file_path.suffix.lower() in (".yaml", ".yml"):
                return cls.from_yaml(content)
            else:
                raise SpecInvalidError(
                    f"Unsupported file extension: {file_path.suffix}. Only .json, .yaml, and .yml files are supported.",
                    details={"file_path": str(file_path)},
                )
        except (OSError, IOError) as e:
            raise SpecInvalidError(
                f"Failed to read file: {str(e)}",
                details={"file_path": str(file_path)},
                cause=e,
            )

    @classmethod
    def from_fastapi(cls, app: "FastAPI") -> "OpenAPISpec":
        """Create an OpenAPISpec instance from a FastAPI application.

        Args:
            app: A FastAPI application instance.

        Returns:
            An OpenAPISpec instance.

        Raises:
            SpecInvalidError: If FastAPI is not installed, the app is not a FastAPI instance,
                or the OpenAPI specification cannot be extracted.
        """
        try:
            from fastapi import FastAPI
        except ImportError as e:
            raise SpecInvalidError(
                "FastAPI is not installed. Please install it with: pip install fastapi",
                details={"missing_package": "fastapi"},
                cause=e,
            )

        if not isinstance(app, FastAPI):
            raise SpecInvalidError(
                f"Expected a FastAPI instance, got {type(app).__name__}",
                details={"app_type": type(app).__name__},
            )

        try:
            # Get the OpenAPI schema from the FastAPI app
            openapi_schema = app.openapi()
            return cls.from_dict(openapi_schema)
        except Exception as e:
            raise SpecInvalidError(
                f"Failed to extract OpenAPI specification from FastAPI app: {str(e)}",
                details={"app_title": getattr(app, "title", "Unknown")},
                cause=e,
            )

    @classmethod
    def from_django(cls) -> "OpenAPISpec":
        """Create an OpenAPISpec instance from a Django application.

        This method requires Django REST Framework and drf-spectacular to be installed
        and properly configured in the Django application.

        Returns:
            An OpenAPISpec instance.

        Raises:
            SpecInvalidError: If Django, DRF, or drf-spectacular are not installed,
                or the OpenAPI specification cannot be extracted.
        """
        try:
            import django
            from django.conf import settings
        except ImportError as e:
            raise SpecInvalidError(
                "Django is not installed. Please install it with: pip install django",
                details={"missing_package": "django"},
                cause=e,
            )

        try:
            # Check if Django REST Framework is installed
            import rest_framework  # noqa: F401
        except ImportError as e:
            raise SpecInvalidError(
                "Django REST Framework is not installed. Please install it with: pip install djangorestframework",
                details={"missing_package": "djangorestframework"},
                cause=e,
            )

        try:
            # Check if drf-spectacular is installed
            import drf_spectacular  # noqa: F401
            from drf_spectacular.openapi import AutoSchema  # noqa: F401
        except ImportError as e:
            raise SpecInvalidError(
                "drf-spectacular is not installed. Please install it with: pip install drf-spectacular",
                details={"missing_package": "drf-spectacular"},
                cause=e,
            )

        try:
            # Ensure Django is configured
            if not settings.configured:
                raise SpecInvalidError(
                    "Django settings are not configured. Please ensure Django is properly set up.",
                    details={"django_configured": False},
                )

            # Check if drf-spectacular is in INSTALLED_APPS
            if "drf_spectacular" not in settings.INSTALLED_APPS:
                raise SpecInvalidError(
                    "drf-spectacular is not in INSTALLED_APPS. Please add 'drf_spectacular' to your INSTALLED_APPS setting.",
                    details={"missing_app": "drf_spectacular"},
                )

            # Check if the schema class is configured
            rest_framework_settings = getattr(settings, "REST_FRAMEWORK", {})
            schema_class = rest_framework_settings.get("DEFAULT_SCHEMA_CLASS")

            if schema_class != "drf_spectacular.openapi.AutoSchema":
                raise SpecInvalidError(
                    "drf-spectacular AutoSchema is not configured. Please set REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS'] = 'drf_spectacular.openapi.AutoSchema'",
                    details={"current_schema_class": schema_class},
                )

            # Generate the OpenAPI schema using drf-spectacular
            # Use the generator directly instead of SpectacularAPIView
            from drf_spectacular.generators import SchemaGenerator

            generator = SchemaGenerator()
            schema_dict = generator.get_schema(request=None, public=True)

            return cls.from_dict(schema_dict)

        except Exception as e:
            raise SpecInvalidError(
                f"Failed to extract OpenAPI specification from Django app: {str(e)}",
                details={"django_version": getattr(django, "VERSION", "Unknown")},
                cause=e,
            )
