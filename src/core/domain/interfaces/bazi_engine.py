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
        handles_jieqi / handles_lichun / handles_mean_solar_time / handles_equation_of_time / supports_yongshen
        """
        pass

    def self_check(self) -> list[str]:
        """自检：用边界案例验证引擎准确性。
        至少覆盖立春（年柱）和惊蛰（月柱）临界点。
        返回失败项列表，空列表表示全部通过。
        """
        return []
