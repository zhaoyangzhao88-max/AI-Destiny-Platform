"""
AI Agent engine.

Manages the ZhiMing AI persona (per ADR-004 and docs/05) as an orchestrator
that drives the 6-step analysis pipeline (docs/07).

Responsibilities:
    - LLM provider abstraction (multi-provider: OpenAI, Anthropic, …)
    - Agent core: conversation context, session tracking, tool dispatching
    - 6-step analysis pipeline: greeting → chart → analysis → deep-dive → report → archive
    - Structured output parsing and data-tier assignment
    - Provider failover, retry, rate-limit management

Implemented in E-AI Iterations 1-5.
"""
