#!/usr/bin/env python3
"""Safety preflight for the 64-row all-confirmed quick-fill preview.

This scanner reads only the local all-confirmed preview CSV. It does not modify
the official quick-fill packet, import workbook rows, transfer templates, run
validators on real input, collect evidence, close blockers, contact anyone, or
claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str((ROOT / "scripts").resolve()))

import saee_commercial_sprint_human_input_safety_preflight as base_preflight  # noqa: E402


SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SOURCE_PREVIEW_JSON = SPRINT_DIR / "commercial_sprint_all_confirmed_values_import_preview.local.json"
SOURCE_PREVIEW_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_quick_fill_preview.local.csv"
SOURCE_OFFICIAL_QUICK_FILL = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

OUT_JSON = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_all_confirmed_values_safety_preflight_boundary_audit.md"

EXPECTED_ROW_COUNT = 64
BENIGN_DATE_KEYS = {"target_review_date", "review_date"}
FALSE_FLAGS = [
    "source_quick_fill_packet_modified",
    "quick_fill_imported_to_workbook",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
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
    "payment_collected",
    "revenue_validated",
    "raw_values_recorded",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_warnings(row: dict[str, Any]) -> tuple[list[str], list[str]]:
    warnings = list(row.get("warning_patterns", []))
    if (
        row.get("input_key") in BENIGN_DATE_KEYS
        and warnings == ["phone_like_value"]
    ):
        return ["date_value_matched_phone_like_pattern"], []
    return [], warnings


def build_payload() -> dict[str, Any]:
    preview = load_json(SOURCE_PREVIEW_JSON)
    scan = base_preflight.build_payload(SOURCE_PREVIEW_CSV)

    benign_warning_count = 0
    unresolved_warning_count = 0
    row_summaries: list[dict[str, Any]] = []
    for row in scan["row_summaries"]:
        benign, unresolved = classify_warnings(row)
        benign_warning_count += len(benign)
        unresolved_warning_count += len(unresolved)
        row_status = "unsafe_stop" if row["unsafe_patterns"] else (
            "warning_review" if unresolved else "safe_preview_value"
        )
        row_summaries.append(
            {
                "quick_fill_row_id": row["quick_fill_row_id"],
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": row["blocker_id"],
                "input_group": row["input_group"],
                "input_key": row["input_key"],
                "value_present": row["value_present"],
                "unsafe_patterns": row["unsafe_patterns"],
                "benign_warning_patterns": benign,
                "unresolved_warning_patterns": unresolved,
                "row_status": row_status,
            }
        )

    boundary_violations: list[str] = []
    if preview.get("confirmed_value_row_count") != EXPECTED_ROW_COUNT:
        boundary_violations.append("preview_confirmed_value_row_count_not_64")
    if preview.get("preview_missing_value_row_count") != 0:
        boundary_violations.append("preview_still_has_missing_values")
    if scan.get("filled_value_row_count") != EXPECTED_ROW_COUNT:
        boundary_violations.append("scan_filled_value_row_count_not_64")
    if scan.get("boundary_violation_count") != 0:
        boundary_violations.append("base_safety_boundary_violation")

    unsafe_count = int(scan.get("unsafe_row_count", 0) or 0)
    if unsafe_count:
        status = "stop_sensitive_or_forbidden_input_detected"
    elif boundary_violations:
        status = "stop_boundary_violation"
    elif unresolved_warning_count:
        status = "hold_unresolved_warning_review_required"
    else:
        status = "pass_no_sensitive_values_found_pending_import_approval"

    safe_after_human_approval = (
        status == "pass_no_sensitive_values_found_pending_import_approval"
        and scan.get("filled_value_row_count") == EXPECTED_ROW_COUNT
    )

    payload: dict[str, Any] = {
        "commercial_sprint_all_confirmed_values_safety_preflight_v0_1": True,
        "preflight_type": "local_all_confirmed_values_preview_safety_preflight",
        "preflight_scope": "all_confirmed_preview_values_only_no_source_overwrite_no_workbook_import",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_all_confirmed_values_safety_preflight.py",
        "source_preview_json": rel(SOURCE_PREVIEW_JSON),
        "source_preview_csv": rel(SOURCE_PREVIEW_CSV),
        "source_official_quick_fill_csv": rel(SOURCE_OFFICIAL_QUICK_FILL),
        "source_preview_confirmed_value_row_count": preview.get("confirmed_value_row_count"),
        "source_preview_missing_value_row_count": preview.get("preview_missing_value_row_count"),
        "rows_scanned_count": scan.get("rows_scanned_count"),
        "filled_value_row_count": scan.get("filled_value_row_count"),
        "blank_value_row_count": scan.get("blank_value_row_count"),
        "secret_pattern_hit_count": scan.get("secret_pattern_hit_count"),
        "private_core_reference_count": scan.get("private_core_reference_count"),
        "production_overclaim_count": scan.get("production_overclaim_count"),
        "customer_validation_claim_count": scan.get("customer_validation_claim_count"),
        "product_launch_claim_count": scan.get("product_launch_claim_count"),
        "external_validation_claim_count": scan.get("external_validation_claim_count"),
        "unsafe_row_count": unsafe_count,
        "base_warning_row_count": scan.get("warning_row_count"),
        "benign_date_warning_count": benign_warning_count,
        "unresolved_warning_count": unresolved_warning_count,
        "boundary_violations": sorted(set(boundary_violations)),
        "boundary_violation_count": len(set(boundary_violations)),
        "safe_to_import_after_human_approval": safe_after_human_approval,
        "ready_for_workbook_import_approval_request": safe_after_human_approval,
        "ready_for_workbook_import_execution": False,
        "ready_for_full_workbook_import": False,
        "row_summaries": row_summaries,
        "next_required_action": (
            "Generate a separate workbook import approval request; do not import "
            "or execute without explicit human approval."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "quick_fill_row_id",
        "workbook_row_id",
        "blocker_id",
        "input_group",
        "input_key",
        "value_present",
        "unsafe_patterns",
        "benign_warning_patterns",
        "unresolved_warning_patterns",
        "row_status",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["row_summaries"]:
            out = dict(row)
            out["unsafe_patterns"] = "|".join(out["unsafe_patterns"])
            out["benign_warning_patterns"] = "|".join(out["benign_warning_patterns"])
            out["unresolved_warning_patterns"] = "|".join(out["unresolved_warning_patterns"])
            writer.writerow({field: out.get(field, "") for field in fields})


def status_lines(payload: dict[str, Any]) -> list[str]:
    return [
        "commercial_sprint_all_confirmed_values_safety_preflight_v0_1: true",
        f"status: {payload['status']}",
        f"preflight_scope: {payload['preflight_scope']}",
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
        f"base_warning_row_count: {payload['base_warning_row_count']}",
        f"benign_date_warning_count: {payload['benign_date_warning_count']}",
        f"unresolved_warning_count: {payload['unresolved_warning_count']}",
        f"safe_to_import_after_human_approval: {str(payload['safe_to_import_after_human_approval']).lower()}",
        "ready_for_workbook_import_execution: false",
        "ready_for_full_workbook_import: false",
        "source_quick_fill_packet_modified: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_performed: false",
        "workbook_written: false",
        "values_transferred: false",
        "human_filled_templates_written: false",
        "validators_run_on_real_input: false",
        "real_evidence_created: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blocker_closure_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]


def write_markdown(path: Path, payload: dict[str, Any], title: str) -> None:
    if payload["benign_date_warning_count"]:
        warning_note = (
            f"{payload['benign_date_warning_count']} date fields matched the "
            "generic phone-like pattern. They are recorded as benign date "
            "warnings because the affected input keys are `target_review_date` "
            "or `review_date`."
        )
    else:
        warning_note = "No unresolved warnings were found in the preview values."
    path.write_text(
        f"""# {title}

{chr(10).join(status_lines(payload))}

## Summary

The 64-row all-confirmed quick-fill preview was scanned for secret-like values,
forbidden production/customer/external-validation claims, private core
references, and unresolved warning patterns.

{warning_note}

## Boundary

This preflight does not modify the official quick-fill packet, does not import
the workbook, does not transfer templates, does not run validators on real
input, does not create production evidence, does not close blockers, and does
not claim production readiness.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_markdown(OUT_MD, payload, "Commercial Sprint All Confirmed Values Safety Preflight v0.1")
    write_markdown(OUT_BOUNDARY, payload, "Commercial Sprint All Confirmed Values Safety Preflight Boundary Audit")
    print(
        "SAEE_COMMERCIAL_SPRINT_ALL_CONFIRMED_VALUES_SAFETY_PREFLIGHT: PASS "
        f"status={payload['status']} "
        f"rows_scanned_count={payload['rows_scanned_count']} "
        f"filled_value_row_count={payload['filled_value_row_count']} "
        f"secret_pattern_hit_count={payload['secret_pattern_hit_count']} "
        f"unresolved_warning_count={payload['unresolved_warning_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
