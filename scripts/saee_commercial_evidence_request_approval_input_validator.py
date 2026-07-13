#!/usr/bin/env python3
"""Validate human approval input for commercial evidence request drafts.

This validator checks whether a human-filled approval input can move one
draft-only evidence request toward a separate evidence-collection or execution
request. It does not collect evidence, execute work, contact owners/customers
or vendors, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
DRAFT_PACKET_PATH = SPRINT_DIR / "evidence_request_draft_packet.local.json"
DEFAULT_INPUT_PATH = SPRINT_DIR / "evidence_request_approval_input.template.json"
DEFAULT_HUMAN_FILLED_INPUT_PATH = (
    SPRINT_DIR / "evidence_request_approval_input.human_filled.local.json"
)
OUTPUT_PATH = SPRINT_DIR / "evidence_request_approval_input_validation.local.json"
REPORT_PATH = SPRINT_DIR / "evidence_request_approval_input_validation.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md"
)

SELECTED_BLOCKER_IDS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]

ALLOWED_DECISIONS = {
    "hold",
    "approved_for_separate_evidence_collection_request",
    "approved_for_separate_execution_request",
}

APPROVAL_SCOPES = {
    "approved_for_separate_evidence_collection_request": "evidence_collection_only",
    "approved_for_separate_execution_request": (
        "implementation_and_evidence_collection_review"
    ),
}

FORBIDDEN_TRUE_KEYS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "owner_contacted_by_codex",
    "customer_data_collected",
    "customer_data_processed",
    "vendor_contacted",
    "payment_collected",
    "revenue_validated",
    "production_claim_added",
    "launch_claim_added",
    "customer_validation_claim_added",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR: "
            f"FAIL invalid JSON {path}: {exc}"
        ) from exc
    if not isinstance(value, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR: "
            f"FAIL {path} must contain an object"
        )
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_input_path() -> Path:
    if DEFAULT_HUMAN_FILLED_INPUT_PATH.exists():
        return DEFAULT_HUMAN_FILLED_INPUT_PATH
    return DEFAULT_INPUT_PATH


def draft_rows(packet: dict[str, Any]) -> list[dict[str, Any]]:
    rows = packet.get("request_drafts", [])
    if not isinstance(rows, list):
        return []
    return [row for row in rows if isinstance(row, dict)]


def build_template(packet: dict[str, Any]) -> dict[str, Any]:
    approval_inputs: list[dict[str, Any]] = []
    for draft in draft_rows(packet):
        approval_inputs.append(
            {
                "request_id": draft["request_id"],
                "blocker_id": draft["blocker_id"],
                "title": draft["title"],
                "owner_review_lane": draft["owner_review_lane"],
                "assigned_human_owner": "",
                "human_approval_reference": "",
                "approval_scope": "",
                "approval_decision": "hold",
                "evidence_collection_request_reference": "",
                "execution_request_reference": "",
                "owner_acknowledged_scope": False,
                "boundary_acknowledged": False,
                "notes": "",
            }
        )
    return {
        "template_type": "saee_commercial_evidence_request_approval_input",
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "source_request_draft_packet": rel(DRAFT_PACKET_PATH),
        "selected_blocker_ids": SELECTED_BLOCKER_IDS,
        "approval_inputs": approval_inputs,
        "boundary_review": {key: False for key in FORBIDDEN_TRUE_KEYS},
        "human_reviewer_name": "",
        "review_date": "",
        "review_notes": "",
    }


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    boundary_review = data.get("boundary_review", {})
    if not isinstance(boundary_review, dict):
        violations.append("boundary_review_missing_or_invalid")
        boundary_review = {}
    for key in FORBIDDEN_TRUE_KEYS:
        if data.get(key) is True or boundary_review.get(key) is True:
            violations.append(key)
    for key in [
        "blockers_closed_by_validator",
        "blockers_closed_by_approval_input",
        "blockers_ready_to_close",
    ]:
        if data.get(key) not in (None, False, 0, "", []):
            violations.append(key)
    return sorted(set(violations))


def approval_rows_by_request(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = data.get("approval_inputs", [])
    if not isinstance(rows, list):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and isinstance(row.get("request_id"), str):
            result[row["request_id"]] = row
    return result


def expected_request_ids(packet: dict[str, Any]) -> list[str]:
    return [str(row.get("request_id")) for row in draft_rows(packet)]


def invalid_decisions(data: dict[str, Any]) -> dict[str, str]:
    invalid: dict[str, str] = {}
    for request_id, row in approval_rows_by_request(data).items():
        decision = str(row.get("approval_decision", "")).strip()
        if decision not in ALLOWED_DECISIONS:
            invalid[request_id] = decision
    return invalid


def approval_missing_fields(
    data: dict[str, Any],
    packet: dict[str, Any],
) -> dict[str, list[str]]:
    rows = approval_rows_by_request(data)
    missing: dict[str, list[str]] = {}
    draft_ids = expected_request_ids(packet)
    for request_id in draft_ids:
        row = rows.get(request_id)
        if row is None:
            missing[request_id] = ["approval_input_row"]
            continue
        decision = str(row.get("approval_decision", "")).strip()
        if decision == "hold":
            continue
        row_missing: list[str] = []
        if decision not in APPROVAL_SCOPES:
            row_missing.append("approval_decision")
        else:
            required_scope = APPROVAL_SCOPES[decision]
            if str(row.get("approval_scope", "")).strip() != required_scope:
                row_missing.append("approval_scope")
            for field in ["assigned_human_owner", "human_approval_reference"]:
                if not str(row.get(field, "")).strip():
                    row_missing.append(field)
            if decision == "approved_for_separate_evidence_collection_request":
                if not str(row.get("evidence_collection_request_reference", "")).strip():
                    row_missing.append("evidence_collection_request_reference")
            if decision == "approved_for_separate_execution_request":
                if not str(row.get("execution_request_reference", "")).strip():
                    row_missing.append("execution_request_reference")
        if row.get("owner_acknowledged_scope") is not True:
            row_missing.append("owner_acknowledged_scope")
        if row.get("boundary_acknowledged") is not True:
            row_missing.append("boundary_acknowledged")
        if row_missing:
            missing[request_id] = row_missing
    return missing


def build_case_reviews(
    data: dict[str, Any],
    packet: dict[str, Any],
    missing_fields: dict[str, list[str]],
    invalid: dict[str, str],
) -> list[dict[str, Any]]:
    rows = approval_rows_by_request(data)
    draft_by_id = {str(row.get("request_id")): row for row in draft_rows(packet)}
    reviews: list[dict[str, Any]] = []
    for request_id in expected_request_ids(packet):
        draft = draft_by_id[request_id]
        row = rows.get(request_id, {})
        decision = str(row.get("approval_decision", "missing")).strip()
        reviews.append(
            {
                "request_id": request_id,
                "blocker_id": draft.get("blocker_id"),
                "title": draft.get("title"),
                "approval_decision": decision,
                "approval_scope": row.get("approval_scope", ""),
                "assigned_human_owner_present": bool(
                    str(row.get("assigned_human_owner", "")).strip()
                ),
                "human_approval_reference_present": bool(
                    str(row.get("human_approval_reference", "")).strip()
                ),
                "owner_acknowledged_scope": row.get("owner_acknowledged_scope") is True,
                "boundary_acknowledged": row.get("boundary_acknowledged") is True,
                "missing_fields": missing_fields.get(request_id, []),
                "invalid_decision": invalid.get(request_id, ""),
                "ready_for_separate_request": (
                    decision in APPROVAL_SCOPES
                    and request_id not in missing_fields
                    and request_id not in invalid
                ),
            }
        )
    return reviews


def build_validation(input_path: Path) -> dict[str, Any]:
    packet = read_json(DRAFT_PACKET_PATH)
    data = read_json(input_path)
    violations = boundary_violations(data)
    invalid = invalid_decisions(data)
    missing_fields = approval_missing_fields(data, packet)
    expected_ids = expected_request_ids(packet)
    rows = approval_rows_by_request(data)
    template_type_valid = (
        data.get("template_type") == "saee_commercial_evidence_request_approval_input"
    )
    selected_ids_match = data.get("selected_blocker_ids") == SELECTED_BLOCKER_IDS
    request_ids_match = list(rows) == expected_ids
    approved_rows = [
        (request_id, row)
        for request_id, row in rows.items()
        if str(row.get("approval_decision", "")).strip() in APPROVAL_SCOPES
    ]
    multiple_approval_violation = len(approved_rows) > 1
    if multiple_approval_violation:
        violations.append("multiple_approved_requests")
        violations = sorted(set(violations))
    approved_request_count = len(approved_rows)
    approved_decision = (
        str(approved_rows[0][1].get("approval_decision", "")).strip()
        if approved_request_count == 1
        else ""
    )
    approved_request_complete = (
        template_type_valid
        and selected_ids_match
        and request_ids_match
        and approved_request_count == 1
        and not missing_fields
        and not invalid
        and not violations
    )
    validation_status = (
        "stop"
        if violations or invalid
        else ("pass" if approved_request_complete else "hold")
    )
    input_path_value = rel(input_path) if input_path.is_relative_to(ROOT) else str(input_path)
    validation: dict[str, Any] = {
        "commercial_evidence_request_approval_input_validator_v0_1": True,
        "validator_type": "saee_commercial_evidence_request_approval_input_validator",
        "validator_version": "v0.1",
        "validation_scope": "local_human_filled_evidence_request_approval_pre_execution_check",
        "source_request_draft_packet": rel(DRAFT_PACKET_PATH),
        "input_path": input_path_value,
        "generated_by": "scripts/saee_commercial_evidence_request_approval_input_validator.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": validation_status,
        "approval_input_complete": approved_request_complete,
        "template_type_valid": template_type_valid,
        "selected_blocker_ids_match": selected_ids_match,
        "request_ids_match": request_ids_match,
        "selected_blocker_count": len(SELECTED_BLOCKER_IDS),
        "draft_request_count": len(expected_ids),
        "approved_request_count": approved_request_count,
        "approved_request_ids": [request_id for request_id, _ in approved_rows],
        "held_request_count": len(
            [
                row
                for row in rows.values()
                if str(row.get("approval_decision", "")).strip() == "hold"
            ]
        ),
        "ready_for_separate_evidence_collection_request": (
            approved_request_complete
            and approved_decision == "approved_for_separate_evidence_collection_request"
        ),
        "ready_for_separate_execution_request": (
            approved_request_complete
            and approved_decision == "approved_for_separate_execution_request"
        ),
        "missing_approval_fields": missing_fields,
        "invalid_approval_decisions": invalid,
        "boundary_violation_count": len(violations),
        "boundary_violations": violations,
        "request_decision_review": build_case_reviews(data, packet, missing_fields, invalid),
        "human_review_required": True,
        "separate_evidence_collection_request_required": True,
        "separate_execution_request_required": True,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blockers_closed_by_validator": 0,
        "blockers_ready_to_close": [],
        "next_action": (
            "If status is pass, create a separate human-approved evidence "
            "collection or execution request. This validator does not collect "
            "evidence, execute work, contact anyone, or close blockers."
        ),
    }
    for key in FORBIDDEN_TRUE_KEYS:
        validation[key] = False
    return validation


def list_missing(value: dict[str, list[str]] | dict[str, str] | list[str]) -> str:
    if not value:
        return "- none"
    if isinstance(value, list):
        return "\n".join(f"- {item}" for item in value)
    return "\n".join(
        f"- {key}: {', '.join(fields) if isinstance(fields, list) else fields}"
        for key, fields in value.items()
    )


def report_markdown(validation: dict[str, Any]) -> str:
    rows = []
    for row in validation["request_decision_review"]:
        rows.append(
            "| {request_id} | {blocker_id} | {approval_decision} | "
            "{ready_for_separate_request} | {missing_fields} |".format(
                request_id=row["request_id"],
                blocker_id=row["blocker_id"],
                approval_decision=row["approval_decision"],
                ready_for_separate_request=str(
                    row["ready_for_separate_request"]
                ).lower(),
                missing_fields=", ".join(row["missing_fields"]) or "none",
            )
        )
    return f"""# SAEE Commercial Evidence Request Approval Input Validation

commercial_evidence_request_approval_input_validator_v0_1: true
status: {validation['status']}
validation_scope: {validation['validation_scope']}
approval_input_complete: {str(validation['approval_input_complete']).lower()}
approved_request_count: {validation['approved_request_count']}
ready_for_separate_evidence_collection_request: {str(validation['ready_for_separate_evidence_collection_request']).lower()}
ready_for_separate_execution_request: {str(validation['ready_for_separate_execution_request']).lower()}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_validator: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This report validates human-filled approval input for draft-only commercial
evidence requests. It checks whether one draft can proceed to a separate
human-approved evidence collection or execution request.

## Decision Review

| Request ID | Blocker | Approval Decision | Ready For Separate Request | Missing Fields |
| --- | --- | --- | --- | --- |
{chr(10).join(rows)}

## Missing Approval Fields

{list_missing(validation['missing_approval_fields'])}

## Invalid Approval Decisions

{list_missing(validation['invalid_approval_decisions'])}

## Boundary Violations

{list_missing(validation['boundary_violations'])}

## Boundary

This validator is a local pre-execution check only. Passing validation means
only that a separate human-approved evidence collection or execution request may
be opened. It does not authorize collection, execution, owner contact, customer
contact, vendor contact, blocker closure, launch, or production-readiness
claims.
"""


def write_static_docs() -> None:
    TOP_DOC.write_text(
        """# SAEE Commercial Evidence Request Approval Input Validator v0.1

commercial_evidence_request_approval_input_validator_v0_1: true
status: hold
validator_scope: local_human_filled_evidence_request_approval_pre_execution_check
selected_blocker_count: 5
draft_request_count: 5
approval_input_complete: false
approved_request_count: 0
ready_for_separate_evidence_collection_request: false
ready_for_separate_execution_request: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_validator: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This validator checks whether a human-filled approval input for an ERD draft is
complete enough to open a separate evidence collection or execution request.

## Entrypoints

- input template: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input.template.json`
- validation output: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_validation.local.json`
- validation report: `phase_b_product/commercial_readiness/commercial_next_evidence_sprint/evidence_request_approval_input_validation.md`
- script: `scripts/saee_commercial_evidence_request_approval_input_validator.py`
- smoke: `scripts/saee_commercial_evidence_request_approval_input_validator_smoke.py`

## Boundary

This is local input validation only. It does not collect evidence, execute work,
assign or contact owners, contact customers or vendors, close blockers, launch
product, modify runtime/backend/kernel/API schema/private core, or claim
production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Commercial Evidence Request Approval Input Validator Recommendation Gate

answer: conditional

recommend_for_evidence_request_approval_input_validation: true
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_owner_contact: false
recommend_for_customer_contact: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The validator is useful for checking whether human approval input for one draft
evidence request is complete before any separate evidence collection or
execution request is opened. It is not an evidence runner and does not authorize
execution.

## Boundary

- approval_input_complete: false
- approved_request_count: 0
- ready_for_separate_evidence_collection_request: false
- ready_for_separate_execution_request: false
- evidence_collection_authorized: false
- execution_authorized: false
- owner_contacted_by_codex: false
- customer_contacted: false
- vendor_contacted: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_validator: 0
""",
        encoding="utf-8",
    )


def write_readme_note() -> None:
    readme = SPRINT_DIR / "README.md"
    text = readme.read_text(encoding="utf-8") if readme.exists() else "# Commercial Next Evidence Sprint\n"
    note = (
        "\nThe evidence request approval input validator checks a human-filled "
        "approval input for the ERD draft packet. It can mark input ready for a "
        "separate evidence collection or execution request, but it does not "
        "authorize collection, execute work, contact anyone, or close blockers.\n"
    )
    if "evidence request approval input validator" not in text:
        text += note
    files_marker = "- `evidence_request_draft_boundary_audit.md`\n"
    additions = (
        "- `evidence_request_approval_input.template.json`\n"
        "- `evidence_request_approval_input_validation.local.json`\n"
        "- `evidence_request_approval_input_validation.md`\n"
    )
    if files_marker in text and "evidence_request_approval_input.template.json" not in text:
        text = text.replace(files_marker, files_marker + additions)
    readme.write_text(text, encoding="utf-8")


def run(input_path: Path, *, json_only: bool = False) -> dict[str, Any]:
    packet = read_json(DRAFT_PACKET_PATH)
    template = build_template(packet)
    write_json(DEFAULT_INPUT_PATH, template)
    validation = build_validation(input_path)
    write_json(OUTPUT_PATH, validation)
    REPORT_PATH.write_text(report_markdown(validation), encoding="utf-8")
    write_static_docs()
    write_readme_note()
    if json_only:
        print(json.dumps(validation, sort_keys=True))
    else:
        print(
            "SAEE_COMMERCIAL_EVIDENCE_REQUEST_APPROVAL_INPUT_VALIDATOR: "
            f"PASS status={validation['status']} "
            f"approval_input_complete={str(validation['approval_input_complete']).lower()} "
            f"approved_request_count={validation['approved_request_count']} "
            "ready_for_separate_evidence_collection_request="
            f"{str(validation['ready_for_separate_evidence_collection_request']).lower()} "
            "ready_for_separate_execution_request="
            f"{str(validation['ready_for_separate_execution_request']).lower()} "
            "evidence_collection_authorized=false execution_authorized=false "
            "blockers_closed_by_validator=0 production_ready=false"
        )
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(default_input_path()))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    input_path = Path(args.input)
    if not input_path.is_absolute():
        input_path = ROOT / input_path
    if input_path == DEFAULT_INPUT_PATH and not input_path.exists():
        packet = read_json(DRAFT_PACKET_PATH)
        write_json(DEFAULT_INPUT_PATH, build_template(packet))
    run(input_path, json_only=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
