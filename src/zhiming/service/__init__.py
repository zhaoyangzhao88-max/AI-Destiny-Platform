"""
Business service layer.

Orchestrates domain logic, repository access, and external integrations.
Each service exposes a clean public API consumed by the router layer.

Services:
    UserService         — User registration, auth, profile management
    BaziService         — Bazi chart calculation and caching
    ReportService       — Life analysis report generation and retrieval
    ChatService         — Conversational AI interaction
    ConfigService       — Application configuration and feature toggles
    KnowledgeService    — Glossary and knowledge base queries
    TaskService         — Long-running task management and status

Implemented in E-SVC Iterations 1-6.
"""
