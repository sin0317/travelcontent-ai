"""行程编排：把飞猪真实数据（景点 + 酒店）整理成 N 天结构化行程，
并区分「脚本重点提到」与「补充推荐」两类资源。
纯规则编排，零外部依赖；在百炼 Managed Agent 中可由大模型进一步个性化。
"""
from __future__ import annotations

from typing import Any, Optional


def _name(item: dict) -> Optional[str]:
    # 兼容 search-poi 的 name 与 keyword-search 的 info.title
    return item.get("name") or (item.get("info") or {}).get("title")


def _copy_item(item: dict) -> dict:
    """保留原始字段的浅拷贝，供前端/渲染使用。"""
    return {k: v for k, v in item.items()}


def build_itinerary(city: str, days: int, pois: list[dict], hotels: list[dict]) -> dict:
    days = max(1, int(days))
    poi_items = []
    seen_names = set()
    for p in pois:
        n = _name(p)
        if n and n not in seen_names:
            seen_names.add(n)
            poi_items.append(_copy_item(p))

    hotel_items = []
    seen_names.clear()
    for h in hotels:
        n = _name(h)
        if n and n not in seen_names:
            seen_names.add(n)
            hotel_items.append(_copy_item(h))

    # 把景点分配到每一天，并区分「脚本要提到」vs「补充」
    daily = []
    for d in range(1, days + 1):
        # 当天按轮转取景点
        day_spots = [poi_items[i] for i in range(len(poi_items)) if i % days == (d - 1)]
        if not day_spots and poi_items:
            day_spots = poi_items[:1]
        # 每天前 2 个进入口播脚本，剩余作为补充
        script_spots = day_spots[:2]
        extra_spots = day_spots[2:]
        daily.append({
            "day": d,
            "spots": day_spots,
            "script_spots": script_spots,
            "extra_spots": extra_spots,
        })

    # 酒店前 2 家进入脚本推荐，其余补充
    script_hotels = hotel_items[:2]
    extra_hotels = hotel_items[2:]

    return {
        "city": city,
        "days": days,
        "daily": daily,
        "hotels": hotel_items[:5],
        "script_hotels": script_hotels,
        "extra_hotels": extra_hotels,
    }
