#!/usr/bin/env python3
"""Smoke check for SAEE Production Operations Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRODUCTION_OPERATIONS_REQUIREMENTS_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_OPERATIONS_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_operations_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")
    require(data["production_operations_implemented"] is False, "operations not implemented")
    require(data["production_monitoring_available"] is False, "production monitoring false")
    require(data["external_alert_delivery_available"] is False, "external alert delivery false")
    require(data["on_call_rotation_available"] is False, "on-call false")
    require(data["alerting_available"] is False, "alerting false")
    require(data["sla_available"] is False, "SLA false")
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
    require(data["external_alert_provider_contacted"] is False, "external alert provider false")

    blockers = set(data["operations_blockers_covered_as_requirements"])
    require(
        blockers == {"production_monitoring", "external_alert_delivery", "on_call_rotation"},
        "operations blockers mismatch",
    )
    slis = set(data["required_slis"])
    for sli in [
        "availability",
        "request_success_rate",
        "p95_latency",
        "p99_latency",
        "error_rate",
        "request_volume",
        "storage_error_rate",
        "auth_failure_rate",
        "tenant_boundary_denial_rate",
        "backup_restore_drill_age_days",
    ]:
        require(sli in slis, f"missing SLI {sli}")

    routes = set(data["required_alert_routes"])
    for route in [
        "primary_on_call",
        "secondary_on_call",
        "security_contact",
        "support_contact",
        "status_page_or_customer_notice",
        "post_incident_review_owner",
    ]:
        require(route in routes, f"missing alert route {route}")

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match operations blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_operations_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_operations_implemented: false",
        "production_monitoring_available: false",
        "external_alert_delivery_available: false",
        "on_call_rotation_available: false",
        "alerting_available: false",
        "sla_available: false",
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
        "external_alert_provider_contacted: false",
        "answer: conditional",
        "recommend_for_production_operations_implementation: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_OPERATIONS_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_OPERATIONS_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_operations_requirements.py",
        "/scripts/saee_production_operations_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_operations_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_operations_requirements_v0_1": True,
        "production_operations_implemented": False,
        "production_monitoring_available": False,
        "external_alert_delivery_available": False,
        "on_call_rotation_available": False,
        "alerting_available": False,
        "sla_available": False,
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
        "SAEE_PRODUCTION_OPERATIONS_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true production_operations_ready=false "
        "production_monitoring_available=false external_alert_delivery_available=false "
        "on_call_rotation_available=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
