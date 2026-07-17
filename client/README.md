# Client Applications

This directory will contain the Windows desktop client application,
developed in **Phase 3.4** of the project.

## Structure (Future)

```
client/
├── desktop/           # PySide6 shell application (E-GUI)
│   ├── window/        # Main window, tray, menus
│   ├── process/       # Core service process lifecycle
│   └── api_client/    # HTTP + WebSocket client (Layer 2)
│
└── web/               # Vue UI module (E-VUE)
    ├── src/           # Vue components, pages, stores
    └── public/        # Static assets
```

## Development

The desktop shell (PySide6) hosts the Vue UI via QWebEngineView.
Communication between the UI and the Python core service is via local
HTTP REST + WebSocket connections (IPC locally).

See `docs/08_系统架构设计.md` for the full architecture description.
