#!/usr/bin/env python3
"""Persist a local-only SAEE cold-start preflight snapshot.

This checks whether the selected local Python environment can start the SAEE
MVP backend from a clean shell. It does not install dependencies, start
servers, open a browser, call external services, modify product behavior, or
claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "phase_b_product/validation/local_trial_cold_start_preflight.local.json"
OUTPUT_MD = ROOT / "phase_b_product/validation/local_trial_cold_start_preflight.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_COLD_START_PREFLIGHT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_COLD_START_PREFLIGHT_RECOMMENDATION_GATE.md"
LOCAL_VENV_PYTHON = ROOT / ".venv/bin/python"


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
        "browser_opened_by_script": False,
        "dependencies_installed_by_script": False,
        "server_started_by_script": False,
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }


def module_available(python: str, module: str) -> bool:
    code = (
        "import importlib.util, sys; "
        f"sys.exit(0 if importlib.util.find_spec({module!r}) else 1)"
    )
    try:
        result = subprocess.run(
            [python, "-c", code],
            cwd=ROOT,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except OSError:
        return False
    return result.returncode == 0


def rel_or_str(path: str) -> str:
    value = Path(path)
    try:
        return str(value.resolve().relative_to(ROOT))
    except (OSError, ValueError):
        return path


def default_python() -> str:
    if LOCAL_VENV_PYTHON.exists():
        return str(LOCAL_VENV_PYTHON)
    return sys.executable


def build_snapshot(python: str) -> dict[str, Any]:
    required_files = {
        "backend_entrypoint": (ROOT / "saee_backend/main.py").exists(),
        "backend_requirements": (ROOT / "saee_backend/requirements.txt").exists(),
        "landing_index": (ROOT / "phase_b_product/landing/index.html").exists(),
        "landing_app": (ROOT / "phase_b_product/landing/app.js").exists(),
    }
    fastapi_available = module_available(python, "fastapi")
    uvicorn_available = module_available(python, "uvicorn")
    required_files_present = all(required_files.values())
    cold_start_ready = required_files_present and fastapi_available and uvicorn_available
    missing = [name for name, present in required_files.items() if not present]
    if not fastapi_available:
        missing.append("python_module_fastapi")
    if not uvicorn_available:
        missing.append("python_module_uvicorn")

    return {
        "local_trial_cold_start_preflight_v0_1": True,
        "snapshot_type": "local_trial_cold_start_preflight",
        "status": "pass" if cold_start_ready else "hold",
        "cold_start_ready": cold_start_ready,
        "preflight_scope": "local_mvp_cold_start_dependency_check",
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_local_trial_cold_start_preflight.py",
        "selected_python": python,
        "selected_python_display": rel_or_str(python),
        "selected_python_source": "local_venv" if Path(python).resolve() == LOCAL_VENV_PYTHON.resolve() else "explicit_or_current_python",
        "required_files_present": required_files_present,
        "required_files": required_files,
        "fastapi_available": fastapi_available,
        "uvicorn_available": uvicorn_available,
        "missing_or_blocking_items": missing,
        "requirements_file": "saee_backend/requirements.txt",
        "backend_start_command": (
            f"{rel_or_str(python)} -m uvicorn saee_backend.main:app --host 127.0.0.1 --port 8000"
        ),
        "landing_start_command": (
            "cd phase_b_product/landing && python3 -m http.server 8765 --bind 127.0.0.1"
        ),
        "blockers_closed_by_cold_start_preflight": 0,
        "local_dependency_probe_only": True,
        "human_review_required": True,
        "next_human_action": (
            "If status is hold, prepare a controlled local Python environment with "
            "the backend requirements, then rerun this cold-start preflight. Do not "
            "treat an already-running backend as cold-start readiness."
        ),
        **boundary_flags(),
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_text(value: object) -> str:
    return "true" if value is True else "false" if value is False else str(value)


def write_report(path: Path, payload: dict[str, Any]) -> None:
    missing = payload.get("missing_or_blocking_items", [])
    missing_lines = "\n".join(f"- {item}" for item in missing) if missing else "- none"
    required_files = payload.get("required_files", {})
    file_lines = "\n".join(
        f"- {name}: {bool_text(present)}" for name, present in sorted(required_files.items())
    )
    body = f"""# SAEE Local Trial Cold-Start Preflight

local_trial_cold_start_preflight_v0_1: true
snapshot_type: local_trial_cold_start_preflight
preflight_scope: {payload["preflight_scope"]}
status: {payload["status"]}
cold_start_ready: {bool_text(payload["cold_start_ready"])}
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
dependencies_installed_by_script: false
server_started_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_cold_start_preflight: 0

## Purpose

This snapshot records whether the selected Python environment can start the
SAEE local MVP backend from a clean shell. It is stricter than the normal local
trial preflight because an already-running backend does not prove cold-start
readiness.

## Local Checks

- selected_python: `{payload["selected_python"]}`
- FastAPI import available: {bool_text(payload["fastapi_available"])}
- Uvicorn import available: {bool_text(payload["uvicorn_available"])}
- required files present: {bool_text(payload["required_files_present"])}
- requirements file: `{payload["requirements_file"]}`

## Required Files

{file_lines}

## Missing Or Blocking Items

{missing_lines}

## Human Start Commands After Cold-Start Readiness

Backend:

```bash
{payload["backend_start_command"]}
```

Landing page:

```bash
{payload["landing_start_command"]}
```

## Boundary

This cold-start preflight uses only local file checks and Python import checks.
It does not install dependencies, start servers, open a browser, call external
services, contact customers, process customer data, modify backend behavior,
modify runtime/kernel/API schema, expose private core, launch product, close
production blockers, or claim production readiness.

## Next Human Action

{payload["next_human_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Local Trial Cold-Start Preflight v0.1

local_trial_cold_start_preflight_v0_1: true
snapshot_scope: local_mvp_cold_start_dependency_check
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
dependencies_installed_by_script: false
server_started_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_cold_start_preflight: 0

## Purpose

The local trial cold-start preflight records whether a reviewer can start the
SAEE MVP backend from the selected Python environment, independent of any
already-running local service.

It helps answer a commercial-readiness question:

```text
Can a fresh local reviewer reproduce the SAEE MVP tryout from this Python environment?
```

## What It Checks

- required local backend and landing files;
- the selected Python executable;
- FastAPI import availability;
- Uvicorn import availability;
- the backend requirements file.

## What It Does Not Do

- does not install dependencies;
- does not start backend or landing services;
- does not open a browser;
- does not call external services;
- does not contact customers;
- does not process customer data;
- does not modify product behavior;
- does not modify runtime, backend logic, kernel, or API schema;
- does not close commercial blockers;
- does not claim customer validation, external validation, product launch, or
  production readiness.

## Generated Outputs

- `phase_b_product/validation/local_trial_cold_start_preflight.local.json`
- `phase_b_product/validation/local_trial_cold_start_preflight.md`

## Run

```bash
python3 scripts/saee_local_trial_cold_start_preflight.py
python3 scripts/saee_local_trial_cold_start_preflight_smoke.py
```
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Local Trial Cold-Start Preflight Recommendation Gate

answer: recommend_for_local_cold_start_preflight_only

## Reason

If a potential reviewer asks whether SAEE can be tried locally from a fresh
environment, this cold-start preflight is useful because it separates
already-running local service availability from reproducible backend startup
readiness.

## Recommendation Boundary

recommend_for_local_cold_start_preflight: true
recommend_for_production: false
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_validation_claim: false
external_calls_made: false
dependencies_installed_by_script: false
server_started_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_cold_start_preflight: 0

## Not Recommended For

- production readiness proof;
- customer validation proof;
- dependency installation automation;
- backend startup automation;
- blocker closure.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def run(python: str) -> dict[str, Any]:
    payload = build_snapshot(python)
    write_json(OUTPUT_JSON, payload)
    write_report(OUTPUT_MD, payload)
    write_top_doc(TOP_DOC)
    write_gate(GATE)
    return payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=default_python())
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run(args.python)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return
    print(
        "SAEE_LOCAL_TRIAL_COLD_START_PREFLIGHT: PASS "
        f"status={payload['status']} "
        f"cold_start_ready={str(payload['cold_start_ready']).lower()} "
        "dependencies_installed_by_script=false production_ready=false "
        "blockers_closed_by_cold_start_preflight=0"
    )


if __name__ == "__main__":
    main()
