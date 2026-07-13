#!/usr/bin/env python3
"""Smoke check for SAEE Production Support Evidence Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_support_evidence import (
    evaluate_production_support_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_SUPPORT_EVIDENCE_SMOKE: FAIL: {message}")


def write_support_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "support_evidence_type": "production_support_sla_evidence",
        "customer_facing_support_contact_configured": True,
        "support_contact_owner_named": True,
        "abuse_handling_path_defined": True,
        "customer_notice_route_defined": True,
        "support_contact_test_recorded": True,
        "staffed_support_process_defined": True,
        "case_triage_workflow_defined": True,
        "support_case_audit_trail_available": True,
        "handoff_to_engineering_defined": True,
        "customer_communication_template_approved": True,
        "support_process_dry_run_recorded": True,
        "human_approved_sla_terms": True,
        "severity_definitions_approved": True,
        "support_hours_approved": True,
        "response_targets_approved": True,
        "exclusions_approved": True,
        "legal_review_completed": True,
        "on_call_rotation_defined": True,
        "escalation_schedule_defined": True,
        "incident_commander_named": True,
        "production_ready": unsafe,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_support_evidence(load_settings({}))
    require(
        local["production_support_evidence_type"]
        == "production_support_sla_evidence_readiness",
        "wrong evidence type",
    )
    require(local["production_support_evidence_readiness_v0_1"] is True, "readiness flag")
    require(local["status"] == "hold", "default evidence status must hold")
    require(local["support_evidence_path_configured"] is False, "default path false")
    require(local["customer_support_available"] is False, "default customer support false")
    require(local["production_support_available"] is False, "default production support false")
    require(local["support_process_available"] is False, "default support process false")
    require(local["sla_available"] is False, "default SLA false")
    require(local["on_call_rotation_available"] is False, "default on-call false")
    require(local["production_ready"] is False, "default production false")
    require(local["customer_validated"] is False, "default customer validation false")
    require(local["product_launched"] is False, "default launch false")
    require(local["private_core_exposed"] is False, "default private core false")
    require(local["external_calls_made"] is False, "default external calls false")
    require(local["customer_contacted"] is False, "default customer contacted false")
    require(local["support_vendor_contacted"] is False, "default support vendor false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "SUPPORT_EVIDENCE.json"
        write_support_evidence(evidence_path)
        settings = load_settings(
            {
                "SAEE_SUPPORT_CONTACT": "support@example.invalid",
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(evidence_path),
            }
        )
        configured = evaluate_production_support_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_SUPPORT_EVIDENCE.json"
        write_support_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_support_evidence(
            load_settings(
                {
                    "SAEE_SUPPORT_CONTACT": "support@example.invalid",
                    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(unsafe_path),
                }
            )
        )

    require(configured["status"] == "pass", "complete support evidence should pass")
    require(configured["support_contact_available"] is True, "support contact evidence true")
    require(configured["customer_support_available"] is True, "customer support evidence true")
    require(configured["production_support_available"] is True, "production support evidence true")
    require(configured["support_process_available"] is True, "support process evidence true")
    require(configured["sla_available"] is True, "SLA evidence true")
    require(configured["on_call_rotation_available"] is True, "on-call evidence true")
    require(configured["production_ready"] is False, "evidence pass must not claim production")
    require(configured["customer_validated"] is False, "evidence pass must not claim customers")
    require(configured["product_launched"] is False, "evidence pass must not claim launch")
    require(configured["external_calls_made"] is False, "evidence pass must not call external")
    require(configured["customer_contacted"] is False, "evidence pass must not contact customers")
    require(configured["support_vendor_contacted"] is False, "evidence pass must not contact vendors")

    blocked = blocker_ids(go_no_go)
    for blocker in ["support_contact", "customer_support", "sla", "on_call_rotation"]:
        require(blocker not in blocked, f"{blocker} should be satisfied by support evidence")
    require(go_no_go["commercial_status"] == "hold", "support evidence alone must not launch")
    require(go_no_go["production_launch_status"] == "hold", "production launch must still hold")
    require(go_no_go["production_ready"] is False, "go/no-go must keep production false")
    require(go_no_go["customer_validated"] is False, "go/no-go must keep customer validation false")
    require(go_no_go["product_launched"] is False, "go/no-go must keep launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go must keep private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require("production_ready" in unsafe["boundary_violations"], "unsafe evidence must detect boundary")
    require(unsafe["production_ready"] is False, "unsafe output must still preserve production false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_SUPPORT_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    for token in [
        "production_support_evidence_readiness_v0_1: true",
        "default_status: hold",
        "production_support_available_default: false",
        "customer_support_available_default: false",
        "sla_available_default: false",
        "on_call_rotation_available_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "support_vendor_contacted: false",
        "answer: conditional",
        "recommend_for_production_launch: false",
    ]:
        require(token in doc or token in gate, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_SUPPORT_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_support_evidence.py",
        "/scripts/saee_production_support_evidence_readiness.py",
        "/scripts/saee_production_support_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_support_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_support_evidence_readiness_hold",
        "production_support_evidence_readiness_v0_1": True,
        "production_support_available_default": False,
        "customer_support_available_default": False,
        "sla_available_default": False,
        "on_call_rotation_available_default": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_SUPPORT_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "support_blockers_satisfied_by_evidence=true production_launch_status=hold "
        "production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
