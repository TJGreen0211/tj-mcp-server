"""Entrypoint: load config, configure logging, create app, run HTTP server."""

import uvicorn

from playwright_mcp.config import get_settings
from playwright_mcp.logging_ import configure_logging, get_logger
from playwright_mcp.server import create_app


def main() -> None:
    """Run the Playwright MCP server over HTTP."""
    settings = get_settings()
    configure_logging(level=settings.log_level, json=settings.log_json)
    logger = get_logger(__name__)
    logger.info("Starting Playwright MCP server", host=settings.mcp_host, port=settings.mcp_port)
    app = create_app()
    # mcp.run(
    #     transport="http",
    #     host=settings.mcp_host,
    #     port=settings.mcp_port,
    # )
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
