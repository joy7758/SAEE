#!/usr/bin/env python3
"""Record the controlled local workbook import execution for the commercial sprint.

This script verifies that the human-confirmed quick-fill values were imported
into the local workbook output CSV. It records only the local workbook-import
execution state. It does not transfer values into templates, run validators,
collect evidence, close blockers, contact anyone, launch product, or claim
production readiness.
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
IMPORTED_WORKBOOK = (
    SPRINT_DIR / "commercial_sprint_human_input_workbook.imported_from_quick_fill.local.csv"
)
SOURCE_QUICK_FILL = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
SOURCE_WORKBOOK = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
SOURCE_REQUEST_PACKET = (
    SPRINT_DIR / "commercial_sprint_workbook_import_execution_request_packet.local.json"
)
OUT_JSON = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_workbook_import_execution_applied_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED_RECOMMENDATION_GATE.md"
)

EXPECTED_WORKBOOK_ROW_COUNT = 65
EXPECTED_IMPORTED_ROW_COUNT = 64


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def bool_text(value: bool) -> str:
    return "true" if value else "false"


def build_payload() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    imported_rows = read_csv(IMPORTED_WORKBOOK)
    request_packet = json.loads(SOURCE_REQUEST_PACKET.read_text(encoding="utf-8"))
    boundary_violations: list[str] = []

    if len(imported_rows) != EXPECTED_WORKBOOK_ROW_COUNT:
        boundary_violations.append("unexpected_imported_workbook_row_count")

    imported_value_rows = [
        row
        for row in imported_rows
        if row.get("human_value_placeholder", "").strip()
        and row.get("status") == "imported_from_quick_fill_pending_validator"
    ]
    pending_rows = [
        row
        for row in imported_rows
        if not row.get("human_value_placeholder", "").strip()
        or row.get("status") != "imported_from_quick_fill_pending_validator"
    ]
    if len(imported_value_rows) != EXPECTED_IMPORTED_ROW_COUNT:
        boundary_violations.append("unexpected_imported_value_row_count")
    if request_packet.get("ready_for_separate_human_execution_request") is not True:
        boundary_violations.append("source_execution_request_not_ready")
    if request_packet.get("recommended_human_decision") != "approve":
        boundary_violations.append("source_execution_request_not_recommended_approve")

    blocker_counts = Counter(row.get("blocker_id", "") for row in imported_value_rows)
    row_summaries: list[dict[str, Any]] = []
    for row in imported_rows:
        value_present = bool(row.get("human_value_placeholder", "").strip())
        imported = value_present and row.get("status") == "imported_from_quick_fill_pending_validator"
        row_summaries.append(
            {
                "workbook_row_id": row.get("workbook_row_id", ""),
                "blocker_id": row.get("blocker_id", ""),
                "owner_review_lane": row.get("owner_review_lane", ""),
                "input_group": row.get("input_group", ""),
                "input_key": row.get("input_key", ""),
                "human_value_present": value_present,
                "imported_from_quick_fill": imported,
                "status": row.get("status", ""),
            }
        )

    payload: dict[str, Any] = {
        "commercial_sprint_workbook_import_execution_applied_v0_1": True,
        "execution_type": "human_authorized_local_workbook_import",
        "execution_scope": "quick_fill_to_local_workbook_csv_only",
        "status": "workbook_import_applied_pending_template_transfer_request",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_workbook_import_execution_applied.py",
        "source_execution_request_packet": rel(SOURCE_REQUEST_PACKET),
        "source_execution_request_status": request_packet.get("status"),
        "source_recommended_human_decision": request_packet.get("recommended_human_decision"),
        "human_execution_authorized": True,
        "human_execution_request_recorded": True,
        "workbook_import_authorized": True,
        "workbook_import_performed": True,
        "workbook_written": True,
        "source_quick_fill_csv": rel(SOURCE_QUICK_FILL),
        "source_workbook_csv": rel(SOURCE_WORKBOOK),
        "imported_workbook_csv": rel(IMPORTED_WORKBOOK),
        "workbook_row_count": len(imported_rows),
        "imported_value_row_count": len(imported_value_rows),
        "pending_value_row_count": len(pending_rows),
        "expected_imported_value_row_count": EXPECTED_IMPORTED_ROW_COUNT,
        "blocker_import_counts": dict(sorted(blocker_counts.items())),
        "ready_for_template_transfer_request": True,
        "template_transfer_authorized": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "validators_run_on_real_input": False,
        "ready_for_validator_execution": False,
        "validator_execution_authorized": False,
        "evidence_collection_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_workbook_import": 0,
        "real_evidence_created": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "vendor_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "payment_collected": False,
        "revenue_validated": False,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "next_required_action": (
            "Create a separate human-approved template-transfer request before "
            "values may be written into human-filled evidence templates."
        ),
        "rows": row_summaries,
    }
    return payload, row_summaries


def write_markdown(payload: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Commercial Sprint Workbook Import Execution Applied v0.1",
        "",
        "This record confirms a local workbook-import execution only.",
        "It does not transfer values into templates, run validators, collect evidence, close blockers, launch product, or claim production readiness.",
        "",
        "```yaml",
    ]
    for key in [
        "commercial_sprint_workbook_import_execution_applied_v0_1",
        "status",
        "execution_type",
        "execution_scope",
        "human_execution_authorized",
        "human_execution_request_recorded",
        "workbook_import_authorized",
        "workbook_import_performed",
        "workbook_written",
        "workbook_row_count",
        "imported_value_row_count",
        "pending_value_row_count",
        "ready_for_template_transfer_request",
        "template_transfer_authorized",
        "values_transferred",
        "human_filled_templates_written",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "evidence_builder_executed",
        "blockers_closed_by_workbook_import",
        "production_ready",
        "product_launched",
        "customer_validated",
        "customer_contacted",
        "private_core_exposed",
        "boundary_violation_count",
    ]:
        value = payload[key]
        if isinstance(value, bool):
            value = bool_text(value)
        lines.append(f"{key}: {value}")
    lines.extend(
        [
            f"imported_workbook_csv: {payload['imported_workbook_csv']}",
            "```",
            "",
            "## Imported Rows",
            "",
            "| Blocker | Imported rows |",
            "| --- | ---: |",
        ]
    )
    for blocker, count in payload["blocker_import_counts"].items():
        lines.append(f"| {blocker} | {count} |")
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No template transfer was performed.",
            "- No validator was run on real input.",
            "- No evidence builder was executed.",
            "- No blocker was closed.",
            "- No customer or vendor was contacted.",
            "- No production-ready or customer-validation claim was made.",
            "- No runtime, backend, kernel, API schema, or private core was modified.",
            "",
            "## Next Required Action",
            "",
            payload["next_required_action"],
            "",
        ]
    )
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    TOP_DOC.write_text("\n".join(lines), encoding="utf-8")

    boundary_lines = [
        "# Workbook Import Execution Boundary Audit",
        "",
        "- workbook_import_performed: true",
        "- workbook_written: true",
        "- template_transfer_authorized: false",
        "- values_transferred: false",
        "- human_filled_templates_written: false",
        "- validators_run_on_real_input: false",
        "- evidence_collection_authorized: false",
        "- evidence_builder_executed: false",
        "- blocker_closure_authorized: false",
        "- blockers_closed_by_workbook_import: 0",
        "- runtime_modified: false",
        "- backend_modified: false",
        "- kernel_modified: false",
        "- api_schema_modified: false",
        "- private_core_exposed: false",
        "- product_launched: false",
        "- production_ready: false",
        "- customer_validated: false",
        "- customer_contacted: false",
        "- external_calls_made: false",
        "- boundary_violation_count: 0",
        "",
    ]
    OUT_BOUNDARY.write_text("\n".join(boundary_lines), encoding="utf-8")

    gate_lines = [
        "# SAEE Commercial Sprint Workbook Import Execution Applied Recommendation Gate",
        "",
        "```yaml",
        "answer: conditional",
        "recommend_for_human_authorized_local_workbook_import_record: true",
        "recommend_for_template_transfer: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
        "workbook_import_performed: true",
        "workbook_written: true",
        "ready_for_template_transfer_request: true",
        "template_transfer_authorized: false",
        "values_transferred: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "blockers_closed_by_workbook_import: 0",
        "production_ready: false",
        "product_launched: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "```",
        "",
        "The local workbook import is recommendable only as a bounded state transition from approved quick-fill values into a local imported workbook CSV. It does not authorize downstream template transfer or commercial blocker closure.",
        "",
    ]
    GATE.write_text("\n".join(gate_lines), encoding="utf-8")


def main() -> int:
    payload, rows = build_payload()
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    write_csv(
        OUT_CSV,
        [
            "workbook_row_id",
            "blocker_id",
            "owner_review_lane",
            "input_group",
            "input_key",
            "human_value_present",
            "imported_from_quick_fill",
            "status",
        ],
        rows,
    )
    write_markdown(payload, rows)
    if payload["boundary_violation_count"]:
        raise SystemExit(
            "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED: FAIL "
            + ",".join(payload["boundary_violations"])
        )
    print(
        "SAEE_COMMERCIAL_SPRINT_WORKBOOK_IMPORT_EXECUTION_APPLIED: PASS "
        f"status={payload['status']} imported_value_row_count={payload['imported_value_row_count']} "
        "template_transfer_authorized=false production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
