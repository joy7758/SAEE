#!/usr/bin/env python3
"""Run a local HTTP E2E trial against the SAEE MVP API shell.

This starts a temporary localhost FastAPI server, posts the landing-page demo
payload to /experiment/run, records the result, and shuts the server down. It
does not call external services, open a browser, contact customers, modify the
backend/runtime/kernel/API schema, expose private core, or claim production
readiness.
"""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/validation/local_trial_http_e2e"
OUTPUT_JSON = OUTPUT_DIR / "local_trial_http_e2e.local.json"
OUTPUT_MD = OUTPUT_DIR / "local_trial_http_e2e.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_HTTP_E2E_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_HTTP_E2E_RECOMMENDATION_GATE.md"
LOCAL_VENV_PYTHON = ROOT / ".venv/bin/python"


def default_python() -> str:
    if LOCAL_VENV_PYTHON.exists():
        return str(LOCAL_VENV_PYTHON)
    return sys.executable


def rel_or_str(path: str) -> str:
    value = Path(path)
    try:
        return str(value.resolve().relative_to(ROOT))
    except (OSError, ValueError):
        return path


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
        "temporary_localhost_server_only": True,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def demo_payload() -> dict[str, Any]:
    return {
        "experiment_id": "local-trial-http-e2e",
        "agents": [
            {
                "agent_id": "agent-a",
                "config": {"policy": "aggressive-experimental-risky-unguarded-fragile"},
                "type": "llm",
            },
            {
                "agent_id": "agent-b",
                "config": {"workflow": "guarded-stable-monitor-retry-bounded-safe"},
                "type": "workflow",
            },
            {
                "agent_id": "agent-c",
                "config": "rule-conservative-bounded-retry",
                "type": "rule",
            },
        ],
        "environment": {
            "scenario_type": "landing_demo_competition",
            "noise_level": 0.25,
            "competition_intensity": 0.55,
            "time_horizon": 60,
        },
        "evaluation_config": {
            "metrics": ["stability", "survival", "failure_mode", "ranking"],
            "repeat_runs": 5,
        },
    }


def fetch_json(url: str, *, timeout: float = 1.5) -> tuple[bool, dict[str, Any] | None, str]:
    req = Request(url, headers={"User-Agent": "saee-local-trial-http-e2e/0.1"})
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except (HTTPError, OSError, URLError) as exc:
        return False, None, str(exc)
    try:
        return True, json.loads(raw), ""
    except json.JSONDecodeError as exc:
        return False, None, f"invalid JSON: {exc}"


def post_json(url: str, payload: dict[str, Any], *, timeout: float = 5.0) -> tuple[int, dict[str, Any] | None, str]:
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "User-Agent": "saee-local-trial-http-e2e/0.1",
        },
    )
    try:
        with urlopen(req, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
            status = int(response.status)
    except HTTPError as exc:
        return int(exc.code), None, exc.read().decode("utf-8", errors="replace")
    except (OSError, URLError) as exc:
        return 0, None, str(exc)
    try:
        return status, json.loads(raw), ""
    except json.JSONDecodeError as exc:
        return status, None, f"invalid JSON: {exc}"


def wait_for_health(url: str, timeout_seconds: float = 8.0) -> tuple[bool, dict[str, Any] | None, str]:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        ok, payload, error = fetch_json(url)
        if ok and payload and payload.get("status") == "ok":
            return True, payload, ""
        last_error = error
        time.sleep(0.25)
    return False, None, last_error or "timeout waiting for /health"


def local_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "SAEE_ENV": "local_http_e2e",
            "SAEE_REQUIRE_API_KEY": "false",
            "SAEE_REQUIRE_TENANT_ID": "false",
            "SAEE_REQUIRE_RBAC_ROLE": "false",
            "SAEE_REQUIRE_JWT_PREVIEW_AUTH": "false",
            "SAEE_STORAGE_BACKEND": "memory",
            "SAEE_REQUEST_AUDIT_ENABLED": "false",
        }
    )
    return env


def build_failure_snapshot(python: str, port: int, reason: str) -> dict[str, Any]:
    return {
        "local_trial_http_e2e_v0_1": True,
        "snapshot_type": "local_trial_http_e2e",
        "status": "hold",
        "http_e2e_ready": False,
        "http_e2e_passed": False,
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_local_trial_http_e2e.py",
        "selected_python": python,
        "selected_python_display": rel_or_str(python),
        "selected_python_source": (
            "local_venv"
            if Path(python).resolve() == LOCAL_VENV_PYTHON.resolve()
            else "explicit_or_current_python"
        ),
        "backend_port": port,
        "health_status": "not_ready",
        "demo_post_status_code": 0,
        "expected_recommended_agent": "agent-b",
        "observed_recommended_agent": None,
        "ranking_top": None,
        "ranking_count": 0,
        "failure_modes_summary_present": False,
        "missing_or_blocking_items": [reason],
        "blockers_closed_by_http_e2e": 0,
        "human_review_required": True,
        "next_human_action": (
            "Resolve the local HTTP E2E blocker, rerun this check, and keep all "
            "commercial launch claims on hold."
        ),
        **boundary_flags(),
    }


def run_http_e2e(python: str) -> dict[str, Any]:
    port = find_free_port()
    health_url = f"http://127.0.0.1:{port}/health"
    run_url = f"http://127.0.0.1:{port}/experiment/run"
    command = [
        python,
        "-m",
        "uvicorn",
        "saee_backend.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
    ]
    proc: subprocess.Popen[bytes] | None = None
    try:
        proc = subprocess.Popen(
            command,
            cwd=ROOT,
            env=local_env(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        ok, health_payload, error = wait_for_health(health_url)
        if not ok:
            return build_failure_snapshot(python, port, error)
        status_code, response, post_error = post_json(run_url, demo_payload())
        if status_code != 200 or not response:
            return build_failure_snapshot(
                python,
                port,
                f"demo POST failed: status={status_code} error={post_error}",
            )

        decision = response.get("decision_result") if isinstance(response, dict) else {}
        if not isinstance(decision, dict):
            decision = {}
        ranking = decision.get("ranking", [])
        failure_summary = decision.get("failure_modes_summary", {})
        observed = response.get("recommended_agent") or decision.get("recommended_agent")
        ranking_top = ranking[0].get("agent_id") if ranking and isinstance(ranking[0], dict) else None
        passed = (
            response.get("status") == "completed"
            and observed == "agent-b"
            and ranking_top == "agent-b"
            and len(ranking) == 3
            and isinstance(failure_summary, dict)
            and set(failure_summary) == {"agent-a", "agent-b", "agent-c"}
        )
        missing = []
        if not passed:
            missing.append("http_demo_response_did_not_match_expected_local_trial_result")
        return {
            "local_trial_http_e2e_v0_1": True,
            "snapshot_type": "local_trial_http_e2e",
            "status": "pass" if passed else "hold",
            "http_e2e_ready": passed,
            "http_e2e_passed": passed,
            "generated_at": datetime.now(UTC).isoformat(),
            "generated_by": "scripts/saee_local_trial_http_e2e.py",
            "selected_python": python,
            "selected_python_display": rel_or_str(python),
            "selected_python_source": (
                "local_venv"
                if Path(python).resolve() == LOCAL_VENV_PYTHON.resolve()
                else "explicit_or_current_python"
            ),
            "backend_port": port,
            "health_status": health_payload.get("status") if health_payload else None,
            "demo_endpoint": "/experiment/run",
            "demo_post_status_code": status_code,
            "expected_recommended_agent": "agent-b",
            "observed_recommended_agent": observed,
            "ranking_top": ranking_top,
            "ranking_count": len(ranking) if isinstance(ranking, list) else 0,
            "failure_modes_summary_present": isinstance(failure_summary, dict)
            and bool(failure_summary),
            "decision_result_present": isinstance(decision, dict) and bool(decision),
            "confidence_score_present": "confidence_score" in response,
            "missing_or_blocking_items": missing,
            "blockers_closed_by_http_e2e": 0,
            "human_review_required": True,
            "next_human_action": (
                "Use this as local HTTP trial proof only; do not treat it as "
                "customer validation, production readiness, or commercial launch."
            ),
            **boundary_flags(),
        }
    finally:
        if proc and proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    missing = payload.get("missing_or_blocking_items", [])
    missing_lines = "\n".join(f"- {item}" for item in missing) if missing else "- none"
    body = f"""# SAEE Local Trial HTTP E2E

local_trial_http_e2e_v0_1: true
snapshot_type: local_trial_http_e2e
status: {payload["status"]}
http_e2e_ready: {bool_text(payload["http_e2e_ready"])}
http_e2e_passed: {bool_text(payload["http_e2e_passed"])}
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
external_ai_assistant_tested: false
external_validation_claim: false
browser_opened_by_script: false
dependencies_installed_by_script: false
server_started_by_script: true
temporary_localhost_server_only: true
private_core_exposed: false
blockers_closed_by_http_e2e: 0

## Purpose

This local HTTP E2E snapshot proves whether a reviewer can exercise the SAEE
MVP public API through a real temporary FastAPI localhost server. It is stricter
than the service-layer E2E check because it uses HTTP `/health` and
`/experiment/run`.

## Observed Result

- selected_python: `{payload["selected_python_display"]}`
- backend_port: `{payload["backend_port"]}`
- health_status: `{payload["health_status"]}`
- demo_post_status_code: `{payload["demo_post_status_code"]}`
- expected_recommended_agent: `{payload["expected_recommended_agent"]}`
- observed_recommended_agent: `{payload["observed_recommended_agent"]}`
- ranking_top: `{payload["ranking_top"]}`
- ranking_count: `{payload["ranking_count"]}`
- failure_modes_summary_present: {bool_text(payload["failure_modes_summary_present"])}

## Missing Or Blocking Items

{missing_lines}

## Boundary

This check starts only a temporary localhost server and shuts it down after the
probe. It does not open a browser. It does not install dependencies. It does
not call external services. It does not claim production readiness. It does not
contact customers, process customer data, modify backend behavior, modify
runtime/kernel/API schema, expose private core, close production blockers,
launch product, or claim customer validation.

## Next Human Action

{payload["next_human_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Local Trial HTTP E2E v0.1

Status: local HTTP trial proof only, not production readiness.

This artifact records the local-only HTTP E2E path for the SAEE MVP API shell:

```text
temporary localhost FastAPI server -> GET /health -> POST /experiment/run -> deterministic recommendation
```

It is intended to reduce trial friction before any commercial pilot. It does not
modify SAEE product behavior, backend implementation, runtime, kernel, API
schema, or private core.

## Boundaries

- external_calls_made: false
- browser_opened_by_script: false
- dependencies_installed_by_script: false
- server_started_by_script: true
- temporary_localhost_server_only: true
- production_ready: false
- customer_validated: false
- customer_contacted: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_http_e2e: 0

## Files

- `phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.local.json`
- `phase_b_product/validation/local_trial_http_e2e/local_trial_http_e2e.md`
- `docs/strategy/SAEE_LOCAL_TRIAL_HTTP_E2E_RECOMMENDATION_GATE.md`
- `scripts/saee_local_trial_http_e2e.py`
- `scripts/saee_local_trial_http_e2e_smoke.py`
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    body = f"""# SAEE Local Trial HTTP E2E Recommendation Gate

answer: {"recommend" if payload["http_e2e_passed"] else "conditional"}

reason: The local HTTP trial proof exercises the public FastAPI API shell through
`/health` and `/experiment/run`, then records whether the deterministic demo
recommendation is available through localhost. This supports controlled local
trial usability, but does not prove production readiness or customer validation.

status: {payload["status"]}
http_e2e_passed: {bool_text(payload["http_e2e_passed"])}
observed_recommended_agent: {payload["observed_recommended_agent"]}
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
blockers_closed_by_http_e2e: 0

## Boundary

The check starts a temporary localhost server only. It does not call external
services, open a browser, contact customers, launch product, modify API schema,
modify runtime/kernel/backend behavior, or expose private core.

## Next Action

Use this as local trial evidence only. Formal commercial readiness still
requires production auth, tenant isolation, operations, support, legal,
billing, and real customer validation evidence.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> None:
    python = sys.argv[1] if len(sys.argv) > 1 else default_python()
    payload = run_http_e2e(python)
    write_json(OUTPUT_JSON, payload)
    write_report(OUTPUT_MD, payload)
    write_top_doc(TOP_DOC)
    write_gate(GATE, payload)
    print(
        "SAEE_LOCAL_TRIAL_HTTP_E2E: "
        f"{payload['status'].upper()} "
        f"http_e2e_passed={str(payload['http_e2e_passed']).lower()} "
        f"observed_recommended_agent={payload['observed_recommended_agent']} "
        "external_calls_made=false "
        "production_ready=false "
        "customer_validated=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
