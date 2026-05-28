"""Entrypoint: load config, configure logging, create app, run HTTP server."""

import uvicorn

from memory.config import get_settings
from memory.logging_ import configure_logging, get_logger
from memory.server import create_app


def main() -> None:
    """Run the Memory MCP server over HTTP."""
    settings = get_settings()
    configure_logging(level=settings.log_level, json=settings.log_json)
    logger = get_logger(__name__)
    logger.info("Starting Memory MCP server", host=settings.mcp_host, port=settings.mcp_port)
    app = create_app()
    uvicorn.run(app, host=settings.mcp_host, port=settings.mcp_port)


if __name__ == "__main__":
    main()
