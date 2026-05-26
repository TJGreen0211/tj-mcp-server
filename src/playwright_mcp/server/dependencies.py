"""Dependency wiring: register tools with the FastMCP server."""

from fastmcp import FastMCP

from playwright_mcp.tools import register_all_tools as register_all_tools_impl


def register_all_tools(mcp: FastMCP) -> None:
    """Register all tool modules with the FastMCP server (navigation, interaction, scraping, screenshot)."""
    register_all_tools_impl(mcp)
