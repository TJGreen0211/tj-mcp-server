"""FastMCP instance, lifespan, and tool registration. No business logic."""

from fastmcp import FastMCP
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from playwright_mcp.browser import create_browser_lifespan
from playwright_mcp.server.dependencies import register_all_tools


def create_app() -> FastMCP:
    """Build the FastMCP app with browser lifespan and all tools registered."""
    mcp = FastMCP(
        name="Playwright MCP",
        instructions=(
            "Browser automation, web scraping, persistent memory, and SQLite database exploration. "
            "Use the tools to navigate, click, type, fill forms, take screenshots, and extract content "
            "from pages. For data extraction use browser_scrape with mode 'text', 'main', 'accessible', or 'headings'. "
            "The knowledge graph memory tools (create_entities, create_relations, add_observations, "
            "search_nodes, open_nodes, read_graph, delete_*) provide persistent structured storage. "
            "The SQLite tools (read_query, list_tables, describe_table) allow querying a SQLite database "
            "configured via SQLITE_DB_PATH."
        ),
        lifespan=create_browser_lifespan,
    )
    register_all_tools(mcp)

    mcp_app = mcp.http_app(path='/', stateless_http=True, json_response=True)
    app = FastAPI(lifespan=mcp_app.lifespan)
    app.mount("/mcp", mcp_app)
    origins = [
        "http://localhost",
        "http://localhost:8080",
        "http://tj-server:5001",
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # List of allowed origins
        allow_credentials=True,  # Allow cookies and authorization headers
        allow_methods=["*"],     # Allow all HTTP methods
        allow_headers=["*"],     # Allow all request headers
    )

    return app
