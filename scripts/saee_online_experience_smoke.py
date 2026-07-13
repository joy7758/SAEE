#!/usr/bin/env python3
"""Smoke check for the static SAEE online experience page.

The online experience is a read-only sample-data preview. It must not upload
user data, call backend services, call external services, run SAEE runtime, or
claim production readiness.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ONLINE_HTML = ROOT / "phase_b_product/landing/online-experience.html"
INDEX_HTML = ROOT / "phase_b_product/landing/index.html"
CSS_PATH = ROOT / "phase_b_product/landing/styles.css"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_ONLINE_EXPERIENCE_SMOKE: FAIL: {message}")


def require_file(path: Path) -> str:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def require_tokens(name: str, text: str, tokens: list[str]) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        fail(f"{name} missing tokens: {', '.join(missing)}")


def reject_tokens(name: str, text: str, tokens: list[str]) -> None:
    found = [token for token in tokens if token in text]
    if found:
        fail(f"{name} contains forbidden tokens: {', '.join(found)}")


def main() -> None:
    online = require_file(ONLINE_HTML)
    index = require_file(INDEX_HTML)
    css = require_file(CSS_PATH)
    llms = require_file(LLMS)
    agent_index = json.loads(require_file(AGENT_INDEX))

    require_tokens(
        "online-experience.html",
        online,
        [
            "SAEE 线上体验版",
            "样例数据演示",
            "不用安装，也能先看懂 SAEE 怎么帮你选 AI。",
            "不上传你的资料",
            "不连接后端",
            "不是正式上线版",
            "本页面只使用样例数据，不上传你的数据。",
            "本页面不连接后端，不执行 SAEE 运行时。",
            "本页面不代表生产可用，不代表客户验证已完成。",
            "查看样例结果",
            "方案 B：最稳",
            "推荐继续试用",
            "查看本地试用方式",
        ],
    )
    reject_tokens(
        "online-experience.html",
        online,
        [
            "<form",
            "type=\"file\"",
            "fetch(",
            "XMLHttpRequest",
            "WebSocket",
            "navigator.sendBeacon",
            "http://",
            "https://",
            "mailto:",
            "生产可用产品",
            "客户已验证",
            "正式上线版</title>",
            "saee_v1_0",
            "selection_engine",
            "mutation_engine",
            "lineage_engine",
            "fitness_engine",
        ],
    )
    require_tokens(
        "index.html",
        index,
        [
            "online-experience.html",
            "线上体验",
            "先看线上体验",
            "线上体验版只用样例数据，不上传你的资料，不代表正式上线。",
            "styles.css?v=linklings-reference-cn-v25-20260709",
        ],
    )
    require_tokens(
        "styles.css",
        css,
        [
            "--palette-name: linklings-reference-cn-v25;",
            ".experience-page",
            ".experience-hero",
            ".experience-window",
            ".experience-demo-grid",
            ".experience-boundary",
            "@keyframes experience-board-float",
        ],
    )
    require_tokens(
        "llms.txt",
        llms,
        [
            "/phase_b_product/landing/online-experience.html",
            "/scripts/saee_online_experience_smoke.py",
        ],
    )
    entry = agent_index.get("online_experience_static_preview_v0_1", {})
    expected = {
        "status": "static_preview_ready",
        "sample_data_only": True,
        "user_upload_enabled": False,
        "backend_call_required": False,
        "runtime_modified": False,
        "backend_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
    }
    for key, value in expected.items():
        if entry.get(key) != value:
            fail(f"agent-index online_experience_static_preview_v0_1 {key} must be {value!r}")
    print("SAEE_ONLINE_EXPERIENCE_SMOKE: PASS static_preview_ready sample_data_only=true")


if __name__ == "__main__":
    main()
