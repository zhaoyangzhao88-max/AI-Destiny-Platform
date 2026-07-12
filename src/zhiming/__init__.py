"""
zhiming — 知命 AI 人生档案顾问 核心服务包

ZhiMing AI — Life Archive Consultant Core Service Package.

This package implements the Python core service for the ZhiMing AI
application. It provides business logic, data management, AI analysis,
and API endpoints consumed by the Windows desktop client.

Architecture Layers (frozen per docs/21):
    1. Presentation   — client/ (PySide6 + Vue)          [Phase 3.4]
    2. API Client     — client/ (HTTP + WS client)       [Phase 3.4]
    3. Router         — zhiming.api/ (FastAPI)            [Phase 3.2]
    4. Service        — zhiming.service/                  [Phase 3.2]
    5. Domain         — zhiming.domain/                   [Phase 3.1]
    6. Data           — zhiming.repository/ + zhiming.db/ [Phase 3.1]

Subpackages:
    boot        — Bootstrap: config, logging, exceptions, utilities
    infra       — Infrastructure: FastAPI factory, middleware, DI
    db          — Database: SQLAlchemy models, Alembic migrations
    repository  — Data access layer (Repository pattern)
    domain      — Domain entities, value objects, enums
    bazi        — Bazi (Four Pillars) calculation engine
    rule        — Rule inference engine for mingli analysis
    service     — Business service layer (orchestration)
    api         — FastAPI HTTP routers + WebSocket handlers
    ai          — AI Agent engine (LLM provider, agent, pipeline)
    prompt      — Prompt template engine
    memory      — Three-tier memory (working, summary, core)
    task        — Long-running task engine
"""

__version__ = "0.1.0"
__app_name__ = "zhiming"
__description__ = "ZhiMing AI — Life Archive Consultant Core Service"
