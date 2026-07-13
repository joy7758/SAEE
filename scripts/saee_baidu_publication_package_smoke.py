#!/usr/bin/env python3
"""Validate the local, publication-ready Baidu demo and article package."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "agent-interface/ecosystem/saee-baidu-publication-package.v1.json"
SITE_ROOT = ROOT / "sites/saee-commercial"
SITE_PAGE = SITE_ROOT / "app/baidu-demos/page.tsx"
SITE_PUBLIC = SITE_ROOT / "public"
SITE_FEATURE_COMMIT = "48e669865c74c5c2f94b56cec8127d0dae25fe65"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_PUBLICATION_PACKAGE_SMOKE: FAIL " + message)


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    demos = manifest["public_demos"]
    boundary = manifest["truth_boundary"]
    require(len(demos) == 3, "demo count")
    require({item["operation"] for item in demos} == {"saee.evaluate_agent_run", "saee.evaluate_evidence"}, "operation set")
    site_names = {
        "customer-service-refund": ("agent-demo-customer-service-refund-request.json", "agent-demo-customer-service-refund-response.json"),
        "coding-agent-release": ("agent-demo-coding-agent-release-request.json", "agent-demo-coding-agent-release-response.json"),
        "evaluate-evidence": ("agent-demo-evaluate-evidence-request.json", "agent-demo-evaluate-evidence-response.json"),
    }
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
        site_request_name, site_response_name = site_names[item["demo_id"]]
        site_request = SITE_PUBLIC / site_request_name
        site_response = SITE_PUBLIC / site_response_name
        require(site_request.is_file() and site_response.is_file(), f"missing site demo assets {item['demo_id']}")
        require(json.loads(site_request.read_text(encoding="utf-8")) == json.loads(request.read_text(encoding="utf-8")), f"site request drift {item['demo_id']}")
        require(json.loads(site_response.read_text(encoding="utf-8")) == result, f"site response drift {item['demo_id']}")
    readme = (ROOT / manifest["human_entrypoint"]).read_text(encoding="utf-8")
    article = (ROOT / manifest["technical_article"]).read_text(encoding="utf-8")
    for marker in ("synthetic_data_only=true", "public_demos_published=false", "production_ready=false"):
        require(marker in readme, f"README boundary {marker}")
    for marker in ("qianfan_real_provider_product_roundtrip=true", "official_qianfan_integration=false", "production_ready=false"):
        require(marker in article, f"article boundary {marker}")
    require(boundary["public_demo_count"] == 3, "manifest demo count")
    require(SITE_PAGE.is_file(), "site demo page")
    site_page = SITE_PAGE.read_text(encoding="utf-8")
    for marker in ("/data/index.html?file=", "public_demos_published=false", "不代表百度官方认证"):
        require(marker in site_page or marker in (SITE_PUBLIC / "llms.txt").read_text(encoding="utf-8"), f"site boundary {marker}")
    require(json.loads((SITE_PUBLIC / "agent-baidu-publication-package.json").read_text(encoding="utf-8")) == manifest, "site publication manifest drift")
    ancestry = subprocess.run(
        ["git", "merge-base", "--is-ancestor", SITE_FEATURE_COMMIT, "HEAD"],
        cwd=SITE_ROOT,
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    require(ancestry.returncode == 0, "site feature commit ancestry")
    for key in ("public_demos_published", "technical_article_published", "github_release_created", "official_qianfan_integration", "marketplace_submission", "marketplace_listed", "customer_validated", "production_ready"):
        require(boundary[key] is False, key)
    print(
        "SAEE_BAIDU_PUBLICATION_PACKAGE_SMOKE: PASS demos=3 site_source_ready=true "
        "site_machine_assets=6 article_draft=true public_demos_published=false technical_article_published=false "
        "marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
