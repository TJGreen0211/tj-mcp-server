"""FastMCP instance and tool registration for SQLite MCP."""

from fastmcp import FastMCP
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from sqlite.tools import register_sqlite_tools


def create_app() -> FastMCP:
    """Build the FastMCP app with SQLite tools registered."""
    mcp = FastMCP(
        name="SQLite MCP",
        instructions=(
            "SQLite database exploration. Use read_query to execute SELECT queries, "
            "list_tables to see all tables, and describe_table to get schema information. "
            "Requires SQLITE_DB_PATH environment variable pointing to a .db or .sqlite file."
        ),
    )
    register_sqlite_tools(mcp)

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
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
