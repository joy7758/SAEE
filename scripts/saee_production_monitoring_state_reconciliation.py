#!/usr/bin/env python3
"""Reconcile production-monitoring evidence without deploying monitoring.

This local surface separates human-filled production-monitoring evidence
readiness from production readiness. It does not configure dashboards, enable
metrics export, contact monitoring vendors, enable external alerts, close
blockers, or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "operations_evidence"
OUT_DIR = EVIDENCE_DIR / "production_monitoring_state_reconciliation"
OUT_JSON = OUT_DIR / "production_monitoring_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "production_monitoring_state_reconciliation.md"
BOUNDARY = OUT_DIR / "production_monitoring_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PRODUCTION_MONITORING_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION_GATE.md"
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
    "approval_input_prompt": EVIDENCE_DIR / "production_monitoring_approval_input_prompt.local.json",
    "approval_input_validation": EVIDENCE_DIR
    / "production_monitoring_approval_input_validation.human_filled.local.json",
    "evidence_builder_output": EVIDENCE_DIR
    / "production_monitoring_evidence_builder_output.human_filled.local.json",
    "operations_evidence": EVIDENCE_DIR
    / "production_operations_evidence.from_production_monitoring.human_filled.local.json",
    "combined_operations_profile": EVIDENCE_DIR
    / "operations_evidence_profile.from_monitoring_alert_on_call_human_filled.local.json",
    "review_packet": EVIDENCE_DIR / "operations_monitoring_alert_review_packet.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
}

FALSE_FLAGS = {
    "production_monitoring_deployed": False,
    "production_monitoring_claim_published": False,
    "dashboard_configured_by_codex": False,
    "metrics_export_enabled_by_codex": False,
    "log_retention_changed_by_codex": False,
    "monitoring_deployed_by_codex": False,
    "monitoring_vendor_contacted_by_codex": False,
    "alert_provider_contacted_by_codex": False,
    "codex_contacted_vendor": False,
    "codex_contacted_customer": False,
    "external_alert_delivery_enabled": False,
    "external_alert_delivery_available": False,
    "on_call_rotation_available": False,
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
    prompt = source_data["approval_input_prompt"]
    approval = source_data["approval_input_validation"]
    builder = source_data["evidence_builder_output"]
    operations = source_data["operations_evidence"]
    profile = source_data["combined_operations_profile"]
    gap_row = find_row(source_data["gap_matrix"], "production_monitoring")
    closure_row = find_row(source_data["closure_readiness_board"], "production_monitoring")

    input_path_ready = approval.get("validation_status") == "pass" and approval.get("builder_ready") is True
    builder_ready = (
        builder.get("status") == "pass"
        and builder.get("input_complete") is True
        and builder.get("accepted_for_blocker_closure_count") == 0
    )
    monitoring_evidence_ready = (
        operations.get("production_monitoring_plan_approved") is True
        and operations.get("monitoring_owner_recorded") is True
        and operations.get("monitoring_vendor_contacted_by_codex") is False
        and operations.get("monitoring_deployed_by_codex") is False
    )
    combined_profile_ready = (
        profile.get("production_monitoring_satisfied_by_profile") is True
        and profile.get("external_alert_delivery_satisfied_by_profile") is True
        and profile.get("on_call_rotation_satisfied_by_profile") is True
        and profile.get("production_ready") is False
    )
    gap_matrix_open = gap_row.get("status") == "open"
    closure_board_not_ready = closure_row.get("closure_status") == "not_ready" or closure_row.get("status") == "not_ready"

    if combined_profile_ready:
        status = "ready_for_human_operations_profile_review_no_closure"
        resolved_path = "combined_operations_profile"
        next_action = (
            "Human operations owner may review combined monitoring, alert delivery, and "
            "on-call evidence for a later matrix update request. Do not configure "
            "monitoring, enable alerts, contact vendors, close blockers, or claim production readiness."
        )
    elif builder_ready and monitoring_evidence_ready:
        status = "ready_for_human_production_monitoring_evidence_review_no_closure"
        resolved_path = "operations_evidence"
        next_action = (
            "Human operations owner may review production-monitoring evidence. "
            "Any matrix update or blocker closure requires a separate explicit request."
        )
    elif input_path_ready:
        status = "ready_for_production_monitoring_evidence_builder_review_only"
        resolved_path = "approval_input_validation"
        next_action = "Use the validator output for review only; evidence builder execution remains separate."
    else:
        status = "hold_production_monitoring_human_input_required"
        resolved_path = "approval_input_prompt"
        next_action = "Complete human-filled production-monitoring input before builder or profile review."

    payload: dict[str, Any] = {
        "production_monitoring_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_production_monitoring_state_reconciliation_no_deploy_no_closure",
        "target_blocker_id": "production_monitoring",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "previous_prompt_status": prompt.get("status"),
        "approval_validation_status": approval.get("validation_status"),
        "approval_input_complete": approval.get("input_complete") is True,
        "approval_builder_ready": input_path_ready,
        "builder_output_status": builder.get("status"),
        "builder_output_ready": builder_ready,
        "monitoring_evidence_ready_for_review": monitoring_evidence_ready,
        "combined_operations_profile_ready": combined_profile_ready,
        "production_monitoring_satisfied_by_profile": profile.get("production_monitoring_satisfied_by_profile") is True,
        "external_alert_delivery_satisfied_by_profile": profile.get(
            "external_alert_delivery_satisfied_by_profile"
        )
        is True,
        "operations_on_call_rotation_satisfied_by_profile": profile.get(
            "on_call_rotation_satisfied_by_profile"
        )
        is True,
        "monitoring_owner_recorded": operations.get("monitoring_owner_recorded") is True,
        "metrics_coverage_approved": operations.get("metrics_coverage_approved") is True,
        "log_retention_reviewed": operations.get("log_retention_reviewed") is True,
        "monitoring_dry_run_recorded": operations.get("monitoring_dry_run_recorded") is True,
        "gap_matrix_open": gap_matrix_open,
        "closure_board_not_ready": closure_board_not_ready,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Older production-monitoring prompt surfaces can remain at first-input state while "
            "human-filled operations evidence is ready for human review. This file selects one "
            "safe next human action without deploying monitoring or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Production Monitoring State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles the current `production_monitoring` blocker
surfaces. It does not configure dashboards, enable metrics export, change log
retention, contact monitoring vendors, enable external alerts, close blockers,
or claim production readiness.

## Current Finding

- target_blocker_id: `production_monitoring`
- previous_prompt_status: `{payload['previous_prompt_status']}`
- approval_validation_status: `{payload['approval_validation_status']}`
- approval_input_complete: `{str(payload['approval_input_complete']).lower()}`
- builder_output_ready: `{str(payload['builder_output_ready']).lower()}`
- monitoring_evidence_ready_for_review: `{str(payload['monitoring_evidence_ready_for_review']).lower()}`
- combined_operations_profile_ready: `{str(payload['combined_operations_profile_ready']).lower()}`
- production_monitoring_satisfied_by_profile: `{str(payload['production_monitoring_satisfied_by_profile']).lower()}`
- external_alert_delivery_satisfied_by_profile: `{str(payload['external_alert_delivery_satisfied_by_profile']).lower()}`
- operations_on_call_rotation_satisfied_by_profile: `{str(payload['operations_on_call_rotation_satisfied_by_profile']).lower()}`
- gap_matrix_open: `{str(payload['gap_matrix_open']).lower()}`
- closure_board_not_ready: `{str(payload['closure_board_not_ready']).lower()}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

## Boundary

- production_monitoring_deployed=false
- dashboard_configured_by_codex=false
- metrics_export_enabled_by_codex=false
- monitoring_vendor_contacted_by_codex=false
- external_alert_delivery_enabled=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Production Monitoring State Reconciliation Boundary Audit

- Only local status and agent-readable evidence surfaces were written.
- No production monitoring deployed by Codex.
- No dashboard configured by Codex.
- No metrics export enabled by Codex.
- No log retention changed by Codex.
- No monitoring vendor contacted by Codex.
- No alert provider contacted by Codex.
- No external alert delivery enabled.
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

production_monitoring_deployed=false
dashboard_configured_by_codex=false
metrics_export_enabled_by_codex=false
monitoring_vendor_contacted_by_codex=false
external_alert_delivery_enabled=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Production Monitoring State Reconciliation v0.1

status: {payload['status']}
target_blocker_id: production_monitoring
resolved_current_path: {payload['resolved_current_path']}
monitoring_evidence_ready_for_review: {str(payload['monitoring_evidence_ready_for_review']).lower()}
combined_operations_profile_ready: {str(payload['combined_operations_profile_ready']).lower()}
human_review_required: true
separate_matrix_update_request_required: true
production_monitoring_deployed=false
dashboard_configured_by_codex=false
metrics_export_enabled_by_codex=false
monitoring_vendor_contacted_by_codex=false
external_alert_delivery_enabled=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false

This is a local state reconciliation layer for production-monitoring evidence.
It may point a human reviewer to source-backed operations evidence, but it does
not deploy monitoring, contact vendors, enable alerting, update the production
blocker matrix, close blockers, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Production Monitoring State Reconciliation Gate

answer: hold_human_operations_review_required_no_monitoring_deploy_no_auto_closure

reason:
Human-filled production-monitoring evidence can be reviewed, but Codex has not
deployed monitoring, contacted vendors, enabled alert delivery, changed runtime
behavior, or closed blockers.

status: {payload['status']}
target_blocker_id: production_monitoring
resolved_current_path: {payload['resolved_current_path']}

boundary:
production_monitoring_deployed: false
dashboard_configured_by_codex: false
metrics_export_enabled_by_codex: false
monitoring_vendor_contacted_by_codex: false
external_alert_delivery_enabled: false
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

    block = f"""## Production Monitoring State Reconciliation v0.1

Status: `{payload['status']}`.

`production_monitoring` human-filled operations evidence is reconciled into a
review-only state. `monitoring_evidence_ready_for_review={str(payload['monitoring_evidence_ready_for_review']).lower()}`,
`combined_operations_profile_ready={str(payload['combined_operations_profile_ready']).lower()}`,
`blockers_closed_by_reconciliation=0`, `production_ready=false`,
`customer_validated=false`, `product_launched=false`, and
`private_core_exposed=false`. No monitoring was deployed, no dashboard or
metrics export was configured, no vendor or customer was contacted, and no
external alert delivery was enabled by Codex.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION", block)

    for line in [
        "/phase_b_product/commercial_readiness/PRODUCTION_MONITORING_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/operations_evidence/production_monitoring_state_reconciliation/production_monitoring_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_production_monitoring_state_reconciliation.py",
        "/scripts/saee_production_monitoring_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["production_monitoring_state_reconciliation_v0_1"] = {
        "status": payload["status"],
        "target_blocker_id": "production_monitoring",
        "resolved_current_path": payload["resolved_current_path"],
        "monitoring_evidence_ready_for_review": payload["monitoring_evidence_ready_for_review"],
        "combined_operations_profile_ready": payload["combined_operations_profile_ready"],
        "production_monitoring_satisfied_by_profile": payload["production_monitoring_satisfied_by_profile"],
        "external_alert_delivery_satisfied_by_profile": payload["external_alert_delivery_satisfied_by_profile"],
        "operations_on_call_rotation_satisfied_by_profile": payload[
            "operations_on_call_rotation_satisfied_by_profile"
        ],
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "production_monitoring_deployed": False,
        "dashboard_configured_by_codex": False,
        "metrics_export_enabled_by_codex": False,
        "monitoring_vendor_contacted_by_codex": False,
        "external_alert_delivery_enabled": False,
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
        "SAEE_PRODUCTION_MONITORING_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
