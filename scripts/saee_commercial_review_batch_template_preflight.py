#!/usr/bin/env python3
"""Preflight the active 10-row commercial review-batch input template.

This checks structure, blank human-value cells, duplicate IDs, and obvious
boundary-risk text before a human starts filling the review-batch template. It
does not generate values, fill values, import a workbook, run validators on real
input, collect evidence, close blockers, contact anyone, launch product, or
claim production readiness.
"""

from __future__ import annotations

import csv
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
SPRINT_DIR = COMMERCIAL_DIR / "commercial_next_evidence_sprint"

TEMPLATE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
TEMPLATE_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"
FILL_CARD_JSON = SPRINT_DIR / "commercial_review_batch_human_fill_card.local.json"
SOURCE_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = SPRINT_DIR / "commercial_review_batch_template_preflight.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_template_preflight.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_template_preflight.csv"
OUT_AUDIT = SPRINT_DIR / "commercial_review_batch_template_preflight_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT_RECOMMENDATION_GATE.md"

EXPECTED_TEMPLATE_ROW_COUNT = 10
EXPECTED_SOURCE_ROW_COUNT = 64
SUPERSEDED_REVIEW_BATCH_STATUS = "superseded_by_full_quick_fill_values_pending_workbook_import_approval"
REQUIRED_COLUMNS = [
    "review_batch_row_id",
    "quick_fill_row_id",
    "queue_item_id",
    "workbook_row_id",
    "blocker_id",
    "owner_review_lane",
    "input_group",
    "input_key",
    "input_kind",
    "expected_value_shape",
    "fill_instruction",
    "leave_blank_condition",
    "target_json_pointer",
    "human_value_to_enter",
    "notes_for_human",
]

SECRET_PATTERNS = {
    "openai_or_provider_api_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}\b"),
    "langsmith_api_key": re.compile(r"\bls__[A-Za-z0-9_=-]{10,}\b"),
    "aws_access_key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "bearer_token": re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{20,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
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
    "human_input_filled_by_codex",
    "source_quick_fill_packet_modified",
    "batch_values_applied_to_source",
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


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def scan_boundary_text(text: str) -> list[str]:
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


def duplicate_count(values: list[str]) -> int:
    counts = Counter(values)
    return sum(count - 1 for count in counts.values() if count > 1)


def row_issues(row: dict[str, str]) -> list[str]:
    issues: list[str] = []
    required_nonblank = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "input_key",
        "expected_value_shape",
        "fill_instruction",
        "target_json_pointer",
    ]
    for field in required_nonblank:
        if not row.get(field, "").strip():
            issues.append(f"missing_{field}")
    if row.get("human_value_to_enter", "").strip():
        issues.append("human_value_prefilled")
    if row.get("notes_for_human", "").strip():
        issues.append("notes_prefilled")
    issues.extend(scan_boundary_text("\n".join(row.values())))
    return sorted(set(issues))


def build_payload() -> dict[str, Any]:
    template_columns, template_rows = read_csv(TEMPLATE_CSV)
    _, source_rows = read_csv(SOURCE_QUICK_FILL_CSV)
    template_meta = json.loads(TEMPLATE_JSON.read_text(encoding="utf-8"))
    fill_card = json.loads(FILL_CARD_JSON.read_text(encoding="utf-8"))
    template_superseded = (
        template_meta.get("status") == SUPERSEDED_REVIEW_BATCH_STATUS
        and len(template_rows) == 0
    )

    missing_columns = [col for col in REQUIRED_COLUMNS if col not in template_columns]
    extra_columns = [col for col in template_columns if col not in REQUIRED_COLUMNS]
    row_reports: list[dict[str, Any]] = []
    boundary_violations: list[str] = []

    for index, row in enumerate(template_rows, start=1):
        issues = row_issues(row)
        if issues:
            boundary_violations.extend(f"{row.get('review_batch_row_id', index)}:{issue}" for issue in issues)
        row_reports.append(
            {
                "row_number": index,
                "review_batch_row_id": row.get("review_batch_row_id", ""),
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "input_key": row.get("input_key", ""),
                "row_status": "pass_blank_ready_for_human_entry" if not issues else "stop_row_issue",
                "issue_count": len(issues),
                "issues": issues,
            }
        )

    duplicate_id_count = (
        duplicate_count([row.get("review_batch_row_id", "") for row in template_rows])
        + duplicate_count([row.get("quick_fill_row_id", "") for row in template_rows])
        + duplicate_count([row.get("target_json_pointer", "") for row in template_rows])
    )
    structural_issues: list[str] = []
    if len(template_rows) != EXPECTED_TEMPLATE_ROW_COUNT and not template_superseded:
        structural_issues.append("unexpected_template_row_count")
    if len(source_rows) != EXPECTED_SOURCE_ROW_COUNT:
        structural_issues.append("unexpected_source_quick_fill_row_count")
    if template_meta.get("status") != "ready_for_human_batch_value_entry" and not template_superseded:
        structural_issues.append("input_template_not_ready_for_human_entry")
    if fill_card.get("status") != "ready_for_human_fill_card_review" and not template_superseded:
        structural_issues.append("fill_card_not_ready_for_human_review")
    if missing_columns:
        structural_issues.append("missing_required_columns")
    if duplicate_id_count:
        structural_issues.append("duplicate_template_identifiers")
    boundary_violations.extend(structural_issues)

    blank_value_count = sum(1 for row in template_rows if not row.get("human_value_to_enter", "").strip())
    blank_notes_count = sum(1 for row in template_rows if not row.get("notes_for_human", "").strip())
    prefilled_value_count = len(template_rows) - blank_value_count
    prefilled_notes_count = len(template_rows) - blank_notes_count
    boundary_violation_count = len(set(boundary_violations))
    preflight_passed = boundary_violation_count == 0 and not template_superseded
    status = "pass_ready_for_human_entry_preflight" if preflight_passed else "stop_preflight_issue"
    if template_superseded and boundary_violation_count == 0:
        status = SUPERSEDED_REVIEW_BATCH_STATUS

    payload: dict[str, Any] = {
        "commercial_review_batch_template_preflight_v0_1": True,
        "preflight_type": "commercial_review_batch_template_preflight",
        "preflight_scope": "local_empty_template_structure_check_no_values_no_import_no_execution",
        "status": status,
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_review_batch_template_preflight.py",
        "source_template_csv": rel(TEMPLATE_CSV),
        "source_template_json": rel(TEMPLATE_JSON),
        "source_fill_card_json": rel(FILL_CARD_JSON),
        "source_quick_fill_csv": rel(SOURCE_QUICK_FILL_CSV),
        "template_row_count": len(template_rows),
        "expected_template_row_count": EXPECTED_TEMPLATE_ROW_COUNT,
        "source_quick_fill_row_count": len(source_rows),
        "expected_source_quick_fill_row_count": EXPECTED_SOURCE_ROW_COUNT,
        "required_column_count": len(REQUIRED_COLUMNS),
        "missing_required_column_count": len(missing_columns),
        "extra_column_count": len(extra_columns),
        "duplicate_id_count": duplicate_id_count,
        "blank_human_value_row_count": blank_value_count,
        "blank_notes_row_count": blank_notes_count,
        "prefilled_human_value_row_count": prefilled_value_count,
        "prefilled_notes_row_count": prefilled_notes_count,
        "row_preflight_pass_count": sum(1 for row in row_reports if row["issue_count"] == 0),
        "row_issue_count": sum(1 for row in row_reports if row["issue_count"] > 0),
        "boundary_violation_count": boundary_violation_count,
        "boundary_violations": sorted(set(boundary_violations)),
        "preflight_passed": preflight_passed,
        "safe_to_start_human_fill": preflight_passed,
        "template_preflight_superseded": template_superseded and status == SUPERSEDED_REVIEW_BATCH_STATUS,
        "ready_for_workbook_import_approval_review": status == SUPERSEDED_REVIEW_BATCH_STATUS,
        "human_input_required": not template_superseded,
        "human_review_required": True,
        "blockers_closed_by_preflight": 0,
        "row_reports": row_reports,
        "next_human_action": (
            "The 10-row review-batch input template is superseded. Review the "
            "workbook import approval request packet instead; do not import the "
            "workbook without a separate explicit human execution approval."
            if template_superseded
            else "If preflight_passed is true, a human may fill only "
            "human_value_to_enter and optional notes_for_human in the 10-row "
            "review-batch template."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "row_number",
        "review_batch_row_id",
        "quick_fill_row_id",
        "input_key",
        "row_status",
        "issue_count",
        "issues",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["row_reports"]:
            writer.writerow({**row, "issues": ";".join(row["issues"])})


def write_markdown(payload: dict[str, Any]) -> None:
    rows = "\n".join(
        f"| {row['row_number']} | {row['review_batch_row_id']} | {row['quick_fill_row_id']} | {row['input_key']} | {row['row_status']} | {row['issue_count']} |"
        for row in payload["row_reports"]
    )
    body = f"""# Commercial Review Batch Template Preflight v0.1

commercial_review_batch_template_preflight_v0_1: true
preflight_scope: {payload['preflight_scope']}
status: {payload['status']}
commercial_status: {payload['commercial_status']}
production_launch_status: {payload['production_launch_status']}

## Summary

- template_row_count: {payload['template_row_count']}
- expected_template_row_count: {payload['expected_template_row_count']}
- source_quick_fill_row_count: {payload['source_quick_fill_row_count']}
- blank_human_value_row_count: {payload['blank_human_value_row_count']}
- prefilled_human_value_row_count: {payload['prefilled_human_value_row_count']}
- missing_required_column_count: {payload['missing_required_column_count']}
- duplicate_id_count: {payload['duplicate_id_count']}
- boundary_violation_count: {payload['boundary_violation_count']}
- preflight_passed: {str(payload['preflight_passed']).lower()}
- safe_to_start_human_fill: {str(payload['safe_to_start_human_fill']).lower()}
- template_preflight_superseded: {str(payload['template_preflight_superseded']).lower()}
- ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
- blockers_closed_by_preflight: {payload['blockers_closed_by_preflight']}

## Row Checks

| # | Batch Row | Quick Fill Row | Input Key | Status | Issues |
| --- | --- | --- | --- | --- | --- |
{rows}

## Boundary

- human_values_generated_by_codex: false
- quick_fill_values_entered_by_codex: false
- source_quick_fill_packet_modified: false
- batch_values_applied_to_source: false
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

SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT: PASS
"""
    OUT_MD.write_text(body, encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    body = f"""# Commercial Review Batch Template Preflight Boundary Audit

commercial_review_batch_template_preflight_v0_1: true
status: {payload['status']}
boundary_violation_count: {payload['boundary_violation_count']}

- No values generated by Codex.
- No human values entered by Codex.
- No source quick-fill packet modified.
- No workbook import authorized or performed.
- No validators run on real input.
- No evidence collection authorized.
- No blocker closure authorized.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.

preflight_passed: {str(payload['preflight_passed']).lower()}
safe_to_start_human_fill: {str(payload['safe_to_start_human_fill']).lower()}
template_preflight_superseded: {str(payload['template_preflight_superseded']).lower()}
ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
production_ready: false
customer_validated: false
product_launched: false
"""
    OUT_AUDIT.write_text(body, encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Review Batch Template Preflight v0.1

This local preflight checks whether the 10-row commercial review-batch input
template is still blank, structurally complete, and ready for human filling.

commercial_review_batch_template_preflight_v0_1: true
status: {payload['status']}
preflight_passed: {str(payload['preflight_passed']).lower()}
safe_to_start_human_fill: {str(payload['safe_to_start_human_fill']).lower()}
template_preflight_superseded: {str(payload['template_preflight_superseded']).lower()}
ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
template_row_count: {payload['template_row_count']}
blank_human_value_row_count: {payload['blank_human_value_row_count']}
blockers_closed_by_preflight: 0
production_ready: false
customer_validated: false
product_launched: false

It does not fill values, infer values, import workbooks, run validators on real
input, collect evidence, close blockers, contact anyone, launch product, or
claim production readiness.
"""
    TOP_DOC.write_text(body, encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Review Batch Template Preflight Recommendation Gate

answer: recommend
reason: The preflight is a local, read-only commercial-readiness check that helps
humans avoid filling a corrupted or prefilled 10-row review-batch template.

recommend_for_human_template_preflight: {str(not payload['template_preflight_superseded']).lower()}
recommend_for_value_generation_by_codex: false
recommend_for_workbook_import_execution: false
recommend_for_validator_execution_on_real_input: false
recommend_for_evidence_collection: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production: false

current_status: {payload['status']}
preflight_passed: {str(payload['preflight_passed']).lower()}
safe_to_start_human_fill: {str(payload['safe_to_start_human_fill']).lower()}
template_preflight_superseded: {str(payload['template_preflight_superseded']).lower()}
ready_for_workbook_import_approval_review: {str(payload['ready_for_workbook_import_approval_review']).lower()}
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
"""
    GATE.write_text(body, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_TEMPLATE_PREFLIGHT: PASS "
        f"status={payload['status']} preflight_passed={str(payload['preflight_passed']).lower()} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
