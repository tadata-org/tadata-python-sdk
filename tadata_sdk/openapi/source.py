import json
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

from ..errors.exceptions import SpecInvalidError


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
