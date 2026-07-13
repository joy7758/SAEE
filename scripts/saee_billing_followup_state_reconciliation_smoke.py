#!/usr/bin/env python3
"""Smoke test for billing follow-up state reconciliation."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_billing_followup_state_reconciliation.py"
OUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "billing_followup_state_reconciliation"
)
SUMMARY = OUT_DIR / "billing_followup_state_reconciliation.local.json"
REPORT = OUT_DIR / "billing_followup_state_reconciliation.md"
BOUNDARY = OUT_DIR / "billing_followup_state_reconciliation_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/BILLING_FOLLOWUP_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION_SMOKE: FAIL " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(data, dict), f"{path.relative_to(ROOT)} must contain an object")
    return data


def main() -> None:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION: PASS" in result.stdout, "runner did not pass")
    for path in [SUMMARY, REPORT, BOUNDARY, TOP_DOC, GATE]:
        require(path.is_file(), f"missing {path.relative_to(ROOT)}")

    payload = read_json(SUMMARY)
    expected = {
        "billing_followup_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_billing_followup_state_reconciliation_no_payment_no_checkout_no_closure",
        "payment_provider_ready_for_review": True,
        "invoice_process_ready_for_review": True,
        "tax_review_ready_for_review": True,
        "refund_policy_ready_for_review": True,
        "tenant_billing_isolation_ready_for_review": True,
        "ready_for_review_count": 5,
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "payment_provider_configured": False,
        "payment_provider_contacted": False,
        "payment_provider_live_mode_enabled": False,
        "codex_configured_payment_provider": False,
        "codex_contacted_payment_provider": False,
        "codex_created_payment_link": False,
        "codex_enabled_checkout": False,
        "codex_processed_payment": False,
        "checkout_enabled": False,
        "invoice_sent_to_customer": False,
        "codex_created_invoice": False,
        "codex_sent_invoice": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "codex_contacted_tax_advisor": False,
        "codex_configured_tax_collection": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "codex_published_refund_policy": False,
        "codex_processed_refund": False,
        "tenant_billing_isolated": False,
        "tenant_billing_isolation_enabled": False,
        "tenant_billing_transaction_processed": False,
        "codex_configured_tenant_billing_handling": False,
        "production_billing_enabled": False,
        "production_billing_revenue_ready": False,
        "revenue_validated": False,
        "customer_payment_collected": False,
        "customer_contacted": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready": False,
        "blocker_closure_authorized": False,
        "blockers_closed_by_reconciliation": 0,
        "canonical_gap_matrix_modified": False,
        "canonical_closure_board_modified": False,
        "development_permission_granted": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value!r}")
    require(
        payload.get("status") == "ready_for_human_billing_followup_review_no_closure",
        "status must be review-ready no-closure",
    )
    require(
        payload.get("target_blocker_ids")
        == [
            "payment_provider",
            "invoice_process",
            "tax_review",
            "refund_policy",
            "tenant_billing_isolation",
        ],
        "target blockers mismatch",
    )
    require(payload.get("resolved_current_path") == "individual_human_filled_evidence_outputs", "path mismatch")

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [REPORT, BOUNDARY, TOP_DOC, GATE])
    for token in [
        "Billing Follow-up State Reconciliation",
        "payment_provider_configured=false",
        "codex_enabled_checkout=false",
        "invoice_sent_to_customer=false",
        "tax_advisor_contacted=false",
        "refund_policy_published=false",
        "tenant_billing_isolation_enabled=false",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
        "No payment provider configured",
        "No checkout enabled",
        "No invoice sent to a customer",
        "answer: hold_human_billing_followup_review_required_no_payment_no_checkout_no_auto_closure",
    ]:
        require(token in combined, f"docs missing {token}")
    for forbidden in [
        "payment_provider_configured=true",
        "codex_enabled_checkout=true",
        "invoice_sent_to_customer=true",
        "tax_advisor_contacted=true",
        "refund_policy_published=true",
        "tenant_billing_isolation_enabled=true",
        "production_ready=true",
        "customer_validated=true",
        "product_launched=true",
        "private_core_exposed=true",
        "blockers_closed_by_reconciliation=1",
    ]:
        require(forbidden not in combined, f"forbidden claim found {forbidden}")

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for token in [
        "/phase_b_product/commercial_readiness/BILLING_FOLLOWUP_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_billing_followup_state_reconciliation.py",
        "/scripts/saee_billing_followup_state_reconciliation_smoke.py",
    ]:
        require(token in llms, f"llms.txt missing {token}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("billing_followup_state_reconciliation_v0_1")
    require(isinstance(entry, dict), "agent-index missing billing_followup_state_reconciliation_v0_1")
    for key in [
        "status",
        "target_blocker_ids",
        "resolved_current_path",
        "payment_provider_ready_for_review",
        "invoice_process_ready_for_review",
        "tax_review_ready_for_review",
        "refund_policy_ready_for_review",
        "tenant_billing_isolation_ready_for_review",
        "ready_for_review_count",
        "payment_provider_configured",
        "codex_enabled_checkout",
        "invoice_sent_to_customer",
        "tax_advisor_contacted",
        "refund_policy_published",
        "tenant_billing_isolation_enabled",
        "blockers_closed_by_reconciliation",
        "production_ready",
        "customer_validated",
        "product_launched",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
    ]:
        require(entry.get(key) == payload.get(key), f"agent-index {key} must match")

    status_text = "\n".join(
        (ROOT / name).read_text(encoding="utf-8")
        for name in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]
    )
    for token in [
        "Billing Follow-up State Reconciliation v0.1",
        "payment_provider_ready_for_review=true",
        "invoice_process_ready_for_review=true",
        "tax_review_ready_for_review=true",
        "refund_policy_ready_for_review=true",
        "tenant_billing_isolation_ready_for_review=true",
        "ready_for_review_count=5",
        "blockers_closed_by_reconciliation=0",
        "production_ready=false",
        "customer_validated=false",
    ]:
        require(token in status_text, f"status surfaces missing {token}")

    print(
        "SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION_SMOKE: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
