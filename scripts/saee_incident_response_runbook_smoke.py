#!/usr/bin/env python3
"""Smoke check for SAEE Incident Response Runbook v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_preflight import evaluate_commercial_preflight
from saee_backend.services.operations_readiness import evaluate_operations_readiness


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_INCIDENT_RESPONSE_RUNBOOK_SMOKE: FAIL: {message}")


def main() -> None:
    settings = load_settings({})
    ready = settings.readiness_payload()
    operations = evaluate_operations_readiness(settings)
    preflight = evaluate_commercial_preflight(settings)

    for report_name, report in [
        ("ready", ready),
        ("operations", operations),
        ("preflight", preflight),
    ]:
        require(
            report["incident_response_runbook_available"] is True,
            f"{report_name} must report incident response runbook availability",
        )
        require(report["production_monitoring_available"] is False, f"{report_name} monitoring false")
        require(report["alerting_available"] is False, f"{report_name} alerting false")
        require(report["on_call_rotation_available"] is False, f"{report_name} on-call false")
        require(report["sla_available"] is False, f"{report_name} SLA false")
        require(report["support_process_available"] is False, f"{report_name} support false")
        require(report["production_operations_ready"] is False, f"{report_name} operations not production ready")
        require(report["production_ready"] is False, f"{report_name} production ready false")
        require(report["customer_validated"] is False, f"{report_name} customer validation false")
        require(report["product_launched"] is False, f"{report_name} product launch false")
        require(report["private_core_exposed"] is False, f"{report_name} private core false")

    runbook = (ROOT / "phase_b_product/commercial_readiness/INCIDENT_RESPONSE_RUNBOOK_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_INCIDENT_RESPONSE_RUNBOOK_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    operations_doc = (ROOT / "phase_b_product/commercial_readiness/OPERATIONS_READINESS_V0_1.md").read_text(
        encoding="utf-8"
    )

    required_tokens = [
        "incident_response_runbook_v0_1: true",
        "incident_response_runbook_available: true",
        "automated_alerting_available: false",
        "on_call_rotation_available: false",
        "sla_available: false",
        "support_process_available: false",
        "production_operations_ready: false",
        "production_ready: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
    ]
    for token in required_tokens:
        require(token in runbook, f"runbook missing token {token}")
        require(token in gate, f"gate missing token {token}")

    require(
        "incident_response_runbook_available: true" in operations_doc,
        "operations readiness doc must expose runbook availability",
    )
    forbidden = [
        "production_operations_ready: true",
        "production_ready: true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
        "api_schema_modified: true",
        "runtime_modified: true",
        "kernel_modified: true",
        "external_calls_made: true",
    ]
    combined = "\n".join([runbook, gate, operations_doc])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claims found: " + ", ".join(found))

    print(
        "SAEE_INCIDENT_RESPONSE_RUNBOOK_SMOKE: PASS "
        "incident_response_runbook_available=true "
        "production_operations_ready=false "
        "production_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
