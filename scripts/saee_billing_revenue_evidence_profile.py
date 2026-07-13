#!/usr/bin/env python3
"""Build a combined SAEE billing/revenue evidence profile.

This profile combines pricing-page, payment-provider, invoice-process,
tax-review, refund-policy, and tenant-billing-isolation evidence into the
single production billing/revenue evidence file consumed by commercial
go/no-go checks. It does not publish pricing, contact customers or vendors,
configure payment, enable checkout, create invoices, collect payment, validate
revenue, close blockers by itself, modify product behavior, or claim
production readiness.
"""

from __future__ import annotations

import argparse
import json
import sys
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
    INVOICE_PROCESS_KEYS,
    PAYMENT_PROVIDER_KEYS,
    PRICING_PAGE_KEYS,
    REFUND_POLICY_KEYS,
    TAX_REVIEW_KEYS,
    TENANT_BILLING_ISOLATION_KEYS,
    evaluate_production_billing_revenue_evidence,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
DEFAULT_SOURCE_PATHS = {
    "pricing_page": OUTPUT_DIR
    / "production_billing_revenue_evidence.from_pricing_page.local.json",
    "payment_provider": OUTPUT_DIR
    / "production_billing_revenue_evidence.from_payment_provider.local.json",
    "invoice_process": OUTPUT_DIR
    / "production_billing_revenue_evidence.from_invoice_process.local.json",
    "tax_review": OUTPUT_DIR
    / "production_billing_revenue_evidence.from_tax_review.local.json",
    "refund_policy": OUTPUT_DIR
    / "production_billing_revenue_evidence.from_refund_policy.local.json",
    "tenant_billing_isolation": OUTPUT_DIR
    / "production_billing_revenue_evidence.from_tenant_billing_isolation.local.json",
}
SOURCE_KEY_GROUPS = {
    "pricing_page": PRICING_PAGE_KEYS,
    "payment_provider": PAYMENT_PROVIDER_KEYS,
    "invoice_process": INVOICE_PROCESS_KEYS,
    "tax_review": TAX_REVIEW_KEYS,
    "refund_policy": REFUND_POLICY_KEYS,
    "tenant_billing_isolation": TENANT_BILLING_ISOLATION_KEYS,
}
TARGET_BLOCKERS = tuple(SOURCE_KEY_GROUPS)
DEFAULT_PROFILE_JSON = OUTPUT_DIR / "billing_revenue_evidence_profile.local.json"
DEFAULT_COMBINED_EVIDENCE = (
    OUTPUT_DIR / "production_billing_revenue_evidence.combined_profile.local.json"
)
REPORT_PATH = OUTPUT_DIR / "billing_revenue_evidence_profile_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/BILLING_REVENUE_EVIDENCE_PROFILE_V0_1.md"
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_BILLING_REVENUE_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"
)

EXTRA_FORBIDDEN_SOURCE_TRUE_KEYS = (
    "external_model_api_called",
    "external_ai_assistant_tested",
    "codex_inferred_missing_evidence",
    "codex_published_pricing_page",
    "codex_approved_pricing_page",
    "codex_sent_sales_offer",
    "codex_selected_payment_provider",
    "codex_contacted_payment_provider",
    "codex_configured_payment_provider",
    "codex_enabled_checkout",
    "codex_created_payment_link",
    "codex_processed_payment",
    "codex_created_invoice",
    "codex_sent_invoice",
    "codex_signed_contract",
    "codex_performed_reconciliation",
    "codex_completed_tax_review",
    "codex_contacted_tax_advisor",
    "codex_published_refund_policy",
    "codex_approved_refund_policy",
    "codex_configured_tenant_billing",
    "blockers_closed_by_builder",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BILLING_REVENUE_EVIDENCE_PROFILE: FAIL: " + message)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_evidence(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_BILLING_REVENUE_EVIDENCE_PROFILE: FAIL: invalid evidence {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"evidence file must be an object: {path}")
    return data


def source_is_billing_revenue_evidence(data: dict[str, Any]) -> bool:
    return data.get("billing_revenue_evidence_type") == "production_billing_revenue_evidence"


def all_true(data: dict[str, Any], keys: tuple[str, ...]) -> bool:
    return all(data.get(key) is True for key in keys)


def source_boundary_violations(label: str, data: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    if data and not source_is_billing_revenue_evidence(data):
        violations.append(f"{label}.billing_revenue_evidence_type_invalid")
    if int(data.get("source_boundary_violation_count", 0) or 0) > 0:
        violations.append(f"{label}.source_boundary_violation_count")
    for key in FORBIDDEN_TRUE_KEYS + EXTRA_FORBIDDEN_SOURCE_TRUE_KEYS:
        if data.get(key) is True:
            violations.append(f"{label}.{key}")
    return violations


def build_combined_evidence(
    sources: dict[str, dict[str, Any]],
    *,
    source_violation_count: int,
) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "billing_revenue_evidence_type": "production_billing_revenue_evidence",
        "evidence_scope": "combined_billing_revenue_evidence_profile_to_go_no_go",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_billing_revenue_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_boundary_violation_count": source_violation_count,
        "profile_note": (
            "Combined billing/revenue profile. Pricing, payment, invoice, tax, "
            "refund, and tenant-billing evidence remain separately sourced."
        ),
    }
    safe = source_violation_count == 0
    for label, keys in SOURCE_KEY_GROUPS.items():
        source = sources.get(label, {})
        evidence[f"{label}_source_scope"] = source.get("evidence_scope", "")
        for key in keys:
            evidence[key] = safe and source.get(key) is True
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    for key in EXTRA_FORBIDDEN_SOURCE_TRUE_KEYS:
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


def profile_status(readiness: dict[str, object], source_violations: list[str]) -> str:
    if source_violations or readiness["status"] == "stop":
        return "stop"
    if readiness["production_billing_revenue_ready"] is True:
        return "pass"
    return "hold"


def target_blocker_state(go_no_go: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers = go_no_go.get("blockers", [])
    require(isinstance(blockers, list), "go/no-go blockers must be a list")
    satisfied: list[str] = []
    unsatisfied: list[str] = []
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


def build_profile(
    source_paths: dict[str, Path],
    profile_output_path: Path,
    combined_evidence_path: Path,
) -> dict[str, Any]:
    sources = {label: read_evidence(path) for label, path in source_paths.items()}
    source_violations = [
        violation
        for label, data in sources.items()
        for violation in source_boundary_violations(f"{label}_source", data)
    ]
    combined_evidence = build_combined_evidence(
        sources,
        source_violation_count=len(source_violations),
    )
    write_json(combined_evidence_path, combined_evidence)
    readiness = billing_readiness(combined_evidence_path)
    go_no_go = commercial_status(combined_evidence_path)
    target_satisfied, target_unsatisfied = target_blocker_state(go_no_go)
    status = profile_status(readiness, source_violations)

    profile: dict[str, Any] = {
        "billing_revenue_evidence_profile_v0_1": True,
        "profile_type": "saee_billing_revenue_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": "combined_billing_revenue_evidence_profile_to_go_no_go",
        "generated_by": "scripts/saee_billing_revenue_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "profile_output_path": str(profile_output_path),
        "combined_billing_revenue_evidence_path": str(combined_evidence_path),
        "source_paths": {label: str(path) for label, path in source_paths.items()},
        "profile_status": status,
        "source_boundary_violation_count": len(source_violations),
        "source_boundary_violations": source_violations,
        "source_completion": {
            label: all_true(sources.get(label, {}), keys)
            for label, keys in SOURCE_KEY_GROUPS.items()
        },
        "pricing_page_evidence_complete": readiness["pricing_page_evidence_complete"],
        "payment_provider_evidence_complete": readiness[
            "payment_provider_evidence_complete"
        ],
        "invoice_process_evidence_complete": readiness[
            "invoice_process_evidence_complete"
        ],
        "tax_review_evidence_complete": readiness["tax_review_evidence_complete"],
        "refund_policy_evidence_complete": readiness["refund_policy_evidence_complete"],
        "tenant_billing_isolation_evidence_complete": readiness[
            "tenant_billing_isolation_evidence_complete"
        ],
        "production_billing_revenue_ready": readiness["production_billing_revenue_ready"],
        "billing_revenue_readiness_status": readiness["status"],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "profile_satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "profile_total_production_checks": go_no_go["total_production_checks"],
        "profile_production_blocker_count": go_no_go["production_blocker_count"],
        "target_blocker_ids": list(TARGET_BLOCKERS),
        "target_blockers_satisfied": target_satisfied,
        "target_blockers_unsatisfied": target_unsatisfied,
        "target_blockers_satisfied_count": len(target_satisfied),
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_human_launch_approval_required": True,
        "development_permission_granted": False,
        "task_candidates_executed": False,
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
        "pricing_page_published": False,
        "sales_offer_sent": False,
        "payment_provider_contacted": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "invoice_sent_to_customer": False,
        "tax_advisor_contacted": False,
        "legal_counsel_contacted": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "next_action": (
            "Use this profile only after all six billing/revenue evidence sources "
            "are human-filled and reviewed. Even if billing/revenue evidence "
            "passes, all remaining production blockers and separate human launch "
            "approval remain."
        ),
    }
    write_json(profile_output_path, profile)
    write_docs(profile)
    return profile


def render_markdown(profile: dict[str, Any]) -> str:
    source_lines = "\n".join(
        f"- {label}: `{path}`" for label, path in profile["source_paths"].items()
    )
    satisfied = "\n".join(f"- {item}" for item in profile["target_blockers_satisfied"])
    if not satisfied:
        satisfied = "- none"
    return f"""# SAEE Billing / Revenue Evidence Profile v0.1

Status: local combined billing/revenue profile generated; default output is hold.

## Summary

- billing_revenue_evidence_profile_v0_1: true
- profile_scope: {profile['profile_scope']}
- profile_status: {profile['profile_status']}
- pricing_page_evidence_complete: {str(profile['pricing_page_evidence_complete']).lower()}
- payment_provider_evidence_complete: {str(profile['payment_provider_evidence_complete']).lower()}
- invoice_process_evidence_complete: {str(profile['invoice_process_evidence_complete']).lower()}
- tax_review_evidence_complete: {str(profile['tax_review_evidence_complete']).lower()}
- refund_policy_evidence_complete: {str(profile['refund_policy_evidence_complete']).lower()}
- tenant_billing_isolation_evidence_complete: {str(profile['tenant_billing_isolation_evidence_complete']).lower()}
- production_billing_revenue_ready: {str(profile['production_billing_revenue_ready']).lower()}
- commercial_status_after_profile: {profile['commercial_status_after_profile']}
- production_launch_status_after_profile: {profile['production_launch_status_after_profile']}
- profile_satisfied_production_checks: {profile['profile_satisfied_production_checks']}
- profile_total_production_checks: {profile['profile_total_production_checks']}
- profile_production_blocker_count: {profile['profile_production_blocker_count']}
- target_blockers_satisfied_count: {profile['target_blockers_satisfied_count']}
- blockers_closed_by_profile: 0

## What This Profile Combines

{source_lines}

## Satisfied Billing / Revenue Signals

{satisfied}

## Boundary

- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- customer_contacted: false
- pricing_page_published: false
- sales_offer_sent: false
- payment_provider_contacted: false
- payment_provider_configured: false
- checkout_enabled: false
- invoice_sent_to_customer: false
- tax_advisor_contacted: false
- legal_counsel_contacted: false
- tax_collection_started: false
- refund_policy_published: false
- customer_payment_collected: false
- revenue_validated: false

## Non-Closure Statement

This profile feeds current billing/revenue evidence into commercial go/no-go.
It does not publish pricing, configure payment, enable checkout, issue invoices,
collect payment, validate revenue, close blockers by itself, contact customers,
or claim production readiness.
"""


def write_docs(profile: dict[str, Any]) -> None:
    REPORT_PATH.write_text(render_markdown(profile), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Billing / Revenue Evidence Profile v0.1

Status: local combined billing/revenue go/no-go profile; default output is hold.

billing_revenue_evidence_profile_v0_1: true
profile_scope: combined_billing_revenue_evidence_profile_to_go_no_go
default_profile_status: {profile['profile_status']}
pricing_page_evidence_complete: {str(profile['pricing_page_evidence_complete']).lower()}
payment_provider_evidence_complete: {str(profile['payment_provider_evidence_complete']).lower()}
invoice_process_evidence_complete: {str(profile['invoice_process_evidence_complete']).lower()}
tax_review_evidence_complete: {str(profile['tax_review_evidence_complete']).lower()}
refund_policy_evidence_complete: {str(profile['refund_policy_evidence_complete']).lower()}
tenant_billing_isolation_evidence_complete: {str(profile['tenant_billing_isolation_evidence_complete']).lower()}
production_billing_revenue_ready: {str(profile['production_billing_revenue_ready']).lower()}
profile_production_blocker_count: {profile['profile_production_blocker_count']}
blockers_closed_by_profile: 0

## Purpose

This profile is the review layer between six separate billing/revenue evidence
sources and the commercial go/no-go aggregator:

1. pricing-page evidence;
2. payment-provider evidence;
3. invoice-process evidence;
4. tax-review evidence;
5. refund-policy evidence;
6. tenant-billing-isolation evidence.

It produces a single billing/revenue evidence file for go/no-go evaluation
without approving pricing, contacting customers, selecting payment providers,
enabling checkout, issuing invoices, collecting payment, validating revenue, or
changing product behavior.

## Required Design Check

1. Evolution subsystem strengthened: Evolutionary Archive / Rollback Immune
   System.
2. It improves commercial evidence review by combining billing/revenue
   evidence sources into one explicit go/no-go input.
3. It preserves safety, license, supply-chain, permission, customer-data, and
   private-core boundaries.
4. It does not push SAEE into audit-first framing; it is a commercial
   readiness profile around market, billing, and revenue evidence.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_payment_enablement: false
recommend_for_customer_contact: false

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_contacted: false
payment_provider_configured: false
checkout_enabled: false
invoice_sent_to_customer: false
tax_advisor_contacted: false
legal_counsel_contacted: false
tax_collection_started: false
refund_policy_published: false
customer_payment_collected: false
revenue_validated: false

## Entrypoints

- profile JSON: `phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_profile.local.json`
- combined evidence JSON: `phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.combined_profile.local.json`
- report: `phase_b_product/commercial_readiness/billing_revenue_evidence/billing_revenue_evidence_profile_report.md`
- runner: `scripts/saee_billing_revenue_evidence_profile.py`
- smoke: `scripts/saee_billing_revenue_evidence_profile_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Billing / Revenue Evidence Profile Recommendation Gate

answer: conditional

recommend_for_human_go_no_go_review: true
recommend_for_blocker_closure_by_profile_alone: false
recommend_for_production_launch: false
recommend_for_payment_enablement: false
recommend_for_customer_contact: false
recommend_for_external_execution: false

## Reason

The profile is useful because commercial go/no-go accepts one billing/revenue
evidence path. This profile combines pricing, payment, invoice, tax, refund,
and tenant-billing evidence into that one path. It does not create any evidence
source, approve pricing, select a provider, enable checkout, contact customers,
or close blockers by itself.

## Boundary

production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
pricing_page_published: false
sales_offer_sent: false
payment_provider_contacted: false
payment_provider_configured: false
checkout_enabled: false
invoice_sent_to_customer: false
tax_advisor_contacted: false
legal_counsel_contacted: false
tax_collection_started: false
refund_policy_published: false
customer_payment_collected: false
revenue_validated: false
blockers_closed_by_profile: 0
""",
        encoding="utf-8",
    )


def parse_source_paths(args: argparse.Namespace) -> dict[str, Path]:
    return {
        "pricing_page": Path(args.pricing_page_evidence).expanduser(),
        "payment_provider": Path(args.payment_provider_evidence).expanduser(),
        "invoice_process": Path(args.invoice_process_evidence).expanduser(),
        "tax_review": Path(args.tax_review_evidence).expanduser(),
        "refund_policy": Path(args.refund_policy_evidence).expanduser(),
        "tenant_billing_isolation": Path(args.tenant_billing_isolation_evidence).expanduser(),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pricing-page-evidence", default=str(DEFAULT_SOURCE_PATHS["pricing_page"]))
    parser.add_argument("--payment-provider-evidence", default=str(DEFAULT_SOURCE_PATHS["payment_provider"]))
    parser.add_argument("--invoice-process-evidence", default=str(DEFAULT_SOURCE_PATHS["invoice_process"]))
    parser.add_argument("--tax-review-evidence", default=str(DEFAULT_SOURCE_PATHS["tax_review"]))
    parser.add_argument("--refund-policy-evidence", default=str(DEFAULT_SOURCE_PATHS["refund_policy"]))
    parser.add_argument(
        "--tenant-billing-isolation-evidence",
        default=str(DEFAULT_SOURCE_PATHS["tenant_billing_isolation"]),
    )
    parser.add_argument("--profile-output", default=str(DEFAULT_PROFILE_JSON))
    parser.add_argument("--combined-output", default=str(DEFAULT_COMBINED_EVIDENCE))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    profile = build_profile(
        parse_source_paths(args),
        Path(args.profile_output).expanduser(),
        Path(args.combined_output).expanduser(),
    )
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_BILLING_REVENUE_EVIDENCE_PROFILE: PASS "
            f"profile_status={profile['profile_status']} "
            f"production_billing_revenue_ready={str(profile['production_billing_revenue_ready']).lower()} "
            f"target_blockers_satisfied={profile['target_blockers_satisfied_count']} "
            f"production_blockers={profile['profile_production_blocker_count']} "
            "blockers_closed_by_profile=0"
        )


if __name__ == "__main__":
    main()
