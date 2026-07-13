#!/usr/bin/env python3
"""Smoke check for the privacy/legal + DPA approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_privacy_legal_dpa_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    TARGET_KEYS,
)
from scripts.saee_privacy_legal_dpa_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)


VALIDATOR_SCRIPT = ROOT / "scripts/saee_privacy_legal_dpa_approval_input_validator.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["codex_performed_legal_review"] = True
    return {
        "template_type": "saee_privacy_legal_dpa_evidence_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_validator_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-07",
        "legal_owner": "Fixture Legal Owner",
        "privacy_owner": "Fixture Privacy Owner",
        "dpa_owner": "Fixture DPA Owner",
        "review_record_reference": "fixture://privacy-legal-dpa/review",
        "decision_summary": "Fixture-only validator smoke input.",
        "evidence_review": {key: True for key in TARGET_KEYS},
        "source_notes_by_key": {
            key: f"Fixture source note for {key}." for key in TARGET_KEYS
        },
        "review_artifacts": [
            {
                "evidence_key": key,
                "artifact_reference": f"fixture://privacy-legal-dpa/{key}",
                "reviewed_by_human": True,
                "owner_named": True,
                "human_source_note": f"Fixture human source note for {key}.",
            }
            for key in TARGET_KEYS
        ],
        "boundary_review": boundary_review,
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
        "external_ai_assistant_tested": False,
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
        "codex_performed_legal_review": False,
        "codex_contacted_legal_counsel": False,
        "codex_created_dpa": False,
        "codex_approved_dpa": False,
        "codex_processed_customer_data": False,
        "codex_inferred_missing_evidence": False,
        "legal_review_claim_published": False,
        "dpa_availability_claim_published": False,
        "customer_data_processing_claim_published": False,
        "privacy_legal_review_completed_by_codex": False,
        "data_processing_agreement_completed_by_codex": False,
        "legal_review_execution_authorized": False,
        "blockers_closed_by_builder": False,
    }


def main() -> None:
    require(VALIDATOR_SCRIPT.exists(), "validator script missing")
    default_run = subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    default_summary = json.loads(default_run.stdout)
    expected_default = {
        "validator_type": "saee_privacy_legal_dpa_approval_input_validator",
        "validation_status": "hold",
        "input_complete": False,
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "privacy_legal_review_approved_by_validator": False,
        "privacy_legal_review_completed_by_validator": False,
        "data_processing_agreement_approved_by_validator": False,
        "data_processing_agreement_completed_by_validator": False,
        "legal_review_performed_by_validator": False,
        "dpa_created_by_validator": False,
        "dpa_approved_by_validator": False,
        "legal_counsel_contacted_by_validator": False,
        "customer_data_processed_by_validator": False,
        "terms_published_by_validator": False,
        "privacy_notice_published_by_validator": False,
        "dpa_sent_to_customer_by_validator": False,
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
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
    }
    for key, value in expected_default.items():
        require(default_summary.get(key) == value, f"default {key} must be {value}")
    require(default_summary["target_blocker_ids"] == [
        "privacy_legal_review",
        "data_processing_agreement",
    ], "target blockers mismatch")
    require(default_summary["missing_review_artifacts"], "default input must miss artifacts")
    require(DEFAULT_OUTPUT_PATH.exists(), "default validation output missing")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        complete_path = tmp / "complete_input.json"
        unsafe_path = tmp / "unsafe_input.json"
        write_json(complete_path, complete_input())
        write_json(unsafe_path, complete_input(unsafe=True))
        complete_summary = build_validation(complete_path)
        unsafe_summary = build_validation(unsafe_path)

    require(complete_summary["validation_status"] == "pass", "complete input must pass")
    require(complete_summary["input_complete"] is True, "complete input complete")
    require(complete_summary["builder_ready"] is True, "complete input builder ready")
    require(
        complete_summary["blockers_closed_by_validator"] == 0,
        "complete input closes no blockers",
    )
    require(
        complete_summary["privacy_legal_review_completed_by_validator"] is False,
        "complete input must not claim privacy/legal completion",
    )
    require(
        complete_summary["data_processing_agreement_completed_by_validator"] is False,
        "complete input must not claim DPA completion",
    )
    require(unsafe_summary["validation_status"] == "stop", "unsafe input stops")
    require(unsafe_summary["boundary_violation_count"] > 0, "unsafe violations")
    require(unsafe_summary["builder_ready"] is False, "unsafe input not builder ready")

    subprocess.run(
        [sys.executable, str(VALIDATOR_SCRIPT)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "privacy_legal_dpa_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_privacy_legal_dpa_input_pre_builder_check",
        "target_blocker_ids: privacy_legal_review,data_processing_agreement",
        "required_metadata_field_count: 7",
        "required_privacy_legal_dpa_evidence_item_count: 13",
        "blockers_closed_by_validator: 0",
        "privacy_legal_review_approved_by_validator: false",
        "privacy_legal_review_completed_by_validator: false",
        "data_processing_agreement_approved_by_validator: false",
        "data_processing_agreement_completed_by_validator: false",
        "legal_review_performed_by_validator: false",
        "dpa_created_by_validator: false",
        "dpa_approved_by_validator: false",
        "legal_counsel_contacted_by_validator: false",
        "customer_data_processed_by_validator: false",
        "terms_published_by_validator: false",
        "privacy_notice_published_by_validator: false",
        "dpa_sent_to_customer_by_validator: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_privacy_legal_review_approval: false",
        "recommend_for_data_processing_agreement_approval: false",
        "recommend_for_legal_review_completion_claim: false",
        "recommend_for_dpa_availability_claim: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_legal_counsel_contact: false",
        "recommend_for_customer_contact: false",
        "recommend_for_terms_publication: false",
        "recommend_for_privacy_notice_publication: false",
        "recommend_for_dpa_customer_send: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_legal_dpa_approval_input_validation.md",
        "/docs/strategy/SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_privacy_legal_dpa_approval_input_validator.py",
        "/scripts/saee_privacy_legal_dpa_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("privacy_legal_dpa_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "hold",
        "validator_type": "saee_privacy_legal_dpa_approval_input_validator",
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "privacy_legal_review_approved_by_validator": False,
        "privacy_legal_review_completed_by_validator": False,
        "data_processing_agreement_approved_by_validator": False,
        "data_processing_agreement_completed_by_validator": False,
        "legal_review_performed_by_validator": False,
        "dpa_created_by_validator": False,
        "dpa_approved_by_validator": False,
        "legal_counsel_contacted_by_validator": False,
        "customer_data_processed_by_validator": False,
        "terms_published_by_validator": False,
        "privacy_notice_published_by_validator": False,
        "dpa_sent_to_customer_by_validator": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_PRIVACY_LEGAL_DPA_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=hold builder_ready=false blockers_closed_by_validator=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
