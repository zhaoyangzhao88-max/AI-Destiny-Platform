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
