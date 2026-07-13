#!/usr/bin/env python3
"""Generate the SAEE formal security review scope draft.

This creates a local, documentation-only scope draft for human security review.
It does not perform a formal security review, contact reviewers or vendors,
run penetration tests, process customer data, modify product behavior, or mark
SAEE production-ready.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/privacy_security_legal_evidence"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_V0_1.md"
)
DRAFT_JSON = OUTPUT_DIR / "formal_security_review_scope_draft.local.json"
DRAFT_MD = OUTPUT_DIR / "formal_security_review_scope_draft.md"
BOUNDARY_AUDIT = OUTPUT_DIR / "formal_security_review_scope_draft_boundary_audit.md"
GATE = (
    ROOT
    / "docs/strategy/SAEE_FORMAL_SECURITY_REVIEW_SCOPE_DRAFT_RECOMMENDATION_GATE.md"
)


SCOPE_SECTIONS = [
    "review_authority_and_approval",
    "review_object_and_asset_inventory",
    "public_shell_threat_model_review",
    "authentication_authorization_review",
    "tenant_boundary_review",
    "data_operations_backup_restore_review",
    "dependency_and_supply_chain_review_plan",
    "vulnerability_management_handoff",
    "private_core_exclusion",
    "customer_data_exclusion",
    "findings_triage_process",
    "remediation_acceptance_boundary",
    "approval_record",
]

REVIEW_AREAS = [
    {
        "area_id": "public_shell_api",
        "area_name": "Public-shell API and local MVP routes",
        "scope": "Review request boundaries, optional preview auth, tenant header handling, and read-only readiness routes.",
        "private_core_in_scope": False,
    },
    {
        "area_id": "landing_demo_surface",
        "area_name": "Static landing demo surface",
        "scope": "Review static demo interaction boundaries and non-production claims.",
        "private_core_in_scope": False,
    },
    {
        "area_id": "local_evidence_artifacts",
        "area_name": "Local commercial evidence artifacts",
        "scope": "Review generated status, evidence, and guard artifacts for overclaiming and sensitive-data exposure.",
        "private_core_in_scope": False,
    },
    {
        "area_id": "data_operations_boundary",
        "area_name": "Data retention, backup, and restore drill boundary",
        "scope": "Review public-shell metadata handling, backup/restore limits, and live-restore non-authorization.",
        "private_core_in_scope": False,
    },
]

BOUNDARY_FLAGS = {
    "draft_scope_available": True,
    "formal_security_review_completed": False,
    "formal_security_review_report_available": False,
    "security_reviewer_assigned": False,
    "security_vendor_contacted": False,
    "legal_counsel_contacted": False,
    "penetration_test_completed": False,
    "dependency_review_completed": False,
    "review_findings_triaged": False,
    "remediation_plan_approved": False,
    "production_security_ready": False,
    "production_privacy_security_legal_ready": False,
    "customer_data_processing_approved": False,
    "customer_data_processed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
    "private_core_inspected": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "customer_contacted": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "production_ready": False,
}


def build_draft() -> dict[str, Any]:
    return {
        "draft_type": "saee_formal_security_review_scope_draft",
        "draft_version": "v0.1",
        "draft_status": "draft_not_approved",
        "review_scope": "formal_security_review_scope_draft_for_human_review_only",
        "blocker_target": "formal_security_review",
        "generated_by": "scripts/saee_formal_security_review_scope_draft.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_inputs": [
            "phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json",
            "phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_V0_1.md",
        ],
        "scope_sections": SCOPE_SECTIONS,
        "review_areas": REVIEW_AREAS,
        "required_human_owners": [
            "security_owner",
            "engineering_owner",
            "privacy_legal_owner",
            "operations_owner",
        ],
        "evidence_required_before_blocker_closure": [
            "named_security_reviewer_or_approved_internal_owner",
            "completed_security_review_report",
            "dependency_review_record",
            "triaged_findings_record",
            "approved_remediation_or_risk_acceptance_record",
            "private_core_non_exposure_confirmation",
        ],
        "hard_boundaries": {
            "review_execution_requires_separate_approval": True,
            "external_reviewer_contact_requires_human_approval": True,
            "penetration_test_requires_separate_approval": True,
            "customer_data_review_requires_privacy_legal_approval": True,
            "private_core_review_forbidden_by_default": True,
            "production_security_claim_requires_completed_review": True,
        },
        "human_review_required": True,
        "separate_review_execution_approval_required": True,
        "blocker_closure_allowed_by_draft": False,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        **BOUNDARY_FLAGS,
    }


def render_scope_draft(draft: dict[str, Any]) -> str:
    sections = "\n".join(f"- {section}" for section in draft["scope_sections"])
    owners = "\n".join(f"- {owner}" for owner in draft["required_human_owners"])
    evidence = "\n".join(
        f"- {item}" for item in draft["evidence_required_before_blocker_closure"]
    )
    areas = "\n\n".join(
        "\n".join(
            [
                f"### {area['area_name']}",
                "",
                f"- area_id: {area['area_id']}",
                f"- scope: {area['scope']}",
                "- private_core_in_scope: false",
            ]
        )
        for area in draft["review_areas"]
    )
    boundary = "\n".join(
        f"- {key}: {str(value).lower()}" for key, value in BOUNDARY_FLAGS.items()
    )

    return f"""# SAEE Formal Security Review Scope Draft v0.1

Status: draft not approved.

This is a documentation-only scope draft for a future formal security review
of SAEE's public-shell commercial surface. It is not a completed security
review, not a penetration test, not a vendor engagement, and not production
security evidence.

## Scope

```yaml
draft_type: {draft['draft_type']}
draft_status: {draft['draft_status']}
review_scope: {draft['review_scope']}
blocker_target: {draft['blocker_target']}
human_review_required: true
separate_review_execution_approval_required: true
blocker_closure_allowed_by_draft: false
formal_security_review_completed: false
formal_security_review_report_available: false
production_security_ready: false
production_ready: false
```

## Review Areas

{areas}

## Scope Sections

{sections}

## Required Human Owners

{owners}

## Evidence Required Before Blocker Closure

{evidence}

## Private Core Exclusion

Private core, kernel internals, fitness logic, selection logic, mutation
logic, lineage internals, and runtime private implementation details are not
in scope for this draft. Any private-core inspection requires a separate
explicit approval path and is not authorized here.

## Customer Data Exclusion

This draft does not authorize customer-data processing, customer-data review,
external data transfer, or production traffic testing. Customer data review
requires privacy/legal approval and separate execution authorization.

## Boundary Flags

{boundary}

## Non-Approval Statement

This draft can help a human owner scope a future formal security review. It
does not complete the `formal_security_review` blocker and does not authorize
review execution, vendor contact, penetration testing, product launch, or
production-readiness claims.
"""


def render_top_doc(draft: dict[str, Any]) -> str:
    return f"""# SAEE Formal Security Review Scope Draft v0.1

Status: draft not approved; human review required.

This top-level note records that a formal security review scope draft exists
for the `formal_security_review` commercial blocker. The draft is
documentation-only and does not perform a security review, contact reviewers
or vendors, run penetration tests, process customer data, expose private core,
launch product, or make SAEE production-ready.

```yaml
formal_security_review_scope_draft_v0_1: true
draft_type: {draft['draft_type']}
draft_status: {draft['draft_status']}
review_scope: {draft['review_scope']}
blocker_target: {draft['blocker_target']}
draft_scope_available: true
human_review_required: true
separate_review_execution_approval_required: true
blocker_closure_allowed_by_draft: false
formal_security_review_completed: false
formal_security_review_report_available: false
security_reviewer_assigned: false
security_vendor_contacted: false
penetration_test_completed: false
dependency_review_completed: false
review_findings_triaged: false
production_security_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Review Purpose

The draft turns the existing privacy/security/legal evidence gaps into a
bounded review scope that a human security owner can inspect before deciding
whether to run a real formal security review.

## Source Inputs

- `phase_b_product/commercial_readiness/privacy_security_legal_evidence/privacy_security_legal_evidence.local.json`
- `phase_b_product/commercial_readiness/PRIVACY_SECURITY_LEGAL_EVIDENCE_RUNNER_V0_1.md`

## Next Human Action

Review the draft scope in
`phase_b_product/commercial_readiness/privacy_security_legal_evidence/formal_security_review_scope_draft.md`.
If actual review execution is desired, create a separate explicit review
execution request.
"""


def render_boundary_audit() -> str:
    return """# SAEE Formal Security Review Scope Draft Boundary Audit

Final boundary decision: draft for human review only.

- Only documentation / formal security review scope materials were created.
- No formal security review was completed.
- No security review report was created.
- No security reviewer was assigned.
- No security vendor was contacted.
- No legal counsel was contacted.
- No penetration test was performed.
- No dependency review was completed.
- No review findings were triaged.
- No remediation plan was approved.
- No customer data was processed.
- No runtime was modified.
- No backend was modified.
- No kernel was modified.
- No API schema was modified.
- No private core was inspected or exposed.
- No external model API was called.
- No customer was contacted.
- No product was launched.
- No production security readiness was claimed.
- No production-ready claim was added.

This draft does not close the `formal_security_review` blocker. Separate human
approval is required before any formal review execution, external reviewer
contact, penetration test, or production security claim can exist.
"""


def render_gate() -> str:
    return """# SAEE Formal Security Review Scope Draft Recommendation Gate

answer: conditional

recommend_for_human_scope_review: true
recommend_for_formal_security_review_claim: false
recommend_for_review_execution: false
recommend_for_security_vendor_contact: false
recommend_for_penetration_test: false
recommend_for_blocker_closure: false
recommend_for_production_security_claim: false
recommend_for_production_readiness_claim: false

## Reason

The draft improves the human-review surface for the `formal_security_review`
blocker by defining a bounded review scope and evidence requirements. It does
not perform or complete a formal security review and cannot support production
security or production-readiness claims.

## Boundary

```yaml
draft_scope_available: true
formal_security_review_completed: false
formal_security_review_report_available: false
security_vendor_contacted: false
penetration_test_completed: false
dependency_review_completed: false
review_findings_triaged: false
production_security_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
```

## Next Action

Human reviewers may review the scope draft. Actual security review execution
requires a separate explicit approval request.
"""


def write_outputs(draft: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_JSON.write_text(
        json.dumps(draft, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    DRAFT_MD.write_text(render_scope_draft(draft), encoding="utf-8")
    TOP_DOC.write_text(render_top_doc(draft), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary_audit(), encoding="utf-8")
    GATE.write_text(render_gate(), encoding="utf-8")


def main() -> None:
    draft = build_draft()
    write_outputs(draft)
    print(
        "SAEE_FORMAL_SECURITY_REVIEW_SCOPE_DRAFT: PASS "
        f"path={DRAFT_JSON} status={draft['draft_status']} "
        "formal_security_review_completed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
