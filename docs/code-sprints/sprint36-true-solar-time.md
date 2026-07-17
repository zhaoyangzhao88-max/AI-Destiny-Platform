# Sprint 36 — 真太阳时校准

> **执行日期:** 2026-07-17
> **执行模式:** 直接执行（带调查分支：先判定 lunar_python 是否原生支持，结论为「不支持」，按公式自实现）
> **涉及文件:** `src/core/domain/services/paipan.py`、`src/core/infrastructure/bazi/engine.py`

---

## 1. lunar_python 是否原生支持的判断过程和结论

**判定方法：** 在库安装目录 `D:\pyhon\Lib\site-packages\lunar_python` 下用多组关键词做源码全文搜索。

| 搜索关键词 | 命中 |
|-----------|------|
| `真太阳时` / `true solar` / `均时差` / `equation of time` / `solarTime` | **0 命中** |
| `经度` / `longitude` / `timezone` / `时区` / `时差` / `setTime` / `adjust` / `修正` / `offset` | **0 命中**（仅 `offset` 作为数组下标变量名出现，与真太阳时无关） |

同时检视 `Solar.py` 与 `EightChar.py` 的公有方法：`Solar` 仅提供 `fromYmdHms / fromYmd / fromDate / fromJulianDay / fromBaZi` 等朴素日历构造接口，**无任何接收经度/时区并做太阳时校准的参数**；`EightChar` 也无时间调整入口。

**结论：lunar_python 不原生支持真太阳时校准。** 必须按 Sprint 给定公式自实现经度修正，再用修正后的时间构造 `Solar` 对象。

---

## 2. 任务描述

在 `calculate_bazi()` 中加入真太阳时经度校准：给定出生地经度，将「钟表时间」修正为「出生地真太阳时」后再传入排盘计算。仅做经度差修正（公式 `修正分钟数 = (出生地经度 − 时区标准经线) × 4`），不涉及用神/大运/其他功能。同步将 `engine_info.handles_true_solar_time` 置 `True`。

---

## 3. 改动 diff

> 说明：`src/` 在 git 中整体为 **untracked**（`?? src/`），`git diff` 无 baseline，故下方为相对改动前已读取内容的行级 diff（动手前已 Read 三文件实际内容）。

### 3.1 `src/core/domain/services/paipan.py`

**(a) 新增导入（zoneinfo + timedelta）：**

```diff
-from datetime import datetime
+from datetime import datetime, timedelta
+from zoneinfo import ZoneInfo

 from lunar_python import Solar

 from core.domain.models.bazi_chart import BaZiRequest, BaZiResult, Pillar
 from core.infrastructure.bazi.constants import HIDDEN_STEMS_MAP
+
+def _true_solar_correction_minutes(request: BaZiRequest) -> float:
+    """真太阳时经度修正量（分钟，可正可负）。
+    公式: 修正分钟数 = (出生地经度 - 时区标准经线) × 4
+          时区标准经线 = 标准时区偏移小时数 × 15
+    关键: 标准经线必须用「标准时区偏移」(utcoffset - dst)，不能含夏令时。
+    说明: 本实现不含「均时差 (Equation of Time)」修正，属公式范围内的简化。"""
+    try:
+        tz = ZoneInfo(request.timezone)
+        dt = datetime(request.birth_year, request.birth_month,
+                      request.birth_day, request.birth_hour, request.birth_minute)
+        std_offset_hours = (tz.utcoffset(dt) - tz.dst(dt)).total_seconds() / 3600.0
+    except Exception:
+        std_offset_hours = 0.0  # 时区解析失败退化，合法 timezone 不应触发
+    standard_meridian = std_offset_hours * 15.0
+    return (request.longitude - standard_meridian) * 4.0
```

**(b) `calculate_bazi()` 用修正后时间构造 Solar：**

```diff
-    # 创建 Solar 对象（含时分秒）
-    solar = Solar.fromYmdHms(
-        request.birth_year, request.birth_month, request.birth_day,
-        request.birth_hour, request.birth_minute, 0,
-    )
-    lunar = solar.getLunar()
+    # 真太阳时校准：钟表时间 → 出生地真太阳时
+    delta_minutes = _true_solar_correction_minutes(request)
+    base = datetime(request.birth_year, request.birth_month, request.birth_day,
+                    request.birth_hour, request.birth_minute)
+    corrected = base + timedelta(minutes=delta_minutes)
+
+    # 用校准后的真太阳时构造 Solar（含时分秒；跨日自动滚入 corrected.date）
+    solar = Solar.fromYmdHms(
+        corrected.year, corrected.month, corrected.day,
+        corrected.hour, corrected.minute, corrected.second,
+    )
+    lunar = solar.getLunar()
```

### 3.2 `src/core/infrastructure/bazi/engine.py`

**(a) `engine_info` 能力声明置 True：**

```diff
-            "handles_true_solar_time": False,  # 真太阳时校准本 Sprint 未实现
+            "handles_true_solar_time": True,   # 真太阳时经度校准已实现（Sprint 36）
```

**(b) `self_check` 的 `_req` 辅助函数扩展经度/时区参数（默认北京，既有用例零改动）：**

```diff
-        def _req(y, mo, d, h, mi, gender="male"):
+        def _req(y, mo, d, h, mi, gender="male",
+                 longitude=116.4, latitude=39.9, timezone="Asia/Shanghai"):
             return BaZiRequest(
                 ...
-                longitude=116.4, latitude=39.9, timezone="Asia/Shanghai",
+                longitude=longitude, latitude=latitude, timezone=timezone,
             )
```

**(c) 新增测试 5 / 测试 6（真太阳时案例），位于「测试 4」之后、「汇总」之前：**

```python
        # ── 测试 5: 真太阳时-子时跨日边界（乌鲁木齐） ──
        r_uq4 = engine.paipan(_req(1990, 8, 15, 2, 0, longitude=87.6,
                                  latitude=43.8, timezone="Asia/Shanghai"))
        uq4_d = f"{r_uq4.day_pillar.heavenly_stem}{r_uq4.day_pillar.earthly_branch}"
        uq4_t = f"{r_uq4.hour_pillar.heavenly_stem}{r_uq4.hour_pillar.earthly_branch}"
        if uq4_d != "辛亥":
            failures.append(f"FAIL 乌鲁木齐02:00 真太阳时日柱错误: 预期 辛亥, 实际 {uq4_d}")
        else:
            print(f"PASS 乌鲁木齐02:00 真太阳时日柱(跨日回退): {uq4_d}")
        if uq4_t != "庚子":
            failures.append(f"FAIL 乌鲁木齐02:00 真太阳时时柱错误: 预期 庚子(晚子时), 实际 {uq4_t}")
        else:
            print(f"PASS 乌鲁木齐02:00 真太阳时时柱(子时): {uq4_t}")

        # ── 测试 6: 真太阳时-同日时柱翻转（乌鲁木齐） ──
        r_uq5 = engine.paipan(_req(1990, 8, 15, 13, 0, longitude=87.6,
                                  latitude=43.8, timezone="Asia/Shanghai"))
        uq5_d = f"{r_uq5.day_pillar.heavenly_stem}{r_uq5.day_pillar.earthly_branch}"
        uq5_t = f"{r_uq5.hour_pillar.heavenly_stem}{r_uq5.hour_pillar.earthly_branch}"
        if uq5_d != "壬子":
            failures.append(f"FAIL 乌鲁木齐13:00 真太阳时日柱错误: 预期 壬子, 实际 {uq5_d}")
        else:
            print(f"PASS 乌鲁木齐13:00 真太阳时日柱(同日): {uq5_d}")
        if uq5_t != "乙巳":
            failures.append(f"FAIL 乌鲁木齐13:00 真太阳时时柱错误: 预期 乙巳(巳时), 实际 {uq5_t}")
        else:
            print(f"PASS 乌鲁木齐13:00 真太阳时时柱(巳时翻转): {uq5_t}")
```

---

## 4. 真太阳时黄金案例的交叉验证过程（≥2 种独立方法）

> 铁律要求：标准答案不能只信自己代码算出的结果。下面用 **4 条互相独立** 的验证路径收敛到同一答案。

**案例设定：** 乌鲁木齐 经度 87.6°E，时区 `Asia/Shanghai`（东八区，标准经线 120°E），
钟表出生时间 `1990-08-15 02:00`（故意选子时边界，触发跨日）。

### 方法 1 — 手工按修正公式算（独立算术）
```
修正分钟数 = (87.6 − 120) × 4 = (−32.4) × 4 = −129.6 分钟 ≈ −2小时9分36秒
钟表 02:00 − 129.6 分 = 1990-08-14 23:50:24  → 前一日 23:50（子时）
```
→ 理论修正后真太阳时落在 **1990-08-14 23:50**。

### 方法 2 — 外部权威（真太阳时/经度时差资料）
网络检索「乌鲁木齐 真太阳时 与北京时间 时差」得到多个命理/历法站点一致结论：
- 乌鲁木齐经度 87.6°E，与北京时间（120°E 标准时）的固定经度时差 **4×(87.6−120) = −129.6 分钟 ≈ −2小时9分36秒**（即地方时比北京晚约 2 小时 10 分）。
- 资料同时明确指出：这 −2h10m 是「**平太阳时**」的经度部分；完整「真太阳时」还需额外叠加随季节变化的「**均时差**」。
- 来源：[北京时间与全国各地真太阳时](https://www.ydygfs.com/wap.php?action=article&id=20073)、[真太阳时查询-换算](https://m.k366.com/gj/zhentaiyangshi.htm)

→ **与方法 1 完全吻合**，并坐实了本 Sprint「只做经度修正、不含均时差」是有据可依的已知简化。

### 方法 3 — 外部权威（万年历干支锚定库计算）
网络检索「1990年8月15日 干支」得到多家万年历一致结论：
- `1990-08-15 = 庚午年 甲申月 壬子日`。
- 来源：xingzuo5.net / 8s8s.net / huangli8.com 等。

→ 锚定 lunar_python 的日柱计算正确（= Sprint35 黄金数据 壬子），并据干支日序推出 **前一日 1990-08-14 = 辛亥**（壬子前一格）。这给出了 Case 5 日柱 辛亥 的**独立标准答案**（不依赖我的代码）。

### 方法 4 — 独立库复算（绕开我的修正函数，直接对「修正后日期时间」调 lunar_python）
在验证脚本中**不调用** `calculate_bazi`，而是手工构造 `Solar.fromYmdHms(1990,8,14,23,50,0)` 直接排盘：
```
1990-08-14 23:50(修正后) → 庚午/甲申/辛亥/庚子  日主=辛
1990-08-15 10:50(修正后) → 庚午/甲申/壬子/乙巳  日主=壬
1990-08-15 13:00(未修正)  → 庚午/甲申/壬子/丁未  日主=壬
```
→ 与上面三条路径汇合：Case5 日柱=辛亥、时柱=庚子；Case6 日柱=壬子、时柱=乙巳。

**收敛结论（4 条独立路径一致）：**

| 用例 | 修正后真太阳时 | 年柱 | 月柱 | 日柱 | 时柱 | 日主 |
|------|---------------|------|------|------|------|------|
| 乌鲁木齐 1990-08-15 02:00 | 08-14 23:50（跨日） | 庚午 | 甲申 | **辛亥** | **庚子** | 辛 |
| 乌鲁木齐 1990-08-15 13:00 | 08-15 10:50（同日） | 庚午 | 甲申 | **壬子** | **乙巳** | 壬 |

> 注：时柱 `庚子` 的「庚」来自 lunar_python 的**晚子时**约定——23:00–23:59 的时柱天干取**次日**日干（08-15 日主壬 → 丁壬日庚子时）。日柱仍按午夜换日取当日（08-14 辛亥）。此行为由 lunar_python 内建，已在方法 4 独立复算中验证。

---

## 5. self_check 完整原始输出（含新增用例）

命令：`PYTHONIOENCODING=utf-8 python src/core/infrastructure/bazi/engine.py`

```
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
```

> 共 16 项检查：原 9 + Sprint35 gender 3 + 本 Sprint 真太阳时 4，**全部通过**。
> 其中北京 12:00 用例（原 Case 3）现在也经过真太阳时校准（北京 116.4E 修正约 −14.4 分 → 11:45，仍属午时 丙午），证明小修正量下既有的「午时」结论不变、零回归。

---

## 6. 文件系统证据

`find src/core -type f` 原始输出（仅 `.py` 源文件，不含 `__pycache__`）：

```
src/core/domain/interfaces/bazi_engine.py
src/core/domain/interfaces/__init__.py
src/core/domain/models/bazi_chart.py
src/core/domain/models/__init__.py
src/core/domain/services/paipan.py
src/core/domain/services/__init__.py
src/core/domain/__init__.py
src/core/infrastructure/bazi/constants.py
src/core/infrastructure/bazi/engine.py
src/core/infrastructure/bazi/utils.py
src/core/infrastructure/bazi/__init__.py
src/core/infrastructure/__init__.py
src/core/__init__.py
```

本次改动仅触及 `src/core/domain/services/paipan.py` 与 `src/core/infrastructure/bazi/engine.py` 两个源文件，未增删任何文件。

---

## 7. 审核摘要

### 7.1 子时跨日边界如何处理（如实报告）
发现并确认：真太阳时修正若跨越午夜，会同时影响**日柱**与**时柱**，处理方式如下：

1. **日柱联动**：修正后时间用 `datetime + timedelta` 构造，`corrected.date` 已自动滚到前一日（08-15 → 08-14）。我把**完整修正后日期时间**喂给 `Solar.fromYmdHms`，lunar_python 的 `getDayInGanZhi()` 按「午夜换日」取当日干支 → 日柱自然回退为 辛亥，**无需手动调整日柱**。
2. **时柱晚子时约定**：当修正后落在 23:00–23:59，lunar_python 的 `getTimeInGanZhi()` 按**晚子时** convention，时柱天干取**次日**日干（08-15 日主壬 → 庚子）。这是库内建行为，非我额外处理，已在方法 4 独立复算中验证为 辛亥/庚子。
3. **边界稳健性**：`timedelta` 处理跨月/跨年（如 1 月 1 日 00:30 修正后落到前一年 12 月 31 日）同样正确，因为整条链路只依赖 `corrected` 的年月日时分秒，不假设不跨日。

> 透明声明：本实现采用 lunar_python 默认的「午夜换日 + 晚子时」约定（即 sect=2）。若产品未来要求「早子时」（23:00 起算当日）口径，需单独处理，不在本 Sprint 范围。

### 7.2 是否发现新问题

1. **🔴 夏令时陷阱（关键正确性 bug，已规避）：** `ZoneInfo("Asia/Shanghai").utcoffset(1990-08-15)` 返回 **9 小时**而非 8 小时——因为 1990 年中国仍在实行夏令时（1986–1991），8 月属夏令时 UTC+9。若直接用 `utcoffset` 当标准经线，会得到 135°E，乌鲁木齐修正量错算成 −189.6 分钟（比正确值多偏 1 小时）。**真太阳时校准必须用「标准时区偏移」**，故实现采用 `标准偏移 = utcoffset − dst`，验证得 8h → 120°E，正确。此坑对所有曾实行夏令时的时区/年份都适用，已固化进 `_true_solar_correction_minutes`。
2. **🟡 均时差（Equation of Time）未包含：** 本 Sprint 按计划公式只做经度差修正（×4 分/度），不含随季节变化的「均时差」（±16 分钟内）。外部资料（方法 2）明确印证：−2h10m 是「平太阳时」经度部分，完整真太阳时还需叠日均时差。因此本实现严格说是「**经度修正后的平太阳时**」，名称 `handles_true_solar_time` 与 Sprint 给定的「真太阳时校准」口径一致，但技术上是该概念的经度子集。**建议后续 Sprint 引入均时差表做完整真太阳时**，届时 `engine_info` 可再细分（如 `handles_equation_of_time`）。
3. **🟡 `birth_time_unknown` 与修正的交互：** 当出生时间未知时（hour 多为占位值），修正仍会被套用，但时柱本就不可信，影响可忽略。不在本 Sprint 范围，仅记录。
4. **⚪ `src/` 仍整体 untracked：** `git diff` 无 baseline，本报告以行级 diff 记录；建议后续将 `src/` 纳入版本管理（需用户确认）。
5. **⚪ 不涉及任何已确认 ADR：** 纯领域计算增强，未触碰 ADR-001~016 红线。

---

## 附：未 git commit（按铁律）
本次仅修改/验证代码并产出本报告，未执行任何 `git commit`。
