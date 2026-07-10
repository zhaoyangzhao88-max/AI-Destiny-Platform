# 22 — Phase 3 Development Plan

> **版本:** v1.0 | **日期:** 2026-07-10 | **状态:** ✅ Active  
> **治理角色:** Project Architect | **Agent ID:** Agent-20260710-02  
> **基于:** Architecture Freeze (docs/21) | Product Owner Approval (docs/20) | 全部 P0 Closed  
> **基线文档:** docs/08, docs/13, docs/14, docs/19, ADR-001~012 & ADR-020

---

## 📋 目录

- [1. Executive Summary](#1-executive-summary)
- [2. Development Principles](#2-development-principles)
- [3. Development Roadmap](#3-development-roadmap)
- [4. Milestones](#4-milestones)
- [5. Epic Breakdown](#5-epic-breakdown)
- [6. Task Breakdown](#6-task-breakdown)
- [7. Development Order & Dependencies](#7-development-order--dependencies)
- [8. Risk Control](#8-risk-control)
- [9. Definition of Done](#9-definition-of-done)

---

## 1. Executive Summary

这是**知命 AI 人生档案顾问**项目的 **Phase 3 开发执行计划**。

**Phase 3 目标：** 交付可运行的 MVP（Minimum Viable Product），涵盖：
- Python 核心服务（FastAPI）—— BaZi 排盘引擎、AI 分析引擎、分层记忆引擎、任务管理
- HTTP API（REST）—— 34 个端点，涵盖用户/排盘/报告/任务/知识库/配置
- WebSocket 实时通信 —— 17 种消息类型，支持 AI 流式对话 + 长任务推送
- Windows 桌面应用 —— PySide6 外壳 + QWebEngineView 嵌入 Vue 前端
- 完整的单元测试、集成测试、端到端测试覆盖

**硬约束：**
- 🧊 架构基线已冻结（docs/21）—— 开发期间不得违反
- 🧊 API 契约已冻结（docs/13）—— 端点、数据模型、错误码不可修改
- 🧊 WebSocket 协议已冻结（docs/14）—— 消息类型、心跳、重连不可修改
- 🧊 13 条 ADR 已批准冻结（ADR-001~012 & ADR-020）—— 不可绕过
- 📝 ADR-014~019 为 Draft 状态，仅作设计参考
- 🟡 17 项 P1 + 9 项 P2 风险开放，不阻断 Phase 3 但需持续跟踪

**路线：** 共 **3 个子阶段**、**5 个里程碑**、**18 个 Epic**、**~110 个 Task**。

---

## 2. Development Principles

### 2.1 不可违反的红线（Hard Rules）

| # | 原则 | 说明 |
|---|------|------|
| P1 | **Architecture Freeze 不可违反** | docs/21 冻结的 6 维基线（架构设计/ADR/API 契约/WS 协议/记忆架构/风险等级）不得擅自修改。任何偏离必须走 RFC → ADR → Review → Approval 正式流程 |
| P2 | **API Contract 不可修改** | docs/13 中的所有 HTTP 端点定义（路径/方法/请求体/响应体/状态码/错误码）和 docs/14 中的 WebSocket 消息类型（type/message_id/data 结构）为冻结内容。只允许**严格向后兼容的扩展**（新增可选字段、新增端点），不允许修改/删除/重命名已有定义 |
| P3 | **Approved ADR 不可绕过** | ADR-001~012 和 ADR-020 的决策内容是强制约束。任何功能实现必须引用其约束的 ADR 并与之对齐 |
| P4 | **数据三层体系不可破坏** | ADR-012 定义的 Fact / Inference / Pending 三层体系和流转方向（Pending→Inference→Fact）为不可逆设计 |
| P5 | **三层记忆架构不可重构** | docs/19 定义的三层记忆模型（工作/摘要/核心）及其与 ADR-012 的映射关系为基本设计。设计参数（70% 水位线、20 轮保留量）可作为调优参数调整，但三层结构不可变更 |

### 2.2 开发纪律

| # | 纪律 | 说明 |
|---|------|------|
| D1 | **文件优先** | 编码前必须读取相关基线文档，禁止仅凭摘要或记忆编码 |
| D2 | **ADR 引用** | 每个 Epic 的 README 或实现说明必须引用其相关的 ADR 编号 |
| D3 | **先 Test 后 Code** | 新功能必须同步编写测试，TDD 为推荐但不强制 |
| D4 | **小步提交** | 每个 Task 完成后提交一次，确保 git log 可追溯 |
| D5 | **日志记录** | 每次改动后更新 docs/11_AI协作日志.md |
| D6 | **越权止步** | 发现冻结基线问题 → 停止编码 → 按 RFC 流程提交变更请求 |

### 2.3 Draft ADR 处理原则

ADR-014~019 为 Draft 状态，**不可作为约束性设计依据**，但可作为方向参考。如开发过程中发现需要确认这些 Draft ADR 的内容，应：

1. 标记为 `⚠️ [设计依赖 Draft ADR-0XX]`
2. 在产品负责人确认其状态前，优先使用 Approved ADR 的方案兼容方向
3. 如需完整实现，先请求 Product Owner 确认该 ADR 状态

---

## 3. Development Roadmap

Phase 3 划分为 **3 个子阶段**，每个子阶段交付一组可独立验证的能力。

```
Phase 3.1: Foundation      Phase 3.2: Core Logic         Phase 3.3: Delivery
┌──────────────────┐      ┌─────────────────────┐      ┌─────────────────────┐
│ E-BOOT           │      │ E-BAZI              │      │ E-GUI-SHELL         │
│ E-INFRA          │      │ E-AI                │      │ E-GUI-VUE           │
│ E-DB             │      │ E-PROMPT            │      │ E-INTEGRATE         │
│ E-REPO           │      │ E-MEMORY            │      │ E-TEST              │
│ E-AUTH           │      │ E-KNOW              │      │ E-PKG               │
│ E-TASK           │      │ E-REPORT            │      └─────────────────────┘
│ E-API (基础框架)  │      │ E-API (完整端点)     │
│ E-WS (基础框架)   │      │ E-WS (完整消息)      │
└──────────────────┘      └─────────────────────┘
     │                           │                         │
     ▼                           ▼                         ▼
  M1: Foundation           M3: Core Logic             M5: MVP Release
  Ready                   Complete
     │                                                   
     ▼                                                   
  M2: API Complete ← 部分任务从 Phase 3.1 延续          
     └────────── M4: GUI Functional ← Phase 3.2 输出为前置条件
```

### Phase 3.1: Foundation（地基工程）

**目标：** 建立从零到可运行 Python 核心服务的完整工程骨架

**包含 Epic：** E-BOOT, E-INFRA, E-DB, E-REPO, E-AUTH, E-TASK

**进入条件：** Phase 3 已获 Product Owner 批准启动 ✅

**完成条件：**
- Python 项目骨架可运行，FastAPI 启动成功
- SQLite 数据库初始化，所有表创建完成，迁移工具就绪
- Repository 层完整实现
- JWT 认证流程（注册→登录→鉴权）完整可用
- Task 引擎状态机运行正常
- 健康检查端点 `/api/v1/config/health` 响应正常

**输出：** M1 + M2（API 端点在此阶段完成实现）

### Phase 3.2: Core Logic（核心引擎）

**目标：** 实现所有业务逻辑引擎——排盘、AI 对话、记忆、报告、知识库

**包含 Epic：** E-BAZI, E-AI, E-PROMPT, E-MEMORY, E-KNOW, E-REPORT, E-API（完整）, E-WS（完整）

**进入条件：** M1 已完成（Foundation Ready）

**完成条件：**
- BaZi 排盘可正确计算四柱/五行/大运/流年
- LLM 集成完成，AI 流式对话可用
- Prompt 模板系统完整，模块化管理
- 三层记忆引擎实现上下文注入和压缩
- 知识库查询和语义搜索可用
- 报告生成和版本管理可用
- 所有 34 个 HTTP 端点实现并通过测试
- WebSocket 全部 17 种消息类型实现

**输出：** M2（如未在 Phase 3.1 完成）+ M3

### Phase 3.3: Delivery（交付工程）

**目标：** 构建 Windows 桌面应用前端、集成双通道通信、完成测试和打包

**包含 Epic：** E-GUI-SHELL, E-GUI-VUE, E-INTEGRATE, E-TEST, E-PKG

**进入条件：** M3 已完成（Core Logic Complete）

**完成条件：**
- PySide6 桌面外壳可启动核心服务
- Vue 前端渲染所有核心页面
- Qt WebChannel + HTTP/WS 双通道集成完成
- 端到端 BaZi 分析流程可运行
- 测试覆盖率 ≥ 80%（核心模块）
- NSIS 安装包可生成、可安装
- 安装后应用可独立运行（无需开发环境）

**输出：** M4 + M5

---

## 4. Milestones

### M1: Foundation Ready

| 维度 | 内容 |
|------|------|
| **ID** | MS-01 |
| **名称** | Foundation Ready |
| **子阶段** | Phase 3.1 |
| **进入条件** | Phase 3 批准启动 |
| **完成条件** | (1) `uvicorn core.main:app` 启动成功，health 端点返回 200<br>(2) SQLite 数据库初始化完成，Alembic migration head 为最新<br>(3) 所有 Repository 接口实现并可通过 DI 注入<br>(4) 用户注册→登录→鉴权流程端到端可用<br>(5) Task 引擎创建/查询/取消功能正常 |
| **交付物** | `core/` 项目骨架、`core/db/` 数据库层、`core/repositories/` 全部 repo、`core/auth/` 认证模块、`core/task/` 任务引擎 |
| **验证方式** | `pytest tests/unit/` 全部通过 + health check 端点手动验证 |

### M2: API Complete

| 维度 | 内容 |
|------|------|
| **ID** | MS-02 |
| **名称** | API Complete |
| **子阶段** | Phase 3.1 → Phase 3.2 过渡 |
| **进入条件** | M1 完成 |
| **完成条件** | (1) 34 个 HTTP 端点全部实现并响应正确状态码<br>(2) 14 个 WebSocket 消息类型（排除未来扩展）全部实现<br>(3) 所有请求/响应模型与 docs/13 完全对齐<br>(4) 统一错误码体系实现，每种错误返回正确 error code<br>(5) 分页、排序、过滤功能正确 |
| **交付物** | `core/api/` 路由层完整实现、`core/ws/` WebSocket 层完整实现 |
| **验证方式** | API 自动化测试覆盖全部端点 + 手动验证 WS 连接和消息收发 |

### M3: Core Logic Complete

| 维度 | 内容 |
|------|------|
| **ID** | MS-03 |
| **名称** | Core Logic Complete |
| **子阶段** | Phase 3.2 |
| **进入条件** | M2 完成 |
| **完成条件** | (1) BaZi 排盘：四柱/五行/大运/流年/十神计算正确<br>(2) AI 引擎：LLM 连接成功，token 流式输出到客户端<br>(3) Prompt 引擎：5 个以上命理分析 prompt 模板可用<br>(4) 记忆引擎：三层记忆结构完整，上下文注入顺序正确<br>(5) 报告引擎：异步生成+版本历史可用<br>(6) 知识库：术语查询+语义搜索可用 |
| **交付物** | `core/bazi/`、`core/ai/`、`core/prompt/`、`core/memory/`、`core/report/`、`core/knowledge/` 全部引擎完整 |
| **验证方式** | 各引擎独立单元测试通过 + 集成测试覆盖 BaZi 分析全流程（Postman / 自动化脚本） |

### M4: GUI Functional

| 维度 | 内容 |
|------|------|
| **ID** | MS-04 |
| **名称** | GUI Functional |
| **子阶段** | Phase 3.3 |
| **进入条件** | M3 完成 |
| **完成条件** | (1) PySide6 窗口启动并自动启动/连接 Python 核心服务<br>(2) QWebEngineView 加载 Vue 前端<br>(3) Qt WebChannel 通道建立，JavaScript 可调用 Python<br>(4) 首页/聊天/排盘/报告/档案 5 个核心页面渲染正常<br>(5) 用户注册→排盘→分析→查看报告的完整 UI 流程可用<br>(6) WebSocket 流式 AI 回复在前端实时显示 |
| **交付物** | `desktop/` PySide6 壳程序、`frontend/` Vue 应用、`qt_webchannel/` 桥接模块 |
| **验证方式** | 手动运行桌面应用 + 执行完整用户流程 |

### M5: MVP Release

| 维度 | 内容 |
|------|------|
| **ID** | MS-05 |
| **名称** | MVP Release |
| **子阶段** | Phase 3.3 收尾 |
| **进入条件** | M4 完成 |
| **完成条件** | (1) 全部单测通过，核心模块覆盖率 ≥ 80%<br>(2) 集成测试覆盖所有 API 端点、WS 消息类型、核心业务流<br>(3) 端到端测试覆盖完整用户旅程<br>(4) NSIS 安装包可构建、可安装、可运行<br>(5) 安装后的应用无需 Python/node 开发环境<br>(6) 风险跟踪表更新：关闭或确认至少 10 项 P1/P2<br>(7) HANDOVER.md 更新，包含 Phase 3 交接信息 |
| **交付物** | `dist/` 安装包（.exe）、完整测试报告、风险跟踪表更新、交接文档更新 |
| **验证方式** | 在干净的 Windows 环境中安装并测试完整用户流程 |

---

## 5. Epic Breakdown

系统拆解为 **18 个 Epic**，按构建依赖关系编号。

### 5.1 Epic 总览

| 编号 | Epic | 缩写 | 子阶段 | 工作量估 | 依赖 | 相关 ADR |
|------|------|------|--------|---------|------|---------|
| 1 | 项目启动 & 骨架搭建 | E-BOOT | 3.1 | 小 | — | — |
| 2 | 核心基础设施 | E-INFRA | 3.1 | 中 | E-BOOT | ADR-017, ADR-019 |
| 3 | 数据库 & 迁移 | E-DB | 3.1 | 中 | E-INFRA | ADR-012, ADR-013, ADR-014 |
| 4 | 仓储层 | E-REPO | 3.1 | 中 | E-DB | ADR-012 |
| 5 | 认证 & 用户模块 | E-AUTH | 3.1 | 中 | E-REPO (UserRepo) | ADR-002 |
| 6 | 任务引擎 | E-TASK | 3.1 | 中 | E-INFRA | ADR-009 |
| 7 | HTTP API 路由层 | E-API | 3.1→3.2 | 大 | E-REPO, E-AUTH, E-TASK | ADR-019 |
| 8 | WebSocket 协议层 | E-WS | 3.2 | 大 | E-TASK, E-INFRA | ADR-019 |
| 9 | BaZi 排盘引擎 | E-BAZI | 3.2 | 大 | E-DB | ADR-009, ADR-011 |
| 10 | AI 引擎（LLM 网关） | E-AI | 3.2 | 大 | E-INFRA, E-PROMPT | ADR-016 |
| 11 | Prompt 引擎 | E-PROMPT | 3.2 | 中 | — | ADR-016 |
| 12 | 记忆引擎 | E-MEMORY | 3.2 | 大 | E-DB, E-REPO, E-AI | ADR-012, ADR-016, docs/19 |
| 13 | 知识库引擎 | E-KNOW | 3.2 | 小 | E-DB, E-REPO | — |
| 14 | 报告引擎 | E-REPORT | 3.2 | 中 | E-REPO, E-AI | ADR-009 |
| 15 | GUI 外壳（PySide6） | E-GUI-SHELL | 3.3 | 中 | E-INFRA | ADR-018, ADR-020 |
| 16 | GUI 前端（Vue） | E-GUI-VUE | 3.3 | 大 | E-API, E-WS, E-AUTH | ADR-018, ADR-020 |
| 17 | 测试套件 | E-TEST | 3.3 | 大 | 全部 Epic | — |
| 18 | 打包 & 部署 | E-PKG | 3.3 | 中 | E-GUI-SHELL, E-GUI-VUE | ADR-015 |

### 5.2 Epic 描述

#### Epic 1: E-BOOT — 项目启动 & 骨架搭建

**目标：** 建立项目源码目录结构和基础开发环境。

**目录结构规划：**

```
E:\VSCODE\AI-Destiny-Platform\
├── core/                       # Python 核心服务
│   ├── main.py                 # FastAPI 入口
│   ├── app.py                  # 应用工厂
│   ├── config/                 # 配置
│   ├── db/                     # 数据库相关
│   ├── models/                 # Pydantic/SQLModel 数据模型
│   ├── repositories/           # Repository 模式实现
│   ├── services/               # 业务服务
│   │   ├── auth/               # 认证服务
│   │   ├── bazi/               # 排盘服务
│   │   ├── ai/                 # AI 服务
│   │   ├── memory/             # 记忆服务
│   │   ├── report/             # 报告服务
│   │   ├── task/               # 任务服务
│   │   └── knowledge/          # 知识库服务
│   ├── api/                    # HTTP 路由
│   ├── ws/                     # WebSocket 路由/处理器
│   ├── prompt/                 # Prompt 模板
│   ├── task/                   # 任务引擎
│   └── utils/                  # 工具函数
├── desktop/                    # PySide6 桌面外壳
│   ├── main.py                 # 入口
│   ├── window.py               # 主窗口
│   ├── system_tray.py          # 系统托盘
│   └── webchannel/             # Qt WebChannel 桥接
├── frontend/                   # Vue 前端
│   ├── src/
│   │   ├── components/         # 组件
│   │   ├── views/              # 页面
│   │   ├── services/           # API/WS 客户端
│   │   └── router/             # 路由
│   └── package.json
├── tests/                      # 测试
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── scripts/                    # 工具脚本
├── docs/                       # 文档
├── pyproject.toml
├── requirements.txt
├── Makefile 或 taskfile
└── README.md
```

**ADR 关联：** —（基础设施，无直接 ADR 约束）

#### Epic 2: E-INFRA — 核心基础设施

**目标：** 构建 Python 核心服务的通用基础设施层。

**包含：**
- FastAPI 应用工厂（生命周期管理、异常处理器、中间件注册）
- 配置管理（pydantic-settings 或 dynaconf，支持 `.env` 文件）
- 日志系统（structlog 或 loguru，结构化日志）
- 异常处理框架（自定义 Exception → HTTP 错误码映射）
- 依赖注入容器（FastAPI 原生 Depends 或注入库）
- 请求/响应序列化中间件
- CORS 中间件（开发模式支持）
- 核心工具函数

**ADR 关联：** ADR-017（业务服务与客户端解耦）、ADR-019（HTTP+WS 双通道）

#### Epic 3: E-DB — 数据库 & 迁移

**目标：** 建立 SQLite 数据库层，实现数据模型和迁移工具。

**数据模型（基于 API 契约 docs/13 提炼）：**

| 实体 | 主要字段 | 说明 |
|------|---------|------|
| User | user_id, username, password_hash, birth_info, gender, calendar_type, birth_place, timezone, created_at, updated_at | ADR-008 信息采集 |
| BaziChart | chart_id, user_id, four_pillars (JSON), five_elements (JSON), day_master, shi_shen (JSON), da_yun (JSON), liu_nian (JSON), is_primary, created_at | ADR-009 排盘 |
| Profile | profile_id, user_id, field_name, field_value, data_tier (fact/inference/pending), source, version, created_at | ADR-012 三层数据 |
| Report | report_id, user_id, chart_id, report_type, title, sections (JSON), status, version, created_at | ADR-009 报告 |
| Task | task_id, user_id, task_type, status, progress, stage, result/error (JSON), created_at, updated_at, completed_at | docs/14 §4.3 |
| Preference | preference_id, user_id, key, value, created_at, updated_at | 用户偏好 |
| ProfileVersion | version_id, profile_id, snapshot (JSON), created_at, comment | ADR-013 版本历史 |

**ADR 关联：** ADR-012（数据三层体系）、ADR-013（版本历史方向）、ADR-014（本地优先）

#### Epic 4: E-REPO — 仓储层

**目标：** 实现 Repository 模式的数据访问层。

**包含 Repository：**
1. **BaseRepository** — CRUD 基础、分页、软删除
2. **UserRepository** — 用户 CURD、用户名查重
3. **BaziChartRepository** — 排盘 CRUD、主排盘标记、按用户查询
4. **ReportRepository** — 报告 CRUD、版本查询
5. **ProfileRepository** — 用户档案 CRUD、数据层级过滤（fact/inference/pending）
6. **TaskRepository** — 任务 CRUD、状态查询、清理过期任务
7. **PreferenceRepository** — 偏好设置 CRUD
8. **ProfileVersionRepository** — 版本快照 CRUD、时间点查询

**ADR 关联：** ADR-012（ProfileRepository 必须支持 data_tier 过滤）

#### Epic 5: E-AUTH — 认证 & 用户模块

**目标：** 实现用户认证体系和用户管理服务。

**包含：**
- JWT Token 服务（HS256 签名、24h 有效期、refresh token 机制）
- 密码哈希服务（bcrypt/argon2）
- UserService（注册、登录、登出、资料查询更新）
- Auth 中间件（FastAPI Depends，从请求头提取 token 验证）
- 用户模块 HTTP 端点（9 个端点）

**ADR 关联：** ADR-002（目标用户为八字爱好者）

#### Epic 6: E-TASK — 任务引擎

**目标：** 实现异步任务状态机和生命周期管理。

**状态机：** `pending` → `processing` → `completed` / `failed` / `cancelled` / `timed_out`

**包含：**
- TaskManager（创建、更新状态、查询、取消）
- 后台 worker 调度（asyncio 后台协程或线程池）
- 进度跟踪（progress 0-100, stage 标识）
- 超时处理（5 分钟超时自动标记 timed_out）
- 重复任务去重（5 分钟内相同 chart_id + analysis_type 返回已有 task_id）
- 轮询/推送给客户端

**ADR 关联：** ADR-009（异步分析流程）

#### Epic 7: E-API — HTTP API 路由层

**目标：** 实现全部 34 个 HTTP REST 端点。

**端点分组：**

| 模块 | 端点数 | 基础路径 |
|------|--------|---------|
| 用户 | 9 | `/api/v1/users/*` |
| BaZi 排盘 | 8 | `/api/v1/bazi/charts/*` |
| 分析报告 | 6 | `/api/v1/reports/*` |
| 长任务 | 2 | `/api/v1/tasks/*` |
| 知识库 | 4 | `/api/v1/knowledge/*` |
| 系统配置 | 5 | `/api/v1/config/*` |

**包含：**
- 路由注册（router per module）
- 请求验证（Pydantic 模型）
- 响应序列化（统一响应体 `{code, message, data, request_id}`）
- 错误码映射（6 大类，22+ 具体错误码）
- 分页支持（page/page_size/sort/sort_order）
- 版本路径前缀 `/api/v1/`

**ADR 关联：** ADR-019（HTTP 通道职责）、ADR-009（7 步分析流程端点）

#### Epic 8: E-WS — WebSocket 协议层

**目标：** 实现完整的 WebSocket 实时通信协议。

**消息类型（17 种）：**
- `chat.message`（用户→服务端）
- `ai.token` / `ai.done` / `ai.error`（服务端→客户端）
- `task.created` / `task.progress` / `task.completed` / `task.failed` / `task.cancelled`（服务端→客户端）
- `task.resume`（客户端→服务端）/ `task.list`（服务端→客户端）
- `notification.system`（服务端→客户端）
- `subscribe` / `subscribe.confirmed`
- `error`（双向）
- `heartbeat.ping` / `heartbeat.pong`

**包含：**
- ConnectionManager（连接映射、鉴权、生命周期）
- MessageRouter（按 type 分发到对应 handler）
- 心跳机制（30s ping, 30s pong timeout, 90s idle timeout）
- 断线重连支持（指数退避 1s→30s、task.resume 恢复机制）
- 消息可靠性（sequence 序号、message_id 去重）
- 速率限制（单用户 10 条/s）

**ADR 关联：** ADR-019（WS 通道职责）

#### Epic 9: E-BAZI — BaZi 排盘引擎

**目标：** 实现四柱八字计算引擎。

**包含：**
- 天干地支基础库（十天干、十二地支、六十甲子、藏干、纳音）
- 公历/农历转换支持
- 真太阳时校准（geolocation API 调用，ADR-014 云端扩展）
- 年柱计算
- 月柱计算（节气校正）
- 日柱计算
- 时柱计算（含未知时辰处理，ADR-011）
- 五行分析（各元素统计、旺衰、平衡度评分）
- 十神（Shi Shen）计算
- 大运（Da Yun）计算 + 起运时间
- 流年（Liu Nian）计算
- 排盘 Chart 数据结构组装

**ADR 关联：** ADR-009（6 步分析流程中的步骤 2）、ADR-011（未知时辰处理）

#### Epic 10: E-AI — AI 引擎（LLM 网关）

**目标：** 实现 LLM 抽象接入层，为 Zhiming AI 提供推理能力。

**包含：**
- LLM Provider 抽象接口（支持 OpenAI 协议兼容的 API）
- LLM 客户端（streaming 模式 + 非 streaming 模式）
- Token 计数器（tiktoken 封装）
- 上下文窗口管理器（控制注入量，不超过 70% 窗口上限）
- 错误处理 & 重试（指数退避）
- 对话历史组装（配合记忆引擎，参见 E-MEMORY）
- 流式响应中间处理（过滤、安全检查、结构化提取）

**ADR 关联：** ADR-014（云端 AI 增强）、ADR-016（单核心 AI Agent）

#### Epic 11: E-PROMPT — Prompt 引擎

**目标：** 实现模块化 Prompt 管理，防止 Prompt 耦合。

**包含：**
- Prompt 模板系统（Jinja2 或类似模板引擎）
- Prompt 模块化组织（按用途分文件）
  - `persona.j2` — 知命角色设定（ADR-004）
  - `bazi_analysis.j2` — 八字分析主 prompt
  - `dynamic_questions.j2` — AI 动态追问（ADR-009）
  - `compression.j2` — 记忆压缩 prompt（docs/19）
  - `welcome.j2` — 首次欢迎（ADR-010）
  - `chat.j2` — 日常交流 prompt
- Prompt 变量注入（用户档案、排盘结果、记忆摘要）
- Prompt 版本管理（Git-tracked 模板文件）

**ADR 关联：** ADR-004（知命角色）、ADR-009（6 步流程 prompt）、ADR-016（模块化 prevent monolith）

#### Epic 12: E-MEMORY — 记忆引擎

**目标：** 实现 docs/19 定义的三层记忆架构。

**包含：**
1. **Working Memory 管理器**
   - 最近 N 轮对话的循环缓冲区（默认 20 轮）
   - 当前任务状态跟踪
   - 用户短期意图识别
   - 窗口水位监控（70% 阈值）

2. **Summary Memory 管理器**
   - 会话摘要生成（会话结束时触发）
   - 主题摘要聚合（跨会话同主题）
   - 摘要持久化到本地数据库
   - 可回溯指针维护（原始 turn_id / session_id）

3. **Core Memory 管理器**
   - 用户档案注入（从 ProfileRepository 读取 Fact 层数据）
   - 已确认命理结论管理
   - 历史版本回溯

4. **Context Injection Orchestrator**
   - 按顺序组装上下文：系统提示 → 核心记忆 → 摘要记忆 → 工作记忆 → 当前消息
   - 裁剪超出窗口上限的内容（从工作记忆最旧轮次开始丢弃）

5. **压缩触发策略**
   - 滚动压缩（工作记忆 ≥ 70% 触发）
   - 会话级压缩（会话结束触发）
   - 去重逻辑（核心记忆优先覆盖摘要）

**ADR 关联：** ADR-012（数据三层映射）、ADR-016（Agent 内 prompt 模块化）、docs/19（完整设计依据）

#### Epic 13: E-KNOW — 知识库引擎

**目标：** 实现命理知识库查询和语义搜索。

**包含：**
- 知识术语 CRUD（60 甲子、十神、五行、神煞等）
- 语义搜索（基于嵌入向量的相似度搜索）
- 知识引用查询（分析报告中引用知识术语）
- 知识库版本跟踪

**ADR 关联：** —（无直接绑定约束，属于扩展功能）

#### Epic 14: E-REPORT — 报告引擎

**目标：** 实现八字分析报告生成和版本管理。

**包含：**
- Report 数据模型（多 section 结构）
- 报告异步生成（Long Task 模式）
- 报告 section 管理（title, content, confidence, data_tier）
- 报告版本历史（每次重新分析产生新版本）
- 可信度标注汇总（最后一个 section）
- 报告 CRUD 服务

**ADR 关联：** ADR-009（6 步流程最终输出报告）

#### Epic 15: E-GUI-SHELL — GUI 外壳（PySide6）

**目标：** 构建 Windows 桌面外壳，承载 Vue 前端和管理核心服务生命周期。

**包含：**
- PySide6 应用入口
- 主窗口（QMainWindow + QWebEngineView）
- 系统托盘（最小化到托盘、后台运行）
- Python Core Service 进程管理（启动/停止/健康检查）
- Qt WebChannel 桥接（Python ↔ JavaScript 宿主级调用）
- 更新检查（版本对比、下载提示）
- 窗口管理（大小/位置记住、多显示器支持）
- 通知（系统原生通知桥接）

**ADR 关联：** ADR-018（PySide6 为底座）、ADR-020（QWebEngineView 嵌入 + Qt WebChannel）

#### Epic 16: E-GUI-VUE — GUI 前端（Vue）

**目标：** 构建完整的用户界面，涵盖所有用户交互场景。

**包含页面/组件：**
1. **启动页/引导** — 首次使用引导（ADR-010 融合风）
2. **首页** — Zhiming 陪伴入口 + 档案进度（ADR-007）
3. **信息采集页** — AI 引导 + 快速填写混合（ADR-008）
4. **排盘展示页** — 四柱/五行/大运可视化展示
5. **AI 聊天界面** — WebSocket 实时代理对话，流式 token 显示
6. **分析报告页** — 多 section 报告展示，各 section data_tier 标注
7. **档案页** — 三层数据（fact/inference/pending）展示，用户反馈交互
8. **设置页** — 偏好配置、主题切换

**技术实现：**
- Vue 3 + Vite
- Vue Router
- Pinia（状态管理）
- Axios（HTTP 客户端）
- WebSocket 客户端封装（原生 WS + 重连逻辑）
- Qt WebChannel 客户端（js 桥接库）

**ADR 关联：** ADR-005（东方科技融合视觉风格）、ADR-006（数字东方书院）、ADR-007（首页双核心模块）、ADR-020（QWebEngineView 嵌入）

#### Epic 17: E-TEST — 测试套件

**目标：** 建立完整的测试覆盖体系。

**测试分类：**
1. **单元测试：**
   - BaZi 引擎（四柱/五行/大运/流年） — 需大量测试用例验证排盘正确性
   - Task 引擎（状态机转换）
   - Auth 模块（JWT 生成/验证）
   - Memory 引擎（压缩、注入、裁剪逻辑）
2. **集成测试：**
   - API 端点测试（pytest + httpx TestClient）
   - WebSocket 消息测试
   - 数据库 CRUD 测试（test database fixture）
   - AI 引擎 Mock 测试
3. **端到端测试：**
   - 完整 BaZi 分析流程（注册 → 填入出生信息 → 排盘 → 分析→ 查看报告）
   - 离线模式测试（核心服务无 AI 可用时的降级行为）
4. **性能测试：**
   - 记忆压缩性能（大上下文下的压缩耗时）
   - 排盘计算性能

**ADR 关联：** —（测试规范遵循 docs/10）

#### Epic 18: E-PKG — 打包 & 部署

**目标：** 构建可分发、可独立安装的 Windows 桌面应用安装包。

**包含：**
- Python Core Service 打包（PyInstaller 或 Nuitka）
- PySide6 桌面壳打包
- Vue 前端构建（Vite build → 静态文件嵌入 PyInstaller）
- NSIS 安装程序配置
- 自动更新机制（版本检查 + 增量下载）
- 开发环境一键设置脚本（setup_dev.bat）

**ADR 关联：** ADR-015（V1 Windows APP 优先）

---

## 6. Task Breakdown

每个 Epic 拆解为可独立开发的 Task。粒度标准：**一个 Claude Code Agent 单次会话可完成**（30 分钟 ~ 2 小时编码）。

### 6.1 E-BOOT: 项目启动 & 骨架搭建（7 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| BOOT-01 | 创建项目顶层目录结构（core/desktop/frontend/tests/docs/scripts） | S | — |
| BOOT-02 | 编写 `pyproject.toml` + `requirements.txt` + 依赖配置 | S | BOOT-01 |
| BOOT-03 | 设置 Python 代码风格工具（black, ruff, mypy）配置 | S | BOOT-02 |
| BOOT-04 | 创建 `core/main.py` 最小 FastAPI app（仅 health 端点） | S | BOOT-02 |
| BOOT-05 | 创建 `desktop/` + `frontend/` 骨架目录和占位 README | S | BOOT-01 |
| BOOT-06 | 创建 `scripts/setup_dev.bat` 开发环境初始化脚本 | S | BOOT-02 |
| BOOT-07 | 创建项目根 `README.md` + 更新 `docs/HANDOVER.md` Phase 3 交接信息 | S | BOOT-04 |

### 6.2 E-INFRA: 核心基础设施（8 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| INFRA-01 | 实现配置管理模块（pydantic-settings，支持 .env + 多环境配置） | M | BOOT-04 |
| INFRA-02 | 实现结构化日志系统（structlog → 控制台 + 文件双输出） | M | BOOT-04 |
| INFRA-03 | 实现全局异常处理框架（自定义 Exception 基类 → HTTP 错误码映射） | M | INFRA-01 |
| INFRA-04 | 实现请求/响应序列化中间件（统一 `{code, message, data, request_id}` 响应体） | S | INFRA-03 |
| INFRA-05 | 实现 CORS 中间件 + 请求 ID 生成中间件 | S | INFRA-04 |
| INFRA-06 | 实现 FastAPI 应用工厂（create_app，含 lifespan 事件管理） | M | INFRA-02, INFRA-03 |
| INFRA-07 | 实现核心工具函数库（日期处理、ID 生成器、类型工具） | S | BOOT-04 |
| INFRA-08 | 实现 RateLimiter 基础工具（支持 API/WSC 限流） | M | INFRA-01 |

### 6.3 E-DB: 数据库 & 迁移（7 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| DB-01 | 设计并实现 SQLite 数据库引擎和 Session 管理器（SQLAlchemy async） | M | INFRA-06 |
| DB-02 | 实现 User + UserProfile 模型（对应 ADR-012 三层数据） | M | DB-01 |
| DB-03 | 实现 BaziChart 模型（four_pillars/five_elements 等 JSON 字段） | M | DB-01 |
| DB-04 | 实现 Report + ReportSection 模型 | M | DB-01 |
| DB-05 | 实现 Task 模型（状态机相关字段） | S | DB-01 |
| DB-06 | 实现 Preference + ProfileVersion 模型 | S | DB-01 |
| DB-07 | 设置 Alembic 迁移系统 + 编写初始迁移脚本 | M | DB-01~06 |

### 6.4 E-REPO: 仓储层（7 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| REPO-01 | 实现 BaseRepository（CRUD + 分页 + 软删除基础类） | M | DB-01 |
| REPO-02 | 实现 UserRepository（按用户名查找、查重） | S | REPO-01, DB-02 |
| REPO-03 | 实现 BaziChartRepository（主排盘标记、用户所有排盘查询） | S | REPO-01, DB-03 |
| REPO-04 | 实现 ReportRepository（版本查询、按用户过滤） | S | REPO-01, DB-04 |
| REPO-05 | 实现 ProfileRepository（data_tier 过滤、层级流转） | M | REPO-01, DB-02 |
| REPO-06 | 实现 TaskRepository（状态过滤、过期任务清理） | S | REPO-01, DB-05 |
| REPO-07 | 实现 PreferenceRepository + ProfileVersionRepository | S | REPO-01, DB-06 |

### 6.5 E-AUTH: 认证 & 用户模块（7 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| AUTH-01 | 实现 JWT Token 服务（生成、验证、refresh） | M | INFRA-01 |
| AUTH-02 | 实现密码哈希服务（bcrypt） | S | AUTH-01 |
| AUTH-03 | 实现 UserService（注册、登录、用户 CRUD） | M | REPO-02, AUTH-01, AUTH-02 |
| AUTH-04 | 实现 Auth 中间件（FastAPI Dependency，Bearer token 提取验证） | S | AUTH-01 |
| AUTH-05 | 实现注册端点 `POST /auth/register` + 登录端点 `POST /auth/login` | S | AUTH-03, AUTH-04 |
| AUTH-06 | 实现用户资料端点（GET/PUT/PATCH /users/me, GET/PUT /users/me/profile） | M | AUTH-04, REPO-05 |
| AUTH-07 | 实现用户版本历史端点（GET /users/me/versions, GET /users/me/versions/{id}） | M | AUTH-04, REPO-07 |

### 6.6 E-TASK: 任务引擎（6 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| TASK-01 | 实现 Task 状态机定义 + TaskManager（状态转换、CRUD） | M | INFRA-06, REPO-06 |
| TASK-02 | 实现后台 worker 调度（asyncio.create_task 后台协程 runner） | M | TASK-01 |
| TASK-03 | 实现进度跟踪（progress 0-100 + stage 标识 + 阶段标签） | S | TASK-01 |
| TASK-04 | 实现超时处理（5 分钟超时自动标记 timed_out + 清理） | S | TASK-01 |
| TASK-05 | 实现重复任务去重（5 分钟内相同 chart_id+analysis_type 返回已有 task_id） | S | TASK-01 |
| TASK-06 | 实现 Task HTTP 端点（GET /tasks/{id}, POST /tasks/{id}/cancel） | S | TASK-01 |

### 6.7 E-API: HTTP API 路由层（12 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| API-01 | 建立 API 路由注册框架（module-level APIRouter，挂载到 app） | S | INFRA-06 |
| API-02 | 实现用户模块全部 9 个端点（register/login/logout/me/me/profile/versions） | M | AUTH-05, AUTH-06, AUTH-07 |
| API-03 | 实现 BaZi 排盘创建端点 `POST /bazi/charts` | M | E-BAZI 依赖，REPO-03 |
| API-04 | 实现 BaZi 排盘查询/更新/删除端点（GET/PUT/DELETE /bazi/charts） | M | REPO-03 |
| API-05 | 实现 BaZi 分析触发端点 `POST /bazi/charts/{id}/analysis`（202 Accepted） | M | TASK-01, E-BAZI, API-03 |
| API-06 | 实现 BaZi 分析查询端点 + 反馈端点 | M | API-05, REPO-05 |
| API-07 | 实现报告模块全部 6 个端点 | M | E-REPORT, TASK-01 |
| API-08 | 实现知识库模块全部 4 个端点 | S | E-KNOW |
| API-09 | 实现系统配置模块全部 5 个端点（health/models/preferences/system） | S | INFRA-06, REPO-07 |
| API-10 | 实现统一错误处理器（注册所有错误码映射到 HTTP 状态码） | M | INFRA-03 |
| API-11 | 实现请求验证中间件（Pydantic request body/model 校验错误友好提示） | S | INFRA-04 |
| API-12 | 实现分页/排序/过滤通用参数处理 | S | REPO-01 |

**注意：** API-03, API-05, API-07 依赖 Phase 3.2 的引擎实现。API-01、API-02、API-09、API-10~12 可在 Phase 3.1 完成。

### 6.8 E-WS: WebSocket 协议层（8 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| WS-01 | 实现 WebSocket ConnectionManager（连接映射/鉴权/生命周期管理） | M | INFRA-06, AUTH-04 |
| WS-02 | 实现 MessageRouter（按 type 字段分发到对应 handler） | M | WS-01 |
| WS-03 | 实现心跳机制（ping/pong 处理，30s 间隔，90s 超时断开） | S | WS-01 |
| WS-04 | 实现 subscribe/subscribe.confirmed + 通道管理 | S | WS-01, WS-02 |
| WS-05 | 实现 chat.message 处理 + 流式回复（ai.token/ai.done/ai.error） | M | WS-02, E-AI, E-MEMORY |
| WS-06 | 实现 task.* 推送（task.created/progress/completed/failed/cancelled） | M | WS-02, TASK-01 |
| WS-07 | 实现断线重连支持（task.resume/task.list + 消息序号重放） | M | WS-01, TASK-01 |
| WS-08 | 实现 WS 速率限制 + 消息校验 + 安全性（敏感信息保护、日志脱敏） | M | WS-01 |

### 6.9 E-BAZI: BaZi 排盘引擎（8 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| BAZI-01 | 实现天干地支基础库（十天干/十二地支/六十甲子/藏干/纳音/生肖） | M | — |
| BAZI-02 | 实现公历/农历转换工具 | M | BAZI-01 |
| BAZI-03 | 实现年柱计算 + 月柱计算（含节气校正） | M | BAZI-01 |
| BAZI-04 | 实现日柱计算 + 时柱计算（含未知时辰处理，ADR-011） | M | BAZI-01 |
| BAZI-05 | 实现真太阳时校准（调用云端 API 或本地近似计算） | M | BAZI-02, INFRA-01 |
| BAZI-06 | 实现五行分析（各元素统计、旺衰、平衡度评分） | M | BAZI-03, BAZI-04 |
| BAZI-07 | 实现十神计算 + 大运计算 + 流年计算 | M | BAZI-03, BAZI-04 |
| BAZI-08 | 实现 BaziService（组装完整排盘 Chart 结构 + 存储到 DB） | M | BAZI-05, BAZI-06, BAZI-07, REPO-03 |

### 6.10 E-AI: AI 引擎 — LLM 网关（7 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| AI-01 | 实现 LLM Provider 抽象接口（支持 OpenAI-compatible API） | M | INFRA-01 |
| AI-02 | 实现 LLM HTTP 客户端（流式 + 非流式，超时/重试/错误处理） | M | AI-01 |
| AI-03 | 实现 Token 计数器（tiktoken 封装，多模型支持） | S | AI-01 |
| AI-04 | 实现上下文窗口管理器（控制注入总量 ≤ 窗口上限 70%） | M | AI-03 |
| AI-05 | 实现对话历史组装器（配合记忆引擎获取上下文） | M | AI-04, E-MEMORY |
| AI-06 | 实现流式响应中间处理（过滤/安全检查/结构化提取） | M | AI-02 |
| AI-07 | 实现 AI Service（编排对话 + 分析 + 报告生成的完整流程） | M | AI-02, AI-05, E-PROMPT |

### 6.11 E-PROMPT: Prompt 引擎（6 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| PROMPT-01 | 建立 Prompt 模板系统（Jinja2 模板引擎 + 文件目录组织） | M | BOOT-04 |
| PROMPT-02 | 实现 Prompt 变量注入器（用户档案、排盘结果、记忆摘要注入） | M | PROMPT-01 |
| PROMPT-03 | 编写知命角色 prompt（persona.j2，对应 ADR-004 角色设定） | M | PROMPT-01, docs/05 |
| PROMPT-04 | 编写八字分析 prompt 组（bazi_analysis.j2 + dynamic_questions.j2 + report.j2） | M | PROMPT-01, ADR-009 |
| PROMPT-05 | 编写日常对话 prompt + 首次欢迎 prompt（welcome.j2, chat.j2） | M | PROMPT-01, ADR-004/010 |
| PROMPT-06 | 编写记忆压缩 prompt（compression.j2，对应 docs/19 压缩策略） | M | PROMPT-01, docs/19 |

### 6.12 E-MEMORY: 记忆引擎（8 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| MEM-01 | 实现 WorkingMemory 管理器（最近 N 轮循环缓冲区 + 水位监控 70%） | M | AI-03（Token 计数） |
| MEM-02 | 实现 SummaryMemory 管理器（摘要生成/存储/查询 + 可回溯指针） | M | DB-01, REPO-05, AI-01 |
| MEM-03 | 实现 CoreMemory 管理器（从 ProfileRepo 加载 Fact 层数据） | M | REPO-05 |
| MEM-04 | 实现 ContextInjectionOrchestrator（核心记忆→摘要记忆→工作记忆→当前消息） | M | MEM-01, MEM-02, MEM-03 |
| MEM-05 | 实现滚动压缩触发器（工作记忆 ≥ 70% → 调用 LLM 压缩最早 5 轮） | M | MEM-01, AI-01, PROMPT-06 |
| MEM-06 | 实现会话级压缩（会话结束时 → 全量摘要 + 关键事实提取） | M | MEM-02, AI-01, PROMPT-06 |
| MEM-07 | 实现去重逻辑（摘要与核心记忆重叠时以核心记忆为准） | S | MEM-02, MEM-03 |
| MEM-08 | 实现记忆引擎整体服务类（MemoryService，统一各层调用入口） | M | MEM-04, MEM-05, MEM-06 |

### 6.13 E-KNOW: 知识库引擎（5 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| KNOW-01 | 设计知识库数据模型 + 初始术语数据填充 | M | DB-01 |
| KNOW-02 | 实现术语 CRUD 服务 | S | REPO-01 |
| KNOW-03 | 实现语义搜索（嵌入模型调用 + 向量相似度计算） | M | AI-01（复用 LLM 做 embedding） |
| KNOW-04 | 实现知识引用服务（分析报告引用知识术语的关联查询） | S | KNOW-02 |
| KNOW-05 | 实现知识库 HTTP 端点（GET /terms, GET /terms/{id}, POST /search, GET /references） | S | KNOW-02, KNOW-03, KNOW-04 |

### 6.14 E-REPORT: 报告引擎（6 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| RPT-01 | 实现 ReportService（报告创建、生成、版本控制） | M | REPO-04, AI-07 |
| RPT-02 | 实现报告 section 管理（title/content/confidence/data_tier 组装） | M | RPT-01 |
| RPT-03 | 实现异步报告生成流程（Task 模式：POST → 202 → WS 推送进度） | M | RPT-01, E-TASK |
| RPT-04 | 实现报告版本历史（每次重新分析产生新版本） | M | RPT-01, REPO-04 |
| RPT-05 | 实现可信度标注汇总（最后一个 section，标注各部分的 data_tier） | M | RPT-02, ADR-012 |
| RPT-06 | 实现报告 HTTP 端点（POST/GET/DELETE /reports, GET /reports/{id}/versions） | S | RPT-01, RPT-04 |

### 6.15 E-GUI-SHELL: GUI 外壳 — PySide6（7 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| SHELL-01 | 实现 PySide6 应用入口 + 主窗口骨架（QMainWindow） | M | BOOT-05 |
| SHELL-02 | 实现 Core Service 进程管理器（启动 Python 子进程/健康检查/关闭） | M | SHELL-01 |
| SHELL-03 | 实现 QWebEngineView 嵌入（加载 Vue 前端本地文件） | M | SHELL-01 |
| SHELL-04 | 实现 Qt WebChannel 桥接（Python ↔ JavaScript 宿主通信） | M | SHELL-03 |
| SHELL-05 | 实现系统托盘（最小化到托盘、右键菜单、后台运行） | M | SHELL-01 |
| SHELL-06 | 实现 Windows 通知桥接（系统原生 notification） | S | SHELL-01 |
| SHELL-07 | 实现窗口管理（大小/位置持久化、多显示器适配）+ 更新检查 | M | SHELL-01 |

### 6.16 E-GUI-VUE: GUI 前端 — Vue（13 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| VUE-01 | 初始化 Vue 3 + Vite 项目 + 配置 ESLint/Prettier | S | BOOT-05 |
| VUE-02 | 建立 API Client 服务层（Axios 封装 + 统一错误处理 + 鉴权拦截器） | M | E-API, E-AUTH |
| VUE-03 | 建立 WebSocket Client 服务层（连接管理 + 心跳 + 重连 + 消息分发） | M | E-WS |
| VUE-04 | 建立 Qt WebChannel Client 桥接（js 端 host 通信） | M | SHELL-04 |
| VUE-05 | 实现首页（ZhiMing 陪伴入口 + 档案进度指示器，ADR-007） | M | VUE-01 |
| VUE-06 | 实现信息采集页（AI 引导对话 + 快速填写混合模式，ADR-008） | M | VUE-02 |
| VUE-07 | 实现排盘展示页（四柱/五行/大运/流年可视化） | M | VUE-02, E-BAZI |
| VUE-08 | 实现 AI 聊天界面（流式 token 显示、对话历史、情绪表达） | M | VUE-02, VUE-03 |
| VUE-09 | 实现分析报告页（多 section 展示、data_tier 标注、可信度汇总） | M | VUE-02 |
| VUE-10 | 实现用户档案页（三层数据展示、用户反馈确认/否认/补充） | M | VUE-02, ADR-012 |
| VUE-11 | 实现设置页 + 首次引导页（ADR-010 融合风） | M | VUE-01 |
| VUE-12 | 实现路由器 + 导航 + 页面过渡动画 | M | VUE-01 |
| VUE-13 | 实现主题系统（东方科技融合风，ADR-005/006）+ 全局状态管理（Pinia） | M | VUE-01 |

### 6.17 E-TEST: 测试套件（10 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| TEST-01 | 设置测试基础设施（pytest 配置、fixtures、test database、mock LLM） | M | INFRA-06, DB-01 |
| TEST-02 | BaZi 引擎单元测试（至少 10 组不同出生时间的排盘验证） | M | E-BAZI |
| TEST-03 | API 端点集成测试（覆盖全部 34 个端点，使用 httpx AsyncClient） | M | E-API |
| TEST-04 | WebSocket 集成测试（覆盖 17 种消息类型，重连场景） | M | E-WS |
| TEST-05 | 任务引擎单元测试（状态机全路径，超时/取消/去重场景） | M | E-TASK |
| TEST-06 | 记忆引擎单元测试（压缩触发、上下文注入、裁剪逻辑） | M | E-MEMORY |
| TEST-07 | Auth 模块集成测试（JWT 超时、refresh、非法 token 场景） | M | E-AUTH |
| TEST-08 | 端到端测试（注册 → 排盘 → 分析 → 报告全流程） | M | E-INTEGRATE |
| TEST-09 | 离线模式测试（无 AI 可用时降级行为验证） | M | E-API, E-BAZI |
| TEST-10 | 性能测试（排盘计算耗时、记忆压缩耗时、API 响应时间基准） | M | E-BAZI, E-MEMORY, E-API |

### 6.18 E-PKG: 打包 & 部署（6 Tasks）

| ID | Task | 工作量 | 前置 |
|----|------|--------|------|
| PKG-01 | Python Core Service PyInstaller 打包配置（单文件/目录 exe） | M | INFRA-06 |
| PKG-02 | Vue 前端生产构建 + 静态文件嵌入 PyInstaller | M | VUE-12, PKG-01 |
| PKG-03 | PySide6 桌面壳 PyInstaller 打包（含所有依赖） | M | SHELL-07, PKG-02 |
| PKG-04 | NSIS 安装程序脚本编写（安装目录、快捷方式、卸载程序） | M | PKG-03 |
| PKG-05 | 实现自动更新检查（版本文件 + 下载提示） | M | SHELL-07 |
| PKG-06 | 一键构建脚本 `scripts/build_all.bat`（从前端构建到安装包生成） | S | PKG-01~04 |

---

## 7. Development Order & Dependencies

### 7.1 严格串行链

以下链上的 Task**必须按顺序开发**，前置完成后才能开始后置：

```
链 1 (Foundation 主线):
  BOOT-01 → BOOT-02~04 → INFRA-01~06 → DB-01~07 → REPO-01~07
  → AUTH-01~07 → API-01~02 / API-09~12 (Phase 3.1 完成)

链 2 (Task 引擎):
  INFRA-06 → TASK-01~06 → WS-01~08 (Task 是 WS 的前置)

链 3 (BaZi 排盘):
  BAZI-01 → BAZI-02 → BAZI-03~04 → BAZI-05~08 (逐步构建)

链 4 (AI + 记忆):
  AI-01~04 → MEM-01~08 → AI-05~07 (记忆是 AI 完整对话的前置)
  PROMPT-01~06 (可与 AI 并行)

链 5 (报告):
  AI-07 + REPO-04 → RPT-01~06

链 6 (GUI 主线):
  SHELL-01 → SHELL-02~07 (逐步构建外壳)
  VUE-01 → VUE-02~04 → VUE-05~13 (逐步构建前端)

链 7 (测试 + 打包):
  全部 Epic → TEST-01~10 → PKG-01~06
```

### 7.2 允许并行的组

以下组内的 Epic/Task 可**并行开发**（需分配不同 Agent）：

```
并行组 A（Phase 3.1 早期）:
  ├─ A1: INFRA-06~08  (基础设施完善)
  ├─ A2: BAZI-01~02   (天干地支基础库 — 纯算法，无依赖)
  └─ A3: PROMPT-01~02 (Prompt 模板系统 — 纯内容，无依赖)

并行组 B（Phase 3.2）:
  ├─ B1: BAZI-03~08    (完整排盘引擎)
  ├─ B2: AI-01~04      (LLM 网关基础)
  ├─ B3: TASK-01~06    (任务引擎)
  └─ B4: KNOW-01~02    (知识库基础)

并行组 C（Phase 3.2 中期）:
  ├─ C1: AI-05~07 + PROMPT-03~06 (AI + Prompt 完善)
  ├─ C2: MEM-01~08                (记忆引擎)
  ├─ C3: WS-01~04                 (WS 连接/心跳/路由基础)
  └─ C4: KNOW-03~05               (知识库语义搜索)

并行组 D（Phase 3.3）:
  ├─ D1: SHELL-01~07 (PySide6 外壳)
  ├─ D2: VUE-01~04   (Vue 基础设施)
  └─ D3: API-03~08   (依赖引擎的端点 — 此时引擎已完成)

并行组 E（Phase 3.3 中期）:
  ├─ E1: VUE-05~13   (Vue 页面组件)
  └─ E2: INTEGRATE   (集成 — Qt WebChannel + HTTP/WS 联调)

并行组 F（Phase 3.3 后期）:
  ├─ F1: TEST-01~10  (测试全系列)
  └─ F2: PKG-01~06   (打包部署)
```

### 7.3 完整依赖关系图

```
BOOT ──→ INFRA ──→ DB ──→ REPO ──┬──→ AUTH ──┬──→ API-01/02/09-12
                                   │           │
                                   │           └──→ API-03~08 ──┐
                                   │                             │
BAZI (独立) ──→ BAZI-08 ──────────┤                             │
                                   │                             │
PROMPT (独立) ──→ AI ──→ MEM ──→ AI-07 ──→ RPT ───────────────┤
                                   │                             │
                             TASK ──┤                             │
                                   │        ┌────────────────────┘
                                   │        ▼
                                   └──→ WS ──→ VUE-03/(WS Client)
                                               │
                                    SHELL ──→ VUE-04/(WebChannel)
                                               │
                                    API + WS + VUE-02~04 → VUE-05~13
                                                                │
                                               SHELL + VUE → INTEGRATE
                                                                │
                                               ALL → TEST → PKG
```

### 7.4 建议开发顺序（按并行批次）

| 批次 | 包含 Task | 说明 | 建议 Agent 数 |
|------|-----------|------|:------------:|
| 1 | BOOT-01~07 | 项目初始化 | 1 |
| 2 | INFRA-01~08, BAZI-01~02, PROMPT-01~02 | 基础设施 + 纯算法 + 纯内容 | 3 |
| 3 | DB-01~07, BAZI-03~05 | 数据库 + 排盘核心 | 2 |
| 4 | REPO-01~07, BAZI-06~08, TASK-01~03 | 仓储层 + 排盘完成 + 任务基础 | 3 |
| 5 | AUTH-01~07, TASK-04~06, AI-01~04, PROMPT-03~04 | 认证 + 任务完善 + AI 基础 + Prompt 内容 | 4 |
| 6 | API-01~02, API-09~12, WS-01~04, KNOW-01~03, AI-05~06, PROMPT-05~06 | API 基础 + WS 基础 + 知识库 + AI 完善 | 5 |
| 7 | MEM-01~08, KNOW-04~05, WS-05~08, API-03~08 | 记忆引擎 + 知识库完成 + WS 完成 + API 完成 | 4 |
| 8 | RPT-01~06 | 报告引擎 | 1-2 |
| 9 | SHELL-01~07, VUE-01~04 | GUI 双轨开发 | 2-3 |
| 10 | VUE-05~13 | Vue 页面全部 | 2-3 |
| 11 | INTEGRATE | 端到端集成联调 | 1-2 |
| 12 | TEST-01~10 | 测试全系列 | 2-3 |
| 13 | PKG-01~06 | 打包发布 | 1-2 |

---

## 8. Risk Control

### 8.1 违反 Architecture Freeze 的行为（🚫 STOP）

以下行为**直接违反冻结基线**，必须在编码前停止并走 RFC 流程：

| # | 违规行为 | 涉及的冻结维度 | 后果 |
|---|---------|-------------|------|
| R1 | 新增/修改/删除 HTTP 端点路径、方法、请求/响应体字段 | docs/13 API Contract | 客户端无法兼容 |
| R2 | 修改 WebSocket 消息 `type` 名称、消息体 `data` 结构 | docs/14 WS Protocol | 客户端无法兼容 |
| R3 | 修改心跳间隔、重连策略、连接路径 `/ws/v1/session` | docs/14 WS Protocol | 协议不兼容 |
| R4 | 修改数据三层体系定义（Fact/Inference/Pending）或流转规则 | ADR-012 | 违反已批决策 |
| R5 | 修改三层记忆架构（Working/Summary/Core）的基本结构 | docs/19 Memory Architecture | 违反已批设计 |
| R6 | 修改系统四层划分（Presentation/Business/Data/Cloud） | docs/08 Architecture | 架构不一致 |
| R7 | 在不走 RFC 流程的前提下绕过任何 Approved ADR 决策 | ADR-001~012, ADR-020 | 治理失效 |
| R8 | 将 Draft ADR 内容作为约束性设计依据强制执行 | ADR-014~019 | 设计方向未锁定 |

### 8.2 需要新增 ADR 的场景

以下变更**必须先创建新 ADR**（或 Draft ADR → Approved），**编码后再实施**：

| # | 场景 | 示例 |
|---|------|------|
| A1 | 引入未在架构文档中定义的新技术/新服务 | 使用 Redis 做缓存（当前架构无此设计） |
| A2 | 新增核心模块（超出 docs/08 定义的模块范围） | 增加"社交分享"模块 |
| A3 | 修改已批准的 ADR 决策内容 | 改变 Freemium 模式（ADR-003） |
| A4 | 改变数据存储方案（超出 SQLite 本地优先） | 增加 PostgreSQL 同步 |
| A5 | 改变 AI Agent 架构（超出单 Agent 范围） | 引入多 Agent 协作 |

### 8.3 需要 Product Owner Approval 的场景

以下变更**必须先获得 Product Owner 审批**：

| # | 场景 |
|---|------|
| P1 | 任何 P0/P1 风险的缓解方案涉及架构变更 |
| P2 | 范围增减影响 MVP 交付（Feature Creep / Scope Cut） |
| P3 | 任何对冻结基线（docs/21 §4）的变更请求 |
| P4 | 任何费用相关的决策（LLM API 超过预算、新增付费服务） |
| P5 | 任何影响用户隐私和数据安全的设计决策 |

### 8.4 已知风险列表

Phase 3 开发期间需要持续关注的已知风险：

| ID | 风险描述 | 等级 | 缓解措施 |
|----|---------|:----:|---------|
| ARC-15-P1-001 | 技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成） | P1 | 开发初期优先逐条确认；不确定项选最兼容方向 |
| ARC-15-P1-002 | HANDOVER.md 中的 ADR-014~019 参考条目未补齐 | P1 | 开发初始化阶段同步补齐 |
| ARC-15-P1-003 | 离线策略颗粒度未定义（docs/08 在线/有限/离线分级确认未完成） | P1 | 按最严格离线模式设计，在线可升级 |
| ARC-15-P1-004 | 认证模型与桌面场景的匹配未验证（JWT 在本地 core service 场景下的必要性） | P1 | 本地 token 简化验证逻辑，预留远程兼容 |
| ARC-15-P1-005 | 核心服务部署与打包方案未确认 | P1 | 按 PyInstaller 单文件方案实施 |
| ARC-15-P1-006 | 数据版本历史存储方案未设计 | P1 | 按 ProfileVersion 快照表实施，暂不引入 diff |
| ARC-15-P1-007 | 分层记忆在 Phase 3 中的压缩优先级未确认（online vs offline） | P1 | 默认在线压缩（LLM 调用），离线备选简单摘要 |
| ARC-15-P1-008~017 | 其余 P1 风险 | P1 | 在编码过程中逐步跟踪关闭 |
| ARC-15-P2-001~009 | 9 项 P2 风险 | P2 | 可在 MVP 后处理 |

### 8.5 风险升级流程

```
开发中发现问题
    │
    ├── 是否违反冻结基线？ ──Yes──→ 🚫 停止编码
    │                                   │
    │                                   └──→ 创建 RFC → 创建 Draft ADR
    │                                       → Architecture Review
    │                                       → Product Owner Approval
    │                                       → 实施修改
    │
    ├── 需要新 ADR？ ──Yes──→ 创建 Draft ADR → Review → 批准后实施
    │
    ├── 需要 PO 审批？ ──Yes──→ 提交审批请求 → 批准后实施
    │
    └── 需要在 docs/18 中记录？ ──Yes──→ 创建新风险条目 → 持续跟踪
```

---

## 9. Definition of Done

### 9.1 Task 完成标准

每一个 Task **必须同时满足以下所有条件**才能标记为完成：

| # | 标准 | 验证方式 | 适用范围 |
|---|------|---------|---------|
| DOD-1 | **代码编译/解释无错误** | `python -m pytest` 或 `npm run build` 通过 | 所有编码 Task |
| DOD-2 | **单元测试通过** | 该模块 `pytest tests/unit/<module>` 全部通过 | 所有编码 Task |
| DOD-3 | **覆盖率 ≥ 80%**（核心模块） | `pytest --cov=<module>` 报告 ≥ 80% | 引擎类 Task（BAZI/AI/MEM/TASK/AUTH） |
| DOD-4 | **API 契约合规** | 端点请求/响应与 docs/13 定义的字段、类型、错误码一致 | API/WS Task |
| DOD-5 | **未违反 Architecture Freeze** | 代码审计 check：无 docs/21 禁止的修改 | 所有 Task |
| DOD-6 | **未违反 ADR 约束** | 相关 ADR 引用核对清单 | 所有 Task |
| DOD-7 | **代码规范符合项目标准** | ruff linting 通过（`ruff check .`） | 所有 Python Task |
| DOD-8 | **AI 协作日志已更新** | `docs/11_AI协作日志.md` 追加本条 Task 记录 | 所有 Task |
| DOD-9 | **提交前 Code Review**（非 Bootstrap Task） | PR 或面对面 Review 记录 | Phase 3.2~3.3 Task |
| DOD-10 | **git 提交信息完整** | 使用约定式提交（`feat/fix/chore/docs/test`） | 所有 Task |

### 9.2 Epic 完成标准

| # | 标准 | 说明 |
|---|------|------|
| EPC-1 | 所有 Task 满足 DOD-1~10 | 无未完成任务 |
| EPC-2 | Epic 内模块间集成测试通过 | 模块 A 调用模块 B 的接口正确 |
| EPC-3 | Epic README 或注释更新 | 说明模块结构、核心设计决策、ADR 引用 |
| EPC-4 | 相关风险条目已更新 | docs/18 中相关风险状态刷新 |
| EPC-5 | 无违反冻结基线的代码 | 最终审计检查 |

### 9.3 里程碑完成标准

| 里程碑 | 额外完成条件 |
|--------|------------|
| M1: Foundation Ready | FastAPI 启动 + health 端点 + DB 迁移 + Auth 流程 + Task 引擎 |
| M2: API Complete | 34 端点全绿测试 + 17 WS 消息类型实现 + 契约对齐 |
| M3: Core Logic Complete | 6 个引擎全部可运行 + 集成测试覆盖分析全流程 |
| M4: GUI Functional | 桌面应用启动 + 5 核心页面渲染 + E2E 流程可用 |
| M5: MVP Release | NSIS 安装包 + 测试覆盖率 ≥ 80% + 10+ 风险跟踪更新 |

### 9.4 关闭条件

当满足以下所有条件时，Phase 3 可标记为 **Completed**：

1. ✅ M5: MVP Release 已完成
2. ✅ 测试覆盖率（核心模块）≥ 80%
3. ✅ 风险跟踪表中至少 10 项 P1/P2 已关闭或显著进展
4. ✅ HANDOVER.md 已更新（含 Phase 3 交接信息）
5. ✅ docs/11_AI协作日志.md 记录了全部 Phase 3 执行记录
6. ✅ 无违反冻结基线的未处理问题
7. ✅ 产品负责人确认 MVP 可交付

---

> **本文档为 Phase 3 开发执行计划的权威版本。**
> **任何偏离必须在 docs/11 中记录并经 Project Architect 确认。**
> **冻结基线修改必须走 RFC → ADR → Review → Approval 流程。**
