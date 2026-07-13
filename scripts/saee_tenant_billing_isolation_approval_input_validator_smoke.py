#!/usr/bin/env python3
"""Smoke check for the tenant billing isolation approval input validator."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_tenant_billing_isolation_approval_input_validator import (
    DEFAULT_OUTPUT_PATH,
    DOC_PATH,
    GATE_PATH,
    REPORT_PATH,
    build_validation,
)
from scripts.saee_tenant_billing_isolation_evidence_builder import (
    INPUT_FORBIDDEN_TRUE_KEYS,
    TARGET_KEYS,
)


VALIDATOR_SCRIPT = (
    ROOT / "scripts/saee_tenant_billing_isolation_approval_input_validator.py"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_VALIDATOR_SMOKE: FAIL: "
            + message
        )


def write_json(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def complete_input(*, unsafe: bool = False) -> dict[str, object]:
    boundary_review = {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS}
    if unsafe:
        boundary_review["tenant_billing_isolated"] = True
    return {
        "template_type": "saee_tenant_billing_isolation_evidence_input",
        "template_version": "v0.1",
        "input_status": "human_filled_fixture_for_validator_smoke_only",
        "human_reviewer_name": "Fixture Reviewer",
        "review_date": "2026-07-07",
        "commercial_owner": "Fixture Commercial Owner",
        "accounting_owner": "Fixture Accounting Owner",
        "legal_owner": "Fixture Legal Owner",
        "support_owner": "Fixture Support Owner",
        "billing_owner": "Fixture Billing Owner",
        "payment_owner": "Fixture Payment Owner",
        "tenant_boundary_owner": "Fixture Tenant Boundary Owner",
        "review_record_reference": "fixture://tenant-billing-isolation/review-record",
        "decision_summary": "Fixture-only validator smoke input.",
        "evidence_review": {key: True for key in TARGET_KEYS},
        "source_notes_by_key": {
            key: f"Fixture source note for {key}." for key in TARGET_KEYS
        },
        "review_artifacts": [
            {
                "evidence_key": key,
                "artifact_reference": f"fixture://tenant-billing-isolation/{key}",
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
        "production_billing_enabled": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
        "tenant_billing_isolation_available": False,
        "tenant_billing_isolation_approved": False,
        "tenant_billing_isolated": False,
        "tenant_billing_isolation_enabled": False,
        "tenant_billing_account_model_available": False,
        "tenant_billing_account_model_approved": False,
        "tenant_invoice_partitioning_tested": False,
        "tenant_payment_event_partitioning_tested": False,
        "cross_tenant_billing_access_tests_passed": False,
        "billing_audit_metadata_policy_approved": False,
        "tenant_billing_retention_policy_approved": False,
        "payment_provider_tenant_mapping_approved": False,
        "payment_provider_tenant_mapping_configured": False,
        "tenant_billing_transaction_processed": False,
        "tenant_billing_invoice_or_charge_issued_to_customer": False,
        "tenant_billing_isolation_completed_by_codex": False,
        "tenant_billing_isolation_execution_authorized": False,
        "codex_published_tenant_billing_isolation": False,
        "codex_processed_tenant_billing": False,
        "codex_configured_tenant_billing_handling": False,
        "codex_inferred_missing_evidence": False,
        "task_candidates_executed": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "development_permission_granted": False,
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
        "validator_type": "saee_tenant_billing_isolation_approval_input_validator",
        "validation_status": "hold",
        "input_complete": False,
        "builder_ready": False,
        "target_blocker_id": "tenant_billing_isolation",
        "blockers_closed_by_validator": 0,
        "tenant_billing_isolation_approved_by_validator": False,
        "tenant_billing_isolation_published_by_validator": False,
        "tenant_billing_isolation_completed_by_validator": False,
        "tenant_billing_account_model_approved_by_validator": False,
        "cross_tenant_billing_access_tested_by_validator": False,
        "payment_provider_tenant_mapping_configured_by_validator": False,
        "customer_payment_collected_by_validator": False,
        "revenue_validated_by_validator": False,
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
    require(
        default_summary["missing_review_artifacts"],
        "default input must miss review artifacts",
    )
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
        "tenant_billing_isolation_approval_input_validator_v0_1: true",
        "validator_scope: local_human_filled_tenant_billing_isolation_input_pre_builder_check",
        "target_blocker_id: tenant_billing_isolation",
        "required_tenant_billing_isolation_evidence_item_count: 6",
        "blockers_closed_by_validator: 0",
        "tenant_billing_isolation_approved_by_validator: false",
        "tenant_billing_isolation_published_by_validator: false",
        "tenant_billing_isolation_completed_by_validator: false",
        "tenant_billing_account_model_approved_by_validator: false",
        "cross_tenant_billing_access_tested_by_validator: false",
        "payment_provider_tenant_mapping_configured_by_validator: false",
        "customer_payment_collected_by_validator: false",
        "revenue_validated_by_validator: false",
        "production_ready: false",
        "customer_validated: false",
        "private_core_exposed: false",
        "answer: conditional",
        "recommend_for_human_input_validation: true",
        "recommend_for_tenant_billing_isolation_approval: false",
        "recommend_for_tenant_billing_isolation_publication: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_payment_provider_tenant_mapping_configuration: false",
        "recommend_for_payment_collection: false",
        "recommend_for_revenue_validation: false",
    ]:
        require(token in combined, "missing doc/gate token: " + token)

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/TENANT_BILLING_ISOLATION_APPROVAL_INPUT_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_evidence_input.template.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_approval_input_validation.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_approval_input_validation.md",
        "/docs/strategy/SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_tenant_billing_isolation_approval_input_validator.py",
        "/scripts/saee_tenant_billing_isolation_approval_input_validator_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("tenant_billing_isolation_approval_input_validator_v0_1", {})
    for key, value in {
        "status": "hold",
        "validator_type": "saee_tenant_billing_isolation_approval_input_validator",
        "target_blocker_id": "tenant_billing_isolation",
        "builder_ready": False,
        "blockers_closed_by_validator": 0,
        "tenant_billing_isolation_approved_by_validator": False,
        "tenant_billing_isolation_published_by_validator": False,
        "tenant_billing_isolation_completed_by_validator": False,
        "tenant_billing_account_model_approved_by_validator": False,
        "cross_tenant_billing_access_tested_by_validator": False,
        "payment_provider_tenant_mapping_configured_by_validator": False,
        "customer_payment_collected_by_validator": False,
        "revenue_validated_by_validator": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_TENANT_BILLING_ISOLATION_APPROVAL_INPUT_VALIDATOR_SMOKE: PASS "
        "status=hold builder_ready=false blockers_closed_by_validator=0 "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
