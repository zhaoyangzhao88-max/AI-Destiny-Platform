"""
API v1 routers.

Implements HTTP REST endpoints for all business domains, versioned under
the ``/api/v1/`` URL prefix.

Endpoint groups:
    User    — 9 endpoints: register, login, profile CRUD, preferences
    Bazi    — 8 endpoints: chart calculate, cache, history
    Report  — 6 endpoints: generate, list, get, compare
    Task    — 5 endpoints: create, status, cancel, list
    Knowledge — 3 endpoints: glossary, search
    Config  — 3 endpoints: health, settings, info

Implemented in E-API Iterations 2-8.
"""
