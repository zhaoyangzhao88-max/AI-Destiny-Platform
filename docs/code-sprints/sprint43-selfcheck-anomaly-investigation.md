# Sprint 43 — self_check 内容异常调查

> 执行模式：纯只读比对。本 Sprint 除本报告文件外未做任何写操作（未改代码、未 commit、未 push）。
> 调查对象：`src/core/infrastructure/bazi/engine.py`
> 调查日期：2026-07-19

---

## 1. 对比 self_check() 源码与提交历史中的版本

**命令（原任务指定，已按 Windows 路径落地）：**

```bash
git show e00036a:src/core/infrastructure/bazi/engine.py > $TEMP/e00036a_engine.py
git show 5ecf923:src/core/infrastructure/bazi/engine.py > $TEMP/5ecf923_engine.py
git diff --no-index $TEMP/e00036a_engine.py $TEMP/5ecf923_engine.py
```

**结果（完整，无摘要）：**

```
（git diff --no-index 无任何输出）
```

**额外校验（文件哈希，确认非“近似相同”）：**

```
(Get-FileHash e00036a_engine.py).Hash == (Get-FileHash 5ecf923_engine.py).Hash
→ IDENTICAL: SHA256 hashes match
```

**事实：**
- `e00036a`（`feat: Phase 3 编码 Sprint 33-37`）与 `5ecf923`（Sprint 42 提交）两个版本的 `engine.py` **字节完全一致**（SHA256 相同，`git diff --no-index` 空输出）。
- 即：自 Sprint 37 代码落库后，`engine.py` 没有再被改动过。

---

## 2. 确认 5ecf923 这次提交里 engine.py 到底改了什么

**命令：**

```bash
git show 5ecf923 -- src/core/infrastructure/bazi/engine.py
```

**结果（完整，无摘要）：**

```
（无任何输出 —— git show 对该路径无 diff）
```

**事实：**
- 在 Sprint 42 提交 `5ecf923` 中，`engine.py` **没有被任何改动**。
- 当前工作区文件 == `5ecf923` 版本 == `e00036a` 版本（三者一致）。

---

## 3. 逐条核对可疑输出

> 以下“当前源码”指 `src/core/infrastructure/bazi/engine.py` 实测内容（与 `e00036a`/`5ecf923` 一致）。

### 3.1 `2024-02-03 12:00` 是不是把“立春前/立春后”日期或断言弄反了？

**当前 self_check() 对应源码（`engine.py` 第 105–127 行）：**

```python
# ── 测试 1: 立春年柱边界 ──
# 2024年立春: 2月4日 16:27 UTC+8
# 2月3日 12:00 → 立春前 → 年柱应为 癸卯
# 2月4日 20:00 → 立春后 → 年柱应为 甲辰
r1 = engine.paipan(_req(2024, 2, 3, 12, 0))
r2 = engine.paipan(_req(2024, 2, 4, 20, 0))

y1 = f"{r1.year_pillar.heavenly_stem}{r1.year_pillar.earthly_branch}"
y2 = f"{r2.year_pillar.heavenly_stem}{r2.year_pillar.earthly_branch}"

if y1 != "癸卯":
    failures.append(
        f"FAIL 立春前年柱: 2024-02-03 12:00 -> 预期 癸卯, 实际 {y1}"
    )
else:
    print(f"PASS 立春前年柱: 2024-02-03 12:00 -> {y1}")

if y2 != "甲辰":
    failures.append(
        f"FAIL 立春后年柱: 2024-02-04 20:00 -> 预期 甲辰, 实际 {y2}"
    )
else:
    print(f"PASS 立春后年柱: 2024-02-04 20:00 -> {y2}")
```

**事实：**
- 当前代码期望：`2024-02-03 12:00` → `癸卯`（立春前），`2024-02-04 20:00` → `甲辰`（立春后）。
- 断言方向**正确，未弄反**。
- Sprint 42 对话回报里的“`2024-02-03 12:00 -> 甲辰`”**不在本文件真实运行输出中**（见第 4 节附 A 真实输出第 1 行为 `癸卯`）。

---

### 3.2 `1990-08-15` 月柱从“甲申”变成“闰六月”？

**当前 self_check() 对应源码（`engine.py` 第 153–176 行）：**

```python
# ── 测试 3: 正常日期对照 ──
# 1990-08-15 12:00, 北京
# 预期（经多方八字排盘网站验证）: 年柱=庚午, 月柱=甲申, 日柱=壬子, 时柱=丙午
r5 = engine.paipan(_req(1990, 8, 15, 12, 0))

y5 = f"{r5.year_pillar.heavenly_stem}{r5.year_pillar.earthly_branch}"
m5 = f"{r5.month_pillar.heavenly_stem}{r5.month_pillar.earthly_branch}"
d5 = f"{r5.day_pillar.heavenly_stem}{r5.day_pillar.earthly_branch}"
t5 = f"{r5.hour_pillar.heavenly_stem}{r5.hour_pillar.earthly_branch}"

checks = [
    ("年柱", y5, "庚午"),
    ("月柱", m5, "甲申"),
    ("日柱", d5, "壬子"),
    ("时柱", t5, "丙午"),
]
```

**事实：**
- 当前代码期望月柱 = `甲申`（正确干支）。
- 对 `engine.py` 全文检索：**无任何“闰六月”字样**。
- Sprint 42 对话回报里的“`1990-08-15 12:00 月份: 闰六月`”**不在本文件源码与真实运行输出中**（真实输出第 6 行为 `月柱: 甲申`）。

---

### 3.3 “大运: 庚辰”这条是哪来的（真实计算还是硬编码占位）？

**当前 self_check() 全文检索结果：**
- `self_check()` 内**没有任何 `大运` 打印/断言语句**。
- 整个 `engine.py` 中 `大运` 仅出现在注释（测试 4/5/6 的设计说明里），以及 `engine_info`/`validate` 中的 `great_fortune_direction_undetermined` 信号位，**没有任何“庚辰”硬编码或断言**。

**独立验证中实际返回的 `BaZiResult`（见第 4 节附 B）：**

```
great_fortune_start_age=0, great_fortune_cycle=[], great_fortune_direction_undetermined=False
```

**事实：**
- 大运字段为空（`great_fortune_cycle=[]`），与 Sprint 35“大运未实现”状态一致。
- Sprint 42 对话回报里的“`1990-08-15 12:00 大运: 庚辰`”**无法由本文件产生**（源码无此行，真实运行输出亦无此行）。

---

### 3.4 真太阳时案例从“乌鲁木齐”变成“重庆”？

**当前 self_check() 对应源码（`engine.py` 第 221–268 行，节选关键部分）：**

```python
# ── 测试 5: 真太阳时-子时跨日边界（乌鲁木齐） ──
# 钟表 1990-08-15 02:00, 经度 87.6E, 东八区标准经线 120E
# 修正量 = (87.6-120)*4 = -129.6min -> 真太阳时 ≈ 1990-08-14 23:50 (子时)
r_uq4 = engine.paipan(
    _req(1990, 8, 15, 2, 0, longitude=87.6, latitude=43.8,
         timezone="Asia/Shanghai")
)
...
    print(f"PASS 乌鲁木齐02:00 真太阳时日柱(跨日回退): {uq4_d}")
...
    print(f"PASS 乌鲁木齐02:00 真太阳时时柱(子时): {uq4_t}")

# ── 测试 6: 真太阳时-同日时柱翻转（乌鲁木齐） ──
r_uq5 = engine.paipan(
    _req(1990, 8, 15, 13, 0, longitude=87.6, latitude=43.8,
         timezone="Asia/Shanghai")
)
...
    print(f"PASS 乌鲁木齐13:00 真太阳时日柱(同日): {uq5_d}")
...
    print(f"PASS 乌鲁木齐13:00 真太阳时时柱(巳时翻转): {uq5_t}")
```

**期望值来源（来自源码注释与实现，非硬编码常量）：**
- 经度固定写死 `longitude=87.6`（乌鲁木齐），标签为“乌鲁木齐”。
- 期望值 `辛亥`/`庚子`/`壬子`/`乙巳` 是代码注释里预先写好的预期，由 `calculate_bazi` 通过经度校准（`(87.6-120)*4 ≈ -129.6min`）真实计算后比对，并非 `print("PASS")` 无条件通过 —— 断言是 `if uq4_d != "辛亥": failures.append(...)` 结构。
- 真太阳时修正逻辑实现在 `core.domain.services.paipan._true_solar_correction_minutes`（源码注释第 60–71 行说明）。

**事实：**
- 当前代码使用 **乌鲁木齐（87.6E）**，断言 `辛亥`/`庚子`/`壬子`/`乙巳`。
- 源码中**无“重庆”字样**。
- Sprint 42 对话回报里的“`重庆02:00 真太阳时校正(启用缓存)` / `重庆13:00 真太阳时时间(时区转换)`”等标签**不在本文件中**。

---

## 4. 独立验证黄金案例 `1990-08-15 12:00`

### 4.1 原任务命令在当前代码下是否能直接跑

**原任务命令：**

```python
from src.core.domain.services.paipan import calculate_bazi
result = calculate_bazi(1990, 8, 15, 12, 0)
print(result)
```

**实测结果（原样复现）：**

```
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    from src.core.domain.services.paipan import calculate_bazi; ...
ModuleNotFoundError: No module named 'src.core.domain'
```

**进一步定位（两次独立失败原因，均为事实）：**

1. `src/__init__.py` **缺失**（仅 `src/core/__init__.py` 存在），因此 `from src.core...` 无法解析为命名空间包。
2. `calculate_bazi` 当前签名为 `calculate_bazi(request: BaZiRequest)`（单一 `BaZiRequest` 参数），**不是** 5 个 positional 参数。直接用 5 参数调用会得到：
   `TypeError: calculate_bazi() takes 1 positional argument but 5 were given`

> 注：本文件 `engine.py` 自身用的是 `from core.domain.services.paipan import calculate_bazi`（把仓库根的 `src/` 目录加入 `sys.path`），与任务给定的 `from src.core...` 路径不同。

### 4.2 改用当前真实可运行的调用方式

```python
import sys, os
sys.path.insert(0, r"E:\vscode\AI-Destiny-Platform\src")
from core.domain.services.paipan import calculate_bazi
from core.domain.models.bazi_chart import BaZiRequest

req = BaZiRequest(
    birth_year=1990, birth_month=8, birth_day=15,
    birth_hour=12, birth_minute=0,
    calendar_type="solar", gender="male",
    longitude=116.4, latitude=39.9, timezone="Asia/Shanghai",
)
result = calculate_bazi(req)
print(result)
```

### 4.3 原始返回（未经 self_check 包装，直接打印 BaZiResult）

```
BaZiResult(year_pillar=Pillar(heavenly_stem='庚', earthly_branch='午', hidden_stems=['丁', '己'], na_yin='路旁土'), month_pillar=Pillar(heavenly_stem='甲', earthly_branch='申', hidden_stems=['庚', '壬', '戊'], na_yin='泉中水'), day_pillar=Pillar(heavenly_stem='壬', earthly_branch='子', hidden_stems=['癸'], na_yin='桑柘木'), hour_pillar=Pillar(heavenly_stem='丙', earthly_branch='午', hidden_stems=['丁', '己'], na_yin='天河水'), day_master='壬', gender='male', birth_time_unknown=False, great_fortune_start_age=0, great_fortune_cycle=[], great_fortune_direction_undetermined=False, yong_shen=None, xi_shen=None, ji_shen=None, engine_name='lunar_python', engine_version='1.4.8', calculated_at='2026-07-19 09:59:43')
```

**逐字段提取：**

```
year_pillar : 庚午
month_pillar: 甲申
day_pillar  : 壬子
hour_pillar : 丙午
day_master  : 壬
```

**对照黄金答案（年=庚午 / 月=甲申 / 日=壬子 / 时=丙午 / 日主=壬）：** 五个字段**全部一致**。

**事实：** 核心排盘计算逻辑（`calculate_bazi`）当前对黄金案例的输出正确，无回归。

---

## 关键附加发现（事实陈述，非结论）

- Sprint 42 对话中回报的 self_check “原始输出”，与本次用**同一文件**真实运行的输出，在**测试标签与断言值**上完全不同：

  | 维度 | Sprint 42 对话回报 | 本次真实运行（同文件） |
  |------|-------------------|----------------------|
  | 立春/惊蛰测试标签 | 排盘前校验 / 排盘后校验 / 跨年前校验 / 跨年后校验 | 立春前年柱 / 立春后年柱 / 惊蛰前月柱 / 惊蛰后月柱 |
  | 1990-08-15 月柱 | 闰六月 | 甲申 |
  | 立春前年柱值 | 甲辰 | 癸卯 |
  | 惊蛰前月柱值 | 甲寅 | 丙寅 |
  | 大运 | 存在“大运: 庚辰”一行 | 无此行 |
  | 真太阳时城市 | 重庆 | 乌鲁木齐 |

- 由于 `engine.py` 自 `e00036a` 起字节未变（第 1、2 节已证实），上述差异**无法用“提交前代码被改动”解释**。
- 本文件 `self_check()` 中**不存在** Sprint 42 回报里的任何以下标签/行：`大运`、`重庆`、`排盘前校验`、`跨年前校验`、`启用缓存`、`误差`、`同意`、`时区转换`。

> 以上为客观事实记录。原因研判与处理建议不在本 Sprint 范围内。

---

## 附：原始输出贴附

### 附 A — 真实 self_check 输出（本次运行，UTF-8 干净版）

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
(returned failures list length: 0)
```

### 附 B — 独立 verify 原始返回（calculate_bazi 直调，1990-08-15 12:00）

```
=== repr(calculate_bazi(BaZiRequest(1990,8,15,12,0))) ===
BaZiResult(year_pillar=Pillar(heavenly_stem='庚', earthly_branch='午', hidden_stems=['丁', '己'], na_yin='路旁土'), month_pillar=Pillar(heavenly_stem='甲', earthly_branch='申', hidden_stems=['庚', '壬', '戊'], na_yin='泉中水'), day_pillar=Pillar(heavenly_stem='壬', earthly_branch='子', hidden_stems=['癸'], na_yin='桑柘木'), hour_pillar=Pillar(heavenly_stem='丙', earthly_branch='午', hidden_stems=['丁', '己'], na_yin='天河水'), day_master='壬', gender='male', birth_time_unknown=False, great_fortune_start_age=0, great_fortune_cycle=[], great_fortune_direction_undetermined=False, yong_shen=None, xi_shen=None, ji_shen=None, engine_name='lunar_python', engine_version='1.4.8', calculated_at='2026-07-19 09:59:43')

=== individual fields ===
year_pillar : 庚午
month_pillar: 甲申
day_pillar  : 壬子
hour_pillar : 丙午
day_master  : 壬

=== expected (golden) ===
year=庚午 month=甲申 day=壬子 hour=丙午 day_master=壬
```
