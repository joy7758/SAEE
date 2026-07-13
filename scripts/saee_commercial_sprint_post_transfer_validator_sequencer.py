#!/usr/bin/env python3
"""Plan the post-transfer validator sequence for the commercial sprint.

This is a local sequencing surface only. It reads the workbook-to-template
transfer applier status and lists the existing local validators that a human may
run after explicit template transfer approval. It does not run validators,
collect evidence, execute builders, contact anyone, close blockers, launch the
product, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
TRANSFER_APPLIER_JSON = (
    SPRINT_DIR / "commercial_sprint_human_input_template_transfer_applier.local.json"
)
OUT_JSON = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence.csv"
OUT_BOUNDARY = (
    SPRINT_DIR / "commercial_sprint_post_transfer_validator_sequence_boundary_audit.md"
)
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER_RECOMMENDATION_GATE.md"
)

VALIDATOR_STEPS = [
    {
        "sequence_id": "PTV-001",
        "blocker_id": "support_contact",
        "validator_key": "support_contact_approval_input_validator_v0_1",
        "runner": "scripts/saee_support_contact_approval_input_validator.py",
        "smoke": "scripts/saee_support_contact_approval_input_validator_smoke.py",
        "human_filled_input_target": "phase_b_product/commercial_readiness/support_evidence/support_contact_human_input_bridge/support_contact_human_input_bridge_input.human_filled.local.json",
        "validation_output": "phase_b_product/commercial_readiness/support_evidence/support_contact_approval_input_validation.local.json",
    },
    {
        "sequence_id": "PTV-002",
        "blocker_id": "pricing_page",
        "validator_key": "pricing_page_approval_input_validator_v0_1",
        "runner": "scripts/saee_pricing_page_approval_input_validator.py",
        "smoke": "scripts/saee_pricing_page_approval_input_validator_smoke.py",
        "human_filled_input_target": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.human_filled.local.json",
        "validation_output": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_approval_input_validation.local.json",
    },
    {
        "sequence_id": "PTV-003",
        "blocker_id": "formal_security_review",
        "validator_key": "formal_security_review_approval_input_validator_v0_1",
        "runner": "scripts/saee_formal_security_review_approval_input_validator.py",
        "smoke": "scripts/saee_formal_security_review_approval_input_validator_smoke.py",
        "human_filled_input_target": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.human_filled.local.json",
        "validation_output": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_validation.local.json",
    },
    {
        "sequence_id": "PTV-004",
        "blocker_id": "production_restore_policy",
        "validator_key": "production_restore_policy_approval_input_validator_v0_1",
        "runner": "scripts/saee_production_restore_policy_approval_input_validator.py",
        "smoke": "scripts/saee_production_restore_policy_approval_input_validator_smoke.py",
        "human_filled_input_target": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input.human_filled.local.json",
        "validation_output": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_approval_input_validation.local.json",
    },
    {
        "sequence_id": "PTV-005",
        "blocker_id": "production_monitoring",
        "validator_key": "production_monitoring_approval_input_validator_v0_1",
        "runner": "scripts/saee_production_monitoring_approval_input_validator.py",
        "smoke": "scripts/saee_production_monitoring_approval_input_validator_smoke.py",
        "human_filled_input_target": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_evidence_input.human_filled.local.json",
        "validation_output": "phase_b_product/commercial_readiness/operations_evidence/production_monitoring_approval_input_validation.local.json",
    },
]

FALSE_FLAGS = [
    "validators_run",
    "evidence_collection_authorized",
    "execution_authorized",
    "evidence_builder_executed",
    "blocker_closure_authorized",
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
    "payment_collected",
    "revenue_validated",
]


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path.resolve())


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_payload() -> dict[str, Any]:
    transfer_applier = read_json(TRANSFER_APPLIER_JSON)
    template_transfer_complete = (
        transfer_applier.get("human_filled_templates_written") is True
        and transfer_applier.get("values_transferred") is True
        and transfer_applier.get("templates_written_count") == 5
    )
    steps: list[dict[str, Any]] = []
    ready_count = 0
    for step in VALIDATOR_STEPS:
        target_path = ROOT / step["human_filled_input_target"]
        input_exists = target_path.exists()
        ready_for_validator = template_transfer_complete and input_exists
        if ready_for_validator:
            ready_count += 1
        command = f"python3 {step['runner']}"
        steps.append(
            {
                **step,
                "human_filled_input_exists": input_exists,
                "template_transfer_complete": template_transfer_complete,
                "ready_for_validator": ready_for_validator,
                "validator_run": False,
                "validation_status": "not_run",
                "builder_ready": False,
                "blockers_closed_by_validator": 0,
                "recommended_command_after_human_approval": command,
                "separate_validator_approval_required": True,
                "separate_evidence_builder_request_required": True,
            }
        )

    status = (
        "ready_for_separate_validator_approval"
        if ready_count == len(VALIDATOR_STEPS)
        else "hold_template_transfer_required"
    )
    payload: dict[str, Any] = {
        "commercial_sprint_post_transfer_validator_sequencer_v0_1": True,
        "sequencer_type": "controlled_post_transfer_validator_sequence",
        "sequencer_scope": (
            "post_transfer_validator_sequence_only_no_validator_execution_no_evidence"
        ),
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_sprint_post_transfer_validator_sequencer.py",
        "source_transfer_applier_json": rel(TRANSFER_APPLIER_JSON),
        "planned_validator_count": len(VALIDATOR_STEPS),
        "ready_validator_count": ready_count,
        "validators_run_count": 0,
        "builder_ready_count": 0,
        "blockers_closed_by_sequencer": 0,
        "template_transfer_complete": template_transfer_complete,
        "ready_for_validator_approval": ready_count == len(VALIDATOR_STEPS),
        "ready_for_validator_execution": False,
        "ready_for_evidence_builder_execution": False,
        "separate_validator_approval_required": True,
        "separate_evidence_builder_request_required": True,
        "next_human_action": (
            "Fill workbook values, run the quick-fill importer, run the template "
            "transfer applier with explicit human approval, then separately approve "
            "and run the listed local validators."
        ),
        "validator_steps": steps,
        "boundary_violations": [],
        "boundary_violation_count": 0,
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    return payload


def write_csv(path: Path, payload: dict[str, Any]) -> None:
    fields = [
        "sequence_id",
        "blocker_id",
        "validator_key",
        "runner",
        "human_filled_input_target",
        "human_filled_input_exists",
        "template_transfer_complete",
        "ready_for_validator",
        "validator_run",
        "validation_status",
        "builder_ready",
        "blockers_closed_by_validator",
        "recommended_command_after_human_approval",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in payload["validator_steps"]:
            writer.writerow({field: row.get(field) for field in fields})


def write_report(path: Path, payload: dict[str, Any]) -> None:
    rows = "\n".join(
        "| {sequence_id} | {blocker_id} | {runner} | {ready_for_validator} | {validator_run} |".format(
            **step
        )
        for step in payload["validator_steps"]
    )
    path.write_text(
        f"""# Commercial Sprint Post-Transfer Validator Sequencer v0.1

commercial_sprint_post_transfer_validator_sequencer_v0_1: true
sequencer_type: {payload['sequencer_type']}
sequencer_scope: {payload['sequencer_scope']}
status: {payload['status']}
planned_validator_count: {payload['planned_validator_count']}
ready_validator_count: {payload['ready_validator_count']}
validators_run_count: {payload['validators_run_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_sequencer: {payload['blockers_closed_by_sequencer']}
template_transfer_complete: {str(payload['template_transfer_complete']).lower()}
ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
ready_for_evidence_builder_execution: false
separate_validator_approval_required: true
separate_evidence_builder_request_required: true
validators_run: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
boundary_violation_count: 0
production_ready: false
customer_validated: false
product_launched: false

## Validator Sequence

| Sequence | Blocker | Validator command | Ready | Run |
| --- | --- | --- | --- | --- |
{rows}

## Boundary

This file sequences existing local validators only. It does not run validators,
collect evidence, execute evidence builders, contact customers or vendors, close
blockers, launch product, or claim production readiness.
""",
        encoding="utf-8",
    )


def write_boundary(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# Commercial Sprint Post-Transfer Validator Sequencer Boundary Audit

commercial_sprint_post_transfer_validator_sequencer_v0_1: true
status: {payload['status']}
sequencer_scope: {payload['sequencer_scope']}
planned_validator_count: {payload['planned_validator_count']}
ready_validator_count: {payload['ready_validator_count']}
template_transfer_complete: {str(payload['template_transfer_complete']).lower()}
ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
ready_for_evidence_builder_execution: false
separate_validator_approval_required: true
separate_evidence_builder_request_required: true
validators_run_count: 0
builder_ready_count: 0
blockers_closed_by_sequencer: 0
validators_run: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
customer_contacted: false
vendor_contacted: false
external_calls_made: false
external_model_api_called: false
external_ai_assistant_tested: false
boundary_violation_count: 0

Only local post-transfer validator sequencing was generated. No validator was
run on real input by this sequencer, and no evidence builder or blocker closure
step was authorized.
""",
        encoding="utf-8",
    )


def write_top_doc(path: Path, payload: dict[str, Any]) -> None:
    write_report(path, payload)


def write_gate(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(
        f"""# SAEE Commercial Sprint Post-Transfer Validator Sequencer Recommendation Gate

answer: conditional
recommend_for_post_transfer_validator_sequence: true
recommend_for_validator_ordering: true
recommend_for_validator_execution: false
recommend_for_real_input_validation_without_human_approval: false
recommend_for_evidence_collection: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

commercial_sprint_post_transfer_validator_sequencer_v0_1: true
status: {payload['status']}
sequencer_scope: {payload['sequencer_scope']}
planned_validator_count: {payload['planned_validator_count']}
ready_validator_count: {payload['ready_validator_count']}
validators_run_count: 0
builder_ready_count: 0
blockers_closed_by_sequencer: 0
template_transfer_complete: {str(payload['template_transfer_complete']).lower()}
ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
ready_for_evidence_builder_execution: false
separate_validator_approval_required: true
separate_evidence_builder_request_required: true
validators_run: false
evidence_collection_authorized: false
execution_authorized: false
evidence_builder_executed: false
blocker_closure_authorized: false
boundary_violation_count: 0
production_ready: false
customer_validated: false
product_launched: false

Reason: this surface is recommendable only as a local ordering and readiness
layer after template transfer. It is not recommendable as validator execution,
evidence collection, evidence-builder execution, blocker closure, launch, or
production-readiness proof.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUT_JSON, payload)
    write_csv(OUT_CSV, payload)
    write_report(OUT_MD, payload)
    write_boundary(OUT_BOUNDARY, payload)
    write_top_doc(TOP_DOC, payload)
    write_gate(GATE, payload)
    print(
        "SAEE_COMMERCIAL_SPRINT_POST_TRANSFER_VALIDATOR_SEQUENCER: PASS "
        f"status={payload['status']} "
        f"planned_validator_count={payload['planned_validator_count']} "
        f"ready_validator_count={payload['ready_validator_count']} "
        "validators_run=false production_ready=false"
    )


if __name__ == "__main__":
    main()
