"""内容生成：基于真实行程，生成可拍成短视频的旅行口播脚本（模板化）。

本作品的差异化亮点：不止于"查数据"，而是把真实数据编排成"内容"——
一条可直接用于抖音 / B站 / 小红书的口播脚本，呼应视频创作与文旅传播需求。
在百炼 Managed Agent 中接入大模型后，可把本模板升级为更具个性化的 AI 生成脚本。
"""
from __future__ import annotations

from typing import Any


def _name(item: dict) -> str:
    return item.get("name") or (item.get("info") or {}).get("title") or ""


def gen_script(city: str, itinerary: dict) -> str:
    days = itinerary["days"]
    all_script_spots = []
    for d in itinerary["daily"]:
        all_script_spots.extend([_name(s) for s in d["script_spots"]])
    all_script_spots = [s for s in all_script_spots if s]
    script_hotels = [_name(h) for h in itinerary["script_hotels"] if _name(h)]

    lines: list[str] = []
    lines.append(f"# {city} {days} 日游 · 短视频口播脚本")
    lines.append("")
    lines.append(f"> 基于飞猪实时真实数据生成 · 可直接用于抖音 / B站 / 小红书口播 · 总时长约 60–90 秒")
    lines.append("")

    # 开场钩子
    lines.append("## 开场钩子（0–6s）")
    lines.append(
        f"“来 {city} 玩了 {days} 天，发现 90% 的人都去错了地方。"
        f"这条视频帮你把 {city} 最好拍、最不踩坑的点一次说清，收藏了直接照着走。”"
    )
    lines.append("")

    # 行程主体：每天一段
    lines.append("## 行程主线")
    for d in itinerary["daily"]:
        day_spots = [_name(s) for s in d["script_spots"] if _name(s)]
        if not day_spots:
            continue
        lines.append(f"### 第 {d['day']} 天")

        # 上午
        lines.append(f"**上午：先去 {day_spots[0]}。**")
        lines.append(
            f"“第一站 {day_spots[0]}。这里不光出片，关键是 {city} 的本地氛围特别浓。"
            f"建议早上 9 点前到，避开人流，拍一组空镜开场。"
            f"飞猪购票链接我放评论区了，提前买能省不少排队时间。”"
        )
        lines.append("- **镜头建议**：大门空镜 + 人物背影入画 + 标志性机位特写。")
        lines.append("")

        # 下午/第二个点
        if len(day_spots) >= 2:
            lines.append(f"**下午：转战 {day_spots[1]}。**")
            lines.append(
                f"“下午去 {day_spots[1]}，和上午形成对比。"
                f"这条路线是我按距离和光线排好的，拍完中午还能顺路吃饭。"
                f"想要同款路线可以直接在评论区拿。”"
            )
            lines.append("- **镜头建议**：路途中转场镜头 + 第二站全景 + 人物互动/打卡动作。")
            lines.append("")

        # 天与天之间的转场（除最后一天）
        if d["day"] < days:
            lines.append(
                f"**转场口播**："
                f"“第 {d['day']} 天先这样，第 {d['day'] + 1} 天我带你们去 {city} 另一个更值得拍的点。”"
            )
            lines.append("")

    # 酒店
    lines.append("## 住哪儿")
    if script_hotels:
        stay_line = "、".join(script_hotels)
        lines.append(
            f"“住宿我推荐 {stay_line}，"
            f"都是飞猪高分且离上面这些点比较方便的酒店。"
            f"价格会随日期浮动，评论区放了同款链接，订之前可以比价。”"
        )
    else:
        lines.append(
            f"“住宿建议选在市中心或景区沿线，飞猪上按评分排序挑高分酒店，"
            f"同款链接放评论区。”"
        )
    lines.append("")

    # 结尾 CTA
    lines.append("## 结尾 CTA（最后 5s）")
    lines.append(
        f"“好了，这份 {city} {days} 天攻略里的景点、酒店、路线全来自飞猪实时数据。"
        f"评论区有购票和酒店同款链接，出发前再确认一次价格。"
        f"点我主页，还有更多城市的 AI 旅行脚本。”"
    )
    lines.append("")

    lines.append("---")
    lines.append(
        "提示：在百炼 Managed Agent 中接入大模型后，可把本模板替换为更具个性化的 AI 生成脚本。"
    )
    return "\n".join(lines)
