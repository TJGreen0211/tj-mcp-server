"""MCP tools: navigation, interaction, scraping, screenshot."""

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
