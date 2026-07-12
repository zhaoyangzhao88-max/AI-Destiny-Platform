# 22 — Phase 3 Development Plan（开发执行计划）

> **版本:** v3.0 | **日期:** 2026-07-11 | **状态:** ✅ Approved
>
> **角色:** Documentation Engineer — 基于 Project Architect v2.0 重构，新增 Iteration/Workflow/Change Mgmt/Review Checklist
>
> **关联文档:** [08_系统架构](./08_系统架构设计.md) | [13_API接口契约](./13_API接口契约设计.md) | [14_WS协议](./14_WebSocket实时通信协议设计.md) | [19_分层记忆架构](./19_分层记忆架构设计.md) | [21_架构冻结声明](./21_Architecture_Freeze_Declaration.md) | [04_ADR](./04_ADR_产品决策记录.md)

---

## 1. Executive Summary

知命 AI 人生档案顾问，Phase 3（编码实施期）正式启动。架构基线已冻结，6 项 P0 已关闭，剩余 17 P1 + 9 P2 待跟踪。

| 指标 | 数值 |
|------|:----:|
| Sub-Phase | **4**（3.1~3.4）|
| Epic | **18** |
| Iteration | 每个 Epic 拆分为 **3~6** 个 Iteration |
| Milestone | **5**（M1~M5）|
| 开发模式 | 串行链 + 并行组，以 **Iteration 为最小推进单元** |

**核心约束：**
- 🧊 Architecture Freeze 不可违反
- 📜 API Contract 不可修改（34 HTTP endpoint + 17 WS 消息类型）
- ⛔ 13 条 Frozen ADR 不可绕过

---

## 2. Development Principles

### 2.1 禁止修改的冻结内容

| 类别 | 文件 | 冻结范围 |
|------|------|---------|
| 架构设计 | docs/08 | 系统分层、模块划分、部署拓扑 |
| ADR Baseline | ADR-001~012 / ADR-020 | 决策内容（不禁止新增 ADR） |
| API 契约 | docs/13 | HTTP endpoint、数据模型、状态码 |
| WS 协议 | docs/14 | 连接路径、消息类型表、心跳机制 |
| 数据契约 | ADR-012 / docs/19 | 三层体系 / 三层记忆模型 |
| 风险基线 | docs/18 | 等级标准、关闭流程 |

### 2.2 Frozen ADR 约束速查

| ADR | 约束 |
|-----|------|
| ADR-001~003 | 产品定位 / 用户分层 / 免费+付费 |
| ADR-004 / 010 | 知命角色设定 / 融合型欢迎语 |
| ADR-005~006 | 东方科技融合风 / 数字东方书院 |
| ADR-007~008 | 首页双核心 / 信息采集混合模式 |
| ADR-009 | 八字分析 6 步流程 |
| ADR-011 | 出生时间允许未知 |
| ADR-012 | 三层数据（Fact / Inference / Pending）|
| ADR-020 | PySide6 + Vue（QWebEngineView 嵌入式）|

Draft ADR（014~019）仅作方向参考，不作为约束性依据。

---

## 3. Development Roadmap

### 3.1 四个子阶段

```
Phase 3.1          Phase 3.2          Phase 3.3          Phase 3.4
Foundation         Business Logic     AI & Intelligence   Frontend & MVP
E-BOOT             E-BAZI             E-AI                E-GUI
E-INFRA            E-RULE             E-PROMPT            E-VUE
E-DB               E-SVC              E-MEM               E-TEST
E-REPO             E-API (HTTP)       E-TASK              E-PKG
E-DOMAIN             ↓                E-API (WS)          E-DOC
    ↓                   ↓                   ↓                   ↓
   M1                  M2                  M3                  M4
Foundation         API Core           AI Pipeline         Client
Ready              Complete           Functional          Integrated
                                                                ↓
                                                               M5
                                                            MVP Release
```

### 3.2 Phase 3.1 — Foundation

| Epic | Task 数 | 作用 |
|------|:-------:|------|
| E-BOOT | 5 | 项目骨架、配置、日志、异常 |
| E-INFRA | 4 | FastAPI 工厂、中间件、DI |
| E-DB | 4 | SQLite Schema、Alembic 迁移 |
| E-REPO | 6 | 数据访问层（6 Repo）|
| E-DOMAIN | 3 | 领域实体、值对象、状态机 |

**完成标志：** FastAPI 启动 → `GET /api/v1/config/health` → 200 OK + DB 可读写

### 3.3 Phase 3.2 — Business Logic

| Epic | Task 数 | 作用 |
|------|:-------:|------|
| E-BAZI | 5 | 四柱排盘算法（含黄金数据集）|
| E-RULE | 3 | 命理规则推理 |
| E-SVC | 6 | 业务编排（6 Service）|
| E-API (HTTP) | 8 | 34+ HTTP 端点全实现 |

**完成标志：** 注册→登录→排盘→分析→报告 完整链路通过

### 3.4 Phase 3.3 — AI & Intelligence

| Epic | Task 数 | 作用 |
|------|:-------:|------|
| E-AI | 5 | LLM Provider + Agent 编排 |
| E-PROMPT | 4 | Prompt 模板 + 知命角色 |
| E-MEM | 4 | 三层记忆（工作/摘要/核心）|
| E-TASK | 3 | 长任务状态机 + 进度推送 |
| E-API (WS) | 2 | WebSocket 链路 |

**完成标志：** WS 连接 → `chat.message` → `ai.token` 流 → `ai.done` 完成

### 3.5 Phase 3.4 — Frontend & MVP

| Epic | Task 数 | 作用 |
|------|:-------:|------|
| E-GUI | 6 | PySide6 外壳 + 进程管理 |
| E-VUE | 5 | Vue 渐进式 UI |
| E-TEST | 4 | 测试框架 + 黄金数据集 |
| E-PKG | 3 | 打包 + 安装程序 |
| E-DOC | 2 | 开发/部署文档 |

**完成标志：** 全新 Windows 环境→安装→注册→排盘→AI 分析→报告

---

## 4. Milestones + Architecture Review Gate

每个 Milestone 完成后 **必须暂停**，通过 Architecture Review Gate 后方可进入下一 Milestone。

### 4.1 里程碑总览

```
M1 ──[GATE]── M2 ──[GATE]── M3 ──[GATE]── M4 ──[GATE]── M5

Gate 内容：CTO Review + Architecture Compliance Review + Risk Review
```

### 4.2 M1 — Foundation Ready

| 项目 | 内容 |
|------|------|
| **进入条件** | Phase 3 已批准启动 |
| **完成条件** | FastAPI 启动 + Health 200 + DB 可读写 + 全部 Repo 可注入 |
| **交付物** | 项目骨架、DB Schema、6 Repo、Domain Models |
| **验证** | `curl localhost:8000/api/v1/config/health` → `{"status":"healthy"}` |

### 4.3 M2 — API Complete

| 项目 | 内容 |
|------|------|
| **进入条件** | M1 完成且 Gate 通过 |
| **完成条件** | 34 HTTP 端点 + 排盘引擎（黄金数据集 100%）+ 错误码体系完整 |
| **交付物** | 全部 API 路由 + Service 层 + 排盘引擎 |
| **验证** | 注册→登录→排盘 链路通过 |

### 4.4 M3 — AI Pipeline Functional

| 项目 | 内容 |
|------|------|
| **进入条件** | M2 完成且 Gate 通过 |
| **完成条件** | WS 流式对话 + 6 步分析 + 记忆系统 + 长任务推送 |
| **交付物** | AI/Prompt/Memory/Task/WS 全部引擎 |
| **验证** | WS `chat.message` → `ai.token` → `ai.done` 完整链路 |

### 4.5 M4 — Client Integrated

| 项目 | 内容 |
|------|------|
| **进入条件** | M3 完成且 Gate 通过 |
| **完成条件** | PySide6 启动 + Vue 5 页面渲染 + 核心服务自管理 |
| **交付物** | 桌面应用（PySide6 + Vue 集成）|
| **验证** | 启动 APP → 自动拉起核心服务 → 全流程操作 |

### 4.6 M5 — MVP Release

| 项目 | 内容 |
|------|------|
| **进入条件** | M4 完成且 Gate 通过 |
| **完成条件** | 安装程序可安装 + 覆盖率 ≥ 80% + E2E 通过 + 关闭 10+ 风险 |
| **交付物** | 安装程序（exe）+ 测试报告 + 交接文档 |
| **验证** | 干净 Windows 环境完整用户旅程 |

### 4.7 Architecture Review Gate 规则

| 维度 | 内容 |
|------|------|
| **参与者** | CTO (ChatGPT Chief Architect)、Claude Code Agent、Product Owner |
| **检查项** | (1) Architecture Compliance — 无 Freeze 违反<br>(2) Risk Review — 无新增 P0 风险<br>(3) CTO Approval — 设计质量满足标准 |
| **阻断条件** | 任何一项未通过 → 退回修复 → 重新 Gate |
| **未通过后果** | 禁止进入下一 Milestone |
| **记录** | 每次 Gate 结果记录到 `docs/11_AI协作日志.md` |

---

## 5. Epic → Iteration → Task

### 5.1 三层架构职责

| 层级 | 职责 | 粒度和控制目标 |
|------|------|---------------|
| **Epic** | 功能域（如排盘引擎、Prompt 引擎）| 边界控制，关联 ADR，定义范围/非范围 |
| **Iteration** | 每个 Epic 内部的开发小步 | **最小推进单元**，每次一个独立可验证的目标 |
| **Task** | Iteration 内的具体执行步骤 | Claude Code 一次会话可完成，是 git commit 和 Code Review 的最小单位 |

**所有开发默认以 Iteration 为单位推进。一次只开发一个 Iteration，完成并通过 Review 后才进入下一个。**

### 5.2 示例：E-INFRA（Infrastructure）

| Iteration | 目标 | 说明 |
|-----------|------|------|
| **Iteration 1** | FastAPI App | 应用工厂、Lifespan 管理、路由注册 |
| **Iteration 2** | Configuration | pydantic-settings、多环境配置、.env 加载 |
| **Iteration 3** | Logging | structlog、级别/格式/轮转、请求 ID 传播 |
| **Iteration 4** | Dependency Injection | DI 容器、Service/Repo 注册 |
| **Iteration 5** | Middleware | CORS、Auth、RateLimit、Global Error Handler |

每个 Iteration = 1 个 Claude Code Prompt → 编码 → 测试 → Review → 通过后继续。

### 5.3 Epic 总表

| ID | 名称 | 所属 Phase | Iteration 数 | 关联 ADR |
|----|------|:----------:|:------------:|----------|
| E-BOOT | Bootstrap | 3.1 | 5 | ADR-017, 019 |
| E-INFRA | Infrastructure | 3.1 | 5 | ADR-017, 019 |
| E-DB | Database | 3.1 | 4 | ADR-012, 013 |
| E-REPO | Repository | 3.1 | 6 | ADR-012, 013 |
| E-DOMAIN | Domain Models | 3.1 | 3 | ADR-009, 012 |
| E-BAZI | Bazi Engine | 3.2 | 5 | ADR-009, 011 |
| E-RULE | Rule Engine | 3.2 | 3 | ADR-009 |
| E-SVC | Service Layer | 3.2 | 6 | ADR-009, 017 |
| E-API (HTTP) | API Layer — HTTP | 3.2 | 8 | ADR-019 |
| E-AI | AI Agent Engine | 3.3 | 5 | ADR-009, 016 |
| E-PROMPT | Prompt Engine | 3.3 | 4 | ADR-004, 009, 010 |
| E-MEM | Memory Engine | 3.3 | 4 | ADR-012, docs/19 |
| E-TASK | Task Engine | 3.3 | 3 | ADR-009, docs/14 |
| E-API (WS) | API Layer — WS | 3.3 | 2 | ADR-019 |
| E-GUI | GUI Client | 3.4 | 6 | ADR-018, 020 |
| E-VUE | Vue UI | 3.4 | 5 | ADR-018, 020 |
| E-TEST | Testing | 3.4 | 4 | — |
| E-PKG | Packaging | 3.4 | 3 | ADR-017, 018 |
| E-DOC | Documentation | 3.4 | 2 | — |

### 5.4 各 Epic 的详细 Iteration 清单

> 每个 Iteration 包含 1~3 个 Task。Task 是 Claude Code 单次会话的编码单位。

| Epic | Iteration | Task 示例 |
|------|-----------|-----------|
| **E-BOOT** | I1: 目录结构 + pyproject.toml | BOOT-01: 创建目录、pyproject.toml、.env.example |
| | I2: 配置系统 | BOOT-02: pydantic-settings |
| | I3: 日志系统 | BOOT-03: structlog 配置 |
| | I4: 工具模块 | BOOT-04: 时间/ID/JSON 工具 |
| | I5: 异常体系 | BOOT-05: Exception 层次 + 全局处理器 |
| **E-INFRA** | I1: FastAPI App | INFRA-01: create_app + lifespan |
| | I2: Configuration | INFRA-02 部分: pydantic-settings |
| | I3: Logging | INFRA-02 部分: structlog 集成 |
| | I4: Dependency Injection | INFRA-03: DI 容器 |
| | I5: Middleware | INFRA-02 + INFRA-04: 中间件 + health |
| **E-DB** | I1: 引擎 + 迁移 | DB-01: SQLAlchemy + Alembic |
| | I2: User + Profile | DB-02: 用户和档案模型 |
| | I3: Bazi + Report | DB-03: 排盘和报告模型 |
| | I4: Task + 偏好 + 术语 | DB-04: 任务/偏好/术语模型 |
| **E-REPO** | I1: BaseRepository | REPO-01: 通用 CRUD + 分页 |
| | I2: UserRepo | REPO-02 |
| | I3: BaziChartRepo | REPO-03 |
| | I4: ProfileRepo | REPO-04 (含 data_tier) |
| | I5: ReportRepo | REPO-05 (含版本) |
| | I6: Task + Pref + Term | REPO-06 |
| **E-DOMAIN** | I1: 核心实体 | DOMAIN-01: User/BaziChart/Report 实体 |
| | I2: 值对象 | DOMAIN-02: Pillar/FiveElements/TenGod/DataTier |
| | I3: 状态机 | DOMAIN-03: Task/Analysis/DataTier 状态机 |
| **E-BAZI** | I1: 天干地支基础 | BAZI-01 |
| | I2: 四柱计算 | BAZI-02 |
| | I3: 五行 + 十神 | BAZI-03 |
| | I4: 大运流年 | BAZI-04 |
| | I5: 接口 + 黄金数据集 | BAZI-05 |
| **E-RULE** | I1: 格局规则库 | RULE-01 |
| | I2: 规则匹配引擎 | RULE-02 |
| | I3: 集成到流水线 | RULE-03 |
| **E-AI** | I1: LLM Provider | AI-01 |
| | I2: 调用管理 | AI-02 (超时/重试/流式) |
| | I3: Agent 核心 | AI-03 (上下文/历史/会话) |
| | I4: 6 步流水线 | AI-04 (ADR-009 分析流程) |
| | I5: 错误降级 | AI-05 |
| **E-PROMPT** | I1: 模板系统 | PROMPT-01 |
| | I2: 角色提示词 | PROMPT-02 (知命 persona) |
| | I3: 分析提示词 | PROMPT-03 (八字/格局/报告) |
| | I4: 追问+记忆提示词 | PROMPT-04 |
| **E-MEM** | I1: 工作记忆 | MEM-01 |
| | I2: 摘要记忆 | MEM-02 |
| | I3: 核心记忆 | MEM-03 |
| | I4: 上下文注入 | MEM-04 |
| **E-TASK** | I1: 状态机 + 生命周期 | TASK-01 |
| | I2: 进度追踪 | TASK-02 |
| | I3: 断线恢复 + 去重 | TASK-03 |
| **E-API(HTTP)** | I1: 路由框架 | API-01/06/08 部分 |
| | I2: User 路由 | API-01 (9 端点) |
| | I3: Bazi 路由 | API-02 (8 端点) |
| | I4: Report 路由 | API-03 (6 端点) |
| | I5: Task+Knowledge+Config | API-04 (11 端点) |
| | I6: Pydantic Schemas | API-05 |
| | I7: 响应格式化 + 错误码 | API-06 + API-07 |
| | I8: 分页/排序/过滤 | API-08 |
| **E-API(WS)** | I1: 连接管理 | API-09 (connect/auth/heartbeat) |
| | I2: 业务消息 | API-10 (chat + task 推送 + resume) |
| **E-GUI** | I1: PySide6 外壳 | GUI-01 (窗口/托盘/菜单) |
| | I2: 进程管理器 | GUI-02 (核心服务生命周期) |
| | I3: API Client 层 | GUI-03 (HTTP + WS Client) |
| | I4: 原生界面 | GUI-04 (登录/首页/设置) |
| | I5: WebChannel 集成 | GUI-05 (QWebEngineView) |
| | I6: 生命周期 + 更新 | GUI-06 |
| **E-VUE** | I1: 脚手架 + 服务层 | VUE-01 (Vite/Router/Pinia/API Client) |
| | I2: 聊天界面 | VUE-02 |
| | I3: 命盘展示 | VUE-03 |
| | I4: 报告查看器 | VUE-04 |
| | I5: 设置页面 | VUE-05 |
| **E-TEST** | I1: 测试基础设施 | TEST-01 |
| | I2: 单元测试 | TEST-02 |
| | I3: 集成测试 | TEST-03 |
| | I4: 黄金数据集回归 | TEST-04 |
| **E-PKG** | I1: PyInstaller 打包 | PKG-01 |
| | I2: 安装程序 | PKG-02 |
| | I3: 版本管理 | PKG-03 |
| **E-DOC** | I1: 开发者指南 | DOC-01 |
| | I2: 部署手册 | DOC-02 |

---

## 6. Development Workflow

### 6.1 角色与职责

| 角色 | 谁担任 | 职责 |
|------|--------|------|
| **Chief Architect / CTO** | ChatGPT | 制定目标、生成 Claude Code Prompt、审查结果、掌控 Architecture Gate |
| **Developer** | Claude Code | 读取文档、执行编码、测试、输出 Execution Report |
| **Product Owner** | 产品负责人 | 确认任务优先级、批准架构变更、签署 Milestone |

### 6.2 Iteration 标准工作流

```
[Chief Architect / CTO]
        │ ① 制定本次 Iteration 目标
        │ ② 生成 Claude Code Prompt（含需要读取的文档 + 修改范围 + 约束条件）
        ▼
[Claude Code]
        │ ③ 读取相关基线文档（docs/08/13/14/19/04 等）
        │ ④ 执行代码修改
        │ ⑤ Lint 检查（ruff check .）
        │ ⑥ 测试（pytest）
        │ ⑦ 生成 Execution Report（做了什么/改了哪些文件/是否违反 Freeze/风险记录）
        ▼
[Chief Architect / CTO]
        │ ⑧ ChatGPT Review（检查修改质量、Freeze 合规、ADR 一致性）
        │ ⑨ Architecture Gate（是否通过）
        │
        ├── ✅ 通过 → 进入下一 Iteration
        └── ❌ 不通过 → 退回 Claude Code 修复 → 重新 Review
```

### 6.3 Execution Report 的意义

每次 Claude Code 执行完成后必须输出 Execution Report，包含：

| 字段 | 说明 |
|------|------|
| Iteration ID | 如 `E-INFRA-I1` |
| 执行内容 | 本次做了什么 |
| 修改文件 | 创建/修改的文件列表 |
| Architecture Freeze 检查 | 是否违反 R1~R8 |
| ADR 合规检查 | 是否违反相关 ADR |
| 遗留问题 | 未解决的事项 |
| 建议 | 对下一步的建议 |

Report 写入协作日志（`docs/11_AI协作日志.md`），作为 Code Review 和 Gate 判断的依据。

### 6.4 Architecture Gate 的意义

- **防止累积错误：** 每次 Iteration 完成后立即检查，错误不积累
- **Freeze 保障：** 每个 Iteration 都验证一次是否违反冻结基线
- **质量门禁：** 不通过 Gate → 禁止进入下一 Iteration
- **风险预警：** 早期发现架构偏离或设计缺陷

---

## 7. Change Management

### 7.1 允许与禁止速查

| 类别 | 允许 ✅ | 禁止 ❌ |
|------|---------|---------|
| **代码修改** | 新增代码、Bug 修复、单元测试 | 修改冻结的架构/API/WS 定义 |
| **文档修改** | 本文档更新、协作日志、开发指南 | 修改 docs/08/13/14/19/21 冻结内容 |
| **日志** | 日志完善、调试信息增加 | 日志中暴露用户敏感信息 |
| **配置** | env 配置、开发环境参数 | 修改技术选型（Python/FastAPI/SQLite 等）|
| **ADR** | 新增 Draft ADR（需走流程）| 修改已批准的 ADR-001~012/020 |
| **API** | 新增可选字段、新增端点（不修改已有）| 修改/删除/重命名已有 endpoint 或字段 |
| **WS** | 实现细节优化（不改变协议定义）| 修改消息 type、data 结构、连接路径 |
| **数据模型** | 数据库索引优化、查询优化 | 修改 Fact/Inference/Pending 三层定义 |

### 7.2 如果确实需要修改冻结内容

必须按以下流程执行：

```
① 提出 Change Request
    └─→ 描述：修改背景、原因、影响范围、备选方案
② 新增/更新 ADR
    └─→ 记录变更内容、技术方案、影响分析
③ CTO Review
    └─→ 评估架构兼容性、风险等级
④ Product Owner Approval
    └─→ PO 签署确认
⑤ Architecture Freeze 更新
    └─→ 批准后更新 docs/21 及相关冻结文档
⑥ 实现变更
    └─→ 编码 → 测试 → 记录到协作日志
```

---

## 8. Review Checklist

### 8.1 Task Review Checklist（Iteration 级别）

每个 Task 完成后，必须逐项检查：

```
□ Architecture Freeze — 无 R1~R8 违规
□ API Contract — 请求/响应与 docs/13 一致（API Task）
□ WS Protocol — 消息类型与 docs/14 一致（WS Task）
□ ADR — 不违反相关 Approved ADR
□ Naming Convention — snake_case / 前缀命名规范
□ Error Code — 错误使用 docs/13 §5 定义的错误码
□ Logging — 关键路径有日志，不泄露敏感信息
□ Unit Test — 至少覆盖正常路径 + 主要错误路径
□ Documentation — 相关注释或文档更新
□ Execution Report — 已记录到 docs/11_AI协作日志.md
```

### 8.2 Epic Review Checklist

全部 Iteration 完成后，执行 Epic 级别 Review：

```
□ 所有 Task Checklist 通过（全部子 Iteration）
□ Integration Test — 模块间接口集成测试通过
□ Architecture Compliance — 无 Freeze 基线违反
□ Risk Review — docs/18 中关联风险状态已更新
□ Code Review — 至少经过 1 次审查
□ Coverage ≥ 80%（引擎类 Epic）
□ 协作日志完整
```

### 8.3 Milestone Review Checklist + Architecture Gate

Milestone 完成后，必须通过 Architecture Review Gate：

```
□ Task 级别检查全部通过
□ Epic 级别检查全部通过
□ End-to-End Validation — Milestone 定义的验证场景通过
□ Architecture Compliance Review — 无 Freeze 基线违反
□ Risk Review — 无新增 P0 Risk
□ CTO (ChatGPT Chief Architect) Approval
□ Phase Audit — 该 Milestone 产生的所有修改已审计
□ Freeze Compliance — 全部修改在冻结范围内
□ Product Owner 确认（M5 需要）
```

---

## 9. Development Order

### 9.1 严格串行链

```
Chain 1: BOOT → INFRA → DB → REPO → SVC → API
Chain 2: BAZI → RULE → AI → MEM
Chain 3: TASK → API-WS
Chain 4: GUI + VUE（可并行）→ PKG
```

### 9.2 允许并行组

| 组 | 内容 | Agent 数 |
|----|------|:--------:|
| PG-1 | BOOT-02/03/04/05（配置/日志/工具/异常）| 2 |
| PG-2 | DB-02/03/04（3 组模型）| 3 |
| PG-3 | REPO-02~06 ║ DOMAIN-01~03 | 3 |
| PG-4 | BAZI-01~05 ║ PROMPT-01~04 | 2 |
| PG-5 | GUI-01~04 ║ VUE-01~05 | 2 |

### 9.3 建议 Batch 推进

| Batch | Iterations | Agent |
|-------|-----------|:-----:|
| B1 | BOOT I1~I5 | 1 |
| B2 | INFRA I1~I5 + BAZI I1 | 2 |
| B3 | DB I1~I4 + DOMAIN I1~I3 + BAZI I2 | 3 |
| B4 | REPO I1~I6 + BAZI I3~I5 | 2 |
| B5 | RULE I1~I3 + PROMPT I1~I4 + SVC I1~I2 | 3 |
| B6 | SVC I3~I6 + API-I1~I4 | 2 |
| B7 | API-I5~I8 + TASK I1~I3 | 2 |
| B8 | AI I1~I5 + MEM I1~I4 | 2 |
| B9 | API-WS I1~I2 + GUI-I1~I4 + VUE I1~I5 | 3 |
| B10 | GUI-I5~I6 + TEST I1~I4 + PKG I1~I3 + DOC I1~I2 | 3 |

---

## 10. Risk Control

### 10.1 八条冻结红线（R1~R8）

| 红线 | 内容 | 检测 |
|------|------|------|
| R1 | 修改 Frozen ADR 内容 | PR Review |
| R2 | 修改 API endpoint 路径/方法/字段 | API 契约审计 |
| R3 | 修改 WS 消息 type/data/路径 | WS 协议审计 |
| R4 | 修改 6 层架构分层或模块划分 | 架构审计 |
| R5 | 修改数据三层体系或流转规则 | ADR 合规检查 |
| R6 | 修改三层记忆架构基本结构 | 架构审计 |
| R7 | 不走 RFC 绕过任何 Approved ADR | 治理审计 |
| R8 | 将 Draft ADR 作为约束性依据 | 代码审查 |

### 10.2 已知风险（摘自 docs/18）

| ID | 描述 | 等级 | 关联 Epic |
|----|------|:----:|:---------:|
| ARC-15-P1-001 | 技术选型表冲突 | P1 | E-BOOT |
| ARC-15-P1-002 | HANDOVER 遗漏 ADR 列表 | P1 | E-BOOT |
| ARC-15-P1-003 | 版本历史存储方案未决 | P1 | E-DB |
| ARC-15-P1-004 | 离线策略颗粒度不足 | P1 | E-SVC |
| ARC-15-P1-005 | 认证模型需适配桌面场景 | P1 | E-SVC |
| ARC-15-P1-006 | 排盘引擎接口抽象缺失 | P1 | E-BAZI |
| ARC-15-P1-007 | 部署打包方案未确认 | P1 | E-PKG |

---

## 11. Definition of Done

### 11.1 Task / Iteration DoD

| # | 标准 | 验证 |
|---|------|------|
| 1 | 代码无错误 | `pytest` 通过 |
| 2 | Lint 通过 | `ruff check .` |
| 3 | API 契约合规（如适用）| 与 docs/13 对齐 |
| 4 | 无 Freeze 违反 | 无 R1~R8 |
| 5 | 无 ADR 违反 | ADR 核对清单 |
| 6 | 协作日志已更新 | `docs/11` 追加记录 |
| 7 | 错误路径覆盖 | 至少 3 种错误场景 |

### 11.2 Epic DoD

| # | 标准 |
|---|------|
| 1 | 全部 Iteration DoD 满足 |
| 2 | 模块间集成测试通过 |
| 3 | 架构合规（无 Freeze 违反）|
| 4 | 风险跟踪表已更新 |
| 5 | Code Review 完成 |

### 11.3 Milestone DoD + Gate

| # | 标准 |
|---|------|
| 1 | 全部 Epic DoD 满足 |
| 2 | E2E 验证场景通过 |
| 3 | Architecture Review Gate 通过（CTO + Compliance + Risk）|
| 4 | 无新增 P0 风险 |
| 5 | M5 额外：PO 签署确认 |

### 11.4 Phase 3 关闭条件

1. ✅ M5 完成 + Gate 通过
2. ✅ 核心模块测试覆盖率 ≥ 80%
3. ✅ 至少 10 项 P1/P2 风险已关闭
4. ✅ HANDOVER.md 已更新 Phase 3 交接信息
5. ✅ 无冻结基线违反的未处理问题
6. ✅ PO 确认 MVP 可交付

---

> **版本：** v3.0 | **2026-07-11** | **角色：** Documentation Engineer
>
> **修改摘要：** 新增 Iteration 层、Development Workflow、Change Management、Review Checklist（3 级）、Architecture Review Gate
>
> **冻结一致性：** 未修改任何冻结基线内容（docs/08/13/14/19/21/04 均未触碰）
