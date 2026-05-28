"""Entrypoint: load config, configure logging, create app, run HTTP server."""

import uvicorn

from sqlite.config import get_settings
from sqlite.logging_ import configure_logging, get_logger
from sqlite.server import create_app


def main() -> None:
    """Run the SQLite MCP server over HTTP."""
    settings = get_settings()
    configure_logging(level=settings.log_level, json=settings.log_json)
    logger = get_logger(__name__)
    logger.info("Starting SQLite MCP server", host=settings.mcp_host, port=settings.mcp_port)
    app = create_app()
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
