#!/usr/bin/env python3
"""Build the SAEE commercial blocker dependency plan.

This script turns the current production blocker gap matrix into a staged,
agent-readable dependency plan. It is local planning only: it does not execute
blocker work, close blockers, contact customers, call external services, launch
product, claim production readiness, or modify runtime/backend/kernel/API
schema/private-core behavior.
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_production_blocker_gap_matrix import build_gap_matrix


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan"
PLAN_JSON = OUTPUT_DIR / "dependency_plan.local.json"
PLAN_MD = OUTPUT_DIR / "dependency_plan.local.md"
PLAN_CSV = OUTPUT_DIR / "dependency_plan.local.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_RECOMMENDATION_GATE.md"


PHASES: list[dict[str, object]] = [
    {
        "phase_id": "phase_1_identity_and_tenant_boundary",
        "title": "Identity, authorization, and tenant boundary",
        "objective": "Establish production identity, authorization, and tenant isolation evidence before multi-tenant or paid use.",
        "blocker_ids": [
            "production_identity_provider",
            "oauth_oidc",
            "rbac",
            "tenant_storage_isolation",
        ],
        "depends_on": [],
        "exit_evidence": [
            "production identity-provider approval",
            "OIDC validation evidence",
            "RBAC enforcement tests",
            "tenant storage isolation tests",
        ],
    },
    {
        "phase_id": "phase_2_data_and_operations_resilience",
        "title": "Data recovery and production operations",
        "objective": "Establish recoverability, monitoring, alert delivery, and operational ownership evidence.",
        "blocker_ids": [
            "production_restore_policy",
            "restore_tested",
            "production_monitoring",
            "external_alert_delivery",
            "on_call_rotation",
        ],
        "depends_on": ["phase_1_identity_and_tenant_boundary"],
        "exit_evidence": [
            "approved production restore policy",
            "restore drill report",
            "production monitoring dashboard evidence",
            "external alert delivery test",
            "on-call rotation approval",
        ],
    },
    {
        "phase_id": "phase_3_support_security_legal",
        "title": "Support, security, privacy, and legal readiness",
        "objective": "Establish customer-facing support, security review, privacy/legal review, and data-processing evidence.",
        "blocker_ids": [
            "support_contact",
            "customer_support",
            "sla",
            "formal_security_review",
            "privacy_legal_review",
            "data_processing_agreement",
            "vulnerability_management",
        ],
        "depends_on": [
            "phase_1_identity_and_tenant_boundary",
            "phase_2_data_and_operations_resilience",
        ],
        "exit_evidence": [
            "customer-facing support intake approval",
            "staffed support process",
            "approved SLA",
            "formal security review",
            "privacy legal approval",
            "approved DPA",
            "vulnerability management policy",
        ],
    },
    {
        "phase_id": "phase_4_commercial_packaging_and_billing",
        "title": "Commercial packaging and billing controls",
        "objective": "Establish pricing, billing, invoice, tax, refund, and tenant-billing evidence without enabling paid use prematurely.",
        "blocker_ids": [
            "pricing_page",
            "payment_provider",
            "invoice_process",
            "tax_review",
            "refund_policy",
            "tenant_billing_isolation",
        ],
        "depends_on": [
            "phase_1_identity_and_tenant_boundary",
            "phase_3_support_security_legal",
        ],
        "exit_evidence": [
            "human-approved pricing or packaging",
            "payment-provider configuration review",
            "invoice workflow approval",
            "tax review",
            "refund policy",
            "tenant billing isolation evidence",
        ],
    },
    {
        "phase_id": "phase_5_customer_validation_and_launch_review",
        "title": "Customer validation and launch review",
        "objective": "Collect human-approved pilot evidence and run final launch review only after operational, legal, and commercial controls exist.",
        "blocker_ids": [
            "pilot_results",
            "customer_validated",
        ],
        "depends_on": [
            "phase_2_data_and_operations_resilience",
            "phase_3_support_security_legal",
            "phase_4_commercial_packaging_and_billing",
        ],
        "exit_evidence": [
            "completed pilot result records",
            "customer value evidence",
            "claim permission review",
            "final human launch decision",
        ],
    },
]


BLOCKER_DEPENDENCIES: dict[str, list[str]] = {
    "oauth_oidc": ["production_identity_provider"],
    "rbac": ["production_identity_provider", "oauth_oidc"],
    "tenant_storage_isolation": ["rbac"],
    "restore_tested": ["production_restore_policy"],
    "external_alert_delivery": ["production_monitoring"],
    "on_call_rotation": ["production_monitoring", "external_alert_delivery"],
    "customer_support": ["support_contact"],
    "sla": ["support_contact", "customer_support"],
    "data_processing_agreement": ["privacy_legal_review"],
    "vulnerability_management": ["formal_security_review"],
    "payment_provider": ["pricing_page", "tax_review", "refund_policy"],
    "invoice_process": ["pricing_page", "tax_review"],
    "tenant_billing_isolation": ["tenant_storage_isolation", "payment_provider"],
    "pilot_results": [
        "support_contact",
        "privacy_legal_review",
        "data_processing_agreement",
        "production_monitoring",
    ],
    "customer_validated": ["pilot_results"],
}


def _phase_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}
    for phase in PHASES:
        for blocker_id in phase["blocker_ids"]:  # type: ignore[index]
            lookup[str(blocker_id)] = str(phase["phase_id"])
    return lookup


def _reverse_dependencies(blocker_ids: list[str]) -> dict[str, list[str]]:
    reverse = {blocker_id: [] for blocker_id in blocker_ids}
    for blocker_id, deps in BLOCKER_DEPENDENCIES.items():
        for dep in deps:
            if dep in reverse:
                reverse[dep].append(blocker_id)
    return {key: sorted(value) for key, value in reverse.items()}


def _planned_blocker(item: dict[str, Any], phase_by_blocker: dict[str, str], reverse: dict[str, list[str]]) -> dict[str, Any]:
    blocker_id = str(item["blocker_id"])
    dependencies = BLOCKER_DEPENDENCIES.get(blocker_id, [])
    return {
        "blocker_id": blocker_id,
        "category": item["category"],
        "phase_id": phase_by_blocker[blocker_id],
        "status": "open",
        "depends_on_blockers": dependencies,
        "unblocks_blockers": reverse.get(blocker_id, []),
        "can_start_without_external_dependency": not bool(item["external_dependency_required"]),
        "engineering_implementation_required": bool(item["engineering_implementation_required"]),
        "external_dependency_required": bool(item["external_dependency_required"]),
        "required_evidence": item["required_evidence"],
        "local_evidence_path": item["local_evidence_path"],
        "owner_review_lane": item["owner_review_lane"],
        "default_decision": "hold",
        "requires_human_approval": True,
        "requires_separate_execution_request": True,
        "execution_allowed_by_plan": False,
        "closure_allowed_by_plan": False,
        "next_human_action": "Open a separate evidence task only after dependencies are satisfied and human approval is explicit.",
    }


def build_dependency_plan() -> dict[str, Any]:
    """Build a staged commercial blocker dependency plan."""

    gap_matrix = build_gap_matrix()
    matrix_items = gap_matrix["matrix"]
    blocker_ids = [str(item["blocker_id"]) for item in matrix_items]
    phase_by_blocker = _phase_lookup()
    missing_phase = sorted(set(blocker_ids) - set(phase_by_blocker))
    if missing_phase:
        raise RuntimeError("missing phase mapping for blockers: " + ", ".join(missing_phase))
    reverse = _reverse_dependencies(blocker_ids)
    blockers = [
        _planned_blocker(item, phase_by_blocker, reverse)
        for item in matrix_items
    ]
    blocker_by_id = {item["blocker_id"]: item for item in blockers}
    phases = []
    for phase in PHASES:
        phase_blockers = [blocker_by_id[blocker_id] for blocker_id in phase["blocker_ids"]]  # type: ignore[index]
        phases.append(
            {
                **phase,
                "blocker_count": len(phase_blockers),
                "open_blocker_count": len(phase_blockers),
                "execution_allowed_by_phase": False,
                "closure_allowed_by_phase": False,
                "requires_human_approval": True,
                "default_decision": "hold",
            }
        )

    return {
        "plan_type": "saee_commercial_blocker_dependency_plan",
        "plan_version": "v0.1",
        "plan_scope": "local_commercial_blocker_dependency_planning",
        "generated_by": "scripts/saee_commercial_blocker_dependency_plan.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_gap_matrix": "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json",
        "source_go_no_go": "scripts/saee_commercial_go_no_go.py",
        "production_launch_status": gap_matrix["production_launch_status"],
        "production_blocker_count": gap_matrix["production_blocker_count"],
        "planned_blocker_count": len(blockers),
        "open_blocker_count": len(blockers),
        "phase_count": len(phases),
        "blockers_closed_by_plan": 0,
        "plan_status": "hold",
        "phases": phases,
        "blockers": blockers,
        "human_review_required": True,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        "execution_authorized": False,
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
        "next_action": "Human reviewers should choose one phase, then open a separate evidence task for one blocker; this plan itself authorizes no execution or launch.",
    }


def render_markdown(plan: dict[str, Any]) -> str:
    phase_rows = [
        "| {phase_id} | {title} | {count} | {deps} | no |".format(
            phase_id=phase["phase_id"],
            title=phase["title"],
            count=phase["blocker_count"],
            deps=", ".join(phase["depends_on"]) if phase["depends_on"] else "none",
        )
        for phase in plan["phases"]
    ]
    blocker_rows = [
        "| {blocker_id} | {phase_id} | {category} | {deps} | {lane} | no |".format(
            blocker_id=item["blocker_id"],
            phase_id=item["phase_id"],
            category=item["category"],
            deps=", ".join(item["depends_on_blockers"]) if item["depends_on_blockers"] else "none",
            lane=item["owner_review_lane"],
        )
        for item in plan["blockers"]
    ]
    return "\n".join(
        [
            "# SAEE Commercial Blocker Dependency Plan v0.1",
            "",
            "Status: local commercial blocker dependency planning; production launch remains hold.",
            "",
            "This plan stages the current 24 production launch blockers into a",
            "dependency-aware sequence for human commercial review. It does not",
            "execute blocker work, close blockers, contact customers, call external",
            "services, launch product, or claim production readiness.",
            "",
            "## Summary",
            "",
            f"- plan_scope: {plan['plan_scope']}",
            f"- production_launch_status: {plan['production_launch_status']}",
            f"- production_blocker_count: {plan['production_blocker_count']}",
            f"- planned_blocker_count: {plan['planned_blocker_count']}",
            f"- open_blocker_count: {plan['open_blocker_count']}",
            f"- phase_count: {plan['phase_count']}",
            f"- blockers_closed_by_plan: {plan['blockers_closed_by_plan']}",
            "- execution_authorized: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
            "",
            "## Phases",
            "",
            "| Phase | Title | Blockers | Depends on | Execution allowed here |",
            "| --- | --- | --- | --- | --- |",
            *phase_rows,
            "",
            "## Blocker Dependency Table",
            "",
            "| Blocker | Phase | Category | Depends on blockers | Owner lane | Closure allowed here |",
            "| --- | --- | --- | --- | --- | --- |",
            *blocker_rows,
            "",
            "## Boundary",
            "",
            "- No blocker is closed by this plan.",
            "- No execution is authorized by this plan.",
            "- No production-ready claim is made.",
            "- No customer validation claim is made.",
            "- No product launch is authorized.",
            "- No customer contact is authorized.",
            "- No backend runtime, kernel, API schema, or private core is modified.",
            "- Each blocker requires a separate human-approved evidence task before closure.",
            "",
        ]
    )


def render_readme() -> str:
    return """# SAEE Commercial Blocker Dependency Plan

Status: local commercial blocker dependency planning, not production readiness.

This directory contains generated local planning artifacts that stage the 24
current production-launch blockers into dependency-aware phases.

It does not execute blocker work, close blockers, contact customers, call
external services, launch product, claim customer validation, claim production
readiness, or expose private core.

Primary files:

```text
dependency_plan.local.json
dependency_plan.local.md
dependency_plan.local.csv
```

Generate them with:

```bash
python3 scripts/saee_commercial_blocker_dependency_plan.py
```

Boundary:

```yaml
plan_scope: local_commercial_blocker_dependency_planning
production_launch_status: hold
production_blocker_count: 24
planned_blocker_count: 24
phase_count: 5
blockers_closed_by_plan: 0
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
"""


def render_doc() -> str:
    return """# SAEE Commercial Blocker Dependency Plan v0.1

commercial_blocker_dependency_plan_v0_1: true
plan_scope: local_commercial_blocker_dependency_planning
production_launch_status: hold
production_blocker_count: 24
planned_blocker_count: 24
phase_count: 5
blockers_closed_by_plan: 0
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false

## Purpose

The dependency plan turns the current production blocker gap matrix into a
staged commercial-readiness sequence. It helps human reviewers decide which
blocker lane to address first without pretending that any blocker has been
closed.

## Phase Order

1. Identity, authorization, and tenant boundary.
2. Data recovery and production operations.
3. Support, security, privacy, and legal readiness.
4. Commercial packaging and billing controls.
5. Customer validation and launch review.

## Boundary

- No blocker is closed by this plan.
- No task candidate is executed.
- No development permission is granted.
- No runtime, backend, kernel, API schema, landing-page interaction, or private core is modified.
- No customer is contacted.
- No external service is called.
- No product is launched.
- No production readiness or customer validation claim is made.

## Next Action

Use this plan to choose one blocker lane for a separate, explicit,
human-approved evidence task. Do not close blockers from this plan alone.
"""


def render_gate() -> str:
    return """# SAEE Commercial Blocker Dependency Plan Recommendation Gate

answer: conditional
recommend_for_local_commercial_review: true
recommend_for_execution_authorization: false
recommend_for_production_readiness_claim: false
recommend_for_customer_validation_claim: false
recommend_for_product_launch: false
recommend_for_customer_contact: false

## Reason

The dependency plan is useful for formal commercial-readiness review because it
orders the 24 open production blockers into staged, dependency-aware lanes. It
does not execute work, approve launch, contact customers, close blockers, or
claim production readiness.

## Boundary

```yaml
plan_scope: local_commercial_blocker_dependency_planning
production_launch_status: hold
production_blocker_count: 24
planned_blocker_count: 24
phase_count: 5
blockers_closed_by_plan: 0
execution_authorized: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```

## Next Action

Use the plan only to decide which blocker deserves a separate human-approved
evidence task. Do not treat this plan as implementation approval.
"""


def write_csv(plan: dict[str, Any]) -> None:
    fields = [
        "blocker_id",
        "phase_id",
        "category",
        "status",
        "depends_on_blockers",
        "unblocks_blockers",
        "owner_review_lane",
        "external_dependency_required",
        "engineering_implementation_required",
        "execution_allowed_by_plan",
        "closure_allowed_by_plan",
        "requires_human_approval",
        "requires_separate_execution_request",
        "required_evidence",
    ]
    with PLAN_CSV.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for item in plan["blockers"]:
            row = {field: item[field] for field in fields}
            row["depends_on_blockers"] = ";".join(item["depends_on_blockers"])
            row["unblocks_blockers"] = ";".join(item["unblocks_blockers"])
            writer.writerow(row)


def write_outputs(plan: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PLAN_JSON.write_text(json.dumps(plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    PLAN_MD.write_text(render_markdown(plan), encoding="utf-8")
    PLAN_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_csv(plan)
    README_PATH.write_text(render_readme(), encoding="utf-8")
    DOC_PATH.write_text(render_doc(), encoding="utf-8")
    GATE_PATH.write_text(render_gate(), encoding="utf-8")


def main() -> None:
    plan = build_dependency_plan()
    write_outputs(plan)
    print(
        "SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN: PASS "
        f"production_blockers={plan['production_blocker_count']} "
        f"planned_blockers={plan['planned_blocker_count']} "
        f"phase_count={plan['phase_count']} "
        f"blockers_closed_by_plan={plan['blockers_closed_by_plan']} "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
