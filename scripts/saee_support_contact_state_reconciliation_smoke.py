#!/usr/bin/env python3
"""Smoke test for support-contact state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_support_contact_state_reconciliation.py"
OUT_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation"
SUMMARY = OUT_DIR / "support_contact_state_reconciliation.local.json"
REPORT = OUT_DIR / "support_contact_state_reconciliation.md"
BOUNDARY = OUT_DIR / "support_contact_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SUPPORT_CONTACT_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION_SMOKE: FAIL " + message)


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
    require("SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "support_contact_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_support_contact_state_reconciliation_no_closure",
        "target_blocker_id": "support_contact",
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
        "matrix_update_executed": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(str(payload.get("status", "")).startswith(("ready_", "hold_")), "status must be ready/hold")
    require(payload.get("resolved_current_path") in payload.get("source_paths", {}), "resolved path must name a source")
    require(payload.get("closure_review_ready") is True, "current support-contact path should be closure-review ready")
    require(payload.get("support_group_evidence_complete") is True, "support group evidence should be complete")
    require(payload.get("final_closure_decision_ready") is True, "final closure decision should be ready")
    require(payload.get("matrix_update_request_ready") is True, "matrix update request should be ready")
    require(payload.get("matrix_update_execution_request_ready") is True, "matrix execution request should be ready")
    require(payload.get("matrix_update_approval_copy_card_ready") is True, "approval copy card should be ready")
    require(
        payload.get("resolved_current_path") == "matrix_update_approval_copy_card",
        "resolved path should point to approval copy card",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Support Contact State Reconciliation",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "matrix_update_approval_copy_card_ready: true",
        "No support contact published by Codex",
        "answer: hold_human_review_required_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
        "support_contact_published=true",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/SUPPORT_CONTACT_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/support_evidence/support_contact_state_reconciliation/support_contact_state_reconciliation.md",
        "/docs/strategy/SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_support_contact_state_reconciliation.py",
        "/scripts/saee_support_contact_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("support_contact_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing support_contact_state_reconciliation_v0_1")
    for key in expected:
        require(entry.get(key) == expected[key], f"agent-index {key} must match")
    require(entry.get("status") == payload.get("status"), "agent-index status must match")
    require(entry.get("resolved_current_path") == payload.get("resolved_current_path"), "agent-index path must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Support Contact State Reconciliation v0.1",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_SUPPORT_CONTACT_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
