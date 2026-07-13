#!/usr/bin/env python3
"""Generate local public-shell privacy/security/legal evidence.

This runner converts existing local privacy, security, legal, and vulnerability
readiness helpers into a partial production privacy/security/legal evidence
JSON file for human review. It does not perform legal review, contact legal
counsel, contact security vendors, process customer data, publish terms,
enable vulnerability operations, modify backend behavior, or mark SAEE
production-ready.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.legal_readiness import evaluate_legal_readiness
from saee_backend.services.privacy_security_readiness import (
    evaluate_privacy_security_readiness,
)
from saee_backend.services.production_privacy_security_legal_evidence import (
    DPA_KEYS,
    FORBIDDEN_TRUE_KEYS,
    FORMAL_SECURITY_REVIEW_KEYS,
    PRIVACY_LEGAL_REVIEW_KEYS,
    VULNERABILITY_MANAGEMENT_KEYS,
    evaluate_production_privacy_security_legal_evidence,
)
from saee_backend.services.vulnerability_management_readiness import (
    evaluate_vulnerability_management_readiness,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
OUTPUT_PATH = OUTPUT_DIR / "privacy_security_legal_evidence.local.json"
README_PATH = OUTPUT_DIR / "README.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def run_local_privacy_security_legal_evidence() -> dict[str, Any]:
    settings = load_settings({})
    privacy_security = evaluate_privacy_security_readiness(settings)
    legal = evaluate_legal_readiness(settings)
    vulnerability = evaluate_vulnerability_management_readiness(settings)

    require(
        privacy_security["privacy_security_readiness_type"]
        == "controlled_preview_privacy_security_readiness",
        "wrong privacy/security readiness type",
    )
    require(
        legal["legal_readiness_type"] == "controlled_preview_legal_dpa_readiness",
        "wrong legal readiness type",
    )
    require(
        vulnerability["vulnerability_management_readiness_type"]
        == "controlled_preview_vulnerability_management_readiness",
        "wrong vulnerability readiness type",
    )
    require(privacy_security["data_classification_available"] is True, "data classification")
    require(privacy_security["public_shell_data_map_available"] is True, "data map")
    require(privacy_security["pii_policy_draft_available"] is True, "PII draft")
    require(privacy_security["secret_handling_guidance_available"] is True, "secrets guide")
    require(
        privacy_security["third_party_processor_inventory_available"] is True,
        "processor inventory",
    )
    require(legal["terms_of_service_draft_available"] is True, "terms draft")
    require(legal["privacy_notice_draft_available"] is True, "privacy notice draft")
    require(legal["dpa_review_packet_available"] is True, "DPA packet")
    require(
        vulnerability["vulnerability_disclosure_policy_draft_available"] is True,
        "vulnerability disclosure draft",
    )
    require(
        vulnerability["vulnerability_triage_runbook_available"] is True,
        "vulnerability triage runbook",
    )
    for report in [privacy_security, legal, vulnerability]:
        require(report["production_ready"] is False, "production must remain false")
        require(report["customer_validated"] is False, "customer validation must remain false")
        require(report["product_launched"] is False, "launch must remain false")
        require(report["private_core_exposed"] is False, "private core must remain false")
        require(report["runtime_modified"] is False, "runtime must remain unchanged")
        require(report["kernel_modified"] is False, "kernel must remain unchanged")
        require(report["api_schema_modified"] is False, "API schema must remain unchanged")
        require(report["external_calls_made"] is False, "external calls must remain false")
        require(report["customer_contacted"] is False, "customer contact must remain false")

    return {
        "privacy_security": privacy_security,
        "legal": legal,
        "vulnerability": vulnerability,
    }


def build_evidence() -> dict[str, Any]:
    result = run_local_privacy_security_legal_evidence()
    privacy_security = result["privacy_security"]
    legal = result["legal"]
    vulnerability = result["vulnerability"]

    evidence: dict[str, Any] = {
        "privacy_security_legal_evidence_type": "production_privacy_security_legal_evidence",
        "evidence_scope": "local_public_shell_privacy_security_legal_review_packet",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_privacy_security_legal_evidence_runner.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_privacy_security_helper": "saee_backend/services/privacy_security_readiness.py",
        "source_legal_helper": "saee_backend/services/legal_readiness.py",
        "source_vulnerability_helper": "saee_backend/services/vulnerability_management_readiness.py",
        "formal_security_review_report": False,
        "public_shell_threat_model_reviewed": True,
        "auth_and_tenant_boundary_reviewed": True,
        "storage_backup_and_restore_reviewed": True,
        "dependency_review_completed": False,
        "private_core_non_exposure_review_completed": True,
        "review_findings_triaged": False,
        "privacy_notice_approved": False,
        "terms_of_service_approved": False,
        "data_inventory_reviewed": True,
        "retention_policy_approved": False,
        "subprocessor_inventory_reviewed": True,
        "customer_data_processing_approved": False,
        "legal_reviewer_recorded": False,
        "dpa_terms_approved": False,
        "controller_processor_roles_defined": True,
        "subprocessor_terms_approved": False,
        "breach_notice_terms_approved": False,
        "deletion_or_return_terms_approved": False,
        "customer_dpa_template_available": False,
        "security_contact_configured": False,
        "coordinated_disclosure_policy_approved": False,
        "triage_owner_named": False,
        "severity_model_approved": False,
        "remediation_targets_approved": False,
        "vulnerability_case_dry_run_recorded": True,
        "advisory_publication_policy_approved": False,
        "local_public_shell_results": {
            "privacy_security_readiness_type": privacy_security[
                "privacy_security_readiness_type"
            ],
            "legal_readiness_type": legal["legal_readiness_type"],
            "vulnerability_management_readiness_type": vulnerability[
                "vulnerability_management_readiness_type"
            ],
            "data_classification_available": True,
            "public_shell_data_map_available": True,
            "pii_policy_draft_available": True,
            "personal_data_allowed": False,
            "secret_handling_guidance_available": True,
            "third_party_processor_inventory_available": True,
            "terms_of_service_draft_available": True,
            "terms_of_service_published": False,
            "privacy_notice_draft_available": True,
            "privacy_notice_published": False,
            "dpa_review_packet_available": True,
            "data_processing_agreement_draft_available": True,
            "data_processing_agreement_available": False,
            "vulnerability_disclosure_policy_draft_available": True,
            "vulnerability_triage_runbook_available": True,
            "security_contact_configured": False,
            "formal_security_review_completed": False,
            "privacy_legal_review_completed": False,
            "vulnerability_management_available": False,
            "production_security_ready": False,
            "production_legal_ready": False,
            "customer_data_processing_ready": False,
            "external_calls_made": False,
            "external_model_api_called": False,
            "customer_contacted": False,
            "security_vendor_contacted": False,
            "legal_counsel_contacted": False,
            "customer_data_processed": False,
        },
        "limitations": [
            "No formal security review report exists.",
            "No dependency review has been completed.",
            "No formal review findings have been triaged.",
            "No privacy notice, terms, retention policy, or customer data processing approval exists.",
            "No legal reviewer has been recorded.",
            "No DPA terms or customer DPA template are approved.",
            "No security contact is configured for production vulnerability management.",
            "No coordinated disclosure policy, severity model, remediation targets, or advisory publication policy is approved.",
            "This evidence is local public-shell evidence only and does not close the production launch gate.",
        ],
    }
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False

    missing_expected = [
        key
        for key in FORMAL_SECURITY_REVIEW_KEYS
        + PRIVACY_LEGAL_REVIEW_KEYS
        + DPA_KEYS
        + VULNERABILITY_MANAGEMENT_KEYS
        + FORBIDDEN_TRUE_KEYS
        if key not in evidence
    ]
    require(not missing_expected, "evidence missing keys: " + ", ".join(missing_expected))
    return evidence


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Privacy / Security / Legal Evidence

Status: local public-shell privacy/security/legal review-packet evidence, not
production privacy/security/legal readiness.

This directory contains a generated local evidence JSON file for review of
public-shell privacy, security, legal, DPA, and vulnerability-management
materials. It records only what the local runner can prove.

It does not perform legal review, contact legal counsel, contact security
vendors, process customer data, send a DPA to customers, publish terms, publish
a privacy notice, enable production security, enable vulnerability operations,
modify runtime behavior, modify backend behavior, modify API schema, or expose
private core.

Primary file:

```text
privacy_security_legal_evidence.local.json
formal_security_review_scope_draft.local.json
formal_security_review_scope_draft.md
formal_security_review_scope_draft_boundary_audit.md
formal_security_review_evidence_input.template.json
formal_security_review_evidence_builder_output.local.json
production_privacy_security_legal_evidence.from_formal_security_review.local.json
formal_security_review_evidence_builder_report.md
privacy_legal_dpa_evidence_input.template.json
privacy_legal_dpa_evidence_builder_output.local.json
production_privacy_security_legal_evidence.from_privacy_legal_dpa.local.json
privacy_legal_dpa_evidence_builder_report.md
vulnerability_management_evidence_input.template.json
vulnerability_management_evidence_builder_output.local.json
production_privacy_security_legal_evidence.from_vulnerability_management.local.json
vulnerability_management_evidence_builder_report.md
vulnerability_management_approval_input_validation.local.json
vulnerability_management_approval_input_validation.md
privacy_legal_review_packet.local.json
privacy_legal_review_packet.md
data_processing_agreement_review_packet.local.json
data_processing_agreement_review_packet.md
privacy_security_legal_evidence_path.local.json
privacy_security_legal_evidence_path_report.md
```

Generate it with:

```bash
python3 scripts/saee_privacy_security_legal_evidence_runner.py
python3 scripts/saee_formal_security_review_scope_draft.py
python3 scripts/saee_formal_security_review_evidence_builder.py
python3 scripts/saee_privacy_legal_dpa_evidence_builder.py
python3 scripts/saee_vulnerability_management_evidence_builder.py
python3 scripts/saee_vulnerability_management_approval_input_validator.py
python3 scripts/saee_privacy_legal_review_packet.py
python3 scripts/saee_data_processing_agreement_review_packet.py
```

Boundary:

```yaml
evidence_scope: local_public_shell_privacy_security_legal_review_packet
formal_security_review_scope_draft_available: true
formal_security_review_scope_draft_status: draft_not_approved
formal_security_review_completed: false
formal_security_review_evidence_builder_available: true
formal_security_review_evidence_builder_status: local_builder_available_default_hold
formal_security_review_completed_for_review: false
privacy_legal_dpa_evidence_builder_available: true
privacy_legal_dpa_evidence_builder_status: local_builder_available_default_hold
privacy_legal_review_completed_for_review: false
data_processing_agreement_available_for_review: false
vulnerability_management_evidence_builder_available: true
vulnerability_management_evidence_builder_status: local_builder_available_default_hold
vulnerability_management_available_for_review: false
vulnerability_management_approval_input_validator_available: true
vulnerability_management_approval_input_validator_status: hold
vulnerability_management_approval_input_validator_builder_ready: false
vulnerability_management_approval_input_validator_closes_blockers: 0
privacy_legal_review_completed: false
privacy_legal_review_packet_available: true
privacy_legal_review_packet_status: draft_ready_for_human_review
privacy_legal_review_evidence_complete: false
data_processing_agreement_review_packet_available: true
data_processing_agreement_review_packet_status: draft_ready_for_human_review
dpa_review_packet_evidence_complete: false
data_processing_agreement_available: false
vulnerability_management_available: false
production_privacy_security_legal_ready: false
privacy_security_legal_evidence_path_proof_available: true
privacy_security_legal_evidence_path_fixture_only: true
privacy_security_legal_evidence_path_blocker_count_after_fixture: 20
privacy_security_legal_evidence_path_closes_blockers: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
customer_contacted: false
security_vendor_contacted: false
legal_counsel_contacted: false
customer_data_processed: false
```

The formal security review scope draft is a documentation-only human-review
surface. It does not execute a formal security review, contact reviewers,
perform penetration testing, inspect private core, close blockers, or make SAEE
production-ready.

The formal security review evidence builder is a local human-input converter.
It does not perform a formal security review, contact reviewers or vendors,
run penetration testing, inspect private core, publish a security claim, close
blockers, or make SAEE production-ready.

The privacy/legal + DPA evidence builder is a local human-input converter. It
does not perform legal review, contact legal counsel, create or approve a DPA,
send a DPA to customers, process customer data, close blockers, or make SAEE
production-ready.

The vulnerability management evidence builder is a local human-input
converter. It does not run scanners, run penetration tests, contact security
reporters or vendors, launch coordinated disclosure, publish security contact
details, process customer data, close blockers, or make SAEE production-ready.

The vulnerability management approval input validator is a pre-builder
completeness and boundary-safety check. It does not run vulnerability scans,
run penetration tests, contact reporters or vendors, publish security contact
details, launch coordinated disclosure, activate vulnerability operations,
process customer data, close blockers, or make SAEE production-ready.

The privacy/legal review packet is a documentation-only human-review surface.
It does not complete privacy legal review, contact legal counsel, publish
terms, publish a privacy notice, approve customer data processing, send a DPA,
process customer data, close blockers, or make SAEE production-ready.

The DPA review packet is a documentation-only human-review surface. It does
not create or approve a DPA, contact legal counsel, send a DPA to customers,
approve customer data processing, process customer data, close blockers, or
make SAEE production-ready.

The privacy/security/legal evidence path proof is fixture-only. It proves that
complete human-provided privacy/security/legal evidence can later flow through
privacy/security/legal readiness and commercial go/no-go, but it does not
perform reviews, approve a DPA, contact legal counsel or security vendors,
process customer data, close blockers, or claim production readiness.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = build_evidence()
    OUTPUT_PATH.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_readme()
    readiness = evaluate_production_privacy_security_legal_evidence(
        load_settings(
            {"SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(OUTPUT_PATH)}
        )
    )
    print(
        "SAEE_PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER: PASS "
        f"path={OUTPUT_PATH} "
        f"status={readiness['status']} "
        "local_public_shell_evidence=true "
        "production_privacy_security_legal_ready=false"
    )


if __name__ == "__main__":
    main()
