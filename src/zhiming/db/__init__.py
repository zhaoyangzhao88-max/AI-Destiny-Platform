"""
Database module.

Manages SQLAlchemy engine configuration, declarative ORM base class,
all model definitions (User, Profile, BaziChart, Report, Task, Preference),
and Alembic migration support.

Responsibilities:
    - SQLAlchemy ``create_async_engine`` and session factory
    - Declarative base with common mixins (timestamps, soft-delete)
    - Alembic ``env.py`` and migration script generation
    - Connection lifecycle tied to FastAPI lifespan events

Implemented in E-DB Iterations 1-4.
"""
