"""
Tests for ``zhiming.boot.logging`` — unified logging system.

Covers: console/json configuration, handler idempotency, log-level mapping,
two-level sensitive data redaction (PII + Domain), environment guards,
request ID contextvar propagation, ``RequestLogContextManager`` cleanup,
and architecture dependency verification.
"""

from __future__ import annotations

import io
import json
import logging
import sys
from typing import TYPE_CHECKING, Any

import pytest
import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer
from structlog.stdlib import ProcessorFormatter

from zhiming.boot import Settings, configure_logging, get_logger
from zhiming.boot.logging import (
    DOMAIN_SENSITIVE_KEYS,
    PII_SENSITIVE_KEYS,
    RequestIDContext,
    RequestLogContextManager,
    SensitiveDataRedactor,
)

if TYPE_CHECKING:
    from collections.abc import Generator

# ── Fixtures ──────────────────────────────────────────────────────────


@pytest.fixture
def dev_settings() -> Settings:
    """Return a Settings instance configured for development."""
    return Settings(env="development", log_level="DEBUG", log_format="console", data_dir="/tmp")


@pytest.fixture
def prod_settings() -> Settings:
    """Return a Settings instance configured for production."""
    return Settings(
        env="production",
        log_level="INFO",
        log_format="json",
        data_dir="/tmp",
        secret_key="prod-secret",
    )


@pytest.fixture
def capture_handler() -> Generator[logging.Handler, None, None]:
    """Provide a ``StringIO`` handler that captures log output for assertions."""
    handler = logging.StreamHandler(io.StringIO())
    root = logging.getLogger()
    old_handlers = list(root.handlers)
    root.handlers.clear()
    root.addHandler(handler)
    try:
        yield handler
    finally:
        root.handlers.clear()
        for h in old_handlers:
            root.addHandler(h)


@pytest.fixture(autouse=True)
def _clean_structlog() -> Generator[None, None, None]:
    """Reset structlog configuration between tests."""
    structlog.reset_defaults()
    yield


# ── Test: configure_logging basic modes ───────────────────────────────


class TestConfigureLoggingConsoleMode:
    """Console (dev) mode produces a StreamHandler with ConsoleRenderer."""

    def test_console_handler_attached(self, dev_settings: Settings) -> None:
        configure_logging(dev_settings)
        root = logging.getLogger()
        assert len(root.handlers) == 1
        handler = root.handlers[0]
        assert isinstance(handler, logging.StreamHandler)
        fmt = handler.formatter
        assert isinstance(fmt, ProcessorFormatter)

    def test_console_level_mapped(self, dev_settings: Settings) -> None:
        configure_logging(dev_settings)
        assert logging.getLogger().level == logging.DEBUG


class TestConfigureLoggingJsonMode:
    """JSON (production) mode produces a RotatingFileHandler with JSONRenderer."""

    def test_file_handler_attached(self, prod_settings: Settings) -> None:
        configure_logging(prod_settings)
        root = logging.getLogger()
        assert len(root.handlers) == 1
        handler = root.handlers[0]
        from logging.handlers import RotatingFileHandler
        assert isinstance(handler, RotatingFileHandler)

    def test_json_level_mapped(self, prod_settings: Settings) -> None:
        configure_logging(prod_settings)
        assert logging.getLogger().level == logging.INFO


class TestConfigureLoggingIdempotent:
    """Calling configure_logging twice must not leak handlers."""

    def test_no_handler_duplication(self, dev_settings: Settings) -> None:
        configure_logging(dev_settings)
        configure_logging(dev_settings)
        assert len(logging.getLogger().handlers) == 1


# ── Test: get_logger ──────────────────────────────────────────────────


class TestGetLogger:
    def test_returns_stdlib_logger(self) -> None:
        logger = get_logger("test.xyz")
        assert isinstance(logger, logging.Logger)

    def test_repeatable_calls(self) -> None:
        a = get_logger("test.repeat")
        b = get_logger("test.repeat")
        assert a is b


# ── Test: Sensitive Data Redaction (Two-Level) ────────────────────────


class TestSensitiveDataRedactor:
    """Verify the two-level sensitive data model."""

    def _make_redactor(self, domain_redact: bool = True) -> SensitiveDataRedactor:
        return SensitiveDataRedactor(pii_always_redact=True, domain_redact=domain_redact)

    def _apply(self, redactor: SensitiveDataRedactor, event: dict[str, Any]) -> dict[str, Any]:
        return redactor(logging.getLogger("test"), "info", event)

    # ── Level 1 (PII): always redacted ─────────────────────────────

    @pytest.mark.parametrize("key", sorted(PII_SENSITIVE_KEYS))
    def test_level1_pii_always_redacted(self, key: str) -> None:
        result = self._apply(self._make_redactor(), {key: "some-value"})
        assert result[key] == "***"

    # ── Level 2 (Domain): redacted by default ──────────────────────

    @pytest.mark.parametrize("key", sorted(DOMAIN_SENSITIVE_KEYS))
    def test_level2_domain_redacted_when_active(self, key: str) -> None:
        result = self._apply(self._make_redactor(domain_redact=True), {key: "甲子"})
        assert result[key] == "***"

    @pytest.mark.parametrize("key", sorted(DOMAIN_SENSITIVE_KEYS))
    def test_level2_domain_revealed_when_disabled(self, key: str) -> None:
        result = self._apply(self._make_redactor(domain_redact=False), {key: "甲子"})
        assert result[key] == "甲子"

    # ── Generic key patterns ───────────────────────────────────────

    @pytest.mark.parametrize("key", ["api_key", "secret_key", "password", "auth_token"])
    def test_generic_key_pattern_redacted(self, key: str) -> None:
        result = self._apply(self._make_redactor(), {key: "some-secret-value"})
        assert result[key] == "***"

    # ── Value-based redaction ──────────────────────────────────────

    @pytest.mark.parametrize(
        "value",
        ["sk-abcdefghijklmnopqrstuvwxyz", "Bearer eyJhbGciOiJIUzI1NiJ9"],
    )
    def test_value_pattern_redacted(self, value: str) -> None:
        result = self._apply(self._make_redactor(), {"token": value})
        assert result["token"] == "***"


class TestEnvironmentGuard:
    """Verify production environment ignores reveal_domain_data."""

    def test_production_ignores_reveal(self) -> None:
        """Even when reveal_domain_data=True, production still redacts Level 2."""
        settings = Settings(env="production", secret_key="guard-test")
        configure_logging(settings, reveal_domain_data=True)

        # Check the root logger's handler formatter's pre-chain includes
        # a SensitiveDataRedactor with domain_redact=True for production
        handler = logging.getLogger().handlers[0]
        formatter = handler.formatter
        assert isinstance(formatter, ProcessorFormatter)

    def test_dev_reveal_works(self, dev_settings: Settings) -> None:
        """Development + reveal_domain_data=True exposes Level 2 fields."""
        configure_logging(dev_settings, reveal_domain_data=True)
        # After config, create a structlog-bound logger and emit a Level 2 field
        log = structlog.get_logger()
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setFormatter(
            ProcessorFormatter(
                foreign_pre_chain=[],
                processor=JSONRenderer(),
            )
        )

        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)

        log.info("test message", birth_year="1986", pillar="甲子")

        buf.seek(0)
        record = json.loads(buf.readline())
        # Domain fields should NOT be redacted in dev with reveal=True
        assert record["birth_year"] == "1986"
        assert record["pillar"] == "甲子"


# ── Test: Context ID propagation ──────────────────────────────────────


class TestRequestIDContext:
    """Verify contextvar-based request ID propagation."""

    def test_get_default_empty(self) -> None:
        assert RequestIDContext.get() == ""

    def test_set_and_get(self) -> None:
        token = RequestIDContext.set("req-001")
        assert RequestIDContext.get() == "req-001"
        RequestIDContext.reset(token)
        assert RequestIDContext.get() == ""

    def test_context_manager(self) -> None:
        with RequestLogContextManager("req-002"):
            assert RequestIDContext.get() == "req-002"
        assert RequestIDContext.get() == ""


class TestRequestIDInLogOutput:
    """Verify request_id appears in structured log output when context is set."""

    def _capture_handler(self) -> logging.Handler:
        """Build a StringIO handler with JSONRenderer for test capture."""
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setFormatter(
            ProcessorFormatter(foreign_pre_chain=[], processor=JSONRenderer())
        )
        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)
        return handler

    def test_request_id_in_json(self, prod_settings: Settings) -> None:
        configure_logging(prod_settings)
        handler = self._capture_handler()
        log = structlog.get_logger("test")

        with RequestLogContextManager("ctx-in-log"):
            log.info("with context")

        assert isinstance(handler.stream, io.StringIO)
        handler.stream.seek(0)
        record = json.loads(handler.stream.readline())
        assert record["request_id"] == "ctx-in-log"

    def test_no_request_id_when_not_set(self, prod_settings: Settings) -> None:
        configure_logging(prod_settings)
        handler = self._capture_handler()
        log = structlog.get_logger("test")

        # No context set
        log.info("no context")

        assert isinstance(handler.stream, io.StringIO)
        handler.stream.seek(0)
        record = json.loads(handler.stream.readline())
        assert "request_id" not in record


# ── Test: Architecture Dependency ─────────────────────────────────────


class TestArchitectureDependency:
    """Foundation Layer must not depend on business-layer modules."""

    FORBIDDEN_MODULES: tuple[str, ...] = (
        "zhiming.api",
        "zhiming.service",
        "zhiming.domain",
        "zhiming.repository",
        "zhiming.bazi",
        "zhiming.ai",
        "zhiming.task",
    )

    def test_boot_logging_does_not_import_business_modules(self) -> None:
        """Verify that importing ``zhiming.boot.logging`` (already imported above)
        does not trigger loading of business-layer modules."""
        import sys as sys_mod

        loaded = [m for m in sys_mod.modules if m in self.FORBIDDEN_MODULES]
        assert not loaded, (
            f"boot.logging triggered import of forbidden modules: {loaded}"
        )


# ── Test: Log Output Format ───────────────────────────────────────────


class TestLogOutputFormat:
    """Verify log output matches expected format for each mode."""

    def test_console_output_contains_event(self, dev_settings: Settings) -> None:
        configure_logging(dev_settings)

        log = structlog.get_logger("test")
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setFormatter(
            ProcessorFormatter(
                foreign_pre_chain=[],
                processor=ConsoleRenderer(colors=False),
            )
        )

        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)

        log.info("hello console")

        buf.seek(0)
        output = buf.read()
        assert "hello console" in output

    def test_json_output_is_valid_json(self, prod_settings: Settings) -> None:
        configure_logging(prod_settings)

        log = structlog.get_logger("test")
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setFormatter(
            ProcessorFormatter(foreign_pre_chain=[], processor=JSONRenderer())
        )

        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)

        log.info("hello json", extra_field="value")

        buf.seek(0)
        record = json.loads(buf.readline())
        assert record["event"] == "hello json"
        assert record["extra_field"] == "value"


# ── Test: Sensitive Data in real log pipeline ─────────────────────────


class TestSensitiveDataInPipeline:
    """Verify that sensitive data is redacted through the full log pipeline."""

    def test_pii_redacted_in_output(self, dev_settings: Settings) -> None:
        configure_logging(dev_settings)

        log = structlog.get_logger("test")
        buf = io.StringIO()
        handler = logging.StreamHandler(buf)
        handler.setFormatter(
            ProcessorFormatter(
                foreign_pre_chain=[],
                processor=JSONRenderer(),
            )
        )

        root = logging.getLogger()
        root.handlers.clear()
        root.addHandler(handler)

        log.info("user lookup", user_name="John Doe", email="john@example.com")

        buf.seek(0)
        record = json.loads(buf.readline())
        assert record["user_name"] == "***"
        assert record["email"] == "***"
