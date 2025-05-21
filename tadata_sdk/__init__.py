try:
    from importlib.metadata import version

    __version__ = version("tadata-sdk")
except Exception:  # pragma: no cover
    # Fallback for local development
    __version__ = "0.0.0.dev0"  # pragma: no cover

from .core.sdk import deploy
from .openapi.source import OpenAPISpec
from .errors.exceptions import (
    TadataSDKError,
    SpecInvalidError,
    AuthError,
    ApiError,
    NetworkError,
)

__all__ = [
    "deploy",
    "OpenAPISpec",
    "TadataSDKError",
    "SpecInvalidError",
    "AuthError",
    "ApiError",
    "NetworkError",
]
