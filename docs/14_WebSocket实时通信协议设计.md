# 14 — WebSocket 实时通信协议设计

> **版本:** v0.1 | **日期:** 2026-07-08 | **状态:** Draft  
> **关联 ADR：** ADR-009（八字分析6步流程）、ADR-014（本地优先+云端扩展）、ADR-017（客户端解耦）、ADR-019（HTTP+WebSocket双通道通信）

---

## 📖 目录

- [1. 设计目标](#1-设计目标)
- [2. 架构模型](#2-架构模型)
- [3. 连接规范](#3-连接规范)
- [4. 消息协议](#4-消息协议)
- [5. 任务流程](#5-任务流程)
- [6. 异常处理](#6-异常处理)
- [7. 安全策略](#7-安全策略)
- [8. 未来扩展](#8-未来扩展)

---

## 1. 设计目标

### 1.1 四个核心目标

| 目标 | 说明 | 衡量标准 |
|------|------|----------|
| **实时性** | AI 对话 Token 流式输出、任务进度即时推送 | 首 Token 延迟 < 1s，心跳间隔 30s |
| **可靠性** | 消息不丢失、不重复、不乱序，断线可恢复 | 消息确认机制、序号追踪、断线重连 |
| **安全性** | 连接鉴权、消息校验、敏感数据保护 | Token 验证、速率限制、数据最小化 |
| **可扩展性** | 支持未来多 Agent 推送、广播通道、消息压缩 | 协议层预留扩展字段 |

### 1.2 设计原则

1. **轻量文本协议** — 所有消息使用 JSON 文本帧，降低序列化/反序列化开销
2. **类型驱动路由** — 消息通过 `type` 字段分发，服务端和客户端各自维护路由表
3. **异步非阻塞** — 消息处理不阻塞连接，心跳和业务消息互相独立
4. **优雅降级** — 网络不稳定时自动重连，任务状态通过 HTTP 轮询作为 fallback
5. **与 HTTP API 互补** — WebSocket 仅负责实时/流式场景，CRUD 操作仍走 HTTP REST

---

## 2. 架构模型

### 2.1 五层架构总览

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: WebSocket Client（客户端连接管理层）                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ · 连接建立/断开管理                                    │   │
│  │ · 心跳保活（定时 ping）                                │   │
│  │ · 自动重连（指数退避）                                  │   │
│  │ · 消息发送队列（断线自动缓存，重连后重发）                │   │
│  │ · 消息序号追踪（去重、排序）                             │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │ ws://127.0.0.1:{port}/ws/*
                          │
┌─────────────────────────┼───────────────────────────────────┐
│ Layer 2: WebSocket Gateway（FastAPI 连接网关层）              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ · 连接接受/拒绝                                        │   │
│  │ · Token 鉴权验证                                      │   │
│  │ · 连接生命周期管理（connect / disconnect 回调）          │   │
│  │ · 单用户连接数限制                                      │   │
│  │ · WebSocket 帧解析/序列化                              │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│ Layer 3: Message Router（消息路由层）                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ · 按 type 字段路由消息到对应 Handler                   │   │
│  │ · 消息格式校验（JSON Schema 验证）                     │   │
│  │ · 消息序号分配（服务端生成 message_id）                  │   │
│  │ · 广播管理（订阅/取消订阅）                             │   │
│  │ · 错误消息构造与返回                                   │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│ Layer 4: Task Manager（任务管理层）                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ · 任务状态有限状态机（pending → processing → completed）│   │
│  │ · 任务进度追踪与推送                                   │   │
│  │ · 任务取消/超时处理                                    │   │
│  │ · 任务恢复（断线重连后查询当前进度）                     │   │
│  │ · 防止重复任务（相同 chart_id + analysis_type 去重）    │   │
│  └──────────────────────┬───────────────────────────────┘   │
└─────────────────────────┼───────────────────────────────────┘
                          │
┌─────────────────────────┼───────────────────────────────────┐
│ Layer 5: AI Analysis Pipeline（AI 分析流水线层）              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ Stage 1: 数据解析（验证出生信息、格式化输入）           │   │
│  │ Stage 2: 四柱计算（调用排盘引擎）                      │   │
│  │ Stage 3: 五行分析（旺衰、用神、格局判定）               │   │
│  │ Stage 4: AI 推理（LLM 深度分析）                      │   │
│  │ Stage 5: 报告生成（结构化输出、数据层级标注）           │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 每层职责详述

| 层级 | 职责 | 关键技术点 | 容错策略 |
|------|------|-----------|----------|
| **Layer 1: Client** | 连接管理、心跳、重连、消息队列 | 指数退避重连、消息序号去重 | 离线缓存消息，重连后按序发送 |
| **Layer 2: Gateway** | 鉴权、帧解析、连接计数 | WebSocket `on_connect`/`on_disconnect` 钩子 | 拒绝非法连接，关闭闲置连接 |
| **Layer 3: Router** | 消息分发、格式校验 | 策略模式路由表、JSON Schema 校验 | 格式错误返回 error 帧，不中断连接 |
| **Layer 4: Task Manager** | 任务状态机、进度推送 | 状态机 + 观察者模式 | 断线后客户端重连时同步当前状态 |
| **Layer 5: Pipeline** | 业务分析流水线 | 管道模式（Pipeline Pattern） | 每阶段 catch 异常，标记任务失败 |

### 2.3 消息流向

```
客户端 → Gateway → Router → Handler → Task Manager → Pipeline → 结果回调 → Router → Gateway → 客户端
```

- **上行路径：** 客户端消息 → 路径解析 → 格式校验 → 业务处理
- **下行路径：** 业务结果 → 消息构造 → 序列化 → 推送给客户端

---

## 3. 连接规范

### 3.1 连接地址

V1 阶段 WebSocket 服务监听 `localhost`，与 HTTP API 共用端口。V1 采用**单一连接**设计，所有消息类型共用同一条 WebSocket 连接，通过 `type` 字段区分。

| 路径 | 方向 | 描述 | 鉴权 |
|------|------|------|------|
| `/ws/v1/session` | 双向 | 统一实时会话通道：AI 对话、任务推送、系统通知全部通过此连接传输 | ✅ |

#### URL 参数

| 参数 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `token` | string | ✅ | JWT Token，用于连接鉴权 |
| `protocol` | string | ❌ | 协议版本，默认 `v1` |

**示例：**

```
ws://127.0.0.1:8000/ws/v1/session?token=eyJhbGciOiJIUzI1NiIs...
```

### 3.2 连接生命周期

共 6 个阶段：

```
 ┌──────────┐
 │ ① connect  │ ──── 客户端发起 WebSocket 连接请求
 └─────┬────┘
       │
 ┌─────▼──────┐
 │ ② authenticate │ ──── 服务端验证 token，通过则接受连接
 └─────┬──────┘
       │
 ┌─────▼──────┐
 │ ③ subscribe  │ ──── 客户端订阅感兴趣的消息通道（按路径区分）
 └─────┬──────┘
       │
 ┌─────▼────────┐
 │ ④ message     │ ──── 消息交换：客户端发送/服务端推送
 │    exchange   │
 └─────┬────────┘
       │
 ┌─────▼──────┐
 │ ⑤ heartbeat  │ ──── 定期 ping/pong 保持连接（与阶段 ④ 并发）
 └─────┬──────┘
       │
 ┌─────▼────────┐
 │ ⑥ disconnect  │ ──── 任意一方主动或被动断开连接
 └──────────────┘
```

#### 阶段详情

**① connect：**

- 客户端发起 HTTP Upgrade 请求，URL 携带 `?token=<jwt_token>`
- 如果 Token 缺失或格式不符，服务端直接拒绝 Upgrade（HTTP 401）
- 同一用户已存在活跃连接时，策略见 7.4 节

**② authenticate：**

- 服务端解析 JWT Token，提取 `user_id`、`role` 等信息
- Token 过期 → 断开连接，返回错误码 `20002`
- Token 有效 → 加载用户上下文，建立连接会话

**③ subscribe：**

- 连接建立后，客户端根据需要按 `type` 订阅不同通道的消息
- 订阅通过 `subscribe` 消息类型完成：
  - `{"type": "subscribe", "data": {"channel": "chat"}}` → 订阅对话通道
  - `{"type": "subscribe", "data": {"channel": "task", "task_id": "task_xxx"}}` → 订阅任务推送
  - `{"type": "subscribe", "data": {"channel": "notification"}}` → 订阅系统通知
- 服务端对每个订阅返回 `subscribe.confirmed` 确认

**④ message exchange：**

- 客户端可发送 `chat.message` 等上行消息
- 服务端可推送 `ai.token`、`task.progress` 等下行的消息
- 所有消息携带 `message_id` 用于去重和确认

**⑤ heartbeat：**

- 客户端每 30 秒发送 `heartbeat.ping`
- 服务端收到后回复 `heartbeat.pong`
- 服务端 90 秒未收到任何消息（含 ping）则判定客户端断开
- 客户端 60 秒未收到 pong 则判定服务端不可用，触发重连（pong 超时 = 2× ping 间隔，预留网络抖动缓冲，见 §3.3）

**⑥ disconnect：**

- 客户端主动关闭：发送 Close 帧，服务端清理会话
- 服务端关闭：发送 Close 帧 + 原因码，客户端触发重连
- 意外断开（网络中断）：客户端触发自动重连机制（第 6 章）

### 3.3 心跳参数

| 参数 | 值 | 说明 |
|------|-----|------|
| ping 间隔 | 30s | 客户端发送 `heartbeat.ping` 的周期 |
| pong 超时 | 60s | 客户端等待 `heartbeat.pong` 的超时时间（= 2× ping 间隔，预留网络抖动缓冲，避免误断连） |
| 连接空闲超时 | 90s | 服务端关闭无活动连接的阈值 |
| 重连初始间隔 | 1s | 第一次重连等待时间 |
| 重连最大间隔 | 30s | 指数退避上限 |

---

## 4. 消息协议

### 4.1 统一消息格式

所有 WebSocket 消息使用 UTF-8 JSON 文本帧，格式如下：

```json
{
  "type": "chat.message",
  "message_id": "msg_a1b2c3d4e5",
  "sequence": 42,
  "timestamp": "2026-07-08T12:00:00Z",
  "data": {}
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `type` | string | ✅ | 消息类型，用于路由和解析（详见 4.2） |
| `message_id` | string | ✅ | 消息唯一标识，客户端生成上行 ID，服务端生成下行 ID。格式：`msg_` + 随机字符串。用于全局去重 |
| `sequence` | int | ❌ | 连接级别的单调递增序号。每建立一次连接从 0 开始计数。用于断线后检测消息间隙和请求重传 |
| `timestamp` | string | ✅ | ISO 8601 格式 UTC 时间，消息发送时间 |
| `data` | object | ✅ | 消息负载，不同 `type` 对应不同结构 |

### 4.2 消息类型定义

| type | 方向 | data 结构 | 描述 |
|------|------|-----------|------|
| **chat.message** | 客户端→服务端 | `{content, chart_id?, session_id?, context?}` | 用户发送对话消息 |
| **ai.token** | 服务端→客户端 | `{token, index, session_id}` | AI 逐 Token 流式输出 |
| **ai.done** | 服务端→客户端 | `{session_id, finish_reason, usage}` | AI 回复完成 |
| **ai.error** | 服务端→客户端 | `{code, message, session_id}` | AI 推理过程出错 |
| **task.created** | 服务端→客户端 | `{task_id, task_type, status, estimated_seconds}` | 任务创建确认 |
| **task.progress** | 服务端→客户端 | `{task_id, progress, stage, message}` | 任务进度更新 |
| **task.completed** | 服务端→客户端 | `{task_id, result, completed_at}` | 任务完成 |
| **task.failed** | 服务端→客户端 | `{task_id, code, message}` | 任务失败 |
| **task.cancelled** | 服务端→客户端 | `{task_id, reason}` | 任务被取消 |
| **task.resume** | 客户端→服务端 | `{last_sequence?: int}` | 断线重连后请求恢复未完成任务并同步当前进度（详见 6.2 节） |
| **task.list** | 服务端→客户端 | `{active_tasks: [{task_id, status, progress, stage, message?}]}` | 返回当前未完成任务列表（详见 6.2 节） |
| **notification.system** | 服务端→客户端 | `{type, title, body, action?}` | 系统通知推送 |
| **subscribe** | 客户端→服务端 | `{channel, task_id?}` | 订阅指定通道的消息推送（channel：`chat` / `task` / `notification`） |
| **subscribe.confirmed** | 服务端→客户端 | `{channel, task_id?}` | 订阅确认 |
| **error** | 双向 | `{code, message, original_message_id?}` | 协议层错误 |
| **heartbeat.ping** | 客户端→服务端 | `{}` | 心跳请求 |
| **heartbeat.pong** | 服务端→客户端 | `{}` | 心跳响应 |

### 4.3 Task 对象定义

Task 对象是 HTTP API 与 WebSocket 之间共享的数据模型，用于统一表达长任务的生命周期和状态。所有涉及任务的消息（`task.*`）和 HTTP 任务轮询接口均使用此对象定义。

```json
{
  "task_id": "task_20260708_xyz789",
  "task_type": "bazi.analysis",
  "status": "processing",
  "progress": 45,
  "stage": "four_pillars",
  "stage_label": "四柱计算",
  "message": "正在进行四柱计算...",
  "created_at": "2026-07-08T12:00:00Z",
  "updated_at": "2026-07-08T12:00:35Z",
  "completed_at": null,
  "estimated_remaining_seconds": 25,
  "result": null,
  "error": null
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `task_id` | string | ✅ | 任务唯一标识，格式 `task_` + 日期 + 随机后缀 |
| `task_type` | string | ✅ | 任务类型，如 `bazi.analysis`、`report.generate` |
| `status` | string | ✅ | 任务状态：`pending` / `processing` / `completed` / `failed` / `cancelled` / `timed_out` |
| `progress` | int | ❌ | 进度百分比 0-100 |
| `stage` | string | ❌ | 当前阶段标识，如 `data_parsing`、`four_pillars` |
| `stage_label` | string | ❌ | 阶段中文名称，如"四柱计算" |
| `message` | string | ❌ | 人类可读的当前状态描述 |
| `created_at` | string | ✅ | ISO 8601 任务创建时间 |
| `updated_at` | string | ✅ | ISO 8601 最后状态变更时间 |
| `completed_at` | string / null | ❌ | ISO 8601 任务完成时间，未完成时为 `null` |
| `estimated_remaining_seconds` | int | ❌ | 预计剩余秒数 |
| `result` | object / null | ❌ | 任务完成后的结果数据 |
| `error` | object / null | ❌ | 任务失败时的错误信息 `{code, message, failed_stage?}` |

**状态机流转：**

```
                  ┌──────────┐
                  │  pending  │
                  └─────┬────┘
                        │
                  ┌─────▼──────┐
          ┌──────│ processing  │
          │      └──────┬──────┘
          │             │
     ┌────┴────┐  ┌────┴────┐  ┌──────────┐
     │cancelled│  │completed│  │  failed  │
     └─────────┘  └─────────┘  └────┬─────┘
                                    │
                               ┌────▼─────┐
                               │ timed_out │
                               └──────────┘
```

**字段命名规则：** HTTP API（`13_API接口契约设计.md`）与 WebSocket（本文档）中的 Task 相关字段必须统一使用此定义。HTTP 轮询接口 `GET /api/v1/tasks/{id}` 的响应体中的 `data` 字段即为完整的 Task 对象。

### 4.4 消息类型详述

#### 4.4.1 chat.message（客户端→服务端）

用户向知命发送一条对话消息。

```json
{
  "type": "chat.message",
  "message_id": "msg_a1b2c3d4",
  "timestamp": "2026-07-08T12:00:00Z",
  "data": {
    "content": "你好知命，请分析我的八字",
    "session_id": "session_abc123",
    "chart_id": "chart_x1y2z3w4",
    "context": {
      "analysis_id": "a_abc123",
      "client_meta": {
        "platform": "windows",
        "app_version": "0.1.0"
      }
    }
  }
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `content` | string | ✅ | 用户消息文本 |
| `session_id` | string | ❌ | 对话会话 ID，留空则服务端新建会话 |
| `chart_id` | string | ❌ | 关联的八字排盘 ID，用于分析上下文 |
| `context` | object | ❌ | 附加上下文（分析 ID、客户端信息等） |

#### 4.4.2 ai.token（服务端→客户端）

AI 回复的逐 Token 流式输出，同一回复的 `session_id` 相同。

```json
{
  "type": "ai.token",
  "message_id": "msg_b2c3d4e5",
  "timestamp": "2026-07-08T12:00:01Z",
  "data": {
    "token": "根据",
    "index": 0,
    "session_id": "session_abc123"
  }
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `token` | string | ✅ | AI 输出的文本片段（一个字或一个词） |
| `index` | int | ✅ | Token 序号，从 0 递增，客户端用于拼接和排序 |
| `session_id` | string | ✅ | 所属对话会话 ID |

#### 4.4.3 ai.done（服务端→客户端）

AI 流式输出结束标志。

```json
{
  "type": "ai.done",
  "message_id": "msg_c3d4e5f6",
  "timestamp": "2026-07-08T12:00:35Z",
  "data": {
    "session_id": "session_abc123",
    "finish_reason": "stop",
    "usage": {
      "prompt_tokens": 1200,
      "completion_tokens": 350,
      "total_tokens": 1550
    }
  }
}
```

#### 4.4.4 ai.error（服务端→客户端）

AI 推理过程发生错误。

```json
{
  "type": "ai.error",
  "message_id": "msg_d4e5f6g7",
  "timestamp": "2026-07-08T12:00:10Z",
  "data": {
    "code": 50002,
    "message": "AI 分析服务暂时不可用",
    "session_id": "session_abc123"
  }
}
```

#### 4.4.5 task.created（服务端→客户端）

创建耗时任务后的确认消息，通过统一会话通道 `/ws/v1/session` 推送（详见 3.1 节）。

```json
{
  "type": "task.created",
  "message_id": "msg_e5f6g7h8",
  "timestamp": "2026-07-08T12:00:00Z",
  "data": {
    "task_id": "task_20260708_xyz789",
    "task_type": "bazi.analysis",
    "status": "pending",
    "estimated_seconds": 45
  }
}
```

#### 4.4.6 task.progress（服务端→客户端）

任务进度更新推送。

```json
{
  "type": "task.progress",
  "message_id": "msg_f6g7h8i9",
  "timestamp": "2026-07-08T12:00:25Z",
  "data": {
    "task_id": "task_20260708_xyz789",
    "progress": 60,
    "stage": "four_pillars",
    "stage_label": "四柱计算",
    "message": "年柱: 庚午, 月柱: 甲申, 日柱: 戊寅, 时柱: 戊午"
  }
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `progress` | int | ✅ | 进度百分比 0-100 |
| `stage` | string | ❌ | 当前阶段标识（如 `data_parsing`、`four_pillars`） |
| `stage_label` | string | ❌ | 阶段中文描述 |
| `message` | string | ❌ | 人类可读的当前状态描述 |

#### 4.4.7 task.completed（服务端→客户端）

任务完成通知。

```json
{
  "type": "task.completed",
  "message_id": "msg_g7h8i9j0",
  "timestamp": "2026-07-08T12:01:00Z",
  "data": {
    "task_id": "task_20260708_xyz789",
    "result": {
      "analysis_id": "a_abc123",
      "report_id": "rpt_mno789"
    },
    "completed_at": "2026-07-08T12:01:00Z"
  }
}
```

#### 4.4.8 task.failed（服务端→客户端）

任务失败通知。

```json
{
  "type": "task.failed",
  "message_id": "msg_h8i9j0k1",
  "timestamp": "2026-07-08T12:00:50Z",
  "data": {
    "task_id": "task_20260708_xyz789",
    "code": 50002,
    "message": "AI 分析服务调用超时",
    "failed_stage": "ai_inference"
  }
}
```

#### 4.4.9 notification.system（服务端→客户端）

系统级通知推送，通过统一会话通道 `/ws/v1/session` 推送（详见 3.1 节）。

```json
{
  "type": "notification.system",
  "message_id": "msg_i9j0k1l2",
  "timestamp": "2026-07-08T14:00:00Z",
  "data": {
    "type": "report.completed",
    "title": "深度分析报告已生成",
    "body": "您的2026年流年分析报告已完成，请在报告中查看。",
    "action": {
      "type": "navigate",
      "payload": {
        "route": "/reports/rpt_mno789"
      }
    },
    "priority": "normal"
  }
}
```

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| `type` | string | ✅ | 通知类型（`report.completed`、`version.update`、`system.announcement`） |
| `title` | string | ✅ | 通知标题 |
| `body` | string | ✅ | 通知正文 |
| `action` | object | ❌ | 用户点击通知后的行为（跳转路由等） |
| `priority` | string | ❌ | 优先级：`low` / `normal` / `high`，默认 `normal` |

#### 4.4.10 error（双向）

协议层错误消息。服务端在消息格式校验失败、路由失败时返回。客户端可在检测到异常时发送。

```json
{
  "type": "error",
  "message_id": "msg_j0k1l2m3",
  "timestamp": "2026-07-08T12:00:00Z",
  "data": {
    "code": 30001,
    "message": "无效的消息类型: 'chat.messsage'",
    "original_message_id": "msg_a1b2c3d4"
  }
}
```

#### 4.4.11 heartbeat.ping / heartbeat.pong（双向）

```json
// 客户端 → 服务端
{
  "type": "heartbeat.ping",
  "message_id": "msg_k1l2m3n4",
  "timestamp": "2026-07-08T12:00:30Z",
  "data": {}
}

// 服务端 → 客户端
{
  "type": "heartbeat.pong",
  "message_id": "msg_l2m3n4o5",
  "timestamp": "2026-07-08T12:00:30Z",
  "data": {}
}
```

### 4.5 消息确认机制

对于关键消息（如 `chat.message`），服务端处理完成后应返回对应的确认消息：

```
客户端发送 chat.message (message_id: msg_001)
    ↓
服务端开始处理，先返回空帧作为 ACK（可选）
    ↓
服务端流式推送 ai.token (引用 session_id)
    ↓
服务端推送 ai.done (引用 session_id) ← 等同于 chat.message 的处理完成确认
```

- **客户端责任：** 为每条上行消息生成唯一 `message_id`
- **服务端责任：** 为每条下行消息生成唯一 `message_id`
- **去重策略：** 服务端缓存最近 50 条收到的 `message_id`，重复消息直接丢弃

---

## 5. 任务流程

### 5.1 八字分析完整时序

以用户提交八字分析请求为例，展示 HTTP + WebSocket 全流程协作：

```
用户                     客户端                 核心服务                  AI Pipeline
 │                        │                      │                        │
 │ ① 填写出生信息          │                      │                        │
 │──────────────────────→ │                      │                        │
 │                        │                      │                        │
 │                        │ ② POST /bazi/charts  │                        │
 │                        │─────────────────────→│                        │
 │                        │   返回 chart_id      │                        │
 │                        │←─────────────────────│                        │
 │                        │                      │                        │
 │                        │ ③ POST .../analysis  │                        │
 │                        │─────────────────────→│                        │
 │                        │  202 + task_id       │                        │
 │                        │←─────────────────────│                        │
 │                        │                      │                        │
 │                        │ ④ WS connect         │                        │
 │                        │ /ws/v1/session       │                        │
 │                        │═════════════════════→│                        │
 │                        │                      │                        │
 │                        │ ⑤ task.created       │                        │
 │                        │←═════════════════════│                        │
 │                        │                      │                        │
 │                        │ ⑥ task.progress(10)  │                        │
 │                        │←═════════════════════│──── Stage 1: 数据解析 ──→│
 │                        │  "数据解析完成"       │                        │
 │                        │                      │                        │
 │                        │ ⑦ task.progress(30)  │                        │
 │                        │←═════════════════════│──── Stage 2: 四柱计算 ──→│
 │                        │  "四柱计算完成"       │                        │
 │                        │                      │                        │
 │                        │ ⑧ task.progress(50)  │                        │
 │                        │←═════════════════════│──── Stage 3: 五行分析 ──→│
 │                        │  "五行分析完成"       │                        │
 │                        │                      │                        │
 │                        │ ⑨ task.progress(70)  │                        │
 │                        │←═════════════════════│──── Stage 4: AI推理 ────→│
 │                        │  "AI推理中..."       │                        │
 │                        │                      │                        │
 │                        │ ⑩ task.progress(90)  │                        │
 │                        │←═════════════════════│──── Stage 5: 报告生成 ──→│
 │                        │  "报告生成中..."     │                        │
 │                        │                      │                        │
 │                        │ ⑪ task.completed     │                        │
 │                        │←═════════════════════│                        │
 │                        │                      │                        │
 │ ⑫ 显示结果             │                      │                        │
 │←──────────────────────│                      │                        │
```

### 5.2 分析阶段定义

| 阶段编号 | 阶段标识 | 阶段名称 | progress 范围 | 描述 | 耗时估计 |
|----------|----------|----------|---------------|------|----------|
| 1 | `data_parsing` | 数据解析 | 1-10 | 验证出生信息、格式化输入、时区校准 | ~1s |
| 2 | `four_pillars` | 四柱计算 | 11-30 | 排年/月/日/时柱、藏干、空亡、纳音 | ~2s |
| 3 | `five_elements` | 五行分析 | 31-50 | 旺衰判定、用神忌神、格局识别 | ~3s |
| 4 | `ai_inference` | AI 推理 | 51-70 | LLM 深度分析（调用云端 API） | ~15-30s |
| 5 | `report_gen` | 报告生成 | 71-90 | 结构化输出、数据层级标注、格式化 | ~3s |
| - | `completed` | 完成 | 100 | 任务完成 | - |

### 5.3 对话式分析流程（WebSocket 专属）

用户可以通过 `/ws/v1/session` 直接在对话中触发分析，无需先走 HTTP：

```
用户                   客户端                      核心服务
 │                      │                           │
 │ ① chat.message       │                           │
 │ "分析我的八字"        │                           │
 │─────────────────────→│                           │
 │                      │ ② 判断需要创建任务           │
 │                      │ ③ 内部调用排盘 + AI 分析    │
 │                      │                           │
 │                      │ ④ ai.token (逐Token)       │
 │                      │←══════════════════════════│
 │                      │  ...                       │
 │                      │ ⑤ ai.done                  │
 │                      │←══════════════════════════│
 │                      │                           │
 │ ⑥ 看到实时回复        │                           │
 │←─────────────────────│                           │
```

此模式不需要显式的 `task.created/progress/completed` 消息，而是通过 `ai.token` → `ai.done` 完成。

### 5.4 任务状态机

```
                  ┌──────────┐
                  │  pending  │   任务已创建，等待执行
                  └─────┬────┘
                        │
                  ┌─────▼──────┐
          ┌──────│ processing  │─── 任务正在执行，持续推送 progress
          │      └──────┬──────┘
          │             │
     ┌────┴────┐  ┌────┴────┐  ┌──────────┐
     │         │  │         │  │          │
  ┌──▼──┐  ┌───┴──┐  ┌───▼──┐  ┌──▼───────┐
  │cancelled│completed│ failed │  │timed_out │
  └────────┘ └──────┘ └──────┘  └──────────┘
```

| 状态 | 可推送消息 | 说明 |
|------|-----------|------|
| `pending` | `task.created` | 任务已入队 |
| `processing` | `task.progress`（多次） | 执行中 |
| `completed` | `task.completed` | 成功结束 |
| `failed` | `task.failed` | 执行失败 |
| `cancelled` | `task.cancelled` | 被用户取消 |
| `timed_out` | `task.failed` | 超时终止 |

---

## 6. 异常处理

### 6.1 断线重连机制

```
客户端检测到连接断开
    │
    ├── 主动关闭（用户退出） → 不重连
    │
    └── 被动断开（网络异常/服务端重启）
        │
        ▼
    等待 1s → 尝试重连
        │
    ┌───┴───┐
    │ 成功   │ 失败
    │        ▼
    │     等待 2s → 尝试重连
    │        │
    │    ┌───┴───┐
    │    │ 成功   │ 失败
    │    │        ▼
    │    │     等待 4s → 尝试重连（以此类推，最大 30s）
    │    │        │
    │    │    ┌───┴───┐
    │    │    │ 成功   │ 继续重试（最多 10 次）
    │    │    │        ▼
    │    │    │     放弃重连，提示用户
    │    │    │
    ▼    ▼    ▼
    恢复连接
        │
        ▼
    发送 resume 请求 → 服务端返回当前未完成任务列表
        │
        ▼
    客户端重新订阅活跃任务 → 继续接收进度推送
```

**重连参数：**

| 参数 | 值 | 说明 |
|------|-----|------|
| 初始延迟 | 1s | 首次重连等待时间 |
| 退避因子 | 2 | 每次失败延迟翻倍 |
| 最大延迟 | 30s | 单次重连等待上限 |
| 最大重试次数 | 10 | 超过后放弃，提示用户手动刷新 |
| 抖动 | ±500ms | 随机抖动防止惊群 |

### 6.2 任务恢复机制

重连后客户端需要恢复正在执行的任务。

**方案：客户端主动查询 + 服务端增量推送**

```
客户端重连成功
    │
    ▼
发送 { "type": "task.resume", "data": {} }
    │
    ▼
服务端返回未完成的任务列表：
{
  "type": "task.list",
  "data": {
    "active_tasks": [
      { "task_id": "...", "status": "processing", "progress": 60, "stage": "ai_inference" }
    ]
  }
}
    │
    ▼
客户端重新订阅每个活跃任务的进度推送
    │
    ▼
服务端继续推送 task.progress
```

**消息确认与断点续传：**

- 服务端为每个连接维护单调递增的 `sequence` 计数器，每条下行消息携带当前序列号
- 服务端缓存最近 N 条已发送消息（N 可配置，建议 20），按 `sequence` 索引
- 客户端重连时在 `task.resume` 中携带 `last_sequence` 参数，服务端根据序号间隙重放缺失消息
- 客户端收到重放消息后，与重连后收到的实时消息按 `sequence` 排序合并
- 如果缓存的旧消息已被丢弃，服务端返回当前最新进度快照，客户端以快照为准

```
客户端重连成功
    │
    ▼
发送 { "type": "task.resume", "data": { "last_sequence": 7 } }
    │
    ▼
服务端检查缓存：
    │  ┌─── seq 8, 9, 10 仍在缓存中 → 重放 seq 8, 9, 10
    │  ├─── 缓存已过期（seq >7 的消息已被丢弃）→ 返回当前最新进度快照
    │  └─── 无活跃任务 → 返回空列表
    │
    ▼
客户端补全消息序列，继续接收实时推送
```

### 6.3 消息可靠性

| 场景 | 处理策略 |
|------|----------|
| **消息丢失** | 每条消息携带 `sequence` 序号，客户端检测到序号跳跃时发送 `retry.request` 请求重传缺失消息 |
| **消息重复** | 客户端和服务端各自缓存最近 50 条 `message_id`，重复消息静默丢弃 |
| **消息乱序** | 每次 `ai.token` 携带 `index` 字段，客户端按 `index` 拼接 |
| **消息格式错误** | 服务端返回 `error` 消息（含 `original_message_id`），不中断连接 |

### 6.4 超时处理

| 超时类型 | 阈值 | 处理动作 |
|----------|------|----------|
| 连接建立超时 | 10s | 客户端放弃连接，触发重连 |
| Token 验证超时 | 5s | 服务端关闭连接，返回错误码 |
| 消息处理超时 | 30s | 服务端返回 `ai.error`（`code: 10003`） |
| 任务执行超时 | 300s（5min） | 任务标记为 `timed_out`，推送 `task.failed` |
| 心跳空闲超时 | 90s | 服务端关闭连接，客户端触发重连 |

---

## 7. 安全策略

### 7.1 连接鉴权

所有 WebSocket 连接必须携带有效的 JWT Token 进行鉴权。

**建立连接时的鉴权流程：**

```
客户端                         服务端
  │                              │
  │ ws://...?token=xxx           │
  │─────────────────────────────→│
  │                              │ ① 解析 JWT Token
  │                              │ ② 验证签名 + 有效期
  │                              │ ③ 从 Token 中提取 user_id
  │                              │
  │← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│ ④ 成功：WebSocket 连接建立
  │  或
  │← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─│ ④ 失败：HTTP 401，连接拒绝
```

**Token 规范：**

| 项目 | 规范 |
|------|------|
| Token 类型 | JWT |
| 签名算法 | HS256 |
| 有效载荷 | `user_id`, `username`, `role`, `iat`, `exp` |
| 有效期 | 24 小时 |
| 传输方式 | URL Query Parameter: `?token=<jwt_token>` |

### 7.2 消息校验

| 校验维度 | 规则 | 违反处理 |
|----------|------|----------|
| **JSON 格式** | 消息必须是合法的 UTF-8 JSON | 返回 `error`（code: 30001），保留连接 |
| **消息类型** | `type` 字段必须是已定义的消息类型之一 | 返回 `error`（code: 30001），保留连接 |
| **必填字段** | 各消息类型的必填字段必须存在 | 返回 `error`（code: 30002），保留连接 |
| **字段类型** | 字段值类型必须匹配定义 | 返回 `error`（code: 30002），保留连接 |
| **消息大小** | 单条消息不超过 1MB | 关闭连接（code: 30003） |

### 7.3 速率限制

| 限制项 | 限制值 | 违反处理 |
|--------|--------|----------|
| 单用户连接数 | 最多 3 个活跃连接 | 拒绝新连接（返回 60001） |
| 消息发送频率 | 每秒最多 10 条上行消息 | 返回 `error`（code: 60001），持续超限则关闭连接 |
| 心跳间隔 | 最少 10s，最多 60s | 超出范围时服务端忽略异常心跳 |

### 7.4 防止重复任务

| 场景 | 防护策略 |
|------|----------|
| 同一用户重复提交相同分析 | 5 分钟内相同的 `chart_id + analysis_type` 判定为重复，返回已有 `task_id` |
| 同任务多客户端订阅 | 允许多个连接同时订阅同一个 `task_id` 的进度推送 |
| 服务端重启后重复任务 | 重启后清空内存中任务状态，客户端通过 `task.resume` 重新同步 |

### 7.5 敏感信息保护

| 数据类型 | 保护措施 |
|----------|----------|
| 用户出生信息 | 在日志中脱敏（只保留年份，隐藏月/日/时） |
| 对话内容 | 不在 WebSocket 日志中持久化完整对话文本 |
| Token | 不在日志中记录 Token 全文，仅记录前 10 字符 |
| 分析结果 | 只通过 WebSocket 推送给本人，不做广播 |

### 7.6 连接关闭原因码

服务端在关闭 WebSocket 连接时，使用 WebSocket 标准 Close 帧的 `code` 和 `reason` 字段说明关闭原因：

| 场景 | 状态码 | reason |
|------|--------|--------|
| 正常关闭 | 1000 | Normal closure |
| Token 过期 | 4001 | Token expired |
| 鉴权失败 | 4002 | Authentication failed |
| 连接数超限 | 4003 | Too many connections |
| 服务端关闭 | 4004 | Server shutting down |
| 消息超限 | 4005 | Rate limit exceeded |
| 协议错误 | 4006 | Protocol error |

---

## 8. 未来扩展

### 8.1 多 Agent 推送

当前单 Agent 架构（ADR-016）下，所有 AI 回复通过同一通道推送。未来拆分为多 Agent 后，协议层需要支持按 Agent 维度路由消息。

```
当前：
  ai.token → 统一推送（不区分 Agent）

未来：
  ai.token → 可携带 agent_id 字段
  客户端根据 agent_id 在 UI 中分别展示
```

**协议扩展方式：** 在 `data` 中增加可选字段 `agent_id`，现有客户端忽略即可。

### 8.2 广播通道

V1 的单一连接设计下，通知通过 `notification.system` 消息类型在同一连接中推送。未来需要运营级广播能力时，可引入独立广播路径：

| 路径 | 用途 |
|------|------|
| `/ws/v1/broadcast/system` | 系统级广播（未来） |
| `/ws/v1/broadcast/marketing` | 运营推送（未来） |

### 8.3 消息压缩

当消息体较大（如批量推送、长文本分析报告）时，可启用消息压缩：

| 阶段 | 压缩策略 | 说明 |
|------|----------|------|
| V1 | 无压缩 | 文本帧直接传输，AI Token 每次 1-10 字符，无需压缩 |
| V2 | 可选 gzip | 客户端在连接参数中声明 `compress=gzip`，服务端对大消息（>4KB）启用压缩 |
| V3 | 二进制帧 | 使用 Protocol Buffers 替代 JSON，适用于高频场景 |

### 8.4 多通道分离（未来扩展）

V1 采用**单一连接**设计（`/ws/v1/session`），所有消息类型通过 `type` 字段在一条连接中区分。未来如果遇到以下场景，可拆分为多条专用连接：

| 场景 | 触发条件 | 拆分方案 |
|------|----------|----------|
| **高负载对话** | 单连接 Token 流式输出影响任务通知的实时性 | 分离出 `/ws/v1/chat` 专用连接 |
| **多任务并行** | 用户同时订阅多个长任务进度 | 分离出 `/ws/v1/task/{task_id}` 动态连接 |
| **运营推送频道** | 通知消息量级大幅增长 | 分离出 `/ws/v1/notification` 独立通道 |

```
V1（当前）：单一连接，type 区分
  ┌─────────┐     /ws/v1/session        ┌─────────┐
  │ 客户端   │  ══════════════════════════ │ 服务端   │
  │         │  type: chat.message       │         │
  │         │  type: task.subscribe     │         │
  │         │  type: notification.sub   │         │
  └─────────┘                           └─────────┘

V2（可选扩展）：多连接分离
  ┌─────────┐     /ws/v1/chat          ┌─────────┐
  │ 客户端   │  ═══ /ws/v1/task/{id} ═══ │ 服务端   │
  │         │     /ws/v1/notification   │         │
  └─────────┘                           └─────────┘
```

### 8.5 与 HTTP API 的关系总结

| 维度 | HTTP API | WebSocket |
|------|----------|-----------|
| **通信模式** | 请求/响应 | 全双工，双向推送 |
| **主要用途** | CRUD、资源操作、同步查询 | 实时对话、流式输出、状态推送 |
| **消息格式** | JSON（标准响应体包裹） | JSON（轻量帧格式） |
| **鉴权方式** | `Authorization: Bearer <token>` | URL Query `?token=<jwt_token>` |
| **状态管理** | 无状态 | 有状态（服务端维护连接映射） |
| **错误处理** | HTTP 状态码 + 错误码 | Close 帧 + `error` 消息 |
| **扩展方向** | 资源维度扩展 | 通道维度扩展 |

---

## 附：变更记录

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v0.1 | 2026-07-08 | 初版 Draft，定义 WebSocket 实时通信协议完整设计 |
