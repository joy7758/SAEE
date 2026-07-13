#!/usr/bin/env python3
"""Smoke check for the local privacy/security/legal evidence runner."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.production_privacy_security_legal_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_privacy_security_legal_evidence,
)
from scripts.saee_privacy_security_legal_evidence_runner import (
    OUTPUT_PATH,
    main as run_runner,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_SMOKE: FAIL: " + message
        )


def main() -> None:
    run_runner()
    require(OUTPUT_PATH.exists(), "evidence file must exist")
    evidence = json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))

    require(
        evidence.get("privacy_security_legal_evidence_type")
        == "production_privacy_security_legal_evidence",
        "wrong privacy/security/legal evidence type",
    )
    require(
        evidence.get("evidence_scope")
        == "local_public_shell_privacy_security_legal_review_packet",
        "wrong evidence scope",
    )
    for flag in [
        "public_shell_threat_model_reviewed",
        "auth_and_tenant_boundary_reviewed",
        "storage_backup_and_restore_reviewed",
        "private_core_non_exposure_review_completed",
        "data_inventory_reviewed",
        "subprocessor_inventory_reviewed",
        "controller_processor_roles_defined",
        "vulnerability_case_dry_run_recorded",
    ]:
        require(evidence.get(flag) is True, f"{flag} must be recorded")
    for flag in [
        "formal_security_review_report",
        "dependency_review_completed",
        "review_findings_triaged",
        "privacy_notice_approved",
        "terms_of_service_approved",
        "retention_policy_approved",
        "customer_data_processing_approved",
        "legal_reviewer_recorded",
        "dpa_terms_approved",
        "customer_dpa_template_available",
        "security_contact_configured",
        "coordinated_disclosure_policy_approved",
        "triage_owner_named",
        "severity_model_approved",
        "remediation_targets_approved",
        "advisory_publication_policy_approved",
    ]:
        require(evidence.get(flag) is False, f"{flag} must remain false")

    forbidden_true = [key for key in FORBIDDEN_TRUE_KEYS if evidence.get(key) is True]
    require(not forbidden_true, "forbidden true claims: " + ", ".join(forbidden_true))

    readiness = evaluate_production_privacy_security_legal_evidence(
        load_settings(
            {"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(OUTPUT_PATH)}
        )
    )
    require(readiness["status"] == "hold", "partial local evidence must remain hold")
    require(
        readiness["formal_security_review_completed"] is False,
        "formal security review must remain incomplete",
    )
    require(
        readiness["privacy_legal_review_completed"] is False,
        "privacy legal review must remain incomplete",
    )
    require(
        readiness["data_processing_agreement_available"] is False,
        "DPA must remain incomplete",
    )
    require(
        readiness["vulnerability_management_available"] is False,
        "vulnerability management must remain incomplete",
    )
    require(
        readiness["production_privacy_security_legal_ready"] is False,
        "production privacy/security/legal readiness must remain incomplete",
    )
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
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
        require(readiness[flag] is False, f"{flag} must remain false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = doc + "\n" + gate
    for token in [
        "privacy_security_legal_evidence_runner_v0_1: true",
        "evidence_scope: local_public_shell_privacy_security_legal_review_packet",
        "formal_security_review_completed: false",
        "privacy_legal_review_completed: false",
        "data_processing_agreement_available: false",
        "vulnerability_management_available: false",
        "production_privacy_security_legal_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "answer: conditional",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_V0_1.md",
        "/docs/strategy/SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/README.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json",
        "/scripts/saee_privacy_security_legal_evidence_runner.py",
        "/scripts/saee_privacy_security_legal_evidence_runner_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("privacy_security_legal_evidence_runner_v0_1", {})
    expected = {
        "status": "local_public_shell_evidence_generated_hold",
        "privacy_security_legal_evidence_runner_v0_1": True,
        "evidence_scope": "local_public_shell_privacy_security_legal_review_packet",
        "public_shell_threat_model_reviewed": True,
        "auth_and_tenant_boundary_reviewed": True,
        "storage_backup_and_restore_reviewed": True,
        "private_core_non_exposure_review_completed": True,
        "data_inventory_reviewed": True,
        "subprocessor_inventory_reviewed": True,
        "controller_processor_roles_defined": True,
        "vulnerability_case_dry_run_recorded": True,
        "formal_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_available": False,
        "vulnerability_management_available": False,
        "production_privacy_security_legal_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "customer_contacted": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "blockers_closed_by_default": 0,
    }
    for flag, expected_value in expected.items():
        require(entry.get(flag) == expected_value, f"agent-index {flag} must be {expected_value}")

    print(
        "SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_SMOKE: PASS "
        "local_public_shell_evidence=true "
        "production_privacy_security_legal_ready=false "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
