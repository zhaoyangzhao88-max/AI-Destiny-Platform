"""
boot.logging — Unified structured logging foundation.

This module is the **single logging entry point** for the entire ZhiMing system.
It uses ``structlog`` (bridged through stdlib ``logging``) to provide:

- Structured JSON output for production
- Colorful console output for development
- Environment-aware two-level sensitive data redaction
- ``contextvars``-based request ID propagation (asyncio-safe)
- File rotation for Desktop V1, with stdout JSON path for future Server

Architecture
------------
All business modules use ``logging.getLogger(__name__)`` (standard library).
``structlog.stdlib.ProcessorFormatter`` intercepts at the handler level,
applying structured enrichment before rendering.  Zero intrusion into
application code.

    raw event_dict
        → [add_timestamp]
        → [add_log_level]
        → [add_logger_name]
        → [add_request_id]
        → [SensitiveDataRedactor]  (two-level)
        → JSONRenderer / ConsoleRenderer

Sensitive Data Model (CTO Approved)
-----------------------------------
- Level 1 (PII):  Always redacted.  Fields: user_name, real_name, phone, email,
                  id_card, address, birth_location.
- Level 2 (Domain): Environment-aware.  Fields: birth_year, birth_month,
                    day_pillar, heavenly_stem, etc.
  * development / test:  opt-in via reveal_domain_data=True
  * production:          always redacted, reveal_domain_data is ignored

Integration example (for INFRA-02 FastAPI middleware)::

    from zhiming.boot import configure_logging, get_logger, RequestIDContext
    from uuid import uuid4

    configure_logging(settings)
    logger = get_logger(__name__)

    @app.middleware("http")
    async def add_request_id(request, call_next):
        rid = str(uuid4())
        token = RequestIDContext.set(rid)
        try:
            response = await call_next(request)
            response.headers["X-Request-Id"] = rid
            return response
        finally:
            RequestIDContext.reset(token)
"""

from __future__ import annotations

import logging
import logging.handlers
import os
import re
import sys
from collections.abc import MutableMapping
from contextvars import ContextVar, Token
from datetime import datetime, timezone
from typing import Any

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
from structlog.stdlib import ProcessorFormatter

from zhiming.boot.settings import Settings

# ── Public ────────────────────────────────────────────────────────────
__all__ = [
    "configure_logging",
    "get_logger",
    "RequestIDContext",
    "RequestLogContextManager",
]

# ── Context Variable (asyncio-safe) ───────────────────────────────────

_request_id_var: ContextVar[str] = ContextVar("request_id", default="")


class RequestIDContext:
    """Asyncio-safe request ID propagation via ``contextvars``.

    Usage::

        token = RequestIDContext.set("abc-123")
        try:
            ...   # all logging in this task picks up the ID
        finally:
            RequestIDContext.reset(token)
    """

    @staticmethod
    def set(request_id: str) -> Token[str]:
        return _request_id_var.set(request_id)

    @staticmethod
    def reset(token: Token[str]) -> None:
        _request_id_var.reset(token)

    @staticmethod
    def get() -> str:
        return _request_id_var.get()


class RequestLogContextManager:
    """Context manager that binds a request ID for the duration of a request.

    Usage::

        with RequestLogContextManager("abc-123"):
            logger.info("inside request")
    """

    def __init__(self, request_id: str) -> None:
        self._request_id = request_id
        self._token: Token[str] | None = None

    def __enter__(self) -> RequestLogContextManager:
        self._token = RequestIDContext.set(self._request_id)
        return self

    def __exit__(self, *exc: Any) -> None:
        if self._token is not None:
            RequestIDContext.reset(self._token)


# ── Two-Level Sensitive Data Redaction ────────────────────────────────

# Level 1 — PII: always redacted regardless of environment
PII_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "user_name", "real_name", "full_name",
    "phone", "email", "id_card", "address",
    "birth_location",
})

# Level 2 — Domain: redacted based on env + reveal_domain_data flag
DOMAIN_SENSITIVE_KEYS: frozenset[str] = frozenset({
    "birth_year", "birth_month", "birth_day", "birth_hour", "birth_minute",
    "year_pillar", "month_pillar", "day_pillar", "hour_pillar",
    "heavenly_stem", "earthly_branch", "na_yin",
})

# Generic key pattern — catches API keys, tokens, credentials, etc.
SENSITIVE_FIELD_PATTERNS: re.Pattern[str] = re.compile(
    r"\b(api_key|api_secret|secret_key|password|token|credential|"
    r"auth_token|access_token|refresh_token|session_key|private_key|"
    r"master_key)\b",
    re.IGNORECASE,
)

# Generic value pattern — catches Bearer tokens, key-like strings, etc.
SENSITIVE_VALUE_PATTERNS: re.Pattern[str] = re.compile(
    r"(?:sk-[a-zA-Z0-9]{20,}|"
    r"secret-[a-zA-Z0-9]+|"
    r"Bearer\s+[a-zA-Z0-9._-]+|"
    r"[A-Za-z0-9+/]{40,}={0,2})"
)


class SensitiveDataRedactor:
    """Two-level sensitive data redactor *structlog* processor.

    - Level 1 (PII):       Always redacted regardless of environment.
    - Level 2 (Domain):    Redacted when ``domain_redact=True``
                           (production default) or revealed for debugging.

    Also scans generic key patterns (api_key, token, …) and value
    patterns (Bearer tokens, key-like strings).
    """

    def __init__(self, pii_always_redact: bool = True, domain_redact: bool = True) -> None:
        self._pii_always = pii_always_redact
        self._domain_redact = domain_redact

    # structlog processor signature: (logger, method_name, event_dict) -> event_dict
    def __call__(
        self, logger: logging.Logger, method_name: str, event_dict: MutableMapping[str, Any]
    ) -> MutableMapping[str, Any]:
        for key in list(event_dict.keys()):
            # Level 1 — always redact
            if self._pii_always and key in PII_SENSITIVE_KEYS:
                event_dict[key] = "***"
            # Level 2 — conditionally redact
            elif self._domain_redact and key in DOMAIN_SENSITIVE_KEYS:
                event_dict[key] = "***"
            # Generic key pattern
            elif SENSITIVE_FIELD_PATTERNS.search(key):
                event_dict[key] = "***"

        # Value-based redaction (scan string values for known patterns)
        for key, value in event_dict.items():
            if isinstance(value, str) and SENSITIVE_VALUE_PATTERNS.search(value):
                event_dict[key] = "***"

        return event_dict


# ── Processors ────────────────────────────────────────────────────────


def _add_timestamp(
    logger: logging.Logger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Add an ISO-8601 UTC timestamp to every event."""
    event_dict["timestamp"] = datetime.now(timezone.utc).isoformat()
    return event_dict


def _add_request_id(
    logger: logging.Logger,  # noqa: ARG001
    method_name: str,  # noqa: ARG001
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """Attach the current request ID from ``contextvars`` if set."""
    rid = RequestIDContext.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


# ── Helpers ───────────────────────────────────────────────────────────


def _resolve_level(level_name: str) -> int:
    """Convert log level name to stdlib integer level."""
    return getattr(logging, level_name.upper(), logging.DEBUG)


def _build_common_processors(settings: Settings) -> list[Any]:
    """Build the shared processor chain for all output modes."""
    return [
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        _add_timestamp,
        _add_request_id,
        SensitiveDataRedactor(
            pii_always_redact=True,
            domain_redact=settings.env not in ("development", "test"),
        ),
        ProcessorFormatter.wrap_for_formatter,
    ]


def _build_console_handler(settings: Settings) -> logging.Handler:
    """Build a handler that writes colorised logs to stderr."""
    formatter = ProcessorFormatter(
        foreign_pre_chain=_build_common_processors(settings),
        processor=ConsoleRenderer(),
    )
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(formatter)
    return handler


def _build_file_handler(settings: Settings) -> logging.Handler:
    """Build a rotating file handler that writes JSON logs.

    Desktop V1: logs are persisted to ``{data_dir}/logs/zhiming.log``.
    """
    log_dir = os.path.join(settings.data_dir, "logs")
    os.makedirs(log_dir, exist_ok=True)

    formatter = ProcessorFormatter(
        foreign_pre_chain=_build_common_processors(settings),
        processor=JSONRenderer(),
    )
    handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, "zhiming.log"),
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding="utf-8",
    )
    handler.setFormatter(formatter)
    return handler


# ── Public API ────────────────────────────────────────────────────────


def configure_logging(settings: Settings, *, reveal_domain_data: bool = False) -> None:
    """Configure the unified logging system.

    This function **must** be called once at application startup, typically
    in the FastAPI *lifespan* or ``__main__`` entry point.

    Parameters
    ----------
    settings:
        Application settings (reads ``log_level``, ``log_format``, ``env``,
        ``data_dir``).
    reveal_domain_data:
        Allow Level 2 (Domain) sensitive fields to appear in logs.
        **Only effective in development/test environments.**
        Ignored silently in production.
    """
    # Detect whether the caller explicitly passed reveal_domain_data
    # so we can enforce the production guard
    effective_domain_redact: bool = True
    if reveal_domain_data and settings.env in ("development", "test"):
        effective_domain_redact = False

    level = _resolve_level(settings.log_level)

    # ── Build output handler ──────────────────────────────────────
    if settings.log_format == "json":
        handler = _build_file_handler(settings)
    else:
        handler = _build_console_handler(settings)

    # ── Attach to root logger (idempotent) ────────────────────────
    root_logger = logging.getLogger()
    for existing_handler in list(root_logger.handlers):
        root_logger.removeHandler(existing_handler)
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # ── Configure structlog internal processors ───────────────────
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            _add_timestamp,
            _add_request_id,
            SensitiveDataRedactor(
                pii_always_redact=True,
                domain_redact=effective_domain_redact,
            ),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # ── Suppress noisy third-party loggers ────────────────────────
    for logger_name in (
        "uvicorn.access",
        "httpx",
        "httpcore",
        "chardet",
    ):
        logging.getLogger(logger_name).setLevel(logging.WARNING)

    # Pre-configure future integration points at quiet levels
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("alembic.runtime.migration").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Return a standard-library ``Logger``.

    This is a convenience over ``logging.getLogger(name)`` that creates
    a single, discoverable import point for the whole codebase.
    """
    return logging.getLogger(name)
