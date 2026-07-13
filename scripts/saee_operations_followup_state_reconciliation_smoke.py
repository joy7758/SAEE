#!/usr/bin/env python3
"""Smoke test for operations follow-up state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_operations_followup_state_reconciliation.py"
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/operations_evidence/"
    "operations_followup_state_reconciliation"
)
SUMMARY = OUT_DIR / "operations_followup_state_reconciliation.local.json"
REPORT = OUT_DIR / "operations_followup_state_reconciliation.md"
BOUNDARY = OUT_DIR / "operations_followup_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "operations_followup_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_operations_followup_state_reconciliation_no_alert_no_on_call_no_closure",
        "external_alert_delivery_ready_for_review": True,
        "on_call_rotation_ready_for_review": True,
        "combined_operations_profile_ready": True,
        "external_alert_delivery_satisfied_by_profile": True,
        "on_call_rotation_satisfied_by_profile": True,
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
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
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("status") == "ready_for_human_operations_followup_review_no_closure",
        "status must be review-ready no-closure",
    )
    require(payload.get("target_blocker_ids") == ["external_alert_delivery", "on_call_rotation"], "target blockers mismatch")
    require(payload.get("resolved_current_path") == "combined_operations_profile", "resolved path mismatch")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Operations Follow-up State Reconciliation",
        "external_alert_delivery_enabled=false",
        "alert_provider_contacted_by_codex=false",
        "on_call_rotation_started=false",
        "on_call_rotation_started_by_codex=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "No external alert delivery enabled",
        "No on-call rotation started",
        "answer: hold_human_operations_followup_review_required_no_alert_no_on_call_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "external_alert_delivery_enabled=true",
        "alert_provider_contacted_by_codex=true",
        "on_call_rotation_started=true",
        "on_call_rotation_started_by_codex=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/operations_evidence/operations_followup_state_reconciliation/operations_followup_state_reconciliation.md",
        "/docs/strategy/SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_operations_followup_state_reconciliation.py",
        "/scripts/saee_operations_followup_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("operations_followup_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing operations_followup_state_reconciliation_v0_1")
    for key in [
        "status",
        "target_blocker_ids",
        "resolved_current_path",
        "external_alert_delivery_ready_for_review",
        "on_call_rotation_ready_for_review",
        "combined_operations_profile_ready",
        "external_alert_delivery_satisfied_by_profile",
        "on_call_rotation_satisfied_by_profile",
        "external_alert_delivery_enabled",
        "alert_provider_contacted_by_codex",
        "on_call_rotation_started",
        "on_call_rotation_started_by_codex",
        "blockers_closed_by_reconciliation",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Operations Follow-up State Reconciliation v0.1",
        "external_alert_delivery_ready_for_review=true",
        "on_call_rotation_ready_for_review=true",
        "combined_operations_profile_ready=true",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_OPERATIONS_FOLLOWUP_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
