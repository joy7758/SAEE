#!/usr/bin/env python3
"""Smoke check for SAEE Pilot Customer Validation Readiness v0.1."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.pilot_validation_readiness import (
    evaluate_pilot_validation_readiness,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PILOT_VALIDATION_READINESS_SMOKE: FAIL: {message}")


def finding(report: dict[str, object], check_id: str) -> dict[str, object]:
    for item in report["findings"]:
        if item["check_id"] == check_id:
            return item
    raise SystemExit(f"SAEE_PILOT_VALIDATION_READINESS_SMOKE: FAIL: missing finding {check_id}")


def main() -> None:
    local = evaluate_pilot_validation_readiness(load_settings({}))
    require(
        local["pilot_validation_readiness_type"] == "controlled_pilot_validation_readiness",
        "wrong readiness type",
    )
    require(local["pilot_validation_readiness_v0_1"] is True, "readiness must be true")
    require(local["pilot_validation_status"] == "hold", "pilot validation must hold")
    require(local["first_user_test_plan_available"] is True, "test plan must be available")
    require(local["feedback_form_available"] is True, "feedback form must be available")
    require(local["success_criteria_available"] is True, "success criteria must be available")
    require(local["pilot_result_template_available"] is True, "result template must be available")
    require(local["pilot_session_protocol_available"] is True, "session protocol must be available")
    require(local["pilot_sessions_completed"] == 0, "pilot sessions must be zero")
    require(local["pilot_results_recorded"] is False, "pilot results must be false")
    require(local["customer_permission_recorded"] is False, "customer permission must be false")
    require(local["customer_contacted"] is False, "customer contact must be false")
    require(local["customer_validated"] is False, "customer validated must remain false")
    require(local["product_market_fit_claimed"] is False, "PMF claim must be false")
    require(local["revenue_validated"] is False, "revenue validation must be false")
    require(local["production_readiness_claimed"] is False, "production readiness claim false")
    require(local["user_upload_enabled"] is False, "user upload must be false")
    require(local["customer_data_processing_ready"] is False, "customer data processing false")
    require(local["product_launched"] is False, "product launch false")
    require(local["production_ready"] is False, "production ready false")
    require(local["private_core_exposed"] is False, "private core false")
    require(local["api_schema_modified"] is False, "API schema false")
    require(local["runtime_modified"] is False, "runtime false")
    require(local["kernel_modified"] is False, "kernel false")
    require(local["external_calls_made"] is False, "external calls false")
    require(finding(local, "pilot_sessions_missing")["passed"] is False, "pilot missing blocks")
    require(
        finding(local, "customer_permission_missing")["passed"] is False,
        "customer permission missing blocks",
    )

    payload = load_settings({}).readiness_payload()
    require(payload["pilot_validation_readiness_v0_1"] is True, "ready payload readiness")
    require(payload["pilot_validation_status"] == "hold", "ready payload hold")
    require(payload["pilot_sessions_completed"] == 0, "ready payload sessions zero")
    require(payload["pilot_results_recorded"] is False, "ready payload results false")
    require(payload["customer_validated"] is False, "ready payload customer validated false")
    require(payload["customer_contacted"] is False, "ready payload customer contacted false")
    require(payload["user_upload_enabled"] is False, "ready payload upload false")

    doc = (
        ROOT / "phase_b_product/commercial_readiness/PILOT_CUSTOMER_VALIDATION_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT / "docs/strategy/SAEE_PILOT_CUSTOMER_VALIDATION_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    template = json.loads((ROOT / "phase_b_product/validation/PILOT_RESULT_TEMPLATE.json").read_text())
    require("pilot_validation_readiness_v0_1: true" in doc, "doc missing state")
    require("pilot_sessions_completed: 0" in doc, "doc missing zero sessions")
    require("customer_validated: false" in doc, "doc customer validation false")
    require("customer_contacted: false" in doc, "doc customer contact false")
    require("user_upload_enabled: false" in doc, "doc upload false")
    require("answer: conditional" in gate, "gate conditional")
    require("recommend_public_launch_now: false" in gate, "gate no launch")
    require(template["pilot_result_template_v0_1"] is True, "template marker true")
    require(template["customer_validated"] is False, "template customer validation false")
    require(template["sessions"][0]["boundary_flags"]["private_core_disclosed"] is False, "template private core false")

    print(
        "SAEE_PILOT_VALIDATION_READINESS_SMOKE: PASS "
        "pilot_validation_readiness_v0_1=true "
        "pilot_sessions_completed=0 "
        "customer_validated=false "
        "customer_contacted=false "
        "user_upload_enabled=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
