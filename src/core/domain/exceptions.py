"""排盘领域异常体系（领域层）。

计算失败时抛出显式异常，使调用方（API 层 / self_check）能拿到可操作的定位信息，
而非底层库原始报错或静默的错误结果。

注：docs/08 §8.8.1 仅定义 BaziEngine 接口与数据类、未定义异常；本模块为 Sprint 48 补齐。
"""


class EngineCalculationError(Exception):
    """排盘计算领域级错误（时区解析失败 / 真太阳时校准无法继续等）。

    异常信息须携带可操作的定位提示（如提示 tzdata 未安装）。
    """
    pass
