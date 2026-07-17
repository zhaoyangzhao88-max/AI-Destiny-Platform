# 知命 AI 人生档案顾问 · ZhiMing AI — Life Archive Consultant

> 基于四柱八字 × 人工智能的人生档案顾问产品

![Phase](https://img.shields.io/badge/Phase-3%20Coding-blue)

## Architecture Overview

```
┌──────────────────────────────────────────────────┐
│  Windows APP (PySide6 + Vue)        [Phase 3.4]  │
│  ┌────────────┐  ┌──────────────────────────┐    │
│  │ PySide6    │  │ Vue (QWebEngineView)      │    │
│  └─────┬──────┘  └────────────┬─────────────┘    │
│        │      API Client      │                    │
│        └──────────┬───────────┘                    │
│                   │ Local IPC (HTTP + WS)            │
├───────────────────┴──────────────────────────────────┤
│  Python Core Service                    [Phase 3.1]  │
│  ┌──────────┐ ┌─────────┐ ┌────────┐ ┌────────┐    │
│  │ FastAPI  │ │Service  │ │ Domain │ │  Data  │    │
│  │ Router   │→│  Layer  │→│ Layer  │→│ Layer  │    │
│  └──────────┘ └─────────┘ └────────┘ └────────┘    │
│  ┌──────────────────────────────────────────────┐   │
│  │ AI Agent · Bazi Engine · Rule Engine · ...   │   │
│  └──────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Prerequisites: Python >= 3.11
python --version

# Install with dev dependencies
pip install -e ".[dev]"

# Verify the package loads
python -c "import zhiming; print(f'{zhiming.__app_name__} v{zhiming.__version__}')"

# Run the CLI skeleton
python -m zhiming

# Run tests
pytest
```

## Project Structure

```
src/zhiming/        Core service Python package
├── api/            FastAPI routers (HTTP v1 + WebSocket)
├── service/        Business service orchestration
├── domain/         Domain entities and value objects
├── repository/     Data access (Repository pattern)
├── db/             Database models and migrations
├── boot/           Bootstrap: config, logging, exceptions
├── infra/          FastAPI factory, middleware, DI
├── bazi/           Bazi (Four Pillars) engine
├── rule/           Rule inference engine
├── ai/             AI Agent engine
├── prompt/         Prompt template engine
├── memory/         Three-tier memory system
└── task/           Long-running task engine
tests/              Pytest suite
client/             Windows desktop client (Phase 3.4)
docs/               Architecture and design documents
```

## Development Roadmap

| Milestone | Target | Description |
|-----------|--------|-------------|
| M1 | Phase 3.1 | Foundation: skeleton, FastAPI app, DB, repos, domain |
| M2 | Phase 3.2 | Core: Bazi engine, rule engine, services, HTTP API |
| M3 | Phase 3.3 | AI: LLM provider, agent, prompts, memory, tasks, WS |
| M4 | Phase 3.4 | Client: PySide6 shell, Vue UI, packaging |
| M5 | Phase 3.5 | Polish: testing, performance, docs, release |

## Documentation

See [docs/HANDOVER.md](docs/HANDOVER.md) for the full project overview.
