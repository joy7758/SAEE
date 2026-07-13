#!/usr/bin/env python3
"""Smoke check for SAEE Production Support / SLA Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_SUPPORT_SLA_REQUIREMENTS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_SUPPORT_SLA_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_support_sla_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")
    require(data["production_support_sla_implemented"] is False, "support/SLA not implemented")
    require(data["support_contact_available"] is False, "support contact false")
    require(data["customer_support_available"] is False, "customer support false")
    require(data["production_support_available"] is False, "production support false")
    require(data["support_process_available"] is False, "support process false")
    require(data["sla_available"] is False, "SLA false")
    require(data["on_call_rotation_available"] is False, "on-call false")
    require(data["production_operations_ready"] is False, "production operations false")
    require(data["production_ready"] is False, "production ready false")
    require(data["customer_validated"] is False, "customer validation false")
    require(data["product_launched"] is False, "product launch false")
    require(data["private_core_exposed"] is False, "private core false")
    require(data["task_candidates_executed"] is False, "tasks not executed")
    require(data["development_permission_granted"] is False, "development permission false")
    require(data["runtime_modified"] is False, "runtime false")
    require(data["backend_modified"] is False, "backend false")
    require(data["kernel_modified"] is False, "kernel false")
    require(data["api_schema_modified"] is False, "API schema false")
    require(data["external_calls_made"] is False, "external calls false")
    require(data["customer_contacted"] is False, "customer contact false")
    require(data["support_vendor_contacted"] is False, "support vendor false")

    blockers = set(data["support_blockers_covered_as_requirements"])
    require(blockers == {"sla", "support_contact", "customer_support"}, "support blockers mismatch")

    channels = set(data["required_support_channels"])
    for channel in [
        "customer_support_email_or_ticket_queue",
        "security_contact_route",
        "billing_contact_route",
        "incident_escalation_route",
        "customer_notice_route",
    ]:
        require(channel in channels, f"missing support channel {channel}")

    roles = set(data["required_support_roles"])
    for role in [
        "support_owner",
        "triage_owner",
        "incident_commander",
        "technical_responder",
        "customer_communications_owner",
        "billing_support_owner",
    ]:
        require(role in roles, f"missing support role {role}")

    terms = set(data["required_sla_terms"])
    for term in [
        "support_hours",
        "severity_definitions",
        "initial_response_targets",
        "update_cadence",
        "exclusions",
        "maintenance_window_policy",
        "credit_or_remedy_policy",
        "termination_and_refund_escalation",
    ]:
        require(term in terms, f"missing SLA term {term}")

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match support blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_support_sla_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_support_sla_implemented: false",
        "support_contact_available: false",
        "customer_support_available: false",
        "production_support_available: false",
        "support_process_available: false",
        "sla_available: false",
        "on_call_rotation_available: false",
        "production_operations_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "task_candidates_executed: false",
        "development_permission_granted: false",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "api_schema_modified: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "support_vendor_contacted: false",
        "answer: conditional",
        "recommend_for_production_support_implementation: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_SUPPORT_SLA_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_support_sla_requirements.py",
        "/scripts/saee_production_support_sla_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_support_sla_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_support_sla_requirements_v0_1": True,
        "production_support_sla_implemented": False,
        "support_contact_available": False,
        "customer_support_available": False,
        "production_support_available": False,
        "support_process_available": False,
        "sla_available": False,
        "on_call_rotation_available": False,
        "production_operations_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_SUPPORT_SLA_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true production_support_available=false "
        "customer_support_available=false sla_available=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
