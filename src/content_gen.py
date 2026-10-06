"""内容生成：基于真实行程，生成可拍成短视频的旅行口播脚本（模板化）。

这是本作品的差异化亮点：不止于"查数据"，而是把真实数据编排成"内容"——
一条可直接用于抖音 / B站 / 小红书的口播脚本，呼应视频创作与文旅传播需求。
在百炼 Managed Agent 中接入大模型后，可把本模板升级为更具个性化的 AI 生成脚本。
"""
from __future__ import annotations

from typing import Any


def gen_script(city: str, itinerary: dict) -> str:
    lines: list[str] = []
    lines.append(f"# {city} {itinerary['days']} 日游 · 短视频口播脚本")
    lines.append("")
    lines.append("> 基于飞猪实时真实数据生成 · 可直接用于抖音 / B站 / 小红书口播")
    lines.append("")
    lines.append("## 开场钩子（0-5s）")
    lines.append(
        f"“{city}到底怎么玩才不踩坑？收藏这条，{itinerary['days']}天帮你安排得明明白白。”"
    )
    lines.append("")
    for d in itinerary["daily"]:
        lines.append(f"## 第 {d['day']} 天")
        if d["spots"]:
            spots = "、".join(d["spots"])
            lines.append(f"主打：{spots}")
            lines.append("镜头建议：实拍打卡 + 飞猪购票链接放评论区，边玩边省。")
        else:
            lines.append("自由活动 / 周边探店")
        lines.append("")
    if itinerary["hotels"]:
        lines.append("## 住哪儿")
        lines.append(
            "、".join(itinerary["hotels"][:3]) + " 都是飞猪高分推荐，链接同款放评论区。"
        )
        lines.append("")
    lines.append("## 结尾 CTA（最后 5s）")
    lines.append(
        f"“数据来自飞猪实时库存，价格随时变，点我主页看更多{city}玩法。”"
    )
    lines.append("")
    lines.append("---")
    lines.append(
        "提示：在百炼 Managed Agent 中接入大模型后，可把本模板替换为更具个性化的 AI 生成脚本。"
    )
    return "\n".join(lines)
