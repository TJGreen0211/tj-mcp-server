"""Environment-based settings for the SQLite MCP server."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """SQLite server settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mcp_host: str = Field(default="0.0.0.0", description="HTTP bind host")
    mcp_port: int = Field(default=9002, ge=1, le=65535, description="HTTP bind port")
    log_level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR",
    )
    log_json: bool = Field(default=False, description="Output logs as JSON")
    sqlite_db_path: str = Field(
        default="",
        description="Path to SQLite database file; set via SQLITE_DB_PATH env var",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
