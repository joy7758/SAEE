#!/usr/bin/env python3
"""Validate the support-group final closure decision template without executing.

This validator checks whether a human has filled the support-group final
closure decision template consistently. A valid approve decision can only make a
future separate matrix-update request ready; it does not update the canonical
matrix, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
REQUEST_JSON = SUPPORT_DIR / "support_group_final_closure_decision_request.local.json"
TEMPLATE_JSON = SUPPORT_DIR / "support_group_final_closure_decision_template.json"
OUT_JSON = SUPPORT_DIR / "support_group_final_closure_decision_validation.local.json"
OUT_MD = SUPPORT_DIR / "support_group_final_closure_decision_validation.md"
OUT_CSV = SUPPORT_DIR / "support_group_final_closure_decision_validation.csv"
BOUNDARY = SUPPORT_DIR / "support_group_final_closure_decision_validation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TARGET_BLOCKERS = ["support_contact", "customer_support", "sla", "on_call_rotation"]
ALLOWED_DECISIONS = ["approve_for_separate_matrix_update_request", "hold", "reject"]

FALSE_FLAGS = {
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_validator": 0,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "support_vendor_contacted": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def replace_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def clean(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def build_payload() -> dict[str, Any]:
    request = read_json(REQUEST_JSON)
    template = read_json(TEMPLATE_JSON)

    decision = clean(template.get("human_final_decision"))
    reviewer = clean(template.get("human_reviewer"))
    decision_date = clean(template.get("decision_date"))
    reason = clean(template.get("reason"))
    authorize_matrix_update = template.get("authorize_separate_matrix_update_request") is True
    authorize_closure_now = template.get("authorize_blocker_closure_now") is True
    authorize_launch = template.get("authorize_product_launch") is True
    confirm_no_customer_validation_claim = template.get("confirm_no_customer_validation_claim") is True
    confirm_no_production_ready_claim = template.get("confirm_no_production_ready_claim") is True
    target_blockers = template.get("target_blockers", [])

    boundary_violations: list[str] = []
    if authorize_closure_now:
        boundary_violations.append("template.authorize_blocker_closure_now")
    if authorize_launch:
        boundary_violations.append("template.authorize_product_launch")
    if not confirm_no_customer_validation_claim:
        boundary_violations.append("template.confirm_no_customer_validation_claim_false")
    if not confirm_no_production_ready_claim:
        boundary_violations.append("template.confirm_no_production_ready_claim_false")
    if target_blockers != TARGET_BLOCKERS:
        boundary_violations.append("template.target_blockers_changed")
    for source_name, source in [("request", request), ("template", template)]:
        for flag in [
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "customer_contacted",
            "external_calls_made",
        ]:
            if source.get(flag) is True:
                boundary_violations.append(f"{source_name}.{flag}")

    decision_fields_complete = bool(decision and reviewer and decision_date and reason)
    decision_allowed = decision in ALLOWED_DECISIONS
    approve_ready = bool(
        decision == "approve_for_separate_matrix_update_request"
        and decision_fields_complete
        and authorize_matrix_update
        and not authorize_closure_now
        and not authorize_launch
        and confirm_no_customer_validation_claim
        and confirm_no_production_ready_claim
        and not boundary_violations
    )
    final_hold_recorded = bool(
        decision == "hold"
        and decision_fields_complete
        and not authorize_matrix_update
        and not authorize_closure_now
        and not authorize_launch
        and not boundary_violations
    )
    final_reject_recorded = bool(
        decision == "reject"
        and decision_fields_complete
        and not authorize_matrix_update
        and not authorize_closure_now
        and not authorize_launch
        and not boundary_violations
    )

    if boundary_violations:
        status = "stop_boundary_violation"
    elif not decision:
        status = "hold_human_final_decision_missing"
    elif not decision_allowed:
        status = "stop_invalid_final_decision"
    elif approve_ready:
        status = "ready_for_separate_matrix_update_request_no_closure"
    elif final_hold_recorded:
        status = "final_hold_recorded_no_action"
    elif final_reject_recorded:
        status = "final_reject_recorded_no_action"
    else:
        status = "hold_incomplete_or_inconsistent_final_decision"

    final_human_decision_recorded = status in {
        "ready_for_separate_matrix_update_request_no_closure",
        "final_hold_recorded_no_action",
        "final_reject_recorded_no_action",
    }

    return {
        "support_group_final_closure_decision_validator_v0_1": True,
        "validator_type": "human_final_closure_decision_template_validator_no_execution",
        "validator_scope": "validate_template_only_no_matrix_change_no_closure",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target_blocker_group": "support",
        "target_blockers": TARGET_BLOCKERS,
        "source_request_json": rel(REQUEST_JSON),
        "source_template_json": rel(TEMPLATE_JSON),
        "source_request_status": request.get("status"),
        "request_recommended_human_decision": request.get("recommended_human_decision"),
        "allowed_final_decisions": ALLOWED_DECISIONS,
        "human_final_decision": decision,
        "human_reviewer_present": bool(reviewer),
        "decision_date_present": bool(decision_date),
        "reason_present": bool(reason),
        "decision_fields_complete": decision_fields_complete,
        "decision_allowed": decision_allowed,
        "authorize_separate_matrix_update_request": authorize_matrix_update,
        "authorize_blocker_closure_now": authorize_closure_now,
        "authorize_product_launch": authorize_launch,
        "confirm_no_customer_validation_claim": confirm_no_customer_validation_claim,
        "confirm_no_production_ready_claim": confirm_no_production_ready_claim,
        "separate_matrix_update_request_ready": approve_ready,
        "final_hold_recorded": final_hold_recorded,
        "final_reject_recorded": final_reject_recorded,
        "final_human_decision_recorded": final_human_decision_recorded,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "next_human_action": (
            "fill the final closure decision template with approve, hold, or reject"
            if not final_human_decision_recorded
            else "create a separate matrix update request if approved"
        ),
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fields = [
            "target_blocker_group",
            "status",
            "human_final_decision",
            "decision_fields_complete",
            "authorize_separate_matrix_update_request",
            "authorize_blocker_closure_now",
            "authorize_product_launch",
            "separate_matrix_update_request_ready",
            "final_human_decision_recorded",
            "blockers_closed_by_validator",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerow({field: payload.get(field) for field in fields})

    OUT_MD.write_text(
        f"""# SAEE Support Group Final Closure Decision Validator v0.1

Status: `{payload['status']}`

This validator checks the human final closure decision template for the support
group. It does not execute the decision, update the matrix, close blockers, or
claim production readiness.

## Summary

- target_blockers: `{', '.join(payload['target_blockers'])}`
- source_request_status: `{payload['source_request_status']}`
- request_recommended_human_decision: `{payload['request_recommended_human_decision']}`
- human_final_decision: `{payload['human_final_decision'] or 'missing'}`
- decision_fields_complete: `{str(payload['decision_fields_complete']).lower()}`
- authorize_separate_matrix_update_request: `{str(payload['authorize_separate_matrix_update_request']).lower()}`
- authorize_blocker_closure_now: `{str(payload['authorize_blocker_closure_now']).lower()}`
- separate_matrix_update_request_ready: `{str(payload['separate_matrix_update_request_ready']).lower()}`
- final_human_decision_recorded: `{str(payload['final_human_decision_recorded']).lower()}`
- blockers_closed_by_validator: `0`

## Boundary

- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- canonical_closure_board_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_validator=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        f"""# SAEE Support Group Final Closure Decision Validator Boundary Audit

support_group_final_closure_decision_validator_v0_1: true
status: {payload['status']}

- Template validation only.
- No matrix update executed.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blockers closed.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.
- No customer-validation claim added.
- blockers_closed_by_validator: 0
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        """# SAEE Support Group Final Closure Decision Validator v0.1

support_group_final_closure_decision_validator_v0_1: true

Purpose: validate whether the support-group final closure decision template has
been filled safely. A passing approval only makes a separate matrix update
request ready; it does not close blockers.

Entrypoints:

- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.local.json`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.md`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.csv`
- `phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation_boundary_audit.md`
""",
        encoding="utf-8",
    )

    GATE.write_text(
        f"""# SAEE Support Group Final Closure Decision Validator Gate

answer: {payload['status']}

reason: The validator inspected the support-group final closure decision
template. It did not update the matrix or close blockers.

boundary:
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- canonical_closure_board_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_validator: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: {payload['next_human_action']}
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation.csv",
        "/phase_b_product/commercial_readiness/support_evidence/support_group_final_closure_decision_validation_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_GATE.md",
        "/scripts/saee_support_group_final_closure_decision_validator.py",
        "/scripts/saee_support_group_final_closure_decision_validator_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["support_group_final_closure_decision_validator_v0_1"] = {
        "name": "SAEE Support Group Final Closure Decision Validator v0.1",
        "status": payload["status"],
        "target_blocker_group": "support",
        "target_blockers": TARGET_BLOCKERS,
        "human_final_decision": payload["human_final_decision"],
        "final_human_decision_recorded": payload["final_human_decision_recorded"],
        "separate_matrix_update_request_ready": payload["separate_matrix_update_request_ready"],
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_validator": 0,
        "development_permission_granted": False,
        "execution_authorized": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "entrypoints": {
            "summary": rel(OUT_JSON),
            "report": rel(OUT_MD),
            "csv": rel(OUT_CSV),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_support_group_final_closure_decision_validator.py",
            "smoke": "scripts/saee_support_group_final_closure_decision_validator_smoke.py",
        },
        "make_target": "make check-support-group-final-closure-decision-validator",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = f"""## Support Group Final Closure Decision Validator v0.1

- `support_group_final_closure_decision_validator_v0_1`
- Status: `{payload['status']}`
- Target blockers: `support_contact`, `customer_support`, `sla`, `on_call_rotation`
- final_human_decision_recorded={str(payload['final_human_decision_recorded']).lower()}
- separate_matrix_update_request_ready={str(payload['separate_matrix_update_request_ready']).lower()}
- matrix_update_executed=false
- blocker_closure_authorized=false
- blockers_closed_by_validator=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_SUPPORT_GROUP_FINAL_CLOSURE_DECISION_VALIDATOR: PASS "
        f"status={payload['status']} "
        f"separate_matrix_update_request_ready={str(payload['separate_matrix_update_request_ready']).lower()} "
        "blockers_closed_by_validator=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
