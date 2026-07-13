#!/usr/bin/env python3
"""Reconcile billing follow-up evidence without enabling revenue paths.

This local surface records that human-filled evidence for payment provider,
invoice process, tax review, refund policy, and tenant billing isolation is
ready for human review. It does not configure providers, enable checkout,
publish policies, contact advisors, close blockers, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
EVIDENCE_DIR = COMMERCIAL_DIR / "billing_revenue_evidence"
OUT_DIR = EVIDENCE_DIR / "billing_followup_state_reconciliation"
OUT_JSON = OUT_DIR / "billing_followup_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "billing_followup_state_reconciliation.md"
BOUNDARY = OUT_DIR / "billing_followup_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "BILLING_FOLLOWUP_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
LLMS = ROOT / "llms.txt"
STATUS_SURFACES = [
    ROOT / "README.md",
    ROOT / "PROJECT_STATUS.md",
    ROOT / "ROADMAP.md",
    ROOT / "CHANGELOG.md",
    ROOT / "agent-readable.md",
]

TARGETS = [
    "payment_provider",
    "invoice_process",
    "tax_review",
    "refund_policy",
    "tenant_billing_isolation",
]

SOURCES = {
    "payment_provider_validation": EVIDENCE_DIR
    / "payment_provider_approval_input_validation.human_filled.local.json",
    "payment_provider_builder": EVIDENCE_DIR
    / "payment_provider_evidence_builder_output.human_filled.local.json",
    "payment_provider_evidence": EVIDENCE_DIR
    / "production_billing_revenue_evidence.from_payment_provider.human_filled.local.json",
    "invoice_process_validation": EVIDENCE_DIR
    / "invoice_process_approval_input_validation.human_filled.local.json",
    "invoice_process_builder": EVIDENCE_DIR
    / "invoice_process_evidence_builder_output.human_filled.local.json",
    "invoice_process_evidence": EVIDENCE_DIR
    / "production_billing_revenue_evidence.from_invoice_process.human_filled.local.json",
    "tax_review_validation": EVIDENCE_DIR / "tax_review_approval_input_validation.human_filled.local.json",
    "tax_review_builder": EVIDENCE_DIR / "tax_review_evidence_builder_output.human_filled.local.json",
    "tax_review_evidence": EVIDENCE_DIR
    / "production_billing_revenue_evidence.from_tax_review.human_filled.local.json",
    "refund_policy_validation": EVIDENCE_DIR
    / "refund_policy_approval_input_validation.human_filled.local.json",
    "refund_policy_builder": EVIDENCE_DIR
    / "refund_policy_evidence_builder_output.human_filled.local.json",
    "refund_policy_evidence": EVIDENCE_DIR
    / "production_billing_revenue_evidence.from_refund_policy.human_filled.local.json",
    "tenant_billing_isolation_validation": EVIDENCE_DIR
    / "tenant_billing_isolation_approval_input_validation.human_filled.local.json",
    "tenant_billing_isolation_builder": EVIDENCE_DIR
    / "tenant_billing_isolation_evidence_builder_output.human_filled.local.json",
    "tenant_billing_isolation_evidence": EVIDENCE_DIR
    / "production_billing_revenue_evidence.from_tenant_billing_isolation.human_filled.local.json",
    "combined_billing_profile": EVIDENCE_DIR / "production_billing_revenue_evidence.combined_profile.local.json",
    "billing_profile": EVIDENCE_DIR / "billing_revenue_evidence_profile.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
}

FALSE_FLAGS = {
    "payment_provider_configured": False,
    "payment_provider_contacted": False,
    "payment_provider_live_mode_enabled": False,
    "codex_selected_payment_provider": False,
    "codex_configured_payment_provider": False,
    "codex_contacted_payment_provider": False,
    "codex_created_payment_link": False,
    "codex_enabled_checkout": False,
    "codex_processed_payment": False,
    "checkout_enabled": False,
    "invoice_sent_to_customer": False,
    "codex_created_invoice": False,
    "codex_sent_invoice": False,
    "codex_signed_contract": False,
    "codex_performed_reconciliation": False,
    "tax_advisor_contacted": False,
    "legal_counsel_contacted": False,
    "codex_contacted_tax_advisor": False,
    "codex_contacted_legal_counsel": False,
    "codex_configured_tax_collection": False,
    "codex_started_tax_collection": False,
    "tax_collection_started": False,
    "refund_policy_published": False,
    "codex_published_refund_policy": False,
    "codex_configured_refund_handling": False,
    "codex_processed_refund": False,
    "tenant_billing_isolated": False,
    "tenant_billing_isolation_enabled": False,
    "tenant_billing_transaction_processed": False,
    "codex_configured_tenant_billing_handling": False,
    "codex_processed_tenant_billing": False,
    "codex_published_tenant_billing_isolation": False,
    "production_billing_enabled": False,
    "revenue_validated": False,
    "customer_payment_collected": False,
    "customer_contacted": False,
    "customer_validated": False,
    "paid_product_launched": False,
    "product_launched": False,
    "production_ready": False,
    "production_billing_revenue_ready": False,
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
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def ensure_line(path: Path, line: str) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if line not in text.splitlines():
        path.write_text(text.rstrip() + "\n" + line + "\n", encoding="utf-8")


def replace_block(path: Path, marker: str, body: str) -> None:
    start = f"<!-- {marker}:START -->"
    end = f"<!-- {marker}:END -->"
    block = f"{start}\n{body.rstrip()}\n{end}\n"
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    if start in text and end in text:
        before = text.split(start, 1)[0]
        after = text.split(end, 1)[1]
        path.write_text(before.rstrip() + "\n\n" + block + after.lstrip(), encoding="utf-8")
    else:
        path.write_text(text.rstrip() + "\n\n" + block, encoding="utf-8")


def find_row(data: dict[str, Any], blocker_id: str) -> dict[str, Any]:
    rows = data.get("matrix") or data.get("rows") or data.get("blockers") or []
    if not isinstance(rows, list):
        return {}
    for row in rows:
        if isinstance(row, dict) and row.get("blocker_id") == blocker_id:
            return row
    return {}


def base_item_ready(data: dict[str, dict[str, Any]], blocker_id: str) -> bool:
    validation = data[f"{blocker_id}_validation"]
    builder = data[f"{blocker_id}_builder"]
    evidence = data[f"{blocker_id}_evidence"]
    return (
        validation.get("validation_status") == "pass"
        and validation.get("input_complete") is True
        and builder.get("status") == "pass"
        and builder.get(f"{blocker_id}_evidence_complete_for_review") is True
        and evidence.get("production_ready") is False
        and evidence.get("product_launched") is False
        and evidence.get("customer_contacted") is False
        and evidence.get("private_core_exposed") is False
    )


def build_payload() -> dict[str, Any]:
    source_data = {name: read_json(path) for name, path in SOURCES.items()}
    gap = source_data["gap_matrix"]
    board = source_data["closure_readiness_board"]
    billing_profile = source_data["billing_profile"]

    readiness = {
        "payment_provider": base_item_ready(source_data, "payment_provider")
        and source_data["payment_provider_evidence"].get("payment_provider_selected") is True
        and source_data["payment_provider_evidence"].get("payment_provider_configured") is False
        and source_data["payment_provider_evidence"].get("codex_enabled_checkout") is False,
        "invoice_process": base_item_ready(source_data, "invoice_process")
        and source_data["invoice_process_evidence"].get("invoice_workflow_approved") is True
        and source_data["invoice_process_evidence"].get("billing_support_handoff_defined") is True
        and source_data["invoice_process_evidence"].get("codex_sent_invoice") is False,
        "tax_review": base_item_ready(source_data, "tax_review")
        and source_data["tax_review_evidence"].get("currency_policy_approved") is True
        and source_data["tax_review_evidence"].get("invoice_wording_approved") is True
        and source_data["tax_review_evidence"].get("tax_advisor_contacted") is False,
        "refund_policy": base_item_ready(source_data, "refund_policy")
        and source_data["refund_policy_evidence"].get("refund_policy_approved") is True
        and source_data["refund_policy_evidence"].get("service_failure_remedy_boundary_approved") is True
        and source_data["refund_policy_evidence"].get("refund_policy_published") is False,
        "tenant_billing_isolation": base_item_ready(source_data, "tenant_billing_isolation")
        and source_data["tenant_billing_isolation_evidence"].get("tenant_billing_account_model_approved") is True
        and source_data["tenant_billing_isolation_evidence"].get("tenant_billing_retention_policy_approved") is True
        and source_data["tenant_billing_isolation_evidence"].get("cross_tenant_billing_access_tests_passed") is True
        and source_data["tenant_billing_isolation_evidence"].get("tenant_billing_isolation_enabled") is False,
    }
    all_ready = all(readiness.values())
    any_ready = any(readiness.values())
    gap_open = {bid: find_row(gap, bid).get("status") == "open" for bid in TARGETS}
    board_not_ready = {
        bid: find_row(board, bid).get("status") in {"not_ready", None, ""} for bid in TARGETS
    }

    if all_ready:
        status = "ready_for_human_billing_followup_review_no_closure"
        resolved_path = "individual_human_filled_evidence_outputs"
        next_action = (
            "Human commercial owner may review billing follow-up evidence for a later "
            "matrix update request. Do not configure payment, enable checkout, publish "
            "policies, contact advisors, close blockers, or claim production readiness."
        )
    elif any_ready:
        status = "partial_billing_followup_review_ready_no_closure"
        resolved_path = "partial_individual_evidence_outputs"
        next_action = "Review ready billing evidence only; no closure or revenue enablement is allowed."
    else:
        status = "hold_billing_followup_human_input_required"
        resolved_path = "approval_input_validation"
        next_action = "Complete human-filled billing/revenue input before follow-up review."

    payload: dict[str, Any] = {
        "billing_followup_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_billing_followup_state_reconciliation_no_payment_no_checkout_no_closure",
        "target_blocker_ids": TARGETS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "resolved_current_path": resolved_path,
        "payment_provider_ready_for_review": readiness["payment_provider"],
        "invoice_process_ready_for_review": readiness["invoice_process"],
        "tax_review_ready_for_review": readiness["tax_review"],
        "refund_policy_ready_for_review": readiness["refund_policy"],
        "tenant_billing_isolation_ready_for_review": readiness["tenant_billing_isolation"],
        "ready_for_review_count": sum(1 for value in readiness.values() if value),
        "combined_billing_profile_status": billing_profile.get("profile_status"),
        "combined_billing_profile_readiness_status": billing_profile.get("billing_revenue_readiness_status"),
        "combined_billing_profile_target_blockers_satisfied_count": billing_profile.get(
            "target_blockers_satisfied_count"
        ),
        "gap_matrix_open_by_blocker": gap_open,
        "closure_board_not_ready_by_blocker": board_not_ready,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "next_human_action": next_action,
        "why_this_exists": (
            "Human-filled billing follow-up evidence can be ready for commercial "
            "review while canonical blocker surfaces remain open. This file records "
            "review readiness without enabling revenue operations or closing blockers."
        ),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Billing Follow-up State Reconciliation v0.1

Status: `{payload['status']}`

This local board reconciles billing/revenue follow-up evidence for
`payment_provider`, `invoice_process`, `tax_review`, `refund_policy`, and
`tenant_billing_isolation`. It does not configure payment providers, enable
checkout, send invoices, contact tax or legal advisors, publish refund policy,
close blockers, or claim production readiness.

## Current Finding

- target_blocker_ids: `payment_provider`, `invoice_process`, `tax_review`, `refund_policy`, `tenant_billing_isolation`
- payment_provider_ready_for_review: `{str(payload['payment_provider_ready_for_review']).lower()}`
- invoice_process_ready_for_review: `{str(payload['invoice_process_ready_for_review']).lower()}`
- tax_review_ready_for_review: `{str(payload['tax_review_ready_for_review']).lower()}`
- refund_policy_ready_for_review: `{str(payload['refund_policy_ready_for_review']).lower()}`
- tenant_billing_isolation_ready_for_review: `{str(payload['tenant_billing_isolation_ready_for_review']).lower()}`
- ready_for_review_count: `{payload['ready_for_review_count']}`
- combined_billing_profile_status: `{payload['combined_billing_profile_status']}`
- combined_billing_profile_readiness_status: `{payload['combined_billing_profile_readiness_status']}`
- resolved_current_path: `{payload['resolved_current_path']}`

## Next Human Action

{payload['next_human_action']}

## Boundary

- payment_provider_configured=false
- codex_enabled_checkout=false
- invoice_sent_to_customer=false
- tax_advisor_contacted=false
- refund_policy_published=false
- tenant_billing_isolation_enabled=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Billing Follow-up State Reconciliation Boundary Audit

- Only local status and agent-readable evidence surfaces were written.
- No payment provider configured.
- No payment provider contacted by Codex.
- No checkout enabled.
- No payment link created.
- No payment processed.
- No invoice sent to a customer.
- No tax advisor or legal counsel contacted.
- No tax collection started.
- No refund policy published.
- No refund processed.
- No tenant billing isolation enabled.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No public SDK released.
- No blocker closed.
- No production-ready claim added.

payment_provider_configured=false
codex_enabled_checkout=false
invoice_sent_to_customer=false
tax_advisor_contacted=false
refund_policy_published=false
tenant_billing_isolation_enabled=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Billing Follow-up State Reconciliation v0.1

status: {payload['status']}
target_blocker_ids: payment_provider,invoice_process,tax_review,refund_policy,tenant_billing_isolation
resolved_current_path: {payload['resolved_current_path']}
payment_provider_ready_for_review: {str(payload['payment_provider_ready_for_review']).lower()}
invoice_process_ready_for_review: {str(payload['invoice_process_ready_for_review']).lower()}
tax_review_ready_for_review: {str(payload['tax_review_ready_for_review']).lower()}
refund_policy_ready_for_review: {str(payload['refund_policy_ready_for_review']).lower()}
tenant_billing_isolation_ready_for_review: {str(payload['tenant_billing_isolation_ready_for_review']).lower()}
ready_for_review_count: {payload['ready_for_review_count']}
human_review_required: true
separate_matrix_update_request_required: true
payment_provider_configured=false
codex_enabled_checkout=false
invoice_sent_to_customer=false
tax_advisor_contacted=false
refund_policy_published=false
tenant_billing_isolation_enabled=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false

This is a local state reconciliation layer for billing follow-up evidence. It
may point a human reviewer to source-backed billing/revenue evidence, but it
does not enable revenue operations, update the production blocker matrix, close
blockers, or claim production readiness.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Billing Follow-up State Reconciliation Gate

answer: hold_human_billing_followup_review_required_no_payment_no_checkout_no_auto_closure

reason:
Human-filled billing/revenue follow-up evidence can be reviewed, but Codex has
not configured payment providers, enabled checkout, contacted advisors, sent
invoices, changed runtime behavior, or closed blockers.

status: {payload['status']}
target_blocker_ids: payment_provider,invoice_process,tax_review,refund_policy,tenant_billing_isolation
resolved_current_path: {payload['resolved_current_path']}

boundary:
payment_provider_configured: false
codex_enabled_checkout: false
invoice_sent_to_customer: false
tax_advisor_contacted: false
refund_policy_published: false
tenant_billing_isolation_enabled: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
product_launched: false
production_ready: false
customer_validated: false
blockers_closed_by_reconciliation: 0

next_action:
Human commercial owner may review the state reconciliation and decide whether a
separate matrix update request should be created. This gate does not authorize
execution, payment enablement, publication, or closure.
""",
        encoding="utf-8",
    )

    block = f"""## Billing Follow-up State Reconciliation v0.1

Status: `{payload['status']}`.

`payment_provider`, `invoice_process`, `tax_review`, `refund_policy`, and
`tenant_billing_isolation` human-filled evidence is reconciled into a review-only
state. `ready_for_review_count={payload['ready_for_review_count']}`,
`payment_provider_ready_for_review={str(payload['payment_provider_ready_for_review']).lower()}`,
`invoice_process_ready_for_review={str(payload['invoice_process_ready_for_review']).lower()}`,
`tax_review_ready_for_review={str(payload['tax_review_ready_for_review']).lower()}`,
`refund_policy_ready_for_review={str(payload['refund_policy_ready_for_review']).lower()}`,
`tenant_billing_isolation_ready_for_review={str(payload['tenant_billing_isolation_ready_for_review']).lower()}`,
`blockers_closed_by_reconciliation=0`, `production_ready=false`,
`customer_validated=false`, `product_launched=false`, and
`private_core_exposed=false`. No payment provider was configured, no checkout
was enabled, no invoice was sent, and no tax/legal advisor or customer was
contacted by Codex.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION", block)

    for line in [
        "/phase_b_product/commercial_readiness/BILLING_FOLLOWUP_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/billing_revenue_evidence/billing_followup_state_reconciliation/billing_followup_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_billing_followup_state_reconciliation.py",
        "/scripts/saee_billing_followup_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["billing_followup_state_reconciliation_v0_1"] = {
        "status": payload["status"],
        "target_blocker_ids": payload["target_blocker_ids"],
        "resolved_current_path": payload["resolved_current_path"],
        "payment_provider_ready_for_review": payload["payment_provider_ready_for_review"],
        "invoice_process_ready_for_review": payload["invoice_process_ready_for_review"],
        "tax_review_ready_for_review": payload["tax_review_ready_for_review"],
        "refund_policy_ready_for_review": payload["refund_policy_ready_for_review"],
        "tenant_billing_isolation_ready_for_review": payload["tenant_billing_isolation_ready_for_review"],
        "ready_for_review_count": payload["ready_for_review_count"],
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "payment_provider_configured": False,
        "codex_enabled_checkout": False,
        "invoice_sent_to_customer": False,
        "tax_advisor_contacted": False,
        "refund_policy_published": False,
        "tenant_billing_isolation_enabled": False,
        "blockers_closed_by_reconciliation": 0,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    write_json(AGENT_INDEX, index)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_BILLING_FOLLOWUP_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
