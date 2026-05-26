"""Environment-based settings. No logging or browser logic."""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Server and browser settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    mcp_host: str = Field(default="127.0.0.1", description="HTTP bind host")
    mcp_port: int = Field(default=8000, ge=1, le=65535, description="HTTP bind port")
    headless: bool = Field(default=False, description="Run browser headless")
    log_level: str = Field(
        default="INFO",
        description="Log level: DEBUG, INFO, WARNING, ERROR",
    )
    log_json: bool = Field(default=False, description="Output logs as JSON")


LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR"]


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
