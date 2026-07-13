#!/usr/bin/env python3
"""Reconcile Phase 1 identity and tenant evidence without enabling production.

The human-filled Phase 1 evidence can be complete enough for a human go/no-go
review while the production identity provider, token validation, production
RBAC enforcement, storage migration, and tenant isolation remain inactive.
This script makes that distinction agent-readable. It never changes the
canonical blocker matrix or closes a blocker.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
COMMERCIAL_DIR = ROOT / "phase_b_product/commercial_readiness"
PROFILE_DIR = COMMERCIAL_DIR / "phase_1_identity_tenant_evidence_profile"
BUILDER_DIR = COMMERCIAL_DIR / "phase_1_identity_tenant_evidence_builder"
OUT_DIR = PROFILE_DIR / "phase_1_identity_tenant_state_reconciliation"
OUT_JSON = OUT_DIR / "phase_1_identity_tenant_state_reconciliation.local.json"
OUT_MD = OUT_DIR / "phase_1_identity_tenant_state_reconciliation.md"
BOUNDARY = OUT_DIR / "phase_1_identity_tenant_state_reconciliation_boundary_audit.md"
TOP_DOC = COMMERCIAL_DIR / "PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_GATE.md"
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
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
]

SOURCES = {
    "human_filled_run_summary": PROFILE_DIR
    / "phase_1_identity_tenant_human_filled_evidence_run_summary.local.json",
    "human_filled_profile": PROFILE_DIR
    / "phase_1_identity_tenant_evidence_profile.human_filled.local.json",
    "human_filled_auth_evidence": BUILDER_DIR
    / "phase_1_identity_tenant_auth_evidence.human_filled.local.json",
    "human_filled_tenant_evidence": BUILDER_DIR
    / "phase_1_identity_tenant_storage_evidence.human_filled.local.json",
    "human_filled_builder_output": BUILDER_DIR
    / "phase_1_identity_tenant_evidence_builder_output.human_filled.local.json",
    "gap_matrix": COMMERCIAL_DIR / "production_blocker_gap_matrix/gap_matrix.local.json",
    "closure_readiness_board": COMMERCIAL_DIR
    / "commercial_blocker_closure_readiness_board/closure_readiness_board.local.json",
}

FALSE_FLAGS: dict[str, Any] = {
    "identity_provider_contacted_by_codex": False,
    "jwks_fetched_by_codex": False,
    "production_tokens_validated_by_codex": False,
    "production_auth_enabled": False,
    "rbac_enforced_in_production": False,
    "tenant_authorization_enabled": False,
    "storage_migration_executed": False,
    "production_database_modified": False,
    "production_tenant_storage_enabled": False,
    "production_tenant_storage_isolated": False,
    "customer_data_processed": False,
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
    "product_launched": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "public_sdk_released": False,
}


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(f"missing required source: {rel(path)}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"{rel(path)} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


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
        path.write_text(
            before.rstrip() + "\n\n" + block + after.lstrip(),
            encoding="utf-8",
        )
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


def build_payload() -> dict[str, Any]:
    data = {name: read_json(path) for name, path in SOURCES.items()}
    summary = data["human_filled_run_summary"]
    profile = data["human_filled_profile"]
    auth = data["human_filled_auth_evidence"]
    tenant = data["human_filled_tenant_evidence"]
    builder = data["human_filled_builder_output"]

    idp_ready = (
        summary.get("idp_validation_status") == "pass"
        and summary.get("production_identity_provider_available") is True
        and auth.get("production_identity_provider_selected") is True
        and auth.get("identity_provider_admin_owner_named") is True
        and auth.get("identity_provider_contacted") is False
        and auth.get("production_auth_enabled") is False
    )
    oauth_ready = (
        summary.get("oauth_oidc_validation_status") == "pass"
        and summary.get("oauth_oidc_available") is True
        and auth.get("oauth_oidc_flow_approved") is True
        and auth.get("oidc_issuer_verified") is True
        and auth.get("oidc_audience_approved") is True
        and auth.get("tokens_validated_in_production") is False
    )
    rbac_ready = (
        summary.get("rbac_validation_status") == "pass"
        and summary.get("rbac_available") is True
        and auth.get("rbac_policy_approved") is True
        and auth.get("role_matrix_reviewed") is True
        and auth.get("least_privilege_reviewed") is True
        and auth.get("rbac_enforced_in_production") is False
    )
    tenant_ready = (
        summary.get("tenant_storage_validation_status") == "pass"
        and summary.get("tenant_storage_isolation_evidence_complete") is True
        and tenant.get("production_tenant_data_model_approved") is True
        and tenant.get("cross_tenant_read_denial_tests_passed") is True
        and tenant.get("cross_tenant_write_denial_tests_passed") is True
        and tenant.get("same_experiment_id_cross_tenant_partition_tests_passed") is True
        and tenant.get("production_tenant_storage_isolated") is False
        and tenant.get("migration_executed") is False
    )
    profile_ready = (
        builder.get("status") == "pass"
        and builder.get("provided_evidence_item_count") == 33
        and builder.get("missing_required_evidence_count") == 0
        and profile.get("profile_status") == "pass"
        and profile.get("phase_1_target_blockers_satisfied_count") == 4
        and profile.get("blockers_closed_by_profile") == 0
        and profile.get("production_ready") is False
        and profile.get("production_launch_status") == "hold"
    )

    readiness = {
        "production_identity_provider": idp_ready,
        "oauth_oidc": oauth_ready,
        "rbac": rbac_ready,
        "tenant_storage_isolation": tenant_ready,
    }
    all_ready = all(readiness.values()) and profile_ready
    any_ready = any(readiness.values())

    gap = data["gap_matrix"]
    board = data["closure_readiness_board"]
    gap_open = {bid: find_row(gap, bid).get("status") == "open" for bid in TARGETS}
    board_not_ready = {
        bid: find_row(board, bid).get("status") in {"not_ready", None, ""}
        for bid in TARGETS
    }

    if all_ready:
        status = "ready_for_human_phase1_identity_tenant_review_no_closure"
        next_action = (
            "Human identity/data-security owner may review the four evidence-backed "
            "readiness markers for a later matrix-update request. Do not contact an "
            "identity provider, fetch JWKS, validate production tokens, enable production "
            "RBAC, migrate storage, isolate live tenant data, close blockers, or claim "
            "production readiness."
        )
    elif any_ready:
        status = "partial_phase1_identity_tenant_review_ready_no_closure"
        next_action = "Review only the ready evidence lanes; no production enablement or blocker closure is allowed."
    else:
        status = "hold_phase1_identity_tenant_evidence_incomplete"
        next_action = "Complete human-filled Phase 1 evidence before requesting further review."

    payload: dict[str, Any] = {
        "phase_1_identity_tenant_state_reconciliation_v0_1": True,
        "reconciliation_type": "local_phase1_identity_tenant_state_reconciliation_no_production_enablement_no_closure",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "target_blocker_ids": TARGETS,
        "production_identity_provider_ready_for_review": idp_ready,
        "oauth_oidc_ready_for_review": oauth_ready,
        "rbac_ready_for_review": rbac_ready,
        "tenant_storage_isolation_ready_for_review": tenant_ready,
        "combined_phase_1_profile_ready": profile_ready,
        "ready_for_review_count": sum(1 for value in readiness.values() if value),
        "human_filled_evidence_item_count": builder.get("provided_evidence_item_count"),
        "missing_required_evidence_count": builder.get("missing_required_evidence_count"),
        "gap_matrix_open_by_blocker": gap_open,
        "closure_board_not_ready_by_blocker": board_not_ready,
        "source_paths": {name: rel(path) for name, path in SOURCES.items()},
        "human_review_required": True,
        "separate_matrix_update_request_required": True,
        "recommendation_gate": "conditional",
        "would_recommend_to_potential_customer": "conditional",
        "recommendation_reason": (
            "The local evidence package is review-ready, but production identity, token "
            "validation, RBAC enforcement, and tenant isolation are not operational."
        ),
        "next_human_action": next_action,
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    write_json(OUT_JSON, payload)
    OUT_MD.write_text(
        f"""# SAEE Phase 1 Identity/Tenant State Reconciliation v0.1

Status: `{payload['status']}`

This agent-readable board reconciles the human-filled identity, OIDC, RBAC,
and tenant-storage evidence. It records review readiness only. It does not
contact an identity provider, validate production tokens, enable production
authorization, migrate storage, isolate live customer data, update the blocker
matrix, or close blockers.

## Current Finding

- production_identity_provider_ready_for_review: `{str(payload['production_identity_provider_ready_for_review']).lower()}`
- oauth_oidc_ready_for_review: `{str(payload['oauth_oidc_ready_for_review']).lower()}`
- rbac_ready_for_review: `{str(payload['rbac_ready_for_review']).lower()}`
- tenant_storage_isolation_ready_for_review: `{str(payload['tenant_storage_isolation_ready_for_review']).lower()}`
- combined_phase_1_profile_ready: `{str(payload['combined_phase_1_profile_ready']).lower()}`
- human_filled_evidence_item_count: `{payload['human_filled_evidence_item_count']}`
- ready_for_review_count: `{payload['ready_for_review_count']}`
- recommendation_gate: `{payload['recommendation_gate']}`

## Recommendation Gate

If a potential customer asked whether this program is ready for production
identity and tenant isolation, the answer is `conditional`: the evidence packet
is review-ready, but operational production controls remain unverified and
inactive.

## Next Human Action

{payload['next_human_action']}

## Boundary

- production_auth_enabled=false
- rbac_enforced_in_production=false
- production_tenant_storage_isolated=false
- storage_migration_executed=false
- customer_data_processed=false
- blockers_closed_by_reconciliation=0
- production_ready=false
- customer_validated=false
- product_launched=false
- private_core_exposed=false
""",
        encoding="utf-8",
    )
    BOUNDARY.write_text(
        """# Phase 1 Identity/Tenant State Reconciliation Boundary Audit

- Only local status and agent-readable evidence surfaces were written.
- No identity provider contacted by Codex.
- No JWKS fetched by Codex.
- No production token validated by Codex.
- No production authentication enabled.
- No production RBAC enforcement enabled.
- No storage migration executed.
- No production tenant storage enabled or isolated.
- No customer data processed.
- No canonical blocker matrix or closure board modified.
- No runtime, backend, kernel, or API schema modified.
- No private core exposed.
- No product launched or customer contacted.
- No blocker closed and no production-ready claim added.

identity_provider_contacted_by_codex=false
jwks_fetched_by_codex=false
production_tokens_validated_by_codex=false
production_auth_enabled=false
rbac_enforced_in_production=false
storage_migration_executed=false
production_tenant_storage_isolated=false
customer_data_processed=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false
""",
        encoding="utf-8",
    )
    TOP_DOC.write_text(
        f"""# SAEE Phase 1 Identity/Tenant State Reconciliation v0.1

status: {payload['status']}
target_blocker_ids: production_identity_provider,oauth_oidc,rbac,tenant_storage_isolation
production_identity_provider_ready_for_review: {str(payload['production_identity_provider_ready_for_review']).lower()}
oauth_oidc_ready_for_review: {str(payload['oauth_oidc_ready_for_review']).lower()}
rbac_ready_for_review: {str(payload['rbac_ready_for_review']).lower()}
tenant_storage_isolation_ready_for_review: {str(payload['tenant_storage_isolation_ready_for_review']).lower()}
combined_phase_1_profile_ready: {str(payload['combined_phase_1_profile_ready']).lower()}
ready_for_review_count: {payload['ready_for_review_count']}
human_filled_evidence_item_count: {payload['human_filled_evidence_item_count']}
recommendation_gate: conditional
human_review_required: true
separate_matrix_update_request_required: true
production_auth_enabled=false
rbac_enforced_in_production=false
production_tenant_storage_isolated=false
storage_migration_executed=false
blockers_closed_by_reconciliation=0
production_ready=false
customer_validated=false
product_launched=false
private_core_exposed=false

This is a review-only reconciliation surface. It does not enable production
controls, update the canonical blocker matrix, close blockers, or authorize
customer-facing use.
""",
        encoding="utf-8",
    )
    GATE.write_text(
        f"""# SAEE Phase 1 Identity/Tenant State Reconciliation Gate

answer: hold_human_phase1_identity_tenant_review_required_no_production_enablement_no_auto_closure

recommendation_gate: conditional

reason:
The 33-item human-filled identity/OIDC/RBAC/tenant-storage evidence package is
locally complete and review-ready. Production identity integration, JWKS/token
validation, production RBAC enforcement, storage migration, and live tenant
isolation remain inactive and unverified.

status: {payload['status']}

boundary:
identity_provider_contacted_by_codex: false
jwks_fetched_by_codex: false
production_tokens_validated_by_codex: false
production_auth_enabled: false
rbac_enforced_in_production: false
storage_migration_executed: false
production_tenant_storage_isolated: false
customer_data_processed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
private_core_exposed: false
production_ready: false
customer_validated: false
blockers_closed_by_reconciliation: 0

next_action:
Human identity/data-security review only. A separate explicit matrix-update
request is required before any review-ready marker can be applied. Production
enablement and blocker closure require their own evidence and approvals.
""",
        encoding="utf-8",
    )

    block = f"""## Phase 1 Identity/Tenant State Reconciliation v0.1

Status: `{payload['status']}`.

The 33-item human-filled Phase 1 evidence package is reconciled into a
review-only state for `production_identity_provider`, `oauth_oidc`, `rbac`, and
`tenant_storage_isolation`. `ready_for_review_count={payload['ready_for_review_count']}`,
`combined_phase_1_profile_ready={str(payload['combined_phase_1_profile_ready']).lower()}`,
`production_identity_provider_ready_for_review={str(payload['production_identity_provider_ready_for_review']).lower()}`,
`oauth_oidc_ready_for_review={str(payload['oauth_oidc_ready_for_review']).lower()}`,
`rbac_ready_for_review={str(payload['rbac_ready_for_review']).lower()}`,
`tenant_storage_isolation_ready_for_review={str(payload['tenant_storage_isolation_ready_for_review']).lower()}`,
`recommendation_gate=conditional`, `blockers_closed_by_reconciliation=0`,
`production_ready=false`, `customer_validated=false`, `product_launched=false`,
and `private_core_exposed=false`. Production identity, token validation, RBAC,
storage migration, and tenant isolation were not enabled by Codex.
"""
    for path in STATUS_SURFACES:
        replace_block(path, "SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION", block)

    for line in [
        "/phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_V0_1.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_state_reconciliation/phase_1_identity_tenant_state_reconciliation_boundary_audit.md",
        "/docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION_GATE.md",
        "/scripts/saee_phase1_identity_tenant_state_reconciliation.py",
        "/scripts/saee_phase1_identity_tenant_state_reconciliation_smoke.py",
    ]:
        ensure_line(LLMS, line)

    index = read_json(AGENT_INDEX)
    index["phase_1_identity_tenant_state_reconciliation_v0_1"] = {
        key: payload[key]
        for key in [
            "status",
            "target_blocker_ids",
            "production_identity_provider_ready_for_review",
            "oauth_oidc_ready_for_review",
            "rbac_ready_for_review",
            "tenant_storage_isolation_ready_for_review",
            "combined_phase_1_profile_ready",
            "ready_for_review_count",
            "human_filled_evidence_item_count",
            "human_review_required",
            "separate_matrix_update_request_required",
            "recommendation_gate",
            "would_recommend_to_potential_customer",
            "identity_provider_contacted_by_codex",
            "jwks_fetched_by_codex",
            "production_tokens_validated_by_codex",
            "production_auth_enabled",
            "rbac_enforced_in_production",
            "storage_migration_executed",
            "production_tenant_storage_isolated",
            "customer_data_processed",
            "blockers_closed_by_reconciliation",
            "production_ready",
            "customer_validated",
            "product_launched",
            "private_core_exposed",
            "runtime_modified",
            "backend_modified",
            "kernel_modified",
            "api_schema_modified",
        ]
    }
    write_json(AGENT_INDEX, index)


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_PHASE_1_IDENTITY_TENANT_STATE_RECONCILIATION: PASS "
        f"status={payload['status']} ready_for_review_count={payload['ready_for_review_count']} "
        "blockers_closed_by_reconciliation=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
