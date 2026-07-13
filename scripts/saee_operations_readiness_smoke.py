#!/usr/bin/env python3
"""Smoke check for SAEE Operations Readiness v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.operations_readiness import evaluate_operations_readiness


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_OPERATIONS_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_OPERATIONS_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_operations_readiness(load_settings({}))
    require(local["operations_readiness_type"] == "public_shell_operations_readiness", "wrong readiness type")
    require(local["public_use_required"] is False, "local environment must not require public operations")
    require(local["status"] == "hold", "local operations readiness must hold")
    require(local["operations_readiness_available"] is True, "operations readiness must be available")
    require(local["local_operations_telemetry_available"] is True, "local telemetry must be available")
    require(local["operations_telemetry_external_export_available"] is False, "external telemetry export false")
    require(local["local_alert_policy_available"] is True, "local alert policy must be available")
    require(local["external_alert_delivery_available"] is False, "external alert delivery false")
    require(local["production_monitoring_available"] is False, "production monitoring must remain false")
    require(local["alerting_available"] is False, "alerting must remain false")
    require(local["incident_response_runbook_available"] is True, "incident response runbook must be available")
    require(local["privacy_security_review_v0_1"] is True, "privacy/security review readiness must be available")
    require(local["privacy_security_review_status"] == "hold", "privacy/security review must hold")
    require(local["data_classification_available"] is True, "data classification must be available")
    require(local["personal_data_allowed"] is False, "personal data must remain false")
    require(
        local["formal_security_review_completed"] is False,
        "formal security review must remain false",
    )
    require(local["privacy_legal_review_completed"] is False, "privacy legal review false")
    require(local["security_certification_available"] is False, "security certification false")
    require(local["production_security_ready"] is False, "production security must remain false")
    require(local["support_readiness_v0_1"] is True, "support readiness must be available")
    require(local["support_runbook_available"] is True, "support runbook must be available")
    require(local["support_case_template_available"] is True, "support case template must be available")
    require(local["support_sla_draft_available"] is True, "support SLA draft must be available")
    require(local["support_contact_configured"] is False, "support contact must remain false")
    require(local["customer_support_available"] is False, "customer support must remain false")
    require(local["production_support_available"] is False, "production support must remain false")
    require(local["on_call_rotation_available"] is False, "on-call must remain false")
    require(local["sla_available"] is False, "SLA must remain false")
    require(local["support_process_available"] is False, "support process must remain false")
    require(local["production_operations_ready"] is False, "production operations must remain false")
    require(local["production_ready"] is False, "production ready must remain false")
    require(local["private_core_exposed"] is False, "private core exposed must remain false")
    require(local["external_calls_made"] is False, "operations readiness must not call external services")
    require(
        finding(local, "production_monitoring_missing")["passed"] is False,
        "production monitoring missing finding must fail",
    )
    require(
        finding(local, "incident_response_runbook_available")["passed"] is True,
        "incident response runbook finding must pass",
    )
    require(
        finding(local, "local_alert_policy_available")["passed"] is True,
        "local alert policy finding must pass",
    )
    require(
        finding(local, "support_runbook_available")["passed"] is True,
        "support runbook finding must pass",
    )
    require(
        finding(local, "privacy_security_review_available")["passed"] is True,
        "privacy/security review finding must pass",
    )
    require(
        finding(local, "incident_response_operations_missing")["passed"] is False,
        "incident response operations missing finding must fail",
    )

    preview = evaluate_operations_readiness(
        load_settings(
            {
                "SAEE_ENV": "preview",
                "SAEE_REQUIRE_API_KEY": "true",
                "SAEE_API_KEY": "local-preview-key",
            }
        )
    )
    require(preview["public_use_required"] is True, "preview must require operations review")
    require(preview["status"] == "hold", "preview operations readiness must hold")
    require(preview["production_operations_ready"] is False, "preview must not claim production operations")

    readiness_payload = load_settings({}).readiness_payload()
    require(readiness_payload["operations_readiness_available"] is True, "ready payload missing operations")
    require(readiness_payload["local_operations_telemetry_available"] is True, "ready payload missing telemetry")
    require(
        readiness_payload["operations_telemetry_external_export_available"] is False,
        "ready payload telemetry export false",
    )
    require(readiness_payload["local_alert_policy_available"] is True, "ready payload alert policy true")
    require(
        readiness_payload["external_alert_delivery_available"] is False,
        "ready payload external alert delivery false",
    )
    require(readiness_payload["support_readiness_v0_1"] is True, "ready payload support readiness true")
    require(
        readiness_payload["privacy_security_review_v0_1"] is True,
        "ready payload privacy/security readiness true",
    )
    require(
        readiness_payload["privacy_security_review_status"] == "hold",
        "ready payload privacy/security hold",
    )
    require(
        readiness_payload["formal_security_review_completed"] is False,
        "ready payload formal security review false",
    )
    require(
        readiness_payload["privacy_legal_review_completed"] is False,
        "ready payload privacy legal review false",
    )
    require(
        readiness_payload["production_security_ready"] is False,
        "ready payload production security false",
    )
    require(readiness_payload["support_runbook_available"] is True, "ready payload support runbook true")
    require(readiness_payload["support_contact_configured"] is False, "ready payload support contact false")
    require(readiness_payload["customer_support_available"] is False, "ready payload customer support false")
    require(readiness_payload["production_support_available"] is False, "ready payload production support false")
    require(readiness_payload["operations_readiness_status"] == "hold", "ready payload must hold")
    require(readiness_payload["production_operations_ready"] is False, "ready payload must not claim ops ready")
    require(readiness_payload["production_monitoring_available"] is False, "ready payload monitoring false")

    doc = (ROOT / "phase_b_product/commercial_readiness/OPERATIONS_READINESS_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_OPERATIONS_READINESS_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("operations_readiness_v0_1: true" in doc, "operations doc missing state")
    require("local_operations_telemetry_available: true" in doc, "operations doc missing telemetry")
    require("operations_telemetry_external_export_available: false" in doc, "operations doc export false")
    require("local_alert_policy_available: true" in doc, "operations doc missing alert policy")
    require("external_alert_delivery_available: false" in doc, "operations doc alert delivery false")
    require("support_readiness_v0_1: true" in doc, "operations doc support readiness true")
    require("privacy_security_review_v0_1: true" in doc, "operations doc privacy/security readiness true")
    require("formal_security_review_completed: false" in doc, "operations doc formal review false")
    require("privacy_legal_review_completed: false" in doc, "operations doc privacy review false")
    require("production_security_ready: false" in doc, "operations doc production security false")
    require("support_contact_configured: false" in doc, "operations doc support contact false")
    require("customer_support_available: false" in doc, "operations doc customer support false")
    require("production_monitoring_available: false" in doc, "operations doc must keep monitoring false")
    require("incident_response_runbook_available: true" in doc, "operations doc must expose runbook")
    require("production_operations_ready: false" in doc, "operations doc must keep production ops false")
    require("answer: conditional" in gate, "operations gate must remain conditional")
    require("recommend_public_launch_now: false" in gate, "operations gate must not recommend launch")

    print(
        "SAEE_OPERATIONS_READINESS_SMOKE: PASS "
        "status=hold "
        "local_alert_policy_available=true "
        "external_alert_delivery_available=false "
        "support_contact_configured=false "
        "customer_support_available=false "
        "production_monitoring_available=false "
        "alerting_available=false "
        "incident_response_runbook_available=true "
        "production_operations_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
