#!/usr/bin/env python3
"""Create a human-fillable workbook for the current commercial sprint.

This workbook consolidates the human input fields for the five selected
commercial evidence sprint blockers. It is a local coordination surface only:
it does not fill fields, run validators, collect evidence, execute builders,
contact anyone, close blockers, launch product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_workbook.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_workbook_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK_RECOMMENDATION_GATE.md"

HANDOFF_JSON = SPRINT_DIR / "commercial_sprint_handoff_pack.local.json"
SUPPORT_BRIDGE_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "support_contact_human_input_bridge/support_contact_human_input_bridge.csv"
)

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
    "vendor_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "development_permission_granted",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
    "task_candidates_executed",
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "human_input_filled_by_codex",
    "validators_run_on_real_input",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "payment_collected",
    "revenue_validated",
]


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def bool_from_csv(value: str) -> bool:
    return value.strip().lower() == "true"


def make_support_rows(start_index: int, handoff_row: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with SUPPORT_BRIDGE_CSV.open(encoding="utf-8", newline="") as handle:
        for raw in csv.DictReader(handle):
            row_number = start_index + len(rows)
            rows.append(
                {
                    "workbook_row_id": f"WB-{row_number:03d}",
                    "blocker_id": "support_contact",
                    "owner_review_lane": handoff_row["owner_review_lane"],
                    "input_group": raw["input_group"],
                    "input_key": raw["input_key"],
                    "input_kind": "support_contact_bridge_field",
                    "human_must_fill": bool_from_csv(raw["human_must_fill"]),
                    "minimum_required": bool_from_csv(raw["minimum_required"]),
                    "codex_may_fill": bool_from_csv(raw["codex_may_fill"]),
                    "human_value_placeholder": "",
                    "source_path": raw["source_path"],
                    "source_prompt": handoff_row["prompt_markdown"],
                    "human_filled_input_target": handoff_row["human_filled_input_target"],
                    "status": "pending_human_input",
                    "notes": raw["notes"],
                }
            )
    return rows


def make_prompt_rows(
    start_index: int, handoff_row: dict[str, Any], prompt_payload: dict[str, Any]
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    source_template = prompt_payload.get("source_template", handoff_row["prompt_json"])
    for list_name, items in prompt_payload.items():
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            input_key = item.get("field_name") or item.get("evidence_key")
            if not input_key:
                continue
            row_number = start_index + len(rows)
            if "field_name" in item:
                input_kind = "metadata_field"
                input_group = "metadata_fields_to_fill"
                minimum_required = bool(item.get("human_must_provide", True))
            else:
                input_kind = "evidence_review_key"
                input_group = list_name
                required_keys = [
                    "human_source_note_required",
                    "owner_named_required",
                    "review_artifact_required",
                    "reviewed_by_human_required",
                    "policy_evidence_slot_required",
                    "monitoring_evidence_slot_required",
                ]
                minimum_required = any(bool(item.get(key)) for key in required_keys)
            rows.append(
                {
                    "workbook_row_id": f"WB-{row_number:03d}",
                    "blocker_id": handoff_row["blocker_id"],
                    "owner_review_lane": handoff_row["owner_review_lane"],
                    "input_group": input_group,
                    "input_key": input_key,
                    "input_kind": input_kind,
                    "human_must_fill": True,
                    "minimum_required": minimum_required,
                    "codex_may_fill": bool(item.get("codex_may_fill", False)),
                    "human_value_placeholder": "",
                    "source_path": source_template,
                    "source_prompt": handoff_row["prompt_markdown"],
                    "human_filled_input_target": handoff_row["human_filled_input_target"],
                    "status": "pending_human_input",
                    "notes": "Human must fill or review this item before validator import.",
                }
            )
    return rows


def write_csv(rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "input_kind",
        "human_must_fill",
        "minimum_required",
        "codex_may_fill",
        "human_value_placeholder",
        "source_path",
        "source_prompt",
        "human_filled_input_target",
        "status",
        "notes",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_md(payload: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    counts = payload["row_counts_by_blocker"]
    lines = [
        "# Commercial Sprint Human Input Workbook",
        "",
        "commercial_sprint_human_input_workbook_v0_1: true",
        f"status: {payload['status']}",
        f"workbook_scope: {payload['workbook_scope']}",
        f"selected_blocker_count: {payload['selected_blocker_count']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        "human_input_required: true",
        "human_input_filled_by_codex: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_workbook: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "## Purpose",
        "",
        "This workbook consolidates the human-fillable input fields for the five",
        "current commercial evidence sprint blockers. It is a local input template",
        "index only.",
        "",
        "## Row Counts",
        "",
        "| Blocker | Rows |",
        "| --- | ---: |",
    ]
    for blocker_id, count in counts.items():
        lines.append(f"| `{blocker_id}` | {count} |")
    lines.extend(
        [
            "",
            "## Workbook Rows",
            "",
            "| Row | Blocker | Group | Key | Kind | Required | Status |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )
    for row in rows:
        lines.append(
            "| {workbook_row_id} | `{blocker_id}` | {input_group} | `{input_key}` | "
            "{input_kind} | {minimum_required} | {status} |".format(**row)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This workbook does not fill inputs, run validators, run evidence builders,",
            "collect evidence, contact customers or vendors, close blockers, launch",
            "product, or claim production readiness.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Workbook Boundary Audit",
        "",
        "commercial_sprint_human_input_workbook_v0_1: true",
        f"status: {payload['status']}",
        f"workbook_scope: {payload['workbook_scope']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        "human_input_filled_by_codex: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "evidence_builder_executed: false",
        "blockers_closed_by_workbook: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "",
        "## Confirmed Boundaries",
        "",
    ]
    for flag in FALSE_FLAGS:
        lines.append(f"- {flag}: false")
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        "\n".join(
            [
                "# SAEE Commercial Sprint Human Input Workbook v0.1",
                "",
                "commercial_sprint_human_input_workbook_v0_1: true",
                f"status: {payload['status']}",
                f"workbook_scope: {payload['workbook_scope']}",
                f"selected_blocker_count: {payload['selected_blocker_count']}",
                f"workbook_row_count: {payload['workbook_row_count']}",
                "human_input_required: true",
                "human_input_filled_by_codex: false",
                "evidence_collection_authorized: false",
                "execution_authorized: false",
                "evidence_builder_executed: false",
                "blockers_closed_by_workbook: 0",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
                "",
                "## Agent Recommendation Gate",
                "",
                "recommendation_gate:",
                "  feature_or_direction: commercial_sprint_human_input_workbook",
                "  target_customer_need: prepare human commercial evidence input without execution",
                "  agent_answer: recommend",
                "  reason: This workbook reduces human input friction for commercial-readiness evidence while preserving all execution and blocker-closure boundaries.",
                "  recommend_for_human_input_preparation: true",
                "  recommend_for_real_evidence: false",
                "  recommend_for_evidence_collection: false",
                "  recommend_for_automatic_execution: false",
                "  recommend_for_blocker_closure: false",
                "  recommend_for_product_launch: false",
                "  recommend_for_production_readiness_claim: false",
                "",
                "## Boundary",
                "",
                "This workbook is a local human input template. It does not execute tasks,",
                "collect evidence, run validators, contact anyone, close blockers, launch",
                "product, or claim production readiness.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        "\n".join(
            [
                "# SAEE Commercial Sprint Human Input Workbook Recommendation Gate",
                "",
                "answer: recommend",
                "recommend_for_human_input_preparation: true",
                "recommend_for_real_evidence: false",
                "recommend_for_evidence_collection: false",
                "recommend_for_automatic_execution: false",
                "recommend_for_blocker_closure: false",
                "recommend_for_product_launch: false",
                "recommend_for_production_readiness_claim: false",
                "",
                "## Reason",
                "",
                "The workbook creates one local human-fillable view over the five selected",
                "commercial sprint blockers without granting Codex execution authority.",
                "",
                "## Boundary",
                "",
                "commercial_sprint_human_input_workbook_v0_1: true",
                f"status: {payload['status']}",
                f"workbook_scope: {payload['workbook_scope']}",
                f"selected_blocker_count: {payload['selected_blocker_count']}",
                f"workbook_row_count: {payload['workbook_row_count']}",
                "human_input_required: true",
                "human_input_filled_by_codex: false",
                "evidence_collection_authorized: false",
                "execution_authorized: false",
                "evidence_builder_executed: false",
                "blockers_closed_by_workbook: 0",
                "production_ready: false",
                "customer_validated: false",
                "product_launched: false",
                "private_core_exposed: false",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    handoff = load_json(HANDOFF_JSON)
    rows: list[dict[str, Any]] = []
    for handoff_row in handoff["rows"]:
        if handoff_row["blocker_id"] == "support_contact":
            rows.extend(make_support_rows(len(rows) + 1, handoff_row))
            continue
        prompt_payload = load_json(ROOT / handoff_row["prompt_json"])
        rows.extend(make_prompt_rows(len(rows) + 1, handoff_row, prompt_payload))

    row_counts: dict[str, int] = {}
    for row in rows:
        row_counts[row["blocker_id"]] = row_counts.get(row["blocker_id"], 0) + 1

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_workbook_v0_1": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_workbook.py",
        "source_handoff_pack": str(HANDOFF_JSON.relative_to(ROOT)),
        "workbook_type": "local_human_input_workbook_for_current_commercial_sprint",
        "workbook_scope": "selected_blocker_human_input_fields_only",
        "status": "hold_human_input_required",
        "selected_blocker_count": handoff["selected_blocker_count"],
        "selected_blocker_ids": [row["blocker_id"] for row in handoff["rows"]],
        "workbook_row_count": len(rows),
        "row_counts_by_blocker": row_counts,
        "human_input_required": True,
        "human_review_required": True,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_workbook": 0,
        "next_human_action": "Fill the workbook rows manually, then copy values into the relevant blocker-specific human-filled input templates before running existing local validators.",
        "rows": rows,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False

    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_csv(rows)
    write_md(payload, rows)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_WORKBOOK: PASS "
        f"status={payload['status']} "
        f"selected_blocker_count={payload['selected_blocker_count']} "
        f"workbook_row_count={payload['workbook_row_count']} "
        f"human_input_filled_by_codex={str(payload['human_input_filled_by_codex']).lower()} "
        f"blockers_closed_by_workbook={payload['blockers_closed_by_workbook']} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
