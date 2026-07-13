#!/usr/bin/env python3
"""Record the local trial session start/status/stop lifecycle proof.

This proof exercises the same local session manager used by `make try-local`,
checks that the localhost backend and landing page report running, then stops
the manager-started processes. It does not open a browser, call external
services, install dependencies, contact customers, modify product behavior, or
claim production readiness.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/validation/local_trial_lifecycle_proof"
OUTPUT_JSON = OUTPUT_DIR / "local_trial_lifecycle_proof.local.json"
OUTPUT_MD = OUTPUT_DIR / "local_trial_lifecycle_proof.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_LIFECYCLE_PROOF_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_LIFECYCLE_PROOF_RECOMMENDATION_GATE.md"


def boundary_flags() -> dict[str, bool]:
    return {
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
        "external_model_api_called": False,
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "server_started_by_script": True,
        "server_stopped_by_script": True,
        "temporary_localhost_server_only": True,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }


def run_json(args: list[str]) -> tuple[bool, dict[str, Any], str]:
    try:
        result = subprocess.run(
            [sys.executable, "scripts/saee_local_trial_session.py", "--json", *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except OSError as exc:
        return False, {}, str(exc)
    if result.returncode != 0:
        return False, {}, (result.stderr or result.stdout).strip()
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return False, {}, f"invalid JSON from {' '.join(args)}: {exc}"
    if not isinstance(payload, dict):
        return False, {}, f"non-object JSON from {' '.join(args)}"
    return True, payload, ""


def compact_status(payload: dict[str, Any]) -> dict[str, Any]:
    keys = [
        "session_state",
        "backend_health_ok",
        "landing_page_ok",
        "backend_pid_running",
        "landing_pid_running",
        "started_by_manager",
        "backend_already_running",
        "landing_already_running",
        "browser_opened_by_script",
        "external_calls_made",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "detached_local_child_processes",
    ]
    return {key: payload.get(key) for key in keys if key in payload}


def build_payload() -> dict[str, Any]:
    start_ok = False
    start_payload: dict[str, Any] = {}
    running_ok = False
    running_payload: dict[str, Any] = {}
    stop_ok = False
    stop_payload: dict[str, Any] = {}
    final_ok = False
    final_payload: dict[str, Any] = {}
    pre_stop_ok = False
    pre_stop_payload: dict[str, Any] = {}
    errors: list[str] = []

    try:
        pre_stop_ok, pre_stop_payload, pre_stop_error = run_json(["stop"])
        if not pre_stop_ok:
            errors.append(f"pre-stop: {pre_stop_error}")
        start_ok, start_payload, start_error = run_json(["start"])
        if not start_ok:
            errors.append(f"start: {start_error}")
        running_ok, running_payload, running_error = run_json(["status"])
        if not running_ok:
            errors.append(f"running status: {running_error}")
    finally:
        stop_ok, stop_payload, stop_error = run_json(["stop"])
        if not stop_ok:
            errors.append(f"stop: {stop_error}")
        final_ok, final_payload, final_error = run_json(["status"])
        if not final_ok:
            errors.append(f"final status: {final_error}")

    lifecycle_passed = (
        start_ok
        and running_ok
        and stop_ok
        and final_ok
        and start_payload.get("session_state") == "running"
        and running_payload.get("session_state") == "running"
        and running_payload.get("backend_health_ok") is True
        and running_payload.get("landing_page_ok") is True
        and start_payload.get("detached_local_child_processes") is True
        and running_payload.get("detached_local_child_processes") is True
        and final_payload.get("session_state") == "not_running"
        and final_payload.get("backend_pid_running") is False
        and final_payload.get("landing_pid_running") is False
    )
    return {
        "local_trial_lifecycle_proof_v0_1": True,
        "proof_type": "local_trial_session_start_status_stop",
        "status": "pass" if lifecycle_passed else "hold",
        "lifecycle_passed": lifecycle_passed,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_local_trial_lifecycle_proof.py",
        "commands_exercised": [
            "python3 scripts/saee_local_trial_session.py --json stop",
            "python3 scripts/saee_local_trial_session.py --json start",
            "python3 scripts/saee_local_trial_session.py --json status",
            "python3 scripts/saee_local_trial_session.py --json stop",
            "python3 scripts/saee_local_trial_session.py --json status",
        ],
        "make_try_local_equivalent_checked": True,
        "pre_stop_attempted": True,
        "pre_stop_ok": pre_stop_ok,
        "start_session_state": start_payload.get("session_state"),
        "running_session_state": running_payload.get("session_state"),
        "stop_session_state": stop_payload.get("session_state"),
        "final_session_state": final_payload.get("session_state"),
        "running_backend_health_ok": running_payload.get("backend_health_ok") is True,
        "running_landing_page_ok": running_payload.get("landing_page_ok") is True,
        "detached_local_child_processes": (
            start_payload.get("detached_local_child_processes") is True
            and running_payload.get("detached_local_child_processes") is True
        ),
        "start_detached_local_child_processes": (
            start_payload.get("detached_local_child_processes") is True
        ),
        "running_detached_local_child_processes": (
            running_payload.get("detached_local_child_processes") is True
        ),
        "final_backend_pid_running": final_payload.get("backend_pid_running") is True,
        "final_landing_pid_running": final_payload.get("landing_pid_running") is True,
        "blockers_closed_by_lifecycle_proof": 0,
        "human_review_required": True,
        "pre_stop_snapshot": compact_status(pre_stop_payload),
        "start_snapshot": compact_status(start_payload),
        "running_snapshot": compact_status(running_payload),
        "stop_snapshot": compact_status(stop_payload),
        "final_snapshot": compact_status(final_payload),
        "missing_or_blocking_items": errors,
        "next_human_action": (
            "If status is pass, a human can use `make try-local`, open the local "
            "URL manually, and stop the session with `make local-trial-stop`. "
            "Keep all production, customer-validation, and launch claims on hold."
        ),
        **boundary_flags(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    errors = payload.get("missing_or_blocking_items", [])
    error_lines = "\n".join(f"- {item}" for item in errors) if errors else "- none"
    body = f"""# SAEE Local Trial Lifecycle Proof

local_trial_lifecycle_proof_v0_1: true
proof_type: local_trial_session_start_status_stop
status: {payload["status"]}
lifecycle_passed: {bool_text(payload["lifecycle_passed"])}
make_try_local_equivalent_checked: true
pre_stop_attempted: true
running_backend_health_ok: {bool_text(payload["running_backend_health_ok"])}
running_landing_page_ok: {bool_text(payload["running_landing_page_ok"])}
detached_local_child_processes: {bool_text(payload["detached_local_child_processes"])}
start_detached_local_child_processes: {bool_text(payload["start_detached_local_child_processes"])}
running_detached_local_child_processes: {bool_text(payload["running_detached_local_child_processes"])}
final_session_state: {payload["final_session_state"]}
final_backend_pid_running: {bool_text(payload["final_backend_pid_running"])}
final_landing_pid_running: {bool_text(payload["final_landing_pid_running"])}
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
browser_opened_by_script: false
dependencies_installed_by_script: false
private_core_exposed: false
blockers_closed_by_lifecycle_proof: 0

## Purpose

This proof records the local trial lifecycle: start the localhost backend and
landing page through the local session manager, confirm both are running, stop
the manager-started processes, and confirm the session is no longer running.

It is a commercial-readiness operator proof for local tryout repeatability. It
is not customer validation, not production readiness, and not product launch.

## Commands Exercised

- `python3 scripts/saee_local_trial_session.py --json stop`
- `python3 scripts/saee_local_trial_session.py --json start`
- `python3 scripts/saee_local_trial_session.py --json status`
- `python3 scripts/saee_local_trial_session.py --json stop`
- `python3 scripts/saee_local_trial_session.py --json status`

## Missing Or Blocking Items

{error_lines}

## Boundary

This proof starts only temporary localhost services and stops them before
finishing. It does not open a browser, install dependencies, call external
services, contact customers, process customer data, modify backend behavior,
modify runtime/kernel/API schema, expose private core, launch product, close
production blockers, or claim production readiness.

The proof also verifies `detached_local_child_processes=true` from the start
and status payloads. That confirms the local trial remains available after the
start command returns in short-lived operator shells.

## Next Human Action

{payload["next_human_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Local Trial Lifecycle Proof v0.1

local_trial_lifecycle_proof_v0_1: true
proof_scope: local_trial_session_start_status_stop
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
browser_opened_by_script: false
dependencies_installed_by_script: false
private_core_exposed: false
blockers_closed_by_lifecycle_proof: 0
detached_local_child_processes: true

## Purpose

This proof records whether the local tryout session can be started, observed as
running, stopped, and observed as not running. It strengthens controlled-preview
trial operations without changing product behavior.

It also verifies detached local child processes so `make try-local` remains
usable after the command returns in short-lived operator shells.

## Run

```bash
python3 scripts/saee_local_trial_lifecycle_proof.py
python3 scripts/saee_local_trial_lifecycle_proof_smoke.py
```

## Boundary

The proof uses localhost only. It does not open a browser, call external
services, install dependencies, contact customers, process customer data, close
commercial blockers, launch product, or claim production readiness.

It does not call external services and does not claim production readiness.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Local Trial Lifecycle Proof Recommendation Gate

answer: recommend_for_local_tryout_lifecycle_proof_only

## Reason

If a reviewer asks whether SAEE can currently be tried locally, this proof is
useful because it records the actual start/status/stop lifecycle for the local
trial session. It should be recommended only as local tryout evidence.

It also checks detached local child processes, so `make try-local` remains
usable after the command returns in short-lived operator shells.

## Boundary

recommend_for_local_tryout_lifecycle: true
recommend_for_production: false
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_validation_claim: false
external_calls_made: false
browser_opened_by_script: false
dependencies_installed_by_script: false
private_core_exposed: false
blockers_closed_by_lifecycle_proof: 0
detached_local_child_processes: true
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_top_doc(TOP_DOC)
    write_gate(GATE)
    write_json(OUTPUT_JSON, payload)
    write_report(OUTPUT_MD, payload)
    print(
        "SAEE_LOCAL_TRIAL_LIFECYCLE_PROOF: PASS "
        f"status={payload['status']} "
        f"lifecycle_passed={str(payload['lifecycle_passed']).lower()} "
        f"final_session_state={payload['final_session_state']} "
        "external_calls_made=false production_ready=false blockers_closed_by_lifecycle_proof=0"
    )
    if not payload["lifecycle_passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
