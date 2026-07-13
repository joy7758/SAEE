#!/usr/bin/env python3
"""Persist a local-only SAEE trial preflight snapshot.

The snapshot is a read-only operator aid for local MVP tryout. It does not
install dependencies, start servers, open a browser, call external services,
modify product behavior, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_local_trial_session import default_python, preflight_payload


OUTPUT_JSON = ROOT / "phase_b_product/validation/local_trial_preflight_snapshot.local.json"
OUTPUT_MD = ROOT / "phase_b_product/validation/local_trial_preflight_snapshot.md"
TOP_DOC = ROOT / "phase_b_product/validation/LOCAL_TRIAL_PREFLIGHT_SNAPSHOT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_LOCAL_TRIAL_PREFLIGHT_SNAPSHOT_RECOMMENDATION_GATE.md"


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
        "private_core_exposed": False,
        "api_schema_modified": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
    }


def build_snapshot(python: str, backend_port: int, landing_port: int) -> dict[str, Any]:
    preflight = preflight_payload(python, backend_port, landing_port)
    status = "pass" if preflight.get("ready_to_start") else "hold"
    return {
        "local_trial_preflight_snapshot_v0_1": True,
        "snapshot_type": "local_trial_preflight_snapshot",
        "status": status,
        "ready_to_start": bool(preflight.get("ready_to_start")),
        "preflight_scope": "local_controlled_trial_demo_operator_check",
        "generated_at": datetime.now(UTC).isoformat(),
        "generated_by": "scripts/saee_local_trial_preflight_snapshot.py",
        "selected_python": preflight.get("selected_python"),
        "selected_python_source": preflight.get("selected_python_source"),
        "prefers_local_venv_python": bool(preflight.get("prefers_local_venv_python")),
        "backend_port": preflight.get("backend_port"),
        "landing_port": preflight.get("landing_port"),
        "backend_port_open": bool(preflight.get("backend_port_open")),
        "landing_port_open": bool(preflight.get("landing_port_open")),
        "backend_owned_by_saee": bool(preflight.get("backend_owned_by_saee")),
        "landing_owned_by_saee": bool(preflight.get("landing_owned_by_saee")),
        "backend_port_usable": bool(preflight.get("backend_port_usable")),
        "landing_port_usable": bool(preflight.get("landing_port_usable")),
        "required_files_present": bool(preflight.get("required_files_present")),
        "required_files": preflight.get("required_files", {}),
        "fastapi_available": bool(preflight.get("fastapi_available")),
        "uvicorn_available": bool(preflight.get("uvicorn_available")),
        "missing_or_blocking_items": preflight.get("missing_or_blocking_items", []),
        "blockers_closed_by_snapshot": 0,
        "local_loopback_probe_only": True,
        "human_review_required": True,
        "next_human_action": (
            "If status is pass, a human may start or use the local trial demo; "
            "if status is hold, resolve missing local dependencies or port conflicts first."
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
    body = f"""# SAEE Local Trial Preflight Snapshot

local_trial_preflight_snapshot_v0_1: true
snapshot_type: local_trial_preflight_snapshot
preflight_scope: {payload["preflight_scope"]}
status: {payload["status"]}
ready_to_start: {bool_text(payload["ready_to_start"])}
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
dependencies_installed_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_snapshot: 0

## Purpose

This snapshot records whether the current local machine appears ready for a
human to run the SAEE local MVP trial path. It is an operator preflight record,
not product validation and not a production readiness claim.

## Local Checks

- selected_python: `{payload["selected_python"]}`
- selected_python_source: `{payload["selected_python_source"]}`
- prefers local `.venv` Python: {bool_text(payload["prefers_local_venv_python"])}
- FastAPI import available: {bool_text(payload["fastapi_available"])}
- Uvicorn import available: {bool_text(payload["uvicorn_available"])}
- backend port: {payload["backend_port"]}
- backend port open: {bool_text(payload["backend_port_open"])}
- backend owned by SAEE: {bool_text(payload["backend_owned_by_saee"])}
- backend port usable: {bool_text(payload["backend_port_usable"])}
- landing port: {payload["landing_port"]}
- landing port open: {bool_text(payload["landing_port_open"])}
- landing owned by SAEE: {bool_text(payload["landing_owned_by_saee"])}
- landing port usable: {bool_text(payload["landing_port_usable"])}
- required files present: {bool_text(payload["required_files_present"])}

## Required Files

{file_lines}

## Missing Or Blocking Items

{missing_lines}

## Boundary

This snapshot uses only local file checks, Python import checks, and localhost
loopback probes. It does not install dependencies, start servers, open a
browser, call external services, contact customers, process customer data,
modify backend behavior, modify runtime/kernel/API schema, expose private core,
launch product, close production blockers, or claim production readiness.

## Next Human Action

{payload["next_human_action"]}
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_top_doc(path: Path) -> None:
    body = """# SAEE Local Trial Preflight Snapshot v0.1

local_trial_preflight_snapshot_v0_1: true
snapshot_scope: current_local_environment_tryout_preflight
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
dependencies_installed_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_snapshot: 0

## Purpose

The local trial preflight snapshot persists the result of checking whether a
human can run the current local SAEE MVP tryout path on this machine.

It helps answer a commercial-readiness question:

```text
Can a reviewer try the local MVP now, and if not, what local setup item blocks it?
```

## What It Checks

- required local backend and landing files;
- the selected Python executable, preferring `.venv/bin/python` when available;
- FastAPI and Uvicorn import availability when the backend is not already
  running;
- localhost backend port ownership;
- localhost landing port ownership;
- whether the existing local backend and landing services appear to be SAEE.

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

- `phase_b_product/validation/local_trial_preflight_snapshot.local.json`
- `phase_b_product/validation/local_trial_preflight_snapshot.md`

## Run

```bash
python3 scripts/saee_local_trial_preflight_snapshot.py
python3 scripts/saee_local_trial_preflight_snapshot_smoke.py
```
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def write_gate(path: Path) -> None:
    body = """# SAEE Local Trial Preflight Snapshot Recommendation Gate

answer: recommend_for_local_tryout_preflight_only

## Reason

If a potential reviewer asks how to try SAEE locally, this snapshot is useful
because it records whether the current local machine is ready for a controlled
MVP tryout. It improves trial handoff clarity without changing product behavior.

## Recommendation Boundary

recommend_for_local_tryout_preflight: true
recommend_for_production: false
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_validation_claim: false
external_calls_made: false
dependencies_installed_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_snapshot: 0

## Not Recommended As

- proof of production readiness;
- proof of customer validation;
- proof of external AI assistant validation;
- proof that support, billing, auth, legal, or operations blockers are closed;
- a launch authorization.

## Next Action

Use `local_trial_preflight_snapshot.local.json` as local setup evidence only.
If the snapshot status is `pass`, a human may run the local demo. If it is
`hold`, a human should resolve local setup items and rerun the snapshot.
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=default_python())
    parser.add_argument("--backend-port", type=int, default=8000)
    parser.add_argument("--landing-port", type=int, default=8765)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = build_snapshot(args.python, args.backend_port, args.landing_port)
    write_top_doc(TOP_DOC)
    write_gate(GATE)
    write_json(OUTPUT_JSON, payload)
    write_report(OUTPUT_MD, payload)
    print(
        "SAEE_LOCAL_TRIAL_PREFLIGHT_SNAPSHOT: PASS "
        f"status={payload['status']} "
        f"ready_to_start={str(payload['ready_to_start']).lower()} "
        "external_calls_made=false production_ready=false blockers_closed_by_snapshot=0"
    )


if __name__ == "__main__":
    main()
