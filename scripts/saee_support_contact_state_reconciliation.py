#!/usr/bin/env python3
"""Reconcile current support-contact readiness surfaces without closing blockers.

This local surface exists because older support-contact entrypoints can still
say "human input required" while later evidence surfaces already reached
closure-review state. The reconciler chooses the next safe human action from
existing local artifacts only. It does not publish support contact details,
contact customers or vendors, execute evidence collection, close blockers, or
claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SUPPORT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUT_DIR = SUPPORT_DIR / "support_contact_state_reconciliation"
OUT_JSON = OUT_DIR / "support_contact_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "support_contact_state_reconciliation.md"
BOUNDARY = OUT_DIR / "support_contact_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION_GATE.md"
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
    "readiness_board": SUPPORT_DIR / "support_contact_readiness_board.local.json",
    "approval_input_validation": SUPPORT_DIR / "support_contact_approval_input_validation.local.json",
    "human_filled_refresh": SUPPORT_DIR / "support_contact_human_filled_evidence_refresh.local.json",
    "closure_gap_review": SUPPORT_DIR / "support_contact_closure_gap_review.local.json",
    "support_group_refresh": SUPPORT_DIR / "support_group_human_filled_evidence_refresh.local.json",
    "final_closure_decision_validator": SUPPORT_DIR
    / "support_group_final_closure_decision_validation.local.json",
    "matrix_update_request_packet": ROOT
    / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_request_packet.local.json",
    "matrix_update_execution_request_packet": ROOT
    / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_request_packet.local.json",
    "matrix_update_approval_copy_card": ROOT
    / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_copy_card.local.json",
    "matrix_update_approval_validation": ROOT
    / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_approval_validation.local.json",
    "matrix_update_dry_run": ROOT
    / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_dry_run.local.json",
    "matrix_update_applier": ROOT
    / "phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_applier.local.json",
}

FALSE_FLAGS = {
    "support_contact_configured": False,
    "support_contact_published": False,
    "support_contact_test_performed": False,
    "support_contact_raw_value_exposed": False,
    "support_contact_raw_value_recorded": False,
    "customer_contacted": False,
    "support_vendor_contacted": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_reconciliation": 0,
    "production_ready": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
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


def build_payload() -> dict[str, Any]:
    source_data = {name: read_json(path) for name, path in SOURCES.items()}
    readiness = source_data["readiness_board"]
    approval = source_data["approval_input_validation"]
    refresh = source_data["human_filled_refresh"]
    closure = source_data["closure_gap_review"]
    support_group = source_data["support_group_refresh"]
    final_validator = source_data["final_closure_decision_validator"]
    matrix_request = source_data["matrix_update_request_packet"]
    execution_request = source_data["matrix_update_execution_request_packet"]
    approval_copy_card = source_data["matrix_update_approval_copy_card"]
    approval_validation = source_data["matrix_update_approval_validation"]
    dry_run = source_data["matrix_update_dry_run"]
    applier = source_data["matrix_update_applier"]

    closure_review_ready = (
        closure.get("support_contact_available_for_review") is True
        and closure.get("production_support_available") is True
        and closure.get("missing_evidence_item_count") == 0
        and closure.get("blockers_closed_by_gap_review") == 0
    )
    input_path_ready = approval.get("input_complete") is True and approval.get("builder_ready") is True
    refresh_ready = refresh.get("input_complete") is True
    support_group_ready = support_group.get("production_support_available") is True
    final_decision_ready = (
        final_validator.get("separate_matrix_update_request_ready") is True
        and final_validator.get("final_human_decision_recorded") is True
        and final_validator.get("authorize_separate_matrix_update_request") is True
        and final_validator.get("authorize_blocker_closure_now") is False
    )
    matrix_request_ready = matrix_request.get("status") == "ready_for_human_matrix_update_execution_request_no_closure"
    execution_request_ready = (
        execution_request.get("status") == "ready_for_explicit_human_execution_approval_no_closure"
    )
    approval_copy_ready = approval_copy_card.get("status") == "ready_for_exact_phrase_human_approval_no_execution"
    approval_validated = approval_validation.get("ready_for_matrix_update_execution") is True
    dry_run_ready = dry_run.get("ready_for_matrix_update_execution") is True
    applier_executed = applier.get("matrix_update_executed") is True

    if applier_executed:
        status = "matrix_update_markers_applied_no_blocker_closure"
        next_action = (
            "Review the matrix update applier output. Blocker closure and production "
            "readiness still require separate gates."
        )
        resolved_path = "matrix_update_applier"
    elif approval_validated or dry_run_ready:
        status = "ready_for_matrix_update_applier_no_auto_closure"
        next_action = (
            "Run the matrix update applier only if the separate human execution approval "
            "is still intended. The applier must apply review-ready markers only."
        )
        resolved_path = "matrix_update_approval_validation"
    elif final_decision_ready and execution_request_ready and approval_copy_ready:
        status = "ready_for_exact_matrix_update_execution_approval_phrase_no_auto_closure"
        next_action = (
            "If the human wants to apply review-ready markers only, copy the exact phrase "
            "from commercial_matrix_update_execution_approval_copy_card.md. Do not close "
            "blockers or claim production readiness."
        )
        resolved_path = "matrix_update_approval_copy_card"
    elif final_decision_ready and matrix_request_ready:
        status = "ready_for_explicit_matrix_update_execution_request_no_auto_closure"
        next_action = (
            "Review commercial_matrix_update_request_packet.md and create a separate "
            "execution approval if review-ready markers should be applied."
        )
        resolved_path = "matrix_update_request_packet"
    elif closure_review_ready:
        status = "ready_for_human_support_contact_closure_review_no_auto_closure"
        next_action = (
            "Review support_contact_closure_gap_review.md and then use a separate human "
            "support-group final closure decision request if closure is desired."
        )
        resolved_path = "closure_gap_review"
    elif support_group_ready:
        status = "ready_for_support_contact_closure_gap_review"
        next_action = "Run or review the support-contact closure gap review before any blocker closure."
        resolved_path = "support_group_refresh"
    elif input_path_ready or refresh_ready:
        status = "ready_for_support_contact_evidence_review_only"
        next_action = "Use the human-filled support-contact evidence for review only; closure still needs a separate gate."
        resolved_path = "approval_input_validation"
    else:
        status = "hold_support_contact_human_input_or_candidate_required"
        next_action = (
            "Complete the support-contact human input/candidate path before evidence builder "
            "or closure review."
        )
        resolved_path = "readiness_board"

    payload: dict[str, Any] = {
        "support_contact_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_support_contact_state_reconciliation_no_closure",
        "target_blocker_id": "support_contact",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "previous_readiness_board_status": readiness.get("status"),
        "approval_input_complete": approval.get("input_complete") is True,
        "approval_builder_ready": approval.get("builder_ready") is True,
        "human_filled_refresh_status": refresh.get("status"),
        "support_group_refresh_status": support_group.get("status"),
        "closure_gap_review_status": closure.get("status"),
        "closure_review_ready": closure_review_ready,
        "support_group_evidence_complete": support_group_ready,
        "final_closure_decision_validator_status": final_validator.get("validation_status")
        or final_validator.get("status"),
        "final_closure_decision_ready": final_decision_ready,
        "matrix_update_request_ready": matrix_request_ready,
        "matrix_update_execution_request_ready": execution_request_ready,
        "matrix_update_approval_copy_card_ready": approval_copy_ready,
        "matrix_update_approval_validated": approval_validated,
        "matrix_update_dry_run_ready": dry_run_ready,
        "matrix_update_executed": applier_executed,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Older support-contact surfaces can remain at first-input state while newer "
            "support-group evidence is ready for closure review. This file selects one "
            "safe next human action without closing the blocker."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    status = payload["status"]
    next_action = payload["next_human_action"]
    OUT_MD.write_text(
        f"""# SAEE Support Contact State Reconciliation v0.1

Status: `{status}`

This local board reconciles the current `support_contact` blocker surfaces. It
does not configure or publish a support contact, contact customers or vendors,
execute evidence collection, close blockers, launch the product, or claim
production readiness.

## Summary

- target_blocker_id: `support_contact`
- resolved_current_path: `{payload['resolved_current_path']}`
- previous_readiness_board_status: `{payload.get('previous_readiness_board_status')}`
- closure_review_ready: `{str(payload['closure_review_ready']).lower()}`
- support_group_evidence_complete: `{str(payload['support_group_evidence_complete']).lower()}`
- final_closure_decision_ready: `{str(payload['final_closure_decision_ready']).lower()}`
- matrix_update_request_ready: `{str(payload['matrix_update_request_ready']).lower()}`
- matrix_update_execution_request_ready: `{str(payload['matrix_update_execution_request_ready']).lower()}`
- matrix_update_approval_copy_card_ready: `{str(payload['matrix_update_approval_copy_card_ready']).lower()}`
- matrix_update_executed: `{str(payload['matrix_update_executed']).lower()}`
- blockers_closed_by_reconciliation: `0`
- production_ready: `false`
- customer_validated: `false`

## Next Human Action

{next_action}

## Source Surfaces

| Source | Path |
| --- | --- |
"""
        + "\n".join(f"| {name} | `{path}` |" for name, path in payload["source_paths"].items())
        + """

## Boundary

- support_contact_configured=false
- support_contact_published=false
- support_contact_test_performed=false
- support_contact_raw_value_exposed=false
- support_contact_raw_value_recorded=false
- customer_contacted=false
- support_vendor_contacted=false
- evidence_collection_authorized=false
- execution_authorized=false
- blocker_closure_authorized=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
- runtime_modified=false
- backend_modified=false
- kernel_modified=false
- api_schema_modified=false
""",
        encoding="utf-8",
    )

    BOUNDARY.write_text(
        """# SAEE Support Contact State Reconciliation Boundary Audit

- Only existing local support-contact evidence surfaces were read.
- No support contact configured by Codex.
- No support contact published by Codex.
- No support test sent by Codex.
- No customer contacted.
- No support vendor contacted.
- No evidence collection authorized.
- No blocker closure authorized.
- No blockers closed by reconciliation.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer validation claimed.
- No production-ready claim added.
""",
        encoding="utf-8",
    )

    TOP_DOC.write_text(
        f"""# SAEE Support Contact State Reconciliation v0.1

support_contact_state_reconciliation_v0_1: true
status: {status}
target_blocker_id: support_contact
resolved_current_path: {payload['resolved_current_path']}
matrix_update_approval_copy_card_ready: {str(payload['matrix_update_approval_copy_card_ready']).lower()}
matrix_update_executed: {str(payload['matrix_update_executed']).lower()}
blockers_closed_by_reconciliation: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

This surface is a local state reconciler. It points the human reviewer to the
current support-contact next action and does not execute closure.
""",
        encoding="utf-8",
    )

    GATE.write_text(
        f"""# SAEE Support Contact State Reconciliation Gate

answer: hold_human_review_required_no_auto_closure

reason: Existing support-contact surfaces disagree about the current stage. The
reconciler selects `{status}` as the current safe state from local evidence
without closing any blocker.

boundary:
- evidence_collection_authorized: false
- execution_authorized: false
- blocker_closure_authorized: false
- blockers_closed_by_reconciliation: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

next_action: {payload['next_human_action']}
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_support_contact_state_reconciliation.py",
        "/scripts/saee_support_contact_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    index["support_contact_state_reconciliation_v0_1"] = {
        "support_contact_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_support_contact_state_reconciliation_no_closure",
        "status": payload["status"],
        "target_blocker_id": "support_contact",
        "resolved_current_path": payload["resolved_current_path"],
        "closure_review_ready": payload["closure_review_ready"],
        "support_group_evidence_complete": payload["support_group_evidence_complete"],
        "final_closure_decision_ready": payload["final_closure_decision_ready"],
        "matrix_update_request_ready": payload["matrix_update_request_ready"],
        "matrix_update_execution_request_ready": payload["matrix_update_execution_request_ready"],
        "matrix_update_approval_copy_card_ready": payload["matrix_update_approval_copy_card_ready"],
        "matrix_update_approval_validated": payload["matrix_update_approval_validated"],
        "matrix_update_dry_run_ready": payload["matrix_update_dry_run_ready"],
        "matrix_update_executed": payload["matrix_update_executed"],
        "human_review_required": True,
        "blockers_closed_by_reconciliation": 0,
        "support_contact_configured": False,
        "support_contact_published": False,
        "support_contact_test_performed": False,
        "support_contact_raw_value_exposed": False,
        "support_contact_raw_value_recorded": False,
        "customer_contacted": False,
        "support_vendor_contacted": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "entrypoints": {
            "summary": rel(OUT_JSON),
            "report": rel(OUT_MD),
            "boundary_audit": rel(BOUNDARY),
            "gate": rel(GATE),
            "runner": "scripts/saee_support_contact_state_reconciliation.py",
            "smoke": "scripts/saee_support_contact_state_reconciliation_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    body = f"""## Support Contact State Reconciliation

Support Contact State Reconciliation v0.1 records
`status={payload['status']}` and resolves the current support-contact path to
`{payload['resolved_current_path']}`. It is a local review surface only:
`blockers_closed_by_reconciliation=0`, `evidence_collection_authorized=false`,
`execution_authorized=false`, `production_ready=false`, and
`customer_validated=false`. The current matrix-update approval copy-card state is
`matrix_update_approval_copy_card_ready={str(payload['matrix_update_approval_copy_card_ready']).lower()}`.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION", body)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} "
        f"resolved_current_path={payload['resolved_current_path']} "
        "blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
