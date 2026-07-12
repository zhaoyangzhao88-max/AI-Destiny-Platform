"""
Repository layer.

Implements the Repository pattern for data access, providing a clean
abstraction over the database layer for the service layer.

Responsibilities:
    - ``BaseRepository[T]`` — generic CRUD + pagination base class
    - ``UserRepo`` — user account persistence
    - ``BaziChartRepo`` — bazi chart caching and retrieval
    - ``ProfileRepo`` — user profile persistence
    - ``ReportRepo`` — analysis report storage
    - ``TaskRepo`` — task record persistence
    - ``PreferenceRepo`` — user preference storage

Implemented in E-REPO Iterations 1-6.
"""
