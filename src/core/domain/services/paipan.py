"""
paipan.py — 排盘计算领域服务（四柱计算核心逻辑）

迁移来源: docs/sprint27-walking-skeleton/scripts/bazi_core.py 中验证过的
calculate_bazi() 函数（节气感知四柱计算）。本 Sprint 仅原样迁移，
不新增用神/格局引擎。

命名对齐 08 §8.8.1 接口: 以 BaZiRequest 为入参，返回 BaZiResult；
字段/类型与 domain/models/bazi_chart.py 中的定义完全一致。
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from lunar_python import Solar

from core.domain.exceptions import EngineCalculationError
from core.domain.models.bazi_chart import BaZiRequest, BaZiResult, Pillar
from core.infrastructure.bazi.constants import HIDDEN_STEMS_MAP


def _true_solar_correction_minutes(request: BaZiRequest) -> float:
    """
    真太阳时经度修正量（分钟，可正可负）。

    公式（本 Sprint 给定，仅经度差修正）:
        修正分钟数 = (出生地经度 - 时区标准经线) × 4
        时区标准经线 = 标准时区偏移小时数 × 15

    关键: 标准经线必须用「标准时区偏移」(utcoffset - dst)，不能含夏令时。
    例: 1990-08-15 的 Asia/Shanghai 因夏令时 utcoffset=9h，但标准偏移=8h，
    标准经线应为 120°E（8×15），若误用 9h 会得到 135°E 而错算修正量。

    说明: 本实现不含「均时差 (Equation of Time)」修正，属公式范围内的简化。
    """
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
    except Exception as exc:
        # Sprint 48 fail-fast：不再静默退化为 0 修正
        # （0 修正会产出看似合理但错误的真太阳时，掩盖依赖缺失）
        raise EngineCalculationError(
            f"时区解析失败: timezone='{request.timezone}'。"
            f"无法获取标准时区偏移，真太阳时校准无法继续。"
            f"常见原因：tzdata 时区数据库未安装（pip install tzdata），"
            f"或 timezone 字符串非法。原始错误: {exc}"
        ) from exc
    standard_meridian = std_offset_hours * 15.0
    return (request.longitude - standard_meridian) * 4.0


def calculate_bazi(request: BaZiRequest) -> BaZiResult:
    """
    计算四柱八字。

    使用 lunar_python 库进行节气感知的排盘计算。
    年柱/月柱使用 Exact 方法（立春换年、节气换月）。
    时柱根据输入的小时计算。

    入参 birth 时间为【钟表时间】，先按出生地经度做真太阳时校准
    （见 _true_solar_correction_minutes），再用校准后的真太阳时构造 Solar。
    校准导致跨日/跨月/跨年时，由 datetime 算术与 lunar_python 的午夜换日
    逻辑自动联动日柱，无需手动干预。

    参数:
        request: BaZiRequest 排盘请求（calendar_type 默认 "solar"）

    返回:
        BaZiResult 对象
    """
    # 真太阳时校准：钟表时间 → 出生地真太阳时
    delta_minutes = _true_solar_correction_minutes(request)
    base = datetime(
        request.birth_year, request.birth_month, request.birth_day,
        request.birth_hour, request.birth_minute,
    )
    corrected = base + timedelta(minutes=delta_minutes)

    # 用校准后的真太阳时构造 Solar 对象（含时分秒；跨日自动滚入 corrected.date）
    solar = Solar.fromYmdHms(
        corrected.year,
        corrected.month,
        corrected.day,
        corrected.hour,
        corrected.minute,
        corrected.second,
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
        gender=request.gender,           # 调用者可覆盖 male/female/unknown
        birth_time_unknown=request.birth_time_unknown,
        # 性别未知时大运顺逆方向无法判定；本 Sprint 不实现大运计算本身
        great_fortune_direction_undetermined=(request.gender == "unknown"),
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
