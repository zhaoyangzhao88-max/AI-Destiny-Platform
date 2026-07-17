"""
Application settings — unified configuration entry point.

Uses pydantic-settings to load configuration from environment variables
and the ``.env`` file. All environment variables use the ``ZHIMING_`` prefix
for namespace isolation.

Singleton access (production):
    >>> from zhiming.boot import get_settings
    >>> settings = get_settings()
    >>> settings.env
    'development'

Direct instantiation (testing):
    >>> from zhiming.boot import Settings
    >>> s = Settings(env="test", db_url="sqlite:///:memory:")

Sensitive fields (``secret_key``, ``llm_api_key``) use pydantic's ``SecretStr``
and are automatically masked in ``repr()``. Never call ``model_dump()`` on
settings for logging or report output — always pass ``exclude={'secret_key', 'llm_api_key'}``
to avoid leaking secrets.
"""

from __future__ import annotations

import json
from functools import lru_cache
from typing import ClassVar, Literal

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables / ``.env``.

    All variables use the ``ZHIMING_`` prefix. The load order is:
    ``default → .env file → system env vars`` (last wins).

    Creating a fresh instance:
        >>> Settings()
    """

    model_config: ClassVar[SettingsConfigDict] = SettingsConfigDict(
        env_prefix="ZHIMING_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Runtime ──────────────────────────────────────────────────
    env: Literal["development", "test", "production"] = Field(
        default="development",
        description="Runtime environment. Invalid values raise ValidationError (fail-fast).",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode (verbose logging, hot-reload).",
    )

    # ── Server ───────────────────────────────────────────────────
    host: str = Field(
        default="127.0.0.1",
        description="Bind address for the FastAPI server.",
    )
    port: int = Field(
        default=8000,
        description="Port for the FastAPI server (1024–65535).",
        ge=1024,
        le=65535,
    )

    # ── Logging ──────────────────────────────────────────────────
    log_level: str = Field(
        default="DEBUG",
        description="Log level: DEBUG | INFO | WARNING | ERROR | CRITICAL.",
    )
    log_format: str = Field(
        default="console",
        description="Log format: json | console.",
    )

    # ── Database ─────────────────────────────────────────────────
    db_url: str = Field(
        default="sqlite:///./data/zhiming.db",
        description="Database connection string.",
    )

    # ── Security ─────────────────────────────────────────────────
    secret_key: SecretStr = Field(
        default=SecretStr(""),
        description="Secret key for JWT / session signing. REQUIRED in production.",
    )

    # ── CORS ─────────────────────────────────────────────────────
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins. JSON array string or Python list.",
    )

    # ── LLM / AI Provider ────────────────────────────────────────
    llm_provider: str = Field(
        default="",
        description="LLM provider name (e.g. openai, anthropic).",
    )
    llm_api_key: SecretStr = Field(
        default=SecretStr(""),
        description="API key for the LLM provider.",
    )
    llm_model: str = Field(
        default="",
        description="Model identifier (e.g. gpt-4o, claude-sonnet-5).",
    )

    # ── Data Paths ───────────────────────────────────────────────
    data_dir: str = Field(
        default="./data",
        description="Local data directory for file storage.",
    )

    # ── Field Validators ─────────────────────────────────────────

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalize_log_level(cls, v: str) -> str:
        """Normalize log level to uppercase and validate."""
        normalized = v.upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if normalized not in allowed:
            raise ValueError(
                f"Invalid log level: '{v}'. Must be one of: {', '.join(sorted(allowed))}."
            )
        return normalized

    @field_validator("log_format", mode="before")
    @classmethod
    def _normalize_log_format(cls, v: str) -> str:
        """Normalize log format to lowercase and validate."""
        normalized = v.lower()
        allowed = {"json", "console"}
        if normalized not in allowed:
            raise ValueError(
                f"Invalid log format: '{v}'. Must be one of: {', '.join(sorted(allowed))}."
            )
        return normalized

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from JSON array string or pass through list."""
        if isinstance(v, str):
            stripped = v.strip()
            if stripped.startswith("["):
                return json.loads(stripped)
            return [stripped]
        return v

    # ── Model Validators ─────────────────────────────────────────

    @model_validator(mode="after")
    def _validate_production_requires_secret_key(self) -> Settings:
        """Fail fast: production environment must have a non-empty ``secret_key``."""
        if self.env == "production" and not self.secret_key.get_secret_value():
            raise ValueError(
                "ZHIMING_SECRET_KEY is required when ZHIMING_ENV=production."
            )
        return self


# ── Lazy Singleton ────────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached ``Settings`` singleton (lazy initialization).

    The settings instance is created on the **first call** and cached
    thereafter via ``functools.lru_cache``. This ensures:
        - Import-time safety (no side effects on ``import zhiming.boot``)
        - Single instance shared across the process
        - Test isolation via ``get_settings.cache_clear()``

    Production usage:
        >>> from zhiming.boot import get_settings
        >>> s = get_settings()
        >>> s.debug
        False

    Test usage — create a fresh ``Settings()`` directly:
        >>> s = Settings(env="test", db_url="sqlite:///:memory:")
        >>> s.env
        'test'

    Or reset the cache for integration tests that exercise the DI path:
        >>> get_settings.cache_clear()
        >>> fresh = get_settings()
    """
    return Settings()
