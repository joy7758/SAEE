#!/usr/bin/env python3
"""Controlled workbook-to-template transfer applier for the commercial sprint.

Default mode is dry-run only. It reads the commercial sprint workbook and
transfer map, reports whether required human-filled values are ready for
template transfer, and writes only transfer-status artifacts.

Human-filled template files are written only when both `--apply` and
`--confirm-human-approved-transfer` are provided and every required transfer
row has a human value. This script does not run validators on real input,
collect evidence, execute builders, contact anyone, close blockers, launch
product, or claim production readiness.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
DEFAULT_WORKBOOK_CSV = SPRINT_DIR / "commercial_sprint_human_input_workbook.csv"
TRANSFER_MAP_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_map.local.json"
TRANSFER_RESOLVER_JSON = SPRINT_DIR / "commercial_sprint_human_input_transfer_resolver_dry_run.local.json"

OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER_RECOMMENDATION_GATE.md"
)

TARGET_TO_TEMPLATE = {
    "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.template.json",
    "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.template.json",
    "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json",
    "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.template.json",
    "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.template.json",
}

EXPECTED_WORKBOOK_ROW_COUNT = 65
EXPECTED_REQUIRED_ROW_COUNT = 64
EXPECTED_MAPPING_ROW_COUNT = 65

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
    "human_input_filled_by_codex",
    "quick_fill_values_entered_by_codex",
    "validators_run_on_real_input",
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    resolved = path.resolve()
    try:
        return str(resolved.relative_to(ROOT))
    except ValueError:
        return str(resolved)


def parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def decode_pointer_part(raw: str) -> str:
    return raw.replace("~1", "/").replace("~0", "~")


def get_parent_and_key(document: Any, pointer: str) -> tuple[Any, str | int | None]:
    current = document
    parts = [decode_pointer_part(part) for part in pointer.strip("/").split("/")]
    for part in parts[:-1]:
        if "[slot_id=" in part and part.endswith("]"):
            list_name, slot_id = part[:-1].split("[slot_id=", 1)
            items = current[list_name]
            current = next(item for item in items if item.get("slot_id") == slot_id)
            continue
        if isinstance(current, list) and part.isdigit():
            current = current[int(part)]
            continue
        current = current[part]
    final = parts[-1]
    if "[slot_id=" in final and final.endswith("]"):
        list_name, slot_id = final[:-1].split("[slot_id=", 1)
        items = current[list_name]
        current = next(item for item in items if item.get("slot_id") == slot_id)
        return current, None
    if isinstance(current, list) and final.isdigit():
        return current, int(final)
    return current, final


def get_target_value(document: Any, pointer: str) -> Any:
    parent, key = get_parent_and_key(document, pointer)
    if key is None:
        return parent
    return parent[key]


def coerce_value(raw_value: str, current_value: Any) -> Any:
    value = raw_value.strip()
    if isinstance(current_value, bool):
        return value.lower() in {"true", "1", "yes", "y", "approved"}
    if current_value is None:
        lower = value.lower()
        if lower in {"true", "1", "yes", "y", "approved"}:
            return True
        if lower in {"false", "0", "no", "n", "hold"}:
            return False
        return value
    if isinstance(current_value, (int, float)) and value.isdigit():
        return type(current_value)(value)
    if isinstance(current_value, dict):
        updated = copy.deepcopy(current_value)
        updated["human_value"] = value
        updated["reviewed_by_human"] = True
        return updated
    return value


def set_pointer_value(document: Any, pointer: str, raw_value: str) -> None:
    parent, key = get_parent_and_key(document, pointer)
    if key is None:
        replacement = coerce_value(raw_value, parent)
        parent.clear()
        parent.update(replacement)
        return
    parent[key] = coerce_value(raw_value, parent[key])


def mark_template_status(document: Any) -> None:
    if isinstance(document, dict):
        if "input_status" in document:
            document["input_status"] = "human_filled_pending_validator"
        if "review_notes" in document and isinstance(document["review_notes"], str):
            document["review_notes"] = (
                document["review_notes"] + " "
                "Values transferred from human-filled commercial sprint workbook by explicit human-approved local applier."
            ).strip()


def output_path_for(target: str, output_root: Path) -> Path:
    return output_root / target


def build_payload(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any]]:
    workbook_csv = Path(args.workbook_csv)
    output_root = Path(args.output_root)
    workbook_rows = read_csv(workbook_csv)
    transfer_map = json.loads(TRANSFER_MAP_JSON.read_text(encoding="utf-8"))
    resolver = json.loads(TRANSFER_RESOLVER_JSON.read_text(encoding="utf-8"))
    mapping_rows = transfer_map.get("mapping_rows", [])
    workbook_by_id = {row["workbook_row_id"]: row for row in workbook_rows}

    boundary_violations: list[str] = []
    transfer_rows: list[dict[str, Any]] = []
    target_counts: Counter[str] = Counter()
    target_ready_counts: Counter[str] = Counter()
    target_written_counts: Counter[str] = Counter()
    required_value_present_count = 0
    optional_value_present_count = 0
    required_transfer_ready_count = 0
    optional_transfer_ready_count = 0

    if len(workbook_rows) != EXPECTED_WORKBOOK_ROW_COUNT:
        boundary_violations.append("unexpected_workbook_row_count")
    if len(mapping_rows) != EXPECTED_MAPPING_ROW_COUNT:
        boundary_violations.append("unexpected_mapping_row_count")
    if resolver.get("all_pointers_resolved") is not True:
        boundary_violations.append("resolver_pointers_not_all_resolved")
    if resolver.get("values_transferred") is not False:
        boundary_violations.append("resolver_already_transferred_values")

    templates: dict[str, Any] = {}
    for target, template_path in TARGET_TO_TEMPLATE.items():
        templates[target] = json.loads((ROOT / template_path).read_text(encoding="utf-8"))

    for mapped in mapping_rows:
        workbook_row = workbook_by_id.get(mapped["workbook_row_id"], {})
        target = mapped["human_filled_input_target"]
        target_counts[target] += 1
        value = workbook_row.get("human_value_placeholder", "").strip()
        value_present = bool(value)
        required = parse_bool(mapped.get("minimum_required"))
        target_known = target in TARGET_TO_TEMPLATE
        pointer_resolved = False
        if target_known:
            try:
                get_target_value(templates[target], mapped["target_json_pointer"])
                pointer_resolved = True
            except Exception:
                pointer_resolved = False
        if required and value_present:
            required_value_present_count += 1
        if (not required) and value_present:
            optional_value_present_count += 1
        transfer_ready = target_known and pointer_resolved and (value_present or not required)
        if required and transfer_ready:
            required_transfer_ready_count += 1
        if (not required) and transfer_ready:
            optional_transfer_ready_count += 1
        if transfer_ready:
            target_ready_counts[target] += 1
        row_status = (
            "ready_for_apply"
            if required and transfer_ready
            else "ready_optional_blank"
            if (not required) and transfer_ready and not value_present
            else "ready_optional_apply"
            if (not required) and transfer_ready and value_present
            else "hold_missing_human_value"
            if required and not value_present
            else "stop_mapping_or_pointer_issue"
        )
        transfer_rows.append(
            {
                "workbook_row_id": mapped["workbook_row_id"],
                "blocker_id": mapped["blocker_id"],
                "input_group": mapped["input_group"],
                "input_key": mapped["input_key"],
                "minimum_required": required,
                "human_value_present": value_present,
                "human_filled_input_target": target,
                "template_path": TARGET_TO_TEMPLATE.get(target, ""),
                "target_json_pointer": mapped["target_json_pointer"],
                "target_known": target_known,
                "pointer_resolved": pointer_resolved,
                "transfer_ready": transfer_ready,
                "row_status": row_status,
                "value_transferred": False,
                "template_written": False,
            }
        )

    apply_requested = bool(args.apply)
    transfer_confirmation = bool(args.confirm_human_approved_transfer)
    apply_preconditions_met = (
        apply_requested
        and transfer_confirmation
        and not boundary_violations
        and required_transfer_ready_count == EXPECTED_REQUIRED_ROW_COUNT
    )
    if apply_requested and not transfer_confirmation:
        boundary_violations.append("apply_requested_without_human_transfer_confirmation")
    if apply_requested and transfer_confirmation and not apply_preconditions_met:
        boundary_violations.append("apply_requested_without_complete_transfer_readiness")

    if apply_preconditions_met:
        for row in transfer_rows:
            if row["human_value_present"] and row["transfer_ready"]:
                value = workbook_by_id[row["workbook_row_id"]]["human_value_placeholder"]
                set_pointer_value(
                    templates[row["human_filled_input_target"]],
                    row["target_json_pointer"],
                    value,
                )
                row["value_transferred"] = True
        for target, document in templates.items():
            mark_template_status(document)
            path = output_path_for(target, output_root)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            target_written_counts[target] += 1
            for row in transfer_rows:
                if row["human_filled_input_target"] == target:
                    row["template_written"] = True

    templates_written = bool(apply_preconditions_met)
    values_transferred = sum(1 for row in transfer_rows if row["value_transferred"])
    if boundary_violations:
        status = "stop_boundary_or_apply_precondition_violation"
    elif templates_written:
        status = "template_transfer_applied_pending_validator_approval"
    elif required_transfer_ready_count == EXPECTED_REQUIRED_ROW_COUNT:
        status = "ready_for_apply_pending_explicit_human_command"
    else:
        status = "hold_human_input_required"

    target_summaries = []
    for target in sorted(target_counts):
        target_summaries.append(
            {
                "human_filled_input_target": target,
                "template_path": TARGET_TO_TEMPLATE.get(target, ""),
                "mapping_row_count": target_counts[target],
                "transfer_ready_row_count": target_ready_counts[target],
                "template_written": target_written_counts[target] > 0,
                "value_transferred_count": sum(
                    1
                    for row in transfer_rows
                    if row["human_filled_input_target"] == target and row["value_transferred"]
                ),
            }
        )

    payload: dict[str, Any] = {
        "commercial_sprint_human_input_template_transfer_applier_v0_1": True,
        "applier_type": "controlled_workbook_to_human_filled_template_transfer",
        "applier_scope": "workbook_to_template_only_no_validator_no_evidence_no_blocker_closure",
        "status": status,
        "execution_mode": "apply_write_local_human_filled_templates" if templates_written else "dry_run_no_write",
        "source_workbook_csv": rel(workbook_csv),
        "source_transfer_map_json": rel(TRANSFER_MAP_JSON),
        "source_transfer_resolver_json": rel(TRANSFER_RESOLVER_JSON),
        "output_root": rel(output_root),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_human_input_template_transfer_applier.py",
        "workbook_row_count": len(workbook_rows),
        "mapping_row_count": len(mapping_rows),
        "required_row_count": EXPECTED_REQUIRED_ROW_COUNT,
        "required_value_present_count": required_value_present_count,
        "missing_required_value_count": EXPECTED_REQUIRED_ROW_COUNT - required_value_present_count,
        "optional_value_present_count": optional_value_present_count,
        "required_transfer_ready_count": required_transfer_ready_count,
        "optional_transfer_ready_count": optional_transfer_ready_count,
        "target_template_count": len(TARGET_TO_TEMPLATE),
        "apply_requested": apply_requested,
        "human_transfer_confirmation_provided": transfer_confirmation,
        "apply_preconditions_met": apply_preconditions_met,
        "apply_performed": templates_written,
        "values_transferred_count": values_transferred,
        "templates_written_count": len(TARGET_TO_TEMPLATE) if templates_written else 0,
        "ready_for_template_transfer": required_transfer_ready_count == EXPECTED_REQUIRED_ROW_COUNT
        and not boundary_violations,
        "ready_for_existing_local_validators": templates_written,
        "values_transferred": templates_written,
        "human_filled_templates_written": templates_written,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_applier": 0,
        "boundary_violation_count": len(boundary_violations),
        "boundary_violations": boundary_violations,
        "target_summaries": target_summaries,
        "transfer_rows": transfer_rows,
        "next_human_action": (
            "Template transfer is complete. Generate and review the validator approval "
            "request before running any validator separately."
            if templates_written
            else (
                "Fill the commercial sprint workbook first. Use --apply "
                "--confirm-human-approved-transfer only after human approval, then run "
                "the existing local validators separately."
            )
        ),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload, templates


def write_artifacts(payload: dict[str, Any]) -> None:
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    csv_fields = [
        "workbook_row_id",
        "blocker_id",
        "input_group",
        "input_key",
        "minimum_required",
        "human_value_present",
        "human_filled_input_target",
        "template_path",
        "target_json_pointer",
        "target_known",
        "pointer_resolved",
        "transfer_ready",
        "row_status",
        "value_transferred",
        "template_written",
    ]
    with OUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=csv_fields)
        writer.writeheader()
        for row in payload["transfer_rows"]:
            writer.writerow({field: row[field] for field in csv_fields})

    status_lines = [
        "commercial_sprint_human_input_template_transfer_applier_v0_1: true",
        f"status: {payload['status']}",
        f"execution_mode: {payload['execution_mode']}",
        f"applier_scope: {payload['applier_scope']}",
        f"workbook_row_count: {payload['workbook_row_count']}",
        f"mapping_row_count: {payload['mapping_row_count']}",
        f"required_row_count: {payload['required_row_count']}",
        f"required_value_present_count: {payload['required_value_present_count']}",
        f"missing_required_value_count: {payload['missing_required_value_count']}",
        f"required_transfer_ready_count: {payload['required_transfer_ready_count']}",
        f"target_template_count: {payload['target_template_count']}",
        f"apply_requested: {str(payload['apply_requested']).lower()}",
        f"human_transfer_confirmation_provided: {str(payload['human_transfer_confirmation_provided']).lower()}",
        f"apply_performed: {str(payload['apply_performed']).lower()}",
        f"ready_for_template_transfer: {str(payload['ready_for_template_transfer']).lower()}",
        f"ready_for_existing_local_validators: {str(payload['ready_for_existing_local_validators']).lower()}",
        f"values_transferred: {str(payload['values_transferred']).lower()}",
        f"human_filled_templates_written: {str(payload['human_filled_templates_written']).lower()}",
        f"values_transferred_count: {payload['values_transferred_count']}",
        f"templates_written_count: {payload['templates_written_count']}",
        f"validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}",
        f"evidence_collection_authorized: {str(payload['evidence_collection_authorized']).lower()}",
        f"execution_authorized: {str(payload['execution_authorized']).lower()}",
        f"evidence_builder_executed: {str(payload['evidence_builder_executed']).lower()}",
        f"blockers_closed_by_applier: {payload['blockers_closed_by_applier']}",
        f"boundary_violation_count: {payload['boundary_violation_count']}",
        f"production_ready: {str(payload['production_ready']).lower()}",
        f"customer_validated: {str(payload['customer_validated']).lower()}",
        f"product_launched: {str(payload['product_launched']).lower()}",
        f"private_core_exposed: {str(payload['private_core_exposed']).lower()}",
    ]
    status_block = "\n".join(status_lines)

    OUT_MD.write_text(
        "# Commercial Sprint Human Input Template Transfer Applier\n\n"
        f"{status_block}\n\n"
        "## Purpose\n\n"
        "This controlled local applier transfers human-filled workbook values into "
        "the blocker-specific human-filled template files only after explicit "
        "human approval. Default execution is dry-run and writes no template files.\n\n"
        "## Boundary\n\n"
        "Apply mode still does not run validators, collect evidence, execute "
        "builders, close blockers, contact anyone, launch product, or claim "
        "production readiness.\n",
        encoding="utf-8",
    )
    if payload["human_filled_templates_written"]:
        transfer_boundary_lines = [
            "- Apply mode wrote five local human-filled template files after explicit human transfer confirmation.",
            "- Values were transferred from the imported human-filled commercial sprint workbook.",
            "- No values were inferred or entered by Codex.",
        ]
    else:
        transfer_boundary_lines = [
            "- Default mode wrote no human-filled templates.",
            "- No values were inferred or entered by Codex.",
        ]

    OUT_BOUNDARY.write_text(
        "# Commercial Sprint Human Input Template Transfer Applier Boundary Audit\n\n"
        f"{status_block}\n\n"
        + "\n".join(transfer_boundary_lines)
        + "\n"
        "- No validator was run on real input.\n"
        "- No evidence was collected.\n"
        "- No blocker was closed.\n"
        "- No runtime, backend, kernel, API schema, or private core was modified.\n",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        "# SAEE Commercial Sprint Human Input Template Transfer Applier v0.1\n\n"
        f"{status_block}\n\n"
        "This applier is conditionally useful only after human workbook values are "
        "complete and a separate human-approved transfer command is provided. It is "
        "not evidence collection, blocker closure, production readiness, or customer "
        "validation.\n",
        encoding="utf-8",
    )
    GATE.write_text(
        "# SAEE Commercial Sprint Human Input Template Transfer Applier Recommendation Gate\n\n"
        "commercial_sprint_human_input_template_transfer_applier_v0_1: true\n"
        "answer: conditional\n"
        "recommend_for_transfer_readiness_check: true\n"
        "recommend_for_human_approved_template_transfer: true\n"
        "recommend_for_unapproved_transfer: false\n"
        "recommend_for_value_inference: false\n"
        "recommend_for_value_suggestion: false\n"
        "recommend_for_validator_execution: false\n"
        "recommend_for_real_evidence: false\n"
        "recommend_for_evidence_collection: false\n"
        "recommend_for_automatic_execution: false\n"
        "recommend_for_blocker_closure: false\n"
        "recommend_for_product_launch: false\n"
        "recommend_for_production_readiness_claim: false\n\n"
        "## Reason\n\n"
        "The applier is conditionally recommendable as a local transfer utility only "
        "after human workbook completion and explicit human transfer approval. It is "
        "not recommended for autonomous execution or commercial blocker closure.\n\n"
        "## Status\n\n"
        f"{status_block}\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workbook-csv", default=str(DEFAULT_WORKBOOK_CSV))
    parser.add_argument("--output-root", default=str(ROOT))
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--confirm-human-approved-transfer", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload, _ = build_payload(args)
    write_artifacts(payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_TEMPLATE_TRANSFER_APPLIER: PASS "
        f"status={payload['status']} "
        f"execution_mode={payload['execution_mode']} "
        f"required_transfer_ready_count={payload['required_transfer_ready_count']} "
        f"apply_performed={str(payload['apply_performed']).lower()} "
        f"production_ready={str(payload['production_ready']).lower()}"
    )
    return 0 if not payload["boundary_violations"] or not args.apply else 1


if __name__ == "__main__":
    raise SystemExit(main())
