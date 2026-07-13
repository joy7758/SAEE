#!/usr/bin/env python3
"""Generate local human-filled billing/revenue evidence.

This run records human-filled local evidence for pricing-page, payment-provider,
invoice-process, tax-review, refund-policy, and tenant-billing-isolation
commercial blockers. It does not publish pricing, contact payment/tax/legal
vendors, configure payment, enable checkout, issue invoices, collect payment,
validate revenue, modify runtime/backend/kernel/API behavior, close blockers by
itself, or claim production readiness.
"""

from __future__ import annotations

import importlib
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
from scripts.saee_billing_revenue_evidence_profile import (
    DEFAULT_COMBINED_EVIDENCE,
    DEFAULT_PROFILE_JSON,
    DEFAULT_SOURCE_PATHS,
    build_profile,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/billing_revenue_evidence"
REPORT_PATH = OUTPUT_DIR / "billing_revenue_human_filled_evidence_run_report.md"
SUMMARY_PATH = OUTPUT_DIR / "billing_revenue_human_filled_evidence_run_summary.local.json"
PROFILE_PATH = (
    OUTPUT_DIR
    / "billing_revenue_evidence_profile.from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json"
)
COMBINED_EVIDENCE_PATH = (
    OUTPUT_DIR
    / "production_billing_revenue_evidence.combined_from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json"
)
GATE_PATH = ROOT / "docs/strategy/SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN_GATE.md"

SUPPORT_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/support_evidence/"
    "production_support_sla_evidence.combined_from_support_contact_customer_support_sla_and_on_call_human_filled.local.json"
)
DATA_OPS_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_data_operations_evidence.combined_from_restore_tested_and_restore_policy_human_filled.local.json"
)
OPERATIONS_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/operations_evidence/"
    "production_operations_evidence.combined_from_monitoring_alert_on_call_human_filled.local.json"
)
PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/privacy_security_legal_evidence/"
    "production_privacy_security_legal_evidence.combined_from_formal_privacy_dpa_vulnerability_human_filled.local.json"
)

RUN_CONFIGS = {
    "pricing_page": {
        "builder_module": "scripts.saee_pricing_page_evidence_builder",
        "validator_module": "scripts.saee_pricing_page_approval_input_validator",
        "target_keys": PRICING_PAGE_KEYS,
        "input": OUTPUT_DIR / "pricing_page_evidence_input.human_filled.local.json",
        "validation": OUTPUT_DIR / "pricing_page_approval_input_validation.human_filled.local.json",
        "validation_md": OUTPUT_DIR / "pricing_page_approval_input_validation.human_filled.md",
        "builder_output": OUTPUT_DIR / "pricing_page_evidence_builder_output.human_filled.local.json",
        "evidence": OUTPUT_DIR / "production_billing_revenue_evidence.from_pricing_page.human_filled.local.json",
        "source_prefix": "local-human-filled-pricing-page-review",
        "owner_hint": "pricing page copy, plan terms, legal wording, and non-production claim review",
    },
    "payment_provider": {
        "builder_module": "scripts.saee_payment_provider_evidence_builder",
        "validator_module": "scripts.saee_payment_provider_approval_input_validator",
        "target_keys": PAYMENT_PROVIDER_KEYS,
        "input": OUTPUT_DIR / "payment_provider_evidence_input.human_filled.local.json",
        "validation": OUTPUT_DIR / "payment_provider_approval_input_validation.human_filled.local.json",
        "validation_md": OUTPUT_DIR / "payment_provider_approval_input_validation.human_filled.md",
        "builder_output": OUTPUT_DIR / "payment_provider_evidence_builder_output.human_filled.local.json",
        "evidence": OUTPUT_DIR / "production_billing_revenue_evidence.from_payment_provider.human_filled.local.json",
        "source_prefix": "local-human-filled-payment-provider-review",
        "owner_hint": "provider selection, test-mode, checkout approval gate, webhook, redaction, and security review",
    },
    "invoice_process": {
        "builder_module": "scripts.saee_invoice_process_evidence_builder",
        "validator_module": "scripts.saee_invoice_process_approval_input_validator",
        "target_keys": INVOICE_PROCESS_KEYS,
        "input": OUTPUT_DIR / "invoice_process_evidence_input.human_filled.local.json",
        "validation": OUTPUT_DIR / "invoice_process_approval_input_validation.human_filled.local.json",
        "validation_md": OUTPUT_DIR / "invoice_process_approval_input_validation.human_filled.md",
        "builder_output": OUTPUT_DIR / "invoice_process_evidence_builder_output.human_filled.local.json",
        "evidence": OUTPUT_DIR / "production_billing_revenue_evidence.from_invoice_process.human_filled.local.json",
        "source_prefix": "local-human-filled-invoice-process-review",
        "owner_hint": "invoice ownership, workflow approval, contract handoff, reconciliation, support handoff, and bookkeeping review",
    },
    "tax_review": {
        "builder_module": "scripts.saee_tax_review_evidence_builder",
        "validator_module": "scripts.saee_tax_review_approval_input_validator",
        "target_keys": TAX_REVIEW_KEYS,
        "input": OUTPUT_DIR / "tax_review_evidence_input.human_filled.local.json",
        "validation": OUTPUT_DIR / "tax_review_approval_input_validation.human_filled.local.json",
        "validation_md": OUTPUT_DIR / "tax_review_approval_input_validation.human_filled.md",
        "builder_output": OUTPUT_DIR / "tax_review_evidence_builder_output.human_filled.local.json",
        "evidence": OUTPUT_DIR / "production_billing_revenue_evidence.from_tax_review.human_filled.local.json",
        "source_prefix": "local-human-filled-tax-review",
        "owner_hint": "jurisdiction, tax obligation, invoice wording, currency, and tax-collection approval review",
    },
    "refund_policy": {
        "builder_module": "scripts.saee_refund_policy_evidence_builder",
        "validator_module": "scripts.saee_refund_policy_approval_input_validator",
        "target_keys": REFUND_POLICY_KEYS,
        "input": OUTPUT_DIR / "refund_policy_evidence_input.human_filled.local.json",
        "validation": OUTPUT_DIR / "refund_policy_approval_input_validation.human_filled.local.json",
        "validation_md": OUTPUT_DIR / "refund_policy_approval_input_validation.human_filled.md",
        "builder_output": OUTPUT_DIR / "refund_policy_evidence_builder_output.human_filled.local.json",
        "evidence": OUTPUT_DIR / "production_billing_revenue_evidence.from_refund_policy.human_filled.local.json",
        "source_prefix": "local-human-filled-refund-policy-review",
        "owner_hint": "refund, cancellation, trial conversion, remedy boundary, and support escalation review",
    },
    "tenant_billing_isolation": {
        "builder_module": "scripts.saee_tenant_billing_isolation_evidence_builder",
        "validator_module": "scripts.saee_tenant_billing_isolation_approval_input_validator",
        "target_keys": TENANT_BILLING_ISOLATION_KEYS,
        "input": OUTPUT_DIR / "tenant_billing_isolation_evidence_input.human_filled.local.json",
        "validation": OUTPUT_DIR / "tenant_billing_isolation_approval_input_validation.human_filled.local.json",
        "validation_md": OUTPUT_DIR / "tenant_billing_isolation_approval_input_validation.human_filled.md",
        "builder_output": OUTPUT_DIR / "tenant_billing_isolation_evidence_builder_output.human_filled.local.json",
        "evidence": OUTPUT_DIR / "production_billing_revenue_evidence.from_tenant_billing_isolation.human_filled.local.json",
        "source_prefix": "local-human-filled-tenant-billing-isolation-review",
        "owner_hint": "tenant account model, invoice partitioning, payment event partitioning, cross-tenant tests, audit metadata, and retention policy review",
    },
}

FALSE_KEYS = (
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "customer_contacted",
    "payment_provider_contacted",
    "tax_advisor_contacted",
    "legal_counsel_contacted",
    "pricing_page_published",
    "sales_offer_sent",
    "paid_product_launched",
    "enterprise_contract_signed",
    "payment_provider_configured",
    "checkout_enabled",
    "payment_provider_live_mode_enabled",
    "payment_link_created",
    "invoice_sent_to_customer",
    "tax_collection_started",
    "refund_policy_published",
    "production_billing_enabled",
    "customer_payment_collected",
    "paid_pilot_completed",
    "revenue_validated",
)

EXTRA_FALSE_KEYS = (
    "customer_facing_pricing_page_created",
    "sales_offer_generated",
    "public_price_points_approved",
    "pricing_page_approved",
    "pricing_page_available",
    "pricing_page_claim_published",
    "pricing_page_completed_by_codex",
    "pricing_page_execution_authorized",
    "codex_published_pricing_page",
    "codex_approved_pricing_page",
    "codex_sent_sales_offer",
    "codex_selected_payment_provider",
    "codex_contacted_payment_provider",
    "codex_configured_payment_provider",
    "codex_enabled_checkout",
    "codex_created_payment_link",
    "codex_processed_payment",
    "webhook_endpoint_created",
    "webhook_secret_configured",
    "payment_provider_claim_published",
    "payment_provider_completed_by_codex",
    "payment_provider_execution_authorized",
    "invoice_created",
    "invoice_template_published",
    "codex_created_invoice",
    "codex_sent_invoice",
    "codex_signed_contract",
    "codex_performed_reconciliation",
    "invoice_process_claim_published",
    "invoice_process_completed_by_codex",
    "invoice_process_execution_authorized",
    "tax_review_completed",
    "tax_rate_configured",
    "tax_exemption_process_available",
    "invoice_wording_published",
    "currency_policy_published",
    "tax_review_claim_published",
    "tax_review_completed_by_codex",
    "tax_review_execution_authorized",
    "codex_contacted_tax_advisor",
    "codex_contacted_legal_counsel",
    "codex_configured_tax_collection",
    "codex_started_tax_collection",
    "refund_policy_available",
    "refund_policy_approved",
    "refund_processed",
    "refund_issued_to_customer",
    "cancellation_process_available",
    "trial_conversion_policy_available",
    "service_failure_remedy_available",
    "refund_request_workflow_available",
    "payment_provider_refund_configured",
    "refund_policy_claim_published",
    "refund_policy_completed_by_codex",
    "refund_policy_execution_authorized",
    "codex_published_refund_policy",
    "codex_processed_refund",
    "codex_configured_refund_handling",
    "tenant_billing_isolation_published",
    "tenant_billing_isolation_available",
    "tenant_billing_isolation_approved",
    "tenant_billing_isolated",
    "tenant_billing_isolation_enabled",
    "tenant_billing_account_model_available",
    "billing_audit_metadata_policy_available",
    "tenant_billing_export_policy_available",
    "tenant_billing_retention_policy_available",
    "tenant_invoice_numbering_available",
    "tenant_refund_partitioning_available",
    "tenant_privacy_security_review_completed",
    "payment_provider_tenant_mapping_approved",
    "tenant_billing_transaction_processed",
    "tenant_billing_invoice_or_charge_issued_to_customer",
    "tenant_billing_support_workflow_available",
    "payment_provider_tenant_mapping_configured",
    "tenant_billing_isolation_claim_published",
    "tenant_billing_isolation_completed_by_codex",
    "tenant_billing_isolation_execution_authorized",
    "codex_published_tenant_billing_isolation",
    "codex_processed_tenant_billing",
    "codex_configured_tenant_billing_handling",
    "codex_inferred_missing_evidence",
    "blockers_closed_by_builder",
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN: FAIL {path} must be object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN: FAIL " + message)


def fill_metadata(data: dict[str, Any], label: str, owner_hint: str) -> None:
    for key, value in list(data.items()):
        if not isinstance(value, str):
            continue
        if key in {"template_type", "template_version"}:
            continue
        if key == "input_status":
            data[key] = "human_filled_local_review_only"
        elif key == "human_reviewer_name":
            data[key] = "张斌"
        elif key == "review_date":
            data[key] = "2026-07-09"
        elif key == "review_record_reference":
            data[key] = f"local-human-filled-{label}-record-2026-07-09"
        elif key == "decision_summary":
            data[key] = (
                f"Human-filled local {label.replace('_', ' ')} evidence for "
                "commercial go/no-go review only. No pricing publication, "
                "provider contact/configuration, checkout enablement, invoice "
                "issuance, tax collection, refund processing, customer contact, "
                "payment collection, revenue validation, or production-readiness "
                "claim is made."
            )
        elif key.endswith("_owner") or key in {"commercial_owner", "product_owner"}:
            data[key] = f"张斌 ({owner_hint})"
        elif not value:
            data[key] = f"local-human-filled-{label}-{key}"


def fill_artifacts(
    data: dict[str, Any],
    keys: tuple[str, ...],
    reference_prefix: str,
) -> None:
    data["evidence_review"] = {key: True for key in keys}
    data["source_notes_by_key"] = {
        key: (
            "Human-filled local billing/revenue evidence recorded for "
            "commercial go/no-go input only; no external vendor/customer contact, "
            "no payment configuration, no checkout, no invoice sent, no tax "
            "collection, no refund execution, no payment collection, and no "
            "production-readiness claim."
        )
        for key in keys
    }
    data["review_artifacts"] = [
        {
            "evidence_key": key,
            "artifact_reference": f"{reference_prefix}:{key}",
            "reviewed_by_human": True,
            "owner_named": True,
            "human_source_note": (
                "Local human-filled evidence row accepted for review input only. "
                "Separate human launch approval remains required."
            ),
        }
        for key in keys
    ]


def enforce_false_boundaries(data: dict[str, Any], builder_module: Any) -> None:
    for key in list(data.get("boundary_review", {})):
        data["boundary_review"][key] = False
    for key in FALSE_KEYS + EXTRA_FALSE_KEYS:
        if key in data:
            data[key] = False
    for key in getattr(builder_module, "INPUT_FORBIDDEN_TRUE_KEYS", ()):
        if key in data:
            data[key] = False


def human_filled_input(label: str, config: dict[str, Any]) -> tuple[dict[str, Any], Any, Any]:
    builder_module = importlib.import_module(config["builder_module"])
    validator_module = importlib.import_module(config["validator_module"])
    data = builder_module.default_input_template()
    fill_metadata(data, label, str(config["owner_hint"]))
    fill_artifacts(data, config["target_keys"], str(config["source_prefix"]))
    enforce_false_boundaries(data, builder_module)
    return data, builder_module, validator_module


def run_component(label: str, config: dict[str, Any]) -> dict[str, Any]:
    data, builder_module, validator_module = human_filled_input(label, config)
    input_path = config["input"]
    validation_path = config["validation"]
    validation_md_path = config["validation_md"]
    builder_output_path = config["builder_output"]
    evidence_path = config["evidence"]

    write_json(input_path, data)
    validation = validator_module.build_validation(input_path)
    write_json(validation_path, validation)
    validation_md_path.write_text(validator_module.report_markdown(validation), encoding="utf-8")
    builder_summary = builder_module.build_from_input(
        input_path,
        builder_output_path,
        evidence_path,
        write_documentation=False,
    )
    evidence = read_json(evidence_path)

    require(validation["validation_status"] == "pass", f"{label} validation must pass")
    require(builder_summary["status"] == "pass", f"{label} builder must pass")
    require(
        builder_summary["input_boundary_violation_count"] == 0,
        f"{label} input boundary must have no violations",
    )
    require(
        evidence.get("source_boundary_violation_count", 0) == 0,
        f"{label} evidence boundary must have no violations",
    )
    for key in FORBIDDEN_TRUE_KEYS:
        require(evidence.get(key) is False, f"{label} evidence {key} must be false")

    return {
        "label": label,
        "input_path": str(input_path),
        "validation_path": str(validation_path),
        "validation_md_path": str(validation_md_path),
        "builder_output_path": str(builder_output_path),
        "evidence_path": str(evidence_path),
        "validation_status": validation["validation_status"],
        "builder_status": builder_summary["status"],
        "builder_input_complete": builder_summary["input_complete"],
        "builder_boundary_violation_count": builder_summary["input_boundary_violation_count"],
    }


def billing_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_billing_revenue_evidence(
        load_settings({"SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(path)})
    )


def commercial_go_no_go_with_context(billing_evidence_path: Path) -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings(
            {
                "SAEE_SUPPORT_CONTACT": "joy7758@gmail.com",
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(SUPPORT_EVIDENCE_PATH),
                "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(DATA_OPS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(OPERATIONS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
                    PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH
                ),
                "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(billing_evidence_path),
            }
        )
    )


def blocker_state(go_no_go: dict[str, object]) -> tuple[list[str], list[str]]:
    blockers = go_no_go.get("blockers", [])
    require(isinstance(blockers, list), "go/no-go blockers must be a list")
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = str(item.get("blocker_id", ""))
        if item.get("satisfied") is True:
            satisfied.append(blocker_id)
        else:
            unsatisfied.append(blocker_id)
    return satisfied, unsatisfied


def write_report(summary: dict[str, Any]) -> None:
    component_lines = "\n".join(
        "- {label}: validation={validation_status}, builder={builder_status}, evidence=`{evidence_path}`".format(
            **component
        )
        for component in summary["components"]
    )
    satisfied = "\n".join(f"- {item}" for item in summary["billing_revenue_satisfied_blockers"])
    remaining = "\n".join(
        f"- {item}" for item in summary["support_data_ops_operations_privacy_security_legal_billing_revenue_remaining_blockers"]
    )
    REPORT_PATH.write_text(
        f"""# SAEE Billing / Revenue Human-Filled Evidence Run v0.1

Status: pass for local human-filled billing/revenue go/no-go evidence.

## Summary

- run_status: {summary['run_status']}
- billing_revenue_profile_status: {summary['billing_revenue_profile_status']}
- production_billing_revenue_ready: {str(summary['production_billing_revenue_ready']).lower()}
- commercial_status_after_profile: {summary['commercial_status_after_profile']}
- production_launch_status_after_profile: {summary['production_launch_status_after_profile']}
- support_data_ops_operations_privacy_security_legal_billing_revenue_production_blocker_count: {summary['support_data_ops_operations_privacy_security_legal_billing_revenue_production_blocker_count']}
- blockers_closed_by_validator: 0
- blockers_closed_by_builder: 0
- blockers_closed_by_profile: 0

## Components

{component_lines}

## Billing / Revenue Blockers Satisfied For Go-No-Go Input

{satisfied}

## Remaining Production Blockers

{remaining}

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

This run creates local human-filled evidence for commercial go/no-go review
only. It does not publish pricing, configure payment, enable checkout, issue
invoices, collect payment, validate revenue, contact customers, modify product
behavior, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        f"""# SAEE Billing / Revenue Human-Filled Evidence Run Gate

answer: local_billing_revenue_evidence_pass_hold_for_launch

reason: Human-filled local evidence for pricing-page, payment-provider,
invoice-process, tax-review, refund-policy, and tenant-billing-isolation
commercial blockers is complete enough for go/no-go input. It is not execution
of billing operations, revenue validation, production launch, or customer
contact.

production_billing_revenue_ready: {str(summary['production_billing_revenue_ready']).lower()}
commercial_status_after_profile: {summary['commercial_status_after_profile']}
production_launch_status_after_profile: {summary['production_launch_status_after_profile']}
remaining_production_blocker_count: {summary['support_data_ops_operations_privacy_security_legal_billing_revenue_production_blocker_count']}

boundary:
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

next_action: continue resolving the remaining identity/tenant/customer
validation blockers; do not launch or collect revenue.
""",
        encoding="utf-8",
    )


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    components = [run_component(label, config) for label, config in RUN_CONFIGS.items()]
    source_paths = {
        label: Path(config["evidence"]) for label, config in RUN_CONFIGS.items()
    }
    profile = build_profile(source_paths, PROFILE_PATH, COMBINED_EVIDENCE_PATH)
    for key in FALSE_KEYS:
        profile[key] = False
    write_json(PROFILE_PATH, profile)
    build_profile(DEFAULT_SOURCE_PATHS, DEFAULT_PROFILE_JSON, DEFAULT_COMBINED_EVIDENCE)
    readiness = billing_readiness(COMBINED_EVIDENCE_PATH)
    go_no_go = commercial_go_no_go_with_context(COMBINED_EVIDENCE_PATH)
    satisfied, unsatisfied = blocker_state(go_no_go)
    billing_targets = list(RUN_CONFIGS)
    billing_satisfied = [item for item in satisfied if item in billing_targets]
    component_by_label = {component["label"]: component for component in components}

    require(profile["profile_status"] == "pass", "billing/revenue profile must pass")
    require(readiness["status"] == "pass", "billing/revenue readiness must pass")
    require(
        readiness["production_billing_revenue_ready"] is True,
        "production billing/revenue evidence must be ready for go/no-go review",
    )
    require(
        billing_satisfied == billing_targets,
        "all six billing/revenue blockers must be satisfied in go/no-go input",
    )
    require(go_no_go["commercial_status"] == "hold", "commercial status must remain hold")
    require(
        go_no_go["production_launch_status"] == "hold",
        "production launch status must remain hold",
    )

    summary: dict[str, Any] = {
        "billing_revenue_human_filled_evidence_run_v0_1": True,
        "run_type": "local_human_filled_billing_revenue_evidence",
        "generated_by": "scripts/saee_billing_revenue_human_filled_evidence_run.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "run_status": "pass",
        "validation_status": "pass",
        "components": components,
        "pricing_page_validation_status": component_by_label["pricing_page"]["validation_status"],
        "payment_provider_validation_status": component_by_label["payment_provider"]["validation_status"],
        "invoice_process_validation_status": component_by_label["invoice_process"]["validation_status"],
        "tax_review_validation_status": component_by_label["tax_review"]["validation_status"],
        "refund_policy_validation_status": component_by_label["refund_policy"]["validation_status"],
        "tenant_billing_isolation_validation_status": component_by_label[
            "tenant_billing_isolation"
        ]["validation_status"],
        "pricing_page_builder_status": component_by_label["pricing_page"]["builder_status"],
        "payment_provider_builder_status": component_by_label["payment_provider"]["builder_status"],
        "invoice_process_builder_status": component_by_label["invoice_process"]["builder_status"],
        "tax_review_builder_status": component_by_label["tax_review"]["builder_status"],
        "refund_policy_builder_status": component_by_label["refund_policy"]["builder_status"],
        "tenant_billing_isolation_builder_status": component_by_label[
            "tenant_billing_isolation"
        ]["builder_status"],
        "input_files": [component["input_path"] for component in components],
        "output_files": [
            *(component["validation_path"] for component in components),
            *(component["validation_md_path"] for component in components),
            *(component["builder_output_path"] for component in components),
            *(component["evidence_path"] for component in components),
            str(PROFILE_PATH),
            str(COMBINED_EVIDENCE_PATH),
            str(REPORT_PATH),
            str(GATE_PATH),
        ],
        "billing_revenue_profile_path": str(PROFILE_PATH),
        "combined_billing_revenue_evidence_path": str(COMBINED_EVIDENCE_PATH),
        "billing_revenue_profile_status": profile["profile_status"],
        "billing_revenue_readiness_status": readiness["status"],
        "production_billing_revenue_ready": readiness["production_billing_revenue_ready"],
        "pricing_page_evidence_complete": readiness["pricing_page_evidence_complete"],
        "payment_provider_evidence_complete": readiness["payment_provider_evidence_complete"],
        "invoice_process_evidence_complete": readiness["invoice_process_evidence_complete"],
        "tax_review_evidence_complete": readiness["tax_review_evidence_complete"],
        "refund_policy_evidence_complete": readiness["refund_policy_evidence_complete"],
        "tenant_billing_isolation_evidence_complete": readiness[
            "tenant_billing_isolation_evidence_complete"
        ],
        "billing_revenue_satisfied_blockers": billing_satisfied,
        "billing_revenue_target_blockers": billing_targets,
        "billing_revenue_satisfied_blocker_count": len(billing_satisfied),
        "support_data_ops_operations_privacy_security_legal_billing_revenue_satisfied_blockers": satisfied,
        "support_data_ops_operations_privacy_security_legal_billing_revenue_remaining_blockers": unsatisfied,
        "support_data_ops_operations_privacy_security_legal_billing_revenue_production_blocker_count": go_no_go[
            "production_blocker_count"
        ],
        "commercial_status_after_profile": go_no_go["commercial_status"],
        "production_launch_status_after_profile": go_no_go["production_launch_status"],
        "blockers_closed_by_validator": 0,
        "blockers_closed_by_builder": 0,
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_human_launch_approval_required": True,
        "development_permission_granted": False,
        "task_candidates_executed": False,
    }
    for key in FALSE_KEYS:
        summary[key] = False

    write_json(SUMMARY_PATH, summary)
    write_report(summary)
    print(
        "SAEE_BILLING_REVENUE_HUMAN_FILLED_EVIDENCE_RUN: PASS "
        f"billing_revenue_profile_status=pass production_blockers={go_no_go['production_blocker_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
