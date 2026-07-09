# API 接口契约设计

- **版本：** v0.1
- **状态：** Draft
- **创建日期：** 2026-07-08
- **关联 ADR：** ADR-009（八字分析 6 步流程）、ADR-012（数据三层体系）、ADR-013（用户资料版本历史）、ADR-014（本地优先 + 云端扩展）、ADR-017（客户端解耦）、ADR-019（HTTP + WebSocket 双通道通信）

---

## 目录

1. [API 设计原则](#1-api-设计原则)
2. [系统分层架构](#2-系统分层架构)
3. [Endpoint 列表](#3-endpoint-列表)
   - 3.1 [通用约定](#31-通用约定)
   - 3.2 [用户模块 User](#32-用户模块-user)
   - 3.3 [八字排盘模块 Bazi](#33-八字排盘模块-bazi)
   - 3.4 [AI 分析报告模块 Report](#34-ai-分析报告模块-report)
   - 3.5 [长任务模块 Task](#35-长任务模块-task)
   - 3.6 [知识库模块 Knowledge](#36-知识库模块-knowledge)
   - 3.7 [系统配置模块 Config](#37-系统配置模块-config)
   - 3.8 [WebSocket 通道](#38-websocket-通道)
4. [Request / Response 规范](#4-request--response-规范)
   - 4.1 [标准响应体](#41-标准响应体)
   - 4.2 [错误响应体](#42-错误响应体)
   - 4.3 [分页格式](#43-分页格式)
   - 4.4 [异步任务模式](#44-异步任务模式)
   - 4.5 [鉴权方式](#45-鉴权方式)
5. [错误码规范](#5-错误码规范)
   - 5.1 [错误码范围](#51-错误码范围)
   - 5.2 [具体错误码定义](#52-具体错误码定义)
6. [版本策略](#6-版本策略)
   - 6.1 [URL 路径版本化](#61-url-路径版本化)
   - 6.2 [版本兼容性规则](#62-版本兼容性规则)
   - 6.3 [弃用策略](#63-弃用策略)
   - 6.4 [客户端兼容性](#64-客户端兼容性)
7. [示例 JSON](#7-示例-json)
   - 7.1 [用户注册与登录](#71-用户注册与登录)
   - 7.2 [八字排盘创建与 AI 分析触发](#72-八字排盘创建与-ai-分析触发)
   - 7.3 [报告生成与查询](#73-报告生成与查询)
   - 7.4 [错误响应示例](#74-错误响应示例)
8. [【待确认】项清单](#8-待确认项清单)

---

## 1. API 设计原则

### 1.1 RESTful 资源导向

HTTP API 遵循 REST 风格。资源通过 URL 路径标识，HTTP 方法表示操作语义：

| 方法 | 语义 | 幂等 |
|------|------|------|
| `GET` | 查询资源 | ✅ 是 |
| `POST` | 创建资源 / 提交操作 | ❌ 否 |
| `PUT` | 全量替换资源 | ✅ 是 |
| `PATCH` | 部分更新资源 | ✅ 是 |
| `DELETE` | 删除资源 | ✅ 是 |

### 1.2 双通道各司其职

遵循 ADR-019，HTTP 与 WebSocket 各司其职：

| 通道 | 职责 | 适用场景 |
|------|------|----------|
| **HTTP** | 请求/响应模式的同步与异步业务操作 | 用户 CRUD、排盘、报告查询、配置管理 |
| **WebSocket** | 实时双向通信 | AI 对话（Token 流式输出）、长任务进度推送、系统通知 |

HTTP 不承载实时流式通信，WebSocket 不承载 REST 风格 CRUD 操作。

### 1.3 统一序列化

- 所有请求与响应使用 `Content-Type: application/json`（文件上传等场景除外）
- 字段命名使用 `snake_case`，与 Python / FastAPI 约定一致
- 时间字段统一为 ISO 8601 格式（UTC），示例：`"2026-07-08T12:00:00Z"`
- ID 字段统一为字符串前缀 + 随机后缀，示例：`"u_a1b2c3d4"`

### 1.4 API 版本化

- URL 路径前缀携带版本号：`/api/v1/`
- 向后兼容的变更（新增可选字段、新增端点、新增枚举值）不触发版本升级
- 破坏性变更（类型变更、字段删除、端点重命名）需升级至 `/api/v2/`

详见第 [6 章](#6-版本策略)。

### 1.5 异步长任务模式

AI 分析、报告生成等耗时操作采用异步任务模式：

```
客户端                         服务端
  │                              │
  │ POST /api/v1/reports         │
  │ ───────────────────────────→ │ 202 Accepted + task_id
  │ ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
  │                              │
  │ GET /api/v1/tasks/{task_id}  │ 轮询
  │ ───────────────────────────→ │ status: "processing", progress: 45
  │ ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │
  │                              │
  │ WebSocket /ws/v1/session     │ 实时推送（替代轮询）
  │ ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ │ task.completed
  │                              │
```

客户端可二选一：HTTP 轮询或 WebSocket 订阅。

### 1.6 分页标准化

所有列表接口支持统一的分页参数与响应格式（详见 [4.3 分页格式](#43-分页格式)）。

### 1.7 无状态鉴权

API 无状态，每次请求通过 `Authorization: Bearer <token>` 携带身份凭证。服务端不维护会话状态，Token 采用 JWT 格式。

### 1.8 最小数据传输

遵循 ADR-014「数据上传最小化规则」：

- 仅传输当前操作所必需的字段
- 不上传完整人生档案作为 API 调用上下文
- 客户端本地缓存档案数据，上传时仅发送变更内容或当前分析所需的最小上下文

### 1.9 未来兼容

通信协议面向未来 Web 扩展设计（ADR-019 8.9.4）：

- V1 在 `localhost` 上通过 HTTP + WebSocket 与本地核心服务通信
- 相同接口天然兼容远程 Web API 调用（仅需更改 Base URL 和网络策略）
- 客户端适配层抽象网络拓扑，切换本地/远程无需修改业务代码

### 1.10 统一错误处理

所有错误响应使用统一的错误码体系（详见第 [5 章](#5-错误码规范)）。客户端根据 `code` 字段做程序化处理，不应依赖 `message` 字符串匹配。

---

## 2. 系统分层架构

```
┌────────────────────────────────────────────────────────────────────┐
│ Layer 1: 客户端表示层 (Client / Presentation)                      │
│  ┌──────────────────────┐  ┌─────────────────────────────────┐     │
│  │  PySide6 原生窗口     │  │  Vue 渐进式 UI 模块              │     │
│  │  · 窗口管理 / 系统集成│  │  · AI 对话界面 / 报告可视化     │     │
│  │  · 托盘 / 通知       │  │  · 命盘图表 / 数据展示           │     │
│  └────────┬─────────────┘  └───────────┬─────────────────────┘     │
│           │                            │                            │
│  ┌────────┴────────────────────────────┴────────────────────────┐   │
│  │ Layer 2: API 客户端适配层 (API Client)                       │   │
│  │  · HTTP Client：请求/响应序列化、重试、超时管理               │   │
│  │  · WebSocket Client：连接管理、心跳保活、自动重连             │   │
│  │  · 离线请求缓存 / 连接状态监控                                │   │
│  │  · 统一错误映射与重试策略                                     │   │
│  └────────────────────────┬─────────────────────────────────────┘   │
└───────────────────────────┼─────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │  localhost:Port        │
                │  HTTP + WebSocket      │
                │  本地 IPC 通信          │
                └───────────┬───────────┘
                            │
┌───────────────────────────┼─────────────────────────────────────────┐
│ Layer 3: FastAPI 路由层 (Router)                                   │
│                                                                     │
│  ┌──────────────────────────────┐  ┌──────────────────────────┐     │
│  │  HTTP Router (/api/v1/)      │  │  WebSocket Router (/ws/) │     │
│  │  · 请求路由与分发            │  │  · 连接生命周期管理      │     │
│  │  · 参数解析与校验            │  │  · 消息帧解析与分发      │     │
│  │  · 响应格式化                │  │  · 心跳检测 / 断线清理   │     │
│  │  · 全局错误拦截              │  │  · 房间 / 通道管理       │     │
│  └──────────┬───────────────────┘  └────────┬──────────────────┘     │
│             │                                │                        │
│  ┌──────────┴────────────────────────────────┴──────────────────┐   │
│  │ Layer 4: 业务服务层 (Service)                                │   │
│  │                                                              │   │
│  │  · UserService：用户注册/登录/资料管理                        │   │
│  │  · BaziService：排盘创建/查询/管理                           │   │
│  │  · ReportService：报告生成编排/查询                           │   │
│  │  · KnowledgeService：知识库检索/术语查询                      │   │
│  │  · ConfigService：系统配置/模型管理                           │   │
│  │  · ChatService：AI 对话编排/会话管理                          │   │
│  │  · TaskService：长任务状态追踪与生命周期管理                   │   │
│  │                                                              │   │
│  │  (负责：业务逻辑编排、跨领域协调、事务管理)                    │   │
│  └──────────────────────────┬───────────────────────────────────┘   │
│                             │                                        │
│  ┌──────────────────────────┴────────────────────────────────────┐  │
│  │ Layer 5: 领域层 (Domain)                                     │  │
│  │                                                              │  │
│  │  领域模型：User / BaziChart / Report / Profile / Task / Term  │  │
│  │                                                              │  │
│  │  领域服务：                                                  │  │
│  │  · 排盘计算：根据出生信息计算四柱/五行/十神/大运              │  │
│  │  · 命理推理：格局判定、旺衰分析、用神忌神判断                 │  │
│  │  · 数据层级流转：Fact → Inference → Pending 的标记与流转     │  │
│  │                                                              │  │
│  │  (负责：核心业务规则、数据模型、状态机)                       │  │
│  └──────────┬───────────────────────┬───────────────────────────┘  │
│             │                       │                               │
│  ┌──────────┴──────────┐  ┌────────┴──────────────────┐            │
│  │ Layer 6a:           │  │ Layer 6b:                 │            │
│  │ 数据访问层          │  │ 基础设施层                 │            │
│  │ (Repository)         │  │ (Infrastructure)          │            │
│  │                      │  │                           │            │
│  │  · UserRepo          │  │  · AI Agent (知命)        │            │
│  │  · BaziChartRepo    │  │  · LLM Provider Gateway   │            │
│  │  · ReportRepo        │  │  · 排盘引擎               │            │
│  │  · ProfileRepo       │  │  · 规则推理引擎           │            │
│  │  · TaskRepo          │  │  · 知识库 (KG + 向量)     │            │
│  │  · PreferenceRepo   │  │  · 本地持久化 (SQLite)     │            │
│  └──────────────────────┘  └──────────────────────────┘            │
└────────────────────────────────────────────────────────────────────┘
```

### 各层职责简述

| 层级 | 职责范围 | 依赖方向 |
|------|----------|----------|
| **Layer 1: 表示层** | UI 渲染、用户交互、离线缓存、系统集成 | → 向下调用 Layer 2 |
| **Layer 2: API 客户端** | 序列化/反序列化、重试/超时/断线重连、状态监控 | → 向下通过 HTTP/WS 调用 Layer 3 |
| **Layer 3: 路由层** | 请求路由、参数校验、全局异常捕获、响应格式化 | → 向下调用 Layer 4 |
| **Layer 4: 服务层** | 业务编排、跨领域协调、事务边界 | → 向下调用 Layer 5+6 |
| **Layer 5: 领域层** | 核心业务规则、领域模型、数据状态机 | → 向下调用 Layer 6 |
| **Layer 6a: 数据访问** | 数据持久化与查询（Repository 模式） | → 本地数据库 |
| **Layer 6b: 基础设施** | AI 推理、排盘计算、知识库检索 | → 外部 LLM API + 本地引擎 |

### 分层调用规则

- **上层只能调用直接下层**：Service 层不能跳过 Domain 层直接调用 Repository
- **同层水平调用**：一个 Service 调用另一个 Service 是允许的（如 ReportService → BaziService）
- **依赖注入**：所有依赖通过构造函数注入，避免循环依赖

---

## 3. Endpoint 列表

### 3.1 通用约定

| 项目 | 约定 |
|------|------|
| Base URL | `http://localhost:{port}/api/v1` |
| 内容类型 | `application/json` |
| 时间格式 | ISO 8601 UTC：`"2026-07-08T12:00:00Z"` |
| ID 格式 | 前缀 + 随机字符串：`u_xxx`、`chart_xxx`、`rpt_xxx`、`task_xxx` |
| 鉴权 | 除标注「无鉴权」外，所有端点需 `Authorization: Bearer <token>` |
| WebSocket Base | `ws://localhost:{port}/ws/v1/session` |

### 3.2 用户模块 User

| 方法 | 路径 | 描述 | 异步 | 鉴权 |
|------|------|------|------|------|
| `POST` | `/api/v1/users/register` | 用户注册 | ❌ | 无鉴权 |
| `POST` | `/api/v1/users/login` | 用户登录，返回 Token | ❌ | 无鉴权 |
| `POST` | `/api/v1/users/logout` | 登出（Token 失效） | ❌ | ✅ |
| `GET` | `/api/v1/users/me` | 获取当前用户基本信息 | ❌ | ✅ |
| `PUT` | `/api/v1/users/me` | 更新当前用户基本信息 | ❌ | ✅ |
| `PATCH` | `/api/v1/users/me/profile` | 部分更新人生档案字段 | ❌ | ✅ |
| `GET` | `/api/v1/users/me/profile` | 获取完整人生档案（含三层标记） | ❌ | ✅ |
| `GET` | `/api/v1/users/me/versions` | 获取档案版本历史列表 | ❌ | ✅ |
| `GET` | `/api/v1/users/me/versions/{version_id}` | 获取某版本档案快照 | ❌ | ✅ |

#### POST /api/v1/users/register

```json
// Request
{
  "username": "string, required, 2-32 chars",
  "password": "string, required, 8-64 chars",
  "birth_year": "int, required, 1900-当前年",
  "birth_month": "int, required, 1-12",
  "birth_day": "int, required, 1-31",
  "birth_hour": "int|null, optional, 0-23",
  "birth_minute": "int|null, optional, 0-59",
  "gender": "string, required, 'male'|'female'",
  "birth_place": "string, optional, 最长 128 字",
  "calendar_type": "string, optional, 默认 'solar', 'solar'|'lunar'"
}

// Response 201 Created
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": "u_a1b2c3d4",
    "username": "test_user",
    "created_at": "2026-07-08T12:00:00Z"
  }
}
```

#### POST /api/v1/users/login

```json
// Request
{
  "username": "string, required",
  "password": "string, required"
}

// Response 200 OK
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_id": "u_a1b2c3d4"
  }
}
```

#### GET /api/v1/users/me

```json
// Response 200 OK
{
  "code": 0,
  "data": {
    "user_id": "u_a1b2c3d4",
    "username": "test_user",
    "gender": "male",
    "birth_place": "北京",
    "calendar_type": "solar",
    "is_premium": false,
    "created_at": "2026-07-08T12:00:00Z"
  }
}
```

#### GET /api/v1/users/me/profile

```json
// Response 200 OK
{
  "code": 0,
  "data": {
    "user_id": "u_a1b2c3d4",
    "basic_info": {
      "birth_year": 1990,
      "birth_month": 8,
      "birth_day": 15,
      "birth_hour": 12,
      "birth_minute": 0,
      "gender": "male",
      "birth_place": "北京"
    },
    "personality": {
      "traits": ["沉稳", "独立", "善谋"],
      "data_tier": "inference"
    },
    "life_events": [
      {
        "event_id": "evt_001",
        "type": "career",
        "description": "2015年转行进入互联网行业",
        "year": 2015,
        "data_tier": "fact"
      },
      {
        "event_id": "evt_002",
        "type": "education",
        "description": "可能毕业于理工科专业",
        "year": 2012,
        "data_tier": "pending"
      }
    ],
    "created_at": "2026-07-08T12:00:00Z",
    "updated_at": "2026-07-08T14:00:00Z"
  }
}
```

#### PATCH /api/v1/users/me/profile

```json
// Request（仅发送需要更新的字段）
{
  "life_events": [
    {
      "type": "career",
      "description": "2015年加入字节跳动",
      "year": 2015,
      "data_tier": "fact"
    }
  ]
}

// Response 200 OK
{
  "code": 0,
  "message": "档案更新成功",
  "data": {
    "user_id": "u_a1b2c3d4",
    "updated_at": "2026-07-08T15:00:00Z"
  }
}
```

#### GET /api/v1/users/me/versions

```json
// Response 200 OK
{
  "code": 0,
  "data": [
    {
      "version_id": "ver_001",
      "created_at": "2026-07-08T12:00:00Z",
      "change_summary": "初始档案创建"
    },
    {
      "version_id": "ver_002",
      "created_at": "2026-07-08T15:00:00Z",
      "change_summary": "新增人生事件：职业经历"
    }
  ],
  "pagination": {
    "page": 1, "page_size": 20, "total": 2,
    "total_pages": 1, "has_next": false, "has_prev": false
  }
}
```

### 3.3 八字排盘模块 Bazi

| 方法 | 路径 | 描述 | 异步 | 鉴权 |
|------|------|------|------|------|
| `POST` | `/api/v1/bazi/charts` | 创建排盘（同步计算） | ❌ | ✅ |
| `GET` | `/api/v1/bazi/charts` | 获取用户所有排盘列表 | ❌ | ✅ |
| `GET` | `/api/v1/bazi/charts/{chart_id}` | 获取单个排盘完整盘面 | ❌ | ✅ |
| `PUT` | `/api/v1/bazi/charts/{chart_id}` | 更新排盘输入（重新计算） | ❌ | ✅ |
| `DELETE` | `/api/v1/bazi/charts/{chart_id}` | 删除排盘记录 | ❌ | ✅ |
| `POST` | `/api/v1/bazi/charts/{chart_id}/analysis` | 触发 AI 分析（6 步流程入口） | ✅ | ✅ |
| `GET` | `/api/v1/bazi/charts/{chart_id}/analysis/{analysis_id}` | 获取某次分析结果 | ❌ | ✅ |
| `POST` | `/api/v1/bazi/charts/{chart_id}/analysis/{analysis_id}/feedback` | 提交用户反馈（数据层级流转） | ❌ | ✅ |

#### POST /api/v1/bazi/charts

```json
// Request
{
  "birth_year": 1990,
  "birth_month": 8,
  "birth_day": 15,
  "birth_hour": 12,
  "birth_minute": 0,
  "gender": "male",
  "birth_place": "北京",
  "timezone": "Asia/Shanghai",
  "calendar_type": "solar",
  "name": "我的八字",
  "is_primary": true
}

// Response 201 Created
{
  "code": 0,
  "message": "排盘成功",
  "data": {
    "chart_id": "chart_x1y2z3w4",
    "name": "我的八字",
    "is_primary": true,
    "input": {
      "birth_year": 1990,
      "birth_month": 8,
      "birth_day": 15,
      "birth_hour": 12,
      "birth_minute": 0,
      "gender": "male",
      "birth_place": "北京",
      "timezone": "Asia/Shanghai",
      "calendar_type": "solar"
    },
    "pillars": {
      "year": { "heavenly_stem": "庚", "earthly_branch": "午", "hidden_stems": ["丁", "己"] },
      "month": { "heavenly_stem": "甲", "earthly_branch": "申", "hidden_stems": ["庚", "壬", "戊"] },
      "day": { "heavenly_stem": "戊", "earthly_branch": "寅", "hidden_stems": ["甲", "丙", "戊"] },
      "hour": { "heavenly_stem": "戊", "earthly_branch": "午", "hidden_stems": ["丁", "己"] }
    },
    "five_elements": {
      "wood": { "count": 2, "status": "旺", "score": 25 },
      "fire": { "count": 3, "status": "旺", "score": 30 },
      "earth": { "count": 4, "status": "最旺", "score": 40 },
      "metal": { "count": 2, "status": "中和", "score": 20 },
      "water": { "count": 0, "status": "弱", "score": 5 }
    },
    "day_master": { "stem": "戊", "strength": "偏旺" },
    "ten_gods": [
      { "pillar": "year", "heavenly_stem": "庚", "ten_god": "食神" },
      { "pillar": "month", "heavenly_stem": "甲", "ten_god": "七杀" },
      { "pillar": "day", "heavenly_stem": "戊", "ten_god": "日主" },
      { "pillar": "hour", "heavenly_stem": "戊", "ten_god": "比肩" }
    ],
    "great_fortune": [
      { "age_range": "0-9", "heavenly_stem": "乙", "earthly_branch": "酉" },
      { "age_range": "10-19", "heavenly_stem": "丙", "earthly_branch": "戌" },
      { "age_range": "20-29", "heavenly_stem": "丁", "earthly_branch": "亥" }
    ],
    "current_year": {
      "year": 2026,
      "heavenly_stem": "丙",
      "earthly_branch": "午"
    },
    "created_at": "2026-07-08T12:01:00Z"
  }
}
```

#### POST /api/v1/bazi/charts/{chart_id}/analysis

触发 AI 分析（对应 ADR-009 的步骤 3-6：AI 初步分析 → AI 动态追问 → 用户反馈验证 → 最终报告）。

```json
// Request
{
  "analysis_type": "full",  // "full" | "quick" | "year_fortune"
  "context": {
    "conversation_id": "conv_xxx",
    "include_dynamic_questions": true
  }
}

// Response 202 Accepted
{
  "code": 0,
  "message": "分析任务已提交",
  "data": {
    "task_id": "task_20260708_xyz789",
    "analysis_id": "a_abc123",
    "status": "pending",
    "estimated_seconds": 45
  }
}
```

#### POST /api/v1/bazi/charts/{chart_id}/analysis/{analysis_id}/feedback

提交用户反馈，触发数据层级流转（ADR-012）。

```json
// Request
{
  "section_id": "s2",
  "feedback_type": "confirm",   // "confirm" | "deny" | "supplement" | "skip"
  "content": "我确实在2015年转行，但原因并非文中所述",
  "supplement": {
    "new_description": "因个人兴趣主动转型",
    "year": 2015,
    "data_tier": "fact"
  }
}

// Response 200 OK
{
  "code": 0,
  "message": "反馈已记录",
  "data": {
    "feedback_id": "fb_xyz789",
    "previous_tier": "inference",
    "new_tier": "fact",
    "will_reanalyze": true
  }
}
```

### 3.4 AI 分析报告模块 Report

| 方法 | 路径 | 描述 | 异步 | 鉴权 |
|------|------|------|------|------|
| `POST` | `/api/v1/reports` | 生成新报告 | ✅ | ✅ |
| `GET` | `/api/v1/reports` | 获取报告列表 | ❌ | ✅ |
| `GET` | `/api/v1/reports/{report_id}` | 获取报告完整内容 | ❌ | ✅ |
| `DELETE` | `/api/v1/reports/{report_id}` | 删除报告 | ❌ | ✅ |
| `GET` | `/api/v1/reports/{report_id}/versions` | 获取报告版本历史 | ❌ | ✅ |
| `GET` | `/api/v1/reports/{report_id}/versions/{version_id}` | 获取某版本报告详情 | ❌ | ✅ |

#### POST /api/v1/reports

```json
// Request
{
  "chart_id": "chart_x1y2z3w4",
  "analysis_id": "a_abc123",
  "report_type": "full_analysis",
  "title": "1990年庚午年命主综合报告",
  "locale": "zh-CN"
}

// Response 202 Accepted
{
  "code": 0,
  "message": "报告生成任务已提交",
  "data": {
    "report_id": null,
    "task_id": "task_20260708_abc456",
    "status": "pending",
    "estimated_seconds": 60
  }
}
```

#### GET /api/v1/reports

```json
// Query: ?page=1&page_size=20&sort_by=created_at&sort_order=desc&report_type=full_analysis

// Response 200 OK
{
  "code": 0,
  "data": [
    {
      "report_id": "rpt_mno789",
      "title": "1990年庚午年命主综合报告",
      "report_type": "full_analysis",
      "status": "completed",
      "chart_id": "chart_x1y2z3w4",
      "created_at": "2026-07-08T12:05:00Z"
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1, "has_next": false, "has_prev": false }
}
```

#### GET /api/v1/reports/{report_id}

```json
// Response 200 OK
{
  "code": 0,
  "message": "success",
  "data": {
    "report_id": "rpt_mno789",
    "title": "1990年庚午年命主综合报告",
    "chart_id": "chart_x1y2z3w4",
    "analysis_id": "a_abc123",
    "report_type": "full_analysis",
    "status": "completed",
    "sections": [
      {
        "section_id": "s1",
        "title": "命盘总览",
        "content": "您的八字为庚午年、甲申月、戊寅日、戊午时。日主戊土生于申月...",
        "confidence": "high",
        "data_tier": "fact",
        "order": 1
      },
      {
        "section_id": "s2",
        "title": "旺衰与用神",
        "content": "日主戊土生于申月，不得月令...",
        "confidence": "medium",
        "data_tier": "inference",
        "order": 2
      },
      {
        "section_id": "s3",
        "title": "格局分析",
        "content": "此命局杀印相生，为贵格...",
        "confidence": "medium",
        "data_tier": "inference",
        "order": 3
      },
      {
        "section_id": "s8",
        "title": "可信度标注",
        "content": null,
        "confidence": null,
        "data_tier": null,
        "order": 8,
        "metadata": {
          "fact_count": 5,
          "inference_count": 8,
          "pending_count": 2
        }
      }
    ],
    "version": 1,
    "created_at": "2026-07-08T12:05:00Z",
    "updated_at": "2026-07-08T12:05:00Z"
  }
}
```

### 3.5 长任务模块 Task

| 方法 | 路径 | 描述 | 异步 | 鉴权 |
|------|------|------|------|------|
| `GET` | `/api/v1/tasks/{task_id}` | 查询长任务状态 | ❌ | ✅ |
| `POST` | `/api/v1/tasks/{task_id}/cancel` | 取消正在执行的任务 | ❌ | ✅ |

> **Task 对象定义：** 长任务的字段定义（`task_id`, `task_type`, `status`, `progress`, `stage`, `message` 等）统一在 `docs/14_WebSocket实时通信协议设计.md` 4.3 节中定义。HTTP 轮询接口的响应体 `data` 字段即为完整的 Task 对象。本节仅保留路径和状态机示意。

长任务状态有限状态机：

```
  ┌──────────┐
  │  pending  │
  └─────┬────┘
        │
  ┌─────▼──────┐
  │  processing │ ◀─── WebSocket 持续推送进度
  └─────┬──────┘
        │
     ┌──┴───┬──────────┐
     │      │          │
  ┌──▼──┐ ┌─▼──┐  ┌───▼───┐
  │completed│failed│cancelled│
  └────────┘ └─────┘ └───────┘
```

#### GET /api/v1/tasks/{task_id}

```json
// Response 200 OK
{
  "code": 0,
  "data": {
    "task_id": "task_20260708_xyz789",
    "task_type": "bazi.analysis",
    "status": "processing",
    "progress": 45,
    "progress_message": "正在进行格局分析...",
    "result": null,
    "error": null,
    "created_at": "2026-07-08T12:00:00Z",
    "updated_at": "2026-07-08T12:00:35Z",
    "completed_at": null,
    "estimated_remaining_seconds": 25
  }
}
```

### 3.6 知识库模块 Knowledge

| 方法 | 路径 | 描述 | 异步 | 鉴权 |
|------|------|------|------|------|
| `GET` | `/api/v1/knowledge/terms` | 获取命理术语列表（可分页、搜索） | ❌ | ✅ |
| `GET` | `/api/v1/knowledge/terms/{term_id}` | 获取单个术语详情 | ❌ | ✅ |
| `POST` | `/api/v1/knowledge/search` | 语义搜索知识库 | ❌ | ✅ |
| `GET` | `/api/v1/knowledge/references` | 获取命理典籍引用列表 | ❌ | ✅ |

#### GET /api/v1/knowledge/terms

```json
// Query: ?page=1&page_size=20&search=十神&category=ten_gods

// Response 200 OK
{
  "code": 0,
  "data": [
    {
      "term_id": "t_001",
      "name": "十神",
      "category": "ten_gods",
      "summary": "十神是八字命理中用于分析日主与其他天干关系的十种分类...",
      "related_terms": ["正官", "七杀", "正印", "偏印"]
    }
  ],
  "pagination": { "page": 1, "page_size": 20, "total": 1, "total_pages": 1, "has_next": false, "has_prev": false }
}
```

#### POST /api/v1/knowledge/search

```json
// Request
{
  "query": "食神生财的含义",
  "max_results": 5,
  "categories": ["ten_gods", "patterns"]
}

// Response 200 OK
{
  "code": 0,
  "data": [
    {
      "term_id": "t_012",
      "name": "食神生财",
      "category": "patterns",
      "summary": "食神生财是八字中的一种富贵格局...",
      "relevance_score": 0.95
    }
  ]
}
```

### 3.7 系统配置模块 Config

| 方法 | 路径 | 描述 | 异步 | 鉴权 |
|------|------|------|------|------|
| `GET` | `/api/v1/config/health` | 核心服务健康检查 | ❌ | 无鉴权 |
| `GET` | `/api/v1/config/models` | 获取可用 AI 模型/提供商列表 | ❌ | ✅ |
| `GET` | `/api/v1/config/preferences` | 获取当前用户偏好设置 | ❌ | ✅ |
| `PUT` | `/api/v1/config/preferences` | 更新用户偏好设置 | ❌ | ✅ |
| `GET` | `/api/v1/config/system` | 获取系统状态信息 | ❌ | ✅ |

#### GET /api/v1/config/health

```json
// Response 200 OK
{
  "code": 0,
  "data": {
    "status": "healthy",
    "version": "0.1.0",
    "uptime_seconds": 3600,
    "components": {
      "service": "healthy",
      "ai_engine": "healthy",
      "knowledge_base": "degraded"
    }
  }
}
```

#### GET /api/v1/config/preferences

```json
// Response 200 OK
{
  "code": 0,
  "data": {
    "language": "zh-CN",
    "theme": "auto",
    "notifications_enabled": true,
    "analysis_detail_level": "standard",
    "default_report_type": "full_analysis",
    "updated_at": "2026-07-08T12:00:00Z"
  }
}
```

#### GET /api/v1/config/system

```json
// Response 200 OK
{
  "code": 0,
  "data": {
    "ai_provider": "deepseek",
    "ai_model": "deepseek-chat-v3",
    "bazi_engine_version": "1.0.0",
    "knowledge_base_version": "1.0.0",
    "database_size_mb": 12.5,
    "uptime_seconds": 3600,
    "memory_usage_mb": 256
  }
}
```

### 3.8 WebSocket 通道

> **注意：** 完整 WebSocket 通信协议设计见 `docs/14_WebSocket实时通信协议设计.md`。本节仅作为快速参考，详细规范以 14 文档为准。

#### 路径定义

V1 采用单一连接设计，所有消息类型共用同一条 WebSocket 连接，通过 `type` 字段区分：

| 路径 | 方向 | 描述 |
|------|------|------|
| `/ws/v1/session` | 双向 | 统一实时会话通道：AI 对话（`chat.message` / `ai.token`）、任务推送（`task.*`）、系统通知（`notification.system`）全部通过此连接传输 |

鉴权方式：`ws://127.0.0.1:{port}/ws/v1/session?token=<jwt_token>`

#### 消息格式

```json
{
  "type": "chat.message",
  "message_id": "msg_a1b2c3d4",
  "sequence": 42,
  "timestamp": "2026-07-08T12:00:00Z",
  "data": {}
}
```

详见 `14_WebSocket实时通信协议设计.md` 第 4 章 — 消息协议。

#### 消息类型

| type | 方向 | 简述 |
|------|------|------|
| `chat.message` | 客户端→服务端 | 用户发送对话消息 |
| `ai.token` | 服务端→客户端 | AI 逐 Token 流式输出 |
| `ai.done` | 服务端→客户端 | AI 回复完成 |
| `ai.error` | 服务端→客户端 | AI 推理出错 |
| `task.created` | 服务端→客户端 | 任务创建确认 |
| `task.progress` | 服务端→客户端 | 任务进度更新 |
| `task.completed` | 服务端→客户端 | 任务完成 |
| `task.failed` | 服务端→客户端 | 任务失败 |
| `task.resume` | 客户端→服务端 | 断线重连后请求恢复未完成任务并同步当前进度（详见 14_WS 6.2 节） |
| `task.list` | 服务端→客户端 | 返回当前未完成任务列表（详见 14_WS 6.2 节） |
| `notification.system` | 服务端→客户端 | 系统通知推送 |
| `heartbeat.ping` / `heartbeat.pong` | 双向 | 心跳保活 |

完整消息类型定义、JSON 示例、消息确认机制详见 `14_WebSocket实时通信协议设计.md` 4.2~4.5 节。

#### 连接生命周期

详见 `14_WebSocket实时通信协议设计.md` 第 3 章 — 连接规范（6 阶段生命周期：connect → authenticate → subscribe → message exchange → heartbeat → disconnect）。

---

## 4. Request / Response 规范

### 4.1 标准响应体

所有 API 响应使用统一外层包裹：

```json
{
  "code": 0,
  "message": "success",
  "data": {},
  "request_id": "req_20260708_a1b2c3d4"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | int | ✅ | 业务码，0=成功，非0=错误码（详见第 5 章） |
| `message` | string | ✅ | 人类可读的状态描述 |
| `data` | object/array/null | ✅ | 响应数据体，成功时承载业务数据，失败时为 `null` |
| `request_id` | string | ✅ | 请求追踪 ID（服务端分配，便于日志排查与调试） |

### 4.2 错误响应体

```json
{
  "code": 40001,
  "message": "排盘记录不存在",
  "detail": {
    "field": "chart_id",
    "reason": "未找到与给定 ID 匹配的排盘记录",
    "constraints": null
  },
  "request_id": "req_20260708_a1b2c3d4"
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `code` | int | ✅ | 错误码（非 0） |
| `message` | string | ✅ | 错误简短描述 |
| `detail.field` | string | ❌ | 出错字段名（用于表单验证场景） |
| `detail.reason` | string | ❌ | 具体错误原因 |
| `detail.constraints` | object | ❌ | 字段约束说明（如最小值、最大值） |
| `request_id` | string | ✅ | 请求追踪 ID |

### 4.3 分页格式

#### 请求参数

| 参数 | 类型 | 默认值 | 最大值 | 描述 |
|------|------|--------|--------|------|
| `page` | int | 1 | - | 页码，从 1 开始 |
| `page_size` | int | 20 | 100 | 每页数量 |
| `sort_by` | string | `created_at` | - | 排序字段 |
| `sort_order` | string | `desc` | - | `asc` 或 `desc` |

#### 响应格式

```json
{
  "code": 0,
  "message": "success",
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 156,
    "total_pages": 8,
    "has_next": true,
    "has_prev": false
  },
  "request_id": "req_..."
}
```

| 分页字段 | 类型 | 描述 |
|----------|------|------|
| `page` | int | 当前页码 |
| `page_size` | int | 当前页大小 |
| `total` | int | 总记录数 |
| `total_pages` | int | 总页数 |
| `has_next` | bool | 是否有下一页 |
| `has_prev` | bool | 是否有上一页 |

### 4.4 异步任务模式

异步端点遵循以下约定：

1. **提交任务**：POST 请求返回 `202 Accepted`
2. **任务 ID**：响应体中包含 `task_id`
3. **状态轮询**：客户端通过 `GET /api/v1/tasks/{task_id}` 查询状态（返回完整的 Task 对象，字段定义见 `14_WebSocket实时通信协议设计.md` 4.3 节）
4. **WebSocket 订阅**：客户端可通过 `/ws/v1/session` 连接，发送 `subscribe` 消息订阅任务进度推送（详见 `14_WebSocket实时通信协议设计.md`）

状态响应体（Task 对象，完整字段定义见 `14_WebSocket实时通信协议设计.md` 4.3 节）：

```json
{
  "code": 0,
  "data": {
    "task_id": "task_20260708_xyz789",
    "task_type": "bazi.analysis",
    "status": "processing",
    "progress": 45,
    "stage": "four_pillars",
    "stage_label": "四柱计算",
    "message": "正在进行格局分析...",
    "created_at": "2026-07-08T12:00:00Z",
    "updated_at": "2026-07-08T12:00:35Z",
    "completed_at": null,
    "estimated_remaining_seconds": 25,
    "result": null,
    "error": {
      "code": 50001,
      "message": "AI 分析服务暂时不可用"
    }
  }
}
```

**客户端轮询推荐策略：**

| 阶段 | 间隔 | 说明 |
|------|------|------|
| 初始 | 2s | 任务刚提交时高频检查 |
| 稳定 | 5s | 任务进入 `processing` 后降低频率 |
| 退避 | max 10s | 超过预期时间后不再加速 |

### 4.5 鉴权方式

**登录获取 Token：**

```json
// POST /api/v1/users/login Response
{
  "code": 0,
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "token_type": "bearer",
    "expires_in": 86400
  }
}
```

**请求鉴权：**

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

**Token 格式：**

| 字段 | 说明 |
|------|------|
| Token 类型 | JWT |
| 负载 | `user_id`, `username`, `role`, `iat`, `exp` |
| 有效期 | 24 小时（配置项 **【待确认】** ）|
| 签名算法 | HS256 |
| 刷新机制 | Token 过期后需重新登录（V1 暂不实现 Refresh Token）|

**WebSocket 鉴权：**

```
ws://localhost:{port}/ws/v1/session?token=<jwt_token>
```

**无鉴权端点：**（仅以下端点不要求 Token）

| 端点 | 用途 |
|------|------|
| `GET /api/v1/config/health` | 健康检查 |
| `POST /api/v1/users/register` | 用户注册 |
| `POST /api/v1/users/login` | 用户登录 |

---

## 5. 错误码规范

### 5.1 错误码范围

| 范围 | 分类 | 描述 |
|------|------|------|
| `0` | 成功 | 请求成功完成 |
| `10000` ~ `19999` | **系统错误** | 服务端内部错误、服务不可用、超时 |
| `20000` ~ `29999` | **鉴权错误** | 未登录、Token 过期、权限不足 |
| `30000` ~ `39999` | **请求验证错误** | 参数无效、格式错误、缺失必填字段 |
| `40000` ~ `49999` | **资源错误** | 资源不存在、冲突、已删除 |
| `50000` ~ `59999` | **业务逻辑错误** | 排盘失败、AI 分析失败、业务规则冲突 |
| `60000` ~ `69999` | **限流与配额** | 请求频率超限、免费额度用尽 |

### 5.2 具体错误码定义

| Code | HTTP Status | Message | 描述 |
|------|-------------|---------|------|
| **成功** | | | |
| `0` | 200/201/204 | 成功 | 请求成功完成 |
| **系统错误** | | | |
| `10001` | 500 | 服务器内部错误 | 未预期的服务端运行时错误 |
| `10002` | 503 | 服务暂时不可用 | 服务正在启动或维护中 |
| `10003` | 504 | 请求超时 | 上游服务（LLM API）响应超时 |
| `10004` | 502 | 外部服务调用失败 | LLM API 或第三方服务返回错误 |
| **鉴权错误** | | | |
| `20001` | 401 | 未授权访问 | 请求缺少或携带无效的 Token |
| `20002` | 401 | Token 已过期 | Token 超过有效期，需重新登录 |
| `20003` | 403 | 权限不足 | Token 有效但无权限访问该资源 |
| `20004` | 401 | 登录凭证无效 | 用户名或密码错误 |
| **请求验证错误** | | | |
| `30001` | 422 | 请求参数无效 | 请求体 JSON 解析失败或缺少必填字段 |
| `30002` | 422 | 字段验证失败 | 某字段值不在合法范围内 |
| `30003` | 413 | 请求体过大 | 请求体超过最大限制 |
| **资源错误** | | | |
| `40001` | 404 | 资源不存在 | 请求的资源不存在 |
| `40002` | 409 | 资源已存在 | 创建资源时发生唯一性冲突（如用户名重复）|
| `40003` | 410 | 资源已被删除 | 请求的资源已被删除 |
| **业务逻辑错误** | | | |
| `50001` | 422 | 排盘计算失败 | 出生信息无法生成有效的排盘结果 |
| `50002` | 500 | AI 分析失败 | AI 分析过程中发生错误 |
| `50003` | 409 | 分析流程状态错误 | 当前分析状态不允许执行此操作 |
| `50004` | 422 | 反馈无法处理 | 用户反馈内容无法对应到有效的分析项 |
| **限流与配额** | | | |
| `60001` | 429 | 请求频率超限 | API 调用频率超过限制 |
| `60002` | 403 | 免费额度用尽 | 免费用户超出每日/每月配额 |

### 5.3 错误码使用规则

- 客户端应使用 `code` 字段做程序化处理，**不得**依赖 `message` 字符串
- 错误码在同一个版本内**保持稳定**，不会变更含义
- 跨版本升级时，错误码变更遵循第 6 章的版本策略
- 系统错误（1xxxx）应触发客户端重试逻辑
- 鉴权错误（2xxxx）应触发客户端跳转到登录页面
- 请求验证错误（3xxxx）应触发客户端字段级错误提示
- 限流错误（6xxxx）应触发客户端指数退避

---

## 6. 版本策略

### 6.1 URL 路径版本化

所有 API 端点以 URL 路径前缀携带版本号：

```
/api/v1/<resource>/<action>
```

- **v1**：当前版本，对应 V1 产品范围（Windows APP）
- **v2**：未来版本，用于承载破坏性变更

### 6.2 版本兼容性规则

| 变更类型 | 示例 | 需要新版本？ |
|----------|------|-------------|
| 新增可选响应字段 | 用户资料增加 `nickname` 字段 | ❌ |
| 新增端点 | 增加 `/api/v1/reports/export` | ❌ |
| 新增枚举值 | 任务增加 `cancelled` 状态 | ❌ |
| 延长字段约束 | 密码长度从 8-64 放宽为 6-64 | ❌ |
| 修改字段数据类型 | `birth_year` 从 int 改为 string | ✅ 需要 v2 |
| 删除字段 | 从排盘响应中移除 `hidden_stems` | ✅ 需要 v2 |
| 重命名字段 | `bazi_chart` 改为 `chart` | ✅ 需要 v2 |
| 修改端点路径 | `/bazi/charts` 改为 `/bazi/fate-charts` | ✅ 需要 v2 |
| 变更错误码语义 | 复用 20001 表示不同错误 | ✅ 需要 v2 |
| 缩短字段约束 | 密码长度从 8-64 缩短为 10-32 | ✅ 需要 v2 |

### 6.3 弃用策略

当某个端点或字段被弃用时：

1. 端点头部携带 `X-API-Deprecated: true`
2. 端点头部携带 `X-API-Sunset: Sat, 31 Jan 2027 00:00:00 GMT`（预期移除日期）
3. 文档中标记为 `⚠️ 已弃用`
4. 弃用期最少 **6 个月**
5. 移除时记入 ChangeLog 并在新的 API 版本中移除

### 6.4 客户端兼容性

| 客户端版本 | API 版本 | 说明 |
|-----------|----------|------|
| V1 Windows APP | `/api/v1/` | 硬编码 v1 路径 |
| V2 Web (未来) | `/api/v2/` | 可在新功能中使用 v2 端点 |
| V1 APP → V2 核心服务 | `/api/v1/` 仍可用 | 服务端同时支持 v1 和 v2 |
| V2 客户端 → V1 核心服务 | 降级使用 v1 端点 | 客户端应兼容 v1 格式 |

---

## 7. 示例 JSON

### 7.1 用户注册与登录

#### 注册

```json
// POST /api/v1/users/register
// Request:
{
  "username": "mingli_enthusiast",
  "password": "secure_password_123",
  "birth_year": 1990,
  "birth_month": 8,
  "birth_day": 15,
  "birth_hour": 12,
  "birth_minute": 0,
  "gender": "male",
  "birth_place": "北京",
  "calendar_type": "solar"
}

// Response 201 Created:
{
  "code": 0,
  "message": "注册成功",
  "data": {
    "user_id": "u_a1b2c3d4",
    "username": "mingli_enthusiast",
    "created_at": "2026-07-08T12:00:00Z"
  },
  "request_id": "req_20260708_a1b2c3d4"
}
```

#### 登录

```json
// POST /api/v1/users/login
// Request:
{
  "username": "mingli_enthusiast",
  "password": "secure_password_123"
}

// Response 200 OK:
{
  "code": 0,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidV9hMWIyYzNkNCIsInVzZXJuYW1lIjoibWluZ2xpX2VudGh1c2lhc3QiLCJleHAiOjE3MjA0MTYwMDB9.abc123...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user_id": "u_a1b2c3d4"
  },
  "request_id": "req_20260708_b2c3d4e5"
}
```

### 7.2 八字排盘创建与 AI 分析触发

#### 创建排盘

```json
// POST /api/v1/bazi/charts
// Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
// Request:
{
  "birth_year": 1990,
  "birth_month": 8,
  "birth_day": 15,
  "birth_hour": 12,
  "birth_minute": 0,
  "gender": "male",
  "birth_place": "北京",
  "timezone": "Asia/Shanghai",
  "calendar_type": "solar",
  "name": "我的八字",
  "is_primary": true
}

// Response 201 Created:
{
  "code": 0,
  "message": "排盘成功",
  "data": {
    "chart_id": "chart_x1y2z3w4",
    "name": "我的八字",
    "is_primary": true,
    "input": {
      "birth_year": 1990,
      "birth_month": 8,
      "birth_day": 15,
      "birth_hour": 12,
      "birth_minute": 0,
      "gender": "male",
      "birth_place": "北京",
      "timezone": "Asia/Shanghai",
      "calendar_type": "solar"
    },
    "pillars": {
      "year": { "heavenly_stem": "庚", "earthly_branch": "午", "hidden_stems": ["丁", "己"] },
      "month": { "heavenly_stem": "甲", "earthly_branch": "申", "hidden_stems": ["庚", "壬", "戊"] },
      "day": { "heavenly_stem": "戊", "earthly_branch": "寅", "hidden_stems": ["甲", "丙", "戊"] },
      "hour": { "heavenly_stem": "戊", "earthly_branch": "午", "hidden_stems": ["丁", "己"] }
    },
    "five_elements": {
      "wood": { "count": 2, "status": "旺", "score": 25 },
      "fire": { "count": 3, "status": "旺", "score": 30 },
      "earth": { "count": 4, "status": "最旺", "score": 40 },
      "metal": { "count": 2, "status": "中和", "score": 20 },
      "water": { "count": 0, "status": "弱", "score": 5 }
    },
    "day_master": { "stem": "戊", "strength": "偏旺" },
    "ten_gods": [
      { "pillar": "year", "heavenly_stem": "庚", "ten_god": "食神" },
      { "pillar": "month", "heavenly_stem": "甲", "ten_god": "七杀" },
      { "pillar": "day", "heavenly_stem": "戊", "ten_god": "日主" },
      { "pillar": "hour", "heavenly_stem": "戊", "ten_god": "比肩" }
    ],
    "great_fortune": [
      { "age_range": "0-9", "heavenly_stem": "乙", "earthly_branch": "酉" },
      { "age_range": "10-19", "heavenly_stem": "丙", "earthly_branch": "戌" },
      { "age_range": "20-29", "heavenly_stem": "丁", "earthly_branch": "亥" }
    ],
    "current_year": { "year": 2026, "heavenly_stem": "丙", "earthly_branch": "午" },
    "created_at": "2026-07-08T12:01:00Z"
  },
  "request_id": "req_20260708_c3d4e5f6"
}
```

#### 触发 AI 分析

```json
// POST /api/v1/bazi/charts/chart_x1y2z3w4/analysis
// Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
// Request:
{
  "analysis_type": "full",
  "context": {
    "conversation_id": "conv_abc123",
    "include_dynamic_questions": true
  }
}

// Response 202 Accepted:
{
  "code": 0,
  "message": "分析任务已提交",
  "data": {
    "task_id": "task_20260708_xyz789",
    "analysis_id": "a_abc123",
    "status": "pending",
    "estimated_seconds": 45
  },
  "request_id": "req_20260708_d4e5f6g7"
}
```

#### 轮询任务状态

```json
// GET /api/v1/tasks/task_20260708_xyz789
// Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

// Response 200 OK (processing):
{
  "code": 0,
  "data": {
    "task_id": "task_20260708_xyz789",
    "task_type": "bazi.analysis",
    "status": "processing",
    "progress": 45,
    "progress_message": "正在进行格局分析...",
    "result": null,
    "error": null,
    "created_at": "2026-07-08T12:00:00Z",
    "updated_at": "2026-07-08T12:00:35Z",
    "completed_at": null,
    "estimated_remaining_seconds": 25
  },
  "request_id": "req_20260708_e5f6g7h8"
}
```

### 7.3 报告生成与查询

#### 生成报告

```json
// POST /api/v1/reports
// Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
// Request:
{
  "chart_id": "chart_x1y2z3w4",
  "analysis_id": "a_abc123",
  "report_type": "full_analysis",
  "title": "1990年庚午年命主综合报告"
}

// Response 202 Accepted:
{
  "code": 0,
  "message": "报告生成任务已提交",
  "data": {
    "report_id": null,
    "task_id": "task_20260708_abc456",
    "status": "pending",
    "estimated_seconds": 60
  },
  "request_id": "req_20260708_f6g7h8i9"
}
```

#### 获取报告内容

```json
// GET /api/v1/reports/rpt_mno789
// Headers: Authorization: Bearer eyJhbGciOiJIUzI1NiIs...

// Response 200 OK:
{
  "code": 0,
  "message": "success",
  "data": {
    "report_id": "rpt_mno789",
    "title": "1990年庚午年命主综合报告",
    "chart_id": "chart_x1y2z3w4",
    "analysis_id": "a_abc123",
    "report_type": "full_analysis",
    "status": "completed",
    "sections": [
      {
        "section_id": "s1",
        "title": "命盘总览",
        "content": "您的八字为庚午年、甲申月、戊寅日、戊午时。日主戊土生于申月，不得月令，但四柱中比肩众多，得地得势，日主偏旺。喜用金水，忌火土。",
        "confidence": "high",
        "data_tier": "fact",
        "order": 1
      },
      {
        "section_id": "s2",
        "title": "旺衰与用神",
        "content": "日主戊土生于申月（秋季），金旺土相，戊土不得月令。但年支午火、时支午火皆为印星生身，日支寅木藏丙火亦生日主。综合判断为身旺，取金水为用，火土为忌。",
        "confidence": "medium",
        "data_tier": "inference",
        "order": 2
      },
      {
        "section_id": "s3",
        "title": "格局分析",
        "content": "此命局杀印相生，年柱食神透出，月柱七杀当头，日坐偏印，时柱比肩帮身。形成食神制杀、杀印相生的贵格。主聪明果断，有管理才能，但七杀旺相亦主人生多波折。",
        "confidence": "medium",
        "data_tier": "inference",
        "order": 3
      }
    ],
    "version": 1,
    "created_at": "2026-07-08T12:05:00Z",
    "updated_at": "2026-07-08T12:05:00Z"
  },
  "request_id": "req_20260708_g7h8i9j0"
}
```

### 7.4 错误响应示例

#### 字段验证失败（422）

```json
// POST /api/v1/users/register — birth_year 超出范围
// HTTP 422 Unprocessable Entity
{
  "code": 30002,
  "message": "字段验证失败",
  "detail": {
    "field": "birth_year",
    "reason": "必须在 1900 至当前年份之间",
    "constraints": { "min": 1900, "max": 2026 }
  },
  "request_id": "req_20260708_h8i9j0k1"
}
```

#### 资源不存在（404）

```json
// GET /api/v1/bazi/charts/nonexistent_id
// HTTP 404 Not Found
{
  "code": 40001,
  "message": "排盘记录不存在",
  "detail": {
    "field": "chart_id",
    "reason": "未找到与给定 ID 匹配的排盘记录"
  },
  "request_id": "req_20260708_i9j0k1l2"
}
```

#### 鉴权失败（401）

```json
// GET /api/v1/users/me — 未提供 Token 或 Token 无效
// HTTP 401 Unauthorized
{
  "code": 20001,
  "message": "未授权访问",
  "detail": {
    "field": "Authorization",
    "reason": "请求缺少 Bearer Token 或 Token 格式错误"
  },
  "request_id": "req_20260708_j0k1l2m3"
}
```

#### 资源冲突（409）

```json
// POST /api/v1/users/register — 用户名已存在
// HTTP 409 Conflict
{
  "code": 40002,
  "message": "用户名已存在",
  "detail": {
    "field": "username",
    "reason": "该用户名已被其他用户注册",
    "constraints": { "unique": true }
  },
  "request_id": "req_20260708_k1l2m3n4"
}
```

---

## 8. 【待确认】项清单

以下项目需产品负责人确认后方可在实现阶段定稿：

| 序号 | 项目 | 当前建议 | 需要确认的内容 |
|------|------|----------|---------------|
| 1 | Token 有效期 | 24 小时 | 是否需要更短（12h）或更长（7天）？是否需要 Refresh Token 机制？ |
| 2 | 报告类型枚举 | `full_analysis`、`quick`、`year_fortune` | V1 需要哪些报告类型？未来规划哪些？ |
| 3 | 免费/付费端点划分 | 未分配 | 哪些端点对免费用户开放？付费用户解锁哪些功能？ |
| 4 | 分页 page_size 上限 | 100 | 是否需要更小（50）或更大（200）限制？ |
| 5 | 限流阈值 | 未定义 | 每小时/每分钟最大请求数？是否按端点区分？ |
| 6 | 错误信息语言策略 | 仅中文 | V1 是否支持 i18n？是否通过 `Accept-Language` 头部切换？ |
| 7 | 敏感字段加密 | 未处理 | 生日/姓名等敏感字段是否需要在传输层额外加密？ |

---

## 附：变更记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v0.1 | 2026-07-08 | 初版 Draft，定义 API 设计原则、Endpoint 列表、错误码规范、版本策略 |
