"""
Prompt template engine.

Manages Jinja2-based prompt templates for the ZhiMing AI persona, bazi
analysis, report generation, follow-up questions, and memory injection.

Responsibilities:
    - Template loading and rendering from ``templates/`` directory
    - Persona prompt management (system prompt, role definition)
    - Analysis step prompts (each of the 6 pipeline stages)
    - Memory injection into prompts (working / summary / core)
    - Template versioning and hot-reload support

Implemented in E-PROMPT Iterations 1-4.
"""
