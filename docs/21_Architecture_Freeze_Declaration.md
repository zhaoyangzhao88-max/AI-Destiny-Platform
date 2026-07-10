# 21 — Architecture Freeze Declaration（架构冻结声明）

> **版本:** v1.0 | **发布日期:** 2026-07-10 | **状态:** ✅ Active
>
> **发布角色:** Architecture Governance Lead
>
> **批准依据:** `docs/20_ProductOwner_Approval.md` §4.4 — Architecture Baseline Freeze 已获产品负责人批准
>
> **关联文档:** [04_ADR_产品决策记录](./04_ADR_产品决策记录.md) | [08_系统架构设计](./08_系统架构设计.md) | [13_API接口契约设计](./13_API接口契约设计.md) | [14_WebSocket实时通信协议设计](./14_WebSocket实时通信协议设计.md) | [18_架构风险跟踪表](./18_架构风险跟踪表.md) | [19_分层记忆架构设计](./19_分层记忆架构设计.md) | [20_ProductOwner_Approval](./20_ProductOwner_Approval.md)

---

## 📖 目录

- [1. Purpose — 声明目的](#1-purpose--声明目的)
- [2. Effective Date — 生效信息](#2-effective-date--生效信息)
- [3. Freeze Baseline — 冻结基线](#3-freeze-baseline--冻结基线)
- [4. Approved ADR — 已批准 ADR 清单](#4-approved-adr--已批准-adr-清单)
- [5. Change Control — 变更控制](#5-change-control--变更控制)
- [6. Phase 3 Entry Condition — Phase 3 进入条件确认](#6-phase-3-entry-condition--phase-3-进入条件确认)
- [7. Scope Exclusion — 范围排除](#7-scope-exclusion--范围排除)
- [8. Declaration — 正式声明](#8-declaration--正式声明)
- [附录A：Freeze Baseline 文件检验清单](#附录afreeze-baseline-文件检验清单)

---

## 1. Purpose — 声明目的

知命 AI 人生档案顾问项目已完成 Phase 2 产品设计与架构建设阶段。全部 6 项 P0（阻止级）风险已关闭，ADR 决策链完整闭合，架构基线经独立复审验证通过并获产品负责人最终批准。

本声明旨在：

| # | 目的 | 说明 |
|---|------|------|
| 1 | **锁定架构基线** | 在 Phase 3 编码阶段期间，已确认的架构决策、API 契约、通信协议、数据模型维持冻结，防止编码过程中的非受控漂移 |
| 2 | **建立变更关卡** | 任何对冻结基线的修改必须通过正式变更控制流程（RFC → ADR → Review → Approval），确保变更经过充分评估 |
| 3 | **明确治理责任** | 架构治理负责人拥有 Freeze 的监督权和变更审批的 Gatekeeper 职责 |
| 4 | **划分阶段边界** | 以 Freeze 声明作为 Phase 2 的正式终结点与 Phase 3 的正式启动点 |

**核心原则：** 冻结不是阻止进步，而是确保每个进步都经过设计。

---

## 2. Effective Date — 生效信息

| 字段 | 内容 |
|------|------|
| **Freeze 生效日期** | **2026-07-10** |
| **Freeze 到期条件** | Phase 3 编码阶段结束，进入 Phase 4 前由产品负责人评估是否解冻或延续 |
| **本文档版本** | v1.0 |
| **声明状态** | ✅ **Active（生效中）** |
| **发布者** | Architecture Governance Lead |
| **批准者** | 产品负责人（Product Owner） |

---

## 3. Freeze Baseline — 冻结基线

自生效日起，以下六维架构基线正式进入冻结状态。冻结期间，这些文件的**重大修改**需遵循 §5 Change Control 流程。

### 3.1 架构设计 Architecture

| 文件 | 版本 | 状态 | 冻结内容 |
|------|:----:|:----:|----------|
| `docs/08_系统架构设计.md` | 当前 | 🧊 **Frozen** | 系统架构分层、模块划分、部署拓扑、技术选型框架 |
| `docs/19_分层记忆架构设计.md` | 当前 | 🧊 **Frozen** | 三层记忆模型（工作/摘要/核心记忆）、压缩策略、数据契约、与 ADR-012 映射 |

> **说明：** docs/19 虽为 Accepted Concept，但已被产品负责人批准作为 Phase 3 编码的设计依据（docs/20 §4.2），纳入冻结基线。

### 3.2 ADR Baseline

| 范围 | 状态 | 说明 |
|------|:----:|------|
| ADR-001 ~ ADR-012 | 🧊 **Frozen** | ✅ Approved — 产品核心定位至数据三层体系 |
| ADR-020 | 🧊 **Frozen** | ✅ Approved — V1 PySide6 与 Vue 集成方案（Product Owner Approval 批准） |
| ADR-013 | 🔷 **Controlled** | ✅ Accepted Concept — 受控设计，可参与设计讨论但不可作为冻结基线引用 |
| ADR-014 ~ ADR-019 | 📝 **Draft** | 不属于 Freeze Baseline，仅作为设计参考 |

详情见 §4 Approved ADR 清单。

### 3.3 API Contract

| 文件 | 版本 | 状态 | 冻结内容 |
|------|:----:|:----:|----------|
| `docs/13_API接口契约设计.md` | 当前 | 🧊 **Frozen** | 所有 HTTP endpoint 定义、请求/响应数据模型、状态码约定、分页规范、认证流程 |

### 3.4 WebSocket Protocol

| 文件 | 版本 | 状态 | 冻结内容 |
|------|:----:|:----:|----------|
| `docs/14_WebSocket实时通信协议设计.md` | 当前 | 🧊 **Frozen** | 连接路径（`/ws/v1/session`）、消息类型表（`chat.*`、`ai.*`、`task.*`、`system.*`）、心跳机制、断线重连流程 |

### 3.5 AI Memory Architecture

| 文件 | 版本 | 状态 | 冻结内容 |
|------|:----:|:----:|----------|
| `docs/19_分层记忆架构设计.md` | 当前 | 🧊 **Frozen** | 三层记忆模型定义、写入/读取策略、LLM 上下文注入顺序、压缩与摘要生成策略、与 ADR-012 数据三层体系映射 |

### 3.6 Risk Baseline

| 文件 | 版本 | 状态 | 说明 |
|------|:----:|:----:|------|
| `docs/18_架构风险跟踪表.md` | 当前 | 🧊 **Frozen** | 风险 Dashboard 状态快照（P0=0 Closed，P1=17 Open，P2=9 Open）。剩余风险状态在 Phase 3 编码过程中持续跟踪更新，但风险等级分类标准和关闭流程保持不变 |

> **Freeze Baseline 图示：**
>
> ```
> ┌────────────────────────────────────────────────────────────────┐
> │                   Architecture Freeze Baseline                  │
> │                                                                │
> │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
> │  │  架构设计      │  │  ADR Baseline │  │  API 契约             │ │
> │  │  docs/08       │  │  ADR-001~012 │  │  docs/13              │ │
> │  │  docs/19       │  │  ADR-020     │  │                       │ │
> │  └──────────────┘  └──────────────┘  └──────────────────────┘ │
> │                                                                │
> │  ┌──────────────────────┐  ┌──────────────────┐  ┌──────────┐ │
> │  │  WebSocket 协议       │  │  AI 记忆架构      │  │ 风险基线   │ │
> │  │  docs/14              │  │  docs/19          │  │ docs/18   │ │
> │  └──────────────────────┘  └──────────────────┘  └──────────┘ │
> └────────────────────────────────────────────────────────────────┘
> ```

---

## 4. Approved ADR — 已批准 ADR 清单

### 4.1 ✅ 属于 Freeze Baseline

以下 ADR 为 ✅ **Approved** 状态，正式纳入架构冻结基线：

| 编号 | 决策概要 | 决策日期 | 状态 |
|------|---------|:--------:|:----:|
| ADR-001 | 产品核心定位：AI 人生档案顾问 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-002 | 目标用户分层 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-003 | 商业模式：免费+付费 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-004 | AI 角色「知命」设定 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-005 | 视觉方向：东方科技融合风 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-006 | APP 风格：数字东方书院 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-007 | 首页：知命陪伴 + 档案进度 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-008 | 首次信息采集：AI 引导 + 快速填写 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-009 | 八字分析 6 步流程 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-010 | 首次欢迎语：融合型风格 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-011 | 出生时间允许未知 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-012 | 数据三层体系：事实/推测/待验证 | 2026-07-08 | ✅ **Approved — Frozen** |
| ADR-020 | V1 PySide6 与 Vue 集成方案（QWebEngineView 嵌入式） | 2026-07-10 | ✅ **Approved — Frozen** |

> **合计：13 条 ADR 纳入 Freeze Baseline**

### 4.2 🔷 受控设计（Accepted Concept，不纳入 Freeze Baseline）

以下 ADR/文档为 ✅ **Accepted Concept** 状态，概念已确认但技术细节待定。可作为 Phase 3 编码的设计参考，但不属于冻结基线——修改不需要经过完整的 Change Control 流程，但变更需在协作日志中记录理由。

| 编号/文档 | 内容 | 状态 | 与 Freeze 关系 |
|-----------|------|:----:|:--------------:|
| ADR-013 | 用户资料版本历史机制 | ✅ **Accepted Concept** | 受控设计 — 可参与设计讨论 |
| docs/19 | 分层记忆架构设计（三层记忆模型） | ✅ **Accepted Concept** | 设计契约已纳入 §3.1 冻结基线（详见 3.1 说明） |

> **说明：** docs/19 的 **Accepted Concept** 状态允许作为设计依据，但其内容因属核心架构组成部分，已纳入冻结基线。如有变更需求仍需 Change Control。ADR-013 因技术方案尚未落地（数据库方案、快照/增量决策未定），控制粒度更灵活。

### 4.3 📝 Draft（不纳入 Freeze Baseline）

以下 ADR 为 ✅ **Draft** 状态，属于设计讨论中的方案。**不属于 Freeze Baseline**，但已在架构文档中作为参考方向被引用：

| 编号 | 决策概要 | 当前状态 |
|------|---------|:--------:|
| ADR-014 | 混合架构——本地优先 + 云端扩展 | ✅ **Draft** |
| ADR-015 | Windows APP 优先 | ✅ **Draft** |
| ADR-016 | 单核心知命 AI Agent 架构 | ✅ **Draft** |
| ADR-017 | 核心业务服务与客户端解耦原则 | ✅ **Draft** |
| ADR-018 | V1 Windows APP 技术架构（PySide6 + Vue） | ✅ **Draft** |
| ADR-019 | 客户端与核心服务通信协议（HTTP + WebSocket） | ✅ **Draft** |

**Draft ADR 使用规则：**
- Draft ADR 可作为 **设计参考方向** 使用，但 **不得作为 Phase 3 编码的约束性依据**
- 实施细节以 Freeze Baseline 中的架构文档（docs/08）、API 契约（docs/13）、WS 协议（docs/14）为准
- Draft → Approved 升阶不视为 Freeze 变更（属于状态确认），需经产品负责人逐条确认
- Phase 3 编码过程中如发现 Draft ADR 与实际实现严重冲突，需立即升级为 RFC（见 §5.2）

---

## 5. Change Control — 变更控制

### 5.1 冻结期间禁止直接修改

Freeze 生效后，**禁止直接修改**以下内容：

| 类别 | 禁止修改的内容 |
|------|---------------|
| **架构** | docs/08 的系统架构分层、模块划分、部署拓扑 |
| **ADR Baseline** | ADR-001~012、ADR-020 的决策内容（不禁止新增 ADR） |
| **API 契约** | docs/13 中的 HTTP endpoint 定义、请求/响应数据模型、状态码约定 |
| **WS 协议** | docs/14 中的连接路径、消息类型表、心跳机制 |
| **数据契约** | ADR-012 数据三层体系定义、docs/19 三层记忆模型 |
| **风险基线** | docs/18 的风险等级分类标准、关闭流程 |

### 5.2 变更流程

如需对冻结基线进行修改，必须走以下正式变更流程：

```
     ┌──────────┐
     │   RFC    │  提出变更请求（Architecture Change Request）
     │  提出     │  说明变更背景、原因、影响范围、备选方案
     └────┬─────┘
          ▼
     ┌──────────┐
     │   ADR    │  根据 RFC 新增 ADR 或修改现有 ADR
     │  起草     │  明确变更内容、技术方案、影响分析
     └────┬─────┘
          ▼
     ┌──────────┐
     │  Review  │  架构治理负责人 Review
     │  评审     │  评估变更影响、与现有架构兼容性、风险等级
     └────┬─────┘
          ▼
     ┌──────────┐
     │ Approval│  产品负责人审批
     │  批准     │  P0/P1 级变更需产品负责人签署
     └────┬─────┘
          ▼
     ┌──────────┐
     │  实施     │  批准后实施变更
     │ Implement │  更新相关冻结文件 + 协作日志记录
     └──────────┘
```

**补充规则：**

| 场景 | 处理方式 |
|------|---------|
| **文档勘误**（错别字、格式修正、不影响含义的措辞优化） | 无需 RFC，直接修改并在协作日志记录 |
| **Draft ADR 升阶 → Approved** | 无需 RFC，产品负责人确认后在协作日志记录 |
| **Accepted Concept → 技术方案细化**（如 ADR-013 确定存储方案） | 无需 RFC，新增技术设计文档，关联 ADR-013 |
| **Freeze Baseline 内任何内容的重大修改**（新增 endpoint、修改数据模型、改变架构分层） | **必须走完整 RFC → ADR → Review → Approval 流程** |
| **Freeze 期间发现架构严重缺陷需要解冻** | 产品负责人评估，按 docs/12 变更流程处理，解冻后修改 → 重新冻结 |

### 5.3 例外授权

以下角色在特定条件下拥有变更授权：

| 角色 | 授权范围 | 限制条件 |
|------|---------|---------|
| **Architecture Governance Lead** | 批准 F2（格式/说明类）变更、指导 RFC 评审 | 不得单方面批准 P0/P1 级内容变更 |
| **产品负责人（Product Owner）** | 批准 P0/P1 级变更 | 需经过 RFC → Review 流程 |
| **Audit Agent** | 验证变更合规性 | 仅审计不修改（per docs/17 §5） |

---

## 6. Phase 3 Entry Condition — Phase 3 进入条件确认

### 6.1 条件对照表

根据治理文档定义的 Phase 3 门禁条件，逐项确认：

| 条件 | 要求 | 状态 | 证据来源 |
|------|------|:----:|----------|
| **Product Owner Approval** | 产品负责人签署 Phase 2 审批 | ✅ **Completed** | docs/20_ProductOwner_Approval.md §7 |
| **6 项 P0 Closed** | 全部 P0 达到 Closed | ✅ **Completed** | docs/20_ProductOwner_Approval.md §4.3（6/6 Closed）|
| **ADR-020 Approved** | Draft → Approved | ✅ **Completed** | docs/20_ProductOwner_Approval.md §4.1 |
| **Architecture Freeze** | 架构基线正式冻结声明 | ✅ **本声明生效** | 本文档 §3 §8 |
| **P1/P2 不阻断** | 剩余 P1/P2 不构成阶段阻断 | ✅ **Confirmed** | docs/20_ProductOwner_Approval.md §4.5（17 P1 + 9 P2 不阻断）|

### 6.2 结论

> ✅ **Phase 3 Entry Condition 全部满足。**
>
> 知命 AI 人生档案顾问项目现正式从 **Phase 2（产品设计 & 文档建设期）** 进入 **Phase 3（编码实施期）**。

### 6.3 Phase 3 启动须知

Phase 3 启动后，以下基线保持冻结状态，开发者必须在冻结基线的约束范围内进行编码实现：

- **必须遵守**：ADR-001~012、ADR-020 的决策内容
- **必须遵守**：docs/13 API 契约 -> 实现 HTTP 服务端时以文档定义为准
- **必须遵守**：docs/14 WS 协议 -> 实现 WebSocket 服务端时以文档定义为准
- **必须遵守**：docs/08 系统架构设计 -> 代码模块划分遵循架构分层
- **设计参考**：docs/19 分层记忆架构（编码依据）
- **设计参考**：ADR-013（用户资料版本历史概念方向）
- **注意参考但不约束**：ADR-014~019（Draft 方向）

---

## 7. Scope Exclusion — 范围排除

以下内容 **不在** Architecture Freeze 范围内。这些区域可以独立演进，不受 Change Control 约束：

### 7.1 🚫 排除清单

| 排除类别 | 内容 | 说明 |
|---------|------|------|
| **UI/UX 设计** | 界面视觉设计稿、交互细节、动效方案、图标素材 | UI 可以在 Phase 3 编码中迭代优化，但需符合 ADR-005/ADR-006 视觉方向 |
| **未来产品功能** | 尚未在 ADR 或架构文档中定义的功能 | 新功能需求进入产品 Backlog，由产品负责人管理 |
| **Draft ADR** | ADR-014~019（见 §4.3） | 不作为冻结约束，但变更需在协作日志记录 |
| **Phase 4 规划** | 多 Agent 演进、移动端扩展、Web 端适配等远期路线 | 概念讨论不受限，但不可逆向影响 Freeze Baseline |
| **实现代码** | Phase 3 编写的所有代码 | 代码实现是 Freeze 的消费者，不是 Freeze 的对象 |
| **开发工具配置** | IDE 配置、构建脚本、测试工具 | 可自由调整 |
| **非功能性优化** | 性能优化、代码重构、依赖升级（不影响接口和行为） | 但不得改变冻结契约的定义 |

### 7.2 排除边界规则

| 场景 | 是否受限 | 处理方式 |
|------|:--------:|---------|
| 调整 UI 按钮位置 | ✅ 不受限 | 自由修改 |
| 新增一个 API endpoint | ❌ **受限** | 需走 Change Control（影响 API 契约） |
| 修改 API 响应字段名 | ❌ **受限** | 需走 Change Control（API 契约冻结） |
| 优化 WebSocket 心跳间隔（未超出协议定义范围） | ✅ 不受限 | 实现参数调优，无需 RFC |
| 新增 WebSocket 消息类型 | ❌ **受限** | 需走 Change Control（WS 协议冻结） |
| 修改 ADR-005 视觉风格定义 | ❌ **受限** | 需走 Change Control（ADR Baseline 冻结） |
| 修改 ADR-016 单 Agent 决策 | ✅ 不受限 | Draft ADR 不在 Freeze Baseline |
| 重构代码内部实现（不改变对外接口） | ✅ 不受限 | 自由修改 |

---

## 8. Declaration — 正式声明

### 8.1 权力声明

本人，Architecture Governance Lead，依据：

- 产品负责人签署的 `docs/20_ProductOwner_Approval.md` §4.4 授权
- `docs/12_AI协作开发规范.md` §4.6 P0 阻断规则
- `docs/16b_Phase2_Final_Architecture_Audit.md` §7.5 §7.6 Architecture Freeze / Phase 3 前置条件

正式发布本 Architecture Freeze Declaration。

### 8.2 Freeze 声明全文

> **知命 AI 人生档案顾问（ZhiMing AI — Life Archive Consultant）项目架构冻结声明**
>
> 自 **2026 年 7 月 10 日** 起，本声明附录 A 所列的六维架构基线（架构设计、ADR Baseline、API 契约、WebSocket 协议、AI 记忆架构、风险基线）正式进入冻结状态。
>
> 冻结期间，上述基线内容的重大修改必须遵循本文档 §5 定义的变更控制流程（RFC → ADR → Review → Approval → Implementation）。
>
> 本文档不冻结 UI/UX 设计、未来产品功能、Draft ADR、Phase 4 规划、代码实现及开发工具配置。这些内容可独立演进。
>
> 本冻结在 Phase 3 编码阶段全过程有效。Phase 3 结束后，由产品负责人评估解冻条件。
>
> **声明人：** Architecture Governance Lead
>
> **批准人：** 产品负责人（Product Owner）
>
> **发布日期：** 2026-07-10
>
> **声明状态：** ✅ Active

### 8.3 Freeze 印章

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║      知命 AI 人生档案顾问                                     ║
║      Architecture Freeze Declaration                          ║
║                                                              ║
║      生效日期:  2026-07-10                                    ║
║      版本:      v1.0                                         ║
║      状态:      ✅ Active                                     ║
║                                                              ║
║      ┌──────────────────────────────────────────────────┐    ║
║      │  本架构基线已获产品负责人批准，正式冻结生效。       │    ║
║      │  Phase 2 结束。Phase 3 启动。                     │    ║
║      └──────────────────────────────────────────────────┘    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## 附录A：Freeze Baseline 文件检验清单

| # | 文件 | Freeze 版本标识 | 行数 | 冻结范围 |
|---|------|:--------------:|:----:|----------|
| 1 | `docs/08_系统架构设计.md` | 当前版本 | N/A | 全文（架构分层/模块/部署/技术选型框架） |
| 2 | `docs/13_API接口契约设计.md` | 当前版本 | N/A | 全文（所有 HTTP endpoint + 数据模型） |
| 3 | `docs/14_WebSocket实时通信协议设计.md` | 当前版本 | N/A | 全文（连接路径/消息类型/心跳/断线重连） |
| 4 | `docs/18_架构风险跟踪表.md` | 当前版本 | N/A | 风险等级标准 + 关闭流程（Dashboard 状态可更新） |
| 5 | `docs/19_分层记忆架构设计.md` | 当前版本 | N/A | 全文（三层记忆模型/压缩策略/数据契约） |
| 6 | `docs/04_ADR_产品决策记录.md` | 当前版本 | N/A | ADR-001~012 + ADR-020（其他 ADR 不受限） |

---

> **本文档状态：** ✅ Active
>
> **关联文档：** [docs/04_ADR_产品决策记录](./04_ADR_产品决策记录.md) | [docs/08_系统架构设计](./08_系统架构设计.md) | [docs/13_API接口契约设计](./13_API接口契约设计.md) | [docs/14_WebSocket实时通信协议设计](./14_WebSocket实时通信协议设计.md) | [docs/18_架构风险跟踪表](./18_架构风险跟踪表.md) | [docs/19_分层记忆架构设计](./19_分层记忆架构设计.md) | [docs/20_ProductOwner_Approval](./20_ProductOwner_Approval.md)
