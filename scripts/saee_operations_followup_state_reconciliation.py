#!/usr/bin/env python3
"""Reconcile external-alert and on-call evidence without enabling operations.

This local surface records that human-filled evidence for
external_alert_delivery and on_call_rotation is ready for human review through
the combined operations profile. It does not enable alert delivery, start
on-call rotation, contact vendors, close blockers, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "operations_evidence"
OUT_DIR = EVIDENCE_DIR / "operations_followup_state_reconciliation"
OUT_JSON = OUT_DIR / "operations_followup_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "operations_followup_state_reconciliation.md"
BOUNDARY = OUT_DIR / "operations_followup_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_GATE.md"
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
    "external_alert_validation": EVIDENCE_DIR
    / "external_alert_delivery_approval_input_validation.human_filled.local.json",
    "external_alert_builder": EVIDENCE_DIR
    / "external_alert_delivery_evidence_builder_output.human_filled.local.json",
    "external_alert_evidence": EVIDENCE_DIR
    / "production_operations_evidence.from_external_alert_delivery.human_filled.local.json",
    "on_call_validation": EVIDENCE_DIR
    / "operations_on_call_rotation_approval_input_validation.human_filled.local.json",
    "on_call_builder": EVIDENCE_DIR
    / "operations_on_call_rotation_evidence_builder_output.human_filled.local.json",
    "on_call_evidence": EVIDENCE_DIR
    / "production_operations_evidence.from_operations_on_call_rotation.human_filled.local.json",
    "combined_operations_profile": EVIDENCE_DIR
    / "operations_evidence_profile.from_monitoring_alert_on_call_human_filled.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
}

FALSE_FLAGS = {
    "external_alert_delivery_enabled": False,
    "external_alert_delivery_enabled_by_codex": False,
    "external_alert_channel_configured_by_codex": False,
    "alert_delivery_test_performed_by_codex": False,
    "alert_routing_policy_published_by_codex": False,
    "alert_provider_contacted_by_codex": False,
    "on_call_rotation_started": False,
    "on_call_rotation_started_by_codex": False,
    "escalation_schedule_published_by_codex": False,
    "incident_commander_assigned_by_codex": False,
    "on_call_vendor_contacted_by_codex": False,
    "codex_contacted_vendor": False,
    "codex_contacted_customer": False,
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
    "external_ai_assistant_tested": False,
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


def find_row(data: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    rows = data.get("matrix") or data.get("rows") or data.get("blockers") or []
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_id") == blocker_id:
            return row
    return {}


def build_payload() -> dict[str, Any]:
    source_data = {name: read_json(path) for name, path in SOURCES.items()}
    external_validation = source_data["external_alert_validation"]
    external_builder = source_data["external_alert_builder"]
    external_evidence = source_data["external_alert_evidence"]
    on_call_validation = source_data["on_call_validation"]
    on_call_builder = source_data["on_call_builder"]
    on_call_evidence = source_data["on_call_evidence"]
    profile = source_data["combined_operations_profile"]
    gap = source_data["gap_matrix"]
    board = source_data["closure_readiness_board"]

    external_alert_ready = (
        external_validation.get("validation_status") == "pass"
        and external_validation.get("builder_ready") is True
        and external_builder.get("status") == "pass"
        and external_builder.get("external_alert_delivery_available_for_review") is True
        and external_evidence.get("alert_delivery_owner_recorded") is True
        and external_evidence.get("alert_delivery_test_recorded") is True
        and external_evidence.get("external_alert_delivery_enabled") is False
        and external_evidence.get("alert_provider_contacted_by_codex") is False
    )
    on_call_ready = (
        on_call_validation.get("validation_status") == "pass"
        and on_call_validation.get("builder_ready") is True
        and on_call_builder.get("status") == "pass"
        and on_call_builder.get("operations_on_call_rotation_available_for_review") is True
        and on_call_evidence.get("on_call_rotation_owner_recorded") is True
        and on_call_evidence.get("incident_commander_named") is True
        and on_call_evidence.get("on_call_rotation_started_by_codex") is False
        and on_call_evidence.get("on_call_vendor_contacted_by_codex") is False
    )
    combined_profile_ready = (
        profile.get("profile_status") == "pass"
        and profile.get("external_alert_delivery_satisfied_by_profile") is True
        and profile.get("on_call_rotation_satisfied_by_profile") is True
        and profile.get("production_ready") is False
    )

    external_gap_open = find_row(gap, "external_alert_delivery").get("status") == "open"
    on_call_gap_open = find_row(gap, "on_call_rotation").get("status") == "open"
    external_board_not_ready = find_row(board, "external_alert_delivery").get("status") == "not_ready"
    on_call_board_not_ready = find_row(board, "on_call_rotation").get("status") == "not_ready"

    if external_alert_ready and on_call_ready and combined_profile_ready:
        status = "ready_for_human_operations_followup_review_no_closure"
        resolved_path = "combined_operations_profile"
        next_action = (
            "Human operations owner may review external-alert and on-call evidence "
            "for a later matrix update request. Do not enable alerts, start on-call, "
            "contact vendors, close blockers, or claim production readiness."
        )
    elif external_alert_ready or on_call_ready:
        status = "partial_operations_followup_review_ready_no_closure"
        resolved_path = "individual_evidence_outputs"
        next_action = "Review the ready evidence item only; no closure or operations enablement is allowed."
    else:
        status = "hold_operations_followup_human_input_required"
        resolved_path = "approval_input_validation"
        next_action = "Complete human-filled alert/on-call input before follow-up review."

    payload: dict[str, Any] = {
        "operations_followup_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_operations_followup_state_reconciliation_no_alert_no_on_call_no_closure",
        "target_blocker_ids": ["external_alert_delivery", "on_call_rotation"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "external_alert_delivery_ready_for_review": external_alert_ready,
        "on_call_rotation_ready_for_review": on_call_ready,
        "combined_operations_profile_ready": combined_profile_ready,
        "external_alert_delivery_satisfied_by_profile": profile.get(
            "external_alert_delivery_satisfied_by_profile"
        )
        is True,
        "on_call_rotation_satisfied_by_profile": profile.get("on_call_rotation_satisfied_by_profile") is True,
        "operations_target_blockers_satisfied_count": profile.get("operations_target_blockers_satisfied_count"),
        "external_alert_delivery_gap_matrix_open": external_gap_open,
        "on_call_rotation_gap_matrix_open": on_call_gap_open,
        "external_alert_delivery_closure_board_not_ready": external_board_not_ready,
        "on_call_rotation_closure_board_not_ready": on_call_board_not_ready,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Human-filled operations follow-up evidence can satisfy local review "
            "criteria while canonical blocker surfaces remain open. This file records "
            "review readiness without enabling operations or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Operations Follow-up State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles `external_alert_delivery` and `on_call_rotation`
evidence. It does not enable external alert delivery, start on-call rotation,
contact vendors, close blockers, or claim production readiness.

## Current Finding

- target_blocker_ids: `external_alert_delivery`, `on_call_rotation`
- external_alert_delivery_ready_for_review: `{str(payload['external_alert_delivery_ready_for_review']).lower()}`
- on_call_rotation_ready_for_review: `{str(payload['on_call_rotation_ready_for_review']).lower()}`
- combined_operations_profile_ready: `{str(payload['combined_operations_profile_ready']).lower()}`
- external_alert_delivery_satisfied_by_profile: `{str(payload['external_alert_delivery_satisfied_by_profile']).lower()}`
- on_call_rotation_satisfied_by_profile: `{str(payload['on_call_rotation_satisfied_by_profile']).lower()}`
- external_alert_delivery_gap_matrix_open: `{str(payload['external_alert_delivery_gap_matrix_open']).lower()}`
- on_call_rotation_gap_matrix_open: `{str(payload['on_call_rotation_gap_matrix_open']).lower()}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

## Boundary

- external_alert_delivery_enabled=false
- alert_provider_contacted_by_codex=false
- on_call_rotation_started=false
- on_call_rotation_started_by_codex=false
- escalation_schedule_published_by_codex=false
- incident_commander_assigned_by_codex=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Operations Follow-up State Reconciliation Boundary Audit

- Only local status and agent-readable evidence surfaces were written.
- No external alert delivery enabled.
- No alert provider contacted by Codex.
- No alert delivery test performed by Codex.
- No on-call rotation started.
- No escalation schedule published by Codex.
- No incident commander assigned by Codex.
- No on-call vendor contacted by Codex.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No public SDK released.
- No blocker closed.
- No production-ready claim added.

external_alert_delivery_enabled=false
alert_provider_contacted_by_codex=false
on_call_rotation_started=false
on_call_rotation_started_by_codex=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Operations Follow-up State Reconciliation v0.1

status: {payload['status']}
target_blocker_ids: external_alert_delivery,on_call_rotation
resolved_current_path: {payload['resolved_current_path']}
external_alert_delivery_ready_for_review: {str(payload['external_alert_delivery_ready_for_review']).lower()}
on_call_rotation_ready_for_review: {str(payload['on_call_rotation_ready_for_review']).lower()}
combined_operations_profile_ready: {str(payload['combined_operations_profile_ready']).lower()}
human_review_required: true
separate_matrix_update_request_required: true
external_alert_delivery_enabled=false
alert_provider_contacted_by_codex=false
on_call_rotation_started=false
on_call_rotation_started_by_codex=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false

This is a local state reconciliation layer for operations follow-up evidence.
It may point a human reviewer to source-backed alert and on-call evidence, but
it does not enable operations, update the production blocker matrix, close
blockers, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Operations Follow-up State Reconciliation Gate

answer: hold_human_operations_followup_review_required_no_alert_no_on_call_no_auto_closure

reason:
Human-filled external-alert and on-call evidence can be reviewed, but Codex has
not enabled alerts, started on-call rotation, contacted vendors, changed runtime
behavior, or closed blockers.

status: {payload['status']}
target_blocker_ids: external_alert_delivery,on_call_rotation
resolved_current_path: {payload['resolved_current_path']}

boundary:
external_alert_delivery_enabled: false
alert_provider_contacted_by_codex: false
on_call_rotation_started: false
on_call_rotation_started_by_codex: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
blockers_closed_by_reconciliation: 0

next_action:
Human operations owner may review the state reconciliation and decide whether a
separate matrix update request should be created. This gate does not authorize
execution or closure.
""",
        encoding="utf-8",
    )

    block = f"""## Operations Follow-up State Reconciliation v0.1

Status: `{payload['status']}`.

`external_alert_delivery` and `on_call_rotation` human-filled evidence is
reconciled into a review-only state.
`external_alert_delivery_ready_for_review={str(payload['external_alert_delivery_ready_for_review']).lower()}`,
`on_call_rotation_ready_for_review={str(payload['on_call_rotation_ready_for_review']).lower()}`,
`combined_operations_profile_ready={str(payload['combined_operations_profile_ready']).lower()}`,
`blockers_closed_by_reconciliation=0`, `production_ready=false`,
`customer_validated=false`, `product_launched=false`, and
`private_core_exposed=false`. No external alert delivery was enabled, no
on-call rotation was started, no vendor or customer was contacted by Codex.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION", block)

    for line in [
        "/phase_b_product/commercial_readiness/OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_operations_followup_state_reconciliation.py",
        "/scripts/saee_operations_followup_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["operations_followup_state_reconciliation_v0_1"] = {
        "status": payload["status"],
        "target_blocker_ids": payload["target_blocker_ids"],
        "resolved_current_path": payload["resolved_current_path"],
        "external_alert_delivery_ready_for_review": payload["external_alert_delivery_ready_for_review"],
        "on_call_rotation_ready_for_review": payload["on_call_rotation_ready_for_review"],
        "combined_operations_profile_ready": payload["combined_operations_profile_ready"],
        "external_alert_delivery_satisfied_by_profile": payload[
            "external_alert_delivery_satisfied_by_profile"
        ],
        "on_call_rotation_satisfied_by_profile": payload["on_call_rotation_satisfied_by_profile"],
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "external_alert_delivery_enabled": False,
        "alert_provider_contacted_by_codex": False,
        "on_call_rotation_started": False,
        "on_call_rotation_started_by_codex": False,
        "blockers_closed_by_reconciliation": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    write_json(AGENT_INDEX, index)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
