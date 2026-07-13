#!/usr/bin/env python3
"""Smoke check for the SAEE tax-review evidence builder."""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
INPUT_TEMPLATE = OUTPUT_DIR / "tax_review_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "tax_review_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = OUTPUT_DIR / "production_billing_revenue_evidence.from_tax_review.local.json"
REPORT = OUTPUT_DIR / "tax_review_evidence_builder_report.md"
DOC = ROOT / "phase_b_product/commercial_readiness/TAX_REVIEW_EVIDENCE_BUILDER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_TAX_REVIEW_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TAX_REVIEW_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    require(INPUT_TEMPLATE.exists(), "input template missing")
    require(BUILDER_OUTPUT.exists(), "builder output missing")
    require(EVIDENCE_OUTPUT.exists(), "billing/revenue evidence output missing")
    require(REPORT.exists(), "builder report missing")
    require(DOC.exists(), "top doc missing")
    require(GATE.exists(), "recommendation gate missing")

    summary = read_json(BUILDER_OUTPUT)
    evidence = read_json(EVIDENCE_OUTPUT)
    template = read_json(INPUT_TEMPLATE)

    expected_summary = {
        "tax_review_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_tax_review_to_production_billing_revenue_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 5,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "tax_review_evidence_complete_for_review": False,
        "production_billing_revenue_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "tax_review_completed": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "tax_rate_configured": False,
        "tax_exemption_process_available": False,
        "invoice_wording_published": False,
        "currency_policy_published": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_contacted_tax_advisor": False,
        "codex_contacted_legal_counsel": False,
        "codex_configured_tax_collection": False,
        "codex_started_tax_collection": False,
        "tax_review_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence",
        "evidence type mismatch",
    )
    for key in [
        "target_jurisdictions_reviewed",
        "tax_obligations_reviewed",
        "invoice_wording_approved",
        "currency_policy_approved",
        "tax_collection_approval_recorded",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "tax_advisor_contacted",
        "legal_counsel_contacted",
        "tax_collection_started",
        "tax_review_completed",
        "tax_rate_configured",
        "tax_exemption_process_available",
        "invoice_wording_published",
        "currency_policy_published",
        "payment_provider_configured",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "codex_contacted_tax_advisor",
        "codex_contacted_legal_counsel",
        "codex_configured_tax_collection",
        "codex_started_tax_collection",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_tax_review_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_contacted_tax_advisor") is False,
        "template must not claim Codex contacted tax advisor",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "tax_review_evidence_builder_v0_1: true",
        "builder_scope: human_filled_tax_review_to_production_billing_revenue_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "tax_review_evidence_complete_for_review: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "tax_review_completed: false",
        "tax_advisor_contacted: false",
        "legal_counsel_contacted: false",
        "tax_rate_configured: false",
        "tax_exemption_process_available: false",
        "invoice_wording_published: false",
        "currency_policy_published: false",
        "tax_collection_started: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "codex_contacted_tax_advisor: false",
        "codex_contacted_legal_counsel: false",
        "codex_configured_tax_collection: false",
        "codex_started_tax_collection: false",
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
        "tax_review_completed: true",
        "tax_advisor_contacted: true",
        "legal_counsel_contacted: true",
        "tax_collection_started: true",
        "customer_payment_collected: true",
        "revenue_validated: true",
        "codex_contacted_tax_advisor: true",
        "codex_configured_tax_collection: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_tax_review_evidence_builder import (
        TARGET_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-tax-reviewer",
                "review_date": "2026-07-04",
                "commercial_owner": "commercial-owner",
                "tax_owner": "tax-owner",
                "accounting_owner": "accounting-owner",
                "legal_owner": "legal-owner",
                "billing_owner": "billing-owner",
                "review_record_reference": "internal-tax-review-reference",
                "decision_summary": "Human tax-review evidence supplied for smoke fixture.",
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
            complete_summary["tax_review_evidence_complete_for_review"] is True,
            "complete fixture tax-review evidence must be true",
        )
        require(
            complete_summary["production_billing_revenue_ready"] is False,
            "complete tax fixture must not make all billing/revenue ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["tax_collection_started"] = True
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
            "tax_collection_started" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report tax_collection_started",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/TAX_REVIEW_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_tax_review.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_evidence_builder_report.md",
        "/docs/strategy/SAEE_TAX_REVIEW_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_tax_review_evidence_builder.py",
        "/scripts/saee_tax_review_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("tax_review_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_tax_review_to_production_billing_revenue_evidence",
        "target_blocker": "tax_review",
        "human_review_required": True,
        "tax_review_evidence_complete_for_review": False,
        "production_billing_revenue_ready": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "tax_review_completed": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_contacted_tax_advisor": False,
        "codex_configured_tax_collection": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Tax review evidence builder v0.1 is implemented",
        "tax_review_evidence_builder_status=local_builder_available_default_hold",
        "tax_review_evidence_complete_for_review=false",
        "tax review evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_TAX_REVIEW_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
