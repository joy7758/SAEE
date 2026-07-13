#!/usr/bin/env python3
"""Smoke check for SAEE Support Readiness v0.1."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.support_readiness import evaluate_support_readiness


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_SUPPORT_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_SUPPORT_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_support_readiness(load_settings({}))
    require(local["support_readiness_type"] == "controlled_preview_support_readiness", "wrong type")
    require(local["support_readiness_v0_1"] is True, "support readiness must be true")
    require(local["status"] == "hold", "support readiness must hold")
    require(local["support_runbook_available"] is True, "support runbook must be available")
    require(local["support_case_template_available"] is True, "case template must be available")
    require(local["support_sla_draft_available"] is True, "SLA draft must be available")
    require(local["support_response_targets_documented"] is True, "response targets must be documented")
    require(local["support_contact_configured"] is False, "support contact must remain false")
    require(local["customer_support_available"] is False, "customer support must remain false")
    require(local["production_support_available"] is False, "production support must remain false")
    require(local["support_process_available"] is False, "support process must remain false")
    require(local["sla_available"] is False, "SLA must remain false")
    require(local["on_call_rotation_available"] is False, "on-call must remain false")
    require(local["production_operations_ready"] is False, "production operations must remain false")
    require(local["production_ready"] is False, "production ready must remain false")
    require(local["customer_validated"] is False, "customer validation must remain false")
    require(local["product_launched"] is False, "product launch must remain false")
    require(local["private_core_exposed"] is False, "private core exposed must remain false")
    require(local["api_schema_modified"] is False, "API schema must not be modified")
    require(local["runtime_modified"] is False, "runtime must not be modified")
    require(local["kernel_modified"] is False, "kernel must not be modified")
    require(local["external_calls_made"] is False, "external calls must be false")
    require(local["customer_contacted"] is False, "customer contact must be false")
    require(finding(local, "support_runbook_available")["passed"] is True, "runbook finding must pass")
    require(finding(local, "support_contact_missing")["passed"] is False, "support contact must block")
    require(finding(local, "production_sla_missing")["passed"] is False, "production SLA must block")

    configured_preview = evaluate_support_readiness(
        load_settings({"SAEE_ENV": "preview", "SAEE_SUPPORT_CONTACT": "support@example.invalid"})
    )
    require(
        configured_preview["support_contact_configured"] is True,
        "configured preview must report support contact configured",
    )
    require(
        finding(configured_preview, "support_contact_missing")["passed"] is True,
        "configured preview support contact finding must pass",
    )
    require(configured_preview["status"] == "hold", "configured preview must still hold without SLA")
    require(
        configured_preview["customer_support_available"] is False,
        "configured preview must not claim customer support",
    )
    require(
        configured_preview["production_support_available"] is False,
        "configured preview must not claim production support",
    )
    require(configured_preview["sla_available"] is False, "configured preview must not claim SLA")
    require(
        configured_preview["production_operations_ready"] is False,
        "configured preview must not claim production operations",
    )

    payload = load_settings({}).readiness_payload()
    require(payload["support_readiness_v0_1"] is True, "ready payload support readiness true")
    require(payload["support_runbook_available"] is True, "ready payload support runbook true")
    require(payload["support_sla_draft_available"] is True, "ready payload SLA draft true")
    require(payload["support_contact_configured"] is False, "ready payload support contact false")
    require(payload["customer_support_available"] is False, "ready payload customer support false")
    require(payload["production_support_available"] is False, "ready payload production support false")
    require(payload["support_process_available"] is False, "ready payload support process false")
    require(payload["sla_available"] is False, "ready payload SLA false")

    doc = (ROOT / "phase_b_product/commercial_readiness/PREVIEW_SUPPORT_PROCESS_V0_1.md").read_text(
        encoding="utf-8"
    )
    gate = (ROOT / "docs/strategy/SAEE_PREVIEW_SUPPORT_PROCESS_RECOMMENDATION_GATE.md").read_text(
        encoding="utf-8"
    )
    require("support_readiness_v0_1: true" in doc, "support doc missing state")
    require("support_runbook_available: true" in doc, "support doc missing runbook")
    require("support_contact_configured: false" in doc, "support doc contact false")
    require("customer_support_available: false" in doc, "support doc customer support false")
    require("production_support_available: false" in doc, "support doc production support false")
    require("support_process_available: false" in doc, "support doc process false")
    require("sla_available: false" in doc, "support doc SLA false")
    require("answer: conditional" in gate, "support gate conditional")
    require("recommend_public_launch_now: false" in gate, "support gate no launch")

    print(
        "SAEE_SUPPORT_READINESS_SMOKE: PASS "
        "support_runbook_available=true "
        "local_support_contact_configured=false "
        "configured_preview_support_contact_configured=true "
        "customer_support_available=false "
        "production_support_available=false "
        "sla_available=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
