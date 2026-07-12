"""
API layer.

FastAPI router modules for HTTP REST endpoints (versioned under ``/api/v1/``)
and WebSocket handlers (under ``/ws/v1/``).

Implements the API contract defined in ``docs/13_API接口契约设计.md`` and the
WebSocket protocol from ``docs/14_WebSocket实时通信协议设计.md``.

Subpackages:
    v1/     — HTTP v1 routers (34+ endpoints across 8 iterations)
    ws/     — WebSocket message handlers (connect, auth, heartbeat, messages)

Implemented in E-API Iterations 1-8 (HTTP) and E-API-WS Iterations 1-2 (WS).
"""
