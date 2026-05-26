"""Structlog configuration and logger factory. Single place for logging setup."""

from playwright_mcp.logging_.setup import configure_logging, get_logger

__all__ = ["configure_logging", "get_logger"]
