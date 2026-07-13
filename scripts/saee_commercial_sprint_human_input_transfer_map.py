#!/usr/bin/env python3
"""Build a local transfer map for the commercial sprint human input workbook.

The map records where each workbook field should go in a later human-approved
template-transfer step. It does not copy values, run validators on real input,
collect evidence, execute builders, close blockers, contact anyone, launch
product, or claim production readiness.
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
WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
WORKBOOK_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook.local.json"
VALIDATION_JSON = SPRINT_DIR / "commercial_sprint_human_input_workbook_validation.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_transfer_map_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP_RECOMMENDATION_GATE.md"
)

EXPECTED_ROW_COUNT = 65
EXPECTED_REQUIRED_ROW_COUNT = 64
EXPECTED_BLOCKERS = [
    "support_contact",
    "pricing_page",
    "formal_security_review",
    "production_restore_policy",
    "production_monitoring",
]

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
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "payment_collected",
    "revenue_validated",
]


def as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def target_pointer(row: dict[str, str]) -> str:
    input_group = row["input_group"]
    input_key = row["input_key"]
    if input_group == "first_owner_input":
        return f"/first_owner_input/{input_key}"
    if input_group == "support_contact_decision_metadata":
        return f"/support_contact_decision_input/{input_key}"
    if input_group == "support_contact_evidence_review":
        return f"/support_contact_decision_input/evidence_review/{input_key}"
    if input_group == "support_contact_candidate_slot":
        return f"/support_contact_decision_input/candidate_contact_slots[slot_id={input_key}]"
    if input_group == "metadata_fields_to_fill":
        return f"/{input_key}"
    if input_group == "policy_evidence_keys_to_review":
        return f"/policy_evidence_review/{input_key}"
    if input_group.endswith("_keys_to_review"):
        return f"/evidence_review/{input_key}"
    return f"/{input_group}/{input_key}"


def read_workbook() -> list[dict[str, str]]:
    with WORKBOOK_CSV.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_payload() -> dict[str, Any]:
    workbook = json.loads(WORKBOOK_JSON.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_JSON.read_text(encoding="utf-8"))
    rows = read_workbook()
    if len(rows) != EXPECTED_ROW_COUNT:
        raise SystemExit(f"expected {EXPECTED_ROW_COUNT} workbook rows, found {len(rows)}")

    mapping_rows: list[dict[str, Any]] = []
    target_counts: Counter[str] = Counter()
    target_required_counts: Counter[str] = Counter()
    source_counts: Counter[str] = Counter()

    for row in rows:
        minimum_required = as_bool(row["minimum_required"])
        human_value_present = bool(row["human_value_placeholder"].strip())
        target = row["human_filled_input_target"]
        source = row["source_path"]
        target_counts[target] += 1
        source_counts[source] += 1
        if minimum_required:
            target_required_counts[target] += 1
        mapping_rows.append(
            {
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": row["blocker_id"],
                "owner_review_lane": row["owner_review_lane"],
                "input_group": row["input_group"],
                "input_key": row["input_key"],
                "input_kind": row["input_kind"],
                "minimum_required": minimum_required,
                "human_value_present": human_value_present,
                "transfer_ready": False,
                "source_path": source,
                "source_prompt": row["source_prompt"],
                "human_filled_input_target": target,
                "target_json_pointer": target_pointer(row),
                "transfer_status": "blocked_missing_human_input"
                if minimum_required
                else "optional_not_transferred",
                "value_transferred": False,
            }
        )

    completed_required = validation.get("completed_required_row_count", 0)
    missing_required = validation.get("missing_required_row_count", EXPECTED_REQUIRED_ROW_COUNT)
    ready_for_transfer = (
        completed_required == EXPECTED_REQUIRED_ROW_COUNT
        and missing_required == 0
        and validation.get("workbook_complete") is True
    )
    status = "ready_for_template_transfer" if ready_for_transfer else "hold_human_input_required"

    target_summaries = []
    for target in sorted(target_counts):
        target_summaries.append(
            {
                "human_filled_input_target": target,
                "workbook_row_count": target_counts[target],
                "required_row_count": target_required_counts[target],
                "completed_required_row_count": 0,
                "missing_required_row_count": target_required_counts[target],
                "ready_for_transfer": False,
                "values_transferred": False,
            }
        )

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_transfer_map_v0_1": True,
        "map_type": "local_workbook_to_human_filled_template_mapping",
        "map_scope": "mapping_only_no_value_transfer",
        "status": status,
        "source_workbook_csv": str(WORKBOOK_CSV.relative_to(ROOT)),
        "source_workbook_json": str(WORKBOOK_JSON.relative_to(ROOT)),
        "source_validation_json": str(VALIDATION_JSON.relative_to(ROOT)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_transfer_map.py",
        "selected_blocker_count": workbook.get("selected_blocker_count", 5),
        "selected_blocker_ids": workbook.get("selected_blocker_ids", EXPECTED_BLOCKERS),
        "workbook_row_count": len(rows),
        "required_row_count": EXPECTED_REQUIRED_ROW_COUNT,
        "completed_required_row_count": completed_required,
        "missing_required_row_count": missing_required,
        "target_template_count": len(target_counts),
        "source_template_count": len(source_counts),
        "ready_for_template_transfer": ready_for_transfer,
        "ready_for_existing_local_validators": False,
        "values_transferred": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_transfer_map": 0,
        "boundary_violation_count": 0,
        "boundary_violations": [],
        "target_summaries": target_summaries,
        "mapping_rows": mapping_rows,
        "next_human_action": (
            "Fill missing human_value_placeholder cells first. Template transfer "
            "requires a separate human-approved request after this map reports ready."
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_json(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_csv(payload: dict[str, Any]) -> None:
    fields = [
        "workbook_row_id",
        "blocker_id",
        "owner_review_lane",
        "input_group",
        "input_key",
        "minimum_required",
        "human_value_present",
        "transfer_ready",
        "source_path",
        "human_filled_input_target",
        "target_json_pointer",
        "transfer_status",
        "value_transferred",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["mapping_rows"]:
            writer.writerow({field: row[field] for field in fields})


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Transfer Map",
        "",
        "commercial_sprint_human_input_transfer_map_v0_1: true",
        f"status: {payload['status']}",
        f"map_scope: {payload['map_scope']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"required_row_count: {payload['required_row_count']}",
        f"completed_required_row_count: {payload['completed_required_row_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"target_template_count: {payload['target_template_count']}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"ready_for_existing_local_validators: {str(payload['ready_for_existing_local_validators']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_transfer_map: {payload['blockers_closed_by_transfer_map']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
        "",
        "## Purpose",
        "",
        "This file maps workbook rows to later human-filled input templates. It is",
        "a planning surface only. It does not copy or infer values.",
        "",
        "## Target Templates",
        "",
        "| Target | Rows | Required | Ready for transfer |",
        "| --- | ---: | ---: | --- |",
    ]
    for target in payload["target_summaries"]:
        lines.append(
            "| `{human_filled_input_target}` | {workbook_row_count} | "
            "{required_row_count} | {ready_for_transfer} |".format(**target)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "No workbook value was transferred. No local validator was run on real",
            "input. No evidence builder was executed. No blocker was closed.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Transfer Map Boundary Audit",
        "",
        "commercial_sprint_human_input_transfer_map_v0_1: true",
        f"status: {payload['status']}",
        "map_scope: mapping_only_no_value_transfer",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"target_template_count: {payload['target_template_count']}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_transfer_map: {payload['blockers_closed_by_transfer_map']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
        "",
        "## Confirmed Boundaries",
        "",
    ]
    for flag in FALSE_FLAGS:
        lines.append(f"- {flag}: false")
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Transfer Map v0.1",
        "",
        "commercial_sprint_human_input_transfer_map_v0_1: true",
        f"status: {payload['status']}",
        "map_scope: mapping_only_no_value_transfer",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"required_row_count: {payload['required_row_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"target_template_count: {payload['target_template_count']}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_transfer_map: {payload['blockers_closed_by_transfer_map']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
        "",
        "## Agent Recommendation Gate",
        "",
        "recommendation_gate:",
        "  feature_or_direction: commercial_sprint_human_input_transfer_map",
        "  target_customer_need: safely prepare human input for later evidence validators",
        "  agent_answer: recommend",
        "  reason: This local map reduces transfer ambiguity without copying values or executing evidence work.",
        "  recommend_for_transfer_planning: true",
        "  recommend_for_value_transfer: false",
        "  recommend_for_real_evidence: false",
        "  recommend_for_evidence_collection: false",
        "  recommend_for_automatic_execution: false",
        "  recommend_for_blocker_closure: false",
        "  recommend_for_product_launch: false",
        "  recommend_for_production_readiness_claim: false",
        "",
        "## Boundary",
        "",
        "This map is a local planning surface only. It must not be treated as",
        "evidence collection, template transfer, blocker closure, or launch approval.",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Transfer Map Recommendation Gate",
        "",
        "answer: recommend",
        "recommend_for_transfer_planning: true",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
        "",
        "## Reason",
        "",
        "The transfer map is recommendable as a documentation and planning layer",
        "because it makes later human-approved template transfer auditable without",
        "transferring values now.",
        "",
        "## Boundary",
        "",
        "commercial_sprint_human_input_transfer_map_v0_1: true",
        f"status: {payload['status']}",
        "map_scope: mapping_only_no_value_transfer",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"missing_required_row_count: {payload['missing_required_row_count']}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_input_filled_by_codex: {str(payload['human_input_filled_by_codex']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_transfer_map: {payload['blockers_closed_by_transfer_map']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]
    GATE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    payload = build_payload()
    write_json(payload)
    write_csv(payload)
    write_markdown(payload)
    write_boundary(payload)
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_MAP: PASS "
        f"status={payload['status']} "
        f"workbook_row_count={payload['workbook_row_count']} "
        f"target_template_count={payload['target_template_count']} "
        f"missing_required_row_count={payload['missing_required_row_count']} "
        f"values_transferred={str(payload['values_transferred']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
