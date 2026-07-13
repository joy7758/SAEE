#!/usr/bin/env python3
"""Smoke test for privacy/security/legal follow-up reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_privacy_security_legal_followup_state_reconciliation.py"
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "privacy_security_legal_followup_state_reconciliation"
)
SUMMARY = OUT_DIR / "privacy_security_legal_followup_state_reconciliation.local.json"
REPORT = OUT_DIR / "privacy_security_legal_followup_state_reconciliation.md"
BOUNDARY = OUT_DIR / "privacy_security_legal_followup_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_SMOKE: FAIL " + message)


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
    require(
        "SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION: PASS" in result.stdout,
        "runner did not pass",
    )
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "privacy_security_legal_followup_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_privacy_security_legal_followup_state_reconciliation_no_security_review_no_legal_publication_no_closure",
        "formal_security_review_ready_for_review": True,
        "privacy_legal_review_ready_for_review": True,
        "data_processing_agreement_ready_for_review": True,
        "vulnerability_management_ready_for_review": True,
        "combined_privacy_security_legal_profile_ready": True,
        "ready_for_review_count": 4,
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "formal_security_review_completed_by_codex": False,
        "codex_performed_security_review": False,
        "codex_inspected_private_core": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "security_vendor_contacted": False,
        "security_review_claim_published": False,
        "production_security_claim_published": False,
        "production_security_enabled": False,
        "privacy_legal_review_completed_by_codex": False,
        "codex_performed_legal_review": False,
        "codex_contacted_legal_counsel": False,
        "legal_counsel_contacted": False,
        "privacy_notice_published": False,
        "codex_created_dpa": False,
        "codex_approved_dpa": False,
        "dpa_sent_to_customer": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "codex_processed_customer_data": False,
        "codex_activated_vulnerability_management": False,
        "codex_published_security_contact": False,
        "codex_ran_vulnerability_scan": False,
        "security_contact_published": False,
        "vulnerability_management_operational": False,
        "vulnerability_management_completed_by_codex": False,
        "vulnerability_management_claim_published": False,
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
        payload.get("status") == "ready_for_human_privacy_security_legal_review_no_closure",
        "status must be review-ready no-closure",
    )
    require(
        payload.get("target_blocker_ids")
        == [
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        ],
        "target blockers mismatch",
    )
    require(payload.get("resolved_current_path") == "combined_privacy_security_legal_profile", "path mismatch")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Privacy/Security/Legal Follow-up State Reconciliation",
        "codex_performed_security_review=false",
        "privacy_notice_published=false",
        "dpa_sent_to_customer=false",
        "customer_data_processed=false",
        "vulnerability_management_operational=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "No security review performed by Codex",
        "No legal counsel contacted by Codex",
        "No customer data processed",
        "answer: hold_human_privacy_security_legal_review_required_no_security_review_no_legal_publication_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "codex_performed_security_review=true",
        "privacy_notice_published=true",
        "dpa_sent_to_customer=true",
        "customer_data_processed=true",
        "vulnerability_management_operational=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_followup_state_reconciliation/privacy_security_legal_followup_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_privacy_security_legal_followup_state_reconciliation.py",
        "/scripts/saee_privacy_security_legal_followup_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("privacy_security_legal_followup_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing privacy_security_legal_followup_state_reconciliation_v0_1")
    for key in [
        "status",
        "target_blocker_ids",
        "resolved_current_path",
        "formal_security_review_ready_for_review",
        "privacy_legal_review_ready_for_review",
        "data_processing_agreement_ready_for_review",
        "vulnerability_management_ready_for_review",
        "combined_privacy_security_legal_profile_ready",
        "ready_for_review_count",
        "codex_performed_security_review",
        "privacy_notice_published",
        "dpa_sent_to_customer",
        "customer_data_processed",
        "vulnerability_management_operational",
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
        "Privacy/Security/Legal Follow-up State Reconciliation v0.1",
        "formal_security_review_ready_for_review=true",
        "privacy_legal_review_ready_for_review=true",
        "data_processing_agreement_ready_for_review=true",
        "vulnerability_management_ready_for_review=true",
        "combined_privacy_security_legal_profile_ready=true",
        "ready_for_review_count=4",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_PRIVACY_SECURITY_LEGAL_FOLLOWUP_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
