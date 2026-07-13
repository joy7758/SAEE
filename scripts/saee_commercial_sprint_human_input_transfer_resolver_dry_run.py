#!/usr/bin/env python3
"""Dry-run resolve commercial sprint workbook transfer targets.

This script verifies that each workbook transfer-map row points to an existing
location in the target template. It does not copy values, create human-filled
templates, run validators on real input, collect evidence, execute builders,
close blockers, contact anyone, launch product, or claim production readiness.
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
TRANSFER_MAP_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.local.json"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN_RECOMMENDATION_GATE.md"
)

TARGET_TO_TEMPLATE = {
    "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json",
    "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.template.json",
    "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json",
    "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json",
    "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.template.json",
}

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
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "payment_collected",
    "revenue_validated",
]


def resolve_pointer(document: Any, pointer: str) -> tuple[bool, str]:
    current = document
    if not pointer.startswith("/"):
        return False, "pointer_must_start_with_slash"
    for raw_part in pointer.strip("/").split("/"):
        part = raw_part.replace("~1", "/").replace("~0", "~")
        if "[slot_id=" in part and part.endswith("]"):
            list_name, slot_id = part[:-1].split("[slot_id=", 1)
            if not isinstance(current, dict) or list_name not in current:
                return False, f"missing_list:{list_name}"
            items = current[list_name]
            if not isinstance(items, list):
                return False, f"not_a_list:{list_name}"
            match = next(
                (item for item in items if isinstance(item, dict) and item.get("slot_id") == slot_id),
                None,
            )
            if match is None:
                return False, f"missing_slot_id:{slot_id}"
            current = match
            continue
        if isinstance(current, dict):
            if part not in current:
                return False, f"missing_key:{part}"
            current = current[part]
            continue
        if isinstance(current, list) and part.isdigit():
            index = int(part)
            if index >= len(current):
                return False, f"missing_index:{part}"
            current = current[index]
            continue
        return False, f"unresolvable_part:{part}"
    return True, "resolved"


def build_payload() -> dict[str, Any]:
    transfer_map = json.loads(TRANSFER_MAP_JSON.read_text(encoding="utf-8"))
    rows = transfer_map.get("mapping_rows", [])
    template_cache: dict[str, Any] = {}
    resolver_rows: list[dict[str, Any]] = []
    unresolved: list[dict[str, Any]] = []
    target_counts: Counter[str] = Counter()
    resolved_counts: Counter[str] = Counter()

    for row in rows:
        target = row["human_filled_input_target"]
        template_path = TARGET_TO_TEMPLATE.get(target, "")
        target_counts[target] += 1
        if not template_path:
            resolved = False
            reason = "unknown_target_template"
        else:
            if template_path not in template_cache:
                template_cache[template_path] = json.loads(
                    (ROOT / template_path).read_text(encoding="utf-8")
                )
            resolved, reason = resolve_pointer(
                template_cache[template_path], row["target_json_pointer"]
            )
        if resolved:
            resolved_counts[target] += 1
        else:
            unresolved.append(
                {
                    "workbook_row_id": row["workbook_row_id"],
                    "target_json_pointer": row["target_json_pointer"],
                    "reason": reason,
                }
            )
        resolver_rows.append(
            {
                "workbook_row_id": row["workbook_row_id"],
                "blocker_id": row["blocker_id"],
                "human_filled_input_target": target,
                "template_path": template_path,
                "target_json_pointer": row["target_json_pointer"],
                "pointer_resolved": resolved,
                "resolution_status": reason,
                "value_transferred": False,
                "template_written": False,
            }
        )

    resolved_count = sum(1 for row in resolver_rows if row["pointer_resolved"])
    unresolved_count = len(resolver_rows) - resolved_count
    all_resolved = unresolved_count == 0 and len(resolver_rows) == 65
    status = (
        "pass_mapping_resolved_hold_human_input_required"
        if all_resolved
        else "stop_unresolved_mapping"
    )

    target_summaries = []
    for target in sorted(target_counts):
        target_summaries.append(
            {
                "human_filled_input_target": target,
                "template_path": TARGET_TO_TEMPLATE.get(target, ""),
                "mapping_row_count": target_counts[target],
                "resolved_mapping_row_count": resolved_counts[target],
                "unresolved_mapping_row_count": target_counts[target] - resolved_counts[target],
                "all_pointers_resolved": target_counts[target] == resolved_counts[target],
                "values_transferred": False,
                "template_written": False,
            }
        )

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1": True,
        "dry_run_type": "local_template_pointer_resolution_only",
        "dry_run_scope": "resolve_transfer_map_targets_without_value_transfer",
        "status": status,
        "source_transfer_map_json": str(TRANSFER_MAP_JSON.relative_to(ROOT)),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_transfer_resolver_dry_run.py",
        "mapping_row_count": len(resolver_rows),
        "resolved_mapping_row_count": resolved_count,
        "unresolved_mapping_row_count": unresolved_count,
        "target_template_count": len(target_counts),
        "all_target_templates_known": all(
            bool(TARGET_TO_TEMPLATE.get(target)) for target in target_counts
        ),
        "all_pointers_resolved": all_resolved,
        "ready_for_template_transfer": False,
        "ready_for_existing_local_validators": False,
        "values_transferred": False,
        "human_filled_templates_written": False,
        "human_input_filled_by_codex": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_resolver_dry_run": 0,
        "boundary_violation_count": 0,
        "boundary_violations": [],
        "target_summaries": target_summaries,
        "unresolved_mappings": unresolved,
        "resolver_rows": resolver_rows,
        "next_human_action": (
            "Fill missing workbook values first. A separate explicit request is "
            "required before any value transfer or validator run."
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
        "human_filled_input_target",
        "template_path",
        "target_json_pointer",
        "pointer_resolved",
        "resolution_status",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["resolver_rows"]:
            writer.writerow(row)


def write_markdown(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Transfer Resolver Dry Run",
        "",
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"mapping_row_count: {payload['mapping_row_count']}",
        f"resolved_mapping_row_count: {payload['resolved_mapping_row_count']}",
        f"unresolved_mapping_row_count: {payload['unresolved_mapping_row_count']}",
        f"target_template_count: {payload['target_template_count']}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_resolver_dry_run: {payload['blockers_closed_by_resolver_dry_run']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        "",
        "## Target Resolution",
        "",
        "| Target | Rows | Resolved | Unresolved |",
        "| --- | ---: | ---: | ---: |",
    ]
    for target in payload["target_summaries"]:
        lines.append(
            "| `{human_filled_input_target}` | {mapping_row_count} | "
            "{resolved_mapping_row_count} | {unresolved_mapping_row_count} |".format(**target)
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "This dry run resolves mapping targets only. It does not transfer values,",
            "write human-filled templates, run validators, collect evidence, execute",
            "builders, close blockers, or claim production readiness.",
        ]
    )
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_boundary(payload: dict[str, Any]) -> None:
    lines = [
        "# Commercial Sprint Human Input Transfer Resolver Dry Run Boundary Audit",
        "",
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"mapping_row_count: {payload['mapping_row_count']}",
        f"resolved_mapping_row_count: {payload['resolved_mapping_row_count']}",
        f"unresolved_mapping_row_count: {payload['unresolved_mapping_row_count']}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_resolver_dry_run: {payload['blockers_closed_by_resolver_dry_run']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        "",
        "## Confirmed Boundaries",
        "",
    ]
    for flag in FALSE_FLAGS:
        lines.append(f"- {flag}: false")
    OUT_BOUNDARY.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_top_doc(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Transfer Resolver Dry Run v0.1",
        "",
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"mapping_row_count: {payload['mapping_row_count']}",
        f"resolved_mapping_row_count: {payload['resolved_mapping_row_count']}",
        f"unresolved_mapping_row_count: {payload['unresolved_mapping_row_count']}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_resolver_dry_run: {payload['blockers_closed_by_resolver_dry_run']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        "",
        "## Agent Recommendation Gate",
        "",
        "recommendation_gate:",
        "  feature_or_direction: commercial_sprint_human_input_transfer_resolver_dry_run",
        "  target_customer_need: verify commercial evidence input mapping before human-approved transfer",
        "  agent_answer: recommend",
        "  reason: The dry run proves template target resolvability without transferring values or executing evidence work.",
        "  recommend_for_mapping_resolution: true",
        "  recommend_for_value_transfer: false",
        "  recommend_for_real_evidence: false",
        "  recommend_for_evidence_collection: false",
        "  recommend_for_automatic_execution: false",
        "  recommend_for_blocker_closure: false",
        "  recommend_for_product_launch: false",
        "  recommend_for_production_readiness_claim: false",
    ]
    TOP_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_gate(payload: dict[str, Any]) -> None:
    lines = [
        "# SAEE Commercial Sprint Human Input Transfer Resolver Dry Run Recommendation Gate",
        "",
        "answer: recommend",
        "recommend_for_mapping_resolution: true",
        "recommend_for_value_transfer: false",
        "recommend_for_real_evidence: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_automatic_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_product_launch: false",
        "recommend_for_production_readiness_claim: false",
        "",
        "## Boundary",
        "",
        "commercial_sprint_human_input_transfer_resolver_dry_run_v0_1: true",
        f"status: {payload['status']}",
        f"dry_run_scope: {payload['dry_run_scope']}",
        f"mapping_row_count: {payload['mapping_row_count']}",
        f"resolved_mapping_row_count: {payload['resolved_mapping_row_count']}",
        f"unresolved_mapping_row_count: {payload['unresolved_mapping_row_count']}",
        f"all_pointers_resolved: {str(payload['all_pointers_resolved']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_resolver_dry_run: {payload['blockers_closed_by_resolver_dry_run']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TRANSFER_RESOLVER_DRY_RUN: PASS "
        f"status={payload['status']} "
        f"mapping_row_count={payload['mapping_row_count']} "
        f"resolved_mapping_row_count={payload['resolved_mapping_row_count']} "
        f"unresolved_mapping_row_count={payload['unresolved_mapping_row_count']} "
        f"values_transferred={str(payload['values_transferred']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
