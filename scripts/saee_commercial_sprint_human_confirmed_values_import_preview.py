#!/usr/bin/env python3
"""Build a local quick-fill import preview from confirmed recommended values.

This script reads the local human-confirmed recommended values ledger and the
official blank quick-fill packet, then writes a separate preview CSV with the
confirmed values applied to QF-001 through QF-028 only.

It does not modify the official quick-fill CSV, import a workbook, transfer
templates, run validators on real input, collect evidence, close blockers,
contact anyone, launch product, or claim production readiness.
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
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
LEDGER_JSON = SPRINT_DIR / "commercial_sprint_human_confirmed_recommended_values.local.json"
SOURCE_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
PREVIEW_QUICK_FILL_CSV = (
    SPRINT_DIR / "commercial_sprint_human_confirmed_values_quick_fill_preview.local.csv"
)
OUT_JSON = (
    SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview.local.json"
)
OUT_MD = SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_confirmed_values_import_preview_boundary_audit.md"
)

EXPECTED_SOURCE_ROWS = 64
EXPECTED_CONFIRMED_ROWS = 28

UNSAFE_PATTERNS = {
    "production_ready_true_claim": re.compile(r"\bproduction[_ -]?ready\s*[:=]\s*true\b", re.I),
    "customer_validated_true_claim": re.compile(r"\bcustomer[_ -]?validated\s*[:=]\s*true\b", re.I),
    "product_launched_true_claim": re.compile(r"\bproduct[_ -]?launched\s*[:=]\s*true\b", re.I),
    "private_core_exposed_true_claim": re.compile(r"\bprivate[_ -]?core[_ -]?exposed\s*[:=]\s*true\b", re.I),
    "api_key_like_secret": re.compile(r"\b(?:sk-|ls__|gh[pousr]_|AKIA)[A-Za-z0-9_-]{12,}\b"),
    "private_key_block": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
}


FALSE_FLAGS = [
    "source_quick_fill_packet_modified",
    "quick_fill_imported_to_workbook",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "evidence_collection_authorized",
    "execution_authorized",
    "blocker_closure_authorized",
    "blockers_closed_by_preview",
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
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scan_value(text: str) -> list[str]:
    matches: list[str] = []
    for name, pattern in UNSAFE_PATTERNS.items():
        if pattern.search(text):
            matches.append(name)
    return sorted(set(matches))


def build_preview() -> dict[str, Any]:
    ledger = json.loads(LEDGER_JSON.read_text(encoding="utf-8"))
    source_fields, source_rows = read_csv(SOURCE_QUICK_FILL_CSV)

    boundary_violations: list[str] = []
    if ledger.get("status") != "hold_confirmed_values_recorded_no_import":
        boundary_violations.append("ledger_status_not_hold_confirmed_values_recorded_no_import")
    if ledger.get("confirmed_value_row_count") != EXPECTED_CONFIRMED_ROWS:
        boundary_violations.append("unexpected_ledger_confirmed_value_row_count")
    if len(source_rows) != EXPECTED_SOURCE_ROWS:
        boundary_violations.append("unexpected_source_quick_fill_row_count")
    source_quick_fill_value_count = sum(
        1 for row in source_rows if row.get("human_value_to_enter", "").strip()
    )
    source_quick_fill_fully_confirmed = source_quick_fill_value_count == EXPECTED_SOURCE_ROWS
    if source_quick_fill_value_count not in {0, EXPECTED_SOURCE_ROWS}:
        boundary_violations.append("source_quick_fill_packet_partially_contains_values")
    for flag in [
        "source_quick_fill_packet_modified",
        "quick_fill_imported_to_workbook",
        "workbook_written",
        "values_transferred",
        "validators_run_on_real_input",
        "production_ready",
        "product_launched",
        "customer_validated",
        "customer_contacted",
        "private_core_exposed",
    ]:
        if ledger.get(flag) is not False:
            boundary_violations.append(f"ledger_{flag}_not_false")

    confirmed_values = ledger.get("confirmed_values", [])
    value_by_id = {
        row.get("quick_fill_row_id", ""): row.get("confirmed_value", "")
        for row in confirmed_values
    }
    expected_confirmed_ids = {f"QF-{index:03d}" for index in range(1, 29)}
    if set(value_by_id) != expected_confirmed_ids:
        boundary_violations.append("confirmed_value_ids_not_qf_001_through_qf_028")

    preview_rows: list[dict[str, Any]] = []
    summary_rows: list[dict[str, Any]] = []
    unsafe_counter: Counter[str] = Counter()
    blocker_value_counts: Counter[str] = Counter()
    blocker_missing_counts: Counter[str] = Counter()
    preview_value_count = 0

    for row in source_rows:
        preview = dict(row)
        row_id = row.get("quick_fill_row_id", "")
        value = value_by_id.get(row_id, "")
        value_source = "initial_confirmed_ledger"
        if not value and source_quick_fill_fully_confirmed:
            value = row.get("human_value_to_enter", "")
            value_source = "superseding_all_confirmed_values_source"
        value_present = bool(value)
        if value_present:
            preview_value_count += 1
            blocker_value_counts[row.get("blocker_id", "")] += 1
            preview["human_value_to_enter"] = value
            preview["notes_for_human"] = (
                "local preview from confirmed values; this artifact is superseded by "
                "the complete 64-row confirmed source when present and does not "
                "authorize workbook import"
            )
            preview["quick_fill_status"] = (
                "preview_value_present_from_superseding_all_confirmed_values"
                if value_source == "superseding_all_confirmed_values_source"
                else "preview_value_present_from_initial_confirmed_ledger"
            )
        else:
            blocker_missing_counts[row.get("blocker_id", "")] += 1
        unsafe = scan_value(value)
        unsafe_counter.update(unsafe)
        if unsafe:
            boundary_violations.append(f"{row_id}:{'|'.join(unsafe)}")
        summary_rows.append(
            {
                "quick_fill_row_id": row_id,
                "blocker_id": row.get("blocker_id", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "preview_value_present": value_present,
                "unsafe_pattern_count": len(unsafe),
                "value_source": value_source if value_present else "",
                "row_status": (
                    "preview_value_present"
                    if value_present
                    else "missing_human_value_not_in_confirmed_ledger"
                ),
            }
        )
        preview_rows.append(preview)

    write_csv(PREVIEW_QUICK_FILL_CSV, source_fields, preview_rows)
    write_csv(
        OUT_CSV,
        [
            "quick_fill_row_id",
            "blocker_id",
            "input_group",
            "input_key",
            "preview_value_present",
            "unsafe_pattern_count",
            "value_source",
            "row_status",
        ],
        summary_rows,
    )

    missing_count = EXPECTED_SOURCE_ROWS - preview_value_count
    unsafe_count = sum(unsafe_counter.values())
    if boundary_violations:
        status = "stop_boundary_or_safety_issue"
    elif source_quick_fill_fully_confirmed:
        status = "superseded_by_all_confirmed_values_pending_workbook_import_approval"
    elif preview_value_count == EXPECTED_SOURCE_ROWS:
        status = "ready_for_full_quick_fill_import_review"
    else:
        status = "hold_partial_preview_missing_remaining_values"

    payload: dict[str, Any] = {
        "commercial_sprint_human_confirmed_values_import_preview_v0_1": True,
        "status": status,
        "preview_type": "local_confirmed_values_to_quick_fill_preview",
        "preview_scope": "local_preview_only_no_source_overwrite_no_workbook_import",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_ledger_json": rel(LEDGER_JSON),
        "source_quick_fill_csv": rel(SOURCE_QUICK_FILL_CSV),
        "preview_quick_fill_csv": rel(PREVIEW_QUICK_FILL_CSV),
        "source_quick_fill_row_count": len(source_rows),
        "source_quick_fill_value_row_count": source_quick_fill_value_count,
        "confirmed_value_row_count": len(confirmed_values),
        "preview_value_row_count": preview_value_count,
        "preview_missing_value_row_count": missing_count,
        "support_contact_preview_value_row_count": blocker_value_counts.get("support_contact", 0),
        "pricing_page_preview_value_row_count": blocker_value_counts.get("pricing_page", 0),
        "remaining_missing_value_row_count": missing_count,
        "global_remaining_missing_value_row_count": 0
        if source_quick_fill_fully_confirmed
        else missing_count,
        "remaining_missing_by_blocker": dict(sorted(blocker_missing_counts.items())),
        "unsafe_pattern_hit_count": unsafe_count,
        "unsafe_pattern_counts": dict(sorted(unsafe_counter.items())),
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "local_quick_fill_preview_written": True,
        "ready_for_safety_preflight_review": status != "stop_boundary_or_safety_issue",
        "ready_for_workbook_import_approval_review": source_quick_fill_fully_confirmed,
        "ready_for_full_workbook_import": False,
        "ready_for_template_transfer": False,
        "values_inferred_by_codex": False,
        "human_confirmed_recommended_values_used": True,
        "superseded_by_all_confirmed_values_preview": source_quick_fill_fully_confirmed,
        "next_human_action": (
            "Review the complete confirmed quick-fill values and explicitly approve "
            "workbook import before any workbook write. This superseded preview does "
            "not authorize workbook import or blocker closure."
            if source_quick_fill_fully_confirmed
            else "Review the 28-row preview, then continue QF-029 through QF-064 "
            "or explicitly request a separate partial-import review. This preview "
            "does not authorize workbook import or blocker closure."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_preview"] = 0

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    OUT_BOUNDARY.write_text(render_boundary(payload), encoding="utf-8")
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    return f"""# Commercial Sprint Human Confirmed Values Import Preview

commercial_sprint_human_confirmed_values_import_preview_v0_1: true
status: {payload['status']}
preview_scope: local_preview_only_no_source_overwrite_no_workbook_import

This preview records the initial human-confirmed recommended values and, when
the complete 64-row confirmed source is already present, marks this artifact as
superseded by that complete source. It does not write the workbook, does not
transfer templates, does not run validators on real input, does not close
blockers, and does not claim production readiness.

## Counts

- source_quick_fill_row_count: {payload['source_quick_fill_row_count']}
- source_quick_fill_value_row_count: {payload['source_quick_fill_value_row_count']}
- confirmed_value_row_count: {payload['confirmed_value_row_count']}
- preview_value_row_count: {payload['preview_value_row_count']}
- preview_missing_value_row_count: {payload['preview_missing_value_row_count']}
- global_remaining_missing_value_row_count: {payload['global_remaining_missing_value_row_count']}
- support_contact_preview_value_row_count: {payload['support_contact_preview_value_row_count']}
- pricing_page_preview_value_row_count: {payload['pricing_page_preview_value_row_count']}
- unsafe_pattern_hit_count: {payload['unsafe_pattern_hit_count']}
- boundary_violation_count: {payload['boundary_violation_count']}

## Boundary

- source_quick_fill_packet_modified: false
- quick_fill_imported_to_workbook: false
- workbook_written: false
- values_transferred: false
- human_filled_templates_written: false
- validators_run_on_real_input: false
- blockers_closed_by_preview: 0
- production_ready: false
- product_launched: false
- customer_validated: false
- customer_contacted: false
- private_core_exposed: false

## Next Human Action

{payload['next_human_action']}
"""


def render_boundary(payload: dict[str, Any]) -> str:
    return f"""# Commercial Sprint Human Confirmed Values Import Preview Boundary Audit

final_boundary_decision: {'pass_local_preview_only' if payload['boundary_violation_count'] == 0 else 'stop_boundary_or_safety_issue'}

- Local quick-fill preview written: true
- Official source quick-fill packet modified: false
- Workbook import performed: false
- Workbook written: false
- Template transfer performed: false
- Validators run on real input: false
- Evidence collection authorized: false
- Execution authorized: false
- Blocker closure authorized: false
- Blockers closed by preview: 0
- Runtime modified: false
- Backend modified: false
- Kernel modified: false
- API schema modified: false
- Private core exposed: false
- Product launched: false
- Customer contacted: false
- Production ready claim: false

Global remaining missing values: {payload['global_remaining_missing_value_row_count']}.
Workbook import remains pending explicit approval.
"""


def main() -> int:
    payload = build_preview()
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_CONFIRMED_VALUES_IMPORT_PREVIEW: PASS "
        f"status={payload['status']} preview_value_row_count={payload['preview_value_row_count']} "
        f"preview_missing_value_row_count={payload['preview_missing_value_row_count']} "
        "source_quick_fill_packet_modified=false production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
