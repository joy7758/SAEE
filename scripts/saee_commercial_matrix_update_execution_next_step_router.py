#!/usr/bin/env python3
"""Route the current commercial matrix-update execution next step.

This router is intentionally non-executing. It reads the support-contact
reconciliation and matrix-update approval chain, then records the exact current
human approval point. It does not write human-filled approval input, execute a
matrix update, modify the gap matrix, close blockers, publish pricing, enable
checkout, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
MATRIX_DIR = COMMERCIAL_DIR / "matrix_update_requests"
SUPPORT_RECONCILIATION = (
    COMMERCIAL_DIR
    / "support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation.local.json"
)
COPY_CARD = MATRIX_DIR / "commercial_matrix_update_execution_approval_copy_card.local.json"
COPY_CARD_MD = MATRIX_DIR / "commercial_matrix_update_execution_approval_copy_card.md"
PHRASE_INTAKE = MATRIX_DIR / "commercial_matrix_update_execution_approval_phrase_intake.local.json"
APPROVAL_VALIDATION = MATRIX_DIR / "commercial_matrix_update_execution_approval_validation.local.json"
DRY_RUN = MATRIX_DIR / "commercial_matrix_update_execution_dry_run.local.json"
APPLIER = MATRIX_DIR / "commercial_matrix_update_execution_applier.local.json"

OUT_JSON = MATRIX_DIR / "commercial_matrix_update_execution_next_step_router.local.json"
OUT_MD = MATRIX_DIR / "commercial_matrix_update_execution_next_step_router.md"
BOUNDARY = MATRIX_DIR / "commercial_matrix_update_execution_next_step_router_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

EXACT_APPROVAL_PHRASE = (
    "批准矩阵更新执行：仅应用 review-ready markers，不关闭 blocker，不发布价格页，不启用 checkout，不声明生产可用。"
)

FALSE_FLAGS = {
    "human_filled_approval_written": False,
    "human_execution_approved_by_router": False,
    "matrix_update_executed": False,
    "canonical_gap_matrix_modified": False,
    "canonical_closure_board_modified": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_router": 0,
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
    support = read_json(SUPPORT_RECONCILIATION)
    copy_card = read_json(COPY_CARD)
    phrase = read_json(PHRASE_INTAKE)
    approval = read_json(APPROVAL_VALIDATION)
    dry_run = read_json(DRY_RUN)
    applier = read_json(APPLIER)

    support_ready_for_phrase = (
        support.get("status") == "ready_for_exact_matrix_update_execution_approval_phrase_no_auto_closure"
        and support.get("matrix_update_approval_copy_card_ready") is True
        and support.get("matrix_update_executed") is False
    )
    copy_card_ready = copy_card.get("status") == "ready_for_exact_phrase_human_approval_no_execution"
    phrase_written = phrase.get("human_filled_approval_written") is True
    approval_ready = approval.get("ready_for_matrix_update_execution") is True
    dry_run_ready = dry_run.get("ready_for_matrix_update_execution") is True
    applier_executed = applier.get("matrix_update_executed") is True

    if applier_executed:
        status = "matrix_update_markers_applied_no_blocker_closure"
        current_required_human_action = "Review matrix update output and keep formal blocker closure separate."
    elif approval_ready or dry_run_ready:
        status = "ready_for_matrix_update_applier_no_auto_closure"
        current_required_human_action = (
            "Run the matrix update applier only if the narrow approval still applies."
        )
    elif phrase_written:
        status = "ready_for_approval_validator_no_auto_execution"
        current_required_human_action = "Run the approval validator before any dry run or applier."
    elif support_ready_for_phrase and copy_card_ready:
        status = "waiting_for_exact_human_approval_phrase"
        current_required_human_action = (
            "Human must send the exact approval phrase before Codex may write the "
            "structured approval input."
        )
    else:
        status = "hold_matrix_update_prerequisite_not_ready"
        current_required_human_action = "Review support-contact reconciliation and matrix update copy card first."

    return {
        "commercial_matrix_update_execution_next_step_router_v0_1": True,
        "router_type": "matrix_update_execution_next_step_no_execution",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "support_reconciliation_status": support.get("status"),
        "copy_card_status": copy_card.get("status"),
        "phrase_intake_status": phrase.get("status"),
        "approval_validation_status": approval.get("status"),
        "dry_run_status": dry_run.get("status"),
        "applier_status": applier.get("status"),
        "support_ready_for_phrase": support_ready_for_phrase,
        "copy_card_ready": copy_card_ready,
        "phrase_intake_written": phrase_written,
        "approval_ready_for_matrix_update_execution": approval_ready,
        "dry_run_ready_for_matrix_update_execution": dry_run_ready,
        "exact_approval_phrase_required": True,
        "exact_approval_phrase": EXACT_APPROVAL_PHRASE,
        "current_required_human_action": current_required_human_action,
        "approval_commands_after_exact_phrase": [
            (
                "python3 scripts/saee_commercial_matrix_update_execution_approval_phrase_intake.py "
                f"--phrase '{EXACT_APPROVAL_PHRASE}' --write-human-filled"
            ),
            "python3 scripts/saee_commercial_matrix_update_execution_approval_validator.py",
            "python3 scripts/saee_commercial_matrix_update_execution_dry_run.py",
            (
                "python3 scripts/saee_commercial_matrix_update_execution_applier.py "
                "--apply --confirm-human-approved-matrix-update"
            ),
            "python3 scripts/mainline_guard.py",
            "make check",
        ],
        "source_paths": {
            "support_reconciliation": rel(SUPPORT_RECONCILIATION),
            "copy_card": rel(COPY_CARD),
            "copy_card_markdown": rel(COPY_CARD_MD),
            "phrase_intake": rel(PHRASE_INTAKE),
            "approval_validation": rel(APPROVAL_VALIDATION),
            "dry_run": rel(DRY_RUN),
            "applier": rel(APPLIER),
        },
        **FALSE_FLAGS,
    }


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    commands = "\n".join(f"1. `{cmd}`" for cmd in payload["approval_commands_after_exact_phrase"])
    OUT_MD.write_text(
        f"""# SAEE Commercial Matrix Update Execution Next Step Router v0.1

Status: `{payload['status']}`

This router records the current matrix-update execution next step. It does not
write approval input, execute matrix updates, modify canonical files, close
blockers, publish pricing, enable checkout, or claim production readiness.

## Current Required Human Action

{payload['current_required_human_action']}

## Exact Approval Phrase

`{EXACT_APPROVAL_PHRASE}`

## Command Chain After Exact Human Approval

{commands}

## Current Truth

- support_ready_for_phrase: `{str(payload['support_ready_for_phrase']).lower()}`
- copy_card_ready: `{str(payload['copy_card_ready']).lower()}`
- phrase_intake_written: `{str(payload['phrase_intake_written']).lower()}`
- approval_ready_for_matrix_update_execution: `{str(payload['approval_ready_for_matrix_update_execution']).lower()}`
- matrix_update_executed: `false`
- blockers_closed_by_router: `0`
- production_ready: `false`
- customer_validated: `false`
- product_launched: `false`

## Boundary

- human_filled_approval_written=false
- human_execution_approved_by_router=false
- matrix_update_executed=false
- canonical_gap_matrix_modified=false
- blocker_closure_authorized=false
- blockers_closed_by_router=0
- pricing_page_published=false
- checkout_enabled=false
- production_ready=false
- customer_validated=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# SAEE Commercial Matrix Update Execution Next Step Router Boundary Audit

- No approval input written by this router.
- No matrix update executed by this router.
- No canonical gap matrix modified.
- No canonical closure board modified.
- No blocker closure authorized.
- No blocker closed.
- No pricing page published.
- No checkout enabled.
- No customer contacted.
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
        f"""# SAEE Commercial Matrix Update Execution Next Step Router v0.1

commercial_matrix_update_execution_next_step_router_v0_1: true
status: {payload['status']}
exact_approval_phrase_required: true
human_filled_approval_written: false
matrix_update_executed: false
blockers_closed_by_router: 0
production_ready: false
customer_validated: false

This surface is the current local routing layer for the matrix update execution
approval point. It reduces ambiguity but does not execute anything.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Commercial Matrix Update Execution Next Step Router Gate

answer: {payload['status']}

reason: The support-contact/support-group evidence chain is ready for the
narrow matrix review-ready marker path, but matrix update execution still
requires an exact human approval phrase.

boundary:
- human_filled_approval_written: false
- matrix_update_executed: false
- canonical_gap_matrix_modified: false
- blocker_closure_authorized: false
- blockers_closed_by_router: 0
- pricing_page_published: false
- checkout_enabled: false
- production_ready: false
- customer_validated: false

next_action: {payload['current_required_human_action']}
""",
        encoding="utf-8",
    )


def update_indexes(payload: dict[str, Any]) -> None:
    for line in [
        "/phase_b_product/commercial_readiness/COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_V0_1.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_next_step_router.local.json",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_next_step_router.md",
        "/phase_b_product/commercial_readiness/matrix_update_requests/commercial_matrix_update_execution_next_step_router_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER_GATE.md",
        "/scripts/saee_commercial_matrix_update_execution_next_step_router.py",
        "/scripts/saee_commercial_matrix_update_execution_next_step_router_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["commercial_matrix_update_execution_next_step_router_v0_1"] = {
        "commercial_matrix_update_execution_next_step_router_v0_1": True,
        "router_type": "matrix_update_execution_next_step_no_execution",
        "status": payload["status"],
        "exact_approval_phrase_required": True,
        "support_ready_for_phrase": payload["support_ready_for_phrase"],
        "copy_card_ready": payload["copy_card_ready"],
        "phrase_intake_written": payload["phrase_intake_written"],
        "approval_ready_for_matrix_update_execution": payload[
            "approval_ready_for_matrix_update_execution"
        ],
        "human_filled_approval_written": False,
        "human_execution_approved_by_router": False,
        "matrix_update_executed": False,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_router": 0,
        "pricing_page_published": False,
        "checkout_enabled": False,
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
            "runner": "scripts/saee_commercial_matrix_update_execution_next_step_router.py",
            "smoke": "scripts/saee_commercial_matrix_update_execution_next_step_router_smoke.py",
        },
    }
    AGENT_INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    body = f"""## Commercial Matrix Update Execution Next Step Router

Commercial Matrix Update Execution Next Step Router v0.1 records
`status={payload['status']}`. It identifies the exact human approval phrase
required before any structured approval input can be written. It does not
execute matrix updates, close blockers, publish pricing, enable checkout, claim
production readiness, or claim customer validation.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER", body)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    update_indexes(payload)
    print(
        "SAEE_COMMERCIAL_MATRIX_UPDATE_EXECUTION_NEXT_STEP_ROUTER: PASS "
        f"status={payload['status']} "
        "matrix_update_executed=false blockers_closed_by_router=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
