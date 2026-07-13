#!/usr/bin/env python3
"""Build the SAEE commercial launch blocker work order.

This script converts the current local commercial go/no-go report into a
machine-readable work order for human review. It does not execute blockers,
approve launch, contact customers, call external services, or modify SAEE
runtime behavior.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go


JSON_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.json"
MD_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_LAUNCH_BLOCKER_WORK_ORDER_V0_1.md"


EVIDENCE_REQUIREMENTS = {
    "production_identity_provider": "Production identity-provider configuration, security review, and operator runbook.",
    "oauth_oidc": "OIDC issuer, client, callback, token validation, and logout behavior evidence.",
    "rbac": "Role model, permission matrix, enforcement tests, and admin recovery process.",
    "tenant_storage_isolation": "Tenant-isolated storage design, migration proof, and cross-tenant isolation tests.",
    "production_monitoring": "Production metrics, dashboard, retention, alert review, and incident linkage evidence.",
    "external_alert_delivery": "External alert destination, escalation route, delivery test, and failure handling evidence.",
    "on_call_rotation": "Named on-call process, escalation schedule, handoff rules, and coverage evidence.",
    "sla": "Human-approved SLA terms, exclusions, support hours, and response target approval.",
    "support_contact": "Customer-facing support intake contact, ownership, response procedure, and abuse handling.",
    "customer_support": "Staffed support process, triage workflow, customer communication template, and audit trail.",
    "formal_security_review": "Completed security review report covering public shell, deployment, data, and access control.",
    "privacy_legal_review": "Completed legal privacy review for collected data, processors, notices, and retention.",
    "data_processing_agreement": "Approved DPA or equivalent customer data-processing agreement ready for use.",
    "vulnerability_management": "Vulnerability disclosure policy, triage process, remediation targets, and security contact.",
    "pilot_results": "Recorded pilot sessions, user feedback, failure notes, and permission to use evidence.",
    "customer_validated": "Real customer validation evidence reviewed and approved for use in product claims.",
    "pricing_page": "Human-approved public pricing or packaging page with current commercial terms.",
    "payment_provider": "Configured payment provider in the intended environment with checkout disabled until approval.",
    "invoice_process": "Invoice workflow, contract handoff, bookkeeping process, and payment reconciliation evidence.",
    "tax_review": "Tax review for target jurisdictions, invoice wording, and payment collection process.",
    "refund_policy": "Human-approved refund/cancellation policy connected to payment and support processes.",
    "tenant_billing_isolation": "Tenant-aware billing records, invoice partitioning, and payment-event isolation evidence.",
    "restore_tested": "Successful restore test with manifest, scope, non-live path proof, and operator review.",
    "production_restore_policy": "Approved production restore policy with RPO/RTO targets and drill cadence.",
}


BLOCKER_TRIAGE = {
    "production_identity_provider": {
        "resolution_lane": "engineering_with_external_service",
        "sequence_group": "identity_and_tenant_boundary",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": True,
    },
    "oauth_oidc": {
        "resolution_lane": "engineering_with_external_service",
        "sequence_group": "identity_and_tenant_boundary",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": True,
    },
    "rbac": {
        "resolution_lane": "engineering_local_design",
        "sequence_group": "identity_and_tenant_boundary",
        "can_prepare_locally_now": True,
        "external_dependency_required": False,
        "engineering_implementation_required": True,
    },
    "tenant_storage_isolation": {
        "resolution_lane": "engineering_local_design",
        "sequence_group": "identity_and_tenant_boundary",
        "can_prepare_locally_now": True,
        "external_dependency_required": False,
        "engineering_implementation_required": True,
    },
    "production_monitoring": {
        "resolution_lane": "engineering_with_external_service",
        "sequence_group": "operations_resilience",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": True,
    },
    "external_alert_delivery": {
        "resolution_lane": "engineering_with_external_service",
        "sequence_group": "operations_resilience",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": True,
    },
    "on_call_rotation": {
        "resolution_lane": "human_operations_evidence",
        "sequence_group": "operations_resilience",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "sla": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "support_contact": {
        "resolution_lane": "human_operations_evidence",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "customer_support": {
        "resolution_lane": "human_operations_evidence",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "formal_security_review": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "privacy_legal_review": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "data_processing_agreement": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "vulnerability_management": {
        "resolution_lane": "human_operations_evidence",
        "sequence_group": "support_security_legal",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "pilot_results": {
        "resolution_lane": "customer_validation_evidence",
        "sequence_group": "customer_validation_and_launch",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "customer_validated": {
        "resolution_lane": "customer_validation_evidence",
        "sequence_group": "customer_validation_and_launch",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "pricing_page": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "billing_and_packaging",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "payment_provider": {
        "resolution_lane": "engineering_with_external_service",
        "sequence_group": "billing_and_packaging",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": True,
    },
    "invoice_process": {
        "resolution_lane": "human_operations_evidence",
        "sequence_group": "billing_and_packaging",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "tax_review": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "billing_and_packaging",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "refund_policy": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "billing_and_packaging",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
    "tenant_billing_isolation": {
        "resolution_lane": "engineering_local_design",
        "sequence_group": "billing_and_packaging",
        "can_prepare_locally_now": True,
        "external_dependency_required": False,
        "engineering_implementation_required": True,
    },
    "restore_tested": {
        "resolution_lane": "engineering_local_design",
        "sequence_group": "data_operations",
        "can_prepare_locally_now": True,
        "external_dependency_required": False,
        "engineering_implementation_required": True,
    },
    "production_restore_policy": {
        "resolution_lane": "legal_business_approval",
        "sequence_group": "data_operations",
        "can_prepare_locally_now": False,
        "external_dependency_required": True,
        "engineering_implementation_required": False,
    },
}


def triage_for(blocker_id: str) -> dict[str, Any]:
    return BLOCKER_TRIAGE.get(
        blocker_id,
        {
            "resolution_lane": "human_operations_evidence",
            "sequence_group": "unclassified",
            "can_prepare_locally_now": False,
            "external_dependency_required": True,
            "engineering_implementation_required": False,
        },
    )


def blocker_work_item(blocker: dict[str, Any]) -> dict[str, Any]:
    blocker_id = str(blocker["blocker_id"])
    triage = triage_for(blocker_id)
    return {
        "blocker_id": blocker_id,
        "category": blocker["category"],
        "can_prepare_locally_now": triage["can_prepare_locally_now"],
        "scope": blocker["scope"],
        "engineering_implementation_required": triage[
            "engineering_implementation_required"
        ],
        "external_dependency_required": triage["external_dependency_required"],
        "resolution_lane": triage["resolution_lane"],
        "sequence_group": triage["sequence_group"],
        "status": "open",
        "source_message": blocker["message"],
        "required_evidence": EVIDENCE_REQUIREMENTS.get(
            blocker_id,
            "Human-reviewed completion evidence for this commercial blocker.",
        ),
        "allowed_next_action": "create a separate human-approved task with evidence before closing this blocker",
        "forbidden_actions": [
            "do_not_mark_production_ready_from_this_work_order",
            "do_not_launch_product_from_this_work_order",
            "do_not_contact_customers_from_this_work_order",
            "do_not_modify_runtime_backend_kernel_or_api_schema_from_this_work_order",
            "do_not_expose_private_core",
        ],
        "requires_human_approval": True,
        "execution_allowed_by_this_work_order": False,
        "can_close_without_evidence": False,
    }


def build_work_order(settings: SaeeBackendSettings = SETTINGS) -> dict[str, Any]:
    report = evaluate_commercial_go_no_go(settings)
    blockers = [blocker_work_item(item) for item in report["unsatisfied_blockers"]]
    category_counts = Counter(str(item["category"]) for item in blockers)
    lane_counts = Counter(str(item["resolution_lane"]) for item in blockers)
    sequence_group_counts = Counter(str(item["sequence_group"]) for item in blockers)
    locally_preparable = [
        item["blocker_id"] for item in blockers if item["can_prepare_locally_now"]
    ]
    external_dependent = [
        item["blocker_id"] for item in blockers if item["external_dependency_required"]
    ]
    engineering_required = [
        item["blocker_id"]
        for item in blockers
        if item["engineering_implementation_required"]
    ]

    return {
        "work_order_type": "commercial_launch_blocker_work_order",
        "work_order_version": "v0.1",
        "source_report": "commercial_go_no_go_v0_1",
        "commercial_status": report["commercial_status"],
        "controlled_preview_status": report["controlled_preview_status"],
        "controlled_preview_policy": "go_if_commercial_preflight_passes",
        "production_launch_status": report["production_launch_status"],
        "production_blocker_count": report["production_blocker_count"],
        "work_order_status": "hold",
        "blockers_closed": 0,
        "category_counts": dict(sorted(category_counts.items())),
        "resolution_lane_counts": dict(sorted(lane_counts.items())),
        "sequence_group_counts": dict(sorted(sequence_group_counts.items())),
        "locally_preparable_blocker_count": len(locally_preparable),
        "locally_preparable_blockers": locally_preparable,
        "external_dependency_blocker_count": len(external_dependent),
        "external_dependency_blockers": external_dependent,
        "engineering_implementation_blocker_count": len(engineering_required),
        "engineering_implementation_blockers": engineering_required,
        "blockers": blockers,
        "human_approval_required": True,
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
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "next_action": "review open blockers and create separate human-approved tasks for selected blockers",
    }


def render_markdown(work_order: dict[str, Any]) -> str:
    rows = []
    for item in work_order["blockers"]:
        rows.append(
            "| {blocker_id} | {category} | {lane} | {local} | {external} | {status} | {required_evidence} | {approval} | {execution} |".format(
                blocker_id=item["blocker_id"],
                category=item["category"],
                lane=item["resolution_lane"],
                local="yes" if item["can_prepare_locally_now"] else "no",
                external="yes" if item["external_dependency_required"] else "no",
                status=item["status"],
                required_evidence=item["required_evidence"],
                approval="yes" if item["requires_human_approval"] else "no",
                execution="no" if not item["execution_allowed_by_this_work_order"] else "yes",
            )
        )

    return "\n".join(
        [
            "# SAEE Commercial Launch Blocker Work Order v0.1",
            "",
            "This work order converts the current local commercial go/no-go blockers into",
            "machine-readable human-review items. It does not execute any blocker, approve",
            "production launch, contact customers, call external services, modify runtime",
            "behavior, modify backend core logic, modify the API schema, or expose private",
            "core internals.",
            "",
            "## Status",
            "",
            f"- work_order_type: {work_order['work_order_type']}",
            f"- work_order_status: {work_order['work_order_status']}",
            f"- commercial_status: {work_order['commercial_status']}",
            f"- controlled_preview_status: {work_order['controlled_preview_status']}",
            f"- controlled_preview_policy: {work_order['controlled_preview_policy']}",
            f"- production_launch_status: {work_order['production_launch_status']}",
            f"- production_blocker_count: {work_order['production_blocker_count']}",
            f"- blockers_closed: {work_order['blockers_closed']}",
            f"- locally_preparable_blocker_count: {work_order['locally_preparable_blocker_count']}",
            f"- external_dependency_blocker_count: {work_order['external_dependency_blocker_count']}",
            f"- engineering_implementation_blocker_count: {work_order['engineering_implementation_blocker_count']}",
            "- human_approval_required: true",
            "- task_candidates_executed: false",
            "- development_permission_granted: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Category Counts",
            "",
            *[
                f"- {category}: {count}"
                for category, count in work_order["category_counts"].items()
            ],
            "",
            "## Resolution Lane Counts",
            "",
            *[
                f"- {lane}: {count}"
                for lane, count in work_order["resolution_lane_counts"].items()
            ],
            "",
            "## Sequence Group Counts",
            "",
            *[
                f"- {group}: {count}"
                for group, count in work_order["sequence_group_counts"].items()
            ],
            "",
            "## Locally Preparable Blockers",
            "",
            "These blockers can have local design or implementation preparation work",
            "started later through separate human approval. This work order itself",
            "does not authorize that work and does not close them.",
            "",
            *[f"- {blocker_id}" for blocker_id in work_order["locally_preparable_blockers"]],
            "",
            "## External Dependency Blockers",
            "",
            "These blockers need an external provider, customer action, legal/business",
            "approval, or staffed operational process before they can be closed.",
            "",
            *[f"- {blocker_id}" for blocker_id in work_order["external_dependency_blockers"]],
            "",
            "## Open Blockers",
            "",
            "| Blocker | Category | Resolution lane | Local prep possible | External dependency | Status | Required evidence | Human approval | Execution allowed here |",
            "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
            *rows,
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this work order.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No product launch is authorized.",
            "- No customer contact is authorized.",
            "- No backend runtime, kernel, API schema, or private core is modified.",
            "- Each blocker requires a separate human-approved task and evidence before it can be closed.",
            "",
        ]
    )


def write_artifacts(work_order: dict[str, Any]) -> None:
    JSON_PATH.write_text(json.dumps(work_order, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MD_PATH.write_text(render_markdown(work_order), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="write JSON and Markdown artifacts")
    args = parser.parse_args()

    work_order = build_work_order()
    if args.write:
        write_artifacts(work_order)
    print(json.dumps(work_order, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
