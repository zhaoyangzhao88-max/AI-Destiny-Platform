# Sprint 46 — self_check 5 项失败根因调查（紧急，纯只读）

- **日期：** 2026-07-20
- **范围：** 纯诊断，验证「`tzdata` 缺失导致时区解析失败」假设。无任何写操作（未改代码、未改 `pyproject.toml`、未改 `requirements.txt`、未 commit）。
- **前置依赖：** 复用 Sprint 45 创建的全新 venv `venv_sprint45_test`（仅按 `pyproject.toml` 安装，本不含 `tzdata`）。

---

## 结论（先说答案）

**tzdata 假设成立 ✅。**

self_check 的 5 项失败**不是引擎算法错误，也不是 Sprint 45 引入**，而是
`pyproject.toml` **缺少 `tzdata` 运行时依赖**所致：

- 在按 `pyproject.toml` 全新安装的 venv 中，`tzdata` 不存在 → `zoneinfo.ZoneInfo('Asia/Shanghai')` 抛 `ZoneInfoNotFoundError`。
- 代码 `src/core/domain/services/paipan.py:36` 的 `_true_solar_correction_minutes` 在 `ZoneInfo` 解析失败时**静默退化**为 `std_offset_hours = 0.0`（第 45-47 行），导致标准经线算成 0°E，真太阳时修正量整体错位 → 5 项涉时区/真太阳时的用例失败。
- 在 venv 内诊断性装上 `tzdata` 后，self_check **16/16 全部通过**。
- 旧环境（系统 Python `D:\pyhon`）因 `tzdata` 2025.2 已被 pandas/exchange_calendars/tzlocal 带入而**恰好存在**，所以历史上 self_check 通过（即 git `5ecf923`「零回归」成立的真实条件）。

> ⚠️ 注意：根因是「**依赖声明缺口**」（`pyproject.toml` 未声明 `tzdata`），而非「算法 bug」。但代码用 `try/except` 静默吞掉时区解析失败、退化为 0 修正，掩盖了该缺口——这是值得在后续 Sprint 一并处理的健壮性隐患（本 Sprint 不修，仅锁定根因）。

---

## 一、[Step 1] 新环境（venv_sprint45_test）检测 tzdata 与 zoneinfo

```text
=== [Step 1] pip show tzdata ===
WARNING: Package(s) not found: tzdata
=== [Step 1] exit: 1 ===

=== [Step 1] zoneinfo Asia/Shanghai ===
Traceback (most recent call last):
  File "D:\pyhon\Lib\zoneinfo\_common.py", line 12, in load_tzdata
    path = resources.files(package_name).joinpath(resource_name)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "D:\pyhon\Lib\importlib\resources\_common.py", line 46, in wrapper
    return func(anchor)
  File "D:\pyhon\Lib\importlib\resources\_common.py", line 56, in files
    return from_package(resolve(anchor))
                        ~~~~~~~^^^^^^^^
  File "D:\pyhon\Lib\functools.py", line 934, in wrapper
    return dispatch(args[0].__class__)(*args, **kw)
                   ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "D:\pyhon\Lib\importlib\resources\_common.py", line 82, in _
    return importlib.import_module(cand)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "D:\pyhon\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name=level:, package=level)
                                   ~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1310, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1310, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'tzdata'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import zoneinfo; print(zoneinfo.ZoneInfo('Asia/Shanghai'))
                           ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "D:\pyhon\Lib\zoneinfo\_common.py", line 29, in load_tzdata
    raise ZoneInfoNotFoundError(f"No time zone found with key {key}")
zoneinfo._common.ZoneInfoNotFoundError: 'No time zone found with key Asia/Shanghai'

=== [Step 1] utcoffset ===
Traceback (most recent call last):
  File "D:\pyhon\Lib\zoneinfo\_common.py", line 12, in load_tzdata
    path = resources.files(package_name).joinpath(resource_name)
           ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^
  File "D:\pyhon\Lib\importlib\resources\_common.py", line 46, in wrapper
    return func(anchor)
  File "D:\pyhon\Lib\importlib\resources\_common.py", line 56, in files
    return from_package(resolve(anchor))
                        ~~~~~~~^^^^^^^^
  File "D:\pyhon\Lib\functools.py", line 934, in wrapper
    return dispatch(args[0].__class__)(*args, **kw)
                   ~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^
  File "D:\pyhon\Lib\importlib\resources\_common.py", line 82, in _
    return importlib.import_module(cand)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "D:\pyhon\Lib\importlib\__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name=level:, package=level)
                                   ~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1310, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1310, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1324, in _find_and_load_unlocked
ModuleNotFoundError: No module named 'tzdata'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import zoneinfo; z = zoneinfo.ZoneInfo('Asia/Shanghai'); import datetime; print(z.utcoffset(datetime.datetime(2024,3,5,9,0)))
                         ~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "D:\pyhon\Lib\zoneinfo\_common.py", line 29, in load_tzdata
    raise ZoneInfoNotFoundError(f"No time zone found with key {key}")
zoneinfo._common.ZoneInfoNotFoundError: 'No time zone found with key Asia/Shanghai'
=== [Step 1] inner exit: 1 ===
```

**判读：** `tzdata` 未安装；`ZoneInfo('Asia/Shanghai')` 与 `utcoffset(...)` 均抛 `ZoneInfoNotFoundError`。Windows + 纯 venv（无系统 tz 数据库）下必须靠 `tzdata` 包提供时区数据，此环节缺失。

---

## 二、[Step 2] 旧环境（非 venv，系统 Python）检测对比

```text
=== [Step 2] which python (old env) ===
/d/pyhon/python

=== [Step 2] python version ===
Python 3.13.7

=== [Step 2] pip show tzdata (OLD env) ===
Name: tzdata
Version: 2025.2
Summary: Provider of IANA time zone data
Home-page: https://github.com/python/tzdata
Author: Python Software Foundation
Author-email: datetime-sig@python.org
License: Apache-2.0
Location: D:\pyhon\Lib\site-packages
Requires:
Required-by: exchange_calendars, pandas, tzlocal
=== [Step 2] exit: 0 ===

=== [Step 2] zoneinfo Asia/Shanghai (OLD env) ===
Asia/Shanghai
=== [Step 2] inner exit: 0 ===
```

**判读（两边对比）：**

| 项 | 旧环境（系统 Python `D:\pyhon` 3.13.7） | 新 venv（仅 pyproject.toml 安装） |
|----|------------------------------------------|-----------------------------------|
| `tzdata` | ✅ 已安装 **2025.2**（`Required-by: exchange_calendars, pandas, tzlocal`） | ❌ 未安装 |
| `ZoneInfo('Asia/Shanghai')` | ✅ 返回 `Asia/Shanghai` | ❌ 抛 `ZoneInfoNotFoundError` |

**关键：** 旧环境的 `tzdata` 是**被 pandas / exchange_calendars / tzlocal 等第三方库间接带入**的，并非项目自身声明。一旦换到「仅按本项目 `pyproject.toml` 安装」的干净环境，`tzdata` 就消失——这正是 Sprint 45 全新 venv 暴露失败的根。

---

## 三、[Step 3] 代码是否真的用 zoneinfo / 依赖系统时区数据库

`grep -rn "zoneinfo\|pytz\|ZoneInfo" src/core/` 结果：

```text
src\core\domain\services\paipan.py:13:from zoneinfo import ZoneInfo
src\core\domain\services\paipan.py:36:        tz = ZoneInfo(request.timezone)
```

**相关代码路径（`src/core/domain/services/paipan.py`）：**

```python
# 第 13 行
from zoneinfo import ZoneInfo

# 第 21-49 行：真太阳时经度修正量
def _true_solar_correction_minutes(request: BaZiRequest) -> float:
    try:
        tz = ZoneInfo(request.timezone)
        dt = datetime(
            request.birth_year, request.birth_month, request.birth_day,
            request.birth_hour, request.birth_minute,
        )
        # 标准偏移 = 含 DST 的偏移 - DST 增量（剔除夏令时）
        std_offset_hours = (
            tz.utcoffset(dt) - tz.dst(dt)
        ).total_seconds() / 3600.0
    except Exception:
        # 时区解析失败：退化为 0 修正，避免崩溃（合法 timezone 不应触发）
        std_offset_hours = 0.0
    standard_meridian = std_offset_hours * 15.0
    return (request.longitude - standard_meridian) * 4.0
```

**判读：** 代码**确实依赖 `zoneinfo` / 系统时区数据库**（第 13、36 行）。失败时（第 45-47 行）**静默退化**为 `std_offset_hours = 0.0` → `standard_meridian = 0.0` → 真太阳时修正量 = `longitude × 4` 分钟（对中国境内任意经度都会被放大成数小时的错误修正），从而把时间整体挪偏，导致真太阳时相关的日柱/时柱错位，以及涉节气边界的月柱错位。

这正是 Step 1/2/4 观察到的失败模式对应的代码路径——**假设指向的代码路径成立**。

---

## 四、[Step 4] 最小复现：装 tzdata 后重跑 self_check

> 仅在 `venv_sprint45_test` 内诊断性 `pip install tzdata`（**不改** `pyproject.toml` / `requirements.txt`，仅 venv 本地安装）。

```text
=== [Step 4] pip install tzdata (diagnostic only) ===
Collecting tzdata
  Downloading tzdata-2026.3-py2.py3-none-any.whl.metadata (1.4 kB)
Downloading tzdata-2026.3-py2.py3-none-any.whl (348 kB)
Installing collected packages: tzdata
Successfully installed tzdata-2026.3

[notice] A new release of pip available: 25.2 -> 26.1.2
[notice] To update, run: python.exe -m pip install --upgrade pip
=== [Step 4] install exit: 0 ===

=== [Step 4] rerun self_check ===
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
=== [Step 4] self_check exit: 0 ===
```

**判读（决定性证据）：** 装 `tzdata` 前 11 PASS / 5 FAIL；装 `tzdata` 后 **16/16 全部通过**。差异变量唯一（`tzdata` 的有无），故假设成立——`tzdata` 缺失是 5 项失败的直接根因。

---

## 五、根因锁定摘要

| 层级 | 事实 |
|------|------|
| 直接原因 | 干净 venv（仅按 `pyproject.toml` 安装）无 `tzdata` → `ZoneInfo('Asia/Shanghai')` 抛 `ZoneInfoNotFoundError` |
| 代码路径 | `src/core/domain/services/paipan.py:36` 解析时区失败，`except` 静默退化为 `std_offset_hours = 0.0`（第 45-47 行），真太阳时修正量错位 |
| 声明缺口 | `pyproject.toml` 的 `dependencies` **未声明 `tzdata`**（Windows / 无系统时区数据的 venv 必须显式安装） |
| 为何历史「零回归」 | 旧环境系统 Python 的 `tzdata` 2025.2 被 pandas/exchange_calendars/tzlocal 间接带入，恰好存在 → self_check 通过 |
| 是否算法 bug | ❌ 不是。引擎排盘逻辑正确；失败纯粹由依赖缺失 + 静默退化掩盖造成 |
| 是否 Sprint 45 引入 | ❌ 不是。Sprint 45 仅补 `lunar_python` 声明，与 `tzdata` 无关；它只是首个「干净只按 pyproject 安装」的环境，从而暴露了既有缺口 |

### 5 项失败与根因的对应（解释）
- `惊蛰前月柱 2024-03-05 09:00`：节气换月边界，标准经线算错使时钟偏移越过惊蛰时刻。
- `1990-08-15 12:00 时柱`：真太阳时修正量错，时辰（2 小时一支）错位。
- `乌鲁木齐 02:00 / 13:00 真太阳时 日柱 / 时柱`：经度 87.6°E 处 `longitude×4` 错误修正量极大，直接跨日/跨时辰。

### 下一步修复方向（本 Sprint 不执行，仅记录供后续）
1. **治标（依赖声明）：** 在 `pyproject.toml` 的 `dependencies` 增加 `"tzdata>=2024.1"`（与既用 `>=` 风格一致），保证 Windows / 干净 venv 可获得时区数据。可合并进类似 Sprint 45 的依赖对齐流程。
2. **治本（健壮性）：** `paipan.py` 的 `except Exception: std_offset_hours = 0.0` 静默退化会掩盖缺失依赖。建议改为：依赖缺失时**显式报错 / 在导入期或初始化期 fail-fast**，而非用 0 修正产出看似合理但错误的结果。是否修改属代码决策，需独立 Sprint 评估（注意 Sprint 43 等涉及 self_check 异常行为调查，改动前应先核对相关约束）。

---

*报告生成：Claude Code（Sprint 46 纯只读根因调查）*
