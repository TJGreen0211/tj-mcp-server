"""FastMCP instance, lifespan, and tool registration for Memory MCP."""

from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastapi import FastAPI

from starlette.middleware.cors import CORSMiddleware
from memory.store import KnowledgeGraphManager
from memory.tools import register_memory_tools


@asynccontextmanager
async def memory_lifespan(server: FastMCP):
    """Create and yield memory manager for tools."""
    memory = KnowledgeGraphManager()
    yield {"memory": memory}


def create_app() -> FastMCP:
    """Build the FastMCP app with memory lifespan and memory tools registered."""
    mcp = FastMCP(
        name="Memory MCP",
        instructions=(
            "Persistent knowledge graph memory for storing entities, relations, and observations. "
            "Use create_entities to add new entities, create_relations to link them, "
            "add_observations to enrich entities, search_nodes to query by keyword, "
            "open_nodes to retrieve specific entities, and read_graph to see everything. "
            "Use delete_entities, delete_relations, and delete_observations to remove data."
        ),
        lifespan=memory_lifespan,
    )
    register_memory_tools(mcp)

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
