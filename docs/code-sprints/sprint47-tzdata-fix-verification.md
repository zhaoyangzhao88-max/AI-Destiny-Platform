# Sprint 47 — tzdata 依赖补全 + 全新 venv 验证

- **日期：** 2026-07-20
- **范围：** 仅将 `tzdata>=2024.1` 补充进 `pyproject.toml` 的 `[project] dependencies`，并用 Sprint 45/46 同款的「全新 venv 仅按 pyproject.toml 安装」方法验证 Sprint 46 锁定的根因（缺 `tzdata`）被彻底消除。
- **改动性质：** 纯声明式依赖补充，无任何业务逻辑代码改动；**未改动** `paipan.py` 的 `except` 静默退化逻辑（那是 Sprint 48 的事）。
- **提交策略：** 本 Sprint 不作 git 提交检查点（按铁律不自动 commit）。

---

## 一、任务描述

Sprint 46 已决定性证明：`pyproject.toml` 缺少 `tzdata` 运行时依赖是 Sprint 45 干净 venv 暴露出的 5 项 self_check 失败的**直接根因**——`zoneinfo.ZoneInfo('Asia/Shanghai')` 在 Windows / 无系统时区数据库的 venv 中抛 `ZoneInfoNotFoundError`，被 `paipan.py` 的 `except` 静默退化为 `std_offset_hours = 0.0`，导致真太阳时修正量整体错位。

本 Sprint 只做「治标（依赖声明）」这一步（Sprint 46 报告 §5 下一步修复方向 #1）：在 `dependencies` 中声明 `"tzdata>=2024.1"`，与文件既有 `>=` 约束风格一致；然后用与 Sprint 45/46 完全相同的全新干净环境方法验证问题确实消失。

**具体操作：**
1. 在 `pyproject.toml` 的 `dependencies` 列表新增 `"tzdata>=2024.1"`（版本约束风格与 `lunar_python>=1.4.8` 等既有 `>=` 约束一致）。
2. 复用 Sprint 45/46 的验证方法：创建全新 venv（从未手动装过 tzdata）→ 仅按 `pyproject.toml` `pip install -e .` → `pip show tzdata` → 运行 `python src/core/infrastructure/bazi/engine.py` 跑 self_check。

---

## 二、pyproject.toml 改动 diff

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 8ea8f99..xxxxxxxx 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -21,6 +21,7 @@ dependencies = [
     "structlog>=24.1.0",
     "lunar_python>=1.4.8",
+    "tzdata>=2024.1",
 ]
```

> 注：修改前已读实际文件确认——`pyproject.toml` 所有既有依赖均用 `>=` 风格（如 `fastapi>=0.111.0`、`lunar_python>=1.4.8`），本次新增 `tzdata>=2024.1` 与文件实际风格完全一致。除该行外，其余 `dependencies` 项、`[build-system]`、`[project.optional-dependencies]`、`[tool.*]` 段落均未改动。

---

## 三、全新虚拟环境安装的完整原始输出

> **环境说明：** 本验证使用一个**全新** venv `venv_sprint47_test`，创建前该目录不存在，从未手动装过 `tzdata`。这与 Sprint 45 创建 `venv_sprint45_test` 后、Sprint 46 又在其内诊断性装上 `tzdata` 的环境**不同**——本环境证明：仅声明依赖、无需任何手动补装，即可获得时区数据。
>
> **编码说明：** 同 Sprint 45 报告，运行 self_check 时设置 `PYTHONIOENCODING=utf-8`，以下为程序向 UTF-8 流写入的真实内容（非终端 GBK 显示层复述）。

### 3.1 前置：创建 venv 并激活（bash / Git Bash）

```text
=== python -m venv venv_sprint47_test ===
venv create exit: 0
=== venv activated: /e/VSCODE/AI-Destiny-Platform/venv_sprint47_test/Scripts/python ===
```

### 3.2 `pip install -e .`（仅依赖 pyproject.toml，未引用 requirements.txt）

```text
=== pip install -e . ===
Obtaining file:///E:/VSCODE/AI-Destiny-Platform
  Installing build dependencies: started
  Installing build dependencies: finished with status 'done'
  Checking if build backend supports build_editable: started
  Checking if build backend supports build_editable: finished with status 'done'
  Getting requirements to build editable: started
  Getting requirements to build editable: finished with status 'done'
  Preparing editable metadata (pyproject.toml): started
  Preparing editable metadata (pyproject.toml): finished with status 'done'
Collecting fastapi>=0.111.0 (from zhiming==0.1.0)
  Using cached fastapi-0.139.2-py3-none-any.whl.metadata (26 kB)
Collecting uvicorn>=0.29.0 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached uvicorn-0.51.0-py3-none-any.whl.metadata (6.6 kB)
Collecting pydantic>=2.7.0 (from zhiming==0.1.0)
  Using cached pydantic-2.13.4-py3-none-any.whl.metadata (109 kB)
Collecting pydantic-settings>=2.2.0 (from zhiming==0.1.0)
  Using cached pydantic_settings-2.14.2-py3-none-any.whl.metadata (3.4 kB)
Collecting structlog>=24.1.0 (from zhiming==0.1.0)
  Using cached structlog-26.1.0-py3-none-any.whl.metadata (9.7 kB)
Collecting lunar_python>=1.4.8 (from zhiming==0.1.0)
  Using cached lunar_python-1.4.8-py3-none-any.whl
Collecting tzdata>=2024.1 (from zhiming==0.1.0)
  Using cached tzdata-2026.3-py2.py3-none-any.whl.metadata (1.4 kB)
Collecting starlette>=0.46.0 (from fastapi>=0.111.0->zhiming==0.1.0)
  Using cached starlette-1.3.1-py3-none-any.whl.metadata (6.4 kB)
Collecting typing-extensions>=4.8.0 (from fastapi>=0.111.0->zhiming==0.1.0)
  Using cached typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting typing-inspection>=0.4.2 (from fastapi>=0.111.0->zhiming==0.1.0)
  Using cached typing_inspection-0.4.2-py3-none-any.whl.metadata (2.6 kB)
Collecting annotated-doc>=0.0.2 (from fastapi>=0.111.0->zhiming==0.1.0)
  Using cached annotated_doc-0.0.4-py3-none-any.whl.metadata (6.6 kB)
Collecting annotated-types>=0.6.0 (from pydantic>=2.7.0->zhiming==0.1.0)
  Using cached annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.46.4 (from pydantic>=2.7.0->zhiming==0.1.0)
  Using cached pydantic_core-2.46.4-cp313-cp313-win_amd64.whl.metadata (6.7 kB)
Collecting python-dotenv>=0.21.0 (from pydantic-settings>=2.2.0->zhiming==0.1.0)
  Using cached python_dotenv-1.2.2-py3-none-any.whl.metadata (27 kB)
Collecting anyio<5,>=3.6.2 (from starlette>=0.46.0->fastapi>=0.111.0->zhiming==0.1.0)
  Using cached anyio-4.14.2-py3-none-any.whl.metadata (4.6 kB)
Collecting idna>=2.8 (from anyio<5,>=3.6.2->starlette>=0.46.0->fastapi>=0.111.0->zhiming==0.1.0)
  Using cached idna-3.18-py3-none-any.whl.metadata (6.1 kB)
Collecting click>=7.0 (from uvicorn>=0.29.0->uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
Collecting h11>=0.8 (from uvicorn>=0.29.0->uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.3 kB)
Collecting colorama (from click>=7.0->uvicorn>=0.29.0->uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Collecting httptools>=0.8.0 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached httptools-0.8.0-cp313-cp313-win_amd64.whl.metadata (3.7 kB)
Collecting pyyaml>=5.1 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached pyyaml-6.0.3-cp313-cp313-win_amd64.whl.metadata (2.4 kB)
Collecting watchfiles>=0.20 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached watchfiles-1.2.0-cp313-cp313-win_amd64.whl.metadata (5.0 kB)
Collecting websockets>=13.0 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Using cached websockets-16.1.1-cp313-cp313-win_amd64.whl.metadata (7.0 kB)
Using cached fastapi-0.139.2-py3-none-any.whl (130 kB)
Using cached annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
Using cached pydantic-2.13.4-py3-none-any.whl (472 kB)
Using cached pydantic_core-2.46.4-cp313-cp313-win_amd64.whl (2.1 MB)
Using cached annotated_types-0.7.0-py3-none-any.whl (13 kB)
Using cached pydantic_settings-2.14.2-py3-none-any.whl (61 kB)
Using cached python_dotenv-1.2.2-py3-none-any.whl (22 kB)
Using cached starlette-1.3.1-py3-none-any.whl (73 kB)
Using cached anyio-4.14.2-py3-none-any.whl (125 kB)
Using cached idna-3.18-py3-none-any.whl (65 kB)
Using cached structlog-26.1.0-py3-none-any.whl (73 kB)
Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Using cached typing_inspection-0.4.2-py3-none-any.whl (14 kB)
Using cached tzdata-2026.3-py2.py3-none-any.whl (348 kB)
Using cached uvicorn-0.51.0-py3-none-any.whl (73 kB)
Using cached click-8.4.2-py3-none-any.whl (119 kB)
Using cached h11-0.16.0-py3-none-any.whl (37 kB)
Using cached httptools-0.8.0-cp313-cp313-win_amd64.whl (90 kB)
Using cached pyyaml-6.0.3-cp313-cp313-win_amd64.whl (154 kB)
Using cached watchfiles-1.2.0-cp313-cp313-win_amd64.whl (288 kB)
Using cached websockets-16.1.1-cp313-cp313-win_amd64.whl (180 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Building wheels for collected packages: zhiming
  Building editable for zhiming (pyproject.toml): started
  Building editable for zhiming (pyproject.toml): finished with status 'done'
  Created wheel for zhiming: filename=zhiming-0.1.0-0.editable-py3-none-any.whl size=1482 sha256=c0fc952cba51b0344fb08691efecbd789d2db9f3080347f5d6ca093beefa17bc
  Stored in directory: C:\Users\DELL\AppData\Local\Temp\pip-ephem-wheel-cache-beb79uyz\wheels\8d\4a\79\d9f71d8a1643c0b0c86e67aeaa8cdade52c5934a4142f81af1
Successfully built zhiming
Installing collected packages: lunar_python, websockets, tzdata, typing-extensions, structlog, pyyaml, python-dotenv, idna, httptools, h11, colorama, annotated-types, annotated-doc, typing-inspection, pydantic-core, click, anyio, watchfiles, uvicorn, starlette, pydantic, pydantic-settings, fastapi, zhiming

Successfully installed annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.14.2 click-8.4.2 colorama-0.4.6 fastapi-0.139.2 h11-0.16.0 httptools-0.8.0 idna-3.18 lunar_python-1.4.8 pydantic-2.13.4 pydantic-core-2.46.4 pydantic-settings-2.14.2 python-dotenv-1.2.2 pyyaml-6.0.3 starlette-1.3.1 structlog-26.1.0 typing-extensions-4.16.0 typing-inspection-0.4.2 tzdata-2026.3 uvicorn-0.51.0 watchfiles-1.2.0 websockets-16.1.1 zhiming-0.1.0

[notice] A new release of pip available: 25.2 -> 26.1.2
[notice] To update, run: python.exe -m pip install --upgrade pip
=== pip install -e . EXIT CODE: 0 ===
```

> **关键验证点已达成：** `tzdata>=2024.1 (from zhiming==0.1.0)` 被收集，并最终 `Successfully installed ... tzdata-2026.3 ...`。这表明 `tzdata` 是作为本包（`zhiming`，由 `pyproject.toml` 描述）的依赖**自动安装**的——**完全未引用 `requirements.txt`，也无需任何手动补装**。Sprint 47 的核心目标（仅声明依赖即可在干净环境获得 tzdata）已验证通过。

### 3.3 `pip show tzdata`

```text
=== pip show tzdata ===
Name: tzdata
Version: 2026.3
Summary: Provider of IANA time zone data
Home-page: https://github.com/python/tzdata
Author: Python Software Foundation
Author-email: datetime-sig@python.org
License: Apache-2.0
Location: E:\VSCODE\AI-Destiny-Platform\venv_sprint47_test\Lib\site-packages
Requires:
Required-by: zhiming
=== pip show tzdata EXIT CODE: 0 ===
```

> `Required-by: zhiming` 确认：`tzdata` 由本包依赖引入，驱动源是 `pyproject.toml`（满足 `tzdata>=2024.1` 约束，解析到最新 2026.3）。版本由 `>=` 约束解析，符合预期。

### 3.4 self_check 在新环境下的完整原始输出

运行命令：`python src/core/infrastructure/bazi/engine.py`（在全新 `venv_sprint47_test` 内，仅按 `pyproject.toml` 安装）。

```text
=== self_check (UTF-8) START ===
PASS 立春前年柱: 2024-02-03 12:00 -> 癸卯
PASS 立春后年柱: 2024-02-04 20:00 -> 甲辰
PASS 惊蛰前月柱: 2024-03-05 09:00 → 丙寅
PASS 惊蛰后月柱: 2024-03-05 12:00 → 丁卯
PASS 1990-08-15 12:00 年柱: 庚午
PASS 1990-08-15 12:00 月柱: 甲申
PASS 1990-08-15 12:00 日柱: 壬子
PASS 1990-08-15 12:00 时柱: 丙午
PASS 1990-08-15 12:00 日主: 壬
PASS gender=unknown 四柱/日主与 male 完全一致
PASS gender=unknown great_fortune_direction_undetermined == True
PASS gender=male great_fortune_direction_undetermined == False
PASS 乌鲁木齐02:00 真太阳时日柱(跨日回退): 辛亥
PASS 乌鲁木齐02:00 真太阳时时柱(子时): 庚子
PASS 乌鲁木齐13:00 真太阳时日柱(同日): 壬子
PASS 乌鲁木齐13:00 真太阳时时柱(巳时翻转): 乙巳

OK self_check: 全部通过!
=== self_check EXIT CODE: 0 ===
```

> **决定性结果：** 全新、从未手动装过 `tzdata` 的干净环境，仅声明依赖即自动装上 `tzdata`，self_check **16/16 全部 PASS**（`OK self_check: 全部通过!`，exit code 0）。
>
> 与 Sprint 45（同一方法、未声明 tzdata 时 11 PASS / 5 FAIL）和 Sprint 46（诊断性手动补装 tzdata 后 16/16 PASS）对比，唯一变量是 `pyproject.toml` 现在声明了 `tzdata>=2024.1`——本 Sprint 证明这条声明足以让干净环境自助获得时区数据，无需任何手动干预。此前 5 项失败（惊蛰前月柱、时柱、乌鲁木齐 02:00/13:00 真太阳时日柱/时柱）全部消失。
>
> 此结果同时也**正面回应了 Sprint 45 §6.2 的疑虑**：那 5 项失败并非引擎算法 bug，而是依赖声明缺口（缺 tzdata）被 `paipan.py` 的 `except` 静默退化掩盖所致。

---

## 四、self_check 逐用例对照（Sprint 45 失败项 → 本 Sprint）

| # | 用例 | Sprint 45（无 tzdata） | 本 Sprint（声明 tzdata） |
|---|------|------------------------|--------------------------|
| 1 | 立春前年柱 2024-02-03 12:00 | PASS 癸卯 | PASS 癸卯 |
| 2 | 立春后年柱 2024-02-04 20:00 | PASS 甲辰 | PASS 甲辰 |
| 3 | 惊蛰前月柱 2024-03-05 09:00 | **FAIL**（实际 丁卯，预期 丙寅） | PASS 丙寅 ✅ |
| 4 | 惊蛰后月柱 2024-03-05 12:00 | PASS 丁卯 | PASS 丁卯 |
| 5 | 1990-08-15 12:00 年柱 | PASS 庚午 | PASS 庚午 |
| 6 | 1990-08-15 12:00 月柱 | PASS 甲申 | PASS 甲申 |
| 7 | 1990-08-15 12:00 日柱 | PASS 壬子 | PASS 壬子 |
| 8 | 1990-08-15 12:00 时柱 | **FAIL**（实际 庚戌，预期 丙午） | PASS 丙午 ✅ |
| 9 | 1990-08-15 12:00 日主 | PASS 壬 | PASS 壬 |
| 10 | gender=unknown 四柱/日主一致 | PASS | PASS |
| 11 | gender=unknown 大运方向待定 | PASS True | PASS True |
| 12 | gender=male 大运方向待定 | PASS False | PASS False |
| 13 | 乌鲁木齐02:00 真太阳时日柱 | **FAIL**（实际 壬子，预期 辛亥） | PASS 辛亥 ✅ |
| 14 | 乌鲁木齐02:00 真太阳时时柱 | **FAIL**（实际 甲辰，预期 庚子） | PASS 庚子 ✅ |
| 15 | 乌鲁木齐13:00 真太阳时日柱 | PASS 壬子 | PASS 壬子 |
| 16 | 乌鲁木齐13:00 真太阳时时柱 | **FAIL**（实际 己酉，预期 乙巳） | PASS 乙巳 ✅ |

**合计：Sprint 45 = 11 PASS / 5 FAIL；本 Sprint = 16 PASS / 0 FAIL。**

---

## 五、文件系统证据（改动后 pyproject.toml 完整 [project] 段落）

```toml
[project]
# zhì mìng — 知命 AI 人生档案顾问
name = "zhiming"
version = "0.1.0"
description = "ZhiMing AI — Life Archive Consultant Core Service"
requires-python = ">=3.11"
license = { text = "Proprietary" }

# Core runtime dependencies — kept minimal for Phase 3.1 bootstrap.
# Additional deps will be added per Epic as development progresses.
dependencies = [
    "fastapi>=0.111.0",
    "uvicorn[standard]>=0.29.0",
    "pydantic>=2.7.0",
    "pydantic-settings>=2.2.0",
    "structlog>=24.1.0",
    "lunar_python>=1.4.8",
    "tzdata>=2024.1",
]
```

> 新增的第 23 行 `"tzdata>=2024.1"` 已落地。其余段落（`[build-system]`、`[project.optional-dependencies]`、`[tool.*]`）均未改动。

---

## 六、审核摘要：是否发现新问题

### 6.1 本 Sprint 目标达成情况

| 验收项 | 结果 |
|--------|------|
| `pyproject.toml` 新增 `tzdata>=2024.1` | ✅ 已完成（风格与文件既有 `>=` 约束一致） |
| 全新 venv 仅用 pyproject.toml 自动装上 `tzdata` | ✅ 验证通过（`Required-by: zhiming`，解析到 2026.3） |
| self_check 在干净环境 16/16 全部 PASS | ✅ 验证通过（`OK self_check: 全部通过!`，exit 0） |
| 无业务逻辑改动 | ✅ `paipan.py` 等零改动；仅改 `pyproject.toml` 一行 |
| 未触动 `paipan.py` 的 `except` 静默退化 | ✅ 按范围保留，留待 Sprint 48 处理 |

### 6.2 是否引入新问题

**否。** 本 Sprint 仅新增一行声明式依赖，依存解析（`lunar_python` 仍为 1.4.8、`fastapi`/`pydantic` 等与 Sprint 45 解析版本一致）无任何意外。全新 venv 验证结果与 Sprint 46 手动补装 tzdata 后的预期完全一致（16/16 PASS），证明根因已被声明层消除。

### 6.3 仍遗留的健壮性隐患（非本 Sprint 引入，明确留给 Sprint 48）

- **`paipan.py` 的 `except Exception: std_offset_hours = 0.0` 静默退化**：本 Sprint 治标后，正常环境不会再触发该分支；但该分支仍会在「tzdata 再次缺失」等异常情况下用 0 修正产出**看似合理但错误**的结果，掩盖依赖缺失。建议 Sprint 48 改为 fail-fast（导入期/初始化期显式报错）或至少记录 warning 日志。
- **`requirements.txt` 是否需同步**：Sprint 45 已决定保持 `requirements.txt` 与 `pyproject.toml` 暂不统一，本 Sprint 维持该决定，`requirements.txt` 未改动。若后续统一依赖源，需一并核对 `tzdata` 是否已在其中。

### 6.4 其他说明

- 测试用 venv `venv_sprint47_test/` 仍保留在仓库工作区，未删除（按铁律不擅自清理）；如不需要可后续手动删除或加入 `.gitignore`。
- 本 Sprint **未执行 git commit**（按铁律这次不作检查点）。如需提交，应连同 `pyproject.toml` 一行改动与 `docs/code-sprints/sprint47-tzdata-fix-verification.md` 一并展示 diff 后由用户确认。

---

*报告生成：Claude Code（Sprint 47 自动化执行）*
