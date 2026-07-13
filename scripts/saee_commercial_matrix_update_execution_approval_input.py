#!/usr/bin/env python3
"""Create the human approval input surface for matrix-update execution."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUT_DIR = COMMERCIAL_DIR / "matrix_update_requests"
SOURCE_REQUEST = OUT_DIR / "commercial_matrix_update_execution_request_packet.local.json"
TEMPLATE = OUT_DIR / "commercial_matrix_update_execution_approval_input.template.json"
PROMPT = OUT_DIR / "commercial_matrix_update_execution_approval_input.md"
VALIDATION = OUT_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
VALIDATION_MD = OUT_DIR / "commercial_matrix_update_execution_approval_validation.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TARGET_BLOCKERS = [
    "support_contact",
    "customer_support",
    "sla",
    "on_call_rotation",
    "pricing_page",
]

FALSE_FLAGS = {
    "human_execution_approved": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_approval_input": 0,
    "open_blocker_count_reduced": False,
    "pricing_page_published": False,
    "checkout_enabled": False,
    "customer_payment_collected": False,
    "revenue_validated": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def replace_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def build_template(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "commercial_matrix_update_execution_approval_input_v0_1": True,
        "input_type": "human_matrix_update_execution_approval",
        "source_execution_request_packet": rel(SOURCE_REQUEST),
        "target_blockers": source.get("target_blockers", TARGET_BLOCKERS),
        "recommended_human_decision": "approve_matrix_update_execution_review_ready_markers_only",
        "human_decision": "",
        "human_reviewer": "",
        "decision_date": "",
        "approval_reference": "",
        "approval_scope": "review_ready_markers_only_no_closure",
        "approve_matrix_update_execution_review_ready_markers_only": False,
        "confirm_no_blocker_closure": False,
        "confirm_no_pricing_publication": False,
        "confirm_no_checkout_enablement": False,
        "confirm_no_production_ready_claim": False,
        "confirm_no_customer_validation_claim": False,
        "confirm_no_product_launch": False,
        "notes": "",
    }


def build_validation() -> dict[str, Any]:
    return {
        "commercial_matrix_update_execution_approval_validation_v0_1": True,
        "status": "hold_human_execution_approval_input_required",
        "source_template": rel(TEMPLATE),
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "approval_input_complete": False,
        "missing_fields": [
            "human_decision",
            "human_reviewer",
            "decision_date",
            "approval_reference",
            "approve_matrix_update_execution_review_ready_markers_only",
            "confirm_no_blocker_closure",
            "confirm_no_pricing_publication",
            "confirm_no_checkout_enablement",
            "confirm_no_production_ready_claim",
            "confirm_no_customer_validation_claim",
            "confirm_no_product_launch",
        ],
        "next_human_action": "Fill a human_filled copy of the approval template, then run the approval validator.",
        **FALSE_FLAGS,
    }


def write_outputs() -> dict[str, Any]:
    source = read_json(SOURCE_REQUEST)
    template = build_template(source)
    validation = build_validation()
    write_json(TEMPLATE, template)
    write_json(VALIDATION, validation)
    PROMPT.write_text(
        f"""# SAEE Commercial Matrix Update Execution Approval Input

Status: `hold_human_execution_approval_input_required`

This is the human approval input for the next step. It does not execute the
matrix update. It only tells a future validator what explicit human approval
must contain before review-ready markers may be applied.

## Recommended Approval

Set these fields in a separate human-filled copy only if you approve the narrow
execution:

```json
{{
  "human_decision": "approve_matrix_update_execution_review_ready_markers_only",
  "human_reviewer": "张斌",
  "decision_date": "2026-07-09",
  "approval_reference": "human-confirmation-2026-07-09",
  "approve_matrix_update_execution_review_ready_markers_only": true,
  "confirm_no_blocker_closure": true,
  "confirm_no_pricing_publication": true,
  "confirm_no_checkout_enablement": true,
  "confirm_no_production_ready_claim": true,
  "confirm_no_customer_validation_claim": true,
  "confirm_no_product_launch": true
}}
```

## Target Blockers

{chr(10).join(f"- `{item}`" for item in source.get("target_blockers", TARGET_BLOCKERS))}

## Boundary

- human_execution_approved=false
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_approval_input=0
- production_ready=false
- customer_validated=false
- product_launched=false
""",
        encoding="utf-8",
    )
    VALIDATION_MD.write_text(
        """# SAEE Commercial Matrix Update Execution Approval Validation

Status: `hold_human_execution_approval_input_required`

No human-filled approval input has been validated yet.

- human_execution_approved=false
- ready_for_matrix_update_execution=false
- matrix_update_executed=false
- blockers_closed_by_approval_input=0
- production_ready=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        """# SAEE Commercial Matrix Update Execution Approval Input v0.1

commercial_matrix_update_execution_approval_input_v0_1: true
status: hold_human_execution_approval_input_required

Purpose: collect explicit human approval before any future matrix-update
execution applies review-ready markers. This surface does not execute a matrix
update and does not close blockers.

Entrypoints:

- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.template.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.md`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.local.json`
- `phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.md`
""",
        encoding="utf-8",
    )
    GATE.write_text(
        """# SAEE Commercial Matrix Update Execution Approval Input Gate

answer: hold_human_execution_approval_input_required

reason: Matrix-update execution can only proceed after a separate human-filled
approval input validates the narrow review-ready-marker-only scope.

boundary:
- human_execution_approved: false
- matrix_update_executed: false
- blocker_closure_authorized: false
- blockers_closed_by_approval_input: 0
- production_ready: false
- customer_validated: false
- product_launched: false

next_action: human fills and validates approval input, or keeps the matrix update on hold.
""",
        encoding="utf-8",
    )

    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.template.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_input.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_approval_input.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_validator.py",
        "/scripts/saee_commercial_matrix_update_execution_approval_input_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_approval_input_v0_1"] = {
        "name": "SAEE Commercial Matrix Update Execution Approval Input v0.1",
        "status": "hold_human_execution_approval_input_required",
        "target_blockers": source.get("target_blockers", TARGET_BLOCKERS),
        "recommended_human_decision": "approve_matrix_update_execution_review_ready_markers_only",
        "human_execution_approved": False,
        "ready_for_matrix_update_execution": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_approval_input": 0,
        "pricing_page_published": False,
        "checkout_enabled": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "entrypoints": {
            "template": rel(TEMPLATE),
            "prompt": rel(PROMPT),
            "validation": rel(VALIDATION),
            "validation_report": rel(VALIDATION_MD),
            "gate": rel(GATE),
            "top_doc": rel(TOP_DOC),
            "runner": "scripts/saee_commercial_matrix_update_execution_approval_input.py",
            "validator": "scripts/saee_commercial_matrix_update_execution_approval_validator.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_approval_input_smoke.py",
        },
        "make_target": "make check-commercial-matrix-update-execution-approval-input",
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    block = """## Commercial Matrix Update Execution Approval Input v0.1

- `commercial_matrix_update_execution_approval_input_v0_1`
- Status: `hold_human_execution_approval_input_required`
- recommended_human_decision=approve_matrix_update_execution_review_ready_markers_only
- human_execution_approved=false
- ready_for_matrix_update_execution=false
- matrix_update_executed=false
- blocker_closure_authorized=false
- blockers_closed_by_approval_input=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT_V0_1", block)

    return validation


def main() -> None:
    validation = write_outputs()
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_APPROVAL_INPUT: PASS "
        f"status={validation['status']} human_execution_approved=false "
        "matrix_update_executed=false blockers_closed_by_approval_input=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
