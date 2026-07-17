# Sprint 35 — gender 字段支持 unknown + 大运方向未定信号位

> **执行日期:** 2026-07-17
> **执行模式:** 直接执行（改动范围明确）
> **涉及文件:** `src/core/domain/models/bazi_chart.py`、`src/core/infrastructure/bazi/engine.py`、`src/core/domain/services/paipan.py`

---

## 1. 任务描述

在现有排盘引擎基础上做两个小颗粒改动，不涉及设计空间：

1. `BaZiRequest.gender` 取值从 `"male" | "female"` 放宽为 `"male" | "female" | "unknown"`，
   同步放宽 `LunarBaziEngine.validate()` 的 gender 校验。
2. 当 `gender == "unknown"` 时，在结果上标注一个信号位
   `great_fortune_direction_undetermined`（大运顺逆方向未定，因性别未知），
   为大运计算 Sprint 预留接口；**本 Sprint 不实现大运计算本身**。

---

## 2. 改动 diff

> 注：`src/` 目录在 git 中整体为 **untracked**（`?? src/`），`git diff` 对未跟踪文件无 baseline，
> 故下方为相对改动前已读取内容的行级 diff（已在动手前 Read 三文件实际内容）。

### 2.1 `src/core/domain/models/bazi_chart.py`

**(a) `BaZiResult` 新增信号位字段** — 插在 `great_fortune_cycle` 之后、`yong_shen` 之前，
与既有 `great_fortune_*` 簇同组：

```diff
     birth_time_unknown: bool = False
     great_fortune_start_age: int = 0
     great_fortune_cycle: list[dict] = field(default_factory=list)
+    # 大运顺逆方向是否待定：性别未知时无法判定大运顺排/逆排，预留给大运计算 Sprint
+    great_fortune_direction_undetermined: bool = False
     yong_shen: Optional[str] = None      # 用神
```

**(b) `BaZiRequest.gender` 类型注释放宽：**

```diff
-    gender: str                  # "male" | "female"
+    gender: str                  # "male" | "female" | "unknown"
```

### 2.2 `src/core/infrastructure/bazi/engine.py` — `validate()` 同步放宽

```diff
-        if request.gender not in ("male", "female"):
+        if request.gender not in ("male", "female", "unknown"):
             errors.append(
-                f"gender 非法: {request.gender} (应为 male|female)"
+                f"gender 非法: {request.gender} (应为 male|female|unknown)"
             )
```

### 2.3 `src/core/domain/services/paipan.py` — `calculate_bazi()` 传递信号位

```diff
         gender=request.gender,           # 调用者可覆盖 male/female
         birth_time_unknown=request.birth_time_unknown,
+        # 性别未知时大运顺逆方向无法判定；本 Sprint 不实现大运计算本身
+        great_fortune_direction_undetermined=(request.gender == "unknown"),
```

### 2.4 `self_check()` 新增测试 4（gender=unknown 信号位验证）

- `_req` 辅助函数增加可选参数 `gender="male"`（默认不变，既有用例零改动）。
- 新增「测试 4」：同生日 `1990-08-15 12:00` 用 `male` 与 `unknown` 各跑一次，
  断言四柱/日主一致（证明 gender 不参与排盘），且 `unknown` 时信号位为 `True`、`male` 时为 `False`。

---

## 3. self_check 完整原始输出（含新增用例）

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

OK self_check: 全部通过!
```

> 共 12 项检查：原 9 项（立春前后 / 惊蛰前后 / 1990 四柱 + 日主）全部保持通过，
> 新增 3 项（unknown 四柱一致 / unknown 信号位 True / male 信号位 False）全部通过。

---

## 4. 文件系统证据

`find src/core -type f` 原始输出：

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
```

（注：列表中 `src/core/domain/models/__init__.py`、`services/__init__.py` 等亦含 `__pycache__` 同辈目录，
此处按 `find -type f` 的非字节码结果呈现；本次改动仅触及上述 3 个 `.py` 源文件，未增删任何文件。）

---

## 5. 审核摘要

### 5.1 新增字段放 BaZiResult 还是 engine_info？

**结论：放在 `BaZiResult`。**

理由（基于第一性原理 + 系统思维）：

- `engine_info` 是 `LunarBaziEngine.engine_info` **静态属性**，语义是「引擎能力声明」
  （handles_jieqi / supports_yongshen 等，对所有请求恒定不变）。
  而本信号位是**每次请求随入参 gender 变化的 per-request 状态**（male→False、unknown→True），
  放进静态能力字典在语义上错位，且每次排盘都需重写 engine_info，违背其「不变声明」的设计意图。
- 既有 `BaZiResult` 已存在同类 per-request 信号 `birth_time_unknown: bool`，
  以及 `great_fortune_*` 簇（`great_fortune_start_age`、`great_fortune_cycle`）。
  新字段与两者都契合：既属「每请求一次的信号位」，又是「大运相关字段」，
  置于 `great_fortune_cycle` 之后、`yong_shen` 之前形成连续的大运字段簇，可读性最佳。
- 大运计算 Sprint 拿到 `BaZiResult` 后可直接读 `great_fortune_direction_undetermined`
  决定走顺排/逆排分支或提示用户补全性别，无需回头查 engine_info。

### 5.2 命名建议

- 采用 `great_fortune_direction_undetermined`（大运方向待定）。语义清晰：
  表达「因性别未知导致大运顺逆方向尚未确定」，且前缀 `great_fortune_` 与既有大运字段成簇。
- 备选（均不如当前命名贴切，供评审参考）：
  - `da_yun_direction_unknown` — 拼音前缀与全仓 `great_fortune_*` 命名不一致，不推荐。
  - `gender_unknown_blocks_da_yun` — 把「原因」和「结果」揉进字段名，过长且耦合原因。
  - `fortune_dir_pending` — 语义稍模糊（pending 既可指待定也可指待处理）。
- **结论**：当前 `great_fortune_direction_undetermined` 命名即为推荐命名，无需调整。

### 5.3 是否发现新问题

1. **`src/` 整体未纳入 git 跟踪**（`?? src/`）：`git diff` 对三文件无 baseline，
   故本报告改用相对改动前行级 diff 记录。建议后续将 `src/` 纳入版本管理（需用户确认是否 `git add`）。
2. **`gender` 在 `BaZiResult` 中仍原样透传**（值可能是 `"unknown"`）。
   下游若直接按 male/female 分支处理 `result.gender`，遇到 `"unknown"` 需自行判空——
   本 Sprint 已在 `great_fortune_direction_undetermined` 显式给出信号，下游应以此为准而非再判字面值。
3. **未触碰任何已确认 ADR**：本次纯属领域模型字段放宽 + 信号位预留，
   不涉产品决策红线（ADR-001~016），无需走 ADR 质疑流程。
4. **self_check 通过且零回归**：新增用例证明 gender 不参与四柱计算（male 与 unknown 四柱逐柱一致），
   与既有设计「gender 不影响排盘」自洽，为大运 Sprint 打下干净基础。

---

## 附：未 git commit（按铁律）

本次仅修改/验证代码并产出本报告，未执行任何 `git commit`。
