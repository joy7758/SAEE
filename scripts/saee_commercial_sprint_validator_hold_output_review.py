#!/usr/bin/env python3
"""Review validator hold outputs without executing evidence builders.

This local review layer reads the five validator outputs from the commercial
sprint validator execution run and extracts the missing input/evidence fields
that keep each validator at hold. It does not fill values, infer evidence,
run evidence builders, close blockers, contact anyone, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

RUN_JSON = SPRINT_DIR / "commercial_sprint_validator_execution_run.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_validator_hold_output_review.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_validator_hold_output_review.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_validator_hold_output_review.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_validator_hold_output_review_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW_GATE.md"

FALSE_FLAGS = [
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
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "real_evidence_created",
    "payment_collected",
    "revenue_validated",
]

MISSING_KEYS = [
    "missing_metadata_fields",
    "missing_evidence_review",
    "missing_source_notes",
    "missing_contact_slot_requirements",
    "missing_review_artifacts",
    "missing_policy_evidence_review",
    "missing_policy_slots",
    "missing_monitoring_slots",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_VALIDATOR_HOLD_OUTPUT_REVIEW: FAIL {rel(path)} must be object")
    return data


def list_value(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key, [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def build_payload() -> dict[str, Any]:
    run = read_json(RUN_JSON)
    results = run.get("validation_results", [])
    if not isinstance(results, list):
        raise SystemExit("SAEE_VALIDATOR_HOLD_OUTPUT_REVIEW: FAIL validation_results must be list")

    review_rows: list[dict[str, Any]] = []
    total_missing_metadata = 0
    total_missing_evidence = 0
    total_missing_source_notes = 0
    boundary_violations: list[str] = []

    for result in results:
        if not isinstance(result, dict):
            continue
        output_path = ROOT / str(result.get("validation_output", ""))
        validation = read_json(output_path)
        missing = {key: list_value(validation, key) for key in MISSING_KEYS}
        missing_metadata = missing["missing_metadata_fields"]
        evidence_items = (
            missing["missing_evidence_review"]
            or missing["missing_review_artifacts"]
            or missing["missing_policy_evidence_review"]
            or missing["missing_policy_slots"]
            or missing["missing_monitoring_slots"]
        )
        source_notes = missing["missing_source_notes"]
        total_missing_metadata += len(missing_metadata)
        total_missing_evidence += len(evidence_items)
        total_missing_source_notes += len(source_notes)

        if int(validation.get("boundary_violation_count", 0) or 0) > 0:
            boundary_violations.append(f"{result.get('blocker_id')}:boundary_violation_count_nonzero")
        for flag in FALSE_FLAGS:
            if validation.get(flag) is True:
                boundary_violations.append(f"{result.get('blocker_id')}:{flag}_true")

        review_rows.append(
            {
                "sequence_id": result.get("sequence_id"),
                "blocker_id": result.get("blocker_id"),
                "validator_key": result.get("validator_key"),
                "validation_status": validation.get("validation_status"),
                "builder_ready": validation.get("builder_ready") is True,
                "input_complete": validation.get("input_complete") is True,
                "metadata_complete": validation.get("metadata_complete") is True,
                "source_notes_complete": validation.get("source_notes_complete") is True,
                "evidence_review_complete": validation.get("evidence_review_complete") is True
                or validation.get("policy_evidence_review_complete") is True,
                "missing_metadata_fields": missing_metadata,
                "missing_evidence_items": evidence_items,
                "missing_source_notes": source_notes,
                "missing_contact_slot_requirements": missing["missing_contact_slot_requirements"],
                "missing_metadata_field_count": len(missing_metadata),
                "missing_evidence_item_count": len(evidence_items),
                "missing_source_note_count": len(source_notes),
                "human_filled_input_target": result.get("human_filled_input_target"),
                "validation_output": result.get("validation_output"),
                "next_required_action": (
                    "Complete the missing metadata fields, evidence review items, and "
                    "source notes in the human-filled input target, then rerun this "
                    "validator. Evidence builder execution remains a separate request "
                    "after validation passes."
                ),
                "evidence_builder_execution_allowed": False,
                "blocker_closure_allowed": False,
            }
        )

    hold_count = sum(1 for row in review_rows if row["validation_status"] == "hold")
    builder_ready_count = sum(1 for row in review_rows if row["builder_ready"])
    if boundary_violations:
        status = "stop_boundary_violation"
        next_human_action = (
            "Resolve the validator boundary violations before any further commercial "
            "readiness action."
        )
    elif hold_count > 0:
        status = "hold_missing_validator_input_evidence_reviewed"
        next_human_action = (
            "Fill the missing metadata fields, evidence review items, and source "
            "notes listed in this review for the five human-filled input targets. "
            "Then rerun the local validators. Do not run evidence builders or close "
            "blockers until a validator passes and a separate execution request is made."
        )
    else:
        status = "validators_passed_evidence_builder_request_required"
        next_human_action = (
            "All five local input validators pass. Evidence builders and blocker "
            "closure still require a separate explicit human-approved execution "
            "request."
        )

    payload: dict[str, Any] = {
        "commercial_sprint_validator_hold_output_review_v0_1": True,
        "review_type": "local_validator_hold_output_review_no_execution",
        "status": status,
        "source_validator_execution_run": rel(RUN_JSON),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_validator_hold_output_review.py",
        "validator_outputs_reviewed_count": len(review_rows),
        "validator_hold_count": hold_count,
        "validator_pass_count": sum(1 for row in review_rows if row["validation_status"] == "pass"),
        "validator_stop_count": sum(1 for row in review_rows if row["validation_status"] == "stop"),
        "builder_ready_count": builder_ready_count,
        "total_missing_metadata_field_count": total_missing_metadata,
        "total_missing_evidence_item_count": total_missing_evidence,
        "total_missing_source_note_count": total_missing_source_notes,
        "missing_input_completion_required": hold_count > 0,
        "rerun_validators_after_completion_required": hold_count > 0,
        "separate_evidence_builder_request_required": True,
        "evidence_builder_execution_allowed": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_review": 0,
        "boundary_violation_count": len(set(boundary_violations)),
        "boundary_violations": sorted(set(boundary_violations)),
        "review_rows": review_rows,
        "next_human_action": next_human_action,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        fieldnames = [
            "sequence_id",
            "blocker_id",
            "validation_status",
            "builder_ready",
            "missing_metadata_field_count",
            "missing_evidence_item_count",
            "missing_source_note_count",
            "human_filled_input_target",
            "validation_output",
            "evidence_builder_execution_allowed",
            "blocker_closure_allowed",
        ]
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in payload["review_rows"]:
            writer.writerow(
                {
                    key: json.dumps(row.get(key), ensure_ascii=False)
                    if isinstance(row.get(key), list)
                    else row.get(key)
                    for key in fieldnames
                }
            )

    rows_md = "\n".join(
        "| {sequence_id} | {blocker_id} | {validation_status} | {builder_ready} | {missing_metadata_field_count} | {missing_evidence_item_count} | {missing_source_note_count} | `{human_filled_input_target}` |".format(
            **row
        )
        for row in payload["review_rows"]
    )
    missing_sections = []
    for row in payload["review_rows"]:
        missing_sections.append(
            "### {blocker_id}\n\n"
            "- missing_metadata_fields: {metadata}\n"
            "- missing_evidence_items: {evidence}\n"
            "- missing_source_notes: {source_notes}\n"
            "- next_required_action: {next_action}\n".format(
                blocker_id=row["blocker_id"],
                metadata=", ".join(row["missing_metadata_fields"]) or "none",
                evidence=", ".join(row["missing_evidence_items"]) or "none",
                source_notes=", ".join(row["missing_source_notes"]) or "none",
                next_action=row["next_required_action"],
            )
        )
    if payload["validator_hold_count"]:
        summary = (
            'The five local validators ran and at least one returned `hold`. This '
            'review lists the missing human input and evidence-review items. It '
            'does not fill those items and does not authorize evidence builders '
            'or blocker closure.'
        )
    else:
        summary = (
            'The five local validators ran and all returned `pass`. This review '
            'records that the missing input blocker has been cleared at the '
            'validator-input layer. Evidence builders and blocker closure still '
            'require a separate explicit human-approved execution request.'
        )

    markdown = f"""# Commercial Sprint Validator Hold Output Review v0.1

commercial_sprint_validator_hold_output_review_v0_1: true
review_type: {payload['review_type']}
status: {payload['status']}
validator_outputs_reviewed_count: {payload['validator_outputs_reviewed_count']}
validator_hold_count: {payload['validator_hold_count']}
builder_ready_count: {payload['builder_ready_count']}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
missing_input_completion_required: {str(payload['missing_input_completion_required']).lower()}
rerun_validators_after_completion_required: {str(payload['rerun_validators_after_completion_required']).lower()}
separate_evidence_builder_request_required: true
evidence_builder_execution_allowed: false
evidence_collection_authorized: false
blocker_closure_authorized: false
blockers_closed_by_review: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Summary

{summary}

## Review Table

| Sequence | Blocker | Status | Builder Ready | Missing Metadata | Missing Evidence | Missing Source Notes | Human Input Target |
| --- | --- | --- | --- | --- | --- | --- | --- |
{rows_md}

## Missing Input Details

{chr(10).join(missing_sections)}

## Next Human Action

{payload['next_human_action']}

## Boundary

No runtime, backend, kernel, API schema, landing interaction, or private core was
modified. No customer or vendor was contacted. No external service was called.
No evidence builder was executed. No blocker was closed. No production-readiness
claim was added.
"""
    for path in [OUT_MD, TOP_DOC]:
        path.write_text(markdown, encoding="utf-8")
    OUT_BOUNDARY.write_text(
        f"""# Commercial Sprint Validator Hold Output Review Boundary Audit

commercial_sprint_validator_hold_output_review_v0_1: true
status: boundary_safe
boundary_violation_count: {payload['boundary_violation_count']}
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
evidence_builder_executed: false
evidence_collection_authorized: false
blocker_closure_authorized: false
blockers_closed_by_review: 0

This audit confirms the review reads validator outputs only. It does not modify
SAEE runtime, backend, kernel, API schema, private core, or product behavior.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Sprint Validator Hold Output Review Gate

answer: {payload['status']}

reason: The five validators ran locally. validator_pass_count={payload['validator_pass_count']},
validator_hold_count={payload['validator_hold_count']}, builder_ready_count={payload['builder_ready_count']}.
This review does not authorize evidence builders or blocker closure.

boundary:
  evidence_builder_execution_allowed: false
  evidence_collection_authorized: false
  blocker_closure_authorized: false
  production_ready: false
  customer_validated: false
  product_launched: false
  private_core_exposed: false

next_action: {payload['next_human_action']}
""",
        encoding="utf-8",
    )


def main() -> int:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_VALIDATOR_HOLD_OUTPUT_REVIEW: PASS "
        f"status={payload['status']} "
        f"validator_hold_count={payload['validator_hold_count']} "
        "evidence_builder_execution_allowed=false production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
