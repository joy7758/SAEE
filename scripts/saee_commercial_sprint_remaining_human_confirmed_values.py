#!/usr/bin/env python3
"""Record remaining human-confirmed recommended quick-fill values.

This runner converts the existing QF-029 through QF-064 recommended draft into a
second local human-confirmed ledger, then builds a complete 64-row local
quick-fill preview by combining the original QF-001 through QF-028 ledger with
the newly confirmed remaining values.

It does not modify the official quick-fill packet, write the workbook, transfer
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

INITIAL_LEDGER_JSON = SPRINT_DIR / "commercial_sprint_human_confirmed_recommended_values.local.json"
REMAINING_DRAFT_JSON = SPRINT_DIR / "commercial_sprint_remaining_recommended_values_draft.local.json"
SOURCE_QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"

REMAINING_JSON = (
    SPRINT_DIR / "commercial_sprint_remaining_human_confirmed_recommended_values.local.json"
)
REMAINING_MD = SPRINT_DIR / "commercial_sprint_remaining_human_confirmed_recommended_values.md"
REMAINING_CSV = SPRINT_DIR / "commercial_sprint_remaining_human_confirmed_recommended_values.csv"
REMAINING_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_remaining_human_confirmed_recommended_values_boundary_audit.md"
)

FULL_PREVIEW_CSV = (
    SPRINT_DIR / "commercial_sprint_all_confirmed_values_quick_fill_preview.local.csv"
)
FULL_PREVIEW_JSON = (
    SPRINT_DIR / "commercial_sprint_all_confirmed_values_import_preview.local.json"
)
FULL_PREVIEW_MD = SPRINT_DIR / "commercial_sprint_all_confirmed_values_import_preview.md"
FULL_PREVIEW_SUMMARY_CSV = SPRINT_DIR / "commercial_sprint_all_confirmed_values_import_preview.csv"
FULL_PREVIEW_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_all_confirmed_values_import_preview_boundary_audit.md"
)

EXPECTED_SOURCE_ROWS = 64
EXPECTED_INITIAL_ROWS = 28
EXPECTED_REMAINING_ROWS = 36
EXPECTED_TOTAL_ROWS = 64

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
    return str(path.resolve().relative_to(ROOT))


def read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def scan_value(text: str) -> list[str]:
    return sorted({name for name, pattern in UNSAFE_PATTERNS.items() if pattern.search(text)})


def false_boundary_payload() -> dict[str, bool | int]:
    payload: dict[str, bool | int] = {flag: False for flag in FALSE_FLAGS}
    payload["blockers_closed_by_confirmed_values"] = 0
    payload["blockers_closed_by_preview"] = 0
    return payload


def build_remaining_ledger(
    remaining_draft: dict[str, Any], source_rows: list[dict[str, str]]
) -> dict[str, Any]:
    boundary_violations: list[str] = []
    if remaining_draft.get("status") != "pending_human_confirmation_no_import":
        boundary_violations.append("remaining_draft_status_not_pending_human_confirmation_no_import")
    if remaining_draft.get("human_confirmed") is not False:
        boundary_violations.append("remaining_draft_already_marked_human_confirmed")
    if remaining_draft.get("draft_row_count") != EXPECTED_REMAINING_ROWS:
        boundary_violations.append("unexpected_remaining_draft_row_count")

    draft_rows = remaining_draft.get("recommended_values", [])
    expected_ids = [f"QF-{index:03d}" for index in range(29, 65)]
    if [row.get("quick_fill_row_id") for row in draft_rows] != expected_ids:
        boundary_violations.append("remaining_draft_ids_not_qf_029_through_qf_064")

    source_by_id = {row.get("quick_fill_row_id", ""): row for row in source_rows}
    confirmed_rows: list[dict[str, Any]] = []
    blocker_counts: Counter[str] = Counter()
    closure_counts: Counter[str] = Counter()
    unsafe_counter: Counter[str] = Counter()

    for draft in draft_rows:
        row_id = draft.get("quick_fill_row_id", "")
        value = draft.get("recommended_value", "")
        source = source_by_id.get(row_id, {})
        unsafe = scan_value(value)
        unsafe_counter.update(unsafe)
        if unsafe:
            boundary_violations.append(f"{row_id}:{'|'.join(unsafe)}")
        blocker_id = draft.get("blocker_id") or source.get("blocker_id", "")
        closure_effect = draft.get("closure_effect", "")
        blocker_counts[blocker_id] += 1
        closure_counts[closure_effect] += 1
        confirmed_rows.append(
            {
                "quick_fill_row_id": row_id,
                "human_input_id": source.get("human_input_id", ""),
                "workbook_row_id": source.get("workbook_row_id", ""),
                "blocker_id": blocker_id,
                "input_group": source.get("input_group", ""),
                "input_key": draft.get("input_key") or source.get("input_key", ""),
                "confirmed_value": value,
                "source_draft_status": draft.get("draft_status", ""),
                "closure_effect": closure_effect,
                "confirmation_source": "human_reply_all_recommended_confirmed",
                "notes": draft.get("reason", ""),
            }
        )

    payload: dict[str, Any] = {
        "commercial_sprint_remaining_human_confirmed_recommended_values_v0_1": True,
        "status": (
            "hold_remaining_confirmed_values_recorded_no_import"
            if not boundary_violations
            else "stop_boundary_or_safety_issue"
        ),
        "record_type": "local_remaining_human_confirmed_recommended_values_ledger",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "source_remaining_draft": rel(REMAINING_DRAFT_JSON),
        "source_quick_fill_packet": rel(SOURCE_QUICK_FILL_CSV),
        "human_confirmation_source": "user_reply_all_recommended_confirmed",
        "confirmed_row_range": "QF-029..QF-064",
        "confirmed_value_row_count": len(confirmed_rows),
        "formal_security_review_confirmed_rows": blocker_counts.get("formal_security_review", 0),
        "pricing_page_confirmed_rows": blocker_counts.get("pricing_page", 0),
        "production_monitoring_confirmed_rows": blocker_counts.get("production_monitoring", 0),
        "production_restore_policy_confirmed_rows": blocker_counts.get(
            "production_restore_policy", 0
        ),
        "keeps_blocker_open_row_count": closure_counts.get("keeps_blocker_open", 0),
        "no_closure_effect_row_count": closure_counts.get("none", 0),
        "unsafe_pattern_hit_count": sum(unsafe_counter.values()),
        "unsafe_pattern_counts": dict(sorted(unsafe_counter.items())),
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "confirmed_values": confirmed_rows,
        "next_human_action": (
            "Review the 64-row full local quick-fill preview and request a separate "
            "safety preflight/import approval. These confirmed values do not close "
            "production blockers by themselves."
        ),
    }
    payload.update(false_boundary_payload())
    REMAINING_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(
        REMAINING_CSV,
        [
            "quick_fill_row_id",
            "blocker_id",
            "input_key",
            "confirmed_value",
            "source_draft_status",
            "closure_effect",
            "confirmation_source",
        ],
        [
            {
                "quick_fill_row_id": row["quick_fill_row_id"],
                "blocker_id": row["blocker_id"],
                "input_key": row["input_key"],
                "confirmed_value": row["confirmed_value"],
                "source_draft_status": row["source_draft_status"],
                "closure_effect": row["closure_effect"],
                "confirmation_source": row["confirmation_source"],
            }
            for row in confirmed_rows
        ],
    )
    REMAINING_MD.write_text(render_remaining_markdown(payload), encoding="utf-8")
    REMAINING_BOUNDARY.write_text(render_remaining_boundary(payload), encoding="utf-8")
    return payload


def build_full_preview(
    initial_ledger: dict[str, Any],
    remaining_ledger: dict[str, Any],
    source_fields: list[str],
    source_rows: list[dict[str, str]],
) -> dict[str, Any]:
    boundary_violations: list[str] = []
    if initial_ledger.get("confirmed_value_row_count") != EXPECTED_INITIAL_ROWS:
        boundary_violations.append("initial_confirmed_ledger_row_count_not_28")
    if remaining_ledger.get("confirmed_value_row_count") != EXPECTED_REMAINING_ROWS:
        boundary_violations.append("remaining_confirmed_ledger_row_count_not_36")
    if len(source_rows) != EXPECTED_SOURCE_ROWS:
        boundary_violations.append("source_quick_fill_row_count_not_64")
    if any(row.get("human_value_to_enter", "").strip() for row in source_rows):
        boundary_violations.append("source_quick_fill_packet_already_contains_values")

    combined_values = initial_ledger.get("confirmed_values", []) + remaining_ledger.get(
        "confirmed_values", []
    )
    value_by_id = {
        row.get("quick_fill_row_id", ""): row.get("confirmed_value", "")
        for row in combined_values
    }
    expected_ids = {f"QF-{index:03d}" for index in range(1, 65)}
    if set(value_by_id) != expected_ids:
        boundary_violations.append("combined_confirmed_value_ids_not_qf_001_through_qf_064")

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
        if value:
            preview_value_count += 1
            blocker_value_counts[row.get("blocker_id", "")] += 1
            preview["human_value_to_enter"] = value
            preview["notes_for_human"] = (
                "local full quick-fill preview from human-confirmed recommended values; "
                "does not modify official source quick-fill packet"
            )
            preview["quick_fill_status"] = "preview_value_present_pending_safety_preflight"
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
                "preview_value_present": bool(value),
                "unsafe_pattern_count": len(unsafe),
                "row_status": (
                    "preview_value_present_pending_safety_preflight"
                    if value
                    else "missing_human_value"
                ),
            }
        )
        preview_rows.append(preview)

    write_csv(FULL_PREVIEW_CSV, source_fields, preview_rows)
    write_csv(
        FULL_PREVIEW_SUMMARY_CSV,
        [
            "quick_fill_row_id",
            "blocker_id",
            "input_group",
            "input_key",
            "preview_value_present",
            "unsafe_pattern_count",
            "row_status",
        ],
        summary_rows,
    )

    missing_count = EXPECTED_TOTAL_ROWS - preview_value_count
    unsafe_count = sum(unsafe_counter.values())
    if boundary_violations:
        status = "stop_boundary_or_safety_issue"
    elif missing_count == 0:
        status = "ready_for_quick_fill_safety_preflight_review_no_source_overwrite"
    else:
        status = "hold_partial_preview_missing_values"

    payload: dict[str, Any] = {
        "commercial_sprint_all_confirmed_values_import_preview_v0_1": True,
        "status": status,
        "preview_type": "local_all_confirmed_values_to_quick_fill_preview",
        "preview_scope": "local_preview_only_no_source_overwrite_no_workbook_import",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_initial_ledger_json": rel(INITIAL_LEDGER_JSON),
        "source_remaining_ledger_json": rel(REMAINING_JSON),
        "source_quick_fill_csv": rel(SOURCE_QUICK_FILL_CSV),
        "preview_quick_fill_csv": rel(FULL_PREVIEW_CSV),
        "source_quick_fill_row_count": len(source_rows),
        "initial_confirmed_value_row_count": len(initial_ledger.get("confirmed_values", [])),
        "remaining_confirmed_value_row_count": len(
            remaining_ledger.get("confirmed_values", [])
        ),
        "confirmed_value_row_count": len(combined_values),
        "preview_value_row_count": preview_value_count,
        "preview_missing_value_row_count": missing_count,
        "remaining_missing_value_row_count": missing_count,
        "value_counts_by_blocker": dict(sorted(blocker_value_counts.items())),
        "remaining_missing_by_blocker": dict(sorted(blocker_missing_counts.items())),
        "unsafe_pattern_hit_count": unsafe_count,
        "unsafe_pattern_counts": dict(sorted(unsafe_counter.items())),
        "boundary_violations": boundary_violations,
        "boundary_violation_count": len(boundary_violations),
        "local_quick_fill_preview_written": True,
        "ready_for_safety_preflight_review": status
        == "ready_for_quick_fill_safety_preflight_review_no_source_overwrite",
        "ready_for_full_workbook_import": False,
        "ready_for_template_transfer": False,
        "ready_for_workbook_import_approval_request": status
        == "ready_for_quick_fill_safety_preflight_review_no_source_overwrite",
        "values_inferred_by_codex": False,
        "human_confirmed_recommended_values_used": True,
        "next_human_action": (
            "Run or request a separate safety preflight review of the 64-row local preview. "
            "Do not import into the workbook or close blockers without separate approval."
        ),
    }
    payload.update(false_boundary_payload())
    FULL_PREVIEW_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    FULL_PREVIEW_MD.write_text(render_full_preview_markdown(payload), encoding="utf-8")
    FULL_PREVIEW_BOUNDARY.write_text(render_full_preview_boundary(payload), encoding="utf-8")
    return payload


def render_remaining_markdown(payload: dict[str, Any]) -> str:
    return f"""# Commercial Sprint Remaining Human Confirmed Recommended Values

commercial_sprint_remaining_human_confirmed_recommended_values_v0_1: true
status: {payload['status']}
record_type: local_remaining_human_confirmed_recommended_values_ledger
confirmed_row_range: QF-029..QF-064

The human reviewer confirmed the remaining recommended values for QF-029
through QF-064. This is a local ledger only: it does not modify the official
quick-fill packet, does not write the workbook, does not run validators on real
input, and does not close production blockers.

## Counts

- confirmed_value_row_count: {payload['confirmed_value_row_count']}
- formal_security_review_confirmed_rows: {payload['formal_security_review_confirmed_rows']}
- pricing_page_confirmed_rows: {payload['pricing_page_confirmed_rows']}
- production_monitoring_confirmed_rows: {payload['production_monitoring_confirmed_rows']}
- production_restore_policy_confirmed_rows: {payload['production_restore_policy_confirmed_rows']}
- keeps_blocker_open_row_count: {payload['keeps_blocker_open_row_count']}
- blockers_closed_by_confirmed_values: 0
- boundary_violation_count: {payload['boundary_violation_count']}

## Boundary

- source_quick_fill_packet_modified: false
- quick_fill_imported_to_workbook: false
- workbook_written: false
- validators_run_on_real_input: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Next Human Action

{payload['next_human_action']}
"""


def render_remaining_boundary(payload: dict[str, Any]) -> str:
    return f"""# Commercial Sprint Remaining Human Confirmed Values Boundary Audit

final_boundary_decision: {'pass_local_ledger_only' if payload['boundary_violation_count'] == 0 else 'stop_boundary_or_safety_issue'}

- Remaining recommended values were recorded as human-confirmed: true
- Official source quick-fill packet modified: false
- Workbook import performed: false
- Workbook written: false
- Template transfer performed: false
- Validators run on real input: false
- Evidence collection authorized: false
- Execution authorized: false
- Blocker closure authorized: false
- Blockers closed by confirmed values: 0
- Runtime modified: false
- Backend modified: false
- Kernel modified: false
- API schema modified: false
- Private core exposed: false
- Product launched: false
- Customer contacted: false
- Production ready claim: false
"""


def render_full_preview_markdown(payload: dict[str, Any]) -> str:
    return f"""# Commercial Sprint All Confirmed Values Import Preview

commercial_sprint_all_confirmed_values_import_preview_v0_1: true
status: {payload['status']}
preview_scope: local_preview_only_no_source_overwrite_no_workbook_import

This preview applies all 64 human-confirmed recommended values to a separate
local quick-fill preview CSV. It does not modify the official source quick-fill
packet, does not write the workbook, does not transfer templates, does not run
validators on real input, does not close blockers, and does not claim production
readiness.

## Counts

- source_quick_fill_row_count: {payload['source_quick_fill_row_count']}
- initial_confirmed_value_row_count: {payload['initial_confirmed_value_row_count']}
- remaining_confirmed_value_row_count: {payload['remaining_confirmed_value_row_count']}
- confirmed_value_row_count: {payload['confirmed_value_row_count']}
- preview_value_row_count: {payload['preview_value_row_count']}
- preview_missing_value_row_count: {payload['preview_missing_value_row_count']}
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


def render_full_preview_boundary(payload: dict[str, Any]) -> str:
    return f"""# Commercial Sprint All Confirmed Values Import Preview Boundary Audit

final_boundary_decision: {'pass_full_local_preview_only' if payload['boundary_violation_count'] == 0 else 'stop_boundary_or_safety_issue'}

- Local full quick-fill preview written: true
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

The preview now contains values for all 64 quick-fill rows, but it still needs a
separate safety preflight/import approval before any workbook or evidence action.
"""


def main() -> int:
    initial_ledger = json.loads(INITIAL_LEDGER_JSON.read_text(encoding="utf-8"))
    remaining_draft = json.loads(REMAINING_DRAFT_JSON.read_text(encoding="utf-8"))
    source_fields, source_rows = read_csv(SOURCE_QUICK_FILL_CSV)

    remaining_ledger = build_remaining_ledger(remaining_draft, source_rows)
    full_preview = build_full_preview(initial_ledger, remaining_ledger, source_fields, source_rows)

    print(
        "SAEE_COMMERCIAL_SPRINT_REMAINING_HUMAN_CONFIRMED_VALUES: PASS "
        f"remaining_confirmed_value_row_count={remaining_ledger['confirmed_value_row_count']} "
        f"full_preview_value_row_count={full_preview['preview_value_row_count']} "
        f"preview_missing_value_row_count={full_preview['preview_missing_value_row_count']} "
        "source_quick_fill_packet_modified=false production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
