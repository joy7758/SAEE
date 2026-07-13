#!/usr/bin/env python3
"""Local safety preflight for commercial sprint human-input quick-fill values.

The preflight scans only the quick-fill human value and note columns before a
future workbook import. It records row ids, pattern names, and counts, but never
copies raw human-entered values into outputs.

It does not import values into the workbook, transfer values into templates,
write human-filled templates, run validators on real input, collect evidence,
execute builders, close blockers, contact anyone, launch product, or claim
production readiness.
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
DEFAULT_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_safety_preflight_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT_RECOMMENDATION_GATE.md"
)

EXPECTED_QUICK_FILL_ROWS = 64
VALUE_COLUMNS = ["human_value_to_enter", "notes_for_human"]

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

CONTACT_WARNING_PATTERNS = {
    "email_address": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone_like_value": re.compile(r"(?:\+?\d[\s().-]*){8,}"),
}

ISO_DATE_PATTERN = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")

FALSE_FLAGS = [
    "quick_fill_imported_to_workbook",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
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
    "payment_collected",
    "revenue_validated",
    "raw_values_recorded",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--quick-fill-csv",
        default=str(DEFAULT_QUICK_FILL_CSV),
        help="Quick-fill CSV to scan without recording raw values.",
    )
    return parser.parse_args()


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def scan_text(text: str) -> tuple[list[str], list[str]]:
    unsafe: list[str] = []
    warnings: list[str] = []
    for name, pattern in SECRET_PATTERNS.items():
        if pattern.search(text):
            unsafe.append(name)
    for name, pattern in FORBIDDEN_CLAIM_PATTERNS.items():
        if pattern.search(text):
            unsafe.append(name)
    lowered = text.lower()
    for term in PRIVATE_CORE_TERMS:
        if term in lowered:
            unsafe.append("private_core_reference")
            break
    contact_scan_text = ISO_DATE_PATTERN.sub("", text)
    for name, pattern in CONTACT_WARNING_PATTERNS.items():
        if pattern.search(contact_scan_text):
            warnings.append(name)
    return sorted(set(unsafe)), sorted(set(warnings))


def build_payload(quick_fill_csv: Path) -> dict[str, Any]:
    rows = read_rows(quick_fill_csv)
    boundary_violations: list[str] = []
    row_summaries: list[dict[str, Any]] = []
    unsafe_counter: Counter[str] = Counter()
    warning_counter: Counter[str] = Counter()
    filled_count = 0
    unsafe_row_count = 0
    warning_row_count = 0

    if len(rows) != EXPECTED_QUICK_FILL_ROWS:
        boundary_violations.append("unexpected_quick_fill_row_count")

    for row in rows:
        text = "\n".join(row.get(column, "") for column in VALUE_COLUMNS)
        value_present = bool(row.get("human_value_to_enter", "").strip())
        note_present = bool(row.get("notes_for_human", "").strip())
        if value_present:
            filled_count += 1
        unsafe_patterns, warning_patterns = scan_text(text)
        unsafe_counter.update(unsafe_patterns)
        warning_counter.update(warning_patterns)
        if unsafe_patterns:
            unsafe_row_count += 1
            boundary_violations.append(
                f"{row.get('quick_fill_row_id', '<missing>')}:{'|'.join(unsafe_patterns)}"
            )
        if warning_patterns:
            warning_row_count += 1
        row_status = "unsafe_stop" if unsafe_patterns else "warning_review" if warning_patterns else "safe_or_blank"
        row_summaries.append(
            {
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "queue_item_id": row.get("queue_item_id", ""),
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "value_present": value_present,
                "note_present": note_present,
                "unsafe_pattern_count": len(unsafe_patterns),
                "warning_pattern_count": len(warning_patterns),
                "unsafe_patterns": unsafe_patterns,
                "warning_patterns": warning_patterns,
                "row_status": row_status,
            }
        )

    blank_count = len(rows) - filled_count
    secret_pattern_hit_count = sum(
        count
        for pattern, count in unsafe_counter.items()
        if pattern in SECRET_PATTERNS
    )
    private_core_reference_count = unsafe_counter.get("private_core_reference", 0)
    production_overclaim_count = unsafe_counter.get("production_ready_claim", 0)
    customer_validation_claim_count = unsafe_counter.get("customer_validated_claim", 0)
    product_launch_claim_count = unsafe_counter.get("product_launched_claim", 0)
    external_validation_claim_count = unsafe_counter.get("external_validation_claim", 0)

    if boundary_violations:
        status = "stop_sensitive_or_forbidden_input_detected"
    elif filled_count == 0:
        status = "hold_human_input_required_no_values_to_scan"
    else:
        status = "pass_no_sensitive_values_found_pending_import_approval"

    safe_to_import = (
        status == "pass_no_sensitive_values_found_pending_import_approval"
        and filled_count == EXPECTED_QUICK_FILL_ROWS
        and warning_row_count == 0
    )

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_safety_preflight_v0_1": True,
        "preflight_type": "local_human_input_safety_preflight",
        "preflight_scope": "quick_fill_values_and_notes_only_no_import_no_transfer_no_evidence",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_safety_preflight.py",
        "source_quick_fill_csv": rel(quick_fill_csv),
        "value_columns_scanned": VALUE_COLUMNS,
        "quick_fill_row_count": len(rows),
        "rows_scanned_count": len(rows),
        "filled_value_row_count": filled_count,
        "blank_value_row_count": blank_count,
        "secret_pattern_hit_count": secret_pattern_hit_count,
        "private_core_reference_count": private_core_reference_count,
        "production_overclaim_count": production_overclaim_count,
        "customer_validation_claim_count": customer_validation_claim_count,
        "product_launch_claim_count": product_launch_claim_count,
        "external_validation_claim_count": external_validation_claim_count,
        "unsafe_row_count": unsafe_row_count,
        "warning_row_count": warning_row_count,
        "contact_data_warning_count": sum(warning_counter.values()),
        "safe_to_import_after_human_approval": safe_to_import,
        "ready_for_workbook_import": False,
        "raw_value_storage_policy": "never_record_raw_human_values",
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "unsafe_pattern_counts": dict(sorted(unsafe_counter.items())),
        "warning_pattern_counts": dict(sorted(warning_counter.items())),
        "row_summaries": row_summaries,
        "next_human_action": (
            "Fill real quick-fill values, run this safety preflight, then run "
            "the quick-fill validator before any separate human-approved import."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "quick_fill_row_id",
        "queue_item_id",
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "value_present",
        "note_present",
        "unsafe_pattern_count",
        "warning_pattern_count",
        "unsafe_patterns",
        "warning_patterns",
        "row_status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["row_summaries"]:
            sanitized = dict(row)
            sanitized["unsafe_patterns"] = "|".join(row["unsafe_patterns"])
            sanitized["warning_patterns"] = "|".join(row["warning_patterns"])
            writer.writerow({field: sanitized.get(field, "") for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_human_input_safety_preflight_v0_1: true",
        f"status: {payload['status']}",
        f"preflight_scope: {payload['preflight_scope']}",
        f"quick_fill_row_count: {payload['quick_fill_row_count']}",
        f"rows_scanned_count: {payload['rows_scanned_count']}",
        f"filled_value_row_count: {payload['filled_value_row_count']}",
        f"blank_value_row_count: {payload['blank_value_row_count']}",
        f"secret_pattern_hit_count: {payload['secret_pattern_hit_count']}",
        f"private_core_reference_count: {payload['private_core_reference_count']}",
        f"production_overclaim_count: {payload['production_overclaim_count']}",
        f"customer_validation_claim_count: {payload['customer_validation_claim_count']}",
        f"product_launch_claim_count: {payload['product_launch_claim_count']}",
        f"external_validation_claim_count: {payload['external_validation_claim_count']}",
        f"unsafe_row_count: {payload['unsafe_row_count']}",
        f"warning_row_count: {payload['warning_row_count']}",
        f"contact_data_warning_count: {payload['contact_data_warning_count']}",
        f"safe_to_import_after_human_approval: {str(payload['safe_to_import_after_human_approval']).lower()}",
        "ready_for_workbook_import: false",
        "raw_values_recorded: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_written: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "real_evidence_created: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blocker_closure_authorized: false",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]


def write_markdown(path: Path, payload: dict[str, Any], title: str) -> None:
    path.write_text(
        f"""# {title}

{chr(10).join(status_lines(payload))}

## Purpose

This local preflight checks commercial sprint quick-fill values for secret-like
tokens, forbidden production/customer/external-validation claims, and private
core references before any future workbook import.

## Boundary

The preflight does not record raw human-entered values. It records only row
identifiers, pattern names, and counts. It does not import workbook values,
transfer templates, write human-filled evidence, run validators, collect
evidence, execute builders, close blockers, contact customers/vendors, launch
product, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Human Input Safety Preflight Recommendation Gate

answer: conditional
recommend_for_pre_import_safety_screening: true
recommend_for_secret_pattern_detection: true
recommend_for_private_core_leakage_screening: true
recommend_for_claim_boundary_screening: true
recommend_for_workbook_import: false
recommend_for_template_transfer: false
recommend_for_validator_execution: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

{chr(10).join(status_lines(payload))}

Reason: this surface is recommendable only as a local pre-import safety screen
for human-filled quick-fill values. It is not evidence completion and does not
authorize import, transfer, validator execution, evidence collection, or launch.
""",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    payload = build_payload(Path(args.quick_fill_csv))
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_markdown(OUT_MD, payload, "Commercial Sprint Human Input Safety Preflight v0.1")
    write_markdown(OUT_BOUNDARY, payload, "Commercial Sprint Human Input Safety Preflight Boundary Audit")
    write_markdown(TOP_DOC, payload, "SAEE Commercial Sprint Human Input Safety Preflight v0.1")
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_SAFETY_PREFLIGHT: PASS "
        f"status={payload['status']} "
        f"rows_scanned_count={payload['rows_scanned_count']} "
        f"secret_pattern_hit_count={payload['secret_pattern_hit_count']} "
        "raw_values_recorded=false production_ready=false"
    )


if __name__ == "__main__":
    main()
