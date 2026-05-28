"""SQLite database connection helper."""

import sqlite3
from pathlib import Path
from sqlite3 import Connection


class SQLiteConnection:
    """Context manager for SQLite database connections."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn: Connection | None = None

    def __enter__(self) -> Connection:
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):  # type: ignore[override]
        if self.conn:
            self.conn.close()
