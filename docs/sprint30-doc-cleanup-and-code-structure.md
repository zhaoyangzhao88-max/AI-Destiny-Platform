# Sprint 30 执行报告 — 文档归档整理 + Phase 3 代码结构规划

> **日期:** 2026-07-17
> **执行人:** Claude Code
> **处理范围:** Part A — Sprint 报告归档 / Part B — 代码目录结构规划

---

## Part A：归档 Sprint 报告

### A1：清点

**已归档文件（13 份）：**

| 文件名 | 大小 | 说明 |
|--------|------|------|
| `sprint13-risk-application-and-extraction.md` | ✅ 已迁移 | 风险方案落地 |
| `sprint14-verification-and-sources.md` | ✅ 已迁移 | 验证与来源 |
| `sprint16-implementation-report.md` | ✅ 已迁移 | 实施报告 |
| `sprint17-doc-hygiene-report.md` | ✅ 已迁移 | 文档卫生 |
| `sprint18-final-cleanup-report.md` | ✅ 已迁移 | 最终清理 |
| `sprint19-remaining-risks-report.md` | ✅ 已迁移 | 剩余风险 |
| `sprint20-verification-and-decisions-report.md` | ✅ 已迁移 | 验证与决策 |
| `sprint21-final-closeout-report.md` | ✅ 已迁移 | 收尾报告 |
| `sprint22-git-repo-and-batch1-report.md` | ✅ 已迁移 | Git 仓库+批次1 |
| `sprint23-final-batch-report.md` | ✅ 已迁移 | 最终批次 |
| `sprint24-cleanup-and-review-extract.md` | ✅ 已迁移 | 清理与审查 |
| `sprint25-governance-closeout-final.md` | ✅ 已迁移 | 治理线收官 |
| `sprint26-compliance-registration.md` | ✅ 已迁移 | 合规登记 |

**未移动：**
- `docs/sprint27-walking-skeleton/` — 独立子目录，已整理过，无需移动
- `docs/00_AI_CONTEXT_INDEX.md` / `docs/16b_Phase2_Final_Architecture_Audit.md` — 非 sprint 报告，留在根目录

### A2：交叉引用检查

**`docs/18_架构风险跟踪表.md`** — 10 处引用，已全部更新为 `./sprints/sprintXX-xxx.md`

| 行号 | 原路径 | 更新后路径 |
|:----:|--------|-----------|
| 794 | `../sprint19-remaining-risks-report.md` | `./sprints/sprint19-remaining-risks-report.md` |
| 796 | `../sprint20-verification-and-decisions-report.md` | `./sprints/sprint20-verification-and-decisions-report.md` |
| 798 | `../sprint21-final-closeout-report.md` | `./sprints/sprint21-final-closeout-report.md` |
| 907 | `../sprint19-remaining-risks-report.md` | `./sprints/sprint19-remaining-risks-report.md` |
| 908 | `../sprint20-verification-and-decisions-report.md` | `./sprints/sprint20-verification-and-decisions-report.md` |
| 909 | `../sprint21-final-closeout-report.md` | `./sprints/sprint21-final-closeout-report.md` |
| 910 | `./sprint22-git-repo-and-batch1-report.md` | `./sprints/sprint22-git-repo-and-batch1-report.md` |
| 911 | `./sprint23-final-batch-report.md` | `./sprints/sprint23-final-batch-report.md` |
| 912 | `./sprint25-governance-closeout-final.md` | `./sprints/sprint25-governance-closeout-final.md` |
| 913 | `./sprint26-compliance-registration.md` | `./sprints/sprint26-compliance-registration.md` |

**Sprint 报告内部引用**（文件已移入 `docs/sprints/`，`./` 路径需改为 `../`）：

| 文件 | 行号 | 原路径 | 更新后路径 |
|------|:----:|--------|-----------|
| `sprint13-risk-application-and-extraction.md` | 5 | `./18_架构风险跟踪表.md` | `../18_架构风险跟踪表.md` |
| `sprint13-risk-application-and-extraction.md` | 5 | `./15_Phase2架构审计报告.md` | `../15_Phase2架构审计报告.md` |
| `sprint13-risk-application-and-extraction.md` | 5 | `./16_AI协作治理体系审计报告.md` | `../16_AI协作治理体系审计报告.md` |
| `sprint14-verification-and-sources.md` | 1875 | `./04_ADR_产品决策记录.md` 等 5 处 | `../04_ADR_产品决策记录.md` 等 |
| `sprint14-verification-and-sources.md` | 2197 | `./04_ADR_产品决策记录.md` 等 5 处 | `../04_ADR_产品决策记录.md` 等 |
| `sprint19-remaining-risks-report.md` | 5 | `./18_架构风险跟踪表.md` + `./risk-resolutions/` | `../18_架构风险跟踪表.md` + `../risk-resolutions/` |
| `sprint21-final-closeout-report.md` | 6 | `./18_架构风险跟踪表.md` | `../18_架构风险跟踪表.md` (sprint20 引用保持 `./`) |
| `sprint22-git-repo-and-batch1-report.md` | 6 | `./18_` + `./risk-resolutions/` | `../18_` + `../risk-resolutions/` |
| `sprint25-governance-closeout-final.md` | 5 | `./11_` + `./12_` + `./18_` | `../11_` + `../12_` + `../18_` |

**`docs/risk-resolutions/` 子目录引用（Sprint 30 补修）** — 初始跑批的 A2 grep 使用 `docs/*.md` 通配符（不递归子目录），漏掉此目录。递归扫描发现 8 处指向移动前根路径的失效链接，已修正为 `../sprints/sprintXX-…`：

| 文件 | 行号 | 原路径（失效） | 更新后路径（有效） |
|------|:----:|---------------|-------------------|
| `ARC-09-P1-001_风险解决方案.md` | 103 | `../sprint22-git-repo-and-batch1-report.md` | `../sprints/sprint22-git-repo-and-batch1-report.md` |
| `ARC-16-P1-001_风险解决方案.md` | 28, 193 | `../sprint13-risk-application-and-extraction.md` | `../sprints/sprint13-risk-application-and-extraction.md` |
| `ARC-16-P1-002_风险解决方案.md` | 166 | `../sprint13-risk-application-and-extraction.md` | `../sprints/sprint13-risk-application-and-extraction.md` |
| `ARC-16-P1-003_风险解决方案.md` | 28, 181 | `../sprint13-risk-application-and-extraction.md` | `../sprints/sprint13-risk-application-and-extraction.md` |
| `ARC-16-P1-004_风险解决方案.md` | 28, 210 | `../sprint13-risk-application-and-extraction.md` | `../sprints/sprint13-risk-application-and-extraction.md` |

**无需更新的引用：**
- `docs/10_测试规范.md:56` — 引用 `docs/sprint27-walking-skeleton/`（未移动，路径有效）
- `docs/11_AI协作日志.md` — 全部为叙述性文本引用（`docs/sprintXX-xxx.md`），非 markdown 链接，历史记录保持原样
- `sprint14-verification-and-sources.md:1653` — 代码示例（`` `[项目简介](./01_项目简介.md)` ``），非实际链接
- `sprint14-verification-and-sources.md:36` — 已使用 `../` 前缀，移动后自动正确
- `sprint24-cleanup-and-review-extract.md:80,217-221` — 已使用 `../` 前缀，移动后自动正确

### A3：执行归档

```bash
mkdir -p docs/sprints/
mv docs/sprint13*.md docs/sprint14*.md docs/sprint16*.md ... docs/sprints/
```

### A4：交叉引用更新

已更新 18 处引用路径（10 处 `docs/18_架构风险跟踪表.md` + 8 处 sprint 报告内部引用）。

### A5：验证

```
✅ docs/ 根目录无残留 sprint 文件
✅ docs/sprints/ 包含全部 13 份 sprint 报告
✅ 无残留失效引用路径（docs/sprintXX 格式引用均为 sprint27-walking-skeleton 或协作日志叙述文本；risk-resolutions 子目录 8 处失效链接已于本 Sprint 30 补修）
✅ 所有 `./sprint` / `../sprint` 引用已更新为 `./sprints/sprint`（含 risk-resolutions 子目录补修的 8 处）
```

---

## Part B：Phase 3 代码结构规划

### 产出文件

- **`docs/23_代码目录结构规划.md`**（v0.1，Draft）

### 内容概要

| 章节 | 内容 |
|------|------|
| §1 顶层目录结构 | `src/core/` / `src/desktop/` / `src/web/` / `src/tests/` 四目录布局 |
| §2 `src/core/` | 7 层子目录（api/services/domain/infrastructure/scripts），与 13 号文档 Layer 3→6 完全对齐 |
| §3 `src/desktop/` | PySide6 外壳，含 process_manager/bridge/native/webview 4 子模块 |
| §4 `src/web/` | Vue 渐进式 UI，含 router/views/components/composables/stores |
| §5 `src/tests/` | 分层测试策略（单元→服务→API→集成→前端） |
| §6 Walking Skeleton 迁移 | 5 个代码文件的明确迁移路径映射表 |
| §7 对应关系表 | 代码目录 ↔ 08 号文档模块 / 13 号文档 API 端点的完整映射 |

### 设计依据

- 技术栈：ADR-014~020（PySide6+Vue 混合 / FastAPI 核心服务 / SQLite 本地优先）
- 模块划分：08_系统架构设计.md §8.4 核心模块划分 + §8.8.1 BaziEngine 接口
- 分层架构：13_API接口契约设计.md §2 系统分层架构（6 层模型）
- 通信协议：14_WebSocket实时通信协议设计.md
- 验证代码：docs/sprint27-walking-skeleton/scripts/bazi_core.py

---

## 遗留问题

1. `docs/11_AI协作日志.md` 中的叙述性引用（`docs/sprintXX-xxx.md`）未更新为 `docs/sprints/sprintXX-xxx.md`——原因是这些是历史记录文本，非 markdown 链接，更新后反而降低历史准确性
2. `docs/23_代码目录结构规划.md` 状态为 Draft，建议产品负责人评审后提升状态
3. 正式编码开始时，需同步更新 `docs/03_当前开发状态.md` 中的待办清单