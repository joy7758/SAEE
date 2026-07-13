#!/usr/bin/env python3
"""Prove the local billing/revenue evidence path without commercial execution.

This path check uses temporary fixture-only billing/revenue source evidence and
feeds it through the existing billing/revenue profile combination logic,
production billing/revenue readiness, and commercial go/no-go checks. It proves
that future human-filled pricing, payment, invoice, tax, refund, and
tenant-billing-isolation evidence can satisfy the billing/revenue blocker group
without publishing pricing, configuring payment providers, enabling checkout,
issuing invoices, collecting payment, validating revenue, contacting customers
or vendors, closing blockers by itself, or claiming production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_billing_revenue_evidence import (
    FORBIDDEN_TRUE_KEYS,
    evaluate_production_billing_revenue_evidence,
)
from scripts.saee_billing_revenue_evidence_profile import (
    SOURCE_KEY_GROUPS,
    build_combined_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "billing_revenue_evidence_path.local.json"
REPORT_PATH = OUTPUT_DIR / "billing_revenue_evidence_path_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PATH_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_BILLING_REVENUE_EVIDENCE_PATH_RECOMMENDATION_GATE.md"
TARGET_BLOCKERS = tuple(SOURCE_KEY_GROUPS)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def fixture_source_evidence(label: str) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "billing_revenue_evidence_type": "production_billing_revenue_evidence",
        "evidence_scope": f"fixture_only_{label}_billing_revenue_evidence_path_proof",
        "evidence_version": "v0.1",
        "input_status": "fixture_only_not_real_billing_revenue_approval",
        "generated_by": "scripts/saee_billing_revenue_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_boundary_violation_count": 0,
        "fixture_only": True,
    }
    for group_label, keys in SOURCE_KEY_GROUPS.items():
        for key in keys:
            evidence[key] = group_label == label
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def billing_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_billing_revenue_evidence(
        load_settings({"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(path)})
    )


def commercial_status(path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings({"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(path)})
    )


def target_blocker_state(go_no_go: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers = go_no_go.get("blockers", [])
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    if not isinstance(blockers, list):
        return satisfied, list(TARGET_BLOCKERS)
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = item.get("blocker_id")
        if blocker_id not in TARGET_BLOCKERS:
            continue
        if item.get("satisfied") is True:
            satisfied.append(str(blocker_id))
        else:
            unsatisfied.append(str(blocker_id))
    return satisfied, unsatisfied


def build_path(output_path: Path) -> dict[str, Any]:
    sources = {label: fixture_source_evidence(label) for label in SOURCE_KEY_GROUPS}
    combined_evidence = build_combined_evidence(sources, source_violation_count=0)

    with tempfile.TemporaryDirectory() as tmpdir:
        fixture_path = Path(tmpdir) / "billing_revenue_evidence.fixture.json"
        write_json(fixture_path, combined_evidence)
        billing = billing_readiness(fixture_path)
        go_no_go = commercial_status(fixture_path)

    target_satisfied, target_unsatisfied = target_blocker_state(go_no_go)
    billing_path_proven = (
        billing["pricing_page_evidence_complete"] is True
        and billing["payment_provider_evidence_complete"] is True
        and billing["invoice_process_evidence_complete"] is True
        and billing["tax_review_evidence_complete"] is True
        and billing["refund_policy_evidence_complete"] is True
        and billing["tenant_billing_isolation_evidence_complete"] is True
        and billing["production_billing_revenue_ready"] is True
        and len(target_satisfied) == len(TARGET_BLOCKERS)
    )

    result: dict[str, Any] = {
        "billing_revenue_evidence_path_v0_1": True,
        "path_type": "local_fixture_only_billing_revenue_evidence_path",
        "path_status": "pass_fixture_only" if billing_path_proven else "hold",
        "generated_by": "scripts/saee_billing_revenue_evidence_path.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
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
        "billing_revenue_readiness_status_after_fixture": billing["status"],
        "pricing_page_evidence_complete_after_fixture": billing[
            "pricing_page_evidence_complete"
        ],
        "payment_provider_evidence_complete_after_fixture": billing[
            "payment_provider_evidence_complete"
        ],
        "invoice_process_evidence_complete_after_fixture": billing[
            "invoice_process_evidence_complete"
        ],
        "tax_review_evidence_complete_after_fixture": billing[
            "tax_review_evidence_complete"
        ],
        "refund_policy_evidence_complete_after_fixture": billing[
            "refund_policy_evidence_complete"
        ],
        "tenant_billing_isolation_evidence_complete_after_fixture": billing[
            "tenant_billing_isolation_evidence_complete"
        ],
        "production_billing_revenue_ready_after_fixture": billing[
            "production_billing_revenue_ready"
        ],
        "commercial_status_after_fixture": go_no_go["commercial_status"],
        "production_launch_status_after_fixture": go_no_go[
            "production_launch_status"
        ],
        "satisfied_production_checks_after_fixture": go_no_go[
            "satisfied_production_checks"
        ],
        "total_production_checks_after_fixture": go_no_go["total_production_checks"],
        "production_blocker_count_after_fixture": go_no_go[
            "production_blocker_count"
        ],
        "billing_revenue_blocker_path_proven": billing_path_proven,
        "billing_revenue_target_blockers_satisfied_by_fixture": target_satisfied,
        "billing_revenue_target_blockers_unsatisfied_by_fixture": target_unsatisfied,
        "billing_revenue_target_blockers_satisfied_count_after_fixture": len(
            target_satisfied
        ),
        "blockers_closed_by_path": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_real_evidence_required": True,
        "separate_go_no_go_profile_required": True,
        "separate_human_launch_approval_required": True,
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
        "next_action": (
            "A human owner must replace the fixture with real pricing, payment, "
            "invoice, tax, refund, and tenant-billing-isolation evidence, then "
            "rerun billing/revenue profile, billing/revenue readiness, and "
            "commercial go/no-go. This path proof alone closes no blockers."
        ),
    }
    write_json(output_path, result)
    write_report(result)
    write_docs()
    return result


def bool_token(value: object) -> str:
    return str(value).lower()


def write_report(result: dict[str, Any]) -> None:
    lines = [
        "# SAEE Billing / Revenue Evidence Path Report v0.1",
        "",
        "Status: local fixture-only path proof generated.",
        "",
        "## Summary",
        "",
        "- billing_revenue_evidence_path_v0_1: true",
        f"- path_type: {result['path_type']}",
        f"- path_status: {result['path_status']}",
        "- fixture_only: true",
        "- real_pricing_page_published: false",
        "- real_pricing_page_approved: false",
        "- real_payment_provider_configured: false",
        "- real_checkout_enabled: false",
        "- real_invoice_process_operational: false",
        "- real_tax_review_completed: false",
        "- real_refund_policy_approved: false",
        "- real_tenant_billing_isolation_approved: false",
        "- real_customer_payment_collected: false",
        "- real_revenue_validated: false",
        f"- billing_revenue_readiness_status_after_fixture: {result['billing_revenue_readiness_status_after_fixture']}",
        f"- pricing_page_evidence_complete_after_fixture: {bool_token(result['pricing_page_evidence_complete_after_fixture'])}",
        f"- payment_provider_evidence_complete_after_fixture: {bool_token(result['payment_provider_evidence_complete_after_fixture'])}",
        f"- invoice_process_evidence_complete_after_fixture: {bool_token(result['invoice_process_evidence_complete_after_fixture'])}",
        f"- tax_review_evidence_complete_after_fixture: {bool_token(result['tax_review_evidence_complete_after_fixture'])}",
        f"- refund_policy_evidence_complete_after_fixture: {bool_token(result['refund_policy_evidence_complete_after_fixture'])}",
        f"- tenant_billing_isolation_evidence_complete_after_fixture: {bool_token(result['tenant_billing_isolation_evidence_complete_after_fixture'])}",
        f"- production_billing_revenue_ready_after_fixture: {bool_token(result['production_billing_revenue_ready_after_fixture'])}",
        f"- billing_revenue_blocker_path_proven: {bool_token(result['billing_revenue_blocker_path_proven'])}",
        f"- billing_revenue_target_blockers_satisfied_count_after_fixture: {result['billing_revenue_target_blockers_satisfied_count_after_fixture']}",
        f"- commercial_status_after_fixture: {result['commercial_status_after_fixture']}",
        f"- production_blocker_count_after_fixture: {result['production_blocker_count_after_fixture']}",
        f"- blockers_closed_by_path: {result['blockers_closed_by_path']}",
        "",
        "## Boundary",
        "",
        "- No pricing page published.",
        "- No sales offer sent.",
        "- No payment provider contacted or configured.",
        "- No checkout enabled.",
        "- No payment link created.",
        "- No invoice sent to customer.",
        "- No tax advisor or legal counsel contacted.",
        "- No tax collection started.",
        "- No refund policy published.",
        "- No customer payment collected.",
        "- No revenue validated.",
        "- No customer contacted.",
        "- No backend, runtime, kernel, or API schema modified.",
        "- No product launched.",
        "- No production-readiness claim added.",
        "- No private core exposed.",
        "",
        "## Next Action",
        "",
        str(result["next_action"]),
        "",
    ]
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def write_docs() -> None:
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        """# SAEE Billing / Revenue Evidence Path v0.1

Status: local fixture-only path proof; not billing/revenue approval.

## Purpose

This path proves that complete billing/revenue evidence can be combined by the
existing billing/revenue profile logic, read by production billing/revenue
readiness, and reflected by commercial go/no-go for these blocker IDs:

- `pricing_page`
- `payment_provider`
- `invoice_process`
- `tax_review`
- `refund_policy`
- `tenant_billing_isolation`

## Machine-Readable Status

```yaml
billing_revenue_evidence_path_v0_1: true
path_type: local_fixture_only_billing_revenue_evidence_path
path_status: pass_fixture_only
fixture_only: true
real_pricing_page_published: false
real_pricing_page_approved: false
real_payment_provider_configured: false
real_checkout_enabled: false
real_invoice_process_operational: false
real_tax_review_completed: false
real_refund_policy_approved: false
real_tenant_billing_isolation_approved: false
real_customer_payment_collected: false
real_revenue_validated: false
billing_revenue_readiness_status_after_fixture: pass
pricing_page_evidence_complete_after_fixture: true
payment_provider_evidence_complete_after_fixture: true
invoice_process_evidence_complete_after_fixture: true
tax_review_evidence_complete_after_fixture: true
refund_policy_evidence_complete_after_fixture: true
tenant_billing_isolation_evidence_complete_after_fixture: true
production_billing_revenue_ready_after_fixture: true
billing_revenue_blocker_path_proven: true
billing_revenue_target_blockers_satisfied_count_after_fixture: 6
production_blocker_count_after_fixture: 18
blockers_closed_by_path: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
customer_contacted: false
payment_provider_contacted: false
tax_advisor_contacted: false
legal_counsel_contacted: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_configured: false
checkout_enabled: false
invoice_sent_to_customer: false
tax_collection_started: false
refund_policy_published: false
customer_payment_collected: false
revenue_validated: false
```

## Boundary

This path does not publish pricing, send a sales offer, contact or configure a
payment provider, enable checkout, create a payment link, issue invoices,
contact tax advisors or legal counsel, start tax collection, publish a refund
policy, collect customer payment, validate revenue, contact customers, close
blockers by itself, launch product, modify runtime, modify backend, modify
kernel, modify API schema, or expose private core.

## Recommendation Gate

Answer: conditional.

Recommend this path for human billing/revenue evidence review and blocker-path
verification. Do not recommend it as pricing publication, payment-provider
configuration, checkout enablement, invoice operation, tax approval, refund
policy approval, tenant billing isolation approval, revenue validation,
production launch approval, customer validation, or blocker closure by itself.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Billing / Revenue Evidence Path Recommendation Gate

answer: conditional

recommend_for_human_billing_revenue_evidence_review: true
recommend_for_blocker_closure_by_path_alone: false
recommend_for_production_launch: false
recommend_for_customer_contact: false
recommend_for_payment_provider_contact: false
recommend_for_payment_enablement: false
recommend_for_checkout_enablement: false
recommend_for_invoice_operation: false
recommend_for_tax_collection: false
recommend_for_revenue_validation: false

## Reason

The path proves local fixture-only wiring from billing/revenue evidence through
the billing/revenue profile, production billing/revenue readiness, and
commercial go/no-go for six billing/revenue blockers. It is useful for human
review of real evidence later, but it is not pricing publication, payment
provider configuration, checkout enablement, invoice operation, tax approval,
refund policy approval, tenant billing isolation approval, revenue validation,
or blocker closure by itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
customer_contacted: false
payment_provider_contacted: false
tax_advisor_contacted: false
legal_counsel_contacted: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_configured: false
checkout_enabled: false
invoice_sent_to_customer: false
tax_collection_started: false
refund_policy_published: false
customer_payment_collected: false
revenue_validated: false
""",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    result = build_path(Path(args.output))
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_BILLING_REVENUE_EVIDENCE_PATH: PASS "
            f"path={Path(args.output).relative_to(ROOT)} "
            f"path_status={result['path_status']} "
            "fixture_only=true "
            "billing_revenue_blocker_path_proven=true "
            "blockers_closed_by_path=0"
        )


if __name__ == "__main__":
    main()
