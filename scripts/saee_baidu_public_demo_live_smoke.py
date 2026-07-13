#!/usr/bin/env python3
"""Read-only live validation for the public Baidu demo site and JSON assets."""

from __future__ import annotations

import json
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://redcrag.cn"
JSON_ENDPOINTS = {
    "/agent-baidu-publication-package.json": ROOT / "agent-interface/ecosystem/saee-baidu-publication-package.v1.json",
    "/agent-demo-customer-service-refund-request.json": ROOT / "cloud-entry-package/demo/customer-service-refund/request.json",
    "/agent-demo-customer-service-refund-response.json": ROOT / "cloud-entry-package/demo/customer-service-refund/response.json",
    "/agent-demo-coding-agent-release-request.json": ROOT / "cloud-entry-package/demo/coding-agent-release/request.json",
    "/agent-demo-coding-agent-release-response.json": ROOT / "cloud-entry-package/demo/coding-agent-release/response.json",
    "/agent-demo-evaluate-evidence-request.json": ROOT / "cloud-entry-package/demo/evaluate-evidence/request.json",
    "/agent-demo-evaluate-evidence-response.json": ROOT / "cloud-entry-package/demo/evaluate-evidence/response.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_PUBLIC_DEMO_LIVE_SMOKE: FAIL " + message)


def fetch(path: str) -> tuple[int, bytes, str]:
    last_error = "unknown"
    for attempt in range(4):
        try:
            request = Request(BASE_URL + path, headers={"User-Agent": "SAEE-public-demo-live-smoke/1.0"})
            with urlopen(request, timeout=20) as response:
                return response.status, response.read(), response.headers.get("content-type", "")
        except (URLError, OSError) as exc:
            last_error = str(exc)
            if attempt < 3:
                time.sleep(0.5 * (attempt + 1))
    raise SystemExit(f"SAEE_BAIDU_PUBLIC_DEMO_LIVE_SMOKE: FAIL fetch {path}: {last_error}")


def main() -> None:
    status, page_body, page_type = fetch("/baidu-demos")
    page = page_body.decode("utf-8")
    require(status == 200 and "text/html" in page_type, "demo page response")
    for marker in ("三个可复核的合成演示", "分数是证据覆盖率", "不代表百度官方认证"):
        require(marker in page, f"demo page marker {marker}")

    status, home_body, _ = fetch("/")
    require(status == 200 and 'href="/baidu-demos"' in home_body.decode("utf-8"), "homepage discovery")

    for endpoint, local_path in JSON_ENDPOINTS.items():
        status, body, content_type = fetch(endpoint)
        require(status == 200, f"status {endpoint}")
        require("json" in content_type, f"content type {endpoint}")
        require(json.loads(body) == json.loads(local_path.read_text(encoding="utf-8")), f"content drift {endpoint}")

    viewer_path = "/data/index.html?file=agent-demo-customer-service-refund-request.json"
    status, viewer_body, viewer_type = fetch(viewer_path)
    viewer = viewer_body.decode("utf-8")
    require(status == 200 and "text/html" in viewer_type, "viewer response")
    require("技术资料阅读页" in viewer and "data-viewer.js" in viewer, "viewer contract")

    print(
        "SAEE_BAIDU_PUBLIC_DEMO_LIVE_SMOKE: PASS "
        "public_page=200 homepage_discovery=true json_assets=7 viewer=200 "
        "live_content_matches_local=true public_site_demos_accessible=true "
        "qianfan_community_published=false github_release_created=false production_ready=false"
    )


if __name__ == "__main__":
    main()
