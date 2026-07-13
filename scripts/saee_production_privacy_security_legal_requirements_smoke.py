#!/usr/bin/env python3
"""Smoke check for SAEE Production Privacy / Security / Legal Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.json"
)
MD_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_SMOKE: FAIL: {message}")


def main() -> None:
    require(JSON_PATH.exists(), "requirements JSON missing")
    require(MD_PATH.exists(), "requirements Markdown missing")
    require(GATE_PATH.exists(), "recommendation gate missing")

    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    require(data["production_privacy_security_legal_requirements_v0_1"] is True, "requirements flag true")
    require(data["requirements_status"] == "requirements_defined_implementation_hold", "status hold")

    false_flags = [
        "production_privacy_security_legal_implemented",
        "formal_security_review_completed",
        "privacy_legal_review_completed",
        "data_processing_agreement_available",
        "vulnerability_management_available",
        "coordinated_disclosure_available",
        "security_contact_configured",
        "penetration_test_completed",
        "production_security_ready",
        "production_legal_ready",
        "customer_data_processing_ready",
        "production_privacy_security_legal_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "task_candidates_executed",
        "development_permission_granted",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "customer_contacted",
        "security_vendor_contacted",
        "legal_counsel_contacted",
    ]
    for flag in false_flags:
        require(data[flag] is False, f"{flag} false")

    blockers = set(data["privacy_security_legal_blockers_covered_as_requirements"])
    require(
        blockers
        == {
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        },
        "privacy/security/legal blockers mismatch",
    )

    required_security_scope = {
        "public_api_shell",
        "authentication_and_authorization_boundaries",
        "tenant_request_boundary",
        "storage_and_backup_paths",
        "request_audit_and_redaction",
        "dependency_and_supply_chain_review",
        "deployment_configuration_review",
        "private_core_non_exposure_review",
    }
    require(
        required_security_scope <= set(data["required_security_review_scope"]),
        "missing required security review scope",
    )

    required_privacy_scope = {
        "data_inventory",
        "personal_data_policy",
        "privacy_notice",
        "data_retention_policy",
        "subprocessor_inventory",
        "cross_border_transfer_review",
        "customer_data_processing_terms",
        "data_subject_request_process",
    }
    require(
        required_privacy_scope <= set(data["required_privacy_legal_review_scope"]),
        "missing required privacy/legal scope",
    )

    required_dpa_terms = {
        "controller_processor_roles",
        "processing_purpose",
        "data_categories",
        "security_measures",
        "subprocessor_terms",
        "audit_rights",
        "breach_notice_window",
        "deletion_or_return_terms",
        "jurisdiction_and_transfer_terms",
    }
    require(required_dpa_terms <= set(data["required_dpa_terms"]), "missing required DPA terms")

    required_vuln_controls = {
        "security_contact_route",
        "coordinated_disclosure_policy",
        "triage_owner",
        "severity_model",
        "remediation_targets",
        "fix_verification_process",
        "advisory_publication_policy",
        "vulnerability_case_audit_trail",
    }
    require(
        required_vuln_controls <= set(data["required_vulnerability_management_controls"]),
        "missing required vulnerability controls",
    )

    evidence_ids = {item["blocker_id"] for item in data["evidence_required_before_closing_blockers"]}
    require(evidence_ids == blockers, "evidence ids must match blockers")

    combined = "\n".join(
        [
            MD_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "production_privacy_security_legal_requirements_v0_1: true",
        "requirements_status: requirements_defined_implementation_hold",
        "production_privacy_security_legal_implemented: false",
        "formal_security_review_completed: false",
        "privacy_legal_review_completed: false",
        "data_processing_agreement_available: false",
        "vulnerability_management_available: false",
        "production_security_ready: false",
        "production_legal_ready: false",
        "customer_data_processing_ready: false",
        "production_privacy_security_legal_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "external_calls_made: false",
        "customer_contacted: false",
        "answer: conditional",
        "recommend_for_security_or_legal_completion: false",
        "recommend_for_production_launch: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    require(not missing_tokens, "missing doc/gate tokens: " + ", ".join(missing_tokens))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.md",
        "/phase_b_product/commercial_readiness/PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_V0_1.json",
        "/docs/strategy/SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_RECOMMENDATION_GATE.md",
        "/scripts/saee_production_privacy_security_legal_requirements.py",
        "/scripts/saee_production_privacy_security_legal_requirements_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("production_privacy_security_legal_requirements_v0_1", {})
    expected = {
        "status": "requirements_defined_implementation_hold",
        "production_privacy_security_legal_requirements_v0_1": True,
        "production_privacy_security_legal_implemented": False,
        "formal_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_available": False,
        "vulnerability_management_available": False,
        "production_security_ready": False,
        "production_legal_ready": False,
        "customer_data_processing_ready": False,
        "production_privacy_security_legal_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "development_permission_granted": False,
    }
    for key, expected_value in expected.items():
        require(entry.get(key) == expected_value, f"agent-index {key} must be {expected_value}")

    print(
        "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_REQUIREMENTS_SMOKE: PASS "
        "requirements_defined=true formal_security_review_completed=false "
        "privacy_legal_review_completed=false data_processing_agreement_available=false "
        "vulnerability_management_available=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
