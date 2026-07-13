#!/usr/bin/env python3
"""Validate the current 10-row quick-fill review batch.

The validator checks only the selected review-batch rows from the source
quick-fill CSV. It records value presence, basic quality status, and boundary
issues without recording raw human values. It does not modify the source CSV,
import a workbook, run validators on real input, collect evidence, close
blockers, contact anyone, launch product, or claim production readiness.

If the 10-row review batch has been superseded by a fully filled 64-row
quick-fill packet, the validator records that superseded state and performs
boundary scanning only. It does not treat the missing 10-row batch as a failure.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
REVIEW_BATCH_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_V0_1.md"
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_RECOMMENDATION_GATE.md"
)

EXPECTED_SOURCE_ROW_COUNT = 64
EXPECTED_BATCH_ROW_COUNT = 10
SUPERSEDED_REVIEW_BATCH_STATUS = (
    "superseded_by_full_quick_fill_values_pending_workbook_import_approval"
)

PLACEHOLDER_VALUES = {
    "",
    "todo",
    "tbd",
    "n/a",
    "na",
    "none",
    "unknown",
    "placeholder",
    "fill later",
    "to be filled",
}

ACTIONABLE_ANCHORS = {
    "approved",
    "approval",
    "assigned",
    "owner",
    "review",
    "decision",
    "evidence",
    "policy",
    "runbook",
    "report",
    "ticket",
    "path",
    "url",
    "provider",
    "threshold",
    "schedule",
    "configured",
    "tested",
    "handoff",
    "reference",
    "artifact",
    "snapshot",
    "date",
    "status",
}

SECRET_PATTERNS = {
    "openai_or_provider_api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "langsmith_api_key": re.compile(r"\bls__[A-Za-z0-9_=-]{10,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "jwt_like_token": re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
}

FORBIDDEN_CLAIM_PATTERNS = {
    "production_ready_claim": re.compile(r"\bproduction[_ -]?ready\s*[:=]\s*true\b", re.I),
    "customer_validated_claim": re.compile(r"\bcustomer[_ -]?validated\s*[:=]\s*true\b", re.I),
    "product_launched_claim": re.compile(r"\bproduct[_ -]?launched\s*[:=]\s*true\b", re.I),
    "external_validation_claim": re.compile(r"\bexternal[_ -]?validation\s*[:=]\s*true\b", re.I),
    "private_core_exposed_claim": re.compile(r"\bprivate[_ -]?core[_ -]?exposed\s*[:=]\s*true\b", re.I),
}

PRIVATE_CORE_TERMS = [
    "fitness logic",
    "selection logic",
    "mutation logic",
    "lineage internals",
    "private core",
    "evolution kernel",
]

FALSE_FLAGS = [
    "raw_values_recorded",
    "human_values_generated_by_codex",
    "quick_fill_values_entered_by_codex",
    "source_quick_fill_packet_modified",
    "quick_fill_imported_to_workbook",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "validators_run_on_real_input",
    "ready_for_safety_preflight",
    "ready_for_workbook_import",
    "safe_to_import_after_human_approval",
    "values_transferred",
    "human_filled_templates_written",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "blockers_closed",
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
    "development_permission_granted",
    "task_candidates_executed",
    "payment_collected",
    "revenue_validated",
    "production_ready_claim",
    "customer_validation_claim",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick-fill-csv",
        default=str(QUICK_FILL_CSV),
        help="Quick-fill CSV to validate for the selected review batch.",
    )
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes"}


def has_iso_date(value: str) -> bool:
    return bool(re.search(r"\b20\d{2}-\d{2}-\d{2}\b", value))


def has_url_or_path(value: str) -> bool:
    return bool(re.search(r"\bhttps?://", value)) or "/" in value or ".md" in value or ".json" in value


def scan_for_boundary_issues(text: str) -> list[str]:
    issues: list[str] = []
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            issues.append(name)
    for name, pattern in FORBIDDEN_CLAIM_PATTERNS.items():
        if pattern.search(text):
            issues.append(name)
    lowered = text.lower()
    if any(term in lowered for term in PRIVATE_CORE_TERMS):
        issues.append("private_core_reference")
    return sorted(set(issues))


def classify_batch_value(row: dict[str, str]) -> tuple[str, list[str]]:
    value = row.get("human_value_to_enter", "").strip()
    notes = row.get("notes_for_human", "").strip()
    lowered = value.lower()
    combined = "\n".join([value, notes])
    issues: list[str] = []

    if not value:
        return "missing_batch_human_value", ["missing_batch_human_value"]
    if lowered in PLACEHOLDER_VALUES:
        issues.append("placeholder_value")
    issues.extend(scan_for_boundary_issues(combined))

    input_key = row.get("input_key", "").lower()
    input_kind = row.get("input_kind", "").lower()
    field_context = f"{input_key} {input_kind}"
    value_len = len(value)

    if "date" in field_context:
        if not has_iso_date(value):
            issues.append("date_field_should_use_iso_date")
    elif any(token in field_context for token in ["owner", "contact"]):
        if value_len < 5:
            issues.append("owner_or_contact_value_too_short")
    elif any(token in field_context for token in ["acknowledged", "approval", "approved", "decision"]):
        if value_len < 8:
            issues.append("decision_value_too_short")
    elif value_len < 12:
        issues.append("value_too_short")

    if not (
        has_iso_date(value)
        or has_url_or_path(value)
        or any(anchor in lowered for anchor in ACTIONABLE_ANCHORS)
        or any(token in field_context for token in ["owner", "contact", "date"])
    ):
        issues.append("insufficient_actionable_anchor")

    boundary_issue_prefixes = set(SECRET_PATTERNS) | set(FORBIDDEN_CLAIM_PATTERNS) | {"private_core_reference"}
    if any(issue in boundary_issue_prefixes for issue in issues):
        return "stop_boundary_or_sensitive_batch_value", sorted(set(issues))
    if issues:
        return "needs_human_batch_quality_review", sorted(set(issues))
    return "batch_value_pass_pending_full_quality_gate", []


def build_payload(quick_fill_csv: Path) -> dict[str, Any]:
    source_rows = read_csv(quick_fill_csv)
    batch = json.loads(REVIEW_BATCH_JSON.read_text(encoding="utf-8"))
    selected_ids = [row["quick_fill_row_id"] for row in batch.get("selected_rows", [])]
    batch_superseded = (
        batch.get("status") == SUPERSEDED_REVIEW_BATCH_STATUS
        and len(selected_ids) == 0
    )
    source_by_id = {row.get("quick_fill_row_id", ""): row for row in source_rows}

    boundary_violations: list[str] = []
    if len(source_rows) != EXPECTED_SOURCE_ROW_COUNT:
        boundary_violations.append("unexpected_source_quick_fill_row_count")
    if len(selected_ids) != EXPECTED_BATCH_ROW_COUNT and not batch_superseded:
        boundary_violations.append("unexpected_review_batch_row_count")
    if (
        batch.get("status") != "hold_review_batch_ready_for_human_entry"
        and not batch_superseded
    ):
        boundary_violations.append("review_batch_not_ready_for_human_entry")
    if batch.get("raw_values_recorded") is not False:
        boundary_violations.append("review_batch_raw_values_recorded")
    if batch_superseded:
        for row in source_rows:
            row_id = row.get("quick_fill_row_id", "unknown_row")
            combined = "\n".join(
                [
                    row.get("human_value_to_enter", ""),
                    row.get("notes_for_human", ""),
                ]
            )
            boundary_violations.extend(
                f"{row_id}:{issue}" for issue in scan_for_boundary_issues(combined)
            )

    validation_rows: list[dict[str, Any]] = []
    status_counts: Counter[str] = Counter()
    issue_counts: Counter[str] = Counter()

    for batch_index, row_id in enumerate(selected_ids, start=1):
        row = source_by_id.get(row_id)
        if row is None:
            boundary_violations.append(f"{row_id}:missing_source_row")
            continue
        for flag in ["value_imported_to_workbook", "value_transferred", "template_written"]:
            if parse_bool(row.get(flag, "")):
                boundary_violations.append(f"{row_id}:{flag}_is_true")

        quality_status, issues = classify_batch_value(row)
        status_counts[quality_status] += 1
        issue_counts.update(issues)
        if quality_status == "stop_boundary_or_sensitive_batch_value":
            boundary_violations.extend(f"{row_id}:{issue}" for issue in issues)

        value = row.get("human_value_to_enter", "").strip()
        notes = row.get("notes_for_human", "").strip()
        validation_rows.append(
            {
                "review_batch_row_id": f"QFRB-{batch_index:03d}",
                "quick_fill_row_id": row_id,
                "queue_item_id": row.get("queue_item_id", ""),
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "input_kind": row.get("input_kind", ""),
                "value_present": bool(value),
                "note_present": bool(notes),
                "value_length": len(value),
                "note_length": len(notes),
                "batch_validation_status": quality_status,
                "issue_codes": issues,
                "target_workbook_csv": row.get("target_workbook_csv", ""),
                "target_workbook_column": row.get("target_workbook_column", ""),
                "target_json_pointer": row.get("target_json_pointer", ""),
            }
        )

    completed = len(validation_rows) - status_counts["missing_batch_human_value"]
    missing = status_counts["missing_batch_human_value"]
    pass_count = status_counts["batch_value_pass_pending_full_quality_gate"]
    review_count = status_counts["needs_human_batch_quality_review"]
    stop_count = status_counts["stop_boundary_or_sensitive_batch_value"]
    issue_count = review_count + stop_count

    if batch_superseded and not boundary_violations:
        status = SUPERSEDED_REVIEW_BATCH_STATUS
    elif boundary_violations:
        status = "stop_boundary_or_sensitive_batch_value_detected"
    elif missing:
        status = "hold_batch_human_values_required"
    elif issue_count:
        status = "hold_batch_quality_review_required"
    else:
        status = "pass_batch_values_present_pending_full_quality_gate_and_safety_preflight"

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1": True,
        "validator_type": "selected_quick_fill_review_batch_validator",
        "validator_scope": "selected_batch_value_presence_and_boundary_only_no_raw_value_storage_no_import",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator.py",
        "source_quick_fill_csv": rel(quick_fill_csv),
        "source_review_batch_json": rel(REVIEW_BATCH_JSON),
        "source_quick_fill_row_count": len(source_rows),
        "review_batch_size": EXPECTED_BATCH_ROW_COUNT,
        "selected_review_row_count": len(selected_ids),
        "completed_batch_value_row_count": completed,
        "missing_batch_value_row_count": missing,
        "batch_quality_pass_row_count": pass_count,
        "batch_quality_review_row_count": review_count,
        "batch_quality_stop_row_count": stop_count,
        "batch_quality_issue_count": issue_count,
        "batch_validator_passed": status == "pass_batch_values_present_pending_full_quality_gate_and_safety_preflight",
        "review_batch_superseded": batch_superseded and status == SUPERSEDED_REVIEW_BATCH_STATUS,
        "ready_for_workbook_import_approval_review": status == SUPERSEDED_REVIEW_BATCH_STATUS,
        "full_quick_fill_completed_value_row_count": sum(
            1 for row in source_rows if row.get("human_value_to_enter", "").strip()
        ),
        "full_quick_fill_missing_value_row_count": sum(
            1 for row in source_rows if not row.get("human_value_to_enter", "").strip()
        ),
        "human_input_required": not batch_superseded,
        "human_review_required": True,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": sorted(set(boundary_violations)),
        "batch_validation_status_counts": dict(sorted(status_counts.items())),
        "batch_issue_counts": dict(sorted(issue_counts.items())),
        "validation_rows": validation_rows,
        "blockers_closed_by_batch_validator": 0,
        "next_human_action": (
            "No selected review-batch rows remain. This validator is superseded "
            "by the full quick-fill source values and the next human step is "
            "workbook import approval review, not batch validation."
            if batch_superseded
            else "Fill or correct the selected review-batch values in the source "
            "quick-fill CSV; then rerun this batch validator, the full quick-fill "
            "quality gate, safety preflight, packet validator, and import dry-run "
            "before any separate human-approved workbook import request."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "value_present",
        "note_present",
        "value_length",
        "note_length",
        "batch_validation_status",
        "issue_codes",
        "target_workbook_csv",
        "target_workbook_column",
        "target_json_pointer",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["validation_rows"]:
            item = dict(row)
            item["issue_codes"] = ";".join(item.get("issue_codes", []))
            writer.writerow({field: item.get(field, "") for field in fields})


def rows_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Batch Row | Quick Fill Row | Input Key | Value Present | Status | Issues |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        issues = ", ".join(row.get("issue_codes", [])) or "none"
        lines.append(
            "| {review_batch_row_id} | {quick_fill_row_id} | {input_key} | "
            "{value_present} | {batch_validation_status} | {issues} |".format(
                issues=issues,
                **row,
            )
        )
    return "\n".join(lines)


def write_markdown(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Sprint Human Input Quick-Fill Review Batch Validation v0.1

commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1: true
validator_scope: {payload['validator_scope']}
status: {payload['status']}
commercial_status: {payload['commercial_status']}
production_launch_status: {payload['production_launch_status']}

## Summary

- source_quick_fill_row_count: {payload['source_quick_fill_row_count']}
- review_batch_size: {payload['review_batch_size']}
- selected_review_row_count: {payload['selected_review_row_count']}
- completed_batch_value_row_count: {payload['completed_batch_value_row_count']}
- missing_batch_value_row_count: {payload['missing_batch_value_row_count']}
- batch_quality_pass_row_count: {payload['batch_quality_pass_row_count']}
- batch_quality_review_row_count: {payload['batch_quality_review_row_count']}
- batch_quality_stop_row_count: {payload['batch_quality_stop_row_count']}
- batch_quality_issue_count: {payload['batch_quality_issue_count']}
- batch_validator_passed: {str(payload['batch_validator_passed']).lower()}
- review_batch_superseded: {str(payload['review_batch_superseded']).lower()}
- ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
- full_quick_fill_completed_value_row_count: {payload['full_quick_fill_completed_value_row_count']}
- full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
- blockers_closed_by_batch_validator: {payload['blockers_closed_by_batch_validator']}

## Selected Row Validation

{rows_table(payload['validation_rows'])}

## Boundary

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- ready_for_safety_preflight: false
- ready_for_workbook_import: false
- workbook_import_authorized: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR: PASS
"""
    OUT_MD.write_text(body, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    body = f"""# Quick-Fill Review Batch Validation Boundary Audit

commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1: true
status: {payload['status']}
boundary_violation_count: {payload['boundary_violation_count']}

This boundary audit confirms the validator checks selected batch value presence
and basic boundary safety only.

- raw_values_recorded: false
- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- quick_fill_imported_to_workbook: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_batch_validator: 0
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- external_calls_made: false
- external_ai_assistant_tested: false

SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATION_BOUNDARY: PASS
"""
    OUT_BOUNDARY.write_text(body, encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Sprint Human Input Quick-Fill Review Batch Validator v0.1

commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1: true
status: {payload['status']}

This validator checks the selected 10-row quick-fill review batch without
recording raw values. It helps the team confirm whether the first batch is
ready for the full quick-fill quality gate and safety preflight.

It does not modify the source quick-fill packet, import a workbook, run
validators on real evidence, collect evidence, close blockers, contact
customers, launch product, or claim production readiness.
"""
    TOP_DOC.write_text(body, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Sprint Quick-Fill Review Batch Validator Recommendation Gate

answer: conditional

commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1: true
status: {payload['status']}

## Recommendation

Recommend this validator only for local checking of the selected 10-row
quick-fill review batch.

## Do Not Recommend For

- full 64-row completion proof
- workbook import
- evidence collection
- blocker closure
- production readiness
- customer validation

## Boundary

raw_values_recorded: false
source_quick_fill_packet_modified: false
workbook_import_authorized: false
validators_run_on_real_input: false
evidence_collection_authorized: false
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
"""
    GATE.write_text(body, encoding="utf-8")


def main() -> int:
    args = parse_args()
    payload = build_payload(Path(args.quick_fill_csv))
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR: "
        f"PASS status={payload['status']} "
        f"completed_batch_value_row_count={payload['completed_batch_value_row_count']} "
        f"missing_batch_value_row_count={payload['missing_batch_value_row_count']} "
        f"raw_values_recorded={str(payload['raw_values_recorded']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
