"""命令行入口：一键生成「行程 + 视频脚本」。

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


def _render(city: str, days: int, pois: list, hotels: list) -> str:
    itin = build_itinerary(city, days, pois, hotels)
    script = gen_script(city, itin)

    md: list[str] = []
    md.append(f"# {city} {days} 日游 · 游纪 AI 生成")
    md.append("")
    md.append("## 真实数据快照（飞猪实时）")
    md.append(f"- 景点命中：{len(pois)} 个")
    md.append(f"- 酒店命中：{len(hotels)} 个")

    if pois:
        md.append("")
        md.append("### 推荐景点")
        for p in pois[:8]:
            name = p.get("name") or (p.get("info") or {}).get("title")
            addr = p.get("address") or ""
            url = p.get("jumpUrl") or (p.get("info") or {}).get("jumpUrl") or ""
            if not name:
                continue
            line = f"- **{name}**" + (f"  {addr}" if addr else "")
            if url:
                line += f"  [购票]({url})"
            md.append(line)

    if hotels:
        md.append("")
        md.append("### 推荐酒店")
        for h in hotels[:5]:
            name = h.get("name") or (h.get("info") or {}).get("title")
            price = h.get("price") or (h.get("info") or {}).get("price") or ""
            url = h.get("detailUrl") or (h.get("info") or {}).get("jumpUrl") or ""
            if not name:
                continue
            line = f"- **{name}**" + (f"  {price}" if price else "")
            if url:
                line += f"  [查看]({url})"
            md.append(line)

    md.append("")
    md.append(script)
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
