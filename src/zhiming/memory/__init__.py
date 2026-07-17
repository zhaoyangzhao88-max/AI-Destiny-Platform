"""
Three-tier memory system.

Implements the memory architecture defined in ``docs/19_分层记忆架构设计.md``.

Tiers:
    Working Memory   — Current session context (recent messages, active topic)
    Summary Memory   — Compressed conversation history (periodic summarization)
    Core Memory      — Long-term user profile and persistent facts

Responsibilities:
    - Memory CRUD operations per tier
    - Automatic summarization triggers
    - Memory injection into AI agent context
    - Persistence to database (via Repository layer)

Implemented in E-MEM Iterations 1-4.
"""
