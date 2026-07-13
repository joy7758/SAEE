#!/usr/bin/env python3
"""Smoke check for the SAEE local trial session manager."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_LOCAL_TRIAL_SESSION_SMOKE: FAIL: {message}")


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> None:
    doc_path = ROOT / "phase_b_product/commercial_readiness/LOCAL_TRIAL_SESSION_MANAGER_V0_1.md"
    gate_path = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_SESSION_MANAGER_RECOMMENDATION_GATE.md"
    script_path = ROOT / "scripts/saee_local_trial_session.py"
    require(doc_path.exists(), "local trial session manager doc missing")
    require(gate_path.exists(), "recommendation gate missing")
    require(script_path.exists(), "session manager script missing")

    result = subprocess.run(
        [sys.executable, str(script_path), "--json", "describe"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    payload = json.loads(result.stdout)
    require(payload["local_trial_session_manager_v0_1"] is True, "describe flag")
    require(payload["session_scope"] == "local_controlled_trial_demo_operator_tool", "scope")
    require(payload["status"] == "available", "status")
    require(payload["prefers_local_venv_python"] is True, "prefers local venv python")
    require(payload["detached_local_child_processes"] is True, "detached local child processes")
    require(
        payload["default_python_source"] in {"local_venv", "explicit_or_current_python"},
        "default python source",
    )
    require(
        set(payload["commands"]) == {"describe", "preflight", "status", "start", "stop"},
        "commands",
    )
    require(payload["preflight"]["scope"] == "local_controlled_trial_demo_operator_check", "preflight scope")
    require(
        payload["preflight"]["command_template"]
        == "python3 scripts/saee_local_trial_session.py --json preflight",
        "preflight command",
    )
    require(payload["backend"]["demo_endpoint"].endswith("/experiment/run"), "demo endpoint")
    require(payload["landing"]["url"] == "http://127.0.0.1:8765/", "landing url")
    boundaries = payload["boundaries"]
    expected_false = [
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
        "private_core_exposed",
        "api_schema_modified",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
    ]
    for key in expected_false:
        require(boundaries.get(key) is False, f"boundary {key} must be false")
        require(payload.get(key) is False, f"top-level describe {key} must be false")

    preflight_result = subprocess.run(
        [sys.executable, str(script_path), "--json", "preflight"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    preflight = json.loads(preflight_result.stdout)
    require(preflight["local_trial_session_preflight_v0_1"] is True, "preflight flag")
    require(preflight["preflight_scope"] == "local_controlled_trial_demo_operator_check", "preflight output scope")
    require(preflight["prefers_local_venv_python"] is True, "preflight prefers local venv python")
    require(
        preflight["selected_python_source"] in {"local_venv", "explicit_or_current_python"},
        "preflight selected python source",
    )
    require(preflight["required_files_present"] is True, "required files")
    require(preflight["required_files"]["backend_entrypoint"] is True, "backend entrypoint")
    require(preflight["required_files"]["landing_index"] is True, "landing index")
    require(preflight["backend_port_usable"] in {True, False}, "backend port usable boolean")
    require(preflight["landing_port_usable"] in {True, False}, "landing port usable boolean")
    require(preflight["external_calls_made"] is False if "external_calls_made" in preflight else True, "external calls")
    for key in expected_false:
        require(preflight["boundaries"].get(key) is False, f"preflight boundary {key} must be false")
        require(preflight.get(key) is False, f"top-level preflight {key} must be false")

    status_result = subprocess.run(
        [sys.executable, str(script_path), "--json", "status"],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    status = json.loads(status_result.stdout)
    require(status["local_trial_session_manager_v0_1"] is True, "status flag")
    require(status["session_state"] in {"running", "not_running"}, "status state")
    require(status["backend_url"].startswith("http://127.0.0.1:"), "status backend url")
    require(status["landing_url"].startswith("http://127.0.0.1:"), "status landing url")
    for key in expected_false:
        require(status["boundaries"].get(key) is False, f"status boundary {key} must be false")
        require(status.get(key) is False, f"top-level status {key} must be false")

    doc = doc_path.read_text(encoding="utf-8")
    gate = gate_path.read_text(encoding="utf-8")
    script = script_path.read_text(encoding="utf-8")
    combined = "\n".join([doc, gate])
    required_tokens = [
        "local_trial_session_manager_v0_1: true",
        "local_trial_session_preflight_v0_1: true",
        "session_scope: local_controlled_trial_demo_operator_tool",
        "python3 scripts/saee_local_trial_session.py --json preflight",
        "python3 scripts/saee_local_trial_session.py start --wait-seconds 20",
        "20-second local readiness window",
        "detached_local_child_processes: true",
        "detached local child processes",
        "python3 scripts/saee_local_trial_session.py status",
        "python3 scripts/saee_local_trial_session.py stop",
        "http://127.0.0.1:8765/",
        "Run Demo Battle",
        "POST http://127.0.0.1:8000/experiment/run",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "external_validation_claim: false",
        "private_core_exposed: false",
        "dependencies_installed_by_script: false",
        "browser_opened_by_script: false",
        "answer: recommend",
        "recommend_for_production: false",
        "local_controlled_trial_demo_operator_check",
        "prefers_local_venv_python: true",
        ".venv/bin/python",
    ]
    missing = [token for token in required_tokens if token not in combined]
    require(not missing, "missing doc/gate tokens: " + ", ".join(missing))

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
    found = [token for token in forbidden_tokens if token in combined]
    require(not found, "forbidden true claims: " + ", ".join(found))
    require("webbrowser.open" not in script, "script must not open browser")
    require("pip install" not in script, "script must not install dependencies")
    require("https://" not in script, "script must not call external HTTPS")
    require("start_new_session=True" in script, "script must detach local child processes")
    require("stdin=subprocess.DEVNULL" in script, "script must close child stdin")

    llms = read("llms.txt")
    required_llms_paths = [
        "/phase_b_product/commercial_readiness/LOCAL_TRIAL_SESSION_MANAGER_V0_1.md",
        "/docs/strategy/SAEE_LOCAL_TRIAL_SESSION_MANAGER_RECOMMENDATION_GATE.md",
        "/scripts/saee_local_trial_session.py",
        "/scripts/saee_local_trial_session_smoke.py",
    ]
    missing_llms = [path for path in required_llms_paths if path not in llms]
    require(not missing_llms, "llms.txt missing paths: " + ", ".join(missing_llms))

    index = json.loads(read("agent-index.json"))
    entry = index.get("local_trial_session_manager_v0_1", {})
    expected = {
        "status": "local_trial_session_manager_available",
        "local_trial_session_manager_v0_1": True,
        "local_trial_session_preflight_v0_1": True,
        "session_scope": "local_controlled_trial_demo_operator_tool",
        "local_backend_required": True,
        "local_static_page_required": True,
        "demo_endpoint": "/experiment/run",
        "demo_button": "Run Demo Battle",
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
        "prefers_local_venv_python": True,
        "detached_local_child_processes": True,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} drift")

    print(
        "SAEE_LOCAL_TRIAL_SESSION_SMOKE: PASS "
        "local_trial_session_manager_available=true "
        "production_ready=false "
        "customer_validated=false "
        "product_launched=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
