#!/usr/bin/env python3
"""Build a local human-input bridge for the support_contact blocker.

This script consolidates the existing first-owner input and support-contact
decision input surfaces. It does not configure, publish, test, or collect any
support-contact evidence.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge"
OUT_JSON = OUT_DIR / "support_contact_human_input_bridge.local.json"
OUT_MD = OUT_DIR / "support_contact_human_input_bridge.md"
OUT_CSV = OUT_DIR / "support_contact_human_input_bridge.csv"
OUT_BOUNDARY = OUT_DIR / "support_contact_human_input_bridge_boundary_audit.md"
OUT_README = OUT_DIR / "README.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE_RECOMMENDATION_GATE.md"

FIRST_OWNER_TEMPLATE = (
    ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input.template.json"
)
FIRST_OWNER_STATUS = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/first_owner_input_completion_status.local.json"
)
SUPPORT_DECISION_TEMPLATE = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_decision_input.template.json"
)
SUPPORT_PROMPT = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_prompt.local.json"
)
SUPPORT_READINESS = (
    ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_readiness_board.local.json"
)
NEXT_SUMMARY = (
    ROOT / "phase_b_product/commercial_readiness/commercial_next_action_summary/commercial_next_action_summary.local.json"
)


FALSE_FLAGS = {
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "owner_assigned_by_codex",
    "owner_contacted_by_codex",
    "support_contact_configured_by_codex",
    "support_contact_published_by_codex",
    "support_contact_tested_by_codex",
    "support_contact_available",
    "support_contact_configured",
    "support_contact_published",
    "support_contact_test_performed",
    "support_vendor_contacted",
    "customer_facing_support_contact_configured",
    "customer_support_available",
    "production_support_available",
    "production_support_claim_published",
    "blocker_closure_authorized",
    "blockers_closed_by_bridge",
}


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def input_rows(
    first_owner_fields: list[str],
    metadata_fields: list[dict[str, Any]],
    evidence_keys: list[dict[str, Any]],
    candidate_slots: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for field in first_owner_fields:
        rows.append(
            {
                "input_group": "first_owner_input",
                "input_key": field,
                "human_must_fill": True,
                "codex_may_fill": False,
                "minimum_required": True,
                "source_path": str(FIRST_OWNER_TEMPLATE.relative_to(ROOT)),
                "notes": "Required before validator import; does not assign an owner by Codex.",
            }
        )
    for field in metadata_fields:
        rows.append(
            {
                "input_group": "support_contact_decision_metadata",
                "input_key": field["field_name"],
                "human_must_fill": True,
                "codex_may_fill": False,
                "minimum_required": True,
                "source_path": str(SUPPORT_DECISION_TEMPLATE.relative_to(ROOT)),
                "notes": "Human review metadata for support contact decision input.",
            }
        )
    for item in evidence_keys:
        rows.append(
            {
                "input_group": "support_contact_evidence_review",
                "input_key": item["evidence_key"],
                "human_must_fill": True,
                "codex_may_fill": False,
                "minimum_required": True,
                "source_path": str(SUPPORT_DECISION_TEMPLATE.relative_to(ROOT)),
                "notes": "Set true only after human source note and review.",
            }
        )
    for slot in candidate_slots:
        rows.append(
            {
                "input_group": "support_contact_candidate_slot",
                "input_key": slot["slot_id"],
                "human_must_fill": True,
                "codex_may_fill": False,
                "minimum_required": slot["slot_id"] == "support_contact_candidate_a",
                "source_path": str(SUPPORT_DECISION_TEMPLATE.relative_to(ROOT)),
                "notes": "At least one candidate slot must be completed by a human.",
            }
        )
    return rows


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
        "input_group",
        "input_key",
        "human_must_fill",
        "codex_may_fill",
        "minimum_required",
        "source_path",
        "notes",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict[str, Any]]) -> str:
    lines = [
        "| Group | Input | Required | Codex may fill | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows:
        lines.append(
            "| {input_group} | {input_key} | {minimum_required} | {codex_may_fill} | {source_path} |".format(
                **row
            )
        )
    return "\n".join(lines)


def build_payload() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    first_owner = read_json(FIRST_OWNER_TEMPLATE)
    support_prompt = read_json(SUPPORT_PROMPT)
    support_template = read_json(SUPPORT_DECISION_TEMPLATE)
    support_readiness = read_json(SUPPORT_READINESS)
    next_summary = read_json(NEXT_SUMMARY)
    first_owner_status = read_json(FIRST_OWNER_STATUS)

    first_owner_fields = first_owner.get("required_human_fields", [])
    metadata_fields = support_prompt.get("metadata_fields_to_fill", [])
    evidence_keys = support_prompt.get("support_contact_evidence_keys_to_review", [])
    candidate_slots = support_prompt.get("candidate_contact_slots_to_fill", [])
    rows = input_rows(first_owner_fields, metadata_fields, evidence_keys, candidate_slots)

    payload: dict[str, Any] = {
        "support_contact_human_input_bridge_v0_1": True,
        "bridge_type": "saee_support_contact_human_input_bridge",
        "bridge_scope": "local_human_input_consolidation_only",
        "status": "hold_combined_human_input_required",
        "commercial_status": "hold",
        "target_blocker_id": "support_contact",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "open_blocker_count": 24,
        "first_owner_input_status": first_owner_status.get("status"),
        "support_contact_readiness_status": support_readiness.get("status"),
        "next_action_summary_status": next_summary.get("status"),
        "first_owner_required_field_count": len(first_owner_fields),
        "support_contact_required_metadata_field_count": len(metadata_fields),
        "support_contact_required_evidence_key_count": len(evidence_keys),
        "candidate_contact_slot_count": len(candidate_slots),
        "minimum_candidate_contact_slot_count": support_prompt.get("minimum_completed_contact_slot_count", 1),
        "combined_input_row_count": len(rows),
        "completed_input_row_count": 0,
        "human_input_required": True,
        "human_review_required": True,
        "requires_separate_validator": True,
        "requires_separate_evidence_collection_request": True,
        "requires_separate_blocker_closure_approval": True,
        "recommended_default_decision": "hold",
        "next_human_action": (
            "Fill the first-owner input, run the first-owner validator, then fill the "
            "support-contact decision input and run its validator. Do not configure, publish, "
            "test, collect evidence, or close blockers without a separate approved request."
        ),
        "source_paths": {
            "first_owner_template": str(FIRST_OWNER_TEMPLATE.relative_to(ROOT)),
            "first_owner_status": str(FIRST_OWNER_STATUS.relative_to(ROOT)),
            "support_contact_decision_template": str(SUPPORT_DECISION_TEMPLATE.relative_to(ROOT)),
            "support_contact_approval_prompt": str(SUPPORT_PROMPT.relative_to(ROOT)),
            "support_contact_readiness_board": str(SUPPORT_READINESS.relative_to(ROOT)),
            "commercial_next_action_summary": str(NEXT_SUMMARY.relative_to(ROOT)),
        },
        "input_rows": rows,
        "support_contact_decision_template_snapshot": {
            "template_type": support_template.get("template_type"),
            "template_version": support_template.get("template_version"),
            "input_status": support_template.get("input_status"),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_support_contact_human_input_bridge.py",
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_bridge"] = 0
    return payload, rows


def write_docs(payload: dict[str, Any], rows: list[dict[str, Any]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, rows)

    table = md_table(rows)
    shared_status = f"""support_contact_human_input_bridge_v0_1: true
status: hold_combined_human_input_required
bridge_scope: local_human_input_consolidation_only
target_blocker_id: support_contact
first_owner_required_field_count: {payload['first_owner_required_field_count']}
support_contact_required_metadata_field_count: {payload['support_contact_required_metadata_field_count']}
support_contact_required_evidence_key_count: {payload['support_contact_required_evidence_key_count']}
candidate_contact_slot_count: {payload['candidate_contact_slot_count']}
combined_input_row_count: {payload['combined_input_row_count']}
completed_input_row_count: 0
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_bridge: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false"""

    OUT_MD.write_text(
        f"""# Support Contact Human Input Bridge v0.1

{shared_status}

## Purpose

This bridge consolidates the existing `support_contact` first-owner input and
support-contact decision input into one human-readable worksheet surface.

It does not configure or publish a support contact, send a support test, collect
production evidence, close a blocker, contact customers or vendors, launch the
product, or claim production readiness.

## Human Input Rows

{table}

## Next Human Action

{payload['next_human_action']}
""",
        encoding="utf-8",
    )

    OUT_BOUNDARY.write_text(
        f"""# Support Contact Human Input Bridge Boundary Audit

{shared_status}

## Confirmed Boundaries

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- private_core_exposed: false
- product_launched: false
- production_ready: false
- customer_validated: false
- customer_contacted: false
- external_calls_made: false
- external_model_api_called: false
- external_ai_assistant_tested: false
- support_contact_configured_by_codex: false
- support_contact_published_by_codex: false
- support_contact_tested_by_codex: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_bridge: 0

Final boundary decision: local human-input consolidation only.
""",
        encoding="utf-8",
    )

    OUT_README.write_text(
        f"""# Support Contact Human Input Bridge

{shared_status}

Use this folder when a human reviewer needs one place to see the required
`support_contact` first-owner input and support-contact decision input.

This folder is not an execution surface. It does not configure support, publish
contact information, send tests, collect evidence, close blockers, or change
product readiness status.
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        f"""# SAEE Support Contact Human Input Bridge v0.1

{shared_status}

## Agent Recommendation Gate

recommendation_gate:
  feature_or_direction: support_contact_human_input_bridge
  target_customer_need: human-readable consolidation of support_contact commercial readiness inputs
  answer: recommend
  reasons_to_recommend:
    - It reduces handoff ambiguity for the current `support_contact` blocker.
    - It keeps all execution, evidence collection, publication, and blocker closure false.
  reasons_not_to_recommend:
    - It does not itself make support contact production-ready.
    - It still requires human-filled evidence and separate validators.
  final_decision: recommend_for_human_input_consolidation_only

## Scope

This is a local bridge for human input. It is not customer support, not evidence
collection, not execution, not blocker closure, and not production readiness.
""",
        encoding="utf-8",
    )

    GATE.write_text(
        f"""# SAEE Support Contact Human Input Bridge Recommendation Gate

answer: recommend
recommend_for_human_input_consolidation: true
recommend_for_support_contact_configuration: false
recommend_for_support_contact_publication: false
recommend_for_support_testing: false
recommend_for_evidence_collection: false
recommend_for_automatic_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

reason: The bridge makes the current `support_contact` human input path easier
to review without granting Codex permission to configure, publish, test, collect
evidence, close blockers, launch product, or claim production readiness.

{shared_status}
""",
        encoding="utf-8",
    )


def main() -> int:
    payload, rows = build_payload()
    write_docs(payload, rows)
    print(
        "SAEE_SUPPORT_CONTACT_HUMAN_INPUT_BRIDGE: PASS "
        "status=hold_combined_human_input_required "
        f"combined_input_row_count={payload['combined_input_row_count']} "
        "blockers_closed_by_bridge=0 production_ready=false"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
