# Sprint 48 — 消除静默退化：时区解析失败改为 fail-fast

- **日期：** 2026-07-20
- **范围：** 仅改 `_true_solar_correction_minutes` 里 `except Exception: std_offset_hours = 0.0` 这一处行为，并新增一个 self_check 用例验证 fail-fast。新建一个领域异常类 `EngineCalculationError` 供其抛出。
- **改动性质：** 核心领域逻辑行为修正（fail-fast）+ 测试增强。无业务逻辑算法改动（排盘公式不变）。
- **前置依赖：** Sprint 47 已在 `pyproject.toml` 声明 `tzdata>=2024.1`（治标）；本 Sprint 治本（依赖缺失时显式报错而非静默算错）。
- **提交策略：** 本 Sprint 不作 git 提交检查点（按铁律不自动 commit）。

---

## 〇、关键前提校正（先说清，避免误判）

任务描述称「复用 08 §8.8.1 已定义的异常体系 / 比如 EngineCalculationError」。**经核实该前提不成立：**

- `docs/08_系统架构设计.md §8.8.1` 仅定义了 `BaziEngine` ABC 与 `BaZiRequest / Pillar / BaZiResult` 数据类，**没有任何异常类**。
- 全仓库 `grep -rn "class .*Error|class .*Exception" src/` **0 命中**。
- `src/zhiming/boot/__init__.py` 仅在 docstring 里 *提及* "define a hierarchical exception tree"（E-BOOT 脚手架，尚未实现），未定义任何异常。

→ **没有可「复用」的异常，必须新建。** 本 Sprint 新建 `core/domain/exceptions.py` 并定义 `EngineCalculationError`，与任务示例名一致，且放在领域层（失败发源地），符合项目分层架构。

---

## 一、任务描述

Sprint 46 锁定根因：`pyproject.toml` 缺 `tzdata` 时，`ZoneInfo('Asia/Shanghai')` 抛 `ZoneInfoNotFoundError`，被 `paipan.py` 的 `except Exception: std_offset_hours = 0.0` **静默吞掉**并退化为 0 修正，产出看似合理但错误的真太阳时结果（5 项 self_check 失败）。Sprint 47 已治标（补 `tzdata` 依赖声明）。

本 Sprint 治本：把「静默返回错误结果」改为「fail-fast 显式报错」，使今后任何时区解析失败（`tzdata` 缺失 / `timezone` 字符串非法）都在第一时间暴露，而不是安静地算错。

**具体操作：**
1. 新建 `core/domain/exceptions.py`，定义 `EngineCalculationError(Exception)` 领域异常类。
2. `paipan.py` 的 `_true_solar_correction_minutes`：`except` 分支由「`std_offset_hours = 0.0`」改为「抛 `EngineCalculationError`，信息含可操作提示（时区解析失败 + tzdata 未安装提示）」；用 `from exc` 保留底层错误链，但主信息是中文可操作提示，不只转发 Python 底层报错。
3. `engine.py` 的 `self_check` 新增「测试 7」：传入不存在的 `timezone="Not/A_Real_Zone"`，验证显式抛 `EngineCalculationError`（而非静默返回错误结果），并入完整 self_check 一起跑。

---

## 二、pyproject.toml / 源码改动 diff

### 2.1 新建 `src/core/domain/exceptions.py`

```diff
+"""排盘领域异常体系（领域层）。
+
+计算失败时抛出显式异常，使调用方（API 层 / self_check）能拿到可操作的定位信息，
+而非底层库原始报错或静默的错误结果。
+
+注：docs/08 §8.8.1 仅定义 BaziEngine 接口与数据类、未定义异常；本模块为 Sprint 48 补齐。
+"""
+
+
+class EngineCalculationError(Exception):
+    """排盘计算领域级错误（时区解析失败 / 真太阳时校准无法继续等）。
+
+    异常信息须携带可操作的定位提示（如提示 tzdata 未安装）。
+    """
+    pass
```

### 2.2 `src/core/domain/services/paipan.py`

```diff
 from lunar_python import Solar
 
+from core.domain.exceptions import EngineCalculationError
 from core.domain.models.bazi_chart import BaZiRequest, BaZiResult, Pillar
 from core.infrastructure.bazi.constants import HIDDEN_STEMS_MAP
@@ -42,9 +43,15 @@ def _true_solar_correction_minutes(request: BaZiRequest) -> float:
         std_offset_hours = (
             tz.utcoffset(dt) - tz.dst(dt)
         ).total_seconds() / 3600.0
-    except Exception:
-        # 时区解析失败：退化为 0 修正，避免崩溃（合法 timezone 不应触发）
-        std_offset_hours = 0.0
+    except Exception as exc:
+        # Sprint 48 fail-fast：不再静默退化为 0 修正
+        # （0 修正会产出看似合理但错误的真太阳时，掩盖依赖缺失）
+        raise EngineCalculationError(
+            f"时区解析失败: timezone='{request.timezone}'。"
+            f"无法获取标准时区偏移，真太阳时校准无法继续。"
+            f"常见原因：tzdata 时区数据库未安装（pip install tzdata），"
+            f"或 timezone 字符串非法。原始错误: {exc}"
+        ) from exc
     standard_meridian = std_offset_hours * 15.0
     return (request.longitude - standard_meridian) * 4.0
```

### 2.3 `src/core/infrastructure/bazi/engine.py`

```diff
+from core.domain.exceptions import EngineCalculationError  # noqa: E402
 from core.domain.interfaces.bazi_engine import BaziEngine  # noqa: E402
 from core.domain.models.bazi_chart import BaZiRequest, BaZiResult  # noqa: E402
 from core.domain.services.paipan import calculate_bazi  # noqa: E402
@@ -267,6 +268,26 @@ class LunarBaziEngine(BaziEngine):
         else:
             print(f"PASS 乌鲁木齐13:00 真太阳时时柱(巳时翻转): {uq5_t}")
 
+        # ── 测试 7: 非法 timezone 应显式报错（fail-fast, Sprint 48） ──
+        # 传入不存在的时区字符串，验证不再静默返回错误结果，
+        # 而是抛出 EngineCalculationError。
+        try:
+            engine.paipan(_req(1990, 8, 15, 12, 0, timezone="Not/A_Real_Zone"))
+            # 若未抛异常，说明仍在静默返回错误结果
+            failures.append(
+                "FAIL 非法 timezone 未显式报错（仍静默返回错误结果，违反 fail-fast 原则）"
+            )
+        except EngineCalculationError as exc:
+            print(
+                f"PASS 非法 timezone 显式报错: timezone='Not/A_Real_Zone' "
+                f"-> {type(exc).__name__}: {exc}"
+            )
+        except Exception as exc:
+            failures.append(
+                f"FAIL 非法 timezone 抛出了非预期异常类型: "
+                f"{type(exc).__name__}: {exc}"
+            )
+
         # ── 汇总 ──
         if not failures:
             print("\nOK self_check: 全部通过!")
```

> 注：`git diff` 出现 `LF will be replaced by CRLF` 警告，系仓库 `core.autocrlf` 行尾规范所致，不影响改动内容；改动仅触及上述 3 处，排盘公式与 `standard_meridian` / `return` 等其余行未动。

---

## 三、self_check 完整原始输出（含新增异常路径测试）

> **编码说明：** 同 Sprint 45/47，运行 self_check 时设置 `PYTHONIOENCODING=utf-8`，以下为程序向 UTF-8 流写入的真实内容（非终端 GBK 显示层复述）。

### 3.1 主验证：干净 venv（`venv_sprint47_test`，按 pyproject.toml 安装、含 tzdata、editable 安装使源码改动即时生效）

```text
=== [Primary] venv_sprint47_test (tzdata present, editable) ===
=== python src/core/infrastructure/bazi/engine.py ===
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
PASS 非法 timezone 显式报错: timezone='Not/A_Real_Zone' -> EngineCalculationError: 时区解析失败: timezone='Not/A_Real_Zone'。无法获取标准时区偏移，真太阳时校准无法继续。常见原因：tzdata 时区数据库未安装（pip install tzdata），或 timezone 字符串非法。原始错误: 'No time zone found with key Not/A_Real_Zone'

OK self_check: 全部通过!
=== self_check EXIT CODE: 0 ===
```

**判读（主验证达成）：** 16 个基线用例 + 新增「测试 7」全部打印 `PASS`，末尾 `OK self_check: 全部通过!`，exit code 0。新增用例明确捕获到 `EngineCalculationError`，异常信息包含「时区解析失败」「tzdata 未安装（pip install tzdata）」「timezone 字符串非法」三类可操作提示，并非原样转发的 Python 底层报错。**17/17 PASS。**

### 3.2 补充验证：全新 venv 卸载 tzdata（复现 Sprint 46 根因场景，证明 fail-fast 抓住依赖缺失）

> 目的：直接坐实「今后依赖缺失会在第一时间明确报错」。全新 venv 按 `pyproject.toml` 安装（含 tzdata，因 Sprint 47 已声明），再 `pip uninstall -y tzdata` 模拟依赖缺口，跑 self_check。

```text
=== pip install -e . (will pull tzdata per Sprint 47) ===
install exit: 0
=== simulate Sprint 46 gap: uninstall tzdata ===
Found existing installation: tzdata 2026.3
Uninstalling tzdata-2026.3:
  Successfully uninstalled tzdata-2026.3
=== pip show tzdata (should be gone) ===
WARNING: Package(s) not found: tzdata
=== run self_check WITHOUT tzdata (expect fail-fast EngineCalculationError) ===
Traceback (most recent call last):
  File "D:\pyhon\Lib\zoneinfo\_common.py", line 12, in load_tzdata
    path = resources.files(package_name).joinpath(resource_name)
           ...
  File "D:\pyhon\Lib\zoneinfo\_common.py", line 29, in load_tzdata
    raise ZoneInfoNotFoundError(f"No time zone found with key {key}")
zoneinfo._common.ZoneInfoNotFoundError: 'No time zone found with key Asia/Shanghai'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "E:\VSCODE\AI-Destiny-Platform\src\core\domain\services\paipan.py", line 37, in _true_solar_correction_minutes
    tz = ZoneInfo(request.timezone)
  ...
  File "E:\VSCODE\AI-Destiny-Platform\src\core\domain\services\paipan.py", line 49, in _true_solar_correction_minutes
    raise EngineCalculationError(
    ...<4 lines>...
    ) from exc
core.domain.exceptions.EngineCalculationError: 时区解析失败: timezone='Asia/Shanghai'。无法获取标准时区偏移，真太阳时校准无法继续。常见原因：tzdata 时区数据库未安装（pip install tzdata），或 timezone 字符串非法。原始错误: 'No time zone found with key Asia/Shanghai'
=== self_check EXIT CODE: 1 ===
```

**判读（补充验证达成，决定性）：** 模拟 Sprint 46 的「缺 tzdata」场景后，self_check 在**第一个**基线用例（立春前年柱，`Asia/Shanghai`）就**立即抛 `EngineCalculationError` 并异常退出（exit code 1）**，而非像 Sprint 45/46 那样静默算错 5 项后打印 `FAIL`。`ZoneInfoNotFoundError` 通过 `from exc` 作为 `__cause__` 保留在异常链中，主错误信息是中文可操作提示（明确点名 `tzdata 未安装`）。

→ 这正面证明：Sprint 46 的根因（依赖缺失）**不再被静默掩盖**——今后任何环境只要 tzdata 缺失，排盘会在第一时间以明确领域异常失败，而不再产出看似合理但错误的真太阳时结果。

---

## 四、`except Exception` 全项目扫描结果（排查，不改动，登记供后续）

扫描命令与命中（read-only）：

```text
$ grep -rn "except Exception" src/core/
src/core/domain/services/paipan.py:45:    except Exception as exc:

$ grep -rn "except" src/
src/core/domain/services/paipan.py:45:    except Exception as exc:
src/zhiming/boot/__init__.py:5:(structlog), exception hierarchy, ...
src/zhiming/__init__.py:19:    boot — Bootstrap: ... exceptions ...
```

**逐命中判定：**

| # | 文件:行 | 是否实际 `except` 代码分支 | 是否存在「吞异常静默返回默认值」隐患 | 处理 |
|---|---------|----------------------------|--------------------------------------|------|
| 1 | `src/core/domain/services/paipan.py:45` | ✅ 是（本次改造对象） | 改造前：是（`std_offset_hours = 0.0`）；改造后：否（改为显式 raise） | **本 Sprint 已消除** |
| 2 | `src/zhiming/boot/__init__.py:5` | ❌ 否（docstring 中 "exception hierarchy" 字样） | 否（非代码） | 不登记 |
| 3 | `src/zhiming/__init__.py:19` | ❌ 否（docstring 中 "exceptions" 字样） | 否（非代码） | 不登记 |

**结论：** 领域 / 服务层 **`except Exception` 仅此一处**（即本次改造对象），**不存在其他「吞异常后静默返回默认值」的同类隐患**，无需登记额外待办项。

> 备注：`src/zhiming/boot/__init__.py` 的 docstring 提到「Define a hierarchical exception tree for all business errors」（E-BOOT 脚手架，迭代 2-5 实现），但当前仅导出 `Settings / configure_logging / get_logger / get_settings`，并无实际异常类。后续若落地该业务异常树，建议将本 Sprint 的 `core/domain/exceptions.EngineCalculationError` 纳入统一体系（属独立决策，不在本 Sprint 范围）。

---

## 五、审核摘要

### 5.1 本 Sprint 目标达成情况

| 验收项 | 结果 |
|--------|------|
| 静默退化改为显式失败 | ✅ `paipan.py` 不再返回 `0.0`，改为抛 `EngineCalculationError` |
| 异常信息可操作（含 tzdata 未安装提示，非原样转发底层报错） | ✅ 主信息为中文提示，底层错误经 `from exc` 保留于异常链 |
| 不改动其他函数 / 排盘公式 | ✅ 仅动 `_true_solar_correction_minutes` 的 `except` 分支 |
| 新增异常路径 self_check 用例并入完整跑 | ✅ 测试 7：`Not/A_Real_Zone` → 捕获 `EngineCalculationError`（PASS） |
| 完整 self_check 通过 | ✅ 主验证 **17/17 PASS**（`OK self_check: 全部通过!`，exit 0） |
| `except Exception` 全项目审计 | ✅ 仅命中 1 处（即改造对象），无其他同类隐患 |

### 5.2 是否发现新问题

**否（本 Sprint 引入的改动均符合预期）。** 补充验证进一步确认：Sprint 46 的根因（缺 tzdata）现在会在第一时间以明确领域异常暴露，彻底杜绝「静默错误结果」。

### 5.3 仍遗留 / 建议（非本 Sprint 引入）

- **`zhiming.boot` 业务异常树尚未落地**：`EngineCalculationError` 目前是领域层独立异常，未纳入 `zhiming.boot` docstring 提及的「hierarchical exception tree」。后续 E-BOOT 实现业务异常体系时，建议统一收口（独立决策）。
- **`validate()` 与 fail-fast 的边界**：`LunarBaziEngine.validate()` 负责入参合法性（返回错误列表），而时区解析失败属运行时计算失败，由 `EngineCalculationError` 承担——职责划分清晰，无需调整。
- **测试用 venv 保留**：`venv_sprint47_test/`、`venv_sprint48_notz/` 仍保留在仓库工作区，未删除（按铁律不擅自清理）；如不需要可后续手动删除或加入 `.gitignore`。

### 5.4 其他说明

- 本 Sprint **未执行 git commit**（按铁律这次不作检查点）。待提交时，应连同 3 个源码改动（`src/core/domain/exceptions.py` 新建、`paipan.py`、`engine.py`）+ 本报告一并展示 diff 后由用户确认。
- `git diff` 出现的 `LF → CRLF` 警告为仓库行尾规范（`core.autocrlf`）行为，与本次改动无关。

---

*报告生成：Claude Code（Sprint 48 自动化执行）*
