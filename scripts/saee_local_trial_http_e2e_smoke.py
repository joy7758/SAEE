#!/usr/bin/env python3
"""Smoke check for the SAEE local trial HTTP E2E artifact."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.local.json"
REPORT = ROOT / "phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_HTTP_E2E_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_HTTP_E2E_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_local_trial_http_e2e.py"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_LOCAL_TRIAL_HTTP_E2E_SMOKE: FAIL: {message}")


def read_json(path: Path) -> dict:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
    if not isinstance(data, dict):
        fail(f"{path.relative_to(ROOT)} must contain a JSON object")
    return data


def require_false(data: dict, key: str) -> None:
    if data.get(key) is not False:
        fail(f"{key} must be false")


def require_true(data: dict, key: str) -> None:
    if data.get(key) is not True:
        fail(f"{key} must be true")


def main() -> None:
    payload = read_json(SUMMARY)
    for path in [REPORT, TOP_DOC, GATE, RUNNER]:
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")

    required_values = {
        "local_trial_http_e2e_v0_1": True,
        "snapshot_type": "local_trial_http_e2e",
        "status": "pass",
        "http_e2e_ready": True,
        "http_e2e_passed": True,
        "expected_recommended_agent": "agent-b",
        "observed_recommended_agent": "agent-b",
        "ranking_top": "agent-b",
        "ranking_count": 3,
        "failure_modes_summary_present": True,
        "blockers_closed_by_http_e2e": 0,
        "server_started_by_script": True,
        "temporary_localhost_server_only": True,
    }
    for key, expected in required_values.items():
        if payload.get(key) != expected:
            fail(f"{key} must be {expected!r}")

    for key in [
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "customer_data_allowed",
        "paid_trial_enabled",
        "payment_provider_configured",
        "product_launched",
        "public_sdk_released",
        "external_ai_assistant_tested",
        "external_validation_claim",
        "external_calls_made",
        "external_model_api_called",
        "browser_opened_by_script",
        "dependencies_installed_by_script",
        "private_core_exposed",
        "api_schema_modified",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
    ]:
        require_false(payload, key)

    require_true(payload, "human_review_required")

    report = REPORT.read_text(encoding="utf-8")
    for token in [
        "production_ready: false",
        "customer_validated: false",
        "external_calls_made: false",
        "server_started_by_script: true",
        "temporary localhost server",
        "blockers_closed_by_http_e2e: 0",
    ]:
        if token not in report:
            fail(f"report missing token: {token}")

    runner = RUNNER.read_text(encoding="utf-8")
    for forbidden in [
        "webbrowser.open",
        "pip install",
        "requests.post",
        "https://",
    ]:
        if forbidden in runner:
            fail(f"runner contains forbidden token: {forbidden}")

    print(
        "SAEE_LOCAL_TRIAL_HTTP_E2E_SMOKE: PASS "
        f"status={payload['status']} "
        f"http_e2e_passed={str(payload['http_e2e_passed']).lower()} "
        f"observed_recommended_agent={payload['observed_recommended_agent']} "
        "external_calls_made=false "
        "production_ready=false "
        "customer_validated=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
