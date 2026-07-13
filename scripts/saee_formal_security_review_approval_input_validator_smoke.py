#!/usr/bin/env python3
"""Smoke check for the formal security review approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.production_privacy_security_legal_evidence import (
    FORMAL_SECURITY_REVIEW_KEYS,
)
from scripts.saee_formal_security_review_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
)
from scripts.saee_formal_security_review_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)


VALIDATOR_SCRIPT = (
    ROOT / "scripts/saee_formal_security_review_approval_input_validator.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["production_ready"] = True
    return {
        "template_type": "saee_formal_security_review_evidence_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_validator_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-05",
        "security_review_owner": "Fixture Security Owner",
        "report_reference": "fixture://formal-security-review/report",
        "decision_summary": "Fixture-only validator smoke input.",
        "evidence_review": {key: True for key in FORMAL_SECURITY_REVIEW_KEYS},
        "source_notes_by_key": {
            key: f"Fixture source note for {key}."
            for key in FORMAL_SECURITY_REVIEW_KEYS
        },
        "review_artifacts": [
            {
                "evidence_key": key,
                "artifact_reference": f"fixture://formal-security-review/{key}",
                "reviewed_by_human": True,
                "owner_named": True,
                "human_source_note": f"Fixture human source note for {key}.",
            }
            for key in FORMAL_SECURITY_REVIEW_KEYS
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
        "codex_performed_security_review": False,
        "codex_contacted_security_reviewer": False,
        "codex_contacted_vendor": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "codex_inferred_missing_evidence": False,
        "security_review_claim_published": False,
        "security_review_execution_authorized": False,
        "formal_security_review_completed_by_codex": False,
        "production_security_claim_published": False,
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
        "validator_type": "saee_formal_security_review_approval_input_validator",
        "validation_status": "pass",
        "input_complete": True,
        "builder_ready": True,
        "target_blocker_id": "formal_security_review",
        "blockers_closed_by_validator": 0,
        "formal_security_review_approved_by_validator": False,
        "formal_security_review_completed_by_validator": False,
        "formal_security_review_report_approved_by_validator": False,
        "dependency_review_completed_by_validator": False,
        "private_core_inspected_by_validator": False,
        "penetration_test_run_by_validator": False,
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
    require(default_summary["missing_review_artifacts"] == [], "default review artifacts complete")
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
        "formal_security_review_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_formal_security_review_input_pre_builder_check",
        "target_blocker_id: formal_security_review",
        "required_formal_security_review_evidence_item_count: 7",
        "blockers_closed_by_validator: 0",
        "formal_security_review_approved_by_validator: false",
        "formal_security_review_completed_by_validator: false",
        "formal_security_review_report_approved_by_validator: false",
        "dependency_review_completed_by_validator: false",
        "private_core_inspected_by_validator: false",
        "penetration_test_run_by_validator: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_security_review_approval: false",
        "recommend_for_security_review_completion_claim: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_security_vendor_contact: false",
        "recommend_for_penetration_test: false",
        "recommend_for_private_core_inspection: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_approval_input_validation.md",
        "/docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_formal_security_review_approval_input_validator.py",
        "/scripts/saee_formal_security_review_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("formal_security_review_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "pass",
        "validator_type": "saee_formal_security_review_approval_input_validator",
        "target_blocker_id": "formal_security_review",
        "builder_ready": True,
        "input_complete": True,
        "metadata_complete": True,
        "evidence_review_complete": True,
        "source_notes_complete": True,
        "review_artifacts_complete": True,
        "completed_review_artifact_count": 7,
        "blockers_closed_by_validator": 0,
        "formal_security_review_approved_by_validator": False,
        "formal_security_review_completed_by_validator": False,
        "formal_security_review_report_approved_by_validator": False,
        "dependency_review_completed_by_validator": False,
        "private_core_inspected_by_validator": False,
        "penetration_test_run_by_validator": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_FORMAL_SECURITY_REVIEW_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=pass builder_ready=true blockers_closed_by_validator=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
