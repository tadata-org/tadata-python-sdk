import logging
import sys
from typing import Any, Protocol


class Logger(Protocol):
    """Logger protocol for dependency injection."""

    def debug(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a debug message."""
        ...

    def info(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an info message."""
        ...

    def warning(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log a warning message."""
        ...

    def error(self, msg: str, *args: Any, **kwargs: Any) -> None:
        """Log an error message."""
        ...


def create_default_logger(name: str = "tadata_sdk", level: int = logging.INFO) -> logging.Logger:
    """Create a default logger for the SDK.

    Args:
        name: The name of the logger.
        level: The minimum logging level to record.

    Returns:
        A configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Only add handler if it doesn't already have one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
