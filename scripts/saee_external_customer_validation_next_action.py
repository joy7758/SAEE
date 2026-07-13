#!/usr/bin/env python3
"""Create the next-action packet for the remaining customer validation blocker.

This records the safest next human action after local commercial evidence has
passed inspection: collect real external customer or target-user feedback, then
run the existing customer-validation input validator. It does not contact
customers, run pilots, infer feedback, execute builders, close blockers, launch
SAEE, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
FINAL_INSPECTION = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_final_human_inspection/"
    "commercial_final_human_inspection_record.local.json"
)
PROMPT_JSON = EVIDENCE_DIR / "customer_validation_approval_input_prompt.local.json"
VALIDATOR_JSON = EVIDENCE_DIR / "customer_validation_approval_input_validation.local.json"
TEMPLATE_JSON = EVIDENCE_DIR / "customer_validation_evidence_input.template.json"
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "customer_validation_evidence_input.human_filled.local.json"
SESSION_ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
SESSION_ENTRY_WORKBENCH = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.html"
SESSION_ENTRY_HUMAN_FILLED = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"

OUTPUT_JSON = EVIDENCE_DIR / "external_customer_validation_next_action.local.json"
OUTPUT_MD = EVIDENCE_DIR / "external_customer_validation_next_action.md"
OUTPUT_CSV = EVIDENCE_DIR / "external_customer_validation_next_action_checklist.csv"
BOUNDARY_AUDIT = EVIDENCE_DIR / "external_customer_validation_next_action_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"


FALSE_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "customer_contacted_by_codex": False,
    "automated_customer_contact": False,
    "customer_data_collected_by_codex": False,
    "customer_secrets_collected": False,
    "customer_data_uploaded": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "revenue_validated": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized_by_codex": False,
    "evidence_builder_executed": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_next_action": 0,
}


CHECKLIST_ROWS = [
    {
        "step_id": "CV-001",
        "human_action": "Open the facilitator page and result-entry workbench.",
        "required_evidence": "facilitator page plus external_customer_validation_session_entry_workbench.html",
        "codex_allowed": False,
        "stop_condition": "Do not let Codex run the external session or invent feedback.",
    },
    {
        "step_id": "CV-002",
        "human_action": "Run at least one real external customer or target-user demo/interview.",
        "required_evidence": "participant role, team type, current evaluation method, session date, and notes",
        "codex_allowed": False,
        "stop_condition": "No automated contact, no scraping, no external assistant calls.",
    },
    {
        "step_id": "CV-003",
        "human_action": "Record scores for understanding, trust, decision influence, and repeat usage intent.",
        "required_evidence": "all required scores in range 1-5",
        "codex_allowed": False,
        "stop_condition": "Do not infer scores from vague feedback.",
    },
    {
        "step_id": "CV-004",
        "human_action": "Confirm all boundary flags remain false.",
        "required_evidence": "no secrets, no production data, no customer upload, no private core disclosure, no production-ready claim",
        "codex_allowed": False,
        "stop_condition": "Stop if any boundary flag becomes true.",
    },
    {
        "step_id": "CV-005",
        "human_action": "Save the generated session-entry JSON at the required human output path.",
        "required_evidence": "external_customer_validation_session_entry.human_filled.local.json",
        "codex_allowed": False,
        "stop_condition": "Do not save internal self-review as external customer feedback.",
    },
    {
        "step_id": "CV-006",
        "human_action": "Run the existing post-session processor after the human-filled session entry exists.",
        "required_evidence": "external_customer_validation_post_session_processor.local.json with processed status",
        "codex_allowed": True,
        "stop_condition": "Processor pass still does not publish a claim or close the blocker by itself.",
    },
    {
        "step_id": "CV-007",
        "human_action": "Request a separate commercial go/no-go update only after processor outputs are reviewed.",
        "required_evidence": "separate explicit human go/no-go update request",
        "codex_allowed": False,
        "stop_condition": "No customer-validation or production-ready claim in this next-action packet.",
    },
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION: "
            f"FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION: "
            f"FAIL JSON root must be object: {rel(path)}"
        )
    return payload


def build_payload() -> dict[str, Any]:
    inspection = read_json(FINAL_INSPECTION)
    prompt = read_json(PROMPT_JSON)
    validator = read_json(VALIDATOR_JSON)
    blockers = inspection.get("remaining_production_blockers_after_local_human_evidence")
    if blockers != ["customer_validated"]:
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION: "
            "FAIL final inspection must leave only customer_validated"
        )
    if inspection.get("local_evidence_lanes_passed") is not True:
        raise SystemExit(
            "SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION: "
            "FAIL local evidence lanes must pass before next action packet"
        )

    payload: dict[str, Any] = {
        "external_customer_validation_next_action_v0_1": True,
        "status": "hold_external_customer_validation_input_required",
        "record_type": "external_customer_validation_next_action_packet",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_external_customer_validation_next_action.py",
        "source_final_human_inspection": rel(FINAL_INSPECTION),
        "source_customer_validation_prompt": rel(PROMPT_JSON),
        "source_customer_validation_validator_output": rel(VALIDATOR_JSON),
        "source_customer_validation_template": rel(TEMPLATE_JSON),
        "source_session_entry_template": rel(SESSION_ENTRY_TEMPLATE),
        "result_entry_workbench": rel(SESSION_ENTRY_WORKBENCH),
        "required_human_output": rel(SESSION_ENTRY_HUMAN_FILLED),
        "human_session_entry_exists": SESSION_ENTRY_HUMAN_FILLED.exists(),
        "ready_for_post_session_processor": SESSION_ENTRY_HUMAN_FILLED.exists(),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "current_goal_blocker": "customer_validated",
        "remaining_blocker_count": 1,
        "local_evidence_lanes_passed": True,
        "local_evidence_lane_count": inspection.get("local_evidence_lane_count", 0),
        "existing_prompt_status": prompt.get("status"),
        "existing_validator_status": validator.get("validation_status"),
        "required_real_external_sessions_min": 1,
        "required_review_key_count": prompt.get("required_review_key_count", 25),
        "required_session_text_field_count": prompt.get("required_session_text_field_count", 5),
        "required_session_score_field_count": prompt.get("required_session_score_field_count", 4),
        "required_boundary_false_key_count": prompt.get(
            "required_session_boundary_false_key_count", 5
        ),
        "human_external_customer_validation_path_ready": True,
        "human_action_required": True,
        "codex_may_contact_customer": False,
        "codex_may_run_external_pilot": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_run_validator_after_human_filled_input": True,
        "separate_evidence_builder_request_required": True,
        "separate_commercial_go_no_go_update_required": True,
        "customer_validation_claim_allowed": False,
        "production_readiness_claim_allowed": False,
        "copy_template_command": f"cp {rel(SESSION_ENTRY_TEMPLATE)} {rel(SESSION_ENTRY_HUMAN_FILLED)}",
        "validator_command_after_human_fill": (
            "python3 scripts/saee_customer_validation_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "post_session_processor_command": (
            "python3 scripts/saee_external_customer_validation_post_session_processor.py"
        ),
        "builder_command_after_separate_approval": (
            "python3 scripts/saee_customer_validation_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "next_human_action": (
            "Collect at least one real external customer or target-user validation "
            "session, use the result-entry workbench to save the human-filled "
            "session-entry JSON, then run the post-session processor. Do not "
            "claim customer validation or production readiness until a later "
            "approved go/no-go update."
        ),
        "checklist": CHECKLIST_ROWS,
        **FALSE_FLAGS,
    }
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    rows = "\n".join(
        "| {step_id} | {human_action} | {required_evidence} | {codex_allowed} | {stop_condition} |".format(
            **row
        )
        for row in payload["checklist"]
    )
    return f"""# SAEE External Customer Validation Next Action v0.1

Status: {payload['status']}.

This is the next-action packet for the remaining formal commercial blocker:
`customer_validated`. It does not contact customers, run an external pilot,
collect customer data, execute the evidence builder, close blockers, launch
SAEE, or claim production readiness.

## Current State

```yaml
external_customer_validation_next_action_v0_1: true
status: {payload['status']}
current_goal_blocker: customer_validated
remaining_blocker_count: 1
local_evidence_lanes_passed: true
human_external_customer_validation_path_ready: true
result_entry_workbench: {payload['result_entry_workbench']}
required_human_output: {payload['required_human_output']}
human_session_entry_exists: {str(payload['human_session_entry_exists']).lower()}
customer_validated: false
production_ready: false
product_launched: false
customer_contacted: false
private_core_exposed: false
blockers_closed_by_next_action: 0
```

## Human Procedure

1. Human tester opens the facilitator page and runs at least one real external
   customer or target-user demo or interview. Codex must not contact the
   participant.
2. Human tester opens the result-entry workbench:

`{payload['result_entry_workbench']}`

3. Human tester saves the generated JSON as:

`{payload['required_human_output']}`

4. Run the existing post-session processor only after that real human-filled
   session-entry file exists:

```bash
{payload['post_session_processor_command']}
```

5. Stop. A processor pass still requires a separate commercial go/no-go update
   before any customer-validation or production-readiness claim.

## Checklist

| Step | Human Action | Required Evidence | Codex Allowed | Stop Condition |
| --- | --- | --- | --- | --- |
{rows}

## Boundary

- codex_may_contact_customer=false
- codex_may_run_external_pilot=false
- codex_may_infer_customer_feedback=false
- evidence_builder_executed=false
- customer_validation_claim_allowed=false
- production_readiness_claim_allowed=false
- customer_validated=false
- production_ready=false
- product_launched=false
- private_core_exposed=false
"""


def render_boundary(payload: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Next Action Boundary Audit

Final boundary decision: hold, human external customer validation input required.

- Runtime modified: {str(payload['runtime_modified']).lower()}
- Backend modified: {str(payload['backend_modified']).lower()}
- Kernel modified: {str(payload['kernel_modified']).lower()}
- API schema modified: {str(payload['api_schema_modified']).lower()}
- Private core exposed: {str(payload['private_core_exposed']).lower()}
- Product launched: {str(payload['product_launched']).lower()}
- Production-ready claim allowed: {str(payload['production_readiness_claim_allowed']).lower()}
- Customer validated: {str(payload['customer_validated']).lower()}
- Customer contacted by Codex: {str(payload['customer_contacted_by_codex']).lower()}
- Codex may contact customer: {str(payload['codex_may_contact_customer']).lower()}
- Codex may run external pilot: {str(payload['codex_may_run_external_pilot']).lower()}
- Codex may infer customer feedback: {str(payload['codex_may_infer_customer_feedback']).lower()}
- Evidence builder executed: {str(payload['evidence_builder_executed']).lower()}
- Blockers closed by next action: {payload['blockers_closed_by_next_action']}
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Next Action Gate

answer: hold_external_customer_validation_input_required

reason: Local commercial evidence and final human inspection are complete, but
formal commercial readiness still requires real external customer or target-user
validation. This packet makes the next human action explicit without authorizing
Codex to contact customers, run pilots, execute builders, close blockers, or
claim validation.

status: {payload['status']}
current_goal_blocker: customer_validated
remaining_blocker_count: 1
human_external_customer_validation_path_ready: true
codex_may_contact_customer: false
codex_may_run_external_pilot: false
codex_may_infer_customer_feedback: false
codex_may_run_validator_after_human_filled_input: true
separate_evidence_builder_request_required: true
separate_commercial_go_no_go_update_required: true

boundary:
customer_validated: false
production_ready: false
product_launched: false
customer_contacted: false
private_core_exposed: false
customer_validation_claim_allowed: false
production_readiness_claim_allowed: false
blockers_closed_by_next_action: 0

next_action: Human collects and records at least one real external customer or
target-user validation session, then runs the existing validator on the
human-filled input.
"""


def write_outputs(payload: dict[str, Any]) -> None:
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary(payload), encoding="utf-8")
    GATE.write_text(render_gate(payload), encoding="utf-8")
    with OUTPUT_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "step_id",
                "human_action",
                "required_evidence",
                "codex_allowed",
                "stop_condition",
            ],
        )
        writer.writeheader()
        writer.writerows(payload["checklist"])
    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    existing = index.get("external_customer_validation_next_action_v0_1", {})
    if not isinstance(existing, dict):
        existing = {}
    existing.update(payload)
    index["external_customer_validation_next_action_v0_1"] = existing
    AGENT_INDEX.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_NEXT_ACTION: PASS "
        "status=hold_external_customer_validation_input_required "
        "remaining_blocker=customer_validated production_ready=false"
    )


if __name__ == "__main__":
    main()
