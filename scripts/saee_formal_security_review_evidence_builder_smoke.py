#!/usr/bin/env python3
"""Smoke check for the SAEE formal security review evidence builder."""

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
INPUT_TEMPLATE = OUTPUT_DIR / "formal_security_review_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "formal_security_review_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = (
    OUTPUT_DIR
    / "production_privacy_security_legal_evidence.from_formal_security_review.local.json"
)
REPORT = OUTPUT_DIR / "formal_security_review_evidence_builder_report.md"
DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_SMOKE: FAIL: " + message
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
        "formal_security_review_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_formal_security_review_to_production_privacy_security_legal_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 7,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "formal_security_review_completed_for_review": False,
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
        "security_vendor_contacted": False,
        "codex_performed_security_review": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "security_review_claim_published": False,
        "production_security_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("privacy_security_legal_evidence_type")
        == "production_privacy_security_legal_evidence",
        "evidence type mismatch",
    )
    for key in [
        "formal_security_review_report",
        "public_shell_threat_model_reviewed",
        "auth_and_tenant_boundary_reviewed",
        "storage_backup_and_restore_reviewed",
        "dependency_review_completed",
        "private_core_non_exposure_review_completed",
        "review_findings_triaged",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_formal_security_review_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_performed_security_review") is False,
        "template must not claim Codex performed review",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "formal_security_review_evidence_builder_v0_1: true",
        "builder_scope: human_filled_formal_security_review_to_production_privacy_security_legal_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "formal_security_review_completed_for_review: false",
        "production_privacy_security_legal_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "codex_performed_security_review: false",
        "codex_ran_penetration_test: false",
        "security_review_claim_published: false",
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
        "codex_performed_security_review: true",
        "codex_ran_penetration_test: true",
        "security_review_claim_published: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_formal_security_review_evidence_builder import (
        FORMAL_SECURITY_REVIEW_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-security-reviewer",
                "review_date": "2026-07-04",
                "security_review_owner": "security-owner",
                "report_reference": "internal-review-report-reference",
                "decision_summary": "Human review record supplied for builder smoke fixture.",
            }
        )
        complete_input["evidence_review"] = {
            key: True for key in FORMAL_SECURITY_REVIEW_KEYS
        }
        complete_input["source_notes_by_key"] = {
            key: f"source note for {key}" for key in FORMAL_SECURITY_REVIEW_KEYS
        }
        complete_input["review_artifacts"] = [
            {
                "evidence_key": key,
                "artifact_reference": f"artifact-{key}",
                "reviewed_by_human": True,
                "owner_named": True,
                "human_source_note": f"artifact note for {key}",
            }
            for key in FORMAL_SECURITY_REVIEW_KEYS
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
            complete_summary["formal_security_review_completed_for_review"] is True,
            "complete fixture formal review evidence must be true",
        )
        require(
            complete_summary["production_privacy_security_legal_ready"] is False,
            "complete formal-only fixture must not make all privacy/security/legal ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["private_core_exposed"] = True
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
            "private_core_exposed" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report private_core_exposed",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/production_privacy_security_legal_evidence.from_formal_security_review.local.json",
        "/phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_evidence_builder_report.md",
        "/docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_formal_security_review_evidence_builder.py",
        "/scripts/saee_formal_security_review_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("formal_security_review_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_formal_security_review_to_production_privacy_security_legal_evidence",
        "target_blocker": "formal_security_review",
        "human_review_required": True,
        "formal_security_review_completed_for_review": False,
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
        "security_vendor_contacted": False,
        "codex_performed_security_review": False,
        "codex_ran_penetration_test": False,
        "codex_inspected_private_core": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Formal security review evidence builder v0.1 is implemented",
        "formal_security_review_evidence_builder_status=local_builder_available_default_hold",
        "formal_security_review_completed_for_review=false",
        "formal security review evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_FORMAL_SECURITY_REVIEW_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
