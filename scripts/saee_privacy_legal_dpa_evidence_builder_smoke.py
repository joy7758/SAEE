#!/usr/bin/env python3
"""Smoke check for the SAEE privacy/legal + DPA evidence builder."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
INPUT_TEMPLATE = OUTPUT_DIR / "privacy_legal_dpa_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "privacy_legal_dpa_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = (
    OUTPUT_DIR / "production_privacy_security_legal_evidence.from_privacy_legal_dpa.local.json"
)
REPORT = OUTPUT_DIR / "privacy_legal_dpa_evidence_builder_report.md"
DOC = ROOT / "phase_b_product/commercial_readiness/PRIVACY_LEGAL_DPA_EVIDENCE_BUILDER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PRIVACY_LEGAL_DPA_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_EVIDENCE_BUILDER_SMOKE: FAIL: " + message
        )


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    require(INPUT_TEMPLATE.exists(), "input template missing")
    require(BUILDER_OUTPUT.exists(), "builder output missing")
    require(EVIDENCE_OUTPUT.exists(), "privacy/security/legal evidence output missing")
    require(REPORT.exists(), "builder report missing")
    require(DOC.exists(), "top doc missing")
    require(GATE.exists(), "recommendation gate missing")

    summary = read_json(BUILDER_OUTPUT)
    evidence = read_json(EVIDENCE_OUTPUT)
    template = read_json(INPUT_TEMPLATE)

    expected_summary = {
        "privacy_legal_dpa_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_privacy_legal_dpa_review_to_production_privacy_security_legal_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 13,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "privacy_legal_review_completed_for_review": False,
        "data_processing_agreement_available_for_review": False,
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
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "dpa_sent_to_customer": False,
        "codex_performed_legal_review": False,
        "codex_created_dpa": False,
        "codex_processed_customer_data": False,
        "legal_review_claim_published": False,
        "dpa_availability_claim_published": False,
        "customer_data_processing_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("privacy_security_legal_evidence_type")
        == "production_privacy_security_legal_evidence",
        "evidence type mismatch",
    )
    for key in [
        "privacy_notice_approved",
        "terms_of_service_approved",
        "data_inventory_reviewed",
        "retention_policy_approved",
        "subprocessor_inventory_reviewed",
        "customer_data_processing_approved",
        "legal_reviewer_recorded",
        "dpa_terms_approved",
        "controller_processor_roles_defined",
        "subprocessor_terms_approved",
        "breach_notice_terms_approved",
        "deletion_or_return_terms_approved",
        "customer_dpa_template_available",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "legal_counsel_contacted",
        "customer_data_processed",
        "dpa_sent_to_customer",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_privacy_legal_dpa_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_performed_legal_review") is False,
        "template must not claim Codex performed legal review",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "privacy_legal_dpa_evidence_builder_v0_1: true",
        "builder_scope: human_filled_privacy_legal_dpa_review_to_production_privacy_security_legal_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "privacy_legal_review_completed_for_review: false",
        "data_processing_agreement_available_for_review: false",
        "production_privacy_security_legal_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "codex_performed_legal_review: false",
        "codex_created_dpa: false",
        "customer_data_processed: false",
        "blockers_closed_by_builder: 0",
    ]:
        require(token in combined_docs, "missing doc token: " + token)
    for token in [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "legal_counsel_contacted: true",
        "customer_data_processed: true",
        "dpa_sent_to_customer: true",
        "codex_performed_legal_review: true",
        "codex_created_dpa: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_privacy_legal_dpa_evidence_builder import (
        TARGET_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-legal-reviewer",
                "review_date": "2026-07-04",
                "legal_owner": "legal-owner",
                "privacy_owner": "privacy-owner",
                "dpa_owner": "dpa-owner",
                "review_record_reference": "internal-legal-review-reference",
                "decision_summary": "Human legal and DPA review record supplied for smoke fixture.",
            }
        )
        complete_input["evidence_review"] = {key: True for key in TARGET_KEYS}
        complete_input["source_notes_by_key"] = {
            key: f"source note for {key}" for key in TARGET_KEYS
        }
        complete_input["review_artifacts"] = [
            {
                "evidence_key": key,
                "artifact_reference": f"artifact-{key}",
                "reviewed_by_human": True,
                "owner_named": True,
                "human_source_note": f"artifact note for {key}",
            }
            for key in TARGET_KEYS
        ]
        complete_path = tmp / "complete.json"
        complete_path.write_text(json.dumps(complete_input), encoding="utf-8")
        complete_summary = build_from_input(
            complete_path,
            tmp / "complete_output.json",
            tmp / "complete_evidence.json",
            write_documentation=False,
        )
        require(complete_summary["status"] == "pass", "complete fixture must pass")
        require(
            complete_summary["privacy_legal_review_completed_for_review"] is True,
            "complete fixture privacy legal review evidence must be true",
        )
        require(
            complete_summary["data_processing_agreement_available_for_review"] is True,
            "complete fixture DPA evidence must be true",
        )
        require(
            complete_summary["production_privacy_security_legal_ready"] is False,
            "complete legal+DPA fixture must not make all privacy/security/legal ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["customer_data_processed"] = True
        unsafe_path = tmp / "unsafe.json"
        unsafe_path.write_text(json.dumps(unsafe_input), encoding="utf-8")
        unsafe_summary = build_from_input(
            unsafe_path,
            tmp / "unsafe_output.json",
            tmp / "unsafe_evidence.json",
            write_documentation=False,
        )
        require(unsafe_summary["status"] == "stop", "unsafe fixture must stop")
        require(
            "customer_data_processed" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report customer_data_processed",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRIVACY_LEGAL_DPA_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/production_privacy_security_legal_evidence.from_privacy_legal_dpa.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_builder_report.md",
        "/docs/strategy/SAEE_PRIVACY_LEGAL_DPA_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_privacy_legal_dpa_evidence_builder.py",
        "/scripts/saee_privacy_legal_dpa_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("privacy_legal_dpa_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_privacy_legal_dpa_review_to_production_privacy_security_legal_evidence",
        "target_blockers": ["privacy_legal_review", "data_processing_agreement"],
        "human_review_required": True,
        "privacy_legal_review_completed_for_review": False,
        "data_processing_agreement_available_for_review": False,
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
        "legal_counsel_contacted": False,
        "customer_data_processed": False,
        "dpa_sent_to_customer": False,
        "codex_performed_legal_review": False,
        "codex_created_dpa": False,
        "codex_processed_customer_data": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Privacy/legal + DPA evidence builder v0.1 is implemented",
        "privacy_legal_dpa_evidence_builder_status=local_builder_available_default_hold",
        "privacy_legal_review_completed_for_review=false",
        "data_processing_agreement_available_for_review=false",
        "privacy/legal + DPA evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_PRIVACY_LEGAL_DPA_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
