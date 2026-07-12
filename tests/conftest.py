"""
Shared pytest fixtures for the zhiming test suite.

This module provides fixtures shared across all test modules.
Additional fixtures will be added incrementally as epics are implemented.
"""

import pytest

from zhiming.boot import get_settings


@pytest.fixture(autouse=True)
def _reset_settings_cache() -> None:
    """Clear the ``get_settings`` LRU cache before each test.

    This ensures:
        - ``monkeypatch``-set env vars are picked up on first ``get_settings()`` call.
        - Each test starts with a cold cache, preventing cross-test pollution.
    """
    get_settings.cache_clear()


# TODO(E-DB): Add database fixtures (in-memory SQLite, session rollback)
# TODO(E-REPO): Add repository fixtures (repo instances with test DB)
# TODO(E-DOMAIN): Add domain entity factory fixtures (builders / fakes)
# TODO(E-API): Add test client fixture (httpx.AsyncClient with app)
