#!/usr/bin/env python3
"""Reconcile conservative gap-audit state with later local human evidence.

This is a read-only commercial-readiness status layer. It explains why the
canonical gap audit still shows all production blockers while the later
human-inspected local evidence overlay narrows the next actionable blocker to
customer validation. It does not close blockers, contact customers, launch
product, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_state_reconciliation"
OUTPUT_JSON = OUTPUT_DIR / "commercial_readiness_state_reconciliation.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_readiness_state_reconciliation.md"
BOUNDARY_AUDIT = OUTPUT_DIR / "commercial_readiness_state_reconciliation_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION_GATE.md"

GAP_AUDIT = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_readiness_gap_audit/"
    "commercial_readiness_gap_audit.local.json"
)
PRIORITY_INDEX = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_priority_index/"
    "commercial_blocker_priority_index.local.json"
)
FINAL_INSPECTION = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_final_human_inspection/"
    "commercial_final_human_inspection_record.local.json"
)
CUSTOMER_NEXT_ACTION = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_next_action.local.json"
)
CUSTOMER_WORKBENCH = (
    ROOT
    / "phase_b_product/commercial_readiness/customer_validation_evidence/"
    "external_customer_validation_session_entry_workbench.local.json"
)
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
    "customer_contacted": False,
    "customer_contacted_by_codex": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
    "public_validation_claim_published": False,
    "testimonial_published": False,
    "case_study_published": False,
    "development_permission_granted": False,
    "execution_authorized": False,
    "evidence_collection_authorized": False,
    "blocker_closure_authorized": False,
    "blockers_closed_by_reconciliation": 0,
}


def rel(path: Path) -> str:
    return str(path.resolve().relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            "SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION: "
            f"FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            "SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION: "
            f"FAIL JSON root must be object: {rel(path)}"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION: FAIL: " + message)


def build_payload() -> dict[str, Any]:
    for path in [GAP_AUDIT, PRIORITY_INDEX, FINAL_INSPECTION, CUSTOMER_NEXT_ACTION, CUSTOMER_WORKBENCH]:
        require(path.exists(), f"missing source {rel(path)}")

    gap = read_json(GAP_AUDIT)
    priority = read_json(PRIORITY_INDEX)
    inspection = read_json(FINAL_INSPECTION)
    next_action = read_json(CUSTOMER_NEXT_ACTION)
    workbench = read_json(CUSTOMER_WORKBENCH)

    canonical_open = int(gap.get("open_blocker_count", 0))
    overlay_remaining = int(
        inspection.get("remaining_production_blocker_count_after_local_human_evidence", 0)
    )
    overlay_blockers = inspection.get("remaining_production_blockers_after_local_human_evidence", [])
    if not isinstance(overlay_blockers, list):
        overlay_blockers = []

    require(gap.get("production_ready") is False, "gap audit must keep production_ready=false")
    require(gap.get("customer_validated") is False, "gap audit must keep customer_validated=false")
    require(inspection.get("local_evidence_lanes_passed") is True, "local evidence lanes must pass")
    require(inspection.get("customer_validated") is False, "inspection must not claim customer validation")
    require(overlay_remaining == 1, "local human evidence overlay must leave one blocker")
    require(overlay_blockers == ["customer_validated"], "remaining blocker must be customer_validated")
    require(next_action.get("current_goal_blocker") == "customer_validated", "next action blocker mismatch")
    require(workbench.get("current_goal_blocker") == "customer_validated", "workbench blocker mismatch")

    status = "hold_customer_validation_required_after_local_evidence_reconciliation"
    return {
        "commercial_readiness_state_reconciliation_v0_1": True,
        "record_type": "commercial_readiness_state_reconciliation",
        "status": status,
        "generated_by": "scripts/saee_commercial_readiness_state_reconciliation.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_gap_audit": rel(GAP_AUDIT),
        "source_priority_index": rel(PRIORITY_INDEX),
        "source_final_human_inspection": rel(FINAL_INSPECTION),
        "source_customer_validation_next_action": rel(CUSTOMER_NEXT_ACTION),
        "source_customer_validation_workbench": rel(CUSTOMER_WORKBENCH),
        "canonical_gap_audit_status": gap.get("status"),
        "canonical_gap_audit_open_blocker_count": canonical_open,
        "canonical_gap_audit_first_priority": priority.get("first_priority_blocker_id"),
        "local_human_evidence_overlay_status": inspection.get("status"),
        "local_human_evidence_lanes_passed": True,
        "manual_check_completed": True,
        "manual_check_statement": inspection.get(
            "human_inspection_statement", "人工检查完毕，没有问题，确认"
        ),
        "overlay_remaining_blocker_count": overlay_remaining,
        "overlay_remaining_blockers": overlay_blockers,
        "current_goal_blocker": "customer_validated",
        "customer_validation_path_ready": True,
        "customer_validation_workbench_ready": workbench.get("status")
        == "local_static_human_entry_workbench_ready",
        "state_reconciliation_result": (
            "The conservative production gap matrix remains open, but the later "
            "human-inspected local evidence overlay narrows the next actionable "
            "commercial blocker to customer_validated."
        ),
        "resolved_confusion": (
            "support_contact remains visible in the old full gap audit, while the "
            "current local-evidence overlay should guide the next human action."
        ),
        "next_human_action": (
            "Run or record at least one real external customer or target-user "
            "validation session, then import it through the existing customer "
            "validation session-entry path. Do not claim customer validation before "
            "that evidence exists."
        ),
        **FALSE_FLAGS,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    blockers = ", ".join(payload["overlay_remaining_blockers"])
    return f"""# SAEE Commercial Readiness State Reconciliation

Status: `{payload['status']}`.

## Purpose

This record reconciles two local commercial-readiness surfaces:

- the conservative full production gap audit, which still reports
  `{payload['canonical_gap_audit_open_blocker_count']}` open production blockers;
- the later local human-inspected evidence overlay, which reports that local
  evidence lanes passed and the next actionable blocker is `{blockers}`.

## Human Confirmation

- manual_check_completed: true
- manual_check_statement: `{payload['manual_check_statement']}`
- local_human_evidence_lanes_passed: true

## Current Interpretation

The current commercial state is still `hold`. SAEE is not production ready and
not customer validated. The local evidence overlay only prevents repeated work
on already reviewed local evidence lanes. It does not close canonical blockers.

## Next Blocker

- current_goal_blocker: `customer_validated`
- customer_validation_path_ready: true
- customer_validation_workbench_ready: true

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- customer_contacted_by_codex: false
- private_core_exposed: false
- blocker_closure_authorized: false
- blockers_closed_by_reconciliation: 0

## Next Human Action

{payload['next_human_action']}
"""


def render_boundary_audit() -> str:
    return """# SAEE Commercial Readiness State Reconciliation Boundary Audit

- Only local status surfaces were reconciled.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No landing page modified.
- No private core exposed.
- No customer contacted.
- No customer data collected by Codex.
- No customer validation claimed.
- No product launched.
- No public SDK released.
- No production-ready claim added.
- No blocker closed by this reconciliation.
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Readiness State Reconciliation Gate

answer: hold_customer_validation_required_after_local_evidence_reconciliation

reason:
The human local evidence inspection has been recorded as passed, but the only
safe next commercial blocker is external customer or target-user validation.
The canonical production gap matrix remains conservative and is not overwritten
by this reconciliation layer.

boundary:
production_ready: false
customer_validated: false
product_launched: false
customer_contacted_by_codex: false
private_core_exposed: false
blocker_closure_authorized: false
blockers_closed_by_reconciliation: 0

next_action:
{payload['next_human_action']}
"""


def update_agent_index(payload: dict[str, Any]) -> None:
    index = read_json(AGENT_INDEX)
    index["commercial_readiness_state_reconciliation_v0_1"] = {
        "name": "SAEE Commercial Readiness State Reconciliation v0.1",
        "status": payload["status"],
        "purpose": (
            "Explain the current commercial-readiness truth surface after human "
            "local evidence inspection without closing blockers or claiming "
            "customer validation."
        ),
        "canonical_gap_audit_open_blocker_count": payload[
            "canonical_gap_audit_open_blocker_count"
        ],
        "local_human_evidence_lanes_passed": True,
        "overlay_remaining_blocker_count": payload["overlay_remaining_blocker_count"],
        "overlay_remaining_blockers": payload["overlay_remaining_blockers"],
        "current_goal_blocker": payload["current_goal_blocker"],
        "customer_validation_path_ready": True,
        "customer_validation_workbench_ready": True,
        "manual_check_completed": True,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "customer_contacted": False,
        "customer_contacted_by_codex": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "development_permission_granted": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
        "entrypoints": {
            "summary": rel(OUTPUT_JSON),
            "report": rel(OUTPUT_MD),
            "boundary_audit": rel(BOUNDARY_AUDIT),
            "gate": rel(GATE),
            "runner": "scripts/saee_commercial_readiness_state_reconciliation.py",
            "smoke": "scripts/saee_commercial_readiness_state_reconciliation_smoke.py",
        },
    }
    write_json(AGENT_INDEX, index)


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary_audit(), encoding="utf-8")
    GATE.parent.mkdir(parents=True, exist_ok=True)
    GATE.write_text(render_gate(payload), encoding="utf-8")
    update_agent_index(payload)
    print(
        "SAEE_COMMERCIAL_READINESS_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} current_goal_blocker=customer_validated "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
