#!/usr/bin/env python3
"""Reconcile formal-security-review evidence state without performing review.

This local surface exists because the minimum human-input workspace can still
say "human input required" while human-filled validator and builder outputs
already show local review evidence ready for human review. It does not perform
a security review, contact reviewers or vendors, run penetration tests, inspect
private core, close blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "privacy_security_legal_evidence"
OUT_DIR = EVIDENCE_DIR / "formal_security_review_state_reconciliation"
OUT_JSON = OUT_DIR / "formal_security_review_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "formal_security_review_state_reconciliation.md"
BOUNDARY = OUT_DIR / "formal_security_review_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "FORMAL_SECURITY_REVIEW_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_STATE_RECONCILIATION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

SOURCES = {
    "minimum_human_input_workspace": EVIDENCE_DIR
    / "formal_security_review_minimum_human_input_workspace/formal_security_review_minimum_human_input_workspace.local.json",
    "approval_input_validation": EVIDENCE_DIR
    / "formal_security_review_approval_input_validation.human_filled.local.json",
    "evidence_builder_output": EVIDENCE_DIR
    / "formal_security_review_evidence_builder_output.human_filled.local.json",
    "production_evidence": EVIDENCE_DIR
    / "production_privacy_security_legal_evidence.from_formal_security_review.human_filled.local.json",
    "scope_draft": EVIDENCE_DIR / "formal_security_review_scope_draft.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
}

FALSE_FLAGS = {
    "formal_security_review_completed": False,
    "formal_security_review_completed_by_codex": False,
    "codex_performed_security_review": False,
    "codex_contacted_security_reviewer": False,
    "codex_contacted_vendor": False,
    "codex_ran_penetration_test": False,
    "codex_inspected_private_core": False,
    "security_review_claim_published": False,
    "production_security_claim_published": False,
    "production_security_enabled": False,
    "privacy_notice_published": False,
    "security_vendor_contacted": False,
    "customer_data_processed": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_reconciliation": 0,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
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
    if not path.exists():
        return {}
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


def closure_board_row(board: dict[str, Any]) -> dict[str, Any]:
    rows = board.get("rows") or board.get("blockers") or []
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_id") == "formal_security_review":
            return row
    return {}


def gap_matrix_row(gap: dict[str, Any]) -> dict[str, Any]:
    rows = gap.get("matrix", [])
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_id") == "formal_security_review":
            return row
    return {}


def build_payload() -> dict[str, Any]:
    source_data = {name: read_json(path) for name, path in SOURCES.items()}
    minimum = source_data["minimum_human_input_workspace"]
    approval = source_data["approval_input_validation"]
    builder = source_data["evidence_builder_output"]
    evidence = source_data["production_evidence"]
    closure_row = closure_board_row(source_data["closure_readiness_board"])
    gap_row = gap_matrix_row(source_data["gap_matrix"])

    input_path_ready = approval.get("validation_status") == "pass" and approval.get("builder_ready") is True
    builder_ready = (
        builder.get("status") == "pass"
        and builder.get("input_complete") is True
        and builder.get("formal_security_review_completed_for_review") is True
    )
    evidence_ready_for_review = (
        evidence.get("formal_security_review_report") is True
        and evidence.get("security_review_owner_recorded") is True
        and evidence.get("codex_performed_security_review") is False
        and evidence.get("security_review_claim_published") is False
    )
    closure_board_not_ready = closure_row.get("closure_status") == "not_ready" or closure_row.get("status") == "not_ready"
    gap_matrix_open = gap_row.get("status") == "open"

    if builder_ready and evidence_ready_for_review:
        status = "ready_for_human_security_review_evidence_review_no_closure"
        resolved_path = "evidence_builder_output"
        next_action = (
            "Human security owner may review the human-filled evidence and decide "
            "whether to create a separate matrix update request. Do not claim a "
            "completed security review, contact reviewers, run tests, or close blockers."
        )
    elif input_path_ready:
        status = "ready_for_formal_security_review_evidence_builder_review_only"
        resolved_path = "approval_input_validation"
        next_action = "Use the validator output for review only; evidence builder execution remains separate."
    else:
        status = "hold_formal_security_review_human_input_required"
        resolved_path = "minimum_human_input_workspace"
        next_action = "Complete human-filled formal-security-review input before any builder or review packet."

    payload: dict[str, Any] = {
        "formal_security_review_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_formal_security_review_state_reconciliation_no_review_no_closure",
        "target_blocker_id": "formal_security_review",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "previous_minimum_workspace_status": minimum.get("status"),
        "approval_validation_status": approval.get("validation_status"),
        "approval_input_complete": approval.get("input_complete") is True,
        "approval_builder_ready": input_path_ready,
        "builder_output_status": builder.get("status"),
        "builder_output_ready": builder_ready,
        "formal_security_review_evidence_ready_for_review": evidence_ready_for_review,
        "formal_security_review_report_recorded": evidence.get("formal_security_review_report") is True,
        "security_review_owner_recorded": evidence.get("security_review_owner_recorded") is True,
        "closure_board_not_ready": closure_board_not_ready,
        "gap_matrix_open": gap_matrix_open,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Older formal-security-review surfaces can remain at first-input state while "
            "human-filled evidence is ready for human review. This file selects one safe "
            "next human action without performing security review or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Formal Security Review State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles the current `formal_security_review` blocker
surfaces. It does not perform a security review, contact reviewers or vendors,
run penetration tests, inspect private core, close blockers, or claim
production readiness.

## Current Finding

- target_blocker_id: `formal_security_review`
- previous_minimum_workspace_status: `{payload['previous_minimum_workspace_status']}`
- approval_validation_status: `{payload['approval_validation_status']}`
- approval_input_complete: `{str(payload['approval_input_complete']).lower()}`
- builder_output_ready: `{str(payload['builder_output_ready']).lower()}`
- formal_security_review_evidence_ready_for_review: `{str(payload['formal_security_review_evidence_ready_for_review']).lower()}`
- formal_security_review_report_recorded: `{str(payload['formal_security_review_report_recorded']).lower()}`
- security_review_owner_recorded: `{str(payload['security_review_owner_recorded']).lower()}`
- gap_matrix_open: `{str(payload['gap_matrix_open']).lower()}`
- closure_board_not_ready: `{str(payload['closure_board_not_ready']).lower()}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

## Boundary

- codex_performed_security_review=false
- codex_contacted_security_reviewer=false
- codex_ran_penetration_test=false
- codex_inspected_private_core=false
- security_review_claim_published=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Formal Security Review State Reconciliation Boundary Audit

- No security review performed by Codex.
- No security reviewer contacted by Codex.
- No security vendor contacted.
- No penetration test run.
- No private core inspected.
- No security-review completion claim published.
- No production-security claim published.
- No evidence collection authorized.
- No execution authorized.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blocker closed.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launch.
- No production-ready claim.
- No customer-validation claim.
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Formal Security Review State Reconciliation v0.1

Status: `{payload['status']}`

This is an agent-readable current-state board for the
`formal_security_review` blocker. It reconciles existing local evidence only
and keeps security review execution, external contact, matrix update, and
blocker closure behind separate human gates.

## Canonical Files

- `{rel(OUT_JSON)}`
- `{rel(OUT_MD)}`
- `{rel(BOUNDARY)}`
- `{rel(GATE)}`
- `scripts/saee_formal_security_review_state_reconciliation.py`
- `scripts/saee_formal_security_review_state_reconciliation_smoke.py`

## Truth State

- codex_performed_security_review=false
- security_review_claim_published=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(
        f"""# SAEE Formal Security Review State Reconciliation Gate

answer: hold_human_review_required_no_security_review_no_auto_closure

reason: Human-filled formal-security-review evidence is ready for human review,
but Codex has not performed a security review and no blocker closure,
production-readiness, or external-contact action is authorized.

status: `{payload['status']}`

boundary:
- codex_performed_security_review: false
- codex_contacted_security_reviewer: false
- security_review_claim_published: false
- blockers_closed_by_reconciliation: 0
- production_ready: false
- customer_validated: false
- private_core_exposed: false

next_action: {payload['next_human_action']}
""",
        encoding="utf-8",
    )

    for line in [
        f"/{rel(TOP_DOC)}",
        f"/{rel(OUT_JSON)}",
        f"/{rel(OUT_MD)}",
        f"/{rel(BOUNDARY)}",
        f"/{rel(GATE)}",
        "/scripts/saee_formal_security_review_state_reconciliation.py",
        "/scripts/saee_formal_security_review_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["formal_security_review_state_reconciliation_v0_1"] = {
        "name": "SAEE Formal Security Review State Reconciliation v0.1",
        "status": payload["status"],
        "target_blocker_id": "formal_security_review",
        "resolved_current_path": payload["resolved_current_path"],
        "formal_security_review_evidence_ready_for_review": payload[
            "formal_security_review_evidence_ready_for_review"
        ],
        "formal_security_review_report_recorded": payload["formal_security_review_report_recorded"],
        "security_review_owner_recorded": payload["security_review_owner_recorded"],
        "separate_matrix_update_request_required": True,
        "human_review_required": True,
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "security_review_claim_published": False,
        "blockers_closed_by_reconciliation": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "make_target": "make check-formal-security-review-state-reconciliation",
    }
    write_json(AGENT_INDEX, index)

    block = f"""## Formal Security Review State Reconciliation v0.1

- `formal_security_review_state_reconciliation_v0_1`
- Status: `{payload['status']}`
- Target blocker: `formal_security_review`
- Resolved current path: `{payload['resolved_current_path']}`
- formal_security_review_evidence_ready_for_review={str(payload['formal_security_review_evidence_ready_for_review']).lower()}
- codex_performed_security_review=false
- security_review_claim_published=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
"""
    for surface in STATUS_SURFACES:
        replace_block(surface, "SAEE_FORMAL_SECURITY_REVIEW_STATE_RECONCILIATION_V0_1", block)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_FORMAL_SECURITY_REVIEW_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
