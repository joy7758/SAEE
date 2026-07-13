#!/usr/bin/env python3
"""Smoke check for the SAEE local trial cold-start preflight."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_COLD_START_PREFLIGHT_V0_1.md"
SNAPSHOT_JSON = ROOT / "phase_b_product/validation/local_trial_cold_start_preflight.local.json"
SNAPSHOT_MD = ROOT / "phase_b_product/validation/local_trial_cold_start_preflight.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_COLD_START_PREFLIGHT_RECOMMENDATION_GATE.md"
RUNNER = ROOT / "scripts/saee_local_trial_cold_start_preflight.py"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_LOCAL_TRIAL_COLD_START_PREFLIGHT_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def require_false(payload: dict, key: str) -> None:
    require(payload.get(key) is False, f"{key} must be false")


def main() -> None:
    for path in [TOP_DOC, SNAPSHOT_JSON, SNAPSHOT_MD, GATE, RUNNER]:
        require(path.exists(), f"missing required file: {path.relative_to(ROOT)}")

    payload = json.loads(SNAPSHOT_JSON.read_text(encoding="utf-8"))
    require(payload.get("local_trial_cold_start_preflight_v0_1") is True, "snapshot flag")
    require(payload.get("snapshot_type") == "local_trial_cold_start_preflight", "snapshot type")
    require(payload.get("status") in {"pass", "hold"}, "status must be pass or hold")
    require(isinstance(payload.get("cold_start_ready"), bool), "cold_start_ready boolean")
    require(payload.get("preflight_scope") == "local_mvp_cold_start_dependency_check", "scope")
    require(payload.get("local_dependency_probe_only") is True, "local dependency probe only")
    require(payload.get("human_review_required") is True, "human review required")
    require(payload.get("blockers_closed_by_cold_start_preflight") == 0, "blockers closed")
    require(isinstance(payload.get("missing_or_blocking_items"), list), "missing items list")
    require(isinstance(payload.get("required_files"), dict), "required files dict")
    require(payload.get("requirements_file") == "saee_backend/requirements.txt", "requirements file")

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
        "browser_opened_by_script",
        "dependencies_installed_by_script",
        "server_started_by_script",
        "private_core_exposed",
        "api_schema_modified",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
    ]:
        require_false(payload, key)

    top_doc = TOP_DOC.read_text(encoding="utf-8")
    report = SNAPSHOT_MD.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    runner = RUNNER.read_text(encoding="utf-8")
    combined_docs = "\n".join([top_doc, report, gate])
    required_tokens = [
        "local_trial_cold_start_preflight_v0_1: true",
        "local_mvp_cold_start_dependency_check",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "product_launched: false",
        "external_calls_made: false",
        "dependencies_installed_by_script: false",
        "server_started_by_script: false",
        "browser_opened_by_script: false",
        "private_core_exposed: false",
        "blockers_closed_by_cold_start_preflight: 0",
        "does not install dependencies",
        "does not start backend or landing services",
        "does not open a browser",
        "does not call external services",
        "does not claim customer validation",
    ]
    missing = [token for token in required_tokens if token not in combined_docs]
    require(not missing, "missing tokens: " + ", ".join(missing))

    forbidden_tokens = [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "customer_contacted: true",
        "product_launched: true",
        "external_validation_claim: true",
        "external_calls_made: true",
        "dependencies_installed_by_script: true",
        "server_started_by_script: true",
        "browser_opened_by_script: true",
        "private_core_exposed: true",
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden true claims: " + ", ".join(found))

    require("webbrowser.open" not in runner, "runner must not open browser")
    require("pip install" not in runner, "runner must not install dependencies")
    require("uvicorn.run" not in runner, "runner must not start uvicorn directly")
    require("https://" not in runner, "runner must not call external HTTPS")

    print(
        "SAEE_LOCAL_TRIAL_COLD_START_PREFLIGHT_SMOKE: PASS "
        f"status={payload['status']} "
        f"cold_start_ready={str(payload['cold_start_ready']).lower()} "
        "external_calls_made=false production_ready=false "
        "blockers_closed_by_cold_start_preflight=0"
    )


if __name__ == "__main__":
    main()
