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
    require(plan["status"] == "phases_0_to_4_partner_consultation_submitted_public_release_withheld", "plan status")
    require(plan["public_operations_target"] == ["evaluate_agent_run", "evaluate_evidence"], "public operation target")
    require(plan["direct_marketplace_qualification"] == {
        "decision": "do_not_recommend_currently",
        "matrix_ref": "agent-interface/ecosystem/saee-baidu-marketplace-qualification-matrix.v1.json",
        "evidence_intake_ref": "agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.template.v1.json",
        "verified_criterion_count": 0,
        "criterion_count": 7,
        "public_release_allowlist_included": False,
        "release_candidate_refresh_required": True,
    }, "direct marketplace qualification")
    require(plan["public_demo_site"] == {
        "repository": "sites/saee-commercial",
        "feature_commit": "48e669865c74c5c2f94b56cec8127d0dae25fe65",
        "audited_site_head": "544479e4a59a68474a37687da8060e3cc23099e8",
        "human_entrypoint": "/baidu-demos",
        "machine_manifest": "/agent-baidu-publication-package.json",
        "machine_demo_asset_count": 6,
        "local_build_validated": True,
        "local_browser_flow_validated": True,
        "deployment_authorization_recorded_in_main_gate": False,
        "deployment_performed_by_current_change": False,
        "deployment_observed": True,
        "deployed": True,
        "live_validated": True,
    }, "public demo site source")
    require(set(plan["internal_debug_operations"]) == {"describe_saee", "compare_observed_traces"}, "debug operation classification")
    require([item["phase"] for item in plan["phases"]] == ["PHASE_0", "PHASE_1", "PHASE_2", "PHASE_3", "PHASE_4"], "phase ladder")
    require(plan["phases"][-1]["status"] == "partner_consultation_submitted_waiting_response", "phase 4 status")
    blockers = set(plan["current_blockers"])
    require("qianfan_real_provider_product_roundtrip_missing" not in blockers, "stale Qianfan blocker")
    require("external_authorization_missing" not in blockers, "stale authorization blocker")
    require({
        "public_license_tag_push_and_github_release_withheld",
        "qianfan_community_and_technical_article_publication_not_authorized",
        "baidu_partner_response_pending",
    }.issubset(blockers), "current blockers")
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
    require(boundary["public_demo_site_source_ready"] is True, "public demo source ready")
    require(boundary["public_demo_site_deployment_observed"] is True, "public demo deployment observed")
    require(boundary["public_demo_site_live_validated"] is True, "public demo live validation")
    require(boundary["public_site_demos_accessible"] is True, "public site demos accessible")
    require(boundary["public_demos_published_channel_scope"] == "github_release_or_qianfan_community", "legacy publication scope")
    require(boundary["qianfan_community_demos_published"] is False, "Qianfan community publication boundary")
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
