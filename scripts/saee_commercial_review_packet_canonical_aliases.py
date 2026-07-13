#!/usr/bin/env python3
"""Create canonical root-level aliases for commercial review packets.

The detailed human-review packets live in evidence subdirectories. This script
adds root-level agent-readable pointers for the canonical paths referenced by
the production-blocker coverage audit. It does not approve packets, collect
evidence, close blockers, contact customers, publish pricing, launch product,
or claim production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
OUTPUT_DIR = COMMERCIAL_DIR / "review_packet_canonical_aliases"
SUMMARY_JSON = OUTPUT_DIR / "review_packet_canonical_aliases.local.json"
SUMMARY_MD = OUTPUT_DIR / "review_packet_canonical_aliases.md"
TOP_DOC = COMMERCIAL_DIR / "COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES_RECOMMENDATION_GATE.md"


ALIASES: list[dict[str, Any]] = [
    {
        "packet_type": "saee_tenant_security_privacy_review_packet",
        "title": "Tenant Security / Privacy Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/TENANT_SECURITY_PRIVACY_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_security_privacy_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_security_privacy_review_packet.local.json",
        "blocker_targets": ["tenant_storage_isolation"],
    },
    {
        "packet_type": "saee_operations_monitoring_alert_review_packet",
        "title": "Operations Monitoring / Alert / On-call Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/OPERATIONS_MONITORING_ALERT_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/operations_evidence/operations_monitoring_alert_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/operations_evidence/operations_monitoring_alert_review_packet.local.json",
        "blocker_targets": ["production_monitoring", "external_alert_delivery", "on_call_rotation"],
    },
    {
        "packet_type": "saee_support_sla_on_call_review_packet",
        "title": "Support / SLA / On-call Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/SUPPORT_SLA_ON_CALL_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/support_evidence/support_sla_on_call_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/support_evidence/support_sla_on_call_review_packet.local.json",
        "blocker_targets": ["sla", "customer_support"],
    },
    {
        "packet_type": "saee_pricing_page_review_packet",
        "title": "Pricing Page Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/PRICING_PAGE_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_review_packet.local.json",
        "blocker_targets": ["pricing_page"],
    },
    {
        "packet_type": "saee_payment_provider_review_packet",
        "title": "Payment Provider Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/PAYMENT_PROVIDER_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/payment_provider_review_packet.local.json",
        "blocker_targets": ["payment_provider"],
    },
    {
        "packet_type": "saee_invoice_process_review_packet",
        "title": "Invoice Process Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/INVOICE_PROCESS_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/invoice_process_review_packet.local.json",
        "blocker_targets": ["invoice_process"],
    },
    {
        "packet_type": "saee_tax_review_packet",
        "title": "Tax Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/TAX_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/tax_review_packet.local.json",
        "blocker_targets": ["tax_review"],
    },
    {
        "packet_type": "saee_refund_policy_review_packet",
        "title": "Refund Policy Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/REFUND_POLICY_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/refund_policy_review_packet.local.json",
        "blocker_targets": ["refund_policy"],
    },
    {
        "packet_type": "saee_tenant_billing_isolation_review_packet",
        "title": "Tenant Billing Isolation Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/TENANT_BILLING_ISOLATION_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/billing_revenue_evidence/tenant_billing_isolation_review_packet.local.json",
        "blocker_targets": ["tenant_billing_isolation"],
    },
    {
        "packet_type": "saee_production_restore_policy_review_packet",
        "title": "Production Restore Policy Review Packet",
        "canonical_path": "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_REVIEW_PACKET_V0_1.md",
        "source_packet_path": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_review_packet.md",
        "source_packet_json": "phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_review_packet.local.json",
        "blocker_targets": ["production_restore_policy"],
    },
]


FALSE_BOUNDARY_FLAGS = {
    "blockers_closed_by_aliases": 0,
    "task_candidates_executed": False,
    "development_permission_granted": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "product_launched": False,
    "customer_contacted": False,
    "customer_validated": False,
    "production_ready": False,
    "production_ready_claim": False,
    "customer_validation_claim": False,
    "external_validation_success_claim": False,
    "public_sdk_released": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
}


def root_path(relative_path: str) -> Path:
    return ROOT / relative_path


def build_alias_doc(alias: dict[str, Any]) -> str:
    blocker_targets = ", ".join(alias["blocker_targets"])
    return f"""# SAEE {alias['title']} v0.1

canonical_review_packet_alias_v0_1: true
packet_type: {alias['packet_type']}
packet_status: draft_ready_for_human_review
canonical_path: {alias['canonical_path']}
source_packet_path: {alias['source_packet_path']}
source_packet_json: {alias['source_packet_json']}
blocker_targets: {blocker_targets}
human_review_required: true
separate_execution_approval_required: true
blocker_closure_allowed: false
blockers_closed_by_alias: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

This file is a canonical root-level pointer for AI agents and human reviewers.
The detailed packet remains in the source packet path above.

## What This Enables

- Easier discovery from the production blocker coverage audit.
- Stable root-level link target for agent-readable commercial readiness review.
- Faster navigation from a blocker to the relevant human-review packet.

## What This Does Not Do

- It does not approve the packet.
- It does not collect real evidence.
- It does not close `{blocker_targets}`.
- It does not publish customer-facing material.
- It does not contact customers or vendors.
- It does not modify runtime, backend, kernel, API schema, or private core.
- It does not make SAEE production-ready.

## Required Next Step

Use the source packet for human review. A blocker can close only after separate
real evidence is collected, reviewed, and explicitly approved.
"""


def build_payload() -> dict[str, Any]:
    enriched = []
    for alias in ALIASES:
        source_packet_exists = root_path(alias["source_packet_path"]).exists()
        source_json_exists = root_path(alias["source_packet_json"]).exists()
        canonical_exists = root_path(alias["canonical_path"]).exists()
        enriched.append(
            {
                **alias,
                "source_packet_exists": source_packet_exists,
                "source_packet_json_exists": source_json_exists,
                "canonical_alias_written": canonical_exists,
                "ready_for_agent_lookup": source_packet_exists and source_json_exists and canonical_exists,
                "blocker_closure_allowed": False,
                "human_review_required": True,
                "separate_execution_approval_required": True,
            }
        )

    missing_sources = [
        item["source_packet_path"]
        for item in enriched
        if not item["source_packet_exists"] or not item["source_packet_json_exists"]
    ]
    missing_aliases = [item["canonical_path"] for item in enriched if not item["canonical_alias_written"]]

    return {
        "commercial_review_packet_canonical_aliases_v0_1": True,
        "status": "ready_for_agent_lookup_no_blocker_closure"
        if not missing_sources and not missing_aliases
        else "hold_missing_canonical_alias_or_source",
        "generated_by": "scripts/saee_commercial_review_packet_canonical_aliases.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "alias_scope": "root_level_agent_readable_review_packet_pointers_only",
        "alias_count": len(enriched),
        "source_packet_count": sum(1 for item in enriched if item["source_packet_exists"]),
        "source_packet_json_count": sum(1 for item in enriched if item["source_packet_json_exists"]),
        "canonical_alias_count": sum(1 for item in enriched if item["canonical_alias_written"]),
        "missing_source_count": len(missing_sources),
        "missing_alias_count": len(missing_aliases),
        "missing_sources": missing_sources,
        "missing_aliases": missing_aliases,
        "ready_for_agent_lookup": not missing_sources and not missing_aliases,
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "aliases": enriched,
        **FALSE_BOUNDARY_FLAGS,
        "next_action": (
            "Run production blocker evidence path coverage audit again so the "
            "canonical review packet paths are visible in the blocker map. "
            "Do not close blockers without separate real evidence and approval."
        ),
    }


def render_summary(payload: dict[str, Any]) -> str:
    alias_lines = "\n".join(
        "- `{canonical}` -> `{source}` ({blockers})".format(
            canonical=item["canonical_path"],
            source=item["source_packet_path"],
            blockers=", ".join(item["blocker_targets"]),
        )
        for item in payload["aliases"]
    )
    return f"""# SAEE Commercial Review Packet Canonical Aliases v0.1

commercial_review_packet_canonical_aliases_v0_1: true
status: {payload['status']}
alias_scope: {payload['alias_scope']}
alias_count: {payload['alias_count']}
canonical_alias_count: {payload['canonical_alias_count']}
missing_alias_count: {payload['missing_alias_count']}
blockers_closed_by_aliases: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

This package creates root-level agent-readable pointers to existing
commercial review packets. It improves discovery and coverage audit alignment.
It does not create evidence, approve review content, close blockers, contact
customers, launch product, or claim production readiness.

## Canonical Aliases

{alias_lines}

## Boundary

- human_review_required: true
- separate_execution_approval_required: true
- blocker_closure_allowed: false
- blockers_closed_by_aliases: 0
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## Next Action

Run the production blocker evidence path coverage audit again. Human reviewers
may use the canonical files for navigation, but blocker closure still requires
separate real evidence and explicit approval.
"""


def render_gate(payload: dict[str, Any]) -> str:
    return f"""# SAEE Commercial Review Packet Canonical Aliases Recommendation Gate

answer: conditional

recommend_for_agent_lookup: true
recommend_for_blocker_closure: false
recommend_for_production_readiness_claim: false

reason:
The canonical aliases make existing commercial review packets easier for AI
agents and human reviewers to discover from root-level coverage paths. They do
not approve packets, collect evidence, close blockers, launch product, or claim
production readiness.

```yaml
commercial_review_packet_canonical_aliases_v0_1: true
status: {payload['status']}
alias_count: {payload['alias_count']}
missing_alias_count: {payload['missing_alias_count']}
blockers_closed_by_aliases: 0
human_review_required: true
separate_execution_approval_required: true
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

next_action:
Use these files as navigation pointers only. Do not close any production blocker
until real evidence is collected and separately approved by a human.
"""


def write_outputs() -> dict[str, Any]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    GATE.parent.mkdir(parents=True, exist_ok=True)

    for alias in ALIASES:
        destination = root_path(alias["canonical_path"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(build_alias_doc(alias), encoding="utf-8")

    payload = build_payload()
    SUMMARY_JSON.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    SUMMARY_MD.write_text(render_summary(payload), encoding="utf-8")
    TOP_DOC.write_text(render_summary(payload), encoding="utf-8")
    GATE.write_text(render_gate(payload), encoding="utf-8")
    return payload


def main() -> None:
    payload = write_outputs()
    print(
        "SAEE_COMMERCIAL_REVIEW_PACKET_CANONICAL_ALIASES: PASS "
        f"status={payload['status']} alias_count={payload['alias_count']} "
        "blockers_closed_by_aliases=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
