#!/usr/bin/env python3
"""Validate the local, publication-ready Baidu demo and article package."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "agent-interface/ecosystem/saee-baidu-publication-package.v1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_PUBLICATION_PACKAGE_SMOKE: FAIL " + message)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    demos = manifest["public_demos"]
    boundary = manifest["truth_boundary"]
    require(len(demos) == 3, "demo count")
    require({item["operation"] for item in demos} == {"saee.evaluate_agent_run", "saee.evaluate_evidence"}, "operation set")
    for item in demos:
        request = ROOT / item["request"]
        response = ROOT / item["response"]
        require(request.is_file() and response.is_file(), f"missing demo files {item['demo_id']}")
        json.loads(request.read_text(encoding="utf-8"))
        result = json.loads(response.read_text(encoding="utf-8"))
        if "expected_score" in item:
            require(result["score"] == item["expected_score"], f"score drift {item['demo_id']}")
            require(result["readiness"] == item["expected_readiness"], f"readiness drift {item['demo_id']}")
        else:
            require(result["evidence_quality"] == item["expected_quality"], f"quality drift {item['demo_id']}")
    readme = (ROOT / manifest["human_entrypoint"]).read_text(encoding="utf-8")
    article = (ROOT / manifest["technical_article"]).read_text(encoding="utf-8")
    for marker in ("synthetic_data_only=true", "public_demos_published=false", "production_ready=false"):
        require(marker in readme, f"README boundary {marker}")
    for marker in ("qianfan_real_provider_product_roundtrip=true", "official_qianfan_integration=false", "production_ready=false"):
        require(marker in article, f"article boundary {marker}")
    require(boundary["public_demo_count"] == 3, "manifest demo count")
    for key in ("public_demos_published", "technical_article_published", "github_release_created", "official_qianfan_integration", "marketplace_submission", "marketplace_listed", "customer_validated", "production_ready"):
        require(boundary[key] is False, key)
    print(
        "SAEE_BAIDU_PUBLICATION_PACKAGE_SMOKE: PASS demos=3 article_draft=true "
        "public_demos_published=false technical_article_published=false "
        "marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
