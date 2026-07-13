#!/usr/bin/env python3
"""Process a human-filled external customer validation session locally.

This script links the existing importer, validator, evidence builder, readiness
checker, and commercial go/no-go checker. It is intentionally conservative:
without a human-filled entry it only records a hold state, and even with a
valid entry it does not claim customer validation, launch, or production
readiness.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_customer_validation_evidence import (
    evaluate_production_customer_validation_evidence,
)
from scripts import saee_customer_validation_approval_input_validator as approval_validator
from scripts import saee_external_customer_validation_session_entry_importer as importer
from scripts.saee_customer_validation_evidence_builder import build_from_file


EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/customer_validation_evidence"
OUT = EVIDENCE_DIR / "external_customer_validation_post_session_processor"
SUMMARY_PATH = OUT / "external_customer_validation_post_session_processor.local.json"
REPORT_PATH = OUT / "external_customer_validation_post_session_processor.md"
BOUNDARY_PATH = OUT / "BOUNDARY_AUDIT.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_POST_SESSION_PROCESSOR_GATE.md"
HUMAN_ENTRY = EVIDENCE_DIR / "external_customer_validation_session_entry.human_filled.local.json"
IMPORTED_INPUT = EVIDENCE_DIR / "customer_validation_evidence_input.human_filled.local.json"
BUILDER_OUTPUT = OUT / "customer_validation_evidence.from_external_session.local.json"
APPROVAL_VALIDATION_OUTPUT = OUT / "customer_validation_approval_input_validation.local.json"
READINESS_OUTPUT = OUT / "production_customer_validation_evidence_readiness.local.json"
GO_NO_GO_OUTPUT = OUT / "commercial_go_no_go.from_external_customer_validation.local.json"
MINIMUM_SESSION_FORM = (
    EVIDENCE_DIR
    / "external_customer_validation_minimum_session_packet"
    / "minimum_session_form.html"
)
MINIMUM_SESSION_QUESTIONS = (
    EVIDENCE_DIR
    / "external_customer_validation_minimum_session_packet"
    / "MINIMUM_SESSION_QUESTIONS.md"
)
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"


FALSE_FLAGS = {
    "customer_validated": False,
    "production_ready": False,
    "product_launched": False,
    "customer_contacted_by_codex": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
}


LLMS_LINES = [
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.md",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/external_customer_validation_post_session_processor.local.json",
    "/phase_b_product/commercial_readiness/customer_validation_evidence/external_customer_validation_post_session_processor/BOUNDARY_AUDIT.md",
    "/docs/strategy/SAEE_EXTERNAL_CUSTOMER_VALIDATION_POST_SESSION_PROCESSOR_GATE.md",
    "/scripts/saee_external_customer_validation_post_session_processor.py",
    "/scripts/saee_external_customer_validation_post_session_processor_smoke.py",
]


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def append_unique_llms() -> None:
    existing = LLMS.read_text(encoding="utf-8") if LLMS.exists() else ""
    lines = existing.splitlines()
    changed = False
    for line in LLMS_LINES:
        if line not in lines:
            lines.append(line)
            changed = True
    if changed:
        LLMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def update_agent_index(summary: dict[str, Any]) -> None:
    data = read_json(AGENT_INDEX)
    data["external_customer_validation_post_session_processor_v0_1"] = {
        "status": summary["status"],
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": summary["recommended_path_locked"],
        "recommended_path_id": summary["recommended_path_id"],
        "recommended_form": summary["recommended_form"],
        "recommended_questions": summary["recommended_questions"],
        "human_entry_path": rel(HUMAN_ENTRY),
        "human_entry_exists": summary["human_entry_exists"],
        "import_status": summary["import_status"],
        "approval_validation_status": summary["approval_validation_status"],
        "evidence_builder_ran": summary["evidence_builder_ran"],
        "readiness_status": summary["readiness_status"],
        "commercial_go_no_go_status": summary["commercial_go_no_go_status"],
        "blockers_closed_by_processor": 0,
        **FALSE_FLAGS,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def status_from_parts(
    human_entry_exists: bool,
    import_summary: dict[str, Any] | None,
    approval: dict[str, Any] | None,
    readiness: dict[str, Any] | None,
) -> str:
    if not human_entry_exists:
        return "hold_human_session_entry_missing"
    if import_summary and import_summary.get("boundary_violation_count", 0) > 0:
        return "stop_boundary_violation"
    if import_summary and import_summary.get("status") != "ready_for_customer_validation_validator":
        return "hold_human_session_entry_incomplete"
    if approval and approval.get("validation_status") == "stop":
        return "stop_boundary_violation"
    if approval and approval.get("validation_status") != "pass":
        return "hold_customer_validation_approval_input_incomplete"
    if readiness and readiness.get("status") == "pass":
        return "processed_customer_validation_evidence_ready_for_go_no_go_review"
    return "hold_customer_validation_evidence_not_ready"


def process() -> dict[str, Any]:
    OUT.mkdir(parents=True, exist_ok=True)
    human_entry_exists = HUMAN_ENTRY.exists()
    import_summary: dict[str, Any] | None = None
    approval: dict[str, Any] | None = None
    readiness: dict[str, Any] | None = None
    go_no_go: dict[str, Any] | None = None
    evidence_builder_ran = False

    if human_entry_exists:
        import_summary = importer.build_summary(HUMAN_ENTRY, apply=True)
        importer.write_outputs(import_summary)
        if import_summary.get("human_filled_output_written") is True:
            approval = approval_validator.build_validation(IMPORTED_INPUT)
            write_json(APPROVAL_VALIDATION_OUTPUT, approval)
            if approval.get("validation_status") == "pass":
                build_from_file(IMPORTED_INPUT, BUILDER_OUTPUT)
                evidence_builder_ran = True
                settings = load_settings(
                    {"SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": str(BUILDER_OUTPUT)}
                )
                readiness = evaluate_production_customer_validation_evidence(settings)
                go_no_go = evaluate_commercial_go_no_go(settings)
                write_json(READINESS_OUTPUT, readiness)
                write_json(GO_NO_GO_OUTPUT, go_no_go)
    else:
        import_summary = importer.build_summary(HUMAN_ENTRY, apply=False)
        importer.write_outputs(import_summary)

    status = status_from_parts(human_entry_exists, import_summary, approval, readiness)
    summary = {
        "external_customer_validation_post_session_processor_v0_1": True,
        "status": status,
        "processor_type": "local_external_customer_validation_post_session_processor",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "current_goal_blocker": "customer_validated",
        "recommended_path_locked": True,
        "recommended_path_id": "minimum_session_packet",
        "recommended_form": rel(MINIMUM_SESSION_FORM),
        "recommended_questions": rel(MINIMUM_SESSION_QUESTIONS),
        "human_entry_path": rel(HUMAN_ENTRY),
        "human_entry_exists": human_entry_exists,
        "imported_customer_validation_input": rel(IMPORTED_INPUT),
        "import_status": import_summary.get("status") if import_summary else "not_run",
        "import_output_written": bool(import_summary and import_summary.get("human_filled_output_written")),
        "approval_validation_status": approval.get("validation_status") if approval else "not_run",
        "approval_input_complete": bool(approval and approval.get("input_complete")),
        "evidence_builder_ran": evidence_builder_ran,
        "builder_output": rel(BUILDER_OUTPUT),
        "readiness_status": readiness.get("status") if readiness else "not_run",
        "production_customer_validation_ready": bool(
            readiness and readiness.get("production_customer_validation_ready") is True
        ),
        "commercial_go_no_go_status": go_no_go.get("status") if go_no_go else "not_run",
        "commercial_production_ready": bool(go_no_go and go_no_go.get("production_ready") is True),
        "commercial_customer_validated_claim": bool(go_no_go and go_no_go.get("customer_validated") is True),
        "blockers_closed_by_processor": 0,
        "post_fill_command": (
            "python3 scripts/saee_external_customer_validation_post_session_processor.py"
        ),
        "post_fill_validation_command": (
            "python3 scripts/saee_external_customer_validation_post_session_processor_smoke.py"
        ),
        "next_human_action": (
            "Open the minimum session form, run one real external customer or target-user session, "
            "and save the generated JSON to the required human entry path."
            if not human_entry_exists
            else "Review processor outputs and use the existing commercial go/no-go process."
        ),
        **FALSE_FLAGS,
    }
    write_json(SUMMARY_PATH, summary)
    return summary


def render_report(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Post-Session Processor

Status: {summary['status']}.

This local processor links the existing customer-validation session importer,
approval-input validator, evidence builder, production customer-validation
readiness checker, and commercial go/no-go checker.

It does not run customer sessions, contact customers, infer feedback, close
blockers, launch the product, claim customer validation, or claim production
readiness.

## Current Inputs

- recommended_path_locked: {str(summary['recommended_path_locked']).lower()}
- recommended_path_id: `{summary['recommended_path_id']}`
- recommended_form: `{summary['recommended_form']}`
- recommended_questions: `{summary['recommended_questions']}`
- human_entry_path: `{summary['human_entry_path']}`
- human_entry_exists: {str(summary['human_entry_exists']).lower()}
- import_status: {summary['import_status']}
- approval_validation_status: {summary['approval_validation_status']}
- evidence_builder_ran: {str(summary['evidence_builder_ran']).lower()}
- readiness_status: {summary['readiness_status']}
- commercial_go_no_go_status: {summary['commercial_go_no_go_status']}

## If Human Entry Is Missing

Open:

`{summary['recommended_form']}`

Ask the 12-question minimum session to one real external customer or target
user, then save the generated JSON exactly here:

`{summary['human_entry_path']}`

After that file exists, run:

```bash
{summary['post_fill_command']}
{summary['post_fill_validation_command']}
```

## Boundary

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blockers_closed_by_processor: 0
"""


def render_boundary(summary: dict[str, Any]) -> str:
    lines = ["# SAEE External Customer Validation Post-Session Boundary Audit", ""]
    lines.append(f"Final status: {summary['status']}.")
    lines.append("")
    for key, value in FALSE_FLAGS.items():
        lines.append(f"- {key}: {str(value).lower()}")
    lines.extend(
        [
            "- blockers_closed_by_processor: 0",
            "- no customer session run by Codex",
            "- no customer feedback inferred by Codex",
            "- no production-ready claim added",
        ]
    )
    return "\n".join(lines) + "\n"


def render_gate(summary: dict[str, Any]) -> str:
    return f"""# SAEE External Customer Validation Post-Session Processor Gate

answer: {summary['status']}

reason: The processor is a local-only chain for human-filled external customer
validation evidence. It waits for real human input and does not replace the
customer session.

boundary:

- customer_validated: false
- production_ready: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blockers_closed_by_processor: 0

next_action: {summary['next_human_action']}

recommended_form: {summary['recommended_form']}

required_human_output: {summary['human_entry_path']}
"""


def update_text_surfaces(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(render_report(summary), encoding="utf-8")
    BOUNDARY_PATH.write_text(render_boundary(summary), encoding="utf-8")
    GATE_PATH.write_text(render_gate(summary), encoding="utf-8")
    append_unique_llms()
    update_agent_index(summary)


def main() -> None:
    summary = process()
    update_text_surfaces(summary)
    print(
        "SAEE_EXTERNAL_CUSTOMER_VALIDATION_POST_SESSION_PROCESSOR: PASS "
        f"status={summary['status']} "
        f"human_entry_exists={str(summary['human_entry_exists']).lower()} "
        "customer_validated=false production_ready=false"
    )


if __name__ == "__main__":
    main()
