# Sprint 40 — docs/22 内容核实 + src/zhiming 与 src/core 关系澄清

**执行模式：** 纯只读核实（铁律：无 git 写操作、无文件修改/删除）
**项目路径：** `E:\vscode\AI-Destiny-Platform`
**日期：** 2026-07-18

---

## Part A：docs/22 内容变化核实

**原始命令（已执行）：**
```bash
git show e00036a:docs/22_Phase3_Development_Plan.md > local_version.md   # 1114 行
git show d44093a:docs/22_Phase3_Development_Plan.md > remote_version.md  # 593 行
# 行数: local=1114, remote=593
# 注: 两文件经 git show 落地为 UTF-16-LE(BOM FF FE)，导致 fc/git diff 误判为二进制；
#     已用 Python(difflib) 解码后产出真实文本 diff。
```

### A1. 本地版本（e00036a）vs 远端版本（d44093a）具体差异

| 维度 | LOCAL（e00036a） | REMOTE（d44093a） |
|------|------------------|-------------------|
| 行数 | **1114** | **593** |
| 元数据 | 版本 **v1.0** \| 日期 **2026-07-10** \| 状态 **✅ Active** | 版本 **v3.0** \| 日期 **2026-07-11** \| 状态 **✅ Approved** |
| 作者标注 | Project Architect \| Agent-20260710-02 | Documentation Engineer — 基于 Project Architect v2.0 重构 |
| 结构 | 9 章节（含目录、Executive Summary、Risk Control、DoD）+ 18 Epic / ~110 Task | 4 子阶段、Milestone + Architecture Review Gate、Iteration/Workflow/Change Mgmt/Review Checklist |
| 治理红线 | 显式 🧊 架构基线冻结(docs/21)、API 契约冻结(docs/13)、WS 协议冻结(docs/14)、13 ADR 冻结、**ADR-014~019 Draft** | 冻结内容表 + Frozen ADR 速查表（同样含 13 ADR 冻结 / Draft 014~019 参考） |

**LOCAL 有而 REMOTE 缺失的内容（已从 diff 确认）：**
- LOCAL §2.3「**Draft ADR 处理原则**」（lines 70-76：标记 `⚠️ [设计依赖 Draft ADR-0XX]`、优先用 Approved ADR 兼容方向、请求 PO 确认状态）—— REMOTE 仅有一句 "Draft ADR（014~019）仅作方向参考"，**无处理流程**。
- LOCAL 的**逐 Epic ADR 映射表**（lines 235-243：E-INFRA→ADR-017/019、E-DB→ADR-012/013/014、E-AUTH→ADR-002、E-TASK→ADR-009、E-API→ADR-019 等）。
- 技术选型风险的**具体表述**（见 A3）。

**REMOTE 有而 LOCAL 缺失的内容：** 重构后的 4 子阶段路线图、`Architecture Review Gate`（每 Milestone 强制 CTO/合规/风险评审）、Iteration/Workflow/Change Mgmt/Review Checklist 章节。

> 注意一个关键事实：REMOTE 的版本号（v3.0 / 07-11）**高于** LOCAL（v1.0 / 07-10）。即"另一台电脑的版本"在时间线上是**更新的重构版**，而非更早的旧版。这与"本地=我们治理版、远端=旧版"的预设不完全一致，仅供参考。

### A2. 当前工作区（751938e 之后）实际生效的是哪一版？

**结论：工作树中的 `docs/22` 与 REMOTE（d44093a）字节级完全相同，不是两者合并的结果。**

证据（SHA-256）：
```
remote (d44093a): 3D533D5F1A80A76FC6BA1FA0164736C2EEA0FED9EDEC5A2BB290E4DEE2228A79
HEAD   (751938e): 3D533D5F1A80A76FC6BA1FA0164736C2EEA0FED9EDEC5A2BB290E4DEE2228A79
IDENTICAL? True
local  (e00036a): CD3CCE6BB5D40416AA20EC99060C8AC6BFC9D04093FE4227BB075F89D979DFA5  (differ)
```
- `git status --porcelain docs/22_*.md` 为空 → 工作树 == HEAD（干净）。
- 因此 merge `751938e` 在 `docs/22` 上**取了远端一侧**（REMOTE 的 593 行 v3.0 版本），LOCAL 的 1114 行治理版未进入合并结果，目前仅作为 `e00036a` 提交历史中的一个孤立版本存在。

### A3. LOCAL 中与 33 条风险治理直接相关的内容，是否在最终版丢失/被覆盖成旧信息？

- **ADR 状态（13 条冻结 + Draft 014~019 参考）：保留。** HEAD/REMOTE 仍明确写有 "⛔ 13 条 Frozen ADR 不可绕过" 与 "Draft ADR（014~019）仅作方向参考"（lines 26、56）。核心冻结信息**未丢失**。
- **Draft ADR 处理流程（§2.3）：丢失。** HEAD 无 LOCAL 的 3 步处理原则。
- **逐 Epic ADR 映射表：丢失。** HEAD 的 Epic 表（lines 225-229）无 per-Epic ADR 关联列。
- **技术栈决策（具体风险表述）：被覆盖为更笼统的旧表述。** 这是最明确的回退点：
  - LOCAL line 1028：`ARC-15-P1-001 | 技术选型表中 8 项 undefined（ADR-014~019 逐条技术确认未完成）`
  - HEAD/REMOTE line 534：`ARC-15-P1-001 | 技术选型表冲突`

  → 即 LOCAL 经过 33 条风险治理后写出的**具体**描述（"8 项 undefined / ADR-014~019 逐条确认未完成"）在 HEAD 中被**回退为笼统的"技术选型表冲突"**。属"覆盖成旧/不具体信息"。

**小结：** ADR 冻结状态本身未丢；但 LOCAL 的治理增量（Draft ADR 处理流程、逐 Epic ADR 映射、技术选型风险的具体措辞）在合并后未进入工作树，其中技术选型风险被回退为更笼统的表述。

---

## Part B：src/zhiming 与 src/core 关系现状确认

**原始命令（已执行）：** `cat pyproject.toml` / `cat requirements.txt` / `find tests/ -type f` / `cat src/zhiming/bazi/__init__.py`

### B1. pyproject.toml 与 requirements.txt 是否冲突？

**无版本冲突，但是两套互不重叠、且存在覆盖缺口的依赖声明。**

- `pyproject.toml`（runtime）：`fastapi>=0.111.0, uvicorn[standard]>=0.29.0, pydantic>=2.7.0, pydantic-settings>=2.2.0, structlog>=24.1.0`；optional: `dev`(pytest/pytest-asyncio/ruff/mypy)、`db`(sqlalchemy/alembic)、`ai`(httpx/websockets)。
- `requirements.txt`：`lunar_python==1.4.8`（注释：由 Sprint 33「bazi_core.py 正式迁移」创建）。
- **冲突判定：** 两个文件**没有任何包被声明两次且版本不同**，因此不存在版本冲突。
- **但存在不一致/缺口：**
  1. `lunar_python`（src/core 的 `LunarBaziEngine` 实际依赖，`engine_info` 中 `engine_version: "1.4.8"`）**只出现在 requirements.txt，未出现在 pyproject.toml**。
  2. pyproject 的 web/API 依赖（fastapi 等）**未出现在 requirements.txt**。
  3. 两者各自独立维护，包集合几乎不相交。

### B2. tests/（远端带来）与 src/core 的 self_check 内联脚本——是否两套测试体系？

**是，目前确为两套并存的测试范式。**

- `tests/`（来自远端脚手架）：`tests/conftest.py`、`tests/__init__.py`、`tests/boot/test_logging.py`、`tests/boot/test_settings.py` —— **pytest 风格**，覆盖 `src/zhiming` 的 boot.logging / boot.settings。
- `src/core`：grep 显示仅 `src/core/domain/interfaces/bazi_engine.py` 与 `src/core/infrastructure/bazi/engine.py` 含 `self_check` / `if __name__` 模式 —— 即**内联 self_check 脚本风格**（`python engine.py` 直接跑自检），非 pytest。
- 事实记录：两套测试体系目前并存，是否将 `src/core` 迁移到 pytest 风格属后续待决事项（本 Sprint 只核实、不给建议）。

### B3. src/zhiming/bazi/__init__.py 的 docstring vs src/core 的 BaziEngine ABC——相同还是不同方案？

**是不同的设计思路。** `src/zhiming/bazi/` 目录**仅含 `__init__.py`（680 字节，纯 docstring，无代码）**。完整 docstring 如下：

```python
"""
Bazi (Four Pillars of Destiny) calculation engine.

Computes the Heavenly Stems (天干) and Earthly Branches (地支) for year,
month, day, and hour pillars from a given birth date/time.

Responsibilities:
    - Solar year / month conversion (accurate calendrical algorithms)
    - Day pillar calculation (days since a known epoch)
    - Hour pillar determination from birth hour + day stem
    - Unknown birth time handling (hour omitted / scanning)
    - Solar time correction (真太阳时)
    - Da Yun (大运) and Liu Nian (流年) calculation
    - Wu Xing (五行) composition and Shi Shen (十神) mapping

Implemented in E-BAZI Iterations 1-5.
"""
```

对比 `src/core` 现有设计（`src/core/domain/interfaces/bazi_engine.py`）：

```python
class BaziEngine(ABC):
    @abstractmethod
    def paipan(self, request: BaZiRequest) -> BaZiResult: ...
    @abstractmethod
    def validate(self, request: BaZiRequest) -> list[str]: ...
    @property
    @abstractmethod
    def engine_info(self) -> dict:
        """返回引擎能力声明，至少包含：
        handles_jieqi / handles_lichun / handles_mean_solar_time /
        handles_equation_of_time / supports_yongshen"""
    def self_check(self) -> list[str]:  # 默认空实现，强制验证立春/惊蛰边界
        return []
```

差异要点（事实记录，非评价）：
1. **成熟度不同：** `src/core` 已是**可运行的 ABC + 具体实现**（`LunarBaziEngine` 继承 `BaziEngine`，用 `lunar_python` 实现 `paipan/validate/engine_info`，含 6 个边界 case 的 `self_check`）；`src/zhiming/bazi` 仅是**规划 stub**，未实现任何代码。
2. **架构思路不同：** `src/core` 采用「抽象接口(ABC) + 能力声明(engine_info 契约) + 强制 self_check 闸门 + 模型/服务/基础设施分层」；`src/zhiming/bazi` 的 docstring 是**单体模块式职责清单**（把四柱/真太阳时/大运/流年/五行/十神全部列为单一引擎职责，计划 "E-BAZI Iterations 1-5" 实现）。
3. **契约意识不同：** `src/zhiming/bazi` 的 docstring **未提及** `engine_info` 能力声明契约，也**未提及** `self_check` 闸门——说明它与 `src/core` 在 Sprint 33-37 引入的 `BaziEngine` ABC 是**独立设计**的，且似乎未对齐该接口契约。
4. **范围有重叠也有差异：** 两者都覆盖四柱/真太阳时/未知出生时；但 `src/core` 当前 `engine_info` 声明 `handles_equation_of_time: False`、`supports_yongshen: False`（均时差、用神未实现），而 `src/zhiming/bazi` 把「大运/流年/五行/十神」列入职责范围——即 zhiming 的规划范围比 core 当前实现更广。

---

## 附录：原始输出摘录（核实证据）

**A. 行数 / 哈希**
```
local (e00036a): 1114 lines
remote (d44093a): 593 lines
HEAD (751938e) docs/22: 593 lines, 首行 "# 22 — Phase 3 Development Plan（开发执行计划）"
remote hash = HEAD hash = 3D533D5F...E2228A79  → IDENTICAL
local  hash = CD3CCE6B...979DFA5               → differ
working tree docs/22 vs HEAD: 空（干净）
```

**B. docs/22 真实文本 diff（LOCAL→REMOTE，difflib 解码 UTF-16 后，节选）**
```
@@ -1,21 +1,8 @@
-# 22 — Phase 3 Development Plan
-> 版本: v1.0 | 日期: 2026-07-10 | 状态: ✅ Active
-> 治理角色: Project Architect | Agent ID: Agent-20260710-02
-> 基于: Architecture Freeze (docs/21) | Product Owner Approval (docs/20) | 全部 P0 Closed
-> 基线文档: docs/08, docs/13, docs/14, docs/19, ADR-001~012 & ADR-020
+# 22 — Phase 3 Development Plan（开发执行计划）
+> 版本: v3.0 | 日期: 2026-07-11 | 状态: ✅ Approved
+> 角色: Documentation Engineer — 基于 Project Architect v2.0 重构
+> 关联文档: [08_系统架构] | [13_API接口契约] | [14_WS协议] | [19_分层记忆架构] | [21_架构冻结声明] | [04_ADR]
@@ -25,20 +12,16 @@
-**硬约束：** 🧊 架构基线已冻结 / 🧊 API 契约已冻结 / 🧊 WS 协议已冻结
- 🧊 13 条 ADR 已批准冻结（ADR-001~012 & ADR-020）—— 不可绕过
- 📝 ADR-014~019 为 Draft 状态，仅作设计参考
- 🟡 17 项 P1 + 9 项 P2 风险开放
- 路线：3 子阶段 / 5 里程碑 / 18 Epic / ~110 Task
+ 核心约束: 🧊 Architecture Freeze 不可违反 / 📜 API Contract 不可修改 / ⛔ 13 条 Frozen ADR 不可绕过
@@ -48,1067 +31,563 @@
-### 2.1 不可违反的红线（Hard Rules）   [LOCAL 详细表]
+### 2.1 禁止修改的冻结内容           [REMOTE 冻结内容表 + Frozen ADR 速查表]
...（LOCAL 大量 Executive Summary / 9 章节 / 逐 Epic ADR 映射 / Risk Control / DoD 被 REMOTE 的
    4 子阶段路线图 + Architecture Review Gate + Iteration/Workflow/Change Mgmt/Review Checklist 取代）
```
（完整 diff 共 1694 行；上述为头部节选，已覆盖 A1/A3 结论。）

**C. pyproject.toml（节选）/ requirements.txt**
```
[project] name="zhiming" version="0.1.0" requires-python=">=3.11"
dependencies = [fastapi>=0.111.0, uvicorn[standard]>=0.29.0, pydantic>=2.7.0,
               pydantic-settings>=2.2.0, structlog>=24.1.0]
[project.optional-dependencies] dev=[pytest>=8.0, pytest-asyncio>=0.23, ruff>=0.4.0, mypy>=1.9]
                              db=[sqlalchemy>=2.0, alembic>=1.13]  ai=[httpx>=0.27, websockets>=12.0]
[tool.pytest.ini_options] testpaths=["tests"] asyncio_mode="auto"

requirements.txt:
lunar_python==1.4.8   # 由 Sprint 33（bazi_core.py 正式迁移）创建
```

**D. tests/ 树 & src/zhiming 结构**
```
tests/conftest.py
tests/__init__.py
tests/boot/__init__.py
tests/boot/test_logging.py
tests/boot/test_settings.py
# src/zhiming 含: app_factory, __main__, boot/{logging,settings}, db/, ai/, api/, domain/,
#   infra/, memory/, prompt/, repository/, rule/, service/, task/, bazi/__init__.py(仅 docstring)
```
