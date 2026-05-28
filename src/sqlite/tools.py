"""SQLite Explorer tools: read_query, list_tables, describe_table."""

from pathlib import Path
from typing import Any

from fastmcp import Context

from sqlite.config import get_settings
from sqlite.store import SQLiteConnection


def _contains_multiple_statements(sql: str) -> bool:
    """Check if SQL contains multiple statements (semicolons outside quotes)."""
    in_single = False
    in_double = False
    for char in sql:
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == ";" and not in_single and not in_double:
            return True
    return False


def _get_db_path() -> Path:
    settings = get_settings()
    if not settings.sqlite_db_path:
        raise ValueError("SQLITE_DB_PATH environment variable must be set")
    return Path(settings.sqlite_db_path)


async def read_query(
    ctx: Context,
    query: str,
    params: list[Any] | None = None,
    fetch_all: bool = True,
    row_limit: int = 1000,
) -> list[dict[str, Any]]:
    """Execute a SELECT query on the SQLite database. Only SELECT and WITH queries are allowed for safety."""
    db_path = _get_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    query = query.strip().removesuffix(";").strip()

    if _contains_multiple_statements(query):
        raise ValueError("Multiple SQL statements are not allowed")

    query_lower = query.lower()
    if not any(query_lower.startswith(p) for p in ("select", "with")):
        raise ValueError("Only SELECT queries (including WITH clauses) are allowed for safety")

    params = params or []

    if "limit" not in query_lower:
        query = f"{query} LIMIT {row_limit}"

    conn = SQLiteConnection(db_path)
    try:
        with conn as c:
            cursor = c.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall() if fetch_all else [cursor.fetchone()]
            return [dict(row) for row in results if row is not None]
    except Exception as e:
        raise ValueError(f"SQLite error: {e}")


async def list_tables(ctx: Context) -> list[str]:
    """List all tables in the SQLite database."""
    db_path = _get_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = SQLiteConnection(db_path)
    try:
        with conn as c:
            cursor = c.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row["name"] for row in cursor.fetchall()]
    except Exception as e:
        raise ValueError(f"SQLite error: {e}")


async def describe_table(
    ctx: Context,
    table_name: str,
) -> list[dict[str, Any]]:
    """Get schema information for a table: column names, types, nullability, defaults, and primary key status."""
    db_path = _get_db_path()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at: {db_path}")

    conn = SQLiteConnection(db_path)
    try:
        with conn as c:
            cursor = c.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", [table_name])
            if not cursor.fetchone():
                raise ValueError(f"Table '{table_name}' does not exist")
            safe_name = "".join(c for c in table_name if c.isalnum() or c == "_")
            cursor.execute(f"PRAGMA table_info([{safe_name}])")
            return [dict(row) for row in cursor.fetchall()]
    except Exception as e:
        if "does not exist" in str(e):
            raise
        raise ValueError(f"SQLite error: {e}")


def register_sqlite_tools(mcp: object) -> None:
    """Register SQLite explorer tools with the FastMCP server."""
    mcp.add_tool(read_query)
    mcp.add_tool(list_tables)
    mcp.add_tool(describe_table)
