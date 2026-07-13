#!/usr/bin/env python3
"""Build pricing-page evidence from human-filled review input.

This builder converts local, human-filled pricing-page evidence into the
production billing/revenue evidence shape consumed by commercial readiness
checks. It does not approve pricing copy, publish a pricing page, create a
sales offer, configure payment providers, enable checkout, collect payment,
validate revenue, close blockers, modify product behavior, or claim production
readiness.
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
DEFAULT_INPUT_PATH = OUTPUT_DIR / "pricing_page_evidence_input.template.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "pricing_page_evidence_builder_output.local.json"
DEFAULT_BILLING_REVENUE_OUTPUT_PATH = (
    OUTPUT_DIR / "production_billing_revenue_evidence.from_pricing_page.local.json"
)
REPORT_PATH = OUTPUT_DIR / "pricing_page_evidence_builder_report.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/PRICING_PAGE_EVIDENCE_BUILDER_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PRICING_PAGE_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"

TARGET_KEYS = PRICING_PAGE_KEYS
INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(FORBIDDEN_TRUE_KEYS)
        | {
            "human_approved_pricing_page_copy",
            "approved_plan_and_usage_terms",
            "legal_review_completed",
            "production_readiness_non_claim_reviewed",
            "pricing_page_publication_approval_recorded",
            "pricing_page_available",
            "pricing_page_approved",
            "public_price_points_approved",
            "customer_facing_pricing_page_created",
            "sales_offer_generated",
            "sales_offer_sent",
            "pricing_page_claim_published",
            "pricing_page_completed_by_codex",
            "pricing_page_execution_authorized",
            "codex_published_pricing_page",
            "codex_approved_pricing_page",
            "codex_sent_sales_offer",
            "codex_inferred_missing_evidence",
            "blockers_closed_by_builder",
        }
    )
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PRICING_PAGE_EVIDENCE_BUILDER: FAIL: " + message)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_pricing_page_evidence_input",
        "template_version": "v0.1",
        "input_status": "template_pending_human_input",
        "human_reviewer_name": "",
        "review_date": "",
        "commercial_owner": "",
        "product_owner": "",
        "accounting_owner": "",
        "legal_owner": "",
        "billing_owner": "",
        "review_record_reference": "",
        "decision_summary": "",
        "evidence_review": {key: False for key in TARGET_KEYS},
        "source_notes_by_key": {key: "" for key in TARGET_KEYS},
        "review_artifacts": [
            {
                "evidence_key": key,
                "artifact_reference": "",
                "reviewed_by_human": False,
                "owner_named": False,
                "human_source_note": "",
            }
            for key in TARGET_KEYS
        ],
        "boundary_review": {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS},
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
        "pricing_page_published": False,
        "production_billing_enabled": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
        "human_approved_pricing_page_copy": False,
        "approved_plan_and_usage_terms": False,
        "legal_review_completed": False,
        "production_readiness_non_claim_reviewed": False,
        "pricing_page_publication_approval_recorded": False,
        "pricing_page_available": False,
        "pricing_page_approved": False,
        "public_price_points_approved": False,
        "customer_facing_pricing_page_created": False,
        "sales_offer_generated": False,
        "pricing_page_claim_published": False,
        "pricing_page_completed_by_codex": False,
        "pricing_page_execution_authorized": False,
        "codex_published_pricing_page": False,
        "codex_approved_pricing_page": False,
        "codex_sent_sales_offer": False,
        "codex_inferred_missing_evidence": False,
        "blockers_closed_by_builder": False,
    }


def ensure_default_template(path: Path) -> None:
    if not path.exists():
        write_json(path, default_input_template())


def read_json(path: Path) -> dict[str, Any]:
    ensure_default_template(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PRICING_PAGE_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in TARGET_KEYS}


def source_notes(data: dict[str, Any]) -> dict[str, str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return {}
    return {key: str(notes.get(key, "")).strip() for key in TARGET_KEYS}


def completed_artifacts(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    artifacts = data.get("review_artifacts", [])
    if not isinstance(artifacts, list):
        return {}
    completed: dict[str, dict[str, Any]] = {}
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        key = str(artifact.get("evidence_key", "")).strip()
        if key not in TARGET_KEYS:
            continue
        if (
            str(artifact.get("artifact_reference", "")).strip()
            and artifact.get("reviewed_by_human") is True
            and artifact.get("owner_named") is True
            and str(artifact.get("human_source_note", "")).strip()
        ):
            completed[key] = artifact
    return completed


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations = [key for key in INPUT_FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    boundary = data.get("boundary_review", {})
    if not isinstance(boundary, dict):
        violations.append("boundary_review_missing")
        return violations
    for key in INPUT_FORBIDDEN_TRUE_KEYS:
        if boundary.get(key) is True:
            violations.append(f"boundary_review.{key}")
    return violations


def input_metadata_complete(data: dict[str, Any]) -> bool:
    fields = (
        "human_reviewer_name",
        "review_date",
        "commercial_owner",
        "product_owner",
        "accounting_owner",
        "legal_owner",
        "billing_owner",
        "review_record_reference",
        "decision_summary",
    )
    return all(str(data.get(field, "")).strip() for field in fields)


def complete_input(data: dict[str, Any]) -> bool:
    flags = evidence_review_flags(data)
    notes = source_notes(data)
    artifacts = completed_artifacts(data)
    return (
        data.get("template_type") == "saee_pricing_page_evidence_input"
        and input_metadata_complete(data)
        and all(flags.values())
        and all(bool(notes.get(key)) for key in TARGET_KEYS)
        and all(key in artifacts for key in TARGET_KEYS)
        and not boundary_violations(data)
    )


def build_billing_revenue_evidence(
    data: dict[str, Any],
    input_path: Path,
    *,
    complete: bool,
) -> dict[str, Any]:
    flags = evidence_review_flags(data)
    artifacts = completed_artifacts(data)
    evidence: dict[str, Any] = {
        "billing_revenue_evidence_type": "production_billing_revenue_evidence",
        "evidence_scope": "human_filled_pricing_page_to_production_billing_revenue_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_pricing_page_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "commercial_owner_recorded": bool(str(data.get("commercial_owner", "")).strip()),
        "product_owner_recorded": bool(str(data.get("product_owner", "")).strip()),
        "accounting_owner_recorded": bool(str(data.get("accounting_owner", "")).strip()),
        "legal_owner_recorded": bool(str(data.get("legal_owner", "")).strip()),
        "billing_owner_recorded": bool(str(data.get("billing_owner", "")).strip()),
        "review_record_reference_recorded": bool(
            str(data.get("review_record_reference", "")).strip()
        ),
        "completed_review_artifact_count": len(artifacts),
        "pricing_page_available": False,
        "pricing_page_approved": False,
        "public_price_points_approved": False,
        "customer_facing_pricing_page_created": False,
        "sales_offer_generated": False,
        "pricing_page_claim_published": False,
        "pricing_page_completed_by_codex": False,
        "codex_published_pricing_page": False,
        "codex_approved_pricing_page": False,
        "codex_sent_sales_offer": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in (
        PAYMENT_PROVIDER_KEYS
        + INVOICE_PROCESS_KEYS
        + TAX_REVIEW_KEYS
        + REFUND_POLICY_KEYS
        + TENANT_BILLING_ISOLATION_KEYS
    ):
        evidence[key] = False
    for key in PRICING_PAGE_KEYS:
        evidence[key] = flags[key] and complete
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def readiness(path: Path) -> dict[str, object]:
    return evaluate_production_billing_revenue_evidence(
        load_settings({"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(path)})
    )


def build_from_input(
    input_path: Path,
    output_path: Path,
    billing_revenue_output_path: Path,
    *,
    write_documentation: bool = True,
) -> dict[str, Any]:
    data = read_json(input_path)
    complete = complete_input(data)
    violations = boundary_violations(data)
    flags = evidence_review_flags(data)
    missing = [key for key in TARGET_KEYS if not flags[key]]
    missing_artifacts = [key for key in TARGET_KEYS if key not in completed_artifacts(data)]
    status = "stop" if violations else ("pass" if complete else "hold")

    evidence = build_billing_revenue_evidence(data, input_path, complete=complete)
    write_json(billing_revenue_output_path, evidence)
    readiness_result = readiness(billing_revenue_output_path)

    summary: dict[str, Any] = {
        "pricing_page_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_pricing_page_to_production_billing_revenue_evidence",
        "generated_by": "scripts/saee_pricing_page_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "billing_revenue_evidence_output": str(billing_revenue_output_path),
        "status": status,
        "input_complete": complete,
        "metadata_complete": input_metadata_complete(data),
        "completed_review_artifact_count": len(completed_artifacts(data)),
        "required_evidence_item_count": len(TARGET_KEYS),
        "provided_evidence_item_count": sum(1 for value in flags.values() if value),
        "missing_required_evidence_count": len(missing),
        "missing_required_evidence": missing,
        "missing_review_artifact_count": len(missing_artifacts),
        "missing_review_artifacts": missing_artifacts,
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "billing_revenue_readiness_status": readiness_result["status"],
        "pricing_page_evidence_complete_for_review": readiness_result[
            "pricing_page_evidence_complete"
        ],
        "production_billing_revenue_ready": readiness_result[
            "production_billing_revenue_ready"
        ],
        "target_blocker_ids": ["pricing_page"],
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
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
        "legal_counsel_contacted": False,
        "tax_advisor_contacted": False,
        "human_approved_pricing_page_copy": False,
        "approved_plan_and_usage_terms": False,
        "legal_review_completed": False,
        "production_readiness_non_claim_reviewed": False,
        "pricing_page_publication_approval_recorded": False,
        "pricing_page_available": False,
        "pricing_page_published": False,
        "pricing_page_approved": False,
        "public_price_points_approved": False,
        "customer_facing_pricing_page_created": False,
        "sales_offer_generated": False,
        "sales_offer_sent": False,
        "tax_collection_started": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "pricing_page_claim_published": False,
        "pricing_page_completed_by_codex": False,
        "pricing_page_execution_authorized": False,
        "codex_published_pricing_page": False,
        "codex_approved_pricing_page": False,
        "codex_sent_sales_offer": False,
        "codex_inferred_missing_evidence": False,
        "next_action": (
            "Human product, commercial, legal, accounting, and billing owners "
            "may fill the pricing-page input with source-backed pricing copy, "
            "plan and usage terms, legal review, non-production-claim review, "
            "and publication approval references. The generated evidence "
            "remains one input to a later go/no-go profile."
        ),
    }
    write_json(output_path, summary)
    if write_documentation:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Pricing Page Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- pricing_page_evidence_builder_v0_1: true
- builder_scope: human_filled_pricing_page_to_production_billing_revenue_evidence
- required_evidence_item_count: {summary['required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- billing_revenue_readiness_status: {summary['billing_revenue_readiness_status']}
- pricing_page_evidence_complete_for_review: {str(summary['pricing_page_evidence_complete_for_review']).lower()}
- production_billing_revenue_ready: false
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete way to convert completed
pricing-page evidence into the existing production billing/revenue evidence
shape. It targets the `pricing_page` evidence group only.

## What It Does Not Do

It does not approve pricing copy, publish a pricing page, create a sales offer,
configure payment providers, enable checkout,
collect payment, validate revenue, close blockers, or mark SAEE as production
ready.

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
- human_approved_pricing_page_copy: false
- approved_plan_and_usage_terms: false
- legal_review_completed: false
- production_readiness_non_claim_reviewed: false
- pricing_page_publication_approval_recorded: false
- pricing_page_available: false
- pricing_page_published: false
- pricing_page_approved: false
- public_price_points_approved: false
- customer_facing_pricing_page_created: false
- sales_offer_generated: false
- sales_offer_sent: false
- tax_advisor_contacted: false
- legal_counsel_contacted: false
- tax_collection_started: false
- payment_provider_configured: false
- checkout_enabled: false
- customer_payment_collected: false
- revenue_validated: false
- codex_published_pricing_page: false
- codex_approved_pricing_page: false
- codex_sent_sales_offer: false

## Next Action

Human owners must fill `pricing_page_evidence_input.template.json` with real
source notes, approval records, and review references. The generated evidence is
only one input to later go/no-go review and does not close the `pricing_page`
blocker by itself.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Pricing Page Evidence Builder v0.1

Status: local builder available; default output is hold.

pricing_page_evidence_builder_v0_1: true
builder_scope: human_filled_pricing_page_to_production_billing_revenue_evidence
required_evidence_item_count: {summary['required_evidence_item_count']}
default_output_status: {summary['status']}
pricing_page_evidence_complete_for_review: {str(summary['pricing_page_evidence_complete_for_review']).lower()}
production_billing_revenue_ready: false
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0

## Purpose

This builder converts human-filled pricing-page input into local production
billing/revenue evidence fields for the `pricing_page` group. It is a
commercial-readiness evidence intake surface, not pricing publication,
sales-offer creation, payment-provider configuration, payment processing, or
customer billing.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false

## Boundary

pricing_page_evidence_complete_for_review: false
production_billing_revenue_ready: false
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
human_approved_pricing_page_copy: false
approved_plan_and_usage_terms: false
legal_review_completed: false
production_readiness_non_claim_reviewed: false
pricing_page_publication_approval_recorded: false
pricing_page_available: false
pricing_page_published: false
pricing_page_approved: false
public_price_points_approved: false
customer_facing_pricing_page_created: false
sales_offer_generated: false
sales_offer_sent: false
tax_advisor_contacted: false
legal_counsel_contacted: false
tax_collection_started: false
payment_provider_configured: false
checkout_enabled: false
customer_payment_collected: false
revenue_validated: false
codex_published_pricing_page: false
codex_approved_pricing_page: false
codex_sent_sales_offer: false
pricing_page_claim_published: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_input.template.json`
- builder output: `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_builder_output.local.json`
- billing/revenue evidence output: `phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_pricing_page.local.json`
- report: `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_evidence_builder_report.md`
- script: `scripts/saee_pricing_page_evidence_builder.py`
- smoke: `scripts/saee_pricing_page_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Pricing Page Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_pricing_page_claim: false
recommend_for_pricing_publication: false
recommend_for_revenue_validation_claim: false
recommend_for_external_execution: false

## Reason

The builder is useful because it converts human-filled pricing-page evidence into
a machine-checkable production billing/revenue evidence shape. It is not
sufficient for blocker closure by itself: default input is incomplete, and even
complete pricing-page evidence leaves payment provider, invoice
process, tax review, and tenant billing isolation evidence unresolved.

## Boundary

pricing_page_evidence_complete_for_review: false
production_billing_revenue_ready: false
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
human_approved_pricing_page_copy: false
approved_plan_and_usage_terms: false
legal_review_completed: false
production_readiness_non_claim_reviewed: false
pricing_page_publication_approval_recorded: false
pricing_page_available: false
pricing_page_published: false
pricing_page_approved: false
public_price_points_approved: false
customer_facing_pricing_page_created: false
sales_offer_generated: false
sales_offer_sent: false
tax_advisor_contacted: false
legal_counsel_contacted: false
tax_collection_started: false
payment_provider_configured: false
checkout_enabled: false
customer_payment_collected: false
revenue_validated: false
codex_published_pricing_page: false
codex_approved_pricing_page: false
codex_sent_sales_offer: false
pricing_page_claim_published: false
blockers_closed_by_builder: 0
""",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default=str(DEFAULT_INPUT_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument(
        "--billing-revenue-output",
        default=str(DEFAULT_BILLING_REVENUE_OUTPUT_PATH),
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    summary = build_from_input(
        Path(args.input),
        Path(args.output),
        Path(args.billing_revenue_output),
    )
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return
    print(
        "SAEE_PRICING_PAGE_EVIDENCE_BUILDER: PASS "
        f"status={summary['status']} "
        f"input_complete={str(summary['input_complete']).lower()} "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
