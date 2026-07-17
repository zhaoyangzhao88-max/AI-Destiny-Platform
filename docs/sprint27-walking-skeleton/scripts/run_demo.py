"""
run_demo.py — 完整链路演示脚本（Walking Skeleton）

串联流程:
  输入生日 → calculate_bazi() → 打印四柱 → interpret_bazi() → 打印AI解读

3 组测试案例:
  1. 1990-08-15 12:00 — 正常日期（对照参考）
  2. 2024-02-04 20:00 — 立春当天（年柱边界）
  3. 2000-06-01 08:00 — 千禧年儿童节（正常日期）
"""

import sys
import io

# 设置 UTF-8 输出，避免 Windows 控制台 GBK 编码问题
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

from bazi_core import calculate_bazi, format_bazi
from ai_interpret import interpret_bazi


def run_case(name: str, year: int, month: int, day: int, hour: int, minute: int = 0):
    """运行单个测试案例：排盘 + AI 解读"""
    sep = "=" * 60
    sub = "-" * 60

    print(f"\n{sep}")
    print(f"  案例: {name}")
    print(f"  出生: {year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}")
    print(f"{sep}")

    # Step 1: 排盘
    print("\n【排盘结果】")
    result = calculate_bazi(year, month, day, hour, minute)
    print(format_bazi(result))

    # Step 2: AI 解读
    print(f"\n{sub}")
    print("【AI 命理解读】")
    print(f"{sub}")
    interpretation = interpret_bazi(result)
    print(f"\n{interpretation}\n")


def main():
    cases = [
        ("正常日期 — 1990-08-15 12:00", 1990, 8, 15, 12, 0),
        ("立春边界 — 2024-02-04 20:00 (立春后)", 2024, 2, 4, 20, 0),
        ("千禧年 — 2000-06-01 08:00", 2000, 6, 1, 8, 0),
    ]

    for name, y, m, d, h, mi in cases:
        run_case(name, y, m, d, h, mi)

    print("=" * 60)
    print("  演示结束")
    print("=" * 60)


if __name__ == "__main__":
    main()