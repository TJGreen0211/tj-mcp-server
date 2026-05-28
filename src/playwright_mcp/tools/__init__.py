"""MCP tools: navigation, interaction, scraping, screenshot, memory, sqlite."""

from playwright_mcp.memory.tools import register_memory_tools
from playwright_mcp.sqlite.tools import register_sqlite_tools
from playwright_mcp.tools.interaction import register_interaction_tools
from playwright_mcp.tools.navigation import register_navigation_tools
from playwright_mcp.tools.scraping import register_scraping_tools
from playwright_mcp.tools.screenshots import register_screenshot_tools


def register_all_tools(mcp: object) -> None:
    """Register all tool modules with the FastMCP server."""
    register_navigation_tools(mcp)
    register_interaction_tools(mcp)
    register_scraping_tools(mcp)
    register_screenshot_tools(mcp)
    register_memory_tools(mcp)
    register_sqlite_tools(mcp)
