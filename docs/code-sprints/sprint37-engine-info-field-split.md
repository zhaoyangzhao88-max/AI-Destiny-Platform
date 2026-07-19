# Sprint 37 — engine_info 字段语义精确化（真太阳时拆分）

> **执行日期:** 2026-07-17
> **执行模式:** 直接执行（单一字段拆分，无判断空间）
> **涉及文件:** `src/core/domain/interfaces/bazi_engine.py`、`src/core/infrastructure/bazi/engine.py`

---

## 1. 任务描述

把 `engine_info` 中语义不准确的 `handles_true_solar_time` 字段，拆分成两个语义精确的字段：
- `handles_mean_solar_time` — 经度修正 / 平太阳时（Sprint 36 已实现）→ `True`
- `handles_equation_of_time` — 均时差（尚未实现）→ `False`

**不涉及任何计算逻辑改动**（Sprint 36 的经度修正实现本身不变，只改能力声明字段）。同步更新 ABC `BaziEngine.engine_info` 文档字符串中的字段清单。

---

## 2. 改动 diff

> 说明：`src/` 现已纳入版本管理（`e00036a` 提交已包含本 Sprint 改动），下方为相对改动前已读取内容的行级 diff（仅能力声明字段拆分，计算逻辑未动）。

### 2.1 `src/core/domain/interfaces/bazi_engine.py` — ABC `engine_info` 文档字符串字段清单

```diff
         """返回引擎能力声明，至少包含：
-        handles_jieqi / handles_lichun / handles_true_solar_time / supports_yongshen
+        handles_jieqi / handles_lichun / handles_mean_solar_time / handles_equation_of_time / supports_yongshen
         """
```

### 2.2 `src/core/infrastructure/bazi/engine.py` — `LunarBaziEngine.engine_info` 实现

**(a) 文档注释计数 4→5：**

```diff
-        """引擎能力声明（08 §8.8.1 要求至少包含 4 个 handles/supports 键）。"""
+        """引擎能力声明（08 §8.8.1 要求至少包含 5 个 handles/supports 键）。"""
```

**(b) 字段拆分（移除 `handles_true_solar_time`，新增两个字段）：**

```diff
-            "handles_true_solar_time": True,   # 真太阳时经度校准已实现（Sprint 36）
+            "handles_mean_solar_time": True,   # 经度修正/平太阳时已实现（Sprint 36）
+            "handles_equation_of_time": False,  # 均时差尚未实现
```

> 备注：Sprint 36 那次替换曾**漏掉该行 12 个前导空格**，导致 `engine.py` 第 63 行实际以 0 缩进存储（dict 在括号内仍可解析，故 self_check 未报错，但格式不一致）。本 Sprint 在补两行新字段时一并**恢复了 12 空格标准缩进**，消除该历史格式瑕疵。

---

## 3. self_check 完整原始输出（确认 16 项零回归）

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

> **16 项全部通过，零回归。** 本次仅为能力声明字段调整，不影响 `calculate_bazi()` 任何排盘计算逻辑，故既有 9 项 + Sprint35 gender 3 项 + Sprint36 真太阳时 4 项均照常通过。

---

## 4. 文件系统证据

`find src/core -type f` 原始输出（仅 `.py` 源文件）：

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

本次改动仅触及 `src/core/domain/interfaces/bazi_engine.py` 与 `src/core/infrastructure/bazi/engine.py` 两个源文件，未增删任何文件。

---

## 5. 审核摘要

### 5.1 grep 检查结果（是否有遗漏引用）
在 `src/` 目录全量 `grep -rn "handles_true_solar_time" src/`：

- **改动前命中 2 处**：`bazi_engine.py:32`（ABC docstring，已随字段清单更新）、`engine.py:63`（实现，已拆分）。
- **改动后复检**：`handles_true_solar_time` 在 `src/` 内 **0 命中**（仅剩 `handles_mean_solar_time` / `handles_equation_of_time` 两条新字段 + ABC docstring 更新）。

结论：**代码层无遗漏引用**。Sprint 33 等历史报告提及 `handles_true_solar_time` 位于 `docs/` 下（非 `src/` 代码），按本 Sprint 范围「只改代码能力声明字段」不触碰文档，且文档中的旧字段名属历史记录性质，不影响运行；如需文档同步可在后续文档清理 Sprint 处理（不在本 Sprint 范围）。

### 5.2 是否发现新问题
1. **🟢 顺带修复一处历史格式瑕疵：** Sprint 36 替换时漏掉 `engine.py:63` 的 12 个前导空格，本 Sprint 补两行新字段时一并恢复了标准缩进，dict 格式恢复一致（不影响运行，仅可读性）。
2. **⚪ 语义澄清价值：** 拆分后 `handles_mean_solar_time=True` 精确表达「仅做了经度差修正的平太阳时」，与 Sprint 36 交叉验证中外部资料确认的事实（−2h10m 是平太阳时经度部分，完整真太阳时需叠日均时差）一致；`handles_equation_of_time=False` 为后续补均时差表预留明确接口位。能力声明现在与实现真实状态一一对应。
3. **🟢 `src/` 已纳入版本管理：** 提交 `e00036a` 已包含本 Sprint 改动，`git status` 当前干净，本报告的行级 diff 为相对改动前内容的记录。
4. **⚪ 不涉及任何已确认 ADR：** 纯能力声明字段重命名，未触碰 ADR-001~016 红线。

---

## 附：未 git commit（按铁律）
本次仅修改代码、跑 self_check 并产出本报告，未执行任何 `git commit`。
