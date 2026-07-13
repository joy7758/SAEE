#!/usr/bin/env python3
"""Generate the SAEE production restore policy draft.

This is a documentation-only commercial-readiness artifact. It creates a
human-reviewable restore policy draft for the `production_restore_policy`
blocker without approving the policy, running restore operations, modifying
live data paths, or changing production readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/PRODUCTION_RESTORE_POLICY_DRAFT_V0_1.md"
DRAFT_JSON = OUTPUT_DIR / "production_restore_policy_draft.local.json"
DRAFT_MD = OUTPUT_DIR / "production_restore_policy_draft.md"
BOUNDARY_AUDIT = OUTPUT_DIR / "production_restore_policy_draft_boundary_audit.md"
GATE = ROOT / "docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_DRAFT_RECOMMENDATION_GATE.md"


POLICY_SECTIONS = [
    "restore_authority_and_approval",
    "service_scope_and_data_classification",
    "backup_retention_and_encryption",
    "proposed_rpo_rto_targets",
    "tenant_data_scope_and_isolation",
    "customer_data_handling_boundary",
    "credential_and_secret_exclusion",
    "private_core_exclusion",
    "restore_execution_controls",
    "incident_response_handoff",
    "customer_notification_boundary",
    "restore_evidence_retention",
    "post_restore_review",
]

PROPOSED_TARGETS = {
    "public_shell_metadata_rpo_hours": 24,
    "public_shell_metadata_rto_hours": 4,
    "request_audit_metadata_rpo_hours": 24,
    "request_audit_metadata_rto_hours": 4,
    "restore_drill_cadence": "quarterly_before_production_claim",
    "backup_retention_days": 30,
    "target_status": "proposed_not_approved",
}

BOUNDARY_FLAGS = {
    "draft_policy_available": True,
    "production_restore_policy_available": False,
    "production_restore_policy_approved": False,
    "backup_retention_policy_approved": False,
    "tenant_restore_boundary_approved": False,
    "customer_data_restore_approved": False,
    "credential_secret_exclusion_reviewed": False,
    "customer_notification_boundary_approved": False,
    "incident_response_handoff_approved": False,
    "production_data_operations_ready": False,
    "restore_to_live_path_enabled": False,
    "live_restore_performed": False,
    "production_data_path_modified": False,
    "credentials_restored": False,
    "private_core_restored": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "private_core_exposed": False,
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
        "draft_type": "saee_production_restore_policy_draft",
        "draft_version": "v0.1",
        "draft_status": "draft_not_approved",
        "review_scope": "production_restore_policy_draft_for_human_review_only",
        "blocker_target": "production_restore_policy",
        "generated_by": "scripts/saee_production_restore_policy_draft.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "policy_sections": POLICY_SECTIONS,
        "proposed_targets": PROPOSED_TARGETS,
        "approval_required_from": [
            "data_operations_owner",
            "security_owner",
            "privacy_legal_owner",
            "operations_incident_response_owner",
        ],
        "hard_boundaries": {
            "live_restore_requires_separate_execution_approval": True,
            "customer_data_restore_requires_privacy_legal_approval": True,
            "tenant_restore_requires_tenant_storage_and_rbac_blockers_closed": True,
            "credentials_restore_requires_separate_secret_review": True,
            "private_core_restore_forbidden": True,
            "customer_notification_requires_legal_approval": True,
            "post_restore_review_required": True,
        },
        "evidence_required_before_blocker_closure": [
            "human_approved_restore_policy",
            "approved_rpo_rto_targets",
            "approved_backup_retention_policy",
            "approved_tenant_restore_boundary",
            "approved_customer_notification_boundary",
            "incident_response_handoff_approval",
            "restore_drill_result_linked_to_policy",
        ],
        "blocker_closure_allowed_by_draft": False,
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "task_candidates_executed": False,
        "development_permission_granted": False,
        **BOUNDARY_FLAGS,
    }


def render_policy(draft: dict[str, Any]) -> str:
    targets = draft["proposed_targets"]
    sections = "\n".join(f"- {section}" for section in draft["policy_sections"])
    evidence = "\n".join(
        f"- {item}" for item in draft["evidence_required_before_blocker_closure"]
    )
    owners = "\n".join(f"- {owner}" for owner in draft["approval_required_from"])
    return f"""# SAEE Production Restore Policy Draft v0.1

Status: draft not approved.

This document is a human-reviewable production restore policy draft for the
`production_restore_policy` blocker. It is not an approved production policy,
does not run a restore, does not modify live data paths, and does not make SAEE
production-ready.

## Scope

```yaml
draft_type: {draft['draft_type']}
draft_status: {draft['draft_status']}
review_scope: {draft['review_scope']}
blocker_target: {draft['blocker_target']}
human_review_required: true
separate_execution_approval_required: true
blocker_closure_allowed_by_draft: false
production_restore_policy_available: false
production_ready: false
```

## Proposed Targets

These targets are proposed for human review only. They are not approved service
levels and are not customer-facing commitments.

- public_shell_metadata_rpo_hours: {targets['public_shell_metadata_rpo_hours']}
- public_shell_metadata_rto_hours: {targets['public_shell_metadata_rto_hours']}
- request_audit_metadata_rpo_hours: {targets['request_audit_metadata_rpo_hours']}
- request_audit_metadata_rto_hours: {targets['request_audit_metadata_rto_hours']}
- restore_drill_cadence: {targets['restore_drill_cadence']}
- backup_retention_days: {targets['backup_retention_days']}
- target_status: {targets['target_status']}

## Policy Sections

{sections}

## Restore Authority and Approval

Production restore may only be authorized by named data operations, security,
privacy/legal, and incident-response owners. This draft does not name owners,
approve restore, or authorize live restore execution.

## Service Scope and Data Classification

The draft is limited to SAEE public-shell operational metadata such as local
experiment report records and request-audit metadata. Customer data restore is
out of scope until privacy/legal review and customer-data processing evidence
exist.

## Backup Retention and Encryption

The proposed backup retention target is 30 days for public-shell operational
metadata. Encryption, key handling, storage provider, and retention exceptions
must be approved separately before this policy can be considered production
evidence.

## Tenant Data Scope and Isolation

Tenant-scoped restore is blocked until production RBAC and tenant storage
isolation blockers are closed. No cross-tenant restore is permitted by this
draft.

## Credential and Secret Exclusion

Credentials, API keys, tokens, signing secrets, and private-core material are
excluded from restore scope. Any secret recovery process requires a separate
secret-management review and approval.

## Private Core Exclusion

Private core, kernel internals, fitness logic, selection logic, mutation logic,
and lineage internals are not restored, exported, copied, or disclosed by this
policy draft.

## Restore Execution Controls

Live restore requires a separate execution request. Restore drills must run in
an isolated environment by default and must preserve audit evidence showing
that no live production path was modified.

## Incident Response Handoff

Restore activity must be linked to an incident record or approved maintenance
record before production use. The incident-response owner must confirm the
handoff and post-restore review path.

## Customer Notification Boundary

Customer notification language and timing require privacy/legal approval. This
draft does not authorize customer contact, public claims, case studies,
testimonials, or customer-validation claims.

## Restore Evidence Retention

Each approved restore drill or live restore must preserve a manifest, operator
identity, start and end timestamps, source backup identifier, target
environment, integrity checks, and post-restore review notes.

## Evidence Required Before Blocker Closure

{evidence}

## Required Human Owners

{owners}

## Non-Approval Statement

This draft can inform human review. It does not close the
`production_restore_policy` blocker and does not authorize production restore,
customer data processing, product launch, customer validation, or production
readiness claims.
"""


def render_top_doc(draft: dict[str, Any]) -> str:
    return f"""# SAEE Production Restore Policy Draft v0.1

production_restore_policy_draft_v0_1: true
draft_scope: production_restore_policy_draft_for_human_review_only
draft_status: draft_not_approved
blocker_target: production_restore_policy
human_review_required: true
separate_execution_approval_required: true
blocker_closure_allowed_by_draft: false
production_restore_policy_available: false
production_restore_policy_approved: false
production_data_operations_ready: false
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This package creates a human-reviewable restore policy draft for the
`production_restore_policy` commercial blocker. It turns the existing review
packet into a concrete policy text with proposed RPO/RTO targets, restore
authority, live-restore controls, tenant boundaries, customer-data boundaries,
secret exclusion, and private-core exclusion.

## Boundary

The draft is not approved production evidence. It does not execute restore,
modify live data paths, contact customers, expose private core, close blockers,
launch product, validate customers, or claim production readiness.

## Entrypoints

- `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.md`
- `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft.local.json`
- `phase_b_product/commercial_readiness/data_operations_evidence/production_restore_policy_draft_boundary_audit.md`
- `docs/strategy/SAEE_PRODUCTION_RESTORE_POLICY_DRAFT_RECOMMENDATION_GATE.md`
"""


def render_boundary_audit(draft: dict[str, Any]) -> str:
    flags = [
        "production_restore_policy_available",
        "production_restore_policy_approved",
        "production_data_operations_ready",
        "restore_to_live_path_enabled",
        "live_restore_performed",
        "production_data_path_modified",
        "credentials_restored",
        "private_core_restored",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "external_calls_made",
        "customer_contacted",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "production_ready",
    ]
    lines = "\n".join(f"- {flag}: {str(draft[flag]).lower()}" for flag in flags)
    return f"""# Production Restore Policy Draft Boundary Audit

Scope: production restore policy draft only.

{lines}
- task_candidates_executed: false
- development_permission_granted: false
- blocker_closure_allowed_by_draft: false

Final boundary decision: draft for human review only.
"""


def render_gate(draft: dict[str, Any]) -> str:
    return """# SAEE Production Restore Policy Draft Recommendation Gate

answer: conditional

recommend_for_human_policy_review: true
recommend_for_production_restore_policy_claim: false
recommend_for_blocker_closure: false
recommend_for_live_restore_execution: false
recommend_for_customer_data_restore: false
recommend_for_product_launch: false
recommend_for_production_readiness_claim: false

## Reason

The draft is useful because it gives human owners concrete restore-policy text
to review. It is not approved, does not execute restore, and does not provide
production evidence by itself.

## Current Evidence

- blocker_target: production_restore_policy
- draft_status: draft_not_approved
- production_restore_policy_available: false
- production_restore_policy_approved: false
- production_ready: false
- private_core_exposed: false

## Next Action

Human data operations, security, privacy/legal, and incident-response owners
must review and explicitly approve or revise the draft before it can become
production evidence.
"""


def write_outputs(draft: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DRAFT_JSON.write_text(json.dumps(draft, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    DRAFT_MD.write_text(render_policy(draft), encoding="utf-8")
    TOP_DOC.write_text(render_top_doc(draft), encoding="utf-8")
    BOUNDARY_AUDIT.write_text(render_boundary_audit(draft), encoding="utf-8")
    GATE.write_text(render_gate(draft), encoding="utf-8")


def main() -> None:
    draft = build_draft()
    write_outputs(draft)
    print(
        "SAEE_PRODUCTION_RESTORE_POLICY_DRAFT: PASS "
        f"path={DRAFT_JSON} status={draft['draft_status']} "
        "production_restore_policy_available=false production_ready=false"
    )


if __name__ == "__main__":
    main()
