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
    # 大运顺逆方向是否待定：性别未知时无法判定大运顺排/逆排，预留给大运计算 Sprint
    great_fortune_direction_undetermined: bool = False
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
    gender: str                  # "male" | "female" | "unknown"
    longitude: float             # 经度（真太阳时校准，必填）
    latitude: float              # 纬度
    timezone: str                # 时区标识（必填）
    birth_time_unknown: bool = False
