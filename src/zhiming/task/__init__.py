"""
Long-running task engine.

Manages asynchronous task lifecycle, progress tracking, and disconnection
recovery for operations that exceed HTTP request/response boundaries.

Responsibilities:
    - Task state machine: pending → running → completed / failed / cancelled
    - Progress tracking with percentage and status messages
    - WebSocket push for real-time task updates
    - Task persistence and recovery after client disconnect
    - Concurrent task execution with configurable worker pool

Used by: AI analysis pipeline, report generation, data import/export.

Implemented in E-TASK Iterations 1-3.
"""
