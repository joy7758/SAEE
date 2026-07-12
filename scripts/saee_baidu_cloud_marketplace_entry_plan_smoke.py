#!/usr/bin/env python3
"""Validate the local-only Baidu Cloud Marketplace entry plan surfaces."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json"
GATE = ROOT / "docs/strategy/SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_RECOMMENDATION_GATE.md"
MATRIX = ROOT / "docs/ecosystem/SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_TRUTH_MATRIX.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_PLAN_SMOKE: FAIL " + message)


def main() -> None:
    plan = json.loads(PLAN.read_text(encoding="utf-8"))
    gate = GATE.read_text(encoding="utf-8")
    matrix = MATRIX.read_text(encoding="utf-8")
    require(plan["external_brand"]["name"] == "SAEE Agent Readiness Platform", "brand")
    require(plan["public_operations_target"] == ["evaluate_agent_run", "evaluate_evidence"], "public operation target")
    require(set(plan["internal_debug_operations"]) == {"describe_saee", "compare_observed_traces"}, "debug operation classification")
    require([item["phase"] for item in plan["phases"]] == ["PHASE_0", "PHASE_1", "PHASE_2", "PHASE_3", "PHASE_4"], "phase ladder")
    boundary = plan["truth_boundary"]
    for key in (
        "qianfan_product_adapter_validated",
        "cloud_entry_package_validated",
        "product_page_local_build_validated",
        "technical_whitepaper_local_validated",
        "three_minute_demo_video_local_validated",
        "release_candidate_prepared",
        "qianfan_real_provider_product_roundtrip",
        "external_action_authorized",
        "baidu_partner_contacted",
        "baidu_ecosystem_application_submitted",
    ):
        require(boundary[key] is True, key)
    for key in (
        "public_release_created",
        "github_release_created",
        "marketplace_submission",
        "marketplace_listed",
        "public_price_points_approved",
        "customer_validated",
        "production_ready",
    ):
        require(boundary[key] is False, key)
    require("answer: conditional" in gate, "conditional recommendation")
    require("audit_first_reframe=false" in gate, "audit boundary")
    require("overall_status=phases_0_to_4_partner_consultation_submitted_public_release_withheld" in matrix, "truth matrix status")
    require("marketplace_submission=false" in matrix and "production_ready=false" in matrix, "matrix false boundaries")
    print(
        "SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_PLAN_SMOKE: PASS "
        "phases=5 local_phases_complete=4 public_operations_target=2 recommendation=conditional "
        "real_qianfan_synthetic_scenarios=2 partner_consultation_submitted=true "
        "external_action_authorized=true_scope_limited "
        "marketplace_submission=false production_ready=false"
    )


if __name__ == "__main__":
    main()
