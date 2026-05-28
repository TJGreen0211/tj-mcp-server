"""Memory tools: knowledge graph CRUD and search for the FastMCP server."""

import json

from fastmcp import Context

from memory.store import KnowledgeGraphManager


async def create_entities(
    ctx: Context,
    entities: list[dict],
) -> str:
    """Create multiple new entities in the knowledge graph. Each entity has a name, entityType, and observations array."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    result = mgr.create_entities(entities)
    return json.dumps(result, indent=2)


async def create_relations(
    ctx: Context,
    relations: list[dict],
) -> str:
    """Create multiple new relations between entities in the knowledge graph. Relations should be in active voice. Each relation has from, to, and relationType."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    result = mgr.create_relations(relations)
    return json.dumps(result, indent=2)


async def add_observations(
    ctx: Context,
    observations: list[dict],
) -> str:
    """Add new observations to existing entities in the knowledge graph. Each item has entityName and contents (array of strings)."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    result = mgr.add_observations(observations)
    return json.dumps(result, indent=2)


async def delete_entities(
    ctx: Context,
    entity_names: list[str],
) -> str:
    """Delete multiple entities and their associated relations from the knowledge graph."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    mgr.delete_entities(entity_names)
    return "Entities deleted successfully"


async def delete_observations(
    ctx: Context,
    deletions: list[dict],
) -> str:
    """Delete specific observations from entities in the knowledge graph. Each item has entityName and observations (array of strings to delete)."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    mgr.delete_observations(deletions)
    return "Observations deleted successfully"


async def delete_relations(
    ctx: Context,
    relations: list[dict],
) -> str:
    """Delete multiple relations from the knowledge graph. Each relation has from, to, and relationType."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    mgr.delete_relations(relations)
    return "Relations deleted successfully"


async def read_graph(ctx: Context) -> str:
    """Read the entire knowledge graph, returning all entities and relations."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    graph = mgr.read_graph()
    return json.dumps(graph, indent=2)


async def search_nodes(
    ctx: Context,
    query: str,
) -> str:
    """Search for nodes in the knowledge graph by matching entity names, types, and observation content."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    graph = mgr.search_nodes(query)
    return json.dumps(graph, indent=2)


async def open_nodes(
    ctx: Context,
    names: list[str],
) -> str:
    """Open specific nodes in the knowledge graph by their names, returning entities and connected relations."""
    mgr: KnowledgeGraphManager = ctx.lifespan_context["memory"]
    graph = mgr.open_nodes(names)
    return json.dumps(graph, indent=2)


def register_memory_tools(mcp: object) -> None:
    """Register memory tools with the FastMCP server."""
    mcp.add_tool(create_entities)
    mcp.add_tool(create_relations)
    mcp.add_tool(add_observations)
    mcp.add_tool(delete_entities)
    mcp.add_tool(delete_observations)
    mcp.add_tool(delete_relations)
    mcp.add_tool(read_graph)
    mcp.add_tool(search_nodes)
    mcp.add_tool(open_nodes)
