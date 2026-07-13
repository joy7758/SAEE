#!/usr/bin/env python3
"""Prepare the first manual external customer-validation run.

This run package is a human-execution aid for the remaining customer_validated
blocker. It does not contact customers, run interviews, collect data through
Codex, import evidence, execute validators, close blockers, launch product, or
claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
RUN_DIR = EVIDENCE_DIR / "external_customer_validation_run_001"
RUN_STATUS = RUN_DIR / "external_customer_validation_run_001_status.local.json"
RUN_README = RUN_DIR / "README.md"
HUMAN_STEPS = RUN_DIR / "HUMAN_EXECUTION_STEPS.md"
RESULT_CHECKLIST = RUN_DIR / "RESULT_ENTRY_CHECKLIST.md"
BOUNDARY_AUDIT = RUN_DIR / "BOUNDARY_AUDIT.md"
GATE = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001_GATE.md"

RECONCILIATION = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation/"
    "commercial_readiness_state_reconciliation.local.json"
)
SESSION_KIT = EVIDENCE_DIR / "external_customer_validation_session_kit.local.json"
SESSION_KIT_MD = EVIDENCE_DIR / "external_customer_validation_session_kit.md"
INTERVIEW_SCRIPT = EVIDENCE_DIR / "external_customer_validation_interview_script.md"
FEEDBACK_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_feedback_form.template.md"
FIELD_MAPPING = EVIDENCE_DIR / "external_customer_validation_field_mapping.csv"
ENTRY_TEMPLATE = EVIDENCE_DIR / "external_customer_validation_session_entry.template.json"
WORKBENCH = EVIDENCE_DIR / "external_customer_validation_session_entry_workbench.html"
IMPORTER = ROOT / "scripts/saee_external_customer_validation_session_entry_importer.py"
VALIDATOR = ROOT / "scripts/saee_customer_validation_approval_input_validator.py"
AGENT_INDEX = ROOT / "agent-index.json"


FALSE_FLAGS = {
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "landing_page_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted_by_codex": False,
    "customer_data_collected_by_codex": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_builder_executed": False,
    "validator_executed": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_run": 0,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001: FAIL: " + message)


def build_status() -> dict[str, Any]:
    for path in [
        RECONCILIATION,
        SESSION_KIT,
        SESSION_KIT_MD,
        INTERVIEW_SCRIPT,
        FEEDBACK_TEMPLATE,
        FIELD_MAPPING,
        ENTRY_TEMPLATE,
        WORKBENCH,
        IMPORTER,
        VALIDATOR,
    ]:
        require(path.exists(), f"missing prerequisite {rel(path)}")

    reconciliation = read_json(RECONCILIATION)
    kit = read_json(SESSION_KIT)
    require(
        reconciliation.get("current_goal_blocker") == "customer_validated",
        "reconciliation must point to customer_validated",
    )
    require(reconciliation.get("customer_validated") is False, "customer_validated must remain false")
    require(kit.get("status") == "ready_for_human_external_customer_validation_session", "session kit must be ready")
    require(kit.get("customer_validated") is False, "session kit must not claim customer validation")

    return {
        "external_customer_validation_run_001_v0_1": True,
        "run_id": "external_customer_validation_run_001",
        "run_type": "manual_external_customer_or_target_user_validation_run",
        "status": "prepared_pending_human_external_session",
        "current_goal_blocker": "customer_validated",
        "source_reconciliation": rel(RECONCILIATION),
        "source_session_kit": rel(SESSION_KIT),
        "interview_script": rel(INTERVIEW_SCRIPT),
        "feedback_form_template": rel(FEEDBACK_TEMPLATE),
        "field_mapping": rel(FIELD_MAPPING),
        "session_entry_template": rel(ENTRY_TEMPLATE),
        "session_entry_workbench": rel(WORKBENCH),
        "importer": rel(IMPORTER),
        "validator": rel(VALIDATOR),
        "planned_external_sessions": 1,
        "required_real_external_sessions_min": 1,
        "human_session_required": True,
        "human_session_performed": False,
        "human_result_entry_required": True,
        "human_result_entered": False,
        "records_entered": 0,
        "ready_for_import_after_human_entry": False,
        "ready_for_validator_after_import": False,
        "codex_may_contact_customer": False,
        "codex_may_run_external_session": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_collect_customer_data": False,
        "human_must_select_external_customer_or_target_user": True,
        "generated_by": "scripts/saee_external_customer_validation_run_001.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "next_human_action": (
            "A human must run one real external customer or target-user session, "
            "then save the session entry as external_customer_validation_session_entry.human_filled.local.json."
        ),
        **FALSE_FLAGS,
    }


def render_readme(status: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Run 001

Status: `{status['status']}`.

This run package prepares the first manual external customer or target-user
validation session for SAEE's remaining commercial blocker:
`customer_validated`.

## What This Run Does

- points the human reviewer to the existing interview script;
- points the human reviewer to the feedback form template;
- points the human reviewer to the local entry workbench;
- records that one real external session is still required.

## What This Run Does Not Do

- Codex does not contact customers;
- Codex does not run the interview;
- Codex does not collect customer data;
- Codex does not infer customer feedback;
- Codex does not import results;
- Codex does not run the validator;
- Codex does not close blockers;
- Codex does not claim production readiness.

## Current Boundary

- customer_validated: false
- production_ready: false
- product_launched: false
- private_core_exposed: false
- blockers_closed_by_run: 0

## Next Human Action

{status['next_human_action']}
"""


def render_human_steps(status: dict[str, Any]) -> str:
    return f"""# Human Execution Steps

1. Select one real external customer or target user.
2. Use `{status['interview_script']}` as the interview guide.
3. Use `{status['feedback_form_template']}` to record the answers.
4. Do not ask for secrets, source code, production data, or customer data.
5. Open `{status['session_entry_workbench']}` locally.
6. Enter the session summary and review checklist.
7. Save the JSON as:
   `phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_session_entry.human_filled.local.json`.
8. After the file exists, run:

```bash
python3 scripts/saee_external_customer_validation_session_entry_importer.py --apply
python3 scripts/saee_customer_validation_approval_input_validator.py
python3 scripts/mainline_guard.py
make check
```

The session must be real. Internal founder review does not satisfy
`customer_validated`.
"""


def render_checklist() -> str:
    return """# Result Entry Checklist

Before importing results, confirm:

- [ ] The participant is an external customer or target user, not only the founder.
- [ ] The participant understood SAEE's purpose in plain language.
- [ ] The session compared at least two candidate agents, workflows, or policies.
- [ ] The participant reviewed whether SAEE could affect deployment decisions.
- [ ] No source code, secrets, production data, or customer data were collected.
- [ ] No production-ready claim was made.
- [ ] No customer-validation claim was made before validator pass.
- [ ] The JSON was saved as `external_customer_validation_session_entry.human_filled.local.json`.

If any item is unchecked, keep `customer_validated=false`.
"""


def render_boundary_audit() -> str:
    return """# SAEE External Customer Validation Run 001 Boundary Audit

- Manual run package only.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No landing page modified.
- No private core exposed.
- No customer contacted by Codex.
- No customer data collected by Codex.
- No external model API called.
- No browser automation used.
- No session result imported.
- No validator executed by this run.
- No customer-validation claim made.
- No product launched.
- No production-ready claim made.
- No blocker closed by this run.
"""


def render_gate(status: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Run 001 Gate

answer: prepared_pending_human_external_session

reason:
The remaining commercial blocker is `customer_validated`. This package prepares
one manual external customer or target-user validation run, but no session has
been performed and no result has been imported yet.

boundary:
customer_validated: false
production_ready: false
product_launched: false
customer_contacted_by_codex: false
private_core_exposed: false
blocker_closure_authorized: false
blockers_closed_by_run: 0

next_action:
{status['next_human_action']}
"""


def update_agent_index(status: dict[str, Any]) -> None:
    index = read_json(AGENT_INDEX)
    entry = {
        "name": "SAEE External Customer Validation Run 001 v0.1",
        "run_id": status["run_id"],
        "run_type": status["run_type"],
        "status": status["status"],
        "purpose": (
            "Prepare one manual external customer or target-user validation run "
            "for the remaining customer_validated blocker without Codex contacting "
            "customers or claiming validation."
        ),
        "current_goal_blocker": "customer_validated",
        "planned_external_sessions": 1,
        "required_real_external_sessions_min": 1,
        "human_session_required": True,
        "human_session_performed": False,
        "human_result_entry_required": True,
        "human_result_entered": False,
        "records_entered": 0,
        "ready_for_import_after_human_entry": False,
        "ready_for_validator_after_import": False,
        "codex_may_contact_customer": False,
        "codex_may_run_external_session": False,
        "codex_may_infer_customer_feedback": False,
        "codex_may_collect_customer_data": False,
        "human_must_select_external_customer_or_target_user": True,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_builder_executed": False,
        "validator_executed": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_run": 0,
        "entrypoints": {
            "status": rel(RUN_STATUS),
            "readme": rel(RUN_README),
            "human_steps": rel(HUMAN_STEPS),
            "result_checklist": rel(RESULT_CHECKLIST),
            "boundary_audit": rel(BOUNDARY_AUDIT),
            "gate": rel(GATE),
            "runner": "scripts/saee_external_customer_validation_run_001.py",
            "smoke": "scripts/saee_external_customer_validation_run_001_smoke.py",
        },
    }
    index["external_customer_validation_run_001_v0_1"] = entry
    write_json(AGENT_INDEX, index)


def main() -> None:
    status = build_status()
    write_json(RUN_STATUS, status)
    RUN_README.write_text(render_readme(status), encoding="utf-8")
    HUMAN_STEPS.write_text(render_human_steps(status), encoding="utf-8")
    RESULT_CHECKLIST.write_text(render_checklist(), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary_audit(), encoding="utf-8")
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(render_gate(status), encoding="utf-8")
    update_agent_index(status)
    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_RUN_001: PASS "
        "status=prepared_pending_human_external_session "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
