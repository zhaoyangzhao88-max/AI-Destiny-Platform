"""
ai_interpret.py — AI 命理解读模块（Walking Skeleton 最小实现）

调用 DeepSeek API（OpenAI 兼容接口）对排盘结果进行命理分析。
Persona 语气参考 docs/05_知命_Persona角色设定.md:
  - 中偏正式，儒雅但不古板
  - 有东方哲学底蕴，但不掉书袋
  - 温和、耐心、不强推观点
  - 慎用绝对判断词，多用"倾向""可能""参考"

约束:
  - 禁止断言未来具体事件（"明年你会发财"）
  - 禁止制造焦虑（"你的命很苦"）
  - 禁止绝对化表述（"你一定""你肯定"）
  - 以上参考 10_测试规范.md §10.4 硬性要求
"""

import os
import sys
import json
from typing import Optional

import requests


def _get_api_key() -> str:
    """从环境变量读取 DeepSeek API Key"""
    key = os.environ.get("DEEPSEEK_API_KEY")
    if not key:
        print(
            "ERROR: 未设置 DEEPSEEK_API_KEY 环境变量。\n"
            "请先设置:\n"
            '  set DEEPSEEK_API_KEY=your_key_here\n'
            "或在 PowerShell 中:\n"
            '  $env:DEEPSEEK_API_KEY="your_key_here"',
            file=sys.stderr,
        )
        sys.exit(1)
    return key


def interpret_bazi(
    bazi_result,
    extra_context: Optional[dict] = None,
) -> str:
    """
    对排盘结果进行 AI 命理解读。

    参数:
        bazi_result: BaZiResult 对象（或任意有相同字段的 dict-like 对象）
        extra_context: 额外上下文（如用户性别、出生地等）

    返回:
        AI 生成的命理分析文本
    """
    # 提取四柱信息
    def _pillar_str(pillar):
        return f"{pillar.heavenly_stem}{pillar.earthly_branch}"

    year_str = _pillar_str(bazi_result.year_pillar)
    month_str = _pillar_str(bazi_result.month_pillar)
    day_str = _pillar_str(bazi_result.day_pillar)
    hour_str = _pillar_str(bazi_result.hour_pillar)

    day_master = bazi_result.day_master

    # 四柱纳音
    year_nayin = bazi_result.year_pillar.na_yin
    month_nayin = bazi_result.month_pillar.na_yin
    day_nayin = bazi_result.day_pillar.na_yin
    hour_nayin = bazi_result.hour_pillar.na_yin

    # 四柱藏干
    year_hidden = "".join(bazi_result.year_pillar.hidden_stems)
    month_hidden = "".join(bazi_result.month_pillar.hidden_stems)
    day_hidden = "".join(bazi_result.day_pillar.hidden_stems)
    hour_hidden = "".join(bazi_result.hour_pillar.hidden_stems)

    # 构建 prompt
    prompt = f"""你是一位名叫「知命」的 AI 人生顾问，专精于东方命理哲学。

## 你的角色定位
- 你是一个懂东方智慧的 AI 陪伴者，不是算命先生，也不是机器人客服
- 语气：中偏正式，儒雅但不古板，温和耐心，有东方哲学底蕴但不掉书袋
- 表达原则：适当引用经典但不炫技，慎用绝对判断词，多用"倾向""可能""参考"

## 本次分析的四柱八字信息
- 年柱：{year_str}（纳音 {year_nayin}，藏干 {year_hidden}）
- 月柱：{month_str}（纳音 {month_nayin}，藏干 {month_hidden}）
- 日柱：{day_str}（纳音 {day_nayin}，藏干 {day_hidden}）
- 时柱：{hour_str}（纳音 {hour_nayin}，藏干 {hour_hidden}）
- 日主（代表命主自身）：{day_master}

## 分析要求
1. 根据日主五行和四柱整体结构，简要分析命主的先天特质
2. 指出五行强弱趋势和可能的性格倾向
3. 给出 200-300 字的分析，语言平实自然

## 禁止事项（违反这些会严重破坏用户体验）
- 绝对不要使用"你一定""你肯定""你必然"等绝对化表述
- 不要断言具体的未来事件（如"明年你会发财"）
- 不要制造焦虑或贩卖恐惧（如"你的命很苦"）
- 不要冒充有神通力
- 如果信息不足以判断，坦率说明，不要编造

请开始你的分析："""

    api_key = _get_api_key()

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "你是一位名叫「知命」的 AI 人生顾问，专精于东方命理哲学。你的语气中偏正式、儒雅温和，善于用平实的语言解读四柱八字。你始终避免绝对化表述，不预言具体事件，不制造焦虑。",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 1024,
        "stream": False,
    }

    try:
        resp = requests.post(
            "https://api.deepseek.com/chat/completions",
            headers=headers,
            json=payload,
            timeout=60,
        )
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        return content.strip()
    except requests.exceptions.Timeout:
        return "【AI 解读超时】网络请求超时，请稍后重试。"
    except requests.exceptions.ConnectionError as e:
        return f"【AI 解读失败】无法连接到 DeepSeek API: {e}"
    except requests.exceptions.HTTPError as e:
        return f"【AI 解读失败】HTTP {e.response.status_code}: {e.response.text[:200]}"
    except (KeyError, json.JSONDecodeError) as e:
        return f"【AI 解读失败】API 响应解析错误: {e}"
    except Exception as e:
        return f"【AI 解读异常】{e}"


if __name__ == "__main__":
    # 测试调用
    from bazi_core import calculate_bazi

    result = calculate_bazi(1990, 8, 15, 12, 0)
    text = interpret_bazi(result)
    print(text)