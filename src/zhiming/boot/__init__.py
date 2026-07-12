"""
Bootstrap module.

Provides configuration management (pydantic-settings), structured logging
(structlog), exception hierarchy, and utility functions (time utilities,
ID generation, JSON helpers).

Responsibilities:
    - Load and validate application settings from env vars / .env file
    - Configure and expose structured logging via structlog
    - Define a hierarchical exception tree for all business errors
    - Provide reusable utility functions (ISO time, prefixed IDs, custom JSON)

Implemented in E-BOOT Iterations 2-5.
"""

from zhiming.boot.logging import configure_logging, get_logger
from zhiming.boot.settings import Settings, get_settings

__all__ = [
    "Settings",
    "configure_logging",
    "get_logger",
    "get_settings",
]
