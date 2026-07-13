#!/usr/bin/env python3
"""Smoke check for SAEE local trial Makefile targets."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_LOCAL_TRIAL_MAKE_TARGETS_SMOKE: FAIL: {message}")


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    doc_path = "phase_b_product/commercial_readiness/LOCAL_TRIAL_MAKE_TARGETS_V0_1.md"
    gate_path = "docs/strategy/SAEE_LOCAL_TRIAL_MAKE_TARGETS_RECOMMENDATION_GATE.md"
    makefile = read("Makefile")
    doc = read(doc_path)
    gate = read(gate_path)
    smoke = read("scripts/saee_local_trial_make_targets_smoke.py")
    combined = "\n".join([doc, gate, makefile])

    required_make_tokens = [
        "local-trial-preflight:",
        "try-local: local-trial-start",
        "local-trial-start:",
        "local-trial-status:",
        "local-trial-stop:",
        "python3 scripts/saee_local_trial_session.py --json preflight",
        "python3 scripts/saee_local_trial_session.py start --wait-seconds 20",
        "python3 scripts/saee_local_trial_session.py status",
        "python3 scripts/saee_local_trial_session.py stop",
        "python3 scripts/saee_commercial_trial_operator_status.py",
    ]
    missing_make = [token for token in required_make_tokens if token not in makefile]
    require(not missing_make, "Makefile missing target tokens: " + ", ".join(missing_make))
    status_block = makefile.split("local-trial-status:", 1)[1].split("\n\n", 1)[0]
    require(
        "python3 scripts/saee_commercial_trial_operator_status.py" in status_block,
        "local-trial-status must refresh operator status",
    )

    required_doc_tokens = [
        "Status: local convenience targets available.",
        "http://127.0.0.1:8765/",
        "Run Demo Battle",
        "20-second local readiness window",
        "detached local child processes",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "external_validation_claim: false",
        "external_calls_made: false",
        "browser_opened_by_script: false",
        "dependencies_installed_by_script: false",
        "detached_local_child_processes: true",
        "refreshes_operator_status_on_start: true",
        "refreshes_operator_status_on_status: true",
        "refreshes_operator_status_on_stop: true",
        "private_core_exposed: false",
        "api_schema_modified: false",
        "runtime_modified: false",
        "backend_modified: false",
        "kernel_modified: false",
        "answer: recommend",
        "recommend_for_local_trial_convenience: true",
        "recommend_for_production: false",
    ]
    missing_doc = [token for token in required_doc_tokens if token not in combined]
    require(not missing_doc, "doc/gate missing tokens: " + ", ".join(missing_doc))

    forbidden_tokens = [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "product_launched: true",
        "external_validation_claim: true",
        "private_core_exposed: true",
        "browser_opened_by_script: true",
        "dependencies_installed_by_script: true",
    ]
    found = [token for token in forbidden_tokens if token in "\n".join([doc, gate])]
    require(not found, "forbidden true claims: " + ", ".join(found))
    require("webbrowser.open" not in makefile, "Makefile must not open browser")
    require("pip install" not in makefile, "Makefile must not install dependencies")
    require("https://" not in makefile, "Makefile must not call external HTTPS")
    subprocess_token = "subprocess" + ".run"
    require(subprocess_token not in smoke, "smoke must not execute make targets")

    llms = read("llms.txt")
    required_llms = [
        "/" + doc_path,
        "/" + gate_path,
        "/scripts/saee_local_trial_make_targets_smoke.py",
    ]
    missing_llms = [path for path in required_llms if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads(read("agent-index.json"))
    entry = index.get("local_trial_make_targets_v0_1", {})
    expected = {
        "status": "local_trial_make_targets_available",
        "local_trial_make_targets_v0_1": True,
        "make_try_local_available": True,
        "start_wait_seconds": 20,
        "uses_existing_session_manager": True,
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
        "external_calls_made": False,
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "detached_local_child_processes": True,
        "refreshes_operator_status_on_start": True,
        "refreshes_operator_status_on_status": True,
        "refreshes_operator_status_on_stop": True,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} drift")

    print(
        "SAEE_LOCAL_TRIAL_MAKE_TARGETS_SMOKE: PASS "
        "make_try_local_available=true "
        "production_ready=false "
        "customer_validated=false "
        "product_launched=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
