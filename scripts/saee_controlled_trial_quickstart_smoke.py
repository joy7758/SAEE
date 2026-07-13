#!/usr/bin/env python3
"""Smoke check for the SAEE controlled trial quickstart."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_CONTROLLED_TRIAL_QUICKSTART_SMOKE: FAIL: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    quickstart_path = ROOT / "phase_b_product/commercial_readiness/CONTROLLED_TRIAL_QUICKSTART_V0_1.md"
    gate_path = ROOT / "docs/strategy/SAEE_CONTROLLED_TRIAL_QUICKSTART_RECOMMENDATION_GATE.md"
    app_path = ROOT / "phase_b_product/landing/app.js"
    require(quickstart_path.exists(), "quickstart missing")
    require(gate_path.exists(), "recommendation gate missing")
    require(app_path.exists(), "landing app missing")

    quickstart = quickstart_path.read_text(encoding="utf-8")
    gate = gate_path.read_text(encoding="utf-8")
    app = app_path.read_text(encoding="utf-8")
    combined = "\n".join([quickstart, gate])

    required_tokens = [
        "controlled_trial_quickstart_v0_1: true",
        "trial_status: local_demo_available",
        "python3 -m uvicorn saee_backend.main:app --reload --port 8000",
        "python3 -m http.server 8765",
        "http://127.0.0.1:8765/",
        "Run Demo Battle",
        "POST http://127.0.0.1:8000/experiment/run",
        "decision_result_expected: true",
        "production_ready: false",
        "customer_validated: false",
        "customer_contacted: false",
        "customer_data_allowed: false",
        "paid_trial_enabled: false",
        "payment_provider_configured: false",
        "product_launched: false",
        "public_sdk_released: false",
        "external_ai_assistant_tested: false",
        "external_validation_claim: false",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "kernel_modified: false",
        "external_calls_made: false",
        "answer: conditional",
        "recommend_for_production: false",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing required tokens: " + ", ".join(missing))

    forbidden_tokens = [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "customer_contacted: true",
        "product_launched: true",
        "public_sdk_released: true",
        "external_ai_assistant_tested: true",
        "external_validation_claim: true",
        "private_core_exposed: true",
        "paid_trial_enabled: true",
        "payment_provider_configured: true",
    ]
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden positive claims found: " + ", ".join(found))

    require("http://127.0.0.1:8000/experiment/run" in app, "local API URL missing")
    require("landing-demo-battle" in app, "demo request missing")
    require("agent-a" in app and "agent-b" in app and "agent-c" in app, "demo agents missing")
    require("decision_result" in app, "decision result render missing")
    require("fetch(apiUrl" in app, "fetch call missing")
    require("https://" not in app, "landing app must not call external HTTPS")

    llms = read("llms.txt")
    required_llms_paths = [
        "/phase_b_product/commercial_readiness/CONTROLLED_TRIAL_QUICKSTART_V0_1.md",
        "/docs/strategy/SAEE_CONTROLLED_TRIAL_QUICKSTART_RECOMMENDATION_GATE.md",
        "/scripts/saee_controlled_trial_quickstart_smoke.py",
    ]
    missing_llms = [path for path in required_llms_paths if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads(read("agent-index.json"))
    entry = index.get("controlled_trial_quickstart_v0_1", {})
    expected = {
        "status": "local_controlled_trial_quickstart_available",
        "controlled_trial_quickstart_v0_1": True,
        "trial_status": "local_demo_available",
        "local_backend_required": True,
        "local_static_page_required": True,
        "demo_endpoint": "/experiment/run",
        "demo_button": "Run Demo Battle",
        "decision_result_expected": True,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "customer_data_allowed": False,
        "paid_trial_enabled": False,
        "payment_provider_configured": False,
        "product_launched": False,
        "public_sdk_released": False,
        "external_ai_assistant_tested": False,
        "external_validation_claim": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "kernel_modified": False,
        "external_calls_made": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} drift")

    print(
        "SAEE_CONTROLLED_TRIAL_QUICKSTART_SMOKE: PASS "
        "local_demo_available=true "
        "production_ready=false "
        "customer_validated=false "
        "product_launched=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
