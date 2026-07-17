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
        if request.gender not in ("male", "female", "unknown"):
            errors.append(
                f"gender 非法: {request.gender} (应为 male|female|unknown)"
            )
        if not (-180.0 <= request.longitude <= 180.0):
            errors.append(f"longitude 超出范围: {request.longitude}")
        if not (-90.0 <= request.latitude <= 90.0):
            errors.append(f"latitude 超出范围: {request.latitude}")
        return errors

    @property
    def engine_info(self) -> dict:
        """引擎能力声明（08 §8.8.1 要求至少包含 5 个 handles/supports 键）。"""
        return {
            "engine_name": "lunar_python",
            "engine_version": "1.4.8",
            "handles_jieqi": True,             # 节气感知换月
            "handles_lichun": True,            # 立春换年
            "handles_mean_solar_time": True,   # 经度修正/平太阳时已实现（Sprint 36）
            "handles_equation_of_time": False,  # 均时差尚未实现
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
        4. gender=unknown 信号位验证（1990-08-15 12:00 北京）
           预期: 四柱/日主与 gender=male 完全一致（证明 gender 不影响排盘），
                且 great_fortune_direction_undetermined == True
        5. 真太阳时-子时跨日边界（乌鲁木齐 87.6E, 1990-08-15 02:00）
           钟表 02:00 经经度修正(≈-130min)后真太阳时≈前一日 23:50(子时)，
           预期: 日柱=辛亥(壬子前一日), 时柱=庚子(晚子时取次日日干)
                 ——证明修正导致跨日, 日柱联动回退一天
        6. 真太阳时-同日时柱翻转（乌鲁木齐 87.6E, 1990-08-15 13:00）
           修正后真太阳时≈10:50(巳时), 未修正为13:00(未时)
           预期: 日柱=壬子(同日不变), 时柱=乙巳(巳时)

        返回:
            失败项列表，空列表表示全部通过。
        """
        engine = self
        failures: list[str] = []

        # 默认测试用请求参数（北京时区，仅验证排盘逻辑，gender 不影响四柱）
        def _req(y, mo, d, h, mi, gender="male",
                 longitude=116.4, latitude=39.9, timezone="Asia/Shanghai"):
            return BaZiRequest(
                birth_year=y, birth_month=mo, birth_day=d,
                birth_hour=h, birth_minute=mi,
                calendar_type="solar", gender=gender,
                longitude=longitude, latitude=latitude, timezone=timezone,
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

        # ── 测试 4: gender=unknown 信号位验证 ──
        # 同一生日用 male 与 unknown 各跑一次，四柱/日主应完全一致
        # （证明 gender 不参与排盘计算），且 unknown 时信号位应为 True
        r_male = engine.paipan(_req(1990, 8, 15, 12, 0, gender="male"))
        r_unknown = engine.paipan(_req(1990, 8, 15, 12, 0, gender="unknown"))

        pillars_male = [r_male.year_pillar, r_male.month_pillar, r_male.day_pillar, r_male.hour_pillar]
        pillars_unknown = [r_unknown.year_pillar, r_unknown.month_pillar, r_unknown.day_pillar, r_unknown.hour_pillar]
        pillars_equal = all(
            f"{a.heavenly_stem}{a.earthly_branch}" == f"{b.heavenly_stem}{b.earthly_branch}"
            for a, b in zip(pillars_male, pillars_unknown)
        ) and (r_male.day_master == r_unknown.day_master)

        if pillars_equal:
            print("PASS gender=unknown 四柱/日主与 male 完全一致")
        else:
            failures.append(
                "FAIL gender=unknown 四柱/日主与 male 不一致（gender 不应影响排盘）"
            )

        if r_unknown.great_fortune_direction_undetermined is True:
            print("PASS gender=unknown great_fortune_direction_undetermined == True")
        else:
            failures.append(
                f"FAIL gender=unknown 信号位应为 True, 实际 "
                f"{r_unknown.great_fortune_direction_undetermined}"
            )

        if r_male.great_fortune_direction_undetermined is False:
            print("PASS gender=male great_fortune_direction_undetermined == False")
        else:
            failures.append(
                f"FAIL gender=male 信号位应为 False, 实际 "
                f"{r_male.great_fortune_direction_undetermined}"
            )

        # ── 测试 5: 真太阳时-子时跨日边界（乌鲁木齐） ──
        # 钟表 1990-08-15 02:00, 经度 87.6E, 东八区标准经线 120E
        # 修正量 = (87.6-120)*4 = -129.6min -> 真太阳时 ≈ 1990-08-14 23:50 (子时)
        # 跨日后日柱应回退为 辛亥(壬子前一日); 时柱庚子(晚子时取次日日干壬->庚子)
        r_uq4 = engine.paipan(
            _req(1990, 8, 15, 2, 0, longitude=87.6, latitude=43.8,
                 timezone="Asia/Shanghai")
        )
        uq4_d = f"{r_uq4.day_pillar.heavenly_stem}{r_uq4.day_pillar.earthly_branch}"
        uq4_t = f"{r_uq4.hour_pillar.heavenly_stem}{r_uq4.hour_pillar.earthly_branch}"

        if uq4_d != "辛亥":
            failures.append(
                f"FAIL 乌鲁木齐02:00 真太阳时日柱错误: 预期 辛亥, 实际 {uq4_d}"
            )
        else:
            print(f"PASS 乌鲁木齐02:00 真太阳时日柱(跨日回退): {uq4_d}")

        if uq4_t != "庚子":
            failures.append(
                f"FAIL 乌鲁木齐02:00 真太阳时时柱错误: 预期 庚子(晚子时), 实际 {uq4_t}"
            )
        else:
            print(f"PASS 乌鲁木齐02:00 真太阳时时柱(子时): {uq4_t}")

        # ── 测试 6: 真太阳时-同日时柱翻转（乌鲁木齐） ──
        # 钟表 1990-08-15 13:00 -> 修正后 ≈10:50(巳时); 未修正为 13:00(未时)
        # 日柱保持 壬子(同日), 时柱由 未时 翻为 巳时(乙巳)
        r_uq5 = engine.paipan(
            _req(1990, 8, 15, 13, 0, longitude=87.6, latitude=43.8,
                 timezone="Asia/Shanghai")
        )
        uq5_d = f"{r_uq5.day_pillar.heavenly_stem}{r_uq5.day_pillar.earthly_branch}"
        uq5_t = f"{r_uq5.hour_pillar.heavenly_stem}{r_uq5.hour_pillar.earthly_branch}"

        if uq5_d != "壬子":
            failures.append(
                f"FAIL 乌鲁木齐13:00 真太阳时日柱错误: 预期 壬子, 实际 {uq5_d}"
            )
        else:
            print(f"PASS 乌鲁木齐13:00 真太阳时日柱(同日): {uq5_d}")

        if uq5_t != "乙巳":
            failures.append(
                f"FAIL 乌鲁木齐13:00 真太阳时时柱错误: 预期 乙巳(巳时), 实际 {uq5_t}"
            )
        else:
            print(f"PASS 乌鲁木齐13:00 真太阳时时柱(巳时翻转): {uq5_t}")

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
