#!/usr/bin/env python3
"""Smoke check for SAEE Production Privacy/Security/Legal Evidence Readiness v0.1."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_privacy_security_legal_evidence import (
    evaluate_production_privacy_security_legal_evidence,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_SMOKE: FAIL: "
            + message
        )


def write_privacy_security_legal_evidence(path: Path, *, unsafe: bool = False) -> None:
    data = {
        "privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence",
        "formal_security_review_report": True,
        "public_shell_threat_model_reviewed": True,
        "auth_and_tenant_boundary_reviewed": True,
        "storage_backup_and_restore_reviewed": True,
        "dependency_review_completed": True,
        "private_core_non_exposure_review_completed": True,
        "review_findings_triaged": True,
        "privacy_notice_approved": True,
        "terms_of_service_approved": True,
        "data_inventory_reviewed": True,
        "retention_policy_approved": True,
        "subprocessor_inventory_reviewed": True,
        "customer_data_processing_approved": True,
        "legal_reviewer_recorded": True,
        "dpa_terms_approved": True,
        "controller_processor_roles_defined": True,
        "subprocessor_terms_approved": True,
        "breach_notice_terms_approved": True,
        "deletion_or_return_terms_approved": True,
        "customer_dpa_template_available": True,
        "security_contact_configured": True,
        "coordinated_disclosure_policy_approved": True,
        "triage_owner_named": True,
        "severity_model_approved": True,
        "remediation_targets_approved": True,
        "vulnerability_case_dry_run_recorded": True,
        "advisory_publication_policy_approved": True,
        "production_ready": unsafe,
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
        "customer_contacted": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
        "production_security_enabled": False,
        "vulnerability_management_operational": False,
    }
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def blocker_ids(report: dict[str, object]) -> set[str]:
    return {str(item["blocker_id"]) for item in report["unsatisfied_blockers"]}


def main() -> None:
    local = evaluate_production_privacy_security_legal_evidence(load_settings({}))
    require(
        local["production_privacy_security_legal_evidence_type"]
        == "production_privacy_security_legal_evidence_readiness",
        "wrong evidence type",
    )
    require(
        local["production_privacy_security_legal_evidence_readiness_v0_1"] is True,
        "readiness flag",
    )
    require(local["status"] == "hold", "default evidence status must hold")
    require(
        local["privacy_security_legal_evidence_path_configured"] is False,
        "default path false",
    )
    require(
        local["formal_security_review_completed"] is False,
        "default formal security false",
    )
    require(
        local["privacy_legal_review_completed"] is False,
        "default privacy legal false",
    )
    require(
        local["data_processing_agreement_available"] is False,
        "default DPA false",
    )
    require(
        local["vulnerability_management_available"] is False,
        "default vulnerability management false",
    )
    require(
        local["production_privacy_security_legal_ready"] is False,
        "default privacy/security/legal ready false",
    )
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
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
        require(local[flag] is False, f"default {flag} false")

    with tempfile.TemporaryDirectory() as tmpdir:
        evidence_path = Path(tmpdir) / "PRIVACY_SECURITY_LEGAL_EVIDENCE.json"
        write_privacy_security_legal_evidence(evidence_path)
        settings = load_settings(
            {
                "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
                    evidence_path
                )
            }
        )
        configured = evaluate_production_privacy_security_legal_evidence(settings)
        go_no_go = evaluate_commercial_go_no_go(settings)

        unsafe_path = Path(tmpdir) / "UNSAFE_PRIVACY_SECURITY_LEGAL_EVIDENCE.json"
        write_privacy_security_legal_evidence(unsafe_path, unsafe=True)
        unsafe = evaluate_production_privacy_security_legal_evidence(
            load_settings(
                {
                    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
                        unsafe_path
                    )
                }
            )
        )

    require(configured["status"] == "pass", "complete evidence should pass")
    require(
        configured["formal_security_review_completed"] is True,
        "formal security evidence true",
    )
    require(
        configured["privacy_legal_review_completed"] is True,
        "privacy legal evidence true",
    )
    require(
        configured["data_processing_agreement_available"] is True,
        "DPA evidence true",
    )
    require(
        configured["vulnerability_management_available"] is True,
        "vulnerability management evidence true",
    )
    require(
        configured["production_privacy_security_legal_ready"] is True,
        "evidence-local ready true",
    )
    for flag in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
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
        require(configured[flag] is False, f"configured {flag} false")

    blocked = blocker_ids(go_no_go)
    for blocker in [
        "formal_security_review",
        "privacy_legal_review",
        "data_processing_agreement",
        "vulnerability_management",
    ]:
        require(blocker not in blocked, f"{blocker} should be satisfied by evidence")
    require(
        go_no_go["production_privacy_security_legal_evidence_status"] == "pass",
        "go/no-go should expose privacy/security/legal evidence pass",
    )
    require(
        go_no_go["privacy_security_legal_evidence_formal_security_review_completed"]
        is True,
        "go/no-go should expose formal security evidence",
    )
    require(
        go_no_go["privacy_security_legal_evidence_privacy_legal_review_completed"]
        is True,
        "go/no-go should expose privacy legal evidence",
    )
    require(
        go_no_go[
            "privacy_security_legal_evidence_data_processing_agreement_available"
        ]
        is True,
        "go/no-go should expose DPA evidence",
    )
    require(
        go_no_go[
            "privacy_security_legal_evidence_vulnerability_management_available"
        ]
        is True,
        "go/no-go should expose vulnerability management evidence",
    )
    require(go_no_go["commercial_status"] == "hold", "evidence alone must not launch")
    require(
        go_no_go["production_launch_status"] == "hold",
        "production launch must still hold",
    )
    require(go_no_go["production_ready"] is False, "go/no-go production false")
    require(go_no_go["customer_validated"] is False, "go/no-go customer false")
    require(go_no_go["product_launched"] is False, "go/no-go launch false")
    require(go_no_go["private_core_exposed"] is False, "go/no-go private core false")

    require(unsafe["status"] == "stop", "unsafe evidence must stop")
    require(
        "production_ready" in unsafe["boundary_violations"],
        "unsafe evidence must detect boundary",
    )
    require(unsafe["production_ready"] is False, "unsafe output production false")

    doc = (
        ROOT
        / "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_READINESS_V0_1.md"
    ).read_text(encoding="utf-8")
    gate = (
        ROOT
        / "docs/strategy/SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_READINESS_RECOMMENDATION_GATE.md"
    ).read_text(encoding="utf-8")
    combined = "\n".join([doc, gate])
    for token in [
        "production_privacy_security_legal_evidence_readiness_v0_1: true",
        "default_status: hold",
        "privacy_security_legal_evidence_path_configured_default: false",
        "formal_security_review_completed_default: false",
        "privacy_legal_review_completed_default: false",
        "data_processing_agreement_available_default: false",
        "vulnerability_management_available_default: false",
        "production_privacy_security_legal_ready_default: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "external_model_api_called: false",
        "customer_contacted: false",
        "security_vendor_contacted: false",
        "legal_counsel_contacted: false",
        "customer_data_processed: false",
        "customer_data_processing_started: false",
        "dpa_sent_to_customer: false",
        "terms_published: false",
        "privacy_notice_published: false",
        "production_security_enabled: false",
        "vulnerability_management_operational: false",
        "customer_data_processing_ready: false",
        "production_security_ready: false",
        "production_legal_ready: false",
        "legal_approval_completed: false",
        "answer: conditional",
        "recommend_for_privacy_security_legal_evidence_review: true",
        "recommend_for_production_privacy_security_legal_implementation: false",
        "recommend_for_production_launch: false",
    ]:
        require(token in combined, f"missing doc/gate token {token}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_READINESS_V0_1.md",
        "/docs/strategy/SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_READINESS_RECOMMENDATION_GATE.md",
        "/saee_backend/services/production_privacy_security_legal_evidence.py",
        "/scripts/saee_production_privacy_security_legal_evidence_readiness.py",
        "/scripts/saee_production_privacy_security_legal_evidence_readiness_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_privacy_security_legal_evidence_readiness_v0_1", {})
    expected = {
        "status": "production_privacy_security_legal_evidence_readiness_hold",
        "production_privacy_security_legal_evidence_readiness_v0_1": True,
        "privacy_security_legal_evidence_path_configured_default": False,
        "formal_security_review_completed_default": False,
        "privacy_legal_review_completed_default": False,
        "data_processing_agreement_available_default": False,
        "vulnerability_management_available_default": False,
        "production_privacy_security_legal_ready_default": False,
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
        "customer_contacted": False,
        "security_vendor_contacted": False,
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "customer_data_processing_started": False,
        "dpa_sent_to_customer": False,
        "terms_published": False,
        "privacy_notice_published": False,
        "production_security_enabled": False,
        "vulnerability_management_operational": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} drift")

    print(
        "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_SMOKE: PASS "
        "default_hold=true configured_evidence_pass=true "
        "privacy_security_legal_blockers_satisfied_by_evidence=true "
        "production_launch_status=hold production_ready=false "
        "private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
