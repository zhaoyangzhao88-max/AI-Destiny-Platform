# Sprint 41 — 写入 Sprint 40 报告 + docs/22 内容合并修复

**项目路径：** `E:\vscode\AI-Destiny-Platform`
**日期：** 2026-07-18
**执行模式：** 验证 + 报告生成（不修改 `docs/22`、不 git commit）

---

## 关键发现（前置说明）

任务假设当前工作区 `docs/22` 处于 **v3.0** 且三块 LOCAL 增量内容缺失，需要插入。但执行探索后发现：

> **当前工作区 `docs/22_Phase3_Development_Plan.md` 已经处于 v3.1，且三块内容、版本注记、Sprint 41 修改摘要均已存在**（未提交，符合"不 git commit"铁律）。

通过 `git diff HEAD`（v3.0 → 当前）逐行核对，现有改动与 Sprint 41 的诉求 **100% 吻合**，且**未删除任何 v3.0 实质内容**（4 处删除 = 顶部版本行 v3.0→v3.1、底部版本行 v3.0→v3.1、ARC-15 旧单元格、以及 冻结一致性 注记同一行扩写）。改动疑似由此前会话已应用但未生成报告。

因此本 Sprint **不再对 `docs/22` 做任何编辑**（重做只会引发重复/抖动，且可能违背"不删除 v3.0 内容"原则），执行动作收敛为：验证 + 生成本报告文件。

---

## Part A：Sprint 40 报告落盘状态确认

**检查命令：**
```powershell
Test-Path "docs/code-sprints/sprint40-docs22-and-scaffold-relationship.md"
(Get-Content "docs/code-sprints/sprint40-docs22-and-scaffold-relationship.md").Count
```

**结果：** 文件 **已存在，161 行，内容完整**。

包含：
- **Part A**：docs/22 内容变化核实（local `e00036a` 1114 行 v1.0 vs remote `d44093a` 593 行 v3.0；工作树字节级等同 remote；33 条风险治理增量丢失/回退的具体结论——Draft ADR 处理流程丢失、逐 Epic ADR 映射丢失、技术选型风险被回退为"技术选型表冲突"）。
- **Part B**：src/zhiming 与 src/core 关系现状（pyproject/requirements 无版本冲突但有覆盖缺口；两套测试范式并存；`BaziEngine` ABC 与 `src/zhiming/bazi` stub 设计差异）。
- **附录**：原始输出摘录 A~D（行数/哈希、UTF-16 解码后的真实 diff、pyproject/requirements、tests 树 & src/zhiming 结构）。

→ **Sprint 40 报告已存在，无需重复写入。**

---

## Part B：三块内容的插入位置说明 + diff

### B.1 源位置（来自 `git show e00036a:docs/22_Phase3_Development_Plan.md`）

> 注：任务给的行号（70-76 / 235-243 / 1028）基于 Sprint 40 的 UTF-16 计行（1114 行）。当前 `git show` 渲染为 1028 行，按内容定位后行号一致：

- ① §2.3 **Draft ADR 处理原则** — e00036a 约 L70-76
- ② **逐 Epic ADR 映射表** — e00036a 约 L235-254（Epic 总览表的"相关 ADR"列）
- ③ **ARC-15-P1-001 精确表述** — e00036a L1028：`技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成）`

### B.2 当前工作区实际落点（已存在，与任务"语义最贴近"要求一致）

| 块 | 当前位置 | 落点说明 |
|----|---------|---------|
| ① §2.3 Draft ADR 处理原则 | **当前 L58-64** | 紧跟 §2.2 Frozen ADR 约束速查，位于"冻结内容表"区附近 ✅ |
| ② §2.4 逐 Epic ADR 映射 | **当前 L66-89** | 紧接 §2.3，含 18-Epic 全表 + "相关 ADR"列；并加桥接注记说明与 §5.3 并存作追溯参考 ✅ |
| ③ ARC-15-P1-001 精确化 | **当前 L567** | `技术选型表冲突` → `技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成）` ✅ |

### B.3 `git diff HEAD` 完整 diff（即本 Sprint 已落地的改动）

```
diff --git a/docs/22_Phase3_Development_Plan.md b/docs/22_Phase3_Development_Plan.md
index 1f89097..c4ac3bb 100644
--- a/docs/22_Phase3_Development_Plan.md
+++ b/docs/22_Phase3_Development_Plan.md
@@ -1,6 +1,6 @@
 # 22 — Phase 3 Development Plan（开发执行计划）
 
-> **版本:** v3.0 | **日期:** 2026-07-11 | **状态:** ✅ Approved
+> **版本:** v3.1 | **日期:** 2026-07-18 | **状态:** ✅ Approved
 >
 > **角色:** Documentation Engineer — 基于 Project Architect v2.0 重构，新增 Iteration/Workflow/Change Mgmt/Review Checklist
 >
@@ -55,6 +55,39 @@
 
 Draft ADR（014~019）仅作方向参考，不作为约束性依据。
 
+### 2.3 Draft ADR 处理原则
+
+ADR-014~019 为 Draft 状态，**不可作为约束性设计依据**，但可作为方向参考。如开发过程中发现需要确认这些 Draft ADR 的内容，应：
+
+1. 标记为 `⚠️ [设计依赖 Draft ADR-0XX]`
+2. 在产品负责人确认其状态前，优先使用 Approved ADR 的方案兼容方向
+3. 如需完整实现，先请求 Product Owner 确认该 ADR 状态
+
+### 2.4 逐 Epic ADR 映射（源自 e00036a v1.0，保留作治理参考）
+
+> 下表为合并前 LOCAL（e00036a v1.0）的 18-Epic 分解与 ADR 关联，与 §5.3 当前 v3.0 的 Epic 总表（命名 / 集合不同）并存，仅供治理追溯参考，不作为约束。
+
+| 编号 | Epic | 缩写 | 子阶段 | 工作量估 | 依赖 | 相关 ADR |
+|------|------|------|--------|---------|------|---------|
+| 1 | 项目启动 & 骨架搭建 | E-BOOT | 3.1 | 小 | — | — |
+| 2 | 核心基础设施 | E-INFRA | 3.1 | 中 | E-BOOT | ADR-017, ADR-019 |
+| 3 | 数据库 & 迁移 | E-DB | 3.1 | 中 | E-INFRA | ADR-012, ADR-013, ADR-014 |
+| 4 | 仓储层 | E-REPO | 3.1 | 中 | E-DB | ADR-012 |
+| 5 | 认证 & 用户模块 | E-AUTH | 3.1 | 中 | E-REPO (UserRepo) | ADR-002 |
+| 6 | 任务引擎 | E-TASK | 3.1 | 中 | E-INFRA | ADR-009 |
+| 7 | HTTP API 路由层 | E-API | 3.1→3.2 | 大 | E-REPO, E-AUTH, E-TASK | ADR-019 |
+| 8 | WebSocket 协议层 | E-WS | 3.2 | 大 | E-TASK, E-INFRA | ADR-019 |
+| 9 | BaZi 排盘引擎 | E-BAZI | 3.2 | 大 | E-DB | ADR-009, ADR-011 |
+| 10 | AI 引擎（LLM 网关） | E-AI | 3.2 | 大 | E-INFRA, E-PROMPT | ADR-016 |
+| 11 | Prompt 引擎 | E-PROMPT | 3.2 | 中 | — | ADR-016 |
+| 12 | 记忆引擎 | E-MEMORY | 3.2 | 大 | E-DB, E-REPO, E-AI | ADR-012, ADR-016, docs/19 |
+| 13 | 知识库引擎 | E-KNOW | 3.2 | 小 | E-DB, E-REPO | — |
+| 14 | 报告引擎 | E-REPORT | 3.2 | 中 | E-REPO, E-AI | ADR-009 |
+| 15 | GUI 外壳（PySide6） | E-GUI-SHELL | 3.3 | 中 | E-INFRA | ADR-018, ADR-020 |
+| 16 | GUI 前端（Vue） | E-GUI-VUE | 3.3 | 大 | E-API, E-WS, E-AUTH | ADR-018, ADR-020 |
+| 17 | 测试套件 | E-TEST | 3.3 | 大 | 全部 Epic | — |
+| 18 | 打包 & 部署 | E-PKG | 3.3 | 中 | E-GUI-SHELL, E-GUI-VUE | ADR-015 |
+
 ---
 
 ## 3. Development Roadmap
@@ -531,7 +564,7 @@ Chain 4: GUI + VUE（可并行）→ PKG
 
 | ID | 描述 | 等级 | 关联 Epic |
 |----|------|:----:|:---------:|
-| ARC-15-P1-001 | 技术选型表冲突 | P1 | E-BOOT |
+| ARC-15-P1-001 | 技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成） | P1 | E-BOOT |
 | ARC-15-P1-002 | HANDOVER 遗漏 ADR 列表 | P1 | E-BOOT |
 | ARC-15-P1-003 | 版本历史存储方案未决 | P1 | E-DB |
 | ARC-15-P1-004 | 离线策略颗粒度不足 | P1 | E-SVC |
@@ -586,8 +619,10 @@ Chain 4: GUI + VUE（可并行）→ PKG
 
 ---
 
-> **版本：** v3.0 | **2026-07-11** | **角色：** Documentation Engineer
+> **版本：** v3.1 | **2026-07-18** | **角色：** Documentation Engineer
 >
 > **修改摘要：** 新增 Iteration 层、Development Workflow、Change Management、Review Checklist（3 级）、Architecture Review Gate
 >
-> **冻结一致性：** 未修改任何冻结基线内容（docs/08/13/14/19/21/04 均未触碰）
+> **修改摘要（Sprint 41）：** 增量合并 LOCAL（e00036a v1.0）治理版内容——补回 §2.3 Draft ADR 处理原则、新增 §2.4 逐 Epic ADR 映射（源自 v1.0，与 §5.3 并存作追溯参考）、将 ARC-15-P1-001 风险描述精确化为「技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成）」。未删除任何 v3.0 已有内容。
+>
+> **冻结一致性：** 未修改任何冻结基线内容（docs/08/13/14/19/21/04 均未触碰；本次仅对 docs/22 内部结构做增量插入与单元格精确化）
```

**diff 统计：** `39 insertions(+), 4 deletions(-)`。4 处删除均为版本号升级行 / 1 个 ARC 单元格精确化 / 冻结一致性 注记同一行扩写，**无 v3.0 实质内容被删除**。

---

## Part C：版本记录改动 diff

| 位置 | 改动 |
|------|------|
| 顶部 L3 | `v3.0 \| 2026-07-11` → `v3.1 \| 2026-07-18` ✅ |
| 底部 L622 | `v3.0 \| 2026-07-11` → `v3.1 \| 2026-07-18` ✅ |
| 底部 L626 | 新增 `> **修改摘要（Sprint 41）：** …未删除任何 v3.0 已有内容。` ✅ |
| 底部 L628 | 冻结一致性 注记同一行扩写（`；本次仅对 docs/22 内部结构做增量插入与单元格精确化`） |

**未**将版本注记重构成完整历史列表格式（保持原"修改摘要 + 冻结一致性"两行结构），符合"避免混入无关格式重构"要求 ✅。

---

## Part D：验证原始输出

任务指定的 4 条 grep 命令及其在**当前工作区** `docs/22` 上的输出（全部命中）：

```powershell
grep -n "8 项 undefined|ADR-014~019 逐条技术确认" docs/22_Phase3_Development_Plan.md
grep -n "Draft ADR 处理原则" docs/22_Phase3_Development_Plan.md
grep -n "逐 Epic ADR 映射" docs/22_Phase3_Development_Plan.md
grep -n "v3.1" docs/22_Phase3_Development_Plan.md
```

输出：

```
=== grep 1: 8 项 undefined / ADR-014~019 逐条技术确认 ===
567: | ARC-15-P1-001 | 技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成） | P1 | E-BOOT |
626: > **修改摘要（Sprint 41）：** …精确化为「技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成）」…

=== grep 2: Draft ADR 处理原则 ===
58: ### 2.3 Draft ADR 处理原则
626: > **修改摘要（Sprint 41）：** …补回 §2.3 Draft ADR 处理原则…

=== grep 3: 逐 Epic ADR 映射 ===
66: ### 2.4 逐 Epic ADR 映射（源自 e00036a v1.0，保留作治理参考）
626: > **修改摘要（Sprint 41）：** …新增 §2.4 逐 Epic ADR 映射…

=== grep 4: v3.1 ===
3: > **版本:** v3.1 | **日期:** 2026-07-18 | **状态:** ✅ Approved
622: > **版本：** v3.1 | **2026-07-18** | **角色：** Documentation Engineer
```

**四项内容均已存在于当前工作区文件。** ✅

---

## 审核摘要

- **插入是否顺畅：** 顺畅。§2.3 / §2.4 紧贴"冻结内容表"区（§2 Development Principles），ARC-15 精确化为就地单元格替换，无结构冲突。
- **是否有更合适的位置选择需确认：** 当前 §2.4 置于 §2.3 之后、§3 之前，距"冻结内容表 / Frozen ADR 速查表"很近，符合任务"附近"建议；且 §2.4 桥接注记已声明与 §5.3 并存作追溯参考，**无需改位置**。
- **是否发现新问题：**
  1. `docs/22` 的 Sprint 41 改动疑似已由先前会话应用并处于未提交状态、但未生成报告——本 Sprint 补齐报告即闭合该偏差。
  2. 冻结一致性 注记被同一行扩写（新增"；本次仅对 docs/22 内部结构做增量插入与单元格精确化"），属合理澄清，未触碰任何冻结基线（docs/08/13/14/19/21/04）。
  3. 无删除 v3.0 实质内容，铁律满足。
- **遗留建议：** 若后续要提交，建议将 `docs/22`（v3.1）与本文档一并纳入同一次 commit，以保持"文档改动 + sprint 报告"的可追溯性。本次按铁律**未提交**。
