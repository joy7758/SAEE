#!/usr/bin/env python3
"""Build invoice-process evidence from human-filled review input.

This builder converts local, human-filled invoice-process evidence into the
production billing/revenue evidence shape consumed by commercial readiness
checks. It does not create invoice templates, create or send invoices, sign
contracts, perform reconciliation, contact customers, collect payment, validate
revenue, close blockers, modify product behavior, or claim production
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
DEFAULT_INPUT_PATH = OUTPUT_DIR / "invoice_process_evidence_input.template.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "invoice_process_evidence_builder_output.local.json"
DEFAULT_BILLING_REVENUE_OUTPUT_PATH = (
    OUTPUT_DIR / "production_billing_revenue_evidence.from_invoice_process.local.json"
)
REPORT_PATH = OUTPUT_DIR / "invoice_process_evidence_builder_report.md"
DOC_PATH = (
    ROOT / "phase_b_product/commercial_readiness/INVOICE_PROCESS_EVIDENCE_BUILDER_V0_1.md"
)
GATE_PATH = (
    ROOT / "docs/strategy/SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)

TARGET_KEYS = INVOICE_PROCESS_KEYS
INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(FORBIDDEN_TRUE_KEYS)
        | {
            "invoice_created",
            "invoice_template_published",
            "invoice_process_claim_published",
            "invoice_process_completed_by_codex",
            "invoice_process_execution_authorized",
            "codex_created_invoice",
            "codex_sent_invoice",
            "codex_signed_contract",
            "codex_performed_reconciliation",
            "codex_inferred_missing_evidence",
            "blockers_closed_by_builder",
        }
    )
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER: FAIL: " + message)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def default_input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_invoice_process_evidence_input",
        "template_version": "v0.1",
        "input_status": "template_pending_human_input",
        "human_reviewer_name": "",
        "review_date": "",
        "commercial_owner": "",
        "invoice_owner": "",
        "accounting_owner": "",
        "support_owner": "",
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
        "invoice_created": False,
        "invoice_template_published": False,
        "invoice_sent_to_customer": False,
        "tax_collection_started": False,
        "refund_policy_published": False,
        "production_billing_enabled": False,
        "customer_payment_collected": False,
        "paid_pilot_completed": False,
        "revenue_validated": False,
        "invoice_process_claim_published": False,
        "invoice_process_completed_by_codex": False,
        "invoice_process_execution_authorized": False,
        "codex_created_invoice": False,
        "codex_sent_invoice": False,
        "codex_signed_contract": False,
        "codex_performed_reconciliation": False,
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
            f"SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
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
        "invoice_owner",
        "accounting_owner",
        "support_owner",
        "review_record_reference",
        "decision_summary",
    )
    return all(str(data.get(field, "")).strip() for field in fields)


def complete_input(data: dict[str, Any]) -> bool:
    flags = evidence_review_flags(data)
    notes = source_notes(data)
    artifacts = completed_artifacts(data)
    return (
        data.get("template_type") == "saee_invoice_process_evidence_input"
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
        "evidence_scope": "human_filled_invoice_process_to_production_billing_revenue_evidence",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_invoice_process_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "commercial_owner_recorded": bool(str(data.get("commercial_owner", "")).strip()),
        "invoice_owner_recorded": bool(str(data.get("invoice_owner", "")).strip()),
        "accounting_owner_recorded": bool(str(data.get("accounting_owner", "")).strip()),
        "support_owner_recorded": bool(str(data.get("support_owner", "")).strip()),
        "review_record_reference_recorded": bool(
            str(data.get("review_record_reference", "")).strip()
        ),
        "completed_review_artifact_count": len(artifacts),
        "invoice_process_claim_published": False,
        "invoice_process_completed_by_codex": False,
        "codex_created_invoice": False,
        "codex_sent_invoice": False,
        "codex_signed_contract": False,
        "codex_performed_reconciliation": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in (
        PRICING_PAGE_KEYS
        + PAYMENT_PROVIDER_KEYS
        + TAX_REVIEW_KEYS
        + REFUND_POLICY_KEYS
        + TENANT_BILLING_ISOLATION_KEYS
    ):
        evidence[key] = False
    for key in INVOICE_PROCESS_KEYS:
        evidence[key] = flags[key] and complete
    for key in FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    evidence["invoice_created"] = False
    evidence["invoice_template_published"] = False
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
        "invoice_process_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_invoice_process_to_production_billing_revenue_evidence",
        "generated_by": "scripts/saee_invoice_process_evidence_builder.py",
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
        "invoice_process_evidence_complete_for_review": readiness_result[
            "invoice_process_evidence_complete"
        ],
        "production_billing_revenue_ready": readiness_result[
            "production_billing_revenue_ready"
        ],
        "target_blocker_ids": ["invoice_process"],
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
        "invoice_created": False,
        "invoice_template_published": False,
        "invoice_sent_to_customer": False,
        "enterprise_contract_signed": False,
        "payment_provider_configured": False,
        "checkout_enabled": False,
        "payment_link_created": False,
        "customer_payment_collected": False,
        "revenue_validated": False,
        "invoice_process_claim_published": False,
        "invoice_process_completed_by_codex": False,
        "invoice_process_execution_authorized": False,
        "codex_created_invoice": False,
        "codex_sent_invoice": False,
        "codex_signed_contract": False,
        "codex_performed_reconciliation": False,
        "codex_inferred_missing_evidence": False,
        "next_action": (
            "Human commercial, invoice, accounting, support, legal, and tax "
            "owners may fill the invoice-process input with source-backed "
            "ownership, workflow, contract handoff, reconciliation, support "
            "handoff, and bookkeeping references. The generated evidence "
            "remains one input to a later go/no-go profile."
        ),
    }
    write_json(output_path, summary)
    if write_documentation:
        write_docs(summary)
    return summary


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Invoice Process Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- invoice_process_evidence_builder_v0_1: true
- builder_scope: human_filled_invoice_process_to_production_billing_revenue_evidence
- required_evidence_item_count: {summary['required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- billing_revenue_readiness_status: {summary['billing_revenue_readiness_status']}
- invoice_process_evidence_complete_for_review: {str(summary['invoice_process_evidence_complete_for_review']).lower()}
- production_billing_revenue_ready: false
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete way to convert completed
invoice-process evidence into the existing production billing/revenue evidence
shape. It targets the `invoice_process` evidence group only.

## What It Does Not Do

It does not create invoice templates, create or send invoices, sign contracts,
perform reconciliation, collect payment, validate revenue, close blockers, or
mark SAEE as production ready.

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
- invoice_created: false
- invoice_template_published: false
- invoice_sent_to_customer: false
- enterprise_contract_signed: false
- payment_provider_configured: false
- checkout_enabled: false
- customer_payment_collected: false
- revenue_validated: false
- codex_created_invoice: false
- codex_sent_invoice: false
- codex_signed_contract: false
- codex_performed_reconciliation: false

## Next Action

Human owners must fill `invoice_process_evidence_input.template.json` with real
source notes, approval records, and review references. The generated evidence is
only one input to later go/no-go review and does not close the `invoice_process`
blocker by itself.
"""


def write_docs(summary: dict[str, Any]) -> None:
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOC_PATH.write_text(
        f"""# SAEE Invoice Process Evidence Builder v0.1

Status: local builder available; default output is hold.

invoice_process_evidence_builder_v0_1: true
builder_scope: human_filled_invoice_process_to_production_billing_revenue_evidence
required_evidence_item_count: {summary['required_evidence_item_count']}
default_output_status: {summary['status']}
invoice_process_evidence_complete_for_review: {str(summary['invoice_process_evidence_complete_for_review']).lower()}
production_billing_revenue_ready: false
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0

## Purpose

This builder converts human-filled invoice-process input into local production
billing/revenue evidence fields for the `invoice_process` group. It is a
commercial-readiness evidence intake surface, not invoice creation, contract
execution, reconciliation, or customer billing.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false

## Boundary

invoice_process_evidence_complete_for_review: false
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
invoice_created: false
invoice_template_published: false
invoice_sent_to_customer: false
enterprise_contract_signed: false
payment_provider_configured: false
checkout_enabled: false
payment_link_created: false
customer_payment_collected: false
revenue_validated: false
codex_created_invoice: false
codex_sent_invoice: false
codex_signed_contract: false
codex_performed_reconciliation: false
invoice_process_claim_published: false

## Entrypoints

- input template: `phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_input.template.json`
- builder output: `phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_builder_output.local.json`
- billing/revenue evidence output: `phase_b_product/commercial_readiness/billing_revenue_evidence/production_billing_revenue_evidence.from_invoice_process.local.json`
- report: `phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_evidence_builder_report.md`
- script: `scripts/saee_invoice_process_evidence_builder.py`
- smoke: `scripts/saee_invoice_process_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        """# SAEE Invoice Process Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_invoice_process_claim: false
recommend_for_invoice_creation: false
recommend_for_contract_execution: false
recommend_for_revenue_validation_claim: false
recommend_for_external_execution: false

## Reason

The builder is useful because it converts human-filled invoice-process evidence
into a machine-checkable production billing/revenue evidence shape. It is not
sufficient for blocker closure by itself: default input is incomplete, and even
complete invoice-process evidence leaves pricing page, payment provider, tax
review, refund policy, and tenant billing isolation evidence unresolved.

## Boundary

invoice_process_evidence_complete_for_review: false
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
invoice_created: false
invoice_template_published: false
invoice_sent_to_customer: false
enterprise_contract_signed: false
payment_provider_configured: false
checkout_enabled: false
payment_link_created: false
customer_payment_collected: false
revenue_validated: false
codex_created_invoice: false
codex_sent_invoice: false
codex_signed_contract: false
codex_performed_reconciliation: false
invoice_process_claim_published: false
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
        "SAEE_INVOICE_PROCESS_EVIDENCE_BUILDER: PASS "
        f"status={summary['status']} "
        f"input_complete={str(summary['input_complete']).lower()} "
        "blockers_closed_by_builder=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
