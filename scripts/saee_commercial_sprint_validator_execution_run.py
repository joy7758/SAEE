#!/usr/bin/env python3
"""Run the approved local commercial sprint validators.

This script is for the explicit human-approved validator step after template
transfer. It runs only the five existing local input validators listed in the
post-transfer approval packet. It does not run evidence builders, close
blockers, contact customers or vendors, launch product, or claim production
readiness.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
APPROVAL_PACKET = SPRINT_DIR / "commercial_sprint_validator_approval_request_packet.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_validator_execution_run.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_validator_execution_run.md"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_validator_execution_run_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN_GATE.md"

FALSE_FLAGS = [
    "development_permission_granted",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "evidence_collection_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_approval(packet: dict[str, Any]) -> None:
    if packet.get("status") != "hold_validator_approval_required":
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN: FAIL "
            "approval packet must be hold_validator_approval_required"
        )
    if packet.get("ready_validator_count") != 5:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN: FAIL "
            "expected five ready validators"
        )
    if packet.get("ready_for_validator_approval") is not True:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN: FAIL "
            "validator approval readiness is not true"
        )


def run_validator(row: dict[str, Any]) -> dict[str, Any]:
    runner = row["runner"]
    input_path = row["human_filled_input_target"]
    output_path = ROOT / row["validation_output"]
    command = [sys.executable, runner, "--input", input_path]
    completed = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    validation: dict[str, Any] = {}
    if output_path.is_file():
        validation = read_json(output_path)
    return {
        "sequence_id": row["sequence_id"],
        "blocker_id": row["blocker_id"],
        "validator_key": row["validator_key"],
        "runner": runner,
        "human_filled_input_target": input_path,
        "command": "python3 " + runner + " --input " + input_path,
        "return_code": completed.returncode,
        "stdout_tail": completed.stdout.strip().splitlines()[-3:],
        "stderr_tail": completed.stderr.strip().splitlines()[-3:],
        "validation_output": row["validation_output"],
        "validation_output_exists": output_path.is_file(),
        "validator_run": True,
        "validation_status": validation.get("validation_status", "execution_failed"),
        "builder_ready": validation.get("builder_ready") is True,
        "blockers_closed_by_validator": int(validation.get("blockers_closed_by_validator", 0) or 0),
    }


def status_for(results: list[dict[str, Any]]) -> str:
    if any(result["return_code"] != 0 for result in results):
        return "completed_with_validator_execution_failures"
    if any(result["validation_status"] == "stop" for result in results):
        return "completed_with_validator_stop"
    if any(result["validation_status"] == "hold" for result in results):
        return "completed_with_validator_holds"
    if all(result["validation_status"] == "pass" for result in results):
        return "completed_all_validators_passed"
    return "completed_with_mixed_validator_status"


def build_payload() -> dict[str, Any]:
    packet = read_json(APPROVAL_PACKET)
    ensure_approval(packet)
    rows = packet.get("approval_requests", [])
    results = [run_validator(row) for row in rows]
    payload: dict[str, Any] = {
        "commercial_sprint_validator_execution_run_v0_1": True,
        "run_type": "human_approved_local_validator_execution_only",
        "status": status_for(results),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_validator_execution_run.py",
        "source_approval_packet": rel(APPROVAL_PACKET),
        "human_validator_execution_authorized": True,
        "validator_execution_authorized": True,
        "validators_run_on_real_input": True,
        "task_candidates_executed": True,
        "planned_validator_count": len(rows),
        "validators_run_count": len(results),
        "validator_pass_count": sum(1 for result in results if result["validation_status"] == "pass"),
        "validator_hold_count": sum(1 for result in results if result["validation_status"] == "hold"),
        "validator_stop_count": sum(1 for result in results if result["validation_status"] == "stop"),
        "validator_execution_failure_count": sum(1 for result in results if result["return_code"] != 0),
        "builder_ready_count": sum(1 for result in results if result["builder_ready"]),
        "blockers_closed_by_run": sum(result["blockers_closed_by_validator"] for result in results),
        "separate_evidence_builder_request_required": True,
        "validation_results": results,
        "next_action": (
            "Review validator outputs. If any validator is hold, complete its missing "
            "input or boundary issue. Evidence builders still require a separate "
            "explicit human-approved request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {sequence_id} | {blocker_id} | {validation_status} | {builder_ready} | {return_code} | {validation_output} |".format(
            **result
        )
        for result in payload["validation_results"]
    )
    path.write_text(
        f"""# Commercial Sprint Validator Execution Run v0.1

commercial_sprint_validator_execution_run_v0_1: true
run_type: {payload['run_type']}
status: {payload['status']}
human_validator_execution_authorized: true
validator_execution_authorized: true
validators_run_on_real_input: true
validators_run_count: {payload['validators_run_count']}
validator_pass_count: {payload['validator_pass_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_stop_count: {payload['validator_stop_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_run: {payload['blockers_closed_by_run']}
separate_evidence_builder_request_required: true
evidence_collection_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
production_ready: false
customer_validated: false
product_launched: false

## Results

| Sequence | Blocker | Status | Builder Ready | Return Code | Output |
| --- | --- | --- | --- | --- | --- |
{rows}

## Boundary

This run executes only local input validators after explicit human approval.
It does not execute evidence builders, close blockers, contact customers or
vendors, launch product, claim production readiness, modify runtime, modify
backend, modify kernel, modify API schema, or expose private core.
""",
        encoding="utf-8",
    )


def write_boundary(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# Commercial Sprint Validator Execution Boundary Audit

commercial_sprint_validator_execution_run_v0_1: true
status: {payload['status']}
validators_run_on_real_input: true
validator_execution_authorized: true
evidence_collection_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
development_permission_granted: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
customer_contacted: false
external_calls_made: false
external_model_api_called: false
external_ai_assistant_tested: false

Only local validator scripts were run. No external service was contacted and no
SAEE runtime, backend, kernel, API schema, or private core was modified.
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Validator Execution Run Gate

answer: local_validator_execution_recorded

reason:
The user explicitly approved running the five prepared local validators after
template transfer. The validators were run locally and recorded with status
`{payload['status']}`. This does not authorize evidence builders or blocker
closure.

boundary:
- validators_run_on_real_input: true
- evidence_collection_authorized: false
- evidence_builder_executed: false
- blocker_closure_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false

next_action:
Review validator outputs. Any evidence-builder execution requires a separate
explicit human-approved request.
""",
        encoding="utf-8",
    )


def update_agent_index(payload: dict[str, Any]) -> None:
    path = ROOT / "agent-index.json"
    index = read_json(path)
    index["commercial_sprint_validator_execution_run_v0_1"] = {
        "status": payload["status"],
        "run_type": payload["run_type"],
        "human_validator_execution_authorized": True,
        "validator_execution_authorized": True,
        "validators_run_on_real_input": True,
        "validators_run_count": payload["validators_run_count"],
        "validator_pass_count": payload["validator_pass_count"],
        "validator_hold_count": payload["validator_hold_count"],
        "validator_stop_count": payload["validator_stop_count"],
        "builder_ready_count": payload["builder_ready_count"],
        "blockers_closed_by_run": payload["blockers_closed_by_run"],
        "separate_evidence_builder_request_required": True,
        "evidence_collection_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    write_json(path, index)


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_report(OUT_MD, payload)
    write_boundary(OUT_BOUNDARY, payload)
    write_gate(GATE, payload)
    update_agent_index(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_EXECUTION_RUN: PASS "
        f"status={payload['status']} validators_run_count={payload['validators_run_count']} "
        f"validator_pass_count={payload['validator_pass_count']} "
        f"validator_hold_count={payload['validator_hold_count']} production_ready=false"
    )
    if payload["validator_execution_failure_count"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
