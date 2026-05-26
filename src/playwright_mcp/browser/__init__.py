"""Playwright browser lifecycle and shared state."""

from playwright_mcp.browser.lifecycle import create_browser_lifespan
from playwright_mcp.browser.state import BrowserState

__all__ = ["BrowserState", "create_browser_lifespan"]
