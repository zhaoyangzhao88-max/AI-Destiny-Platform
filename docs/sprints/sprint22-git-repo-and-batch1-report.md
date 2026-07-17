# Sprint 22 报告 — 登记 git 仓库风险 + 落地首批 5 条已决策方案

> **日期：** 2026-07-16
> **执行人：** Claude Code（Sprint 22 Agent）
> **项目：** 知命 AI 人生档案顾问（E:\VSCODE\AI-Destiny-Platform）
> **关联：** [18_架构风险跟踪表.md](../18_架构风险跟踪表.md) · [risk-resolutions/ARC-09-P1-001_风险解决方案.md](../risk-resolutions/ARC-09-P1-001_风险解决方案.md)

---

## 一、A1 — git 现状实测（原样贴出）

```bash
=== git status (project dir) ===
On branch master
Your branch is up to date with 'origin/master'.
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
	modified:   CLAUDE.md
	modified:   "docs/04_ADR_产品决策记录.md"
	modified:   "docs/08_系统架构设计.md"
	modified:   "docs/09_开发规范.md"
	modified:   "docs/10_测试规范.md"
	modified:   "docs/11_AI协作日志.md"
	modified:   "docs/12_AI协作开发规范.md"
	modified:   "docs/13_API接口契约设计.md"
	modified:   "docs/18_架构风险跟踪表.md"
	modified:   docs/HANDOVER.md
Untracked files:
  (use "git add <file>..." to include what will be committed)
	.zcode/
	AGENTS.md
	docs/bazi-skill-dist-checks/
	docs/risk-resolutions/
	docs/sprint13-risk-application-and-extraction.md
	docs/sprint14-verification-and-sources.md
	docs/sprint16-implementation-report.md
	docs/sprint17-doc-hygiene-report.md
	docs/sprint18-final-cleanup-report.md
	docs/sprint19-remaining-risks-report.md
	docs/sprint20-verification-and-decisions-report.md
	docs/sprint21-final-closeout-report.md
no changes added to commit (use "git add" and/or "git commit -a")

=== rev-parse toplevel (project dir) ===
E:/VSCODE/AI-Destiny-Platform

=== git log -5 ===
0dfa16a docs: Phase 2 closeout and Phase 3 Development Plan
92e3dee feat: initial commit — 知命 AI 人生档案顾问 Phase 2 documentation suite

=== find .git in project root ===
./.git

=== cd .. to parent ===
=== git status (parent) ===
（空）

=== rev-parse toplevel (parent) ===
（空，exit 128）
```

**结论（回答任务 A1 三问）：**
1. `AI-Destiny-Platform` 目录**本身有独立的 `.git`**（`find . -iname .git` → `./.git`）。
2. **不是** `E:\VSCODE` 父目录 git 仓库的一部分——父目录 `git status` / `rev-parse` 均空（exit 128），父目录非 git 仓库。
3. `docs/` 下部分文件已被追踪（`CLAUDE.md`、`04/08/09/10/11/12/13/18_*`、`HANDOVER.md` 为 *modified*），其余（sprint 报告、`risk-resolutions/`）为 *untracked*。

---

## 二、A1 对 A3 推荐方案的修正（关键）

任务 A3 原拟推荐「为 `E:\VSCODE\AI-Destiny-Platform` 初始化独立 `.git` 仓库」。**A1 实测推翻了该前提**：项目本就是独立仓库，不存在需要拆分的父仓库。

依据任务「依据 A1 实际 git 现状填写、不照抄 09 推测性描述」的硬要求，A3 方案**重构**为：

- **不再执行 `git init` / submodule**（无父仓库可拆）。
- 真正待办是**修订过时文档**：`09_开发规范.md` §9.4 与 `HANDOVER.md` §1/§4.1/§5 仍声称项目在共享大仓库中、需独立拆分——与真实 git 状态矛盾。风险实质由「共享仓库风险」重新表述为「**文档与现实 git 状态脱节**」。
- 修订步骤已写入 `risk-resolutions/ARC-09-P1-001_风险解决方案.md`（状态 🟡 Pending Review，待你确认后执行文档修订）。
- 若 A1 发现项目确被父仓库追踪（实测未发生），才需 `git filter-repo` / 开新仓库——本任务未触发该分支。

---

## 三、Part B — 5 条已决策方案落地情况

方案文件均已 `Approved - 已确认方案`，逐条按「涉及文件」落地。方案文件中的章节指引与真实文档**基本吻合**，无实质性冲突：

| 风险 | 落地位置 | 具体内容 | 不符报告 |
|------|----------|----------|----------|
| ARC-15-P1-002 | `HANDOVER.md` §3 ADR 表格 | 新增 ADR-014~020 共 7 行（Draft + ADR-020 Approved）；并修正 §3「完整文档体系」表中「13 条 ADR」→「20 条 ADR」 | 无冲突；附带修正了 002 方案未提及但同属本风险的「13 条」过时引用 |
| ARC-15-P1-003 | `08_系统架构设计.md` §8.6 | 替换「版本存储【待确认】」为「V1 全快照（Snapshots Only）」决策 + 约束 + 曾评估替代方案；`13_API` §3.2 版本端点加存储约束注 | 无冲突 |
| ARC-15-P1-004 | `08_系统架构设计.md` §8.1.2 | 替换「离线策略细节【待确认】」为 5 维度细化表（队列/重试/冲突/API 可用性/UI）+ 后续升级方向 | 无冲突 |
| ARC-15-P1-005 | `13_API接口契约设计.md` §1.7/§3.1/§4.5 + 新增 §4.5.1 | 本地/云端双层鉴权；无鉴权端点表更新；新增 §4.5.1 设备绑定模型（含认证流程图 + V2 扩展条件，原样带入） | 无冲突 |
| ARC-15-P1-007 | `08_系统架构设计.md` 新增 §8.10 | PyInstaller Sidecar 部署、SemVer 兼容矩阵、安装/更新/卸载流程；TOC 加 8.10 | 方案写「新增 §8.10」，原文档确止于 §8.9，插入点清晰，无冲突 |

> 一致性核对：§8.10 版本策略与 `13_API` §6（SemVer / URL 路径版本化）正交互补，已加注说明。

---

## 四、新发现问题

1. **`18_架构风险跟踪表.md` Dashboard 历史内部不一致（非本次引入，存疑待裁决）：**
   - §7.1 总量统计 `风险总数 = 33`（本次后），但 §7.2 按来源分布「合计」仍为 `26`（10+15+1），与总数差 7。
   - 根因：6 条 P0 风险（ARC-15-P0-001~006）已 `Resolved（待验证）` 但仍计入「风险总数」却未计入 §7.2 的 P0 分布行（该行显式为 0），导致总数与按来源/按状态分布长期不自洽。
   - 本次仅刷新了本次相关指标（Open/PR/Resolved/总数 +1），**未擅自修正该历史不一致**，建议产品负责人另行审计全部 33 条条目后统一校准。

2. **任务 Part C 的 Dashboard 算术自相矛盾：**
   - 任务原写「Pending Review=17（21-5+1新增）」——**算错**。新增的 ARC-09-P1-001 状态是 🟢 **Open**（非 Pending Review），正确应为 `21-5=16`。
   - 准确结果见下表。

---

## 五、完成后 Dashboard 预期（准确版）

| 指标 | Sprint 21 基线 | Sprint 22 后 |
|------|---------------|--------------|
| 🟢 Open | 0 | **1**（ARC-09-P1-001） |
| 🟡 Pending Review | 21 | **16**（21 − 5 已解决） |
| 🔵 Resolved | 11 | **16**（11 + 5） |
| P1 总数 | 17 | **13**（17 − 5 + 1） |
| P2 总数 | 8 | 8 |
| **风险总数** | 32 | **33** |

> 说明：任务原文期望 `Open=1 / Pending Review=17 / Resolved=16`，其中 Pending Review=17 系把新增 Open 风险误计入 Pending Review；本表采用准确口径（Pending Review=16）。§7.2 按来源分布「合计=26」与总数 33 的 7 条历史缺口为遗留问题，不在本 Sprint 修正范围（见第四节）。

---

## 六、变更文件清单

| 文件 | 改动 |
|------|------|
| `docs/HANDOVER.md` | §3 ADR 表补 ADR-014~020；「13 条」→「20 条」 |
| `docs/08_系统架构设计.md` | §8.1.2 离线策略细化；§8.6 全快照决策；新增 §8.10 部署打包；TOC 加 8.10 |
| `docs/13_API接口契约设计.md` | §1.7/§3.1/§4.5 鉴权模型更新；新增 §4.5.1 设备绑定；§3.2 存储约束注 |
| `docs/18_架构风险跟踪表.md` | 新增 §6 项目基础设施风险分组（ARC-09-P1-001, Open）；5 条 P1 → Resolved；Dashboard 刷新；meta 章节顺延 §7/§8/§9；§9 变更记录加 Sprint 22 行 |
| `docs/risk-resolutions/ARC-09-P1-001_风险解决方案.md` | 新建（🟡 Pending Review，重构为修订过时文档） |
| `docs/11_AI协作日志.md` | 追加 Sprint 22 记录 |

> ⚠️ 本任务「完成后上传」未自动执行 `git commit`（遵守全局「禁止自动提交」铁律）；上述文件创建/修改后是否提交由产品负责人确认。

---

## 七、Sprint 22 验证执行（2026-07-17）

### 7.1 Phase 0 — 精确验证结果

逐行读取目标章节，验证 5 条 ARC-15-P1 方案落地完成度：

| 风险 | 目标文档 | 目标位置 | 状态 | 证据 |
|------|---------|---------|:----:|------|
| ARC-15-P1-002 | HANDOVER.md | §3 ADR 表 | ✅ **已完成** | lines 48-69，ADR-001~020 完整 |
| ARC-15-P1-003 | 08_系统架构设计.md | §8.6 数据版本历史 | ✅ **已完成** | lines 562-610，全快照决策完整（含约束/替代方案） |
| ARC-15-P1-004 | 08_系统架构设计.md | §8.1.2 离线策略 | ✅ **已完成** | lines 113-127，5 维度矩阵完整 |
| ARC-15-P1-005 | 13_API接口契约设计.md | §4.5.1 设备绑定认证 | ✅ **已完成** | lines 1146-1203，完整含 V2 扩展条件 |
| ARC-15-P1-007 | 08_系统架构设计.md | §8.10 部署打包 | ✅ **已完成** | lines 822-884，PyInstaller sidecar 完整 |

**结论：5 条方案在之前 sprint 已全部落地，Sprint 22 无需额外文档修改。**

### 7.2 Phase 2 — 解决方案文件更新

5 个解决方案文件已追加 Sprint 22 验证注释（版本号 +1）：

| 文件 | 原版本 | 新版本 |
|------|:------:|:------:|
| `ARC-15-P1-002_风险解决方案.md` | v1.0 | v1.1 |
| `ARC-15-P1-003_风险解决方案.md` | v2.0 | v2.1 |
| `ARC-15-P1-004_风险解决方案.md` | v1.1 | v1.2 |
| `ARC-15-P1-005_风险解决方案.md` | v1.1 | v1.2 |
| `ARC-15-P1-007_风险解决方案.md` | v1.1 | v1.2 |

### 7.3 跟踪表状态确认

| 指标 | 原值 | 现确认 |
|------|:----:|:------:|
| 🟢 Open | 1（ARC-09-P1-001） | ✅ 一致 |
| 🟡 Pending Review | 16 | ✅ 一致（5 条已转 Resolved，1 条新增 Open） |
| 🔵 Resolved | 16 | ✅ 一致（含 5 条 ARC-15-P1） |
| 风险总数 | 33 | ✅ 一致 |

### 7.4 遗留事项

1. **HANDOVER.md 过时 git 描述待修订**：§1 line 30（"父 git 仓库"→独立仓库）、§4.1 line 101（"Git 仓库独立方案"→已完成）、§5 line 127（"P0 ── Git 仓库独立"→✅已完成）。已写入 ARC-09-P1-001 解决方案文件（🟡 Pending Review），待产品负责人确认后执行。
2. **Dashboard 总数 33 vs §7.2 来源合计 26 不一致**：历史遗留，6 条 P0 已 Resolved 计入总数但未计入 P0 分布行。需单独审计。
3. **08_系统架构设计.md §8.5 line 560 数据库选型【待确认】**：独立于本 sprint 范围，属 Phase 3 内容。
