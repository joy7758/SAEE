#!/usr/bin/env python3
"""Smoke check for the SAEE billing/revenue evidence path proof."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_billing_revenue_evidence_path import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
)


RUNNER = ROOT / "scripts/saee_billing_revenue_evidence_path.py"
TARGET_BLOCKERS = [
    "pricing_page",
    "payment_provider",
    "invoice_process",
    "tax_review",
    "refund_policy",
    "tenant_billing_isolation",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BILLING_REVENUE_EVIDENCE_PATH_SMOKE: FAIL: " + message)


def main() -> None:
    require(RUNNER.exists(), "runner missing")
    run = subprocess.run(
        [sys.executable, str(RUNNER), "--json"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    result = json.loads(run.stdout)
    expected = {
        "billing_revenue_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_billing_revenue_evidence_path",
        "path_status": "pass_fixture_only",
        "fixture_only": True,
        "real_pricing_page_published": False,
        "real_pricing_page_approved": False,
        "real_payment_provider_configured": False,
        "real_checkout_enabled": False,
        "real_invoice_process_operational": False,
        "real_tax_review_completed": False,
        "real_refund_policy_approved": False,
        "real_tenant_billing_isolation_approved": False,
        "real_customer_payment_collected": False,
        "real_revenue_validated": False,
        "billing_revenue_readiness_status_after_fixture": "pass",
        "pricing_page_evidence_complete_after_fixture": True,
        "payment_provider_evidence_complete_after_fixture": True,
        "invoice_process_evidence_complete_after_fixture": True,
        "tax_review_evidence_complete_after_fixture": True,
        "refund_policy_evidence_complete_after_fixture": True,
        "tenant_billing_isolation_evidence_complete_after_fixture": True,
        "production_billing_revenue_ready_after_fixture": True,
        "commercial_status_after_fixture": "hold",
        "production_launch_status_after_fixture": "hold",
        "satisfied_production_checks_after_fixture": 6,
        "total_production_checks_after_fixture": 24,
        "production_blocker_count_after_fixture": 18,
        "billing_revenue_blocker_path_proven": True,
        "billing_revenue_target_blockers_satisfied_count_after_fixture": 6,
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
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
        "payment_provider_contacted": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "payment_provider_live_mode_enabled": False,
        "payment_link_created": False,
        "invoice_sent_to_customer": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "production_billing_enabled": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
    }
    for flag, expected_value in expected.items():
        require(result.get(flag) == expected_value, f"{flag} must be {expected_value}")
    require(
        result["billing_revenue_target_blockers_satisfied_by_fixture"]
        == TARGET_BLOCKERS,
        "target blockers changed",
    )
    require(
        result["billing_revenue_target_blockers_unsatisfied_by_fixture"] == [],
        "no target blockers should be unsatisfied in fixture",
    )
    require(DEFAULT_OUTPUT_PATH.exists(), "default output missing")
    persisted = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))
    require(persisted == result, "persisted output differs")

    for path in [DOC_PATH, GATE_PATH, REPORT_PATH]:
        require(path.exists(), f"{path} missing")
    combined_docs = "\n".join(
        path.read_text(encoding="utf-8") for path in [DOC_PATH, GATE_PATH, REPORT_PATH]
    )
    for token in [
        "billing_revenue_evidence_path_v0_1: true",
        "path_type: local_fixture_only_billing_revenue_evidence_path",
        "path_status: pass_fixture_only",
        "fixture_only: true",
        "real_pricing_page_published: false",
        "real_pricing_page_approved: false",
        "real_payment_provider_configured: false",
        "real_checkout_enabled: false",
        "real_invoice_process_operational: false",
        "real_tax_review_completed: false",
        "real_refund_policy_approved: false",
        "real_tenant_billing_isolation_approved: false",
        "real_customer_payment_collected: false",
        "real_revenue_validated: false",
        "billing_revenue_readiness_status_after_fixture: pass",
        "pricing_page_evidence_complete_after_fixture: true",
        "payment_provider_evidence_complete_after_fixture: true",
        "invoice_process_evidence_complete_after_fixture: true",
        "tax_review_evidence_complete_after_fixture: true",
        "refund_policy_evidence_complete_after_fixture: true",
        "tenant_billing_isolation_evidence_complete_after_fixture: true",
        "production_billing_revenue_ready_after_fixture: true",
        "billing_revenue_blocker_path_proven: true",
        "billing_revenue_target_blockers_satisfied_count_after_fixture: 6",
        "production_blocker_count_after_fixture: 18",
        "blockers_closed_by_path: 0",
        "answer: conditional",
        "recommend_for_human_billing_revenue_evidence_review: true",
        "recommend_for_blocker_closure_by_path_alone: false",
        "recommend_for_production_launch: false",
        "recommend_for_customer_contact: false",
        "recommend_for_payment_provider_contact: false",
        "recommend_for_payment_enablement: false",
        "recommend_for_checkout_enablement: false",
        "recommend_for_invoice_operation: false",
        "recommend_for_tax_collection: false",
        "recommend_for_revenue_validation: false",
    ]:
        require(token in combined_docs, "missing doc token: " + token)
    for token in [
        "production_ready: true",
        "\"production_ready\": true",
        "customer_validated: true",
        "\"customer_validated\": true",
        "product_launched: true",
        "\"product_launched\": true",
        "private_core_exposed: true",
        "\"private_core_exposed\": true",
        "real_pricing_page_published: true",
        "\"real_pricing_page_published\": true",
        "real_pricing_page_approved: true",
        "\"real_pricing_page_approved\": true",
        "real_payment_provider_configured: true",
        "\"real_payment_provider_configured\": true",
        "real_checkout_enabled: true",
        "\"real_checkout_enabled\": true",
        "real_invoice_process_operational: true",
        "\"real_invoice_process_operational\": true",
        "real_tax_review_completed: true",
        "\"real_tax_review_completed\": true",
        "real_refund_policy_approved: true",
        "\"real_refund_policy_approved\": true",
        "real_tenant_billing_isolation_approved: true",
        "\"real_tenant_billing_isolation_approved\": true",
        "real_customer_payment_collected: true",
        "\"real_customer_payment_collected\": true",
        "real_revenue_validated: true",
        "\"real_revenue_validated\": true",
        "customer_contacted: true",
        "\"customer_contacted\": true",
        "payment_provider_contacted: true",
        "\"payment_provider_contacted\": true",
        "tax_advisor_contacted: true",
        "\"tax_advisor_contacted\": true",
        "legal_counsel_contacted: true",
        "\"legal_counsel_contacted\": true",
        "pricing_page_published: true",
        "\"pricing_page_published\": true",
        "sales_offer_sent: true",
        "\"sales_offer_sent\": true",
        "payment_provider_configured: true",
        "\"payment_provider_configured\": true",
        "checkout_enabled: true",
        "\"checkout_enabled\": true",
        "invoice_sent_to_customer: true",
        "\"invoice_sent_to_customer\": true",
        "tax_collection_started: true",
        "\"tax_collection_started\": true",
        "refund_policy_published: true",
        "\"refund_policy_published\": true",
        "customer_payment_collected: true",
        "\"customer_payment_collected\": true",
        "revenue_validated: true",
        "\"revenue_validated\": true",
        "recommend_for_blocker_closure_by_path_alone: true",
        "recommend_for_production_launch: true",
        "recommend_for_customer_contact: true",
        "recommend_for_payment_provider_contact: true",
        "recommend_for_payment_enablement: true",
        "recommend_for_checkout_enablement: true",
        "recommend_for_invoice_operation: true",
        "recommend_for_tax_collection: true",
        "recommend_for_revenue_validation: true",
    ]:
        require(token not in combined_docs, "forbidden doc token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_path_report.md",
        "/docs/strategy/SAEE_BILLING_REVENUE_EVIDENCE_PATH_RECOMMENDATION_GATE.md",
        "/scripts/saee_billing_revenue_evidence_path.py",
        "/scripts/saee_billing_revenue_evidence_path_smoke.py",
    ]:
        require(path in llms, "llms.txt missing path: " + path)

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("billing_revenue_evidence_path_v0_1", {})
    expected_index = {
        "status": "local_fixture_only_path_proof",
        "path_type": "local_fixture_only_billing_revenue_evidence_path",
        "fixture_only": True,
        "real_pricing_page_published": False,
        "real_pricing_page_approved": False,
        "real_payment_provider_configured": False,
        "real_checkout_enabled": False,
        "real_invoice_process_operational": False,
        "real_tax_review_completed": False,
        "real_refund_policy_approved": False,
        "real_tenant_billing_isolation_approved": False,
        "real_customer_payment_collected": False,
        "real_revenue_validated": False,
        "billing_revenue_blocker_path_proven": True,
        "pricing_page_evidence_complete_after_fixture": True,
        "payment_provider_evidence_complete_after_fixture": True,
        "invoice_process_evidence_complete_after_fixture": True,
        "tax_review_evidence_complete_after_fixture": True,
        "refund_policy_evidence_complete_after_fixture": True,
        "tenant_billing_isolation_evidence_complete_after_fixture": True,
        "production_billing_revenue_ready_after_fixture": True,
        "billing_revenue_target_blockers_satisfied_count_after_fixture": 6,
        "production_blocker_count_after_fixture": 18,
        "blockers_closed_by_path": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "customer_contacted": False,
        "payment_provider_contacted": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_sent_to_customer": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
    }
    for flag, expected_value in expected_index.items():
        require(
            entry.get(flag) == expected_value,
            f"agent-index billing_revenue_evidence_path_v0_1 {flag} must be {expected_value}",
        )

    print("SAEE_BILLING_REVENUE_EVIDENCE_PATH_SMOKE: PASS")


if __name__ == "__main__":
    main()
