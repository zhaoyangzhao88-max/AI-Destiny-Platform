"""
Infrastructure module.

Provides the FastAPI application factory, dependency injection container,
and middleware components.

Responsibilities:
    - ``create_app()`` factory with lifespan management
    - Middleware: CORS, request ID, authentication, error handling, rate limiting
    - Dependency injection wiring for services, repositories, and domain
    - Health check endpoint (``GET /api/v1/config/health``)

Implemented in E-INFRA Iterations 1-5.
"""
