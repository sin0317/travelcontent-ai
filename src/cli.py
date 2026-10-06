"""命令行入口：一键生成「脚本 → 脚本提到资源 → 补充资源」。

用法：
    python src/cli.py 开封 --days 2 --category 历史古迹
    python src/cli.py 杭州 --days 3 --hotel-stars 4,5 --out demo/kaifeng.md
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def load_env(path: Path) -> None:
    # 轻量读取 .env，避免引入第三方依赖
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


load_env(ROOT / ".env")

from src.flyai_client import FlyAIClient  # noqa: E402
from src.planner import build_itinerary  # noqa: E402
from src.content_gen import gen_script  # noqa: E402


def _item_name(item: dict) -> str:
    return item.get("name") or (item.get("info") or {}).get("title") or ""


def _item_address(item: dict) -> str:
    return item.get("address") or (item.get("info") or {}).get("address") or ""


def _item_url(item: dict) -> str:
    return (
        item.get("jumpUrl")
        or item.get("detailUrl")
        or (item.get("info") or {}).get("jumpUrl")
        or (item.get("info") or {}).get("detailUrl")
        or ""
    )


def _item_price(item: dict) -> str:
    return item.get("price") or (item.get("info") or {}).get("price") or ""


def _render_item_lines(items: list[dict], is_hotel: bool = False) -> list[str]:
    lines = []
    for it in items:
        name = _item_name(it)
        if not name:
            continue
        line = f"- **{name}**"
        if is_hotel:
            price = _item_price(it)
            if price:
                line += f"  {price}"
        else:
            addr = _item_address(it)
            if addr:
                line += f"  {addr}"
        url = _item_url(it)
        if url:
            label = "查看 / 预订" if is_hotel else "购票 / 详情"
            line += f"  [{label}]({url})"
        lines.append(line)
    return lines


def _render(city: str, days: int, pois: list, hotels: list) -> str:
    itin = build_itinerary(city, days, pois, hotels)
    script = gen_script(city, itin)

    md: list[str] = []
    md.append(f"# {city} {days} 日游 · 游纪 AI 生成")
    md.append("")
    md.append("> 生成结构：短视频口播脚本 → 脚本提到的景点 / 酒店 → 补充景点 / 酒店")
    md.append("")

    # 1. 脚本
    md.append(script)
    md.append("")

    # 2. 脚本提到的资源
    md.append("## 脚本中提到的景点（飞猪实时）")
    script_pois = []
    for d in itin["daily"]:
        script_pois.extend(d["script_spots"])
    lines = _render_item_lines(script_pois, is_hotel=False)
    if lines:
        md.extend(lines)
    else:
        md.append("- 暂无")
    md.append("")

    md.append("## 脚本中提到的酒店（飞猪实时）")
    lines = _render_item_lines(itin["script_hotels"], is_hotel=True)
    if lines:
        md.extend(lines)
    else:
        md.append("- 暂无")
    md.append("")

    # 3. 补充资源
    md.append("## 补充景点")
    extra_pois = []
    for d in itin["daily"]:
        extra_pois.extend(d["extra_spots"])
    lines = _render_item_lines(extra_pois, is_hotel=False)
    if lines:
        md.extend(lines)
    else:
        md.append("- 暂无")
    md.append("")

    md.append("## 补充酒店")
    lines = _render_item_lines(itin["extra_hotels"], is_hotel=True)
    if lines:
        md.extend(lines)
    else:
        md.append("- 暂无")

    return "\n".join(md)


def main() -> None:
    ap = argparse.ArgumentParser(description="游纪 · AI 旅行内容官")
    ap.add_argument("city", help="目的地城市，如 开封")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--category", default="历史古迹",
                    help="景点类别，如 历史古迹/自然风光/主题乐园")
    ap.add_argument("--hotel-stars", default="4,5", help="酒店星级，逗号分隔")
    ap.add_argument("--out", default="", help="输出 markdown 文件路径")
    args = ap.parse_args()

    client = FlyAIClient()
    print(f"正在调用飞猪实时数据：{args.city} ...", file=sys.stderr)

    poi_resp = client.search_poi(args.city, category=args.category)
    hotel_resp = client.search_hotel(args.city, hotel_stars=args.hotel_stars, sort="rate_desc")

    pois = client.items(poi_resp)
    hotels = client.items(hotel_resp)

    if not client.ok(poi_resp):
        print(f"景点查询异常：{poi_resp.get('message')}", file=sys.stderr)
    if not client.ok(hotel_resp):
        print(f"酒店查询异常：{hotel_resp.get('message')}", file=sys.stderr)

    out = _render(args.city, args.days, pois, hotels)
    if args.out:
        Path(args.out).write_text(out, encoding="utf-8")
        print(f"已写入 {args.out}", file=sys.stderr)
    print(out)


if __name__ == "__main__":
    main()
