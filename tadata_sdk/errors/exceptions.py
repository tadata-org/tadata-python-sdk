from http import HTTPStatus
from typing import Any, Optional


class TadataSDKError(Exception):
    """Base error class for all errors originating from the Tadata SDK.

    All specific SDK errors will extend this class.
    You can use this class to catch any error thrown by the SDK.
    """

    def __init__(
        self,
        message: str,
        code: str,
        status_code: Optional[int] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Create a new TadataSDKError.

        Args:
            message: A human-readable description of the error.
            code: A unique machine-readable error code.
            status_code: Optional HTTP status code related to the error.
            cause: Optional original error that led to this error.
        """
        super().__init__(message)
        self.name = self.__class__.__name__
        self.code = code
        self.status_code = status_code
        self.cause = cause


class SpecInvalidError(TadataSDKError):
    """Error thrown when an OpenAPI specification is invalid or cannot be processed.

    This can occur during operations like `OpenAPISpec.from_file()` or `deploy()`
    if the provided specification has structural issues, syntax errors, or fails validation.
    """

    def __init__(
        self,
        message: str,
        details: Optional[Any] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Create a new SpecInvalidError.

        Args:
            message: A human-readable description of the validation error.
            details: Optional additional details about the validation failure.
            cause: Optional original error that led to this validation error.
        """
        super().__init__(message, code="spec_invalid", status_code=HTTPStatus.BAD_REQUEST, cause=cause)
        self.details = details


class AuthError(TadataSDKError):
    """Error thrown when an API request fails due to authentication issues.

    This typically means the provided API key is invalid, expired, or lacks necessary permissions.
    """

    def __init__(self, message: str = "Authentication failed", cause: Optional[Exception] = None) -> None:
        """Create a new AuthError.

        Args:
            message: A human-readable description of the authentication failure.
            cause: Optional original error that led to this authentication error.
        """
        super().__init__(message, code="auth_error", status_code=HTTPStatus.UNAUTHORIZED, cause=cause)


class ApiError(TadataSDKError):
    """Error thrown when the Tadata API returns an error response.

    This class provides access to the HTTP status code and the body of the API error response.
    """

    def __init__(
        self,
        message: str,
        status_code: int,
        body: Optional[Any] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Create a new ApiError.

        Args:
            message: A human-readable description of the API error.
            status_code: The HTTP status code received from the API.
            body: Optional body of the API error response.
            cause: Optional original error that led to this API error.
        """
        super().__init__(message, code="api_error", status_code=status_code, cause=cause)
        self.body = body


class NetworkError(TadataSDKError):
    """Error thrown for network-related issues encountered while trying to communicate with the Tadata API.

    This could be due to DNS resolution failures, TCP connection timeouts, or other network interruptions.
    """

    def __init__(self, message: str, cause: Optional[Exception] = None) -> None:
        """Create a new NetworkError.

        Args:
            message: A human-readable description of the network failure.
            cause: Optional original error that led to this network error.
        """
        super().__init__(message, code="network_error", cause=cause)
