"""
Entry point for the ZhiMing core service.

Invoked via: python -m zhiming

Future subcommands (implemented in later epics):
    serve       — Start the FastAPI server (E-INFRA)
    migrate     — Run Alembic database migrations (E-DB)
    shell       — Interactive REPL with domain models loaded (E-DOMAIN)
"""

from __future__ import annotations

import sys

from zhiming import __app_name__, __description__, __version__


def main() -> None:
    """Display version info and available commands."""
    print(f"{__app_name__} v{__version__}")
    print(f"{__description__}")
    print()
    print("Available subcommands (future):")
    print("  serve     Start the FastAPI server")
    print("  migrate   Run database migrations")
    print("  shell     Open an interactive shell")
    print()
    print("Usage: python -m zhiming [subcommand]")


if __name__ == "__main__":
    main()
