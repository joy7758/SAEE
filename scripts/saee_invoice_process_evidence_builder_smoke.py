#!/usr/bin/env python3
"""Smoke check for the SAEE invoice-process evidence builder."""

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
INPUT_TEMPLATE = OUTPUT_DIR / "invoice_process_evidence_input.template.json"
BUILDER_OUTPUT = OUTPUT_DIR / "invoice_process_evidence_builder_output.local.json"
EVIDENCE_OUTPUT = OUTPUT_DIR / "production_billing_revenue_evidence.from_invoice_process.local.json"
REPORT = OUTPUT_DIR / "invoice_process_evidence_builder_report.md"
DOC = ROOT / "phase_b_product/commercial_readiness/INVOICE_PROCESS_EVIDENCE_BUILDER_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER_SMOKE: FAIL: " + message)


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
        "invoice_process_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_invoice_process_to_production_billing_revenue_evidence",
        "status": "hold",
        "input_complete": False,
        "required_evidence_item_count": 6,
        "provided_evidence_item_count": 0,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "invoice_process_evidence_complete_for_review": False,
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
        "invoice_created": False,
        "invoice_template_published": False,
        "invoice_sent_to_customer": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_created_invoice": False,
        "codex_sent_invoice": False,
        "codex_signed_contract": False,
        "codex_performed_reconciliation": False,
        "invoice_process_claim_published": False,
    }
    for key, expected in expected_summary.items():
        require(summary.get(key) == expected, f"summary {key} must be {expected}")

    require(
        evidence.get("billing_revenue_evidence_type")
        == "production_billing_revenue_evidence",
        "evidence type mismatch",
    )
    for key in [
        "invoice_owner_named",
        "invoice_workflow_approved",
        "contract_handoff_defined",
        "payment_reconciliation_tested",
        "billing_support_handoff_defined",
        "bookkeeping_review_completed",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "invoice_sent_to_customer",
        "enterprise_contract_signed",
        "payment_provider_configured",
        "checkout_enabled",
        "customer_payment_collected",
        "revenue_validated",
        "invoice_created",
        "invoice_template_published",
    ]:
        require(evidence.get(key) is False, f"default evidence {key} must be false")

    require(
        template.get("template_type") == "saee_invoice_process_evidence_input",
        "template type mismatch",
    )
    require(
        template.get("codex_created_invoice") is False,
        "template must not claim Codex created invoice",
    )

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [REPORT, DOC, GATE]
    )
    for token in [
        "invoice_process_evidence_builder_v0_1: true",
        "builder_scope: human_filled_invoice_process_to_production_billing_revenue_evidence",
        "recommend_for_human_evidence_input: true",
        "recommend_for_blocker_closure: false",
        "invoice_process_evidence_complete_for_review: false",
        "production_billing_revenue_ready: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "invoice_created: false",
        "invoice_template_published: false",
        "invoice_sent_to_customer: false",
        "enterprise_contract_signed: false",
        "payment_provider_configured: false",
        "checkout_enabled: false",
        "customer_payment_collected: false",
        "revenue_validated: false",
        "codex_created_invoice: false",
        "codex_sent_invoice: false",
        "codex_signed_contract: false",
        "codex_performed_reconciliation: false",
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
        "invoice_sent_to_customer: true",
        "enterprise_contract_signed: true",
        "customer_payment_collected: true",
        "revenue_validated: true",
        "codex_created_invoice: true",
        "codex_sent_invoice: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production_launch: true",
    ]:
        require(token not in combined_docs, "forbidden true claim present: " + token)

    from saee_invoice_process_evidence_builder import (
        TARGET_KEYS,
        build_from_input,
        default_input_template,
    )

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        complete_input = default_input_template()
        complete_input.update(
            {
                "human_reviewer_name": "human-invoice-reviewer",
                "review_date": "2026-07-04",
                "commercial_owner": "commercial-owner",
                "invoice_owner": "invoice-owner",
                "accounting_owner": "accounting-owner",
                "support_owner": "support-owner",
                "review_record_reference": "internal-invoice-process-review-reference",
                "decision_summary": "Human invoice-process evidence supplied for smoke fixture.",
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
            complete_summary["invoice_process_evidence_complete_for_review"] is True,
            "complete fixture invoice-process evidence must be true",
        )
        require(
            complete_summary["production_billing_revenue_ready"] is False,
            "complete invoice fixture must not make all billing/revenue ready",
        )
        require(
            complete_summary["blockers_closed_by_builder"] == 0,
            "complete fixture still closes zero blockers",
        )

        unsafe_input = default_input_template()
        unsafe_input["invoice_sent_to_customer"] = True
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
            "invoice_sent_to_customer" in unsafe_summary["input_boundary_violations"],
            "unsafe fixture must report invoice_sent_to_customer",
        )

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/INVOICE_PROCESS_EVIDENCE_BUILDER_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_builder_output.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_invoice_process.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_builder_report.md",
        "/docs/strategy/SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md",
        "/scripts/saee_invoice_process_evidence_builder.py",
        "/scripts/saee_invoice_process_evidence_builder_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("invoice_process_evidence_builder_v0_1", {})
    for key, expected in {
        "status": "local_builder_available_default_hold",
        "builder_scope": "human_filled_invoice_process_to_production_billing_revenue_evidence",
        "target_blocker": "invoice_process",
        "human_review_required": True,
        "invoice_process_evidence_complete_for_review": False,
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
        "invoice_sent_to_customer": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "codex_created_invoice": False,
        "codex_sent_invoice": False,
        "blockers_closed_by_builder": 0,
    }.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")

    status = (ROOT / "PROJECT_STATUS.md").read_text(encoding="utf-8")
    for token in [
        "Invoice process evidence builder v0.1 is implemented",
        "invoice_process_evidence_builder_status=local_builder_available_default_hold",
        "invoice_process_evidence_complete_for_review=false",
        "invoice process evidence builder blockers_closed=0",
    ]:
        require(token in status, "PROJECT_STATUS.md missing token: " + token)

    print(
        "SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER_SMOKE: PASS "
        "default_hold=true complete_fixture_pass=true unsafe_fixture_stop=true "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
