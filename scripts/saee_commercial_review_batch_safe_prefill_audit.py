#!/usr/bin/env python3
"""Audit whether Codex may safely prefill the active 10-row commercial batch.

This is intentionally conservative. The active review batch contains human
business decisions for `support_contact`; the audit should prevent examples,
placeholders, or local guesses from being treated as production evidence.
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

SOURCE_TEMPLATE = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
QUALITY_GUIDE = SPRINT_DIR / "commercial_review_batch_human_entry_quality_guide.local.json"
EXECUTION_PACKET = SPRINT_DIR / "commercial_review_batch_human_execution_packet.local.json"

OUT_JSON = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_review_batch_safe_prefill_audit_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT_RECOMMENDATION_GATE.md"

EXPECTED_ROW_COUNT = 10
FALSE_FLAGS = [
    "human_values_generated_by_codex",
    "human_input_filled_by_codex",
    "codex_prefill_performed",
    "source_template_modified",
    "raw_values_recorded",
    "workbook_import_authorized",
    "workbook_import_performed",
    "values_transferred",
    "validators_run_on_real_input",
    "evidence_collection_authorized",
    "execution_authorized",
    "blocker_closure_authorized",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "customer_contacted",
    "product_launched",
    "production_ready",
    "production_ready_claim",
    "customer_validated",
    "customer_validation_claim",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def human_reason(input_key: str) -> str:
    reasons = {
        "assigned_human_owner": "Requires a real owner selected by a human.",
        "owner_contact_reference": "Requires a human-approved internal record reference.",
        "target_review_date": "Requires a real target date chosen by a human.",
        "owner_acknowledged_scope": "Requires owner acknowledgement, not a generated assertion.",
        "human_approval_reference": "Requires an actual approval record.",
        "human_reviewer_name": "Requires the actual reviewer or approved reviewer role.",
        "review_date": "Requires the real review date.",
        "selected_support_contact_channel": "Requires a human decision on the support channel.",
        "decision_summary": "Requires a human decision summary.",
        "abuse_handling_path_defined": "Requires a human-approved abuse handling path.",
    }
    return reasons.get(input_key, "Requires human commercial review.")


def build_rows(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    audited: list[dict[str, Any]] = []
    for row in rows:
        input_key = row.get("input_key", "")
        human_value = row.get("human_value_to_enter", "").strip()
        notes = row.get("notes_for_human", "").strip()
        audited.append(
            {
                "review_batch_row_id": row.get("review_batch_row_id", ""),
                "quick_fill_row_id": row.get("quick_fill_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_key": input_key,
                "expected_value_shape": row.get("expected_value_shape", ""),
                "human_value_present": bool(human_value),
                "notes_present": bool(notes),
                "codex_prefill_allowed": False,
                "safe_prefill_decision": "human_required",
                "safe_prefill_reason": human_reason(input_key),
                "placeholder_or_hold_value_allowed_by_codex": False,
                "requires_human_approval": True,
            }
        )
    return audited


def build_payload() -> dict[str, Any]:
    template_rows = read_csv(SOURCE_TEMPLATE)
    quality = json.loads(QUALITY_GUIDE.read_text(encoding="utf-8"))
    packet = json.loads(EXECUTION_PACKET.read_text(encoding="utf-8"))
    audit_rows = build_rows(template_rows)
    row_count = len(audit_rows)
    human_required = sum(1 for row in audit_rows if row["safe_prefill_decision"] == "human_required")
    codex_allowed = sum(1 for row in audit_rows if row["codex_prefill_allowed"] is True)
    existing_values = sum(1 for row in audit_rows if row["human_value_present"])

    boundary_violation_count = 0
    status = "hold_no_safe_codex_prefill"
    if row_count != EXPECTED_ROW_COUNT or codex_allowed != 0:
        status = "stop_prefill_boundary_violation"
        boundary_violation_count += 1
    if existing_values:
        status = "hold_human_values_present_review_required"

    payload: dict[str, Any] = {
        "commercial_review_batch_safe_prefill_audit_v0_1": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "audit_type": "safe_prefill_audit_no_value_generation",
        "status": status,
        "target_blocker_id": "support_contact",
        "source_template_csv": rel(SOURCE_TEMPLATE),
        "source_quality_guide_json": rel(QUALITY_GUIDE),
        "source_execution_packet_json": rel(EXECUTION_PACKET),
        "template_row_count": row_count,
        "expected_template_row_count": EXPECTED_ROW_COUNT,
        "human_required_row_count": human_required,
        "codex_safe_prefill_count": codex_allowed,
        "existing_human_value_row_count": existing_values,
        "placeholder_or_hold_prefill_allowed_count": 0,
        "safe_to_prefill_by_codex": False,
        "recommended_next_action": "human_fill_required",
        "next_human_action": (
            "A human must fill human_value_to_enter and optional notes_for_human "
            "in the active 10-row review-batch CSV. Codex must not prefill these values."
        ),
        "rows": audit_rows,
        "boundary_violation_count": boundary_violation_count,
        "quality_guide_status": quality.get("status"),
        "execution_packet_status": packet.get("status"),
        "blockers_closed_by_audit": 0,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "review_batch_row_id",
        "quick_fill_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_key",
        "expected_value_shape",
        "codex_prefill_allowed",
        "safe_prefill_decision",
        "safe_prefill_reason",
        "placeholder_or_hold_value_allowed_by_codex",
        "requires_human_approval",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["rows"]:
            writer.writerow({field: row.get(field, "") for field in fields})


def markdown_table(payload: dict[str, Any]) -> str:
    lines = [
        "| Row | Field | Decision | Why Codex cannot prefill |",
        "| --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| {row_id} | `{key}` | {decision} | {reason} |".format(
                row_id=row["review_batch_row_id"],
                key=row["input_key"],
                decision=row["safe_prefill_decision"],
                reason=row["safe_prefill_reason"],
            )
        )
    return "\n".join(lines)


def write_docs(payload: dict[str, Any]) -> None:
    body = f"""# SAEE Commercial Review Batch Safe Prefill Audit v0.1

commercial_review_batch_safe_prefill_audit_v0_1: true
status: {payload['status']}
target_blocker_id: support_contact
audit_type: safe_prefill_audit_no_value_generation

## Summary

The active 10-row commercial review batch was checked for values that Codex may
safe-prefill from current local evidence. Result: no row is safe for Codex to
prefill.

- template_row_count: {payload['template_row_count']}
- human_required_row_count: {payload['human_required_row_count']}
- codex_safe_prefill_count: {payload['codex_safe_prefill_count']}
- placeholder_or_hold_prefill_allowed_count: 0
- safe_to_prefill_by_codex: false
- blockers_closed_by_audit: 0
- production_ready: false
- product_launched: false
- customer_contacted: false

## Audit Table

{markdown_table(payload)}

## Required Human Action

Fill only `human_value_to_enter` and optional `notes_for_human` in:

`{payload['source_template_csv']}`

Do not treat placeholder examples, conservative `hold` text, guessed dates,
guessed owners, guessed channels, or local public-shell facts as human-approved
commercial evidence.

## Boundary

- human_values_generated_by_codex: false
- human_input_filled_by_codex: false
- codex_prefill_performed: false
- source_template_modified: false
- workbook_import_authorized: false
- workbook_import_performed: false
- validators_run_on_real_input: false
- evidence_collection_authorized: false
- blocker_closure_authorized: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- customer_contacted: false
- product_launched: false
- production_ready_claim: false
- customer_validation_claim: false
"""
    for path in [OUT_MD, TOP_DOC]:
        path.write_text(body, encoding="utf-8")

    OUT_BOUNDARY.write_text(
        """# Commercial Review Batch Safe Prefill Boundary Audit

- No human values generated by Codex.
- No `human_value_to_enter` cell modified.
- No source template modified.
- No workbook import authorized or performed.
- No validators run on real input.
- No evidence collected.
- No blocker closed.
- No runtime, backend, kernel, or API schema modified.
- No private core exposed.
- No customer contacted.
- No product launched.
- No production-ready or customer-validation claim added.
""",
        encoding="utf-8",
    )

    GATE.write_text(
        """# SAEE Commercial Review Batch Safe Prefill Audit Recommendation Gate

answer: hold_human_input_required

reason:
The active 10-row support-contact review batch contains human commercial
decisions. Codex cannot safely prefill owners, approval references, dates,
support channels, decision summaries, or abuse-handling paths from local
materials.

decision:
Do not prefill. Human input remains required.

boundary:
human_values_generated_by_codex: false
human_input_filled_by_codex: false
codex_prefill_performed: false
source_template_modified: false
workbook_import_authorized: false
workbook_import_performed: false
validators_run_on_real_input: false
evidence_collection_authorized: false
blocker_closure_authorized: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
customer_contacted: false
product_launched: false
production_ready_claim: false
customer_validation_claim: false

next_action:
Human must fill the active 10-row review-batch CSV before post-fill dry-run,
workbook import approval, evidence collection, or blocker closure.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(payload)
    write_docs(payload)
    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_SAFE_PREFILL_AUDIT: "
        f"{payload['status']} rows={payload['template_row_count']} "
        f"codex_safe_prefill_count={payload['codex_safe_prefill_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
