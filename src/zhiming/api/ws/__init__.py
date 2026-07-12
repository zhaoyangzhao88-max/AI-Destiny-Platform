"""
WebSocket message handlers.

Implements the WebSocket protocol defined in ``docs/14_WebSocket实时通信协议设计.md``.

Responsibilities:
    - Connection lifecycle (connect, authenticate, disconnect)
    - Heartbeat management (ping/pong keep-alive)
    - Message routing by type (chat.*, ai.*, task.*, system.*)
    - Streaming token output for AI responses
    - Progress push for long-running tasks
    - Error and notification delivery to connected clients

Implemented in E-API-WS Iterations 1-2.
"""
