#!/usr/bin/env python3
"""Smoke check for the SAEE privacy/security/legal evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_privacy_security_legal_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_privacy_security_legal_evidence_path.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_SMOKE: FAIL: " + message
        )


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    run = subprocess.run(
        [sys.executable, str(RUNNER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    result = json.loads(run.stdout)
    require(
        result["privacy_security_legal_evidence_path_v0_1"] is True,
        "path flag true",
    )
    require(
        result["path_type"] == "local_fixture_only_privacy_security_legal_evidence_path",
        "path type changed",
    )
    require(result["path_status"] == "pass_fixture_only", "fixture path must pass")
    require(result["fixture_only"] is True, "fixture only true")
    require(
        result["real_formal_security_review_completed"] is False,
        "real formal security review false",
    )
    require(
        result["real_privacy_legal_review_completed"] is False,
        "real privacy/legal review false",
    )
    require(result["real_dpa_approved"] is False, "real DPA approval false")
    require(
        result["real_vulnerability_management_operational"] is False,
        "real vulnerability management operational false",
    )
    require(
        result["real_customer_data_processing_approved"] is False,
        "real customer data processing approval false",
    )
    require(
        result["privacy_security_legal_readiness_status_after_fixture"] == "pass",
        "privacy/security/legal readiness pass",
    )
    require(
        result["formal_security_review_completed_after_fixture"] is True,
        "formal security fixture true",
    )
    require(
        result["privacy_legal_review_completed_after_fixture"] is True,
        "privacy/legal fixture true",
    )
    require(
        result["data_processing_agreement_available_after_fixture"] is True,
        "DPA fixture true",
    )
    require(
        result["vulnerability_management_available_after_fixture"] is True,
        "vulnerability management fixture true",
    )
    require(
        result["production_privacy_security_legal_ready_after_fixture"] is True,
        "privacy/security/legal ready in fixture",
    )
    require(
        result["privacy_security_legal_blocker_path_proven"] is True,
        "privacy/security/legal path proven",
    )
    require(
        result["privacy_security_legal_target_blockers_satisfied_count_after_fixture"]
        == 4,
        "four privacy/security/legal target blockers satisfied by fixture",
    )
    require(result["commercial_status_after_fixture"] == "hold", "commercial hold")
    require(result["production_launch_status_after_fixture"] == "hold", "launch hold")
    require(
        result["production_blocker_count_after_fixture"] == 20,
        "go/no-go leaves 20 blockers",
    )
    require(result["blockers_closed_by_path"] == 0, "path closes no blockers")
    for key in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "customer_contacted",
        "security_vendor_contacted",
        "legal_counsel_contacted",
        "customer_data_processed",
        "customer_data_processing_started",
        "dpa_sent_to_customer",
        "terms_published",
        "privacy_notice_published",
        "production_security_enabled",
        "vulnerability_management_operational",
        "production_security_ready",
        "production_legal_ready",
        "customer_data_processing_ready",
        "legal_approval_completed",
    ]:
        require(result[key] is False, f"{key} must be false")
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    persisted = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    require(persisted == result, "persisted output differs")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "privacy_security_legal_evidence_path_v0_1: true",
        "path_type: local_fixture_only_privacy_security_legal_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_formal_security_review_completed: false",
        "real_privacy_legal_review_completed: false",
        "real_dpa_approved: false",
        "real_vulnerability_management_operational: false",
        "real_customer_data_processing_approved: false",
        "privacy_security_legal_readiness_status_after_fixture: pass",
        "formal_security_review_completed_after_fixture: true",
        "privacy_legal_review_completed_after_fixture: true",
        "data_processing_agreement_available_after_fixture: true",
        "vulnerability_management_available_after_fixture: true",
        "production_privacy_security_legal_ready_after_fixture: true",
        "privacy_security_legal_blocker_path_proven: true",
        "privacy_security_legal_target_blockers_satisfied_count_after_fixture: 4",
        "production_blocker_count_after_fixture: 20",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_privacy_security_legal_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_legal_counsel_contact: false",
        "recommend_for_security_vendor_contact: false",
        "recommend_for_customer_data_processing: false",
        "recommend_for_vulnerability_operations_enablement: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)
    for token in [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "real_formal_security_review_completed: true",
        "\"real_formal_security_review_completed\": true",
        "real_privacy_legal_review_completed: true",
        "\"real_privacy_legal_review_completed\": true",
        "real_dpa_approved: true",
        "\"real_dpa_approved\": true",
        "real_vulnerability_management_operational: true",
        "\"real_vulnerability_management_operational\": true",
        "real_customer_data_processing_approved: true",
        "\"real_customer_data_processing_approved\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "security_vendor_contacted: true",
        "\"security_vendor_contacted\": true",
        "legal_counsel_contacted: true",
        "\"legal_counsel_contacted\": true",
        "customer_data_processed: true",
        "\"customer_data_processed\": true",
        "dpa_sent_to_customer: true",
        "\"dpa_sent_to_customer\": true",
        "terms_published: true",
        "\"terms_published\": true",
        "privacy_notice_published: true",
        "\"privacy_notice_published\": true",
        "production_security_enabled: true",
        "\"production_security_enabled\": true",
        "vulnerability_management_operational: true",
        "\"vulnerability_management_operational\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_legal_counsel_contact: true",
        "recommend_for_security_vendor_contact: true",
        "recommend_for_customer_data_processing: true",
        "recommend_for_vulnerability_operations_enablement: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence_path_report.md",
        "/docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_privacy_security_legal_evidence_path.py",
        "/scripts/saee_privacy_security_legal_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("privacy_security_legal_evidence_path_v0_1", {})
    expected = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_privacy_security_legal_evidence_path",
        "fixture_only": True,
        "real_formal_security_review_completed": False,
        "real_privacy_legal_review_completed": False,
        "real_dpa_approved": False,
        "real_vulnerability_management_operational": False,
        "real_customer_data_processing_approved": False,
        "privacy_security_legal_blocker_path_proven": True,
        "formal_security_review_completed_after_fixture": True,
        "privacy_legal_review_completed_after_fixture": True,
        "data_processing_agreement_available_after_fixture": True,
        "vulnerability_management_available_after_fixture": True,
        "production_privacy_security_legal_ready_after_fixture": True,
        "privacy_security_legal_target_blockers_satisfied_count_after_fixture": 4,
        "production_blocker_count_after_fixture": 20,
        "blockers_closed_by_path": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "customer_contacted": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
        "production_security_enabled": False,
        "vulnerability_management_operational": False,
    }
    for flag, expected_value in expected.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index privacy_security_legal_evidence_path_v0_1 {flag} must be {expected_value}",
        )

    print("SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH_SMOKE: PASS")


if __name__ == "__main__":
    main()
