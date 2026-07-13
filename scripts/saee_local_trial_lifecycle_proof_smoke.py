#!/usr/bin/env python3
"""Smoke check for the SAEE local trial lifecycle proof artifact."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.local.json"
REPORT = ROOT / "phase_b_product/validation/local_trial_lifecycle_proof/local_trial_lifecycle_proof.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_LIFECYCLE_PROOF_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_LIFECYCLE_PROOF_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_local_trial_lifecycle_proof.py"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_LOCAL_TRIAL_LIFECYCLE_PROOF_SMOKE: FAIL: {message}")


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

    expected_values = {
        "local_trial_lifecycle_proof_v0_1": True,
        "proof_type": "local_trial_session_start_status_stop",
        "status": "pass",
        "lifecycle_passed": True,
        "make_try_local_equivalent_checked": True,
        "pre_stop_attempted": True,
        "pre_stop_ok": True,
        "start_session_state": "running",
        "running_session_state": "running",
        "stop_session_state": "stopped",
        "final_session_state": "not_running",
        "running_backend_health_ok": True,
        "running_landing_page_ok": True,
        "detached_local_child_processes": True,
        "start_detached_local_child_processes": True,
        "running_detached_local_child_processes": True,
        "final_backend_pid_running": False,
        "final_landing_pid_running": False,
        "blockers_closed_by_lifecycle_proof": 0,
        "human_review_required": True,
        "server_started_by_script": True,
        "server_stopped_by_script": True,
        "temporary_localhost_server_only": True,
    }
    for key, expected in expected_values.items():
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

    for key in [
        "pre_stop_snapshot",
        "start_snapshot",
        "running_snapshot",
        "stop_snapshot",
        "final_snapshot",
    ]:
        if not isinstance(payload.get(key), dict):
            fail(f"{key} must be an object")

    report = REPORT.read_text(encoding="utf-8")
    for token in [
        "local_trial_lifecycle_proof_v0_1: true",
        "lifecycle_passed: true",
        "pre_stop_attempted: true",
        "detached_local_child_processes: true",
        "start_detached_local_child_processes: true",
        "running_detached_local_child_processes: true",
        "final_session_state: not_running",
        "production_ready: false",
        "customer_validated: false",
        "external_calls_made: false",
        "browser_opened_by_script: false",
        "dependencies_installed_by_script: false",
        "blockers_closed_by_lifecycle_proof: 0",
    ]:
        if token not in report:
            fail(f"report missing token: {token}")

    runner = RUNNER.read_text(encoding="utf-8")
    for forbidden in [
        "webbrowser.open",
        "pip install",
        "requests.",
        "https://",
    ]:
        if forbidden in runner:
            fail(f"runner contains forbidden token: {forbidden}")

    print(
        "SAEE_LOCAL_TRIAL_LIFECYCLE_PROOF_SMOKE: PASS "
        f"status={payload['status']} "
        f"lifecycle_passed={str(payload['lifecycle_passed']).lower()} "
        f"final_session_state={payload['final_session_state']} "
        "external_calls_made=false production_ready=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
