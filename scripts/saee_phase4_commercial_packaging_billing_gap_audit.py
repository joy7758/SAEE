#!/usr/bin/env python3
"""Audit Phase 4 commercial packaging and billing evidence gaps.

This runner compares Phase 4 pricing, payment-provider, invoice, tax, refund,
and tenant-billing-isolation production evidence requirements against existing
local public-shell billing/revenue evidence. It is a planning and review aid
only: it does not publish pricing, contact payment providers, configure
checkout, collect payments, send invoices, contact tax or legal advisors,
close blockers, or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from scripts.saee_commercial_review_semantics import local_public_shell_go_no_go_summary


BILLING_REVENUE_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence.local.json"
)
DEPENDENCY_PLAN_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
)
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_4_commercial_packaging_billing_gap_audit"
)
OUTPUT_JSON = OUTPUT_DIR / "phase_4_commercial_packaging_billing_gap_audit.local.json"
OUTPUT_MD = OUTPUT_DIR / "phase_4_commercial_packaging_billing_gap_audit.md"
OUTPUT_CSV = OUTPUT_DIR / "phase_4_commercial_packaging_billing_gap_audit.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_4_COMMERCIAL_PACKAGING_BILLING_GAP_AUDIT_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_4_COMMERCIAL_PACKAGING_BILLING_GAP_AUDIT_RECOMMENDATION_GATE.md"
)


LOCAL_PROFILE_ENV = {
    "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": "phase_b_product/commercial_readiness/auth_evidence/auth_evidence.local.json",
    "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": "phase_b_product/commercial_readiness/support_evidence/support_evidence.local.json",
    "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/data_operations_evidence/data_operations_evidence.local.json",
    "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": "phase_b_product/commercial_readiness/operations_evidence/operations_evidence.local.json",
    "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json",
    "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(
        BILLING_REVENUE_EVIDENCE_PATH.relative_to(ROOT)
    ),
    "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
    "SAEE_PRODUCTION_CUSTOMER_VALIDATION_EVIDENCE_PATH": "phase_b_product/commercial_readiness/customer_validation_evidence/customer_validation_evidence.local.json",
}


PHASE_ID = "phase_4_commercial_packaging_and_billing"
TARGET_BLOCKERS = [
    "pricing_page",
    "payment_provider",
    "invoice_process",
    "tax_review",
    "refund_policy",
    "tenant_billing_isolation",
]


REQUIRED_EVIDENCE_ITEMS: list[dict[str, str]] = [
    {
        "blocker_id": "pricing_page",
        "evidence_key": "human_approved_pricing_page_copy",
    },
    {
        "blocker_id": "pricing_page",
        "evidence_key": "approved_plan_and_usage_terms",
    },
    {
        "blocker_id": "pricing_page",
        "evidence_key": "legal_review_completed",
    },
    {
        "blocker_id": "pricing_page",
        "evidence_key": "production_readiness_non_claim_reviewed",
    },
    {
        "blocker_id": "pricing_page",
        "evidence_key": "pricing_page_publication_approval_recorded",
    },
    {
        "blocker_id": "payment_provider",
        "evidence_key": "payment_provider_selected",
    },
    {
        "blocker_id": "payment_provider",
        "evidence_key": "test_mode_configuration_reviewed",
    },
    {
        "blocker_id": "payment_provider",
        "evidence_key": "checkout_enablement_approval_required",
    },
    {
        "blocker_id": "payment_provider",
        "evidence_key": "webhook_signature_validation_tested",
    },
    {
        "blocker_id": "payment_provider",
        "evidence_key": "payment_event_redaction_reviewed",
    },
    {
        "blocker_id": "payment_provider",
        "evidence_key": "security_review_completed",
    },
    {
        "blocker_id": "invoice_process",
        "evidence_key": "invoice_owner_named",
    },
    {
        "blocker_id": "invoice_process",
        "evidence_key": "invoice_workflow_approved",
    },
    {
        "blocker_id": "invoice_process",
        "evidence_key": "contract_handoff_defined",
    },
    {
        "blocker_id": "invoice_process",
        "evidence_key": "payment_reconciliation_tested",
    },
    {
        "blocker_id": "invoice_process",
        "evidence_key": "billing_support_handoff_defined",
    },
    {
        "blocker_id": "invoice_process",
        "evidence_key": "bookkeeping_review_completed",
    },
    {
        "blocker_id": "tax_review",
        "evidence_key": "target_jurisdictions_reviewed",
    },
    {
        "blocker_id": "tax_review",
        "evidence_key": "tax_obligations_reviewed",
    },
    {
        "blocker_id": "tax_review",
        "evidence_key": "invoice_wording_approved",
    },
    {
        "blocker_id": "tax_review",
        "evidence_key": "currency_policy_approved",
    },
    {
        "blocker_id": "tax_review",
        "evidence_key": "tax_collection_approval_recorded",
    },
    {
        "blocker_id": "refund_policy",
        "evidence_key": "refund_policy_approved",
    },
    {
        "blocker_id": "refund_policy",
        "evidence_key": "cancellation_process_approved",
    },
    {
        "blocker_id": "refund_policy",
        "evidence_key": "trial_conversion_policy_approved",
    },
    {
        "blocker_id": "refund_policy",
        "evidence_key": "service_failure_remedy_boundary_approved",
    },
    {
        "blocker_id": "refund_policy",
        "evidence_key": "support_escalation_route_defined",
    },
    {
        "blocker_id": "tenant_billing_isolation",
        "evidence_key": "tenant_billing_account_model_approved",
    },
    {
        "blocker_id": "tenant_billing_isolation",
        "evidence_key": "tenant_invoice_partitioning_tested",
    },
    {
        "blocker_id": "tenant_billing_isolation",
        "evidence_key": "tenant_payment_event_partitioning_tested",
    },
    {
        "blocker_id": "tenant_billing_isolation",
        "evidence_key": "cross_tenant_billing_access_tests_passed",
    },
    {
        "blocker_id": "tenant_billing_isolation",
        "evidence_key": "billing_audit_metadata_policy_approved",
    },
    {
        "blocker_id": "tenant_billing_isolation",
        "evidence_key": "tenant_billing_retention_policy_approved",
    },
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def phase_blockers(plan: dict[str, Any]) -> list[dict[str, Any]]:
    blockers = [
        blocker
        for blocker in plan.get("blockers", [])
        if blocker.get("phase_id") == PHASE_ID
    ]
    blocker_ids = [blocker["blocker_id"] for blocker in blockers]
    if blocker_ids != TARGET_BLOCKERS:
        raise SystemExit(
            "SAEE_PHASE4_COMMERCIAL_PACKAGING_BILLING_GAP_AUDIT: FAIL "
            f"unexpected phase blockers {blocker_ids}"
        )
    return blockers


def blocker_map(blockers: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {blocker["blocker_id"]: blocker for blocker in blockers}


def classify_item(local_value: bool) -> str:
    if local_value:
        return "local_public_shell_evidence_present_requires_human_production_approval"
    return "missing_external_or_human_production_evidence"


def build_gap_rows(
    billing: dict[str, Any],
    blockers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_blocker = blocker_map(blockers)
    rows: list[dict[str, Any]] = []
    for item in REQUIRED_EVIDENCE_ITEMS:
        local_value = billing.get(item["evidence_key"]) is True
        blocker = by_blocker[item["blocker_id"]]
        rows.append(
            {
                "blocker_id": item["blocker_id"],
                "evidence_file_type": "production_billing_revenue_evidence",
                "evidence_key": item["evidence_key"],
                "local_public_shell_value": local_value,
                "accepted_for_blocker_closure": False,
                "gap_status": classify_item(local_value),
                "external_dependency_required": blocker.get(
                    "external_dependency_required"
                )
                is True,
                "engineering_implementation_required": blocker.get(
                    "engineering_implementation_required"
                )
                is True,
                "human_review_required": True,
                "notes": (
                    "Local evidence is review input only; it does not close the production blocker."
                    if local_value
                    else "Production-grade external, engineering, or human-approved evidence is still missing."
                ),
            }
        )
    return rows


def summarize_by_blocker(
    rows: list[dict[str, Any]], blockers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    by_blocker = blocker_map(blockers)
    summary: list[dict[str, Any]] = []
    for blocker_id in TARGET_BLOCKERS:
        subset = [row for row in rows if row["blocker_id"] == blocker_id]
        local_present = sum(1 for row in subset if row["local_public_shell_value"])
        missing = len(subset) - local_present
        blocker = by_blocker[blocker_id]
        summary.append(
            {
                "blocker_id": blocker_id,
                "required_items": len(subset),
                "local_public_shell_present": local_present,
                "missing_production_evidence": missing,
                "ready_to_close": False,
                "external_dependency_required": blocker.get(
                    "external_dependency_required"
                )
                is True,
                "engineering_implementation_required": blocker.get(
                    "engineering_implementation_required"
                )
                is True,
                "next_action": (
                    "Human owners must provide approved commercial, finance, legal, "
                    "payment, tax, refund, and tenant-billing evidence before this "
                    "blocker can close."
                ),
            }
        )
    return summary


def csv_text(rows: list[dict[str, Any]]) -> str:
    output = StringIO()
    fieldnames = [
        "blocker_id",
        "evidence_file_type",
        "evidence_key",
        "local_public_shell_value",
        "accepted_for_blocker_closure",
        "gap_status",
        "external_dependency_required",
        "engineering_implementation_required",
        "human_review_required",
        "notes",
    ]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()


def build_audit() -> dict[str, Any]:
    billing = read_json(BILLING_REVENUE_EVIDENCE_PATH)
    plan = read_json(DEPENDENCY_PLAN_PATH)
    blockers = phase_blockers(plan)
    default_go_no_go = evaluate_commercial_go_no_go(load_settings({}))
    local_profile_go_no_go = evaluate_commercial_go_no_go(load_settings(LOCAL_PROFILE_ENV))
    rows = build_gap_rows(billing, blockers)
    blocker_summary = summarize_by_blocker(rows, blockers)
    local_present = sum(1 for row in rows if row["local_public_shell_value"])
    missing = len(rows) - local_present

    return {
        "audit_type": "saee_phase_4_commercial_packaging_billing_gap_audit",
        "audit_version": "v0.1",
        "audit_scope": "local_public_shell_to_production_commercial_packaging_billing_gap_review",
        "phase_id": PHASE_ID,
        "generated_by": "scripts/saee_phase4_commercial_packaging_billing_gap_audit.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_dependency_plan": str(DEPENDENCY_PLAN_PATH.relative_to(ROOT)),
        "source_billing_revenue_evidence": str(
            BILLING_REVENUE_EVIDENCE_PATH.relative_to(ROOT)
        ),
        "target_blockers": [blocker["blocker_id"] for blocker in blockers],
        "target_blocker_count": len(blockers),
        "required_evidence_item_count": len(rows),
        "local_public_shell_present_count": local_present,
        "missing_production_evidence_count": missing,
        "accepted_for_blocker_closure_count": 0,
        "blockers_ready_to_close": [],
        "blockers_closed_by_audit": 0,
        "default_go_no_go": {
            "commercial_status": default_go_no_go["commercial_status"],
            "production_launch_status": default_go_no_go["production_launch_status"],
            "satisfied_production_checks": default_go_no_go[
                "satisfied_production_checks"
            ],
            "production_blocker_count": default_go_no_go["production_blocker_count"],
            "total_production_checks": default_go_no_go["total_production_checks"],
        },
        "local_profile_go_no_go": local_public_shell_go_no_go_summary(local_profile_go_no_go),
        "blocker_summary": blocker_summary,
        "gap_rows": rows,
        "human_review_required": True,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "pricing_page_published": False,
        "pricing_page_publication_approval_recorded": False,
        "sales_offer_sent": False,
        "payment_provider_contacted_by_codex": False,
        "payment_provider_selected": False,
        "payment_provider_configured": False,
        "payment_provider_live_mode_enabled": False,
        "checkout_enabled": False,
        "payment_link_created": False,
        "customer_payment_collected": False,
        "invoice_sent_to_customer": False,
        "invoice_process_ready": False,
        "tax_advisor_contacted_by_codex": False,
        "tax_review_completed": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "tenant_billing_isolated": False,
        "production_billing_enabled": False,
        "billing_operations_ready": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
        "paid_product_launched": False,
        "enterprise_contract_signed": False,
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
        "next_action": (
            "Human owners must provide approved pricing, payment-provider, invoice, "
            "tax, refund, and tenant-billing-isolation evidence before any Phase 4 "
            "blocker can close."
        ),
    }


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Phase 4 Commercial Packaging/Billing Gap Audit

Status: local gap audit only; no blocker closure.

This directory compares Phase 4 pricing, payment-provider, invoice, tax,
refund, and tenant-billing-isolation evidence requirements against existing
local public-shell billing/revenue evidence. It is a commercial-readiness
review surface, not an execution task.

Boundary:

- no pricing page published
- no sales offer sent
- no payment provider contacted or configured by Codex
- no checkout enabled
- no payment link created
- no customer payment collected
- no invoice sent to a customer
- no tax advisor contacted
- no refund policy published
- no tenant billing isolation claimed
- no blocker closure
- no production-ready claim
- no backend, runtime, kernel, API schema, or private core modification
""",
        encoding="utf-8",
    )


def markdown_report(audit: dict[str, Any]) -> str:
    lines = [
        "# SAEE Phase 4 Commercial Packaging/Billing Gap Audit v0.1",
        "",
        "Status: local public-shell gap audit only; no blocker closure.",
        "",
        "This audit compares Phase 4 production evidence requirements against",
        "existing local billing/revenue evidence. Local evidence may support",
        "human review, but it is not accepted as production blocker closure by",
        "this audit.",
        "",
        "## Summary",
        "",
        f"- required_evidence_item_count: {audit['required_evidence_item_count']}",
        f"- local_public_shell_present_count: {audit['local_public_shell_present_count']}",
        f"- missing_production_evidence_count: {audit['missing_production_evidence_count']}",
        f"- accepted_for_blocker_closure_count: {audit['accepted_for_blocker_closure_count']}",
        f"- blockers_closed_by_audit: {audit['blockers_closed_by_audit']}",
        f"- default_go_no_go: {audit['default_go_no_go']['satisfied_production_checks']}/{audit['default_go_no_go']['total_production_checks']} satisfied",
        f"- local_profile_go_no_go: {audit['local_profile_go_no_go']['satisfied_production_checks']}/{audit['local_profile_go_no_go']['total_production_checks']} satisfied",
        f"- local_public_shell_review_candidate_count: {audit['local_profile_go_no_go']['local_public_shell_review_candidate_count']}",
        f"- production_ready: {str(audit['production_ready']).lower()}",
        f"- customer_validated: {str(audit['customer_validated']).lower()}",
        f"- product_launched: {str(audit['product_launched']).lower()}",
        f"- revenue_validated: {str(audit['revenue_validated']).lower()}",
        f"- private_core_exposed: {str(audit['private_core_exposed']).lower()}",
        "",
        "## Blocker Summary",
        "",
        "| Blocker | Required items | Local public-shell present | Missing production evidence | Ready to close | External dependency | Engineering implementation |",
        "| --- | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in audit["blocker_summary"]:
        lines.append(
            "| {blocker_id} | {required_items} | {local_public_shell_present} | {missing_production_evidence} | {ready} | {external} | {engineering} |".format(
                blocker_id=row["blocker_id"],
                required_items=row["required_items"],
                local_public_shell_present=row["local_public_shell_present"],
                missing_production_evidence=row["missing_production_evidence"],
                ready=str(row["ready_to_close"]).lower(),
                external=str(row["external_dependency_required"]).lower(),
                engineering=str(row["engineering_implementation_required"]).lower(),
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this audit.",
            "- No pricing page is published.",
            "- No sales offer is sent.",
            "- No payment provider is contacted or configured by Codex.",
            "- No checkout path or payment link is enabled.",
            "- No customer payment is collected.",
            "- No invoice is sent to a customer.",
            "- No tax advisor is contacted.",
            "- No refund policy is published.",
            "- No tenant billing isolation is claimed.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No product launch is authorized.",
            "- No private core is exposed.",
            "",
        ]
    )
    return "\n".join(lines)


def write_doc() -> None:
    DOC_PATH.write_text(
        """# SAEE Phase 4 Commercial Packaging/Billing Gap Audit v0.1

phase_4_commercial_packaging_billing_gap_audit_v0_1: true
audit_scope: local_public_shell_to_production_commercial_packaging_billing_gap_review
required_evidence_item_count: 33
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_contacted_by_codex: false
payment_provider_configured: false
checkout_enabled: false
payment_link_created: false
customer_payment_collected: false
invoice_sent_to_customer: false
tax_advisor_contacted_by_codex: false
tax_collection_started: false
refund_policy_published: false
tenant_billing_isolated: false
production_billing_enabled: false
revenue_validated: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This audit compares Phase 4 pricing, payment-provider, invoice, tax, refund,
and tenant-billing-isolation production evidence requirements against existing
local public-shell billing/revenue evidence. It records which evidence keys are
locally present and which still need external, engineering, or human production
approval.

It is an audit only. It does not authorize execution, close blockers, publish a
pricing page, contact a payment provider, configure checkout, collect payments,
send invoices, contact tax advisors, publish refund policy, claim tenant billing
isolation, validate revenue, or claim production readiness.

## Target Blockers

- pricing_page
- payment_provider
- invoice_process
- tax_review
- refund_policy
- tenant_billing_isolation
""",
        encoding="utf-8",
    )


def write_gate() -> None:
    GATE_PATH.write_text(
        """# SAEE Phase 4 Commercial Packaging/Billing Gap Audit Recommendation Gate

answer: conditional
recommend_for_human_review: true
recommend_for_blocker_closure: false
recommend_for_execution_authorization: false
recommend_for_pricing_publication: false
recommend_for_payment_provider_configuration: false
recommend_for_checkout_enablement: false
recommend_for_invoice_sending: false
recommend_for_tax_collection: false
recommend_for_refund_policy_publication: false
recommend_for_tenant_billing_isolation_claim: false
recommend_for_revenue_validation_claim: false
recommend_for_production_launch: false

## Reason

This audit is useful because it separates local public-shell billing/revenue
review packets from production-grade pricing, payment-provider, invoice, tax,
refund, and tenant-billing-isolation evidence. It does not close any blocker or
authorize any commercial action.

## Boundary

```yaml
audit_scope: local_public_shell_to_production_commercial_packaging_billing_gap_review
accepted_for_blocker_closure_count: 0
blockers_closed_by_audit: 0
execution_authorized: false
evidence_collection_authorized: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_contacted_by_codex: false
payment_provider_configured: false
checkout_enabled: false
payment_link_created: false
customer_payment_collected: false
invoice_sent_to_customer: false
tax_advisor_contacted_by_codex: false
tax_collection_started: false
refund_policy_published: false
tenant_billing_isolated: false
production_billing_enabled: false
revenue_validated: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Next Action

Human reviewers may use the gap table to decide whether to authorize a
separate production evidence collection task. Until then, all Phase 4 blockers
remain open.
""",
        encoding="utf-8",
    )


def write_outputs(audit: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(
        json.dumps(audit, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    OUTPUT_MD.write_text(markdown_report(audit), encoding="utf-8")
    OUTPUT_CSV.write_text(csv_text(audit["gap_rows"]), encoding="utf-8")
    write_readme()
    write_doc()
    write_gate()


def main() -> None:
    audit = build_audit()
    write_outputs(audit)
    print(
        "SAEE_PHASE4_COMMERCIAL_PACKAGING_BILLING_GAP_AUDIT: PASS "
        f"required_items={audit['required_evidence_item_count']} "
        f"local_present={audit['local_public_shell_present_count']} "
        f"missing_production={audit['missing_production_evidence_count']} "
        f"blockers_closed_by_audit={audit['blockers_closed_by_audit']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
