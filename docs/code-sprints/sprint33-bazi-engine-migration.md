# Sprint 33 — bazi_core.py 正式迁移

> **日期:** 2026-07-17
> **执行者:** Claude Code
> **目标:** 将 `docs/sprint27-walking-skeleton/scripts/bazi_core.py` 验证过的四柱排盘逻辑，正式迁移到 `docs/23_代码目录结构规划.md` 规划的目录位置，并实现为继承 08 §8.8.1 `BaziEngine` ABC 的正式类。
> **范围:** 仅迁移已验证的排盘逻辑，**不**新增用神/格局引擎，**不**接入 ABC 全部字段，**不** git commit。

---

## 1. 迁移前后路径对照

| 来源（walking skeleton） | 目标（正式目录，依据 23 §6.2） | 说明 |
|---|---|---|
| `bazi_core.py` :: `Pillar` / `BaZiResult` 数据类 | `src/core/domain/models/bazi_chart.py` | 领域模型，字段与 08 §8.8.1 一致 |
| `bazi_core.py` :: `HEAVENLY_STEMS` / `EARTHLY_BRANCHES` / `HIDDEN_STEMS_MAP` / `SIXTY_CYCLE_NAYIN` | `src/core/infrastructure/bazi/constants.py` | 排盘引擎常量 |
| `bazi_core.py` :: `calculate_bazi()` | `src/core/domain/services/paipan.py` | 领域服务——排盘计算核心 |
| `bazi_core.py` :: `_build_ganzhi_index` / `_stem_index` / `_branch_index` / `_ganzhi_to_index_lookup` / `_nayin_from_ganzhi` | `src/core/infrastructure/bazi/utils.py` | 工具函数 |
| `bazi_core.py` :: `self_check()` | `src/core/infrastructure/bazi/engine.py` | 继承 ABC 后作为 `self_check` 实现 |
| （新增）08 §8.8.1 的 `BaziEngine` ABC | `src/core/domain/interfaces/bazi_engine.py` | 抽象接口（原 walking skeleton 无此层） |
| （新增）`BaZiRequest` 入参数据类 | `src/core/domain/models/bazi_chart.py` | 对应 ABC `paipan(request)` 入参 |
| （新增）`LunarBaziEngine` 实现类 | `src/core/infrastructure/bazi/engine.py` | 实现 `BaziEngine`，持有 `paipan/validate/engine_info/self_check` |
| （新增）`requirements.txt`（根目录） | `requirements.txt` | 登记 `lunar_python==1.4.8` |

> 迁移映射完全遵循 `docs/23_代码目录结构规划.md` §6.2 迁移映射表。其中 `self_check()` 的目标（23 §6.2 末行 / §6.3 #2）明确为「继承 BaziEngine ABC 后作为 self_check 实现」，故落点在 `engine.py` 而非 `paipan.py`。

---

## 2. 代码改动

> 本 Sprint 全部为**新建文件**，无对既有文件的修改。下方以「【新建文件】路径」标注并附完整内容。

### 【新建文件】`src/core/domain/models/bazi_chart.py`

领域模型：`Pillar` / `BaZiResult` / `BaZiRequest`。

> 与 08 §8.8.1 的差异说明：`BaZiResult` 的 `birth_time_unknown` / `great_fortune_start_age` / `great_fortune_cycle` 三字段在 08 接口中列出但**未给默认值**；此处补上安全默认值（`False` / `0` / 空列表）以便实例化，字段名与类型完全不变、与接口兼容。

```python
"""
bazi_chart.py — 排盘领域模型（Pillar / BaZiResult / BaZiRequest）

字段定义与 docs/08_系统架构设计.md §8.8.1 的 BaziEngine 接口保持一致。
迁移来源: docs/sprint27-walking-skeleton/scripts/bazi_core.py 中验证过的
Pillar / BaZiResult 数据类（本 Sprint 仅原样迁移，不新增用神/格局引擎）。

说明: 08 §8.8.1 的 BaZiResult 列出 birth_time_unknown / great_fortune_start_age /
great_fortune_cycle 三个字段但未给默认值；此处为便于实例化补上安全的默认值
（False / 0 / 空列表），不改动字段名与类型，与接口完全兼容。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Pillar:
    """柱（年/月/日/时）"""
    heavenly_stem: str
    earthly_branch: str
    hidden_stems: list[str]
    na_yin: str


@dataclass
class BaZiResult:
    """四柱八字排盘结果"""
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    gender: str
    birth_time_unknown: bool = False
    great_fortune_start_age: int = 0
    great_fortune_cycle: list[dict] = field(default_factory=list)
    yong_shen: Optional[str] = None      # 用神
    xi_shen: Optional[str] = None        # 喜神
    ji_shen: Optional[str] = None        # 忌神
    engine_name: str = ""
    engine_version: str = ""
    calculated_at: str = ""


@dataclass
class BaZiRequest:
    """排盘请求（输入参数）— 对应 08 §8.8.1 BaziEngine 接口的 paipan 入参"""
    birth_year: int
    birth_month: int
    birth_day: int
    birth_hour: int
    birth_minute: int
    calendar_type: str           # "solar" | "lunar"
    gender: str                  # "male" | "female"
    longitude: float             # 经度（真太阳时校准，必填）
    latitude: float              # 纬度
    timezone: str                # 时区标识（必填）
    birth_time_unknown: bool = False
```

### 【新建文件】`src/core/domain/interfaces/bazi_engine.py`

抽象接口：`BaziEngine` ABC，与 08 §8.8.1 逐字对齐。

```python
"""
bazi_engine.py — 排盘引擎抽象接口（BaziEngine ABC）

定义与 docs/08_系统架构设计.md §8.8.1 完全一致。任何具体排盘引擎
（如 lunar_python 实现）必须继承本 ABC 并实现 paipan / validate / engine_info。
self_check 提供默认空实现，具体引擎应覆盖以执行边界案例校验。

self_check() 机制: 任何新引擎接入前必须通过 self_check，强制验证节气换年
（立春）和节气换月（惊蛰）的正确性。
"""

from abc import ABC, abstractmethod

from core.domain.models.bazi_chart import BaZiRequest, BaZiResult


class BaziEngine(ABC):
    """排盘引擎抽象基类"""

    @abstractmethod
    def paipan(self, request: BaZiRequest) -> BaZiResult:
        pass

    @abstractmethod
    def validate(self, request: BaZiRequest) -> list[str]:
        pass

    @property
    @abstractmethod
    def engine_info(self) -> dict:
        """返回引擎能力声明，至少包含：
        handles_jieqi / handles_lichun / handles_true_solar_time / supports_yongshen
        """
        pass

    def self_check(self) -> list[str]:
        """自检：用边界案例验证引擎准确性。
        至少覆盖立春（年柱）和惊蛰（月柱）临界点。
        返回失败项列表，空列表表示全部通过。
        """
        return []
```

### 【新建文件】`src/core/infrastructure/bazi/constants.py`

常量表，与 walking skeleton 完全一致（天干 / 地支 / 藏干 / 六十甲子纳音）。

```python
"""
constants.py — 排盘引擎常量（天干地支 / 纳音 / 藏干）

迁移来源: docs/sprint27-walking-skeleton/scripts/bazi_core.py 验证过的常量表。
字段命名与 walking skeleton 完全一致，未做改动。
"""

# 天干
HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
# 地支
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

# 藏干映射表（地支 → 藏干列表）
# 来源: 渊海子平 / 三命通会 标准藏干表
HIDDEN_STEMS_MAP: dict[str, list[str]] = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

# 六十甲子纳音分段表（每对干支对应一个纳音）
# 以 60 甲子顺序索引 0-59，每个索引对应一个干支
SIXTY_CYCLE_NAYIN = [
    # 0-9: 甲子~癸酉
    "海中金", "海中金", "炉中火", "炉中火", "大林木", "大林木",
    "路旁土", "路旁土", "剑锋金", "剑锋金",
    # 10-19: 甲戌~癸未
    "山头火", "山头火", "涧下水", "涧下水", "城头土", "城头土",
    "白蜡金", "白蜡金", "杨柳木", "杨柳木",
    # 20-29: 甲申~癸巳
    "泉中水", "泉中水", "屋上土", "屋上土", "霹雳火", "霹雳火",
    "松柏木", "松柏木", "长流水", "长流水",
    # 30-39: 甲午~癸卯
    "沙中金", "沙中金", "山下火", "山下火", "平地木", "平地木",
    "壁上土", "壁上土", "金箔金", "金箔金",
    # 40-49: 甲辰~癸丑
    "覆灯火", "覆灯火", "天河水", "天河水", "大驿土", "大驿土",
    "钗钏金", "钗钏金", "桑柘木", "桑柘木",
    # 50-59: 甲寅~癸亥
    "大溪水", "大溪水", "沙中土", "沙中土", "天上火", "天上火",
    "石榴木", "石榴木", "大海水", "大海水",
]
```

### 【新建文件】`src/core/infrastructure/bazi/utils.py`

工具函数。

> **改动说明：** 原 walking skeleton 中的 `_ganzhi_to_index()` 是一个**占位残骸**——函数体直接 `raise ValueError("Use _calc_ganzhi_index instead")`，带一整段推导注释，但未参与任何实际计算（`calculate_bazi` 与 `nayin` 计算均未调用它）。本次迁移**剔除**该死代码，仅保留已验证可用的查表实现。

```python
"""
utils.py — 排盘辅助工具函数

迁移来源: docs/sprint27-walking-skeleton/scripts/bazi_core.py 中验证过的辅助函数。

注意: 原文件中的 _ganzhi_to_index() 为占位残骸（函数体直接 raise ValueError，
带有一段长长的推导注释，但未参与任何实际计算，calculate_bazi 与 nayin 计算均
未调用它）。本次迁移已剔除该死代码。保留下方已验证可用的查表实现。
"""

from core.infrastructure.bazi.constants import (
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    SIXTY_CYCLE_NAYIN,
)

# 六十甲子索引预计算表 (ganzhi_str -> index)
_GANZHI_INDEX_CACHE: dict[str, int] = {}


def _build_ganzhi_index() -> None:
    """预计算六十甲子索引"""
    if _GANZHI_INDEX_CACHE:
        return
    for idx in range(60):
        stem = HEAVENLY_STEMS[idx % 10]
        branch = EARTHLY_BRANCHES[idx % 12]
        _GANZHI_INDEX_CACHE[stem + branch] = idx


def _stem_index(stem: str) -> int:
    """天干 → 索引 (0-9)"""
    return HEAVENLY_STEMS.index(stem)


def _branch_index(branch: str) -> int:
    """地支 → 索引 (0-11)"""
    return EARTHLY_BRANCHES.index(branch)


def _ganzhi_to_index_lookup(ganzhi: str) -> int:
    """查表法获取六十甲子索引 (ganzhi 如 "甲子" -> 0)"""
    _build_ganzhi_index()
    return _GANZHI_INDEX_CACHE[ganzhi]


def _nayin_from_ganzhi(ganzhi: str) -> str:
    """根据干支获取纳音（每对干支共享一个纳音）"""
    idx = _ganzhi_to_index_lookup(ganzhi)
    # 每对干支共享一个纳音（2 个一组）
    pair_idx = idx // 2
    return SIXTY_CYCLE_NAYIN[pair_idx]
```

### 【新建文件】`src/core/domain/services/paipan.py`

排盘计算核心。将 walking skeleton 的 `calculate_bazi(year, month, day, hour, minute, longitude)` **改造为** `calculate_bazi(request: BaZiRequest) -> BaZiResult`，对齐 08 §8.8.1 的 `paipan(request)` 入参约定；计算逻辑（lunar_python Exact 方法）原样保留。

```python
"""
paipan.py — 排盘计算领域服务（四柱计算核心逻辑）

迁移来源: docs/sprint27-walking-skeleton/scripts/bazi_core.py 中验证过的
calculate_bazi() 函数（节气感知四柱计算）。本 Sprint 仅原样迁移，
不新增用神/格局引擎。

命名对齐 08 §8.8.1 接口: 以 BaZiRequest 为入参，返回 BaZiResult；
字段/类型与 domain/models/bazi_chart.py 中的定义完全一致。
"""

from datetime import datetime

from lunar_python import Solar

from core.domain.models.bazi_chart import BaZiRequest, BaZiResult, Pillar
from core.infrastructure.bazi.constants import HIDDEN_STEMS_MAP


def calculate_bazi(request: BaZiRequest) -> BaZiResult:
    """
    计算四柱八字。

    使用 lunar_python 库进行节气感知的排盘计算。
    年柱/月柱使用 Exact 方法（立春换年、节气换月）。
    时柱根据输入的小时计算。

    参数:
        request: BaZiRequest 排盘请求（calendar_type 默认 "solar"）

    返回:
        BaZiResult 对象
    """
    # 创建 Solar 对象（含时分秒）
    solar = Solar.fromYmdHms(
        request.birth_year,
        request.birth_month,
        request.birth_day,
        request.birth_hour,
        request.birth_minute,
        0,
    )
    lunar = solar.getLunar()

    # 获取四柱干支（Exact 版本：立春感知换年、节气感知换月）
    year_ganzhi = lunar.getYearInGanZhiExact()      # 年柱
    month_ganzhi = lunar.getMonthInGanZhiExact()    # 月柱
    day_ganzhi = lunar.getDayInGanZhi()             # 日柱（午夜换日）
    time_ganzhi = lunar.getTimeInGanZhi()           # 时柱

    # 获取日主（日干）
    day_master = lunar.getDayGan()

    # 提取地支
    year_branch = year_ganzhi[1]
    month_branch = month_ganzhi[1]
    day_branch = day_ganzhi[1]
    time_branch = time_ganzhi[1]

    year_pillar = Pillar(
        heavenly_stem=year_ganzhi[0],
        earthly_branch=year_branch,
        hidden_stems=HIDDEN_STEMS_MAP.get(year_branch, []),
        na_yin=lunar.getYearNaYin(),
    )
    month_pillar = Pillar(
        heavenly_stem=month_ganzhi[0],
        earthly_branch=month_branch,
        hidden_stems=HIDDEN_STEMS_MAP.get(month_branch, []),
        na_yin=lunar.getMonthNaYin(),
    )
    day_pillar = Pillar(
        heavenly_stem=day_ganzhi[0],
        earthly_branch=day_branch,
        hidden_stems=HIDDEN_STEMS_MAP.get(day_branch, []),
        na_yin=lunar.getDayNaYin(),
    )
    hour_pillar = Pillar(
        heavenly_stem=time_ganzhi[0],
        earthly_branch=time_branch,
        hidden_stems=HIDDEN_STEMS_MAP.get(time_branch, []),
        na_yin=lunar.getTimeNaYin(),
    )

    # 当前时间戳
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return BaZiResult(
        year_pillar=year_pillar,
        month_pillar=month_pillar,
        day_pillar=day_pillar,
        hour_pillar=hour_pillar,
        day_master=day_master,
        gender=request.gender,           # 调用者可覆盖 male/female
        birth_time_unknown=request.birth_time_unknown,
        engine_name="lunar_python",
        engine_version="1.4.8",
        calculated_at=now_str,
    )


def format_bazi(result: BaZiResult) -> str:
    """
    格式化输出四柱八字信息。

    返回格式:
        年柱: 甲辰 (覆灯火) 藏:戊乙癸
        月柱: 丙寅 (炉中火) 藏:甲丙戊
        日柱: 乙卯 (大溪水) 藏:乙
        时柱: 壬午 (杨柳木) 藏:丁己
        日主: 乙
    """
    lines = []
    for name, pillar in [
        ("年柱", result.year_pillar),
        ("月柱", result.month_pillar),
        ("日柱", result.day_pillar),
        ("时柱", result.hour_pillar),
    ]:
        hidden_str = "藏:" + "".join(pillar.hidden_stems)
        lines.append(
            f"{name}: {pillar.heavenly_stem}{pillar.earthly_branch} "
            f"({pillar.na_yin}) {hidden_str}"
        )
    lines.append(f"日主: {result.day_master}")
    return "\n".join(lines)
```

### 【新建文件】`src/core/infrastructure/bazi/engine.py`

正式引擎实现 `LunarBaziEngine(BaziEngine)` + `self_check()`（从 walking skeleton 原样迁移，内部改用 `BaZiRequest` + `self.paipan()`）。入口 `if __name__ == "__main__": LunarBaziEngine().self_check()` 与 walking skeleton 的 `self_check()` 入口保持一致。脚本顶部插入 `sys.path` 引导，使「直接运行脚本」与「`python -m` 模块运行」两种方式均可工作。

```python
"""
engine.py — 排盘引擎正式实现（继承 08 §8.8.1 BaziEngine ABC）

迁移来源: docs/sprint27-walking-skeleton/scripts/bazi_core.py 中验证过的
self_check()（立春/惊蛰边界 + 1990-08-15 黄金数据）。

类名对齐接口设计: LunarBaziEngine 实现
core.domain.interfaces.bazi_engine.BaziEngine。

运行方式:
    python src/core/infrastructure/bazi/engine.py   # 直接运行 self_check
    python -m core.infrastructure.bazi.engine        # 模块方式运行（需 cwd=src）
"""

import os
import sys

# 确保 `src` 在 sys.path 上，使 `core.*` 绝对导入在直接运行脚本时也可用
_SRC_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if _SRC_ROOT not in sys.path:
    sys.path.insert(0, _SRC_ROOT)

from core.domain.interfaces.bazi_engine import BaziEngine  # noqa: E402
from core.domain.models.bazi_chart import BaZiRequest, BaZiResult  # noqa: E402
from core.domain.services.paipan import calculate_bazi  # noqa: E402


class LunarBaziEngine(BaziEngine):
    """基于 lunar_python 的排盘引擎实现"""

    def paipan(self, request: BaZiRequest) -> BaZiResult:
        return calculate_bazi(request)

    def validate(self, request: BaZiRequest) -> list[str]:
        """校验 BaZiRequest 入参合法性，返回错误列表（空=通过）。"""
        errors: list[str] = []
        if not (1900 <= request.birth_year <= 2100):
            errors.append(
                f"birth_year 超出支持范围: {request.birth_year} (建议 1900-2100)"
            )
        if request.calendar_type not in ("solar", "lunar"):
            errors.append(
                f"calendar_type 非法: {request.calendar_type} (应为 solar|lunar)"
            )
        if request.gender not in ("male", "female"):
            errors.append(
                f"gender 非法: {request.gender} (应为 male|female)"
            )
        if not (-180.0 <= request.longitude <= 180.0):
            errors.append(f"longitude 超出范围: {request.longitude}")
        if not (-90.0 <= request.latitude <= 90.0):
            errors.append(f"latitude 超出范围: {request.latitude}")
        return errors

    @property
    def engine_info(self) -> dict:
        """引擎能力声明（08 §8.8.1 要求至少包含 4 个 handles/supports 键）。"""
        return {
            "engine_name": "lunar_python",
            "engine_version": "1.4.8",
            "handles_jieqi": True,             # 节气感知换月
            "handles_lichun": True,            # 立春换年
            "handles_true_solar_time": False,  # 真太阳时校准本 Sprint 未实现
            "supports_yongshen": False,        # 用神推导属下一 Sprint
        }

    def self_check(self) -> list[str]:
        """
        自检：用边界案例验证引擎准确性。

        测试用例:
        1. 年柱边界：立春前后（2024-02-03 癸卯 vs 2024-02-04 甲辰）
        2. 月柱边界：惊蛰前后（2024-03-05 09:00 丙寅 vs 12:00 丁卯）
           2024年惊蛰在3月5日10:23，选择 09:00 vs 12:00 跨临界点
        3. 正常日期对照（1990-08-15 12:00 北京）
           预期: 年柱=庚午, 月柱=甲申, 日柱=壬子, 时柱=丙午, 日主=壬

        返回:
            失败项列表，空列表表示全部通过。
        """
        engine = self
        failures: list[str] = []

        # 默认测试用请求参数（北京时区，仅验证排盘逻辑，gender 不影响四柱）
        def _req(y, mo, d, h, mi):
            return BaZiRequest(
                birth_year=y, birth_month=mo, birth_day=d,
                birth_hour=h, birth_minute=mi,
                calendar_type="solar", gender="male",
                longitude=116.4, latitude=39.9, timezone="Asia/Shanghai",
            )

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

        # ── 测试 2: 惊蛰月柱边界 ──
        # 2024年惊蛰: 3月5日 10:23 UTC+8
        # 3月5日 09:00 → 惊蛰前 → 月柱应为 丙寅（正月寅月）
        # 3月5日 12:00 → 惊蛰后 → 月柱应为 丁卯（二月卯月）
        r3 = engine.paipan(_req(2024, 3, 5, 9, 0))
        r4 = engine.paipan(_req(2024, 3, 5, 12, 0))

        m3 = f"{r3.month_pillar.heavenly_stem}{r3.month_pillar.earthly_branch}"
        m4 = f"{r4.month_pillar.heavenly_stem}{r4.month_pillar.earthly_branch}"

        if m3 != "丙寅":
            failures.append(
                f"惊蛰前月柱错误: 2024-03-05 09:00 → 预期 丙寅, 实际 {m3}"
            )
        else:
            print(f"PASS 惊蛰前月柱: 2024-03-05 09:00 → {m3}")

        if m4 != "丁卯":
            failures.append(
                f"惊蛰后月柱错误: 2024-03-05 12:00 → 预期 丁卯, 实际 {m4}"
            )
        else:
            print(f"PASS 惊蛰后月柱: 2024-03-05 12:00 → {m4}")

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

        for label, actual, expected in checks:
            if actual != expected:
                failures.append(
                    f"1990-08-15 12:00 {label}错误: 预期 {expected}, 实际 {actual}"
                )
            else:
                print(f"PASS 1990-08-15 12:00 {label}: {actual}")

        # 日主验证
        dm = r5.day_master
        if dm != "壬":
            failures.append(f"1990-08-15 12:00 日主错误: 预期 壬, 实际 {dm}")
        else:
            print(f"PASS 1990-08-15 12:00 日主: {dm}")

        # ── 汇总 ──
        if not failures:
            print("\nOK self_check: 全部通过!")
        else:
            print(f"\nFAIL self_check: {len(failures)} 项失败:")
            for f in failures:
                print(f"  - {f}")

        return failures


if __name__ == "__main__":
    LunarBaziEngine().self_check()
```

### 【新建文件】`requirements.txt`（根目录）

```
# 知命 AI 人生档案顾问 — Python 核心服务依赖
# 本文件由 Sprint 33（bazi_core.py 正式迁移）创建。

# 排盘引擎依赖：节气感知四柱计算（立春换年 / 节气换月）
lunar_python==1.4.8
```

### 包初始化文件（均为空）

`src/core/__init__.py`、`src/core/domain/__init__.py`、`src/core/domain/models/__init__.py`、`src/core/domain/services/__init__.py`、`src/core/domain/interfaces/__init__.py`、`src/core/infrastructure/__init__.py`、`src/core/infrastructure/bazi/__init__.py`

---

## 3. `self_check()` 原始运行输出

> 运行命令（直接脚本方式）：`python src/core/infrastructure/bazi/engine.py`
> 运行环境：Python 3.13.7 / lunar_python 1.4.8（与 `requirements.txt` 锁定版本一致）
> 退出码：`0`（全部通过）

首次原始运行（控制台默认 GBK 编码，中文乱码但逻辑通过，exit=0）：

```
PASS ����ǰ����: 2024-02-03 12:00 -> ��î
PASS ����������: 2024-02-04 20:00 -> �׳�
PASS ����ǰ����: 2024-03-05 09:00 �� ����
PASS ���ݺ�����: 2024-03-05 12:00 �� ��î
PASS 1990-08-15 12:00 ����: ����
PASS 1990-08-15 12:00 ����: ����
PASS 1990-08-15 12:00 ����: ����
PASS 1990-08-15 12:00 ʱ��: ����
PASS 1990-08-15 12:00 ����: ��

OK self_check: ȫ��ͨ��!
=== EXIT CODE: 0 ===
```

强制 UTF-8 后的同一次成功运行（用于清晰核对，输出内容一致）：

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

OK self_check: 全部通过!
=== EXIT CODE: 0 ===
```

> 另以模块方式 `cd src && python -m core.infrastructure.bazi.engine` 复跑，exit=0，结果一致，确认正式包结构（`core.*` 绝对导入）可正常加载。

---

## 4. 审核摘要

### 4.1 接口命名是否与 08 §8.8.1 完全对齐

| 项 | 08 §8.8.1 定义 | 本 Sprint 实现 | 对齐 |
|---|---|---|---|
| `Pillar` 字段 | `heavenly_stem / earthly_branch / hidden_stems / na_yin` | 完全一致 | ✅ |
| `BaZiResult` 字段 | 13 字段（含 `yong_shen/xi_shen/ji_shen/engine_name/...`） | 字段名/类型一致（3 字段补默认值，见 §2 bazi_chart 说明） | ✅ |
| `BaZiRequest` | `birth_year~timezone` + `birth_time_unknown` | 完全一致 | ✅ |
| `BaziEngine.paipan` | `@abstractmethod paipan(request)->BaZiResult` | `LunarBaziEngine.paipan` 实现 | ✅ |
| `BaziEngine.validate` | `@abstractmethod validate(request)->list[str]` | 实现（入参/返回对齐） | ✅ |
| `BaziEngine.engine_info` | `@property @abstractmethod -> dict`（≥4 键） | 返回含 `handles_jieqi/handles_lichun/handles_true_solar_time/supports_yongshen` | ✅ |
| `BaziEngine.self_check` | 默认空实现，要求覆盖立春/惊蛰 | 覆盖立春年柱 + 惊蛰月柱 + 1990 黄金数据 | ✅ |

**结论：完全对齐。** 类名 `LunarBaziEngine` 为 08 接口未指定的实现类名，按「以 lunar_python 实现」语义命名，无冲突。

### 4.2 需要产品负责人判断的地方

1. **`gender` 取值语义**：08 接口 `gender: "male" | "female"`，但 walking skeleton 历来用 `"unknown"` 占位（排盘逻辑实际不依赖性别）。本次 `BaZiRequest.gender` 按 08 设为必填且 `validate()` 仅接受 `male/female`。若后续「未知性别」场景（如档案初建）需要保留，需产品负责人决定是扩展枚举（加 `"unknown"`）还是调整 `validate` 规则。
2. **`handles_true_solar_time=False` / `supports_yongshen=False`**：`engine_info` 已如实声明本 Sprint 未实现真太阳时校准与用神推导。是否需要在本引擎内实现、还是交给下一 Sprint 的 `mingli.py`，需产品/架构确认（23 §6.3 #4 已标注为后续扩展）。
3. **`latitude` / `timezone` 字段当前为「接收但不参与计算」**：lunar_python 的 `Solar.fromYmdHms` 按输入时分直接构造，未经真太阳时换算。若产品要求高精度的真太阳时校准，需明确是否接入（见上条）。

### 4.3 新发现问题

1. **walking skeleton 死代码**：原 `bazi_core.py` 的 `_ganzhi_to_index()` 是占位残骸（直接 `raise ValueError`），从未被调用。已在本迁移中剔除，不影响任何计算。建议 walking skeleton 源文件后续清理（不影响本次迁移）。
2. **`calculated_at` 使用 `datetime.now()`**：正式代码仍沿用 walking skeleton 的本地时间字符串。若产品要求时区明确或机器可读格式（ISO-8601 UTC），建议后续统一为 `datetime.now(timezone.utc).isoformat()`——属后续打磨项，不影响本 Sprint 验证。
3. **`great_fortune_*`（大运）字段均为空/0**：walking skeleton 与 08 接口均未实现大运计算，本 Sprint 按「不扩展」铁律保留空位，字段存在但无计算逻辑。大运顺逆规则按 23 §6.3 属后续 Sprint。
4. **无 import / 路径运行失败**：首次运行即成功（exit=0），未发生需要重试调整的失败。为兼顾「直接脚本运行」与「`python -m` 模块运行」两种方式，在 `engine.py` 顶部加了 `sys.path` 引导（仅入口文件），属无害的工程便利，已在代码注释说明。

---

## 5. 遗留事项

- 未 git commit（按 Sprint 33 铁律 #3）。
- `docs/23_代码目录结构规划.md` 仍为 Draft（其 §6.2 迁移映射表已与本次实际落地核对一致）。
- 后续 Sprint：用神/喜神/忌神推导引擎（23 §6.3 #4）、大运计算、真太阳时校准、AI 解读层 `ai_interpret.py` 迁移至 `src/core/infrastructure/ai/`。
