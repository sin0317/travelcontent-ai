"""行程编排：把飞猪真实数据（景点 + 酒店）整理成 N 天结构化行程。
纯规则编排，零外部依赖；在百炼 Managed Agent 中可由大模型进一步个性化。
"""
from __future__ import annotations

from typing import Any, Optional


def _name(item: dict) -> Optional[str]:
    # 兼容 search-poi 的 name 与 keyword-search 的 info.title
    return item.get("name") or (item.get("info") or {}).get("title")


def build_itinerary(city: str, days: int, pois: list[dict], hotels: list[dict]) -> dict:
    days = max(1, int(days))
    poi_names = []
    for p in pois:
        n = _name(p)
        if n and n not in poi_names:
            poi_names.append(n)

    hotel_names = []
    for h in hotels:
        n = _name(h)
        if n and n not in hotel_names:
            hotel_names.append(n)

    # 按取模把景点轮转分配到各天，保证每天都有安排
    daily = []
    for d in range(1, days + 1):
        picks = [poi_names[i] for i in range(len(poi_names)) if i % days == (d - 1)]
        if not picks and poi_names:
            picks = poi_names[:1]
        daily.append({"day": d, "spots": picks})

    return {
        "city": city,
        "days": days,
        "daily": daily,
        "hotels": hotel_names[:5],
    }
