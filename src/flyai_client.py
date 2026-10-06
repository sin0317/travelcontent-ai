"""飞猪 FlyAI CLI 封装 —— 把 flyai-cli 的调用与 JSON 解析收口到一处。

飞猪 Skill 本质是通过 @fly-ai/flyai-cli 访问 Fliggy MCP 真实数据。
本模块负责：定位可执行文件、注入 Key（可选）、调用子命令、解析单行 JSON。
"""
from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent


class FlyAIClient:
    def __init__(self, api_key: Optional[str] = None, timeout: int = 60):
        self.timeout = timeout
        self.api_key = api_key or os.environ.get("FLYAI_API_KEY")
        self.bin = self._locate_bin()
        if self.api_key:
            self._apply_key(self.api_key)

    def _locate_bin(self) -> str:
        # 优先使用仓库内局部安装的 flyai-cli
        if os.name == "nt":
            cand = REPO_ROOT / "node_modules" / ".bin" / "flyai.cmd"
        else:
            cand = REPO_ROOT / "node_modules" / ".bin" / "flyai"
        if cand.exists():
            return str(cand)
        # 回退到系统 PATH 中的 flyai / npx @fly-ai/flyai-cli
        return "flyai"

    def _apply_key(self, key: str) -> None:
        # 把 Key 写入 flyai 本地配置（trial 模式无需，失败不影响）
        try:
            subprocess.run(
                [self.bin, "config", "set", "FLYAI_API_KEY", key],
                capture_output=True, text=True,
                shell=(os.name == "nt"), timeout=30,
            )
        except Exception:
            pass

    def _run(self, args: list[str]) -> dict[str, Any]:
        try:
            proc = subprocess.run(
                [self.bin] + args, capture_output=True, text=True,
                shell=(os.name == "nt" and self.bin.endswith(".cmd")),
                timeout=self.timeout,
            )
        except FileNotFoundError:
            return {"status": -1, "message": "flyai CLI 未找到，请先 npm i @fly-ai/flyai-cli", "data": {}}
        except subprocess.TimeoutExpired:
            return {"status": -2, "message": f"调用超时（>{self.timeout}s）", "data": {}}

        raw = (proc.stdout or "").strip()
        if not raw:
            return {"status": -3, "message": (proc.stderr or "").strip() or "空输出", "data": {}}

        # 容错：截取第一个 { 到最后一个 } 之间的 JSON
        start, end = raw.find("{"), raw.rfind("}")
        if start == -1 or end == -1:
            return {"status": -4, "message": "非 JSON 输出: " + raw[:200], "data": {}}
        try:
            return json.loads(raw[start:end + 1])
        except json.JSONDecodeError as e:
            return {"status": -5, "message": f"JSON 解析失败: {e}", "data": {}}

    # ---- 业务方法（参数名对齐 flyai-cli）----
    def keyword_search(self, query: str) -> dict:
        return self._run(["keyword-search", "--query", query])

    def search_poi(self, city_name: str, category: Optional[str] = None,
                   keyword: Optional[str] = None, poi_level: Optional[int] = None) -> dict:
        args = ["search-poi", "--city-name", city_name]
        if category:
            args += ["--category", category]
        if keyword:
            args += ["--keyword", keyword]
        if poi_level:
            args += ["--poi-level", str(poi_level)]
        return self._run(args)

    def search_hotel(self, dest_name: str, **opts) -> dict:
        args = ["search-hotel", "--dest-name", dest_name]
        for k, v in opts.items():
            if v is not None:
                args += ["--" + k.replace("_", "-"), str(v)]
        return self._run(args)

    def search_flight(self, origin: str, destination: Optional[str] = None,
                      dep_date: Optional[str] = None, **opts) -> dict:
        args = ["search-flight", "--origin", origin]
        if destination:
            args += ["--destination", destination]
        if dep_date:
            args += ["--dep-date", dep_date]
        for k, v in opts.items():
            if v is not None:
                args += ["--" + k.replace("_", "-"), str(v)]
        return self._run(args)

    @staticmethod
    def items(resp: dict) -> list:
        return (resp.get("data") or {}).get("itemList") or []

    @staticmethod
    def ok(resp: dict) -> bool:
        return resp.get("status") == 0
