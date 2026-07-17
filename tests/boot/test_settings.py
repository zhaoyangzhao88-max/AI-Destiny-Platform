"""
Tests for ``zhiming.boot.settings`` — application configuration.

Covers: default values, environment variable override, type coercion,
field validation (fail-fast), ``SecretStr`` masking, cross-field validation
(production requires secret key), Lazy Singleton via ``@lru_cache``,
``cache_clear()`` isolation, and direct constructor override for test injection.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import pytest
from pydantic import SecretStr as PydanticSecretStr
from pydantic import ValidationError

from zhiming.boot import Settings, get_settings

if TYPE_CHECKING:
    from collections.abc import Generator

# ── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> Generator[None, None, None]:
    """Clear the ``get_settings`` LRU cache before each test.

    This ensures tests that exercise the DI path
    (``get_settings()``) start with a fresh singleton, and that
    ``monkeypatch``-set env vars are picked up on first access.
    """
    get_settings.cache_clear()
    yield


# ── Default Values ────────────────────────────────────────────────


class TestDefaults:
    """Verify every field has the expected default value."""

    def test_env_defaults_to_development(self) -> None:
        s = Settings()
        assert s.env == "development"

    def test_debug_defaults_to_false(self) -> None:
        s = Settings()
        assert s.debug is False

    def test_host_default(self) -> None:
        s = Settings()
        assert s.host == "127.0.0.1"

    def test_port_default(self) -> None:
        s = Settings()
        assert s.port == 8000

    def test_log_level_default(self) -> None:
        s = Settings()
        assert s.log_level == "DEBUG"

    def test_log_format_default(self) -> None:
        s = Settings()
        assert s.log_format == "console"

    def test_db_url_default(self) -> None:
        s = Settings()
        assert s.db_url == "sqlite:///./data/zhiming.db"

    def test_cors_origins_default(self) -> None:
        s = Settings()
        assert s.cors_origins == ["*"]

    def test_data_dir_default(self) -> None:
        s = Settings()
        assert s.data_dir == "./data"

    def test_secret_key_default_is_empty(self) -> None:
        s = Settings()
        assert s.secret_key.get_secret_value() == ""

    def test_llm_api_key_default_is_empty(self) -> None:
        s = Settings()
        assert s.llm_api_key.get_secret_value() == ""

    def test_llm_provider_default_empty(self) -> None:
        s = Settings()
        assert s.llm_provider == ""

    def test_llm_model_default_empty(self) -> None:
        s = Settings()
        assert s.llm_model == ""


# ── Environment Variable Override ─────────────────────────────────


class TestEnvOverride:
    """Environment variables with ``ZHIMING_`` prefix override defaults."""

    def test_debug_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ZHIMING_DEBUG", "true")
        s = Settings()
        assert s.debug is True

    def test_port_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ZHIMING_PORT", "9000")
        s = Settings()
        assert s.port == 9000

    def test_db_url_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ZHIMING_DB_URL", "sqlite:///:memory:")
        s = Settings()
        assert s.db_url == "sqlite:///:memory:"

    def test_env_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("ZHIMING_ENV", "test")
        s = Settings()
        assert s.env == "test"

    def test_env_var_takes_precedence_over_default(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Env var should override the class default."""
        monkeypatch.setenv("ZHIMING_DEBUG", "true")
        s = Settings()
        assert s.debug is True

    def test_boolean_env_variants(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """pydantic should coerce various truthy values."""
        for val in ("1", "True", "true", "yes"):
            monkeypatch.setenv("ZHIMING_DEBUG", val)
            s = Settings()
            assert s.debug is True, f"Failed to coerce '{val}' to True"


# ── Direct Constructor Override ───────────────────────────────────


class TestDirectOverride:
    """Direct ``Settings(key=value)`` should override everything."""

    def test_env_override(self) -> None:
        s = Settings(env="test")
        assert s.env == "test"

    def test_db_url_override(self) -> None:
        s = Settings(db_url="sqlite:///:memory:")
        assert s.db_url == "sqlite:///:memory:"

    def test_multi_field_override(self) -> None:
        s = Settings(env="test", debug=True, port=9999, data_dir="/tmp/test")
        assert s.env == "test"
        assert s.debug is True
        assert s.port == 9999
        assert s.data_dir == "/tmp/test"


# ── Field Validation (Fail-Fast) ──────────────────────────────────


class TestEnvValidation:
    """``env`` must be one of ``development | test | production``."""

    @pytest.mark.parametrize("invalid_env", ["", "prod", "staging", "DEV", "Production", "abc"])
    def test_rejects_invalid_env(self, invalid_env: str) -> None:
        with pytest.raises(ValidationError, match="development.*test.*production"):
            Settings(env=invalid_env)  # type: ignore[arg-type]

    @pytest.mark.parametrize(
        ("valid_env", "extra_kwargs"),
        [
            ("development", {}),
            ("test", {}),
            ("production", {"secret_key": "prod-secret-key"}),
        ],
    )
    def test_accepts_valid_env(self, valid_env: str, extra_kwargs: dict) -> None:
        s = Settings(env=valid_env, **extra_kwargs)  # type: ignore[arg-type]
        assert s.env == valid_env


class TestLogLevelValidation:
    """``log_level`` must be a valid logging level."""

    @pytest.mark.parametrize("invalid", ["TRACE", "FATAL", "unknown", "debugg", ""])
    def test_rejects_invalid_log_level(self, invalid: str) -> None:
        with pytest.raises(ValidationError):
            Settings(log_level=invalid)

    @pytest.mark.parametrize("valid", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
    def test_accepts_valid_uppercase(self, valid: str) -> None:
        s = Settings(log_level=valid)
        assert s.log_level == valid

    def test_normalizes_lowercase(self) -> None:
        s = Settings(log_level="info")
        assert s.log_level == "INFO"

    def test_normalizes_mixed_case(self) -> None:
        s = Settings(log_level="Debug")
        assert s.log_level == "DEBUG"


class TestLogFormatValidation:
    """``log_format`` must be ``json`` or ``console``."""

    @pytest.mark.parametrize("invalid", ["xml", "text", "pretty", ""])
    def test_rejects_invalid_format(self, invalid: str) -> None:
        with pytest.raises(ValidationError):
            Settings(log_format=invalid)

    def test_accepts_json(self) -> None:
        s = Settings(log_format="json")
        assert s.log_format == "json"

    def test_accepts_console(self) -> None:
        s = Settings(log_format="console")
        assert s.log_format == "console"

    def test_normalizes_uppercase(self) -> None:
        s = Settings(log_format="JSON")
        assert s.log_format == "json"


class TestPortValidation:
    """``port`` must be in 1024–65535 range."""

    @pytest.mark.parametrize("invalid_port", [0, 1, 80, 443, 1000, 1023, 70000, 99999])
    def test_rejects_out_of_range(self, invalid_port: int) -> None:
        with pytest.raises(ValidationError):
            Settings(port=invalid_port)

    @pytest.mark.parametrize("valid_port", [1024, 2048, 8000, 30000, 65535])
    def test_accepts_valid_range(self, valid_port: int) -> None:
        s = Settings(port=valid_port)
        assert s.port == valid_port


class TestCorsOriginsValidation:
    """``cors_origins`` accepts JSON string or list."""

    def test_parses_json_array_string(self) -> None:
        s = Settings(cors_origins='["http://localhost:3000", "http://localhost:5173"]')
        assert s.cors_origins == ["http://localhost:3000", "http://localhost:5173"]

    def test_accepts_list_directly(self) -> None:
        s = Settings(cors_origins=["*"])
        assert s.cors_origins == ["*"]

    def test_single_url_string(self) -> None:
        """A string that is not a JSON array is wrapped in a list."""
        s = Settings(cors_origins="http://localhost:3000")
        assert s.cors_origins == ["http://localhost:3000"]

    def test_empty_list(self) -> None:
        s = Settings(cors_origins=[])
        assert s.cors_origins == []


# ── Cross-Field Validation ────────────────────────────────────────


class TestProductionSecretKey:
    """``production`` environment **requires** a non-empty ``secret_key``."""

    def test_production_without_secret_raises(self) -> None:
        with pytest.raises(ValidationError, match="ZHIMING_SECRET_KEY"):
            Settings(env="production", secret_key="")

    def test_production_with_secret_succeeds(self) -> None:
        s = Settings(env="production", secret_key="super-secret-key")
        assert s.env == "production"
        assert s.secret_key.get_secret_value() == "super-secret-key"

    def test_development_without_secret_ok(self) -> None:
        """Only production is gated — dev/test may run without a secret key."""
        s = Settings(env="development")
        assert s.env == "development"

    def test_test_without_secret_ok(self) -> None:
        s = Settings(env="test")
        assert s.env == "test"
        assert s.secret_key.get_secret_value() == ""


# ── Sensitive Field Protection ────────────────────────────────────


class TestSecretMasking:
    """Sensitive fields must be masked in ``repr()`` and not leaked to logs."""

    def test_secret_key_is_secret_str_type(self) -> None:
        s = Settings(secret_key="my-secret")
        assert isinstance(s.secret_key, PydanticSecretStr)

    def test_secret_key_repr_masked(self) -> None:
        s = Settings(secret_key="my-secret")
        assert "my-secret" not in repr(s.secret_key)
        assert "**" in repr(s.secret_key) or "SecretStr" in repr(s.secret_key)

    def test_llm_api_key_is_secret_str_type(self) -> None:
        s = Settings(llm_api_key="sk-12345")
        assert isinstance(s.llm_api_key, PydanticSecretStr)

    def test_llm_api_key_repr_masked(self) -> None:
        s = Settings(llm_api_key="sk-12345")
        assert "sk-12345" not in repr(s.llm_api_key)

    def test_model_dump_exclude_secrets(self) -> None:
        """``model_dump(exclude=...)`` should not contain secret values."""
        s = Settings(secret_key="my-secret", llm_api_key="sk-12345")
        dumped = s.model_dump(exclude={"secret_key", "llm_api_key"})
        assert "secret_key" not in dumped
        assert "llm_api_key" not in dumped
        assert dumped["env"] == "development"


# ── Lazy Singleton ────────────────────────────────────────────────


class TestGetSettings:
    """``get_settings()`` must behave as a Lazy Singleton."""

    def test_returns_settings_instance(self) -> None:
        s = get_settings()
        assert isinstance(s, Settings)

    def test_same_instance_on_multiple_calls(self) -> None:
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

    def test_cache_clear_returns_new_instance(self) -> None:
        s1 = get_settings()
        get_settings.cache_clear()
        s2 = get_settings()
        assert s1 is not s2

    def test_autouse_fixture_ensures_fresh_cache(self) -> None:
        """Because ``_reset_settings_cache`` runs before each test,
        every test starts with a cold cache."""
        s1 = get_settings()  # This test is the first consumer
        s2 = get_settings()
        assert s1 is s2  # Within the same test, cache holds

    def test_settings_picks_up_env_var_after_cache_clear(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """After ``cache_clear()``, a newly set env var must be visible."""
        monkeypatch.setenv("ZHIMING_DEBUG", "true")
        s = get_settings()
        assert s.debug is True


# ── Error Messages ────────────────────────────────────────────────


class TestErrorMessages:
    """Validation error messages should be human-readable."""

    def test_invalid_env_message(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Settings(env="invalid")
        msg = str(exc_info.value)
        assert "development" in msg
        assert "test" in msg
        assert "production" in msg

    def test_production_secret_missing_message(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            Settings(env="production", secret_key="")
        msg = str(exc_info.value)
        assert "ZHIMING_SECRET_KEY" in msg
