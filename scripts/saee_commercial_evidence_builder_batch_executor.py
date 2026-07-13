#!/usr/bin/env python3
"""Preflight and, after exact human approval, run four fixed local builders.

Default behavior is a dry-run that executes zero builders. ``--apply`` is
accepted only when the canonical approval, request, and all four current
validator records pass strict checks. The executor never closes blockers.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request"
REQUEST = OUT / "batch_request.local.json"
APPROVAL = OUT / "batch_approval.human_filled.local.json"
PREFLIGHT = OUT / "batch_execution_preflight.local.json"
PREFLIGHT_MD = OUT / "batch_execution_preflight.md"
BOUNDARY = OUT / "batch_execution_boundary_audit.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"

EXACT_PHRASE = (
    "批准本地批量证据 builder 执行：仅运行 production_monitoring、"
    "production_restore_policy、formal_security_review、pricing_page 四个 builder，"
    "不关闭 blocker，不联系任何人，不发布，不声明生产可用。"
)

TARGETS = [
    {
        "blocker_id": "production_monitoring",
        "builder": "scripts/saee_production_monitoring_evidence_builder.py",
        "input": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json",
        "validator": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_validation.local.json",
        "output": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_builder_output.local.json",
    },
    {
        "blocker_id": "production_restore_policy",
        "builder": "scripts/saee_production_restore_policy_evidence_builder.py",
        "input": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json",
        "validator": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_validation.local.json",
        "output": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_evidence_builder_output.local.json",
    },
    {
        "blocker_id": "formal_security_review",
        "builder": "scripts/saee_formal_security_review_evidence_builder.py",
        "input": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json",
        "validator": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_validation.local.json",
        "output": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_output.local.json",
    },
    {
        "blocker_id": "pricing_page",
        "builder": "scripts/saee_pricing_page_evidence_builder.py",
        "input": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json",
        "validator": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_validation.local.json",
        "output": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_builder_output.local.json",
    },
]
TARGET_IDS = [target["blocker_id"] for target in TARGETS]

FALSE_FLAGS = {
    "blocker_closure_authorized": False,
    "blockers_closed": 0,
    "customer_contacted": False,
    "vendor_contacted": False,
    "external_calls_made": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "private_core_exposed": False,
}


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def validate_request(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "commercial_evidence_builder_batch_request_v0_1": True,
        "status": "ready_for_exact_human_batch_builder_execution_approval",
        "target_blocker_ids": TARGET_IDS,
        "target_count": 4,
        "ready_target_count": 4,
        "builders_executed_by_request": 0,
        "blockers_closed_by_request": 0,
        "production_ready": False,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"request.{key} must equal {value!r}")
    return errors


def validate_approval(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "commercial_evidence_builder_batch_human_approval_v0_1": True,
        "status": "approved_four_local_builders_pending_separate_execution",
        "exact_approval_phrase": EXACT_PHRASE,
        "approve_four_local_builders_only": True,
        "approved_target_blocker_ids": TARGET_IDS,
        "confirm_no_blocker_closure": True,
        "confirm_no_external_contact": True,
        "confirm_no_publication": True,
        "confirm_no_production_readiness_claim": True,
        "confirm_separate_execution_step_required": True,
        "batch_builder_execution_approved": True,
        "builder_execution_authorized": True,
        "builders_executed": 0,
        **FALSE_FLAGS,
    }
    for key, value in expected.items():
        if data.get(key) != value:
            errors.append(f"approval.{key} must equal {value!r}")
    for key in ("human_reviewer_name", "approval_reference", "approval_date"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            errors.append(f"approval.{key} must be a non-empty string")
    return errors


def validate_target(target: dict[str, str]) -> dict[str, Any]:
    errors: list[str] = []
    builder = ROOT / target["builder"]
    input_path = ROOT / target["input"]
    validator_path = ROOT / target["validator"]
    output_path = ROOT / target["output"]
    for label, path in (("builder", builder), ("input", input_path), ("validator", validator_path)):
        if not path.is_file():
            errors.append(f"{label} missing: {path.relative_to(ROOT)}")
    validator: dict[str, Any] = {}
    if validator_path.is_file():
        try:
            validator = read_json(validator_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"validator unreadable: {exc}")
    expected = {
        "target_blocker_id": target["blocker_id"],
        "validation_status": "pass",
        "input_complete": True,
        "builder_ready": True,
        "boundary_violation_count": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
    }
    for key, value in expected.items():
        if validator.get(key) != value:
            errors.append(f"validator.{key} must equal {value!r}")
    return {
        **target,
        "command": [sys.executable, target["builder"], "--input", target["input"]],
        "builder_exists": builder.is_file(),
        "input_exists": input_path.is_file(),
        "validator_exists": validator_path.is_file(),
        "output_exists_before": output_path.is_file(),
        "validator_passed": not errors,
        "preflight_errors": errors,
    }


Runner = Callable[..., subprocess.CompletedProcess[str]]


def execute_targets(
    targets: list[dict[str, str]], runner: Runner = subprocess.run
) -> list[dict[str, Any]]:
    """Run only the fixed argv mappings; runner injection supports no-op tests."""
    results: list[dict[str, Any]] = []
    for target in targets:
        command = [sys.executable, target["builder"], "--input", target["input"]]
        completed = runner(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        result: dict[str, Any] = {
            "blocker_id": target["blocker_id"],
            "command": command,
            "returncode": completed.returncode,
            "stdout_tail": completed.stdout[-2000:],
            "stderr_tail": completed.stderr[-2000:],
            "builder_succeeded": False,
            "output_status": None,
            "output_input_complete": False,
        }
        output_path = ROOT / target["output"]
        if completed.returncode == 0 and output_path.is_file():
            try:
                output = read_json(output_path)
                result["output_status"] = output.get("status")
                result["output_input_complete"] = output.get("input_complete") is True
                result["builder_succeeded"] = (
                    output.get("status") == "pass"
                    and output.get("input_complete") is True
                    and output.get("production_ready") is False
                    and output.get("customer_validated") is False
                    and output.get("product_launched") is False
                )
            except (OSError, ValueError, json.JSONDecodeError) as exc:
                result["output_read_error"] = str(exc)
        results.append(result)
        if not result["builder_succeeded"]:
            break
    return results


def build_summary(apply_requested: bool, runner: Runner = subprocess.run) -> dict[str, Any]:
    request_errors: list[str] = []
    approval_errors: list[str] = []
    try:
        request_errors = validate_request(read_json(REQUEST))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        request_errors = [f"request unavailable: {exc}"]
    approval_present = APPROVAL.is_file()
    approval: dict[str, Any] = {}
    if approval_present:
        try:
            approval = read_json(APPROVAL)
            approval_errors = validate_approval(approval)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            approval_errors = [f"approval unreadable: {exc}"]
    else:
        approval_errors = ["canonical human approval record is missing"]

    target_preflights = [validate_target(target) for target in TARGETS]
    targets_ready = all(item["validator_passed"] for item in target_preflights)
    preflight_passed = not request_errors and not approval_errors and targets_ready
    results: list[dict[str, Any]] = []
    if apply_requested and preflight_passed:
        results = execute_targets(TARGETS, runner=runner)
    executed = len(results)
    succeeded = sum(bool(result.get("builder_succeeded")) for result in results)

    if apply_requested and not preflight_passed:
        status = "hold_apply_rejected_preflight_failed"
    elif apply_requested and succeeded == 4:
        status = "four_local_builders_executed_pending_separate_evidence_review"
    elif apply_requested:
        status = "stop_builder_execution_incomplete_separate_review_required"
    elif preflight_passed:
        status = "ready_for_explicit_apply_no_execution"
    elif not approval_present:
        status = "hold_human_approval_missing_no_execution"
    else:
        status = "hold_preflight_failed_no_execution"

    return {
        "commercial_evidence_builder_batch_executor_v0_1": True,
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_mode": "apply" if apply_requested else "dry_run",
        "apply_requested": apply_requested,
        "canonical_approval_path": str(APPROVAL.relative_to(ROOT)),
        "canonical_approval_present": approval_present,
        "approval_valid": not approval_errors,
        "approval_errors": approval_errors,
        "human_reviewer_name": approval.get("human_reviewer_name", "") if not approval_errors else "",
        "approval_reference": approval.get("approval_reference", "") if not approval_errors else "",
        "request_valid": not request_errors,
        "request_errors": request_errors,
        "target_count": 4,
        "target_blocker_ids": TARGET_IDS,
        "targets_ready": targets_ready,
        "target_preflights": target_preflights,
        "preflight_passed": preflight_passed,
        "builder_execution_authorized": preflight_passed,
        "builders_executed": executed,
        "builders_succeeded": succeeded,
        "execution_results": results,
        "separate_evidence_review_required": True,
        "separate_blocker_closure_review_required": True,
        "next_human_action": (
            "Review the four local builder outputs; do not close blockers without a separate evidence decision."
            if succeeded == 4
            else (
                "Run this fixed executor with --apply only if the approved four-builder scope is still intended."
                if preflight_passed
                else "Record the exact canonical human approval and resolve every preflight error before any apply attempt."
            )
        ),
        **FALSE_FLAGS,
    }


def render_markdown(summary: dict[str, Any]) -> str:
    error_lines = [f"- {error}" for error in summary["approval_errors"] + summary["request_errors"]]
    for target in summary["target_preflights"]:
        error_lines.extend(f"- {target['blocker_id']}: {error}" for error in target["preflight_errors"])
    errors = "\n".join(error_lines) or "- none"
    return f"""# SAEE Four-Builder Batch Execution Preflight

Status: `{summary['status']}`

- execution_mode: `{summary['execution_mode']}`
- canonical_approval_present: `{str(summary['canonical_approval_present']).lower()}`
- approval_valid: `{str(summary['approval_valid']).lower()}`
- preflight_passed: `{str(summary['preflight_passed']).lower()}`
- builders_executed: `{summary['builders_executed']}`
- builders_succeeded: `{summary['builders_succeeded']}`
- blockers_closed: `0`
- production_ready: `false`

## Preflight errors

{errors}

## Boundary

Default mode is dry-run. Even a successful `--apply` only creates local
evidence for separate review; it does not close a blocker, contact anyone,
publish anything, or establish production readiness.
"""


def update_agent_index(summary: dict[str, Any]) -> None:
    data = read_json(AGENT_INDEX)
    data["commercial_evidence_builder_batch_executor_v0_1"] = {
        "status": summary["status"],
        "execution_mode": summary["execution_mode"],
        "target_count": 4,
        "target_blocker_ids": TARGET_IDS,
        "canonical_approval_present": summary["canonical_approval_present"],
        "approval_valid": summary["approval_valid"],
        "preflight_passed": summary["preflight_passed"],
        "builders_executed": summary["builders_executed"],
        "builders_succeeded": summary["builders_succeeded"],
        "separate_evidence_review_required": True,
        "separate_blocker_closure_review_required": True,
        "entrypoints": {
            "gate": "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_EXECUTOR_GATE.md",
            "preflight": "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_execution_preflight.local.json",
            "runner": "scripts/saee_commercial_evidence_builder_batch_executor.py",
            "smoke": "scripts/saee_commercial_evidence_builder_batch_executor_smoke.py",
        },
        **FALSE_FLAGS,
    }
    write_json(AGENT_INDEX, data)


def append_llms() -> None:
    additions = [
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_EXECUTOR_GATE.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_execution_preflight.local.json",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_execution_preflight.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_execution_boundary_audit.md",
        "/scripts/saee_commercial_evidence_builder_batch_executor.py",
        "/scripts/saee_commercial_evidence_builder_batch_executor_smoke.py",
    ]
    lines = LLMS.read_text(encoding="utf-8").splitlines()
    for item in additions:
        if item not in lines:
            lines.append(item)
    write(LLMS, "\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Run the four fixed local builders only after canonical approval and preflight pass.",
    )
    args = parser.parse_args()
    summary = build_summary(args.apply)
    write_json(PREFLIGHT, summary)
    write(PREFLIGHT_MD, render_markdown(summary))
    write(
        BOUNDARY,
        "# SAEE Batch Executor Boundary Audit\n\n"
        f"- status: `{summary['status']}`\n"
        f"- execution_mode: `{summary['execution_mode']}`\n"
        f"- builders_executed: {summary['builders_executed']}\n"
        f"- builders_succeeded: {summary['builders_succeeded']}\n"
        "- arbitrary_commands_allowed: false\n- shell_execution_allowed: false\n"
        "- blocker_closure_authorized: false\n- blockers_closed: 0\n"
        "- external_calls_made: false\n- production_ready: false\n"
        "- separate_evidence_review_required: true\n",
    )
    update_agent_index(summary)
    append_llms()
    print(
        "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_EXECUTOR: PASS "
        f"status={summary['status']} mode={summary['execution_mode']} "
        f"preflight_passed={str(summary['preflight_passed']).lower()} "
        f"builders_executed={summary['builders_executed']} "
        "blockers_closed=0 production_ready=false"
    )
    if args.apply and not summary["preflight_passed"]:
        return 2
    if args.apply and summary["builders_succeeded"] != 4:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
