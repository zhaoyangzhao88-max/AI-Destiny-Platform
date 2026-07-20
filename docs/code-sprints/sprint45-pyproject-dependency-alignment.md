# Sprint 45 — 依赖清单对齐（pyproject.toml 补充 lunar_python）

- **日期：** 2026-07-20
- **范围：** 仅将 `requirements.txt` 中已有的 `lunar_python` 依赖补充进 `pyproject.toml` 的 `[project] dependencies`，消除 Sprint 40 发现的依赖声明缺口。
- **改动性质：** 纯声明式依赖补充，无任何业务逻辑代码改动。
- **提交策略：** 本 Sprint 不作为 git 提交检查点（按铁律不自动 commit）。

---

## 一、任务描述

Sprint 40 发现 `pyproject.toml` 的运行时依赖列表缺少排盘引擎实际依赖的 `lunar_python`，而该依赖仅存在于 `requirements.txt`（`lunar_python==1.4.8`）。本次补上声明，使仅凭 `pyproject.toml` 即可完整安装排盘引擎所需依赖。

**具体操作：**
1. 在 `pyproject.toml` 的 `dependencies` 列表新增 `lunar_python>=1.4.8`
   - 版本约束风格：文件内既有依赖统一使用 `>=`（如 `fastapi>=0.111.0`），故本次采用 `>=1.4.8`，与文件实际风格一致。
2. `requirements.txt` 保留不变（统一成单一依赖文件属后续独立决策，本 Sprint 不做）。

---

## 二、pyproject.toml 改动 diff

```diff
diff --git a/pyproject.toml b/pyproject.toml
index 1b3ae20..8ea8f99 100644
--- a/pyproject.toml
+++ b/pyproject.toml
@@ -19,6 +19,7 @@ dependencies = [
     "pydantic>=2.7.0",
     "pydantic-settings>=2.2.0",
     "structlog>=24.1.0",
+    "lunar_python>=1.4.8",
 ]
 
 [project.optional-dependencies]
```

> 注：修改前已读实际文件确认——`pyproject.toml` 所有既有依赖均用 `>=` 风格，与任务要求一致，无需偏离文件实际风格。

---

## 三、全新虚拟环境安装的完整原始输出

### 3.1 前置：创建 venv 并激活（bash / Git Bash）

```text
python -m venv venv_sprint45_test
source venv_sprint45_test/Scripts/activate
=== venv activated: /e/VSCODE/AI-Destiny-Platform/venv_sprint45_test/Scripts/python ===
```

> 说明：`pip install --upgrade pip` 在 Windows venv 内因 `pip.exe` 占用自升级失败（exit 1，属已知 Windows 行为，与本次验证无关），已跳过；不影响 `pip install -e .` 主体验证。

### 3.2 `pip install -e .`（仅依赖 pyproject.toml，未引用 requirements.txt）

```text
=== pip install -e . START ===
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
  Downloading fastapi-0.139.2-py3-none-any.whl.metadata (26 kB)
Collecting uvicorn>=0.29.0 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Downloading uvicorn-0.51.0-py3-none-any.whl.metadata (6.6 kB)
Collecting pydantic>=2.7.0 (from zhiming==0.1.0)
  Downloading pydantic-2.13.4-py3-none-any.whl.metadata (109 kB)
Collecting pydantic-settings>=2.2.0 (from zhiming==0.1.0)
  Downloading pydantic_settings-2.14.2-py3-none-any.whl.metadata (3.4 kB)
Collecting structlog>=24.1.0 (from zhiming==0.1.0)
  Downloading structlog-26.1.0-py3-none-any.whl.metadata (9.7 kB)
Collecting lunar_python>=1.4.8 (from zhiming==0.1.0)
  Using cached lunar_python-1.4.8-py3-none-any.whl
Collecting starlette>=0.46.0 (from fastapi>=0.111.0->zhiming==0.1.0)
  Downloading starlette-1.3.1-py3-none-any.whl.metadata (6.4 kB)
Collecting typing-extensions>=4.8.0 (from fastapi>=0.111.0->zhiming==0.1.0)
  Using cached typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
Collecting typing-inspection>=0.4.2 (from fastapi>=0.111.0->zhiming==0.1.0)
  Downloading typing_inspection-0.4.2-py3-none-any.whl.metadata (2.6 kB)
Collecting annotated-doc>=0.0.2 (from fastapi>=0.111.0->zhiming==0.1.0)
  Downloading annotated_doc-0.0.4-py3-none-any.whl.metadata (6.6 kB)
Collecting annotated-types>=0.6.0 (from pydantic>=2.7.0->zhiming==0.1.0)
  Downloading annotated_types-0.7.0-py3-none-any.whl.metadata (15 kB)
Collecting pydantic-core==2.46.4 (from pydantic>=2.7.0->zhiming==0.1.0)
  Downloading pydantic_core-2.46.4-cp313-cp313-win_amd64.whl.metadata (6.7 kB)
Collecting python-dotenv>=0.21.0 (from pydantic-settings>=2.2.0->zhiming==0.1.0)
  Downloading python_dotenv-1.2.2-py3-none-any.whl.metadata (27 kB)
Collecting anyio<5,>=3.6.2 (from starlette>=0.46.0->fastapi>=0.111.0->zhiming==0.1.0)
  Downloading anyio-4.14.2-py3-none-any.whl.metadata (4.6 kB)
Collecting idna>=2.8 (from anyio<5,>=3.6.2->starlette>=0.46.0->fastapi>=0.111.0->zhiming==0.1.0)
  Using cached idna-3.18-py3-none-any.whl.metadata (6.1 kB)
Collecting click>=7.0 (from uvicorn>=0.29.0->zhiming==0.1.0)
  Downloading click-8.4.2-py3-none-any.whl.metadata (2.6 kB)
Collecting h11>=0.8 (from uvicorn>=0.29.0->zhiming==0.1.0)
  Using cached h11-0.16.0-py3-none-any.whl.metadata (8.1 kB)
Collecting colorama (from click>=7.0->uvicorn>=0.29.0->zhiming==0.1.0)
  Using cached colorama-0.4.6-py2.py3-none-any.whl.metadata (17 kB)
Collecting httptools>=0.8.0 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Downloading httptools-0.8.0-cp313-cp313-win_amd64.whl.metadata (3.7 kB)
Collecting pyyaml>=5.1 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Downloading pyyaml-6.0.3-cp313-cp313-win_amd64.whl.metadata (2.4 kB)
Collecting watchfiles>=0.20 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Downloading watchfiles-1.2.0-cp313-cp313-win_amd64.whl.metadata (5.0 kB)
Collecting websockets>=13.0 (from uvicorn[standard]>=0.29.0->zhiming==0.1.0)
  Downloading websockets-16.1.1-cp313-cp313-win_amd64.whl.metadata (7.0 kB)
Downloading fastapi-0.139.2-py3-none-any.whl (130 kB)
Downloading annotated_doc-0.0.4-py3-none-any.whl (5.3 kB)
Downloading pydantic-2.13.4-py3-none-any.whl (472 kB)
Downloading pydantic_core-2.46.4-cp313-cp313-win_amd64.whl (2.1 MB)
   ---------------------------------------- 2.1/2.1 MB 9.5 MB/s  0:00:00
Downloading annotated_types-0.7.0-py3-none-any.whl (13 kB)
Downloading pydantic_settings-2.14.2-py3-none-any.whl (61 kB)
Downloading python_dotenv-1.2.2-py3-none-any.whl (22 kB)
Downloading starlette-1.3.1-py3-none-any.whl (73 kB)
Downloading anyio-4.14.2-py3-none-any.whl (125 kB)
Using cached idna-3.18-py3-none-any.whl (65 kB)
Downloading structlog-26.1.0-py3-none-any.whl (73 kB)
Using cached typing_extensions-4.16.0-py3-none-any.whl (45 kB)
Downloading typing_inspection-0.4.2-py3-none-any.whl (14 kB)
Downloading uvicorn-0.51.0-py3-none-any.whl (73 kB)
Downloading click-8.4.2-py3-none-any.whl (119 kB)
Using cached h11-0.16.0-py3-none-any.whl (37 kB)
Downloading httptools-0.8.0-cp313-cp313-win_amd64.whl (90 kB)
Downloading pyyaml-6.0.3-cp313-cp313-win_amd64.whl (154 kB)
Downloading watchfiles-1.2.0-cp313-cp313-win_amd64.whl (288 kB)
Downloading websockets-16.1.1-cp313-cp313-win_amd64.whl (180 kB)
Using cached colorama-0.4.6-py2.py3-none-any.whl (25 kB)
Building wheels for collected packages: zhiming
  Building editable for zhiming (pyproject.toml): started
  Building editable for zhiming (pyproject.toml): finished with status 'done'
  Created wheel for zhiming: filename=zhiming-0.1.0-0.editable-py3-none-any.whl size=1472 sha256=c3540560c8b70ee6f23343cd8d3a52e8093790bb47cea5a85273fe68b08e5ff2
  Stored in directory: C:\Users\DELL\AppData\Local\Temp\pip-ephem-wheel-cache-ezhellnu\wheels\8d\4a\79\d9f71d8a1643c0b0c86e67aeaa8cdade52c5934a4142f81af1
Successfully built zhiming
Installing collected packages: lunar_python, websockets, typing-extensions, structlog, pyyaml, python-dotenv, idna, httptools, h11, colorama, annotated-types, annotated-doc, typing-inspection, pydantic-core, click, anyio, watchfiles, uvicorn, starlette, pydantic, pydantic-settings, fastapi, zhiming

Successfully installed annotated-doc-0.0.4 annotated-types-0.7.0 anyio-4.14.2 click-8.4.2 colorama-0.4.6 fastapi-0.139.2 h11-0.16.0 httptools-0.8.0 idna-3.18 lunar_python-1.4.8 pydantic-2.13.4 pydantic-core-2.46.4 pydantic-settings-2.14.2 python-dotenv-1.2.2 pyyaml-6.0.3 starlette-1.3.1 structlog-26.1.0 typing-extensions-4.16.0 typing-inspection-0.4.2 uvicorn-0.51.0 watchfiles-1.2.0 websockets-16.1.1 zhiming-0.1.0

[notice] A new release of pip is available: 25.2 -> 26.1.2
[notice] To update, run: python.exe -m pip install --upgrade pip
=== pip install -e . EXIT CODE: 0 ===
```

> **关键验证点已达成：** `lunar_python>=1.4.8 (from zhiming==0.1.0)` 被收集，并最终 `Successfully installed ... lunar_python-1.4.8 ...`。这表明 `lunar_python` 是作为本包（`zhiming`，由 `pyproject.toml` 描述）的依赖安装的，**完全未引用 `requirements.txt`**。Sprint 45 的核心目标（仅用 pyproject.toml 即可装上 lunar_python）已验证通过。

### 3.3 `pip show lunar_python`

```text
=== pip show lunar_python START ===
Name: lunar_python
Version: 1.4.8
Summary: lunar is a calendar library for Solar and Chinese Lunar.
Home-page: https://github.com/6tail/lunar-python
Author: 6tail
Author-email: 6tail@6tail.cn
License: MIT
Location: E:\VSCODE\AI-Destiny-Platform\venv_sprint45_test\Lib\site-packages
Requires:
Required-by: zhiming
=== pip show lunar_python EXIT CODE: 0 ===
```

> `Required-by: zhiming` 再次确认：`lunar_python` 由本包依赖引入，驱动源是 `pyproject.toml`。版本 1.4.8 与 `requirements.txt` 锁定值一致。

---

## 四、self_check 在新环境下的完整原始输出

运行命令：`python src/core/infrastructure/bazi/engine.py`（在 `venv_sprint45_test` 内）。

> **编码说明：** 首次运行在默认 GBK 代码页下中文显示为乱码（mojibake）。下列为设置 `PYTHONIOENCODING=utf-8` 后的真实程序输出（即程序向 UTF-8 流写入的内容，非复述）。乱码仅是终端显示编码问题，不影响程序逻辑与断言结果。

```text
=== self_check (UTF-8) START ===
PASS 立春前年柱: 2024-02-03 12:00 -> 癸卯
PASS 立春后年柱: 2024-02-04 20:00 -> 甲辰
PASS 惊蛰后月柱: 2024-03-05 12:00 → 丁卯
PASS 1990-08-15 12:00 年柱: 庚午
PASS 1990-08-15 12:00 月柱: 甲申
PASS 1990-08-15 12:00 日柱: 壬子
PASS 1990-08-15 12:00 日主: 壬
PASS gender=unknown 四柱/日主与 male 完全一致
PASS gender=unknown great_fortune_direction_undetermined == True
PASS gender=male great_fortune_direction_undetermined == False
PASS 乌鲁木齐13:00 真太阳时日柱(同日): 壬子

FAIL self_check: 5 项失败:
  - 惊蛰前月柱错误: 2024-03-05 09:00 → 预期 丙寅, 实际 丁卯
  - 1990-08-15 12:00 时柱错误: 预期 丙午, 实际 庚戌
  - FAIL 乌鲁木齐02:00 真太阳时日柱错误: 预期 辛亥, 实际 壬子
  - FAIL 乌鲁木齐02:00 真太阳时时柱错误: 预期 庚子(晚子时), 实际 甲辰
  - FAIL 乌鲁木齐13:00 真太阳时时柱错误: 预期 乙巳(巳时), 实际 己酉

=== self_check EXIT CODE: 0 ===
```

> exit code 为 0 是因为 `engine.py` 的 self_check 打印结果后直接 `sys.exit(0)`（或主流程未以失败码退出），**不代表测试全过**——程序自身已明确打印 `FAIL self_check: 5 项失败`。

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
]
```

> 其余段落（`[build-system]`、`[project.optional-dependencies]`、`[tool.*]`）均未改动，与改动前一致。

---

## 六、审核摘要：是否发现新问题

### 6.1 本 Sprint 目标达成情况

| 验收项 | 结果 |
|--------|------|
| `pyproject.toml` 新增 `lunar_python>=1.4.8` | ✅ 已完成（风格与文件既有 `>=` 约束一致） |
| 全新 venv 仅用 pyproject.toml 装上 `lunar_python` | ✅ 验证通过（`Required-by: zhiming`，版本 1.4.8） |
| `requirements.txt` 保持不变 | ✅ 未触碰 |
| 无业务逻辑改动 | ✅ `git diff` 确认仅改动 `pyproject.toml`（`engine.py` 零改动） |

### 6.2 ⚠️ 发现的新问题（如实报告，非本次引入，超出本 Sprint 范围）

**self_check 存在 5 项失败。** 这一结果与 git 历史中 `5ecf923`「所有代码改动均通过 self_check 验证（16项边界案例零回归）」的表述**相矛盾**。

**归因判断（重要）：**
- 本 Sprint 仅做声明式依赖补充，`lunar_python` 解析版本仍为 **1.4.8**（与 `requirements.txt` 锁定值完全相同），且 `git diff` 确认 `engine.py` 一行未改。
- 排盘引擎 self_check 仅依赖 `lunar_python`，与其他被拉入的运行时依赖（fastapi/pydantic 等）无关。
- 因此，这 5 项失败**不是本次改动引入的**，而是 `engine.py` 当前工作区代码已预存的问题（可能由 `engine.py` 后续编辑引入，该文件 mtime 为 2026-07-17，晚于上述“零回归”提交）。

**5 项失败清单（供后续独立 Sprint 跟进）：**
1. `惊蛰前月柱错误: 2024-03-05 09:00` → 预期 丙寅，实际 丁卯（惊蛰换月边界）
2. `1990-08-15 12:00 时柱错误` → 预期 丙午，实际 庚戌
3. `乌鲁木齐02:00 真太阳时日柱错误` → 预期 辛亥，实际 壬子
4. `乌鲁木齐02:00 真太阳时时柱错误` → 预期 庚子(晚子时)，实际 甲辰
5. `乌鲁木齐13:00 真太阳时时柱错误` → 预期 乙巳(巳时)，实际 己酉

**建议（不在本 Sprint 处理）：**
- 将“self_check 5 项失败”登记为独立 Bug Sprint，逐一核对预期值是否源于节气精确时刻/真太阳时经度校准逻辑，确认是测试用例预期写错还是引擎计算出错。
- 同时建议核正 `5ecf923` 提交中“零回归”表述与现实代码的偏差来源，避免后续治理误判。

### 6.3 其他说明
- `pip install --upgrade pip` 在 Windows venv 内自升级失败（exit 1）属已知 Windows 行为，与本验证无关，已跳过。
- 测试用 venv `venv_sprint45_test/` 仍保留在仓库工作区，未删除（按铁律不擅自清理）；如不需要可后续手动删除，或加入 `.gitignore`。

---

*报告生成：Claude Code（Sprint 45 自动化执行）*
