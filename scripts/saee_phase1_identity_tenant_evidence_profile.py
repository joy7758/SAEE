#!/usr/bin/env python3
"""Profile Phase 1 identity/tenant evidence against commercial go/no-go.

This runner reads the local Phase 1 evidence-builder output and feeds the
generated auth and tenant-storage evidence files into the existing commercial
go/no-go checks. It does not create production evidence, contact identity
providers, fetch JWKS, validate production tokens, run storage migrations,
process customer data, close blockers by default, launch product, or claim
production readiness.
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
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from saee_backend.services.production_auth_evidence import evaluate_production_auth_evidence
from saee_backend.services.production_tenant_storage_evidence import (
    evaluate_production_tenant_storage_evidence,
)


BUILDER_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
DEFAULT_BUILDER_SUMMARY_PATH = (
    BUILDER_DIR / "phase_1_identity_tenant_evidence_builder_output.local.json"
)
OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile"
)
DEFAULT_PROFILE_JSON = OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.local.json"
DEFAULT_PROFILE_MD = OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.md"
DEFAULT_PROFILE_ENV = OUTPUT_DIR / "phase_1_identity_tenant_evidence_profile.env.example"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_PROFILE_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"
)
LOCAL_AUTHORIZATION_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_local_execution_authorization/authorization.local.json"
)
RBAC_CONSISTENCY_PROFILE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/auth_evidence/rbac_role_permission_consistency.local.json"
)
TENANT_REQUIRED_STORAGE_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json"
)
TENANT_SECRET_BOUNDARY_PROFILE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/tenant_secret_boundary/tenant_secret_boundary.local.json"
)
BOUND_TENANT_AUTHORIZATION_PROFILE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/tenant_authorization/tenant_authorization.local.json"
)

TARGET_BLOCKERS = [
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
]

BOUNDARY_FLAGS: dict[str, bool] = {
    "production_ready": False,
    "customer_validated": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "landing_page_modified": False,
    "external_calls_made": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "customer_contacted": False,
    "identity_provider_contacted_by_codex": False,
    "jwks_fetched_by_codex": False,
    "production_tokens_validated_by_codex": False,
    "storage_migration_executed": False,
    "customer_data_processed": False,
    "codex_inferred_missing_evidence": False,
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_PROFILE: FAIL: " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_PROFILE: FAIL: invalid JSON {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"{path} must contain a JSON object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def path_from_summary(summary: dict[str, Any], key: str) -> Path:
    raw = summary.get(key)
    require(isinstance(raw, str) and raw.strip(), f"builder summary missing {key}")
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = ROOT / path
    require(path.exists(), f"builder evidence path missing: {path}")
    return path


def go_no_go_settings(auth_path: Path, tenant_path: Path) -> dict[str, str]:
    return {
        "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(auth_path),
        "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(tenant_path),
    }


def target_blocker_state(go_no_go: dict[str, Any]) -> tuple[list[str], list[str]]:
    blockers = go_no_go.get("blockers", [])
    require(isinstance(blockers, list), "go/no-go blockers must be a list")
    satisfied: list[str] = []
    unsatisfied: list[str] = []
    for item in blockers:
        if not isinstance(item, dict):
            continue
        blocker_id = item.get("blocker_id")
        if blocker_id not in TARGET_BLOCKERS:
            continue
        if item.get("satisfied") is True:
            satisfied.append(str(blocker_id))
        else:
            unsatisfied.append(str(blocker_id))
    return satisfied, unsatisfied


def profile_status(
    builder_summary: dict[str, Any],
    auth_status: dict[str, Any],
    tenant_status: dict[str, Any],
    go_no_go: dict[str, Any],
) -> str:
    if (
        builder_summary.get("status") == "stop"
        or auth_status.get("status") == "stop"
        or tenant_status.get("status") == "stop"
        or int(go_no_go.get("boundary_violation_count", 0)) > 0
    ):
        return "stop"
    if (
        builder_summary.get("status") == "pass"
        and auth_status.get("status") == "pass"
        and tenant_status.get("status") == "pass"
    ):
        return "pass"
    return "hold"


def build_profile(builder_summary_path: Path) -> dict[str, Any]:
    builder_summary = read_json(builder_summary_path)
    auth_path = path_from_summary(builder_summary, "auth_evidence_output")
    tenant_path = path_from_summary(builder_summary, "tenant_storage_evidence_output")
    settings_env = go_no_go_settings(auth_path, tenant_path)
    settings = load_settings(settings_env)

    auth_status = evaluate_production_auth_evidence(settings)
    tenant_status = evaluate_production_tenant_storage_evidence(settings)
    go_no_go = evaluate_commercial_go_no_go(settings)
    phase1_satisfied, phase1_unsatisfied = target_blocker_state(go_no_go)
    status = profile_status(builder_summary, auth_status, tenant_status, go_no_go)
    local_authorization = read_json(LOCAL_AUTHORIZATION_PATH)
    rbac_consistency = read_json(RBAC_CONSISTENCY_PROFILE_PATH)
    tenant_required_guard = read_json(TENANT_REQUIRED_STORAGE_EVIDENCE_PATH)
    tenant_secret_boundary = read_json(TENANT_SECRET_BOUNDARY_PROFILE_PATH)
    bound_tenant_authorization = read_json(BOUND_TENANT_AUTHORIZATION_PROFILE_PATH)

    return {
        "phase_1_identity_tenant_evidence_profile_v0_1": True,
        "profile_type": "saee_phase_1_identity_tenant_evidence_profile",
        "profile_version": "v0.1",
        "profile_scope": "local_phase_1_builder_outputs_to_go_no_go_profile",
        "generated_by": "scripts/saee_phase1_identity_tenant_evidence_profile.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "builder_summary_path": str(builder_summary_path),
        "auth_evidence_path": str(auth_path),
        "tenant_storage_evidence_path": str(tenant_path),
        "local_execution_authorization_path": str(LOCAL_AUTHORIZATION_PATH.relative_to(ROOT)),
        "rbac_consistency_profile_path": str(RBAC_CONSISTENCY_PROFILE_PATH.relative_to(ROOT)),
        "tenant_required_storage_guard_evidence_path": str(
            TENANT_REQUIRED_STORAGE_EVIDENCE_PATH.relative_to(ROOT)
        ),
        "tenant_secret_boundary_profile_path": str(
            TENANT_SECRET_BOUNDARY_PROFILE_PATH.relative_to(ROOT)
        ),
        "bound_tenant_authorization_profile_path": str(
            BOUND_TENANT_AUTHORIZATION_PROFILE_PATH.relative_to(ROOT)
        ),
        "development_permission_granted_for_local_scope": local_authorization[
            "development_permission_granted_for_local_scope"
        ],
        "sanitized_local_evidence_collection_authorized": local_authorization[
            "sanitized_local_evidence_collection_authorized"
        ],
        "production_deployment_authorized": local_authorization[
            "production_deployment_authorized"
        ],
        "production_data_migration_authorized": local_authorization[
            "production_data_migration_authorized"
        ],
        "rbac_role_permission_consistency_enforced": rbac_consistency[
            "role_permission_consistency_enforced"
        ],
        "rbac_consistency_negative_cases_passed": rbac_consistency[
            "negative_cases_passed"
        ],
        "rbac_consistency_negative_cases_total": rbac_consistency[
            "negative_cases_total"
        ],
        "tenant_required_storage_guard_available": tenant_required_guard[
            "tenant_required_storage_guard_available"
        ],
        "memory_store_unscoped_operations_denied": tenant_required_guard[
            "memory_store_unscoped_operations_denied"
        ],
        "sqlite_store_unscoped_operations_denied": tenant_required_guard[
            "sqlite_store_unscoped_operations_denied"
        ],
        "default_local_unscoped_mode_preserved": tenant_required_guard[
            "default_local_unscoped_mode_preserved"
        ],
        "storage_tenant_membership_enforcement_available": tenant_required_guard[
            "storage_tenant_membership_enforcement_available"
        ],
        "unlisted_tenant_operations_denied": tenant_required_guard[
            "unlisted_tenant_operations_denied"
        ],
        "unlisted_tenant_operation_cases_passed": tenant_required_guard[
            "unlisted_tenant_operation_cases_passed"
        ],
        "unlisted_tenant_operation_cases_total": tenant_required_guard[
            "unlisted_tenant_operation_cases_total"
        ],
        "membership_scope": tenant_required_guard["membership_scope"],
        "allowed_tenant_snapshot_requires_restart": tenant_required_guard[
            "allowed_tenant_snapshot_requires_restart"
        ],
        "tenant_secret_boundary_available": tenant_secret_boundary[
            "tenant_secret_boundary_profile_v0_1"
        ],
        "tenant_secret_boundary_negative_cases_passed": tenant_secret_boundary[
            "negative_cases_passed"
        ],
        "tenant_secret_boundary_negative_cases_total": tenant_secret_boundary[
            "negative_cases_total"
        ],
        "tenant_secret_boundary_secret_echo_count": tenant_secret_boundary[
            "secret_echo_count"
        ],
        "tenant_secret_boundary_profile_reviewed": tenant_secret_boundary[
            "tenant_secret_boundary_reviewed"
        ],
        "tenant_secret_boundary_reviewed": tenant_required_guard[
            "tenant_secret_boundary_reviewed"
        ],
        "production_secrets_management_available": tenant_secret_boundary[
            "production_secrets_management_available"
        ],
        "encryption_at_rest_proven": tenant_secret_boundary[
            "encryption_at_rest_proven"
        ],
        "kms_hsm_available": tenant_secret_boundary["kms_hsm_available"],
        "bound_tenant_authorization_available": bound_tenant_authorization[
            "bound_tenant_authorization_profile_v0_1"
        ],
        "bound_tenant_authorization_negative_cases_passed": bound_tenant_authorization[
            "negative_cases_passed"
        ],
        "bound_tenant_authorization_negative_cases_total": bound_tenant_authorization[
            "negative_cases_total"
        ],
        "context_capability_hmac_verified": bound_tenant_authorization[
            "context_capability_hmac_verified"
        ],
        "storage_operation_permission_bound": bound_tenant_authorization[
            "storage_operation_permission_bound"
        ],
        "tenant_authorization_profile_policy_reviewed": bound_tenant_authorization[
            "tenant_authorization_policy_reviewed"
        ],
        "tenant_authorization_policy_reviewed": tenant_required_guard[
            "tenant_authorization_policy_reviewed"
        ],
        "tenant_authorization_enabled": bound_tenant_authorization[
            "tenant_authorization_enabled"
        ],
        "profile_env": settings_env,
        "builder_status": builder_summary.get("status"),
        "builder_input_complete": builder_summary.get("input_complete") is True,
        "builder_required_evidence_item_count": builder_summary.get(
            "required_evidence_item_count"
        ),
        "builder_missing_required_evidence_count": builder_summary.get(
            "missing_required_evidence_count"
        ),
        "auth_readiness_status": auth_status["status"],
        "auth_production_ready_for_review": auth_status["production_auth_ready"],
        "auth_evidence_production_identity_provider_available": auth_status[
            "production_identity_provider_available"
        ],
        "auth_evidence_oauth_oidc_available": auth_status["oauth_oidc_available"],
        "auth_evidence_rbac_available": auth_status["rbac_available"],
        "tenant_storage_readiness_status": tenant_status["status"],
        "tenant_storage_production_ready_for_review": tenant_status[
            "production_tenant_storage_evidence_complete"
        ],
        "tenant_storage_model_complete": tenant_status[
            "tenant_storage_model_evidence_complete"
        ],
        "tenant_storage_isolation_complete": tenant_status[
            "tenant_storage_isolation_evidence_complete"
        ],
        "tenant_operations_complete": tenant_status[
            "tenant_operations_evidence_complete"
        ],
        "tenant_security_privacy_complete": tenant_status[
            "tenant_security_privacy_evidence_complete"
        ],
        "security_review_completed": tenant_required_guard[
            "security_review_completed"
        ],
        "security_review_completion_scope": tenant_required_guard[
            "security_review_completion_scope"
        ],
        "agent_privacy_boundary_review_completed": tenant_required_guard[
            "agent_privacy_boundary_review_completed"
        ],
        "agent_privacy_boundary_review_scope": tenant_required_guard[
            "agent_privacy_boundary_review_scope"
        ],
        "general_dlp_available": False,
        "deidentification_proven": False,
        "real_customer_data_allowed": False,
        "privacy_legal_review_completed": False,
        "commercial_status": go_no_go["commercial_status"],
        "controlled_preview_status": go_no_go["controlled_preview_status"],
        "production_launch_status": go_no_go["production_launch_status"],
        "satisfied_production_checks": go_no_go["satisfied_production_checks"],
        "production_blocker_count": go_no_go["production_blocker_count"],
        "total_production_checks": go_no_go["total_production_checks"],
        "readiness_score": go_no_go["readiness_score"],
        "target_blocker_ids": TARGET_BLOCKERS,
        "phase_1_target_blockers_satisfied": phase1_satisfied,
        "phase_1_target_blockers_unsatisfied": phase1_unsatisfied,
        "phase_1_target_blockers_satisfied_count": len(phase1_satisfied),
        "phase_1_blockers_closed_by_profile": 0,
        "blockers_closed_by_profile": 0,
        "accepted_for_blocker_closure_count": 0,
        "would_satisfy_phase_1_if_complete": len(phase1_satisfied) == len(TARGET_BLOCKERS),
        "profile_status": status,
        "human_review_required": False,
        "human_validation_used": False,
        "agent_validation_primary": True,
        "separate_launch_approval_required": True,
        "development_permission_granted": False,
        "task_candidates_executed": False,
        **BOUNDARY_FLAGS,
        "next_action": (
            "Use independent-agent evidence to review whether Phase 1 identity and "
            "tenant-storage evidence would satisfy the related go/no-go checks. "
            "Do not treat it as blocker closure or production launch approval."
        ),
    }


def render_env(profile: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SAEE Phase 1 identity/tenant evidence profile.",
            "# Local review only; do not use as production launch approval.",
            "# This config points go/no-go at generated auth and tenant evidence files.",
            f"export SAEE_PRODUCTION_AUTH_EVIDENCE_PATH={profile['auth_evidence_path']}",
            f"export SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH={profile['tenant_storage_evidence_path']}",
            "",
        ]
    )


def render_markdown(profile: dict[str, Any]) -> str:
    return f"""# SAEE Phase 1 Identity/Tenant Evidence Profile v0.1

Status: local profile generated; default output is hold.

## Summary

- phase_1_identity_tenant_evidence_profile_v0_1: true
- profile_scope: {profile['profile_scope']}
- builder_status: {profile['builder_status']}
- profile_status: {profile['profile_status']}
- auth_readiness_status: {profile['auth_readiness_status']}
- tenant_storage_readiness_status: {profile['tenant_storage_readiness_status']}
- commercial_status: {profile['commercial_status']}
- production_launch_status: {profile['production_launch_status']}
- satisfied_production_checks: {profile['satisfied_production_checks']}
- production_blocker_count: {profile['production_blocker_count']}
- total_production_checks: {profile['total_production_checks']}
- phase_1_target_blockers_satisfied_count: {profile['phase_1_target_blockers_satisfied_count']}
- phase_1_blockers_closed_by_profile: 0
- blockers_closed_by_profile: 0
- development_permission_granted_for_local_scope: {str(profile['development_permission_granted_for_local_scope']).lower()}
- sanitized_local_evidence_collection_authorized: {str(profile['sanitized_local_evidence_collection_authorized']).lower()}
- rbac_role_permission_consistency_enforced: {str(profile['rbac_role_permission_consistency_enforced']).lower()}
- rbac_consistency_negative_cases: {profile['rbac_consistency_negative_cases_passed']}/{profile['rbac_consistency_negative_cases_total']}
- tenant_required_storage_guard_available: {str(profile['tenant_required_storage_guard_available']).lower()}
- memory_store_unscoped_operations_denied: {str(profile['memory_store_unscoped_operations_denied']).lower()}
- sqlite_store_unscoped_operations_denied: {str(profile['sqlite_store_unscoped_operations_denied']).lower()}
- default_local_unscoped_mode_preserved: {str(profile['default_local_unscoped_mode_preserved']).lower()}
- storage_tenant_membership_enforcement_available: {str(profile['storage_tenant_membership_enforcement_available']).lower()}
- unlisted_tenant_operations_denied: {str(profile['unlisted_tenant_operations_denied']).lower()}
- unlisted_tenant_operation_cases: {profile['unlisted_tenant_operation_cases_passed']}/{profile['unlisted_tenant_operation_cases_total']}
- membership_scope: {profile['membership_scope']}
- allowed_tenant_snapshot_requires_restart: {str(profile['allowed_tenant_snapshot_requires_restart']).lower()}
- tenant_authorization_policy_reviewed: {str(profile['tenant_authorization_policy_reviewed']).lower()}
- tenant_secret_boundary_reviewed: {str(profile['tenant_secret_boundary_reviewed']).lower()}
- security_review_completed: {str(profile['security_review_completed']).lower()}
- agent_privacy_boundary_review_completed: {str(profile['agent_privacy_boundary_review_completed']).lower()}
- privacy_legal_review_completed: false
- human_validation_used: false
- agent_validation_primary: true
- production_deployment_authorized: false
- production_data_migration_authorized: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false

## What This Profiles

This profile takes the generated auth and tenant-storage evidence files from
the Phase 1 evidence builder and runs the existing commercial go/no-go
aggregation with those paths configured.

Target blockers:

```text
{chr(10).join(profile['target_blocker_ids'])}
```

Satisfied target blockers in this local profile:

```text
{chr(10).join(profile['phase_1_target_blockers_satisfied']) or 'none'}
```

Unsatisfied target blockers in this local profile:

```text
{chr(10).join(profile['phase_1_target_blockers_unsatisfied']) or 'none'}
```

## What It Does Not Do

The recorded authorization permits local code, contracts, tests, sanitized
evidence, and Chinese site updates. It does not create production evidence,
contact identity providers, fetch JWKS, validate production tokens, run storage
migrations, process customer data, close blockers, launch product, or claim
production readiness.

## Boundary

- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
- external_calls_made: false
- customer_contacted: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- storage_migration_executed: false
- customer_data_processed: false

## Next Action

If independent-agent evidence fills all 33 Phase 1 evidence items and this profile passes for the
four target blockers, a separate agent go/no-go decision is still required before
any blocker closure or launch decision.
"""


def write_readme(profile: dict[str, Any]) -> None:
    README_PATH.write_text(
        f"""# SAEE Phase 1 Identity/Tenant Evidence Profile

Status: local profile available; default output is hold.

This directory contains the local profile that connects Phase 1 evidence-builder
outputs to the existing commercial go/no-go aggregation.

Primary files:

```text
phase_1_identity_tenant_evidence_profile.env.example
phase_1_identity_tenant_evidence_profile.local.json
phase_1_identity_tenant_evidence_profile.md
```

Generate them with:

```bash
python3 scripts/saee_phase1_identity_tenant_evidence_profile.py
```

Boundary:

```yaml
phase_1_identity_tenant_evidence_profile_v0_1: true
profile_scope: {profile['profile_scope']}
default_profile_status: {profile['profile_status']}
phase_1_blockers_closed_by_profile: 0
development_permission_granted_for_local_scope: {str(profile['development_permission_granted_for_local_scope']).lower()}
rbac_role_permission_consistency_enforced: {str(profile['rbac_role_permission_consistency_enforced']).lower()}
production_deployment_authorized: false
production_launch_status: {profile['production_launch_status']}
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false
external_calls_made: false
```
""",
        encoding="utf-8",
    )


def write_docs(profile: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    DEFAULT_PROFILE_ENV.write_text(render_env(profile), encoding="utf-8")
    DEFAULT_PROFILE_MD.write_text(render_markdown(profile), encoding="utf-8")
    write_readme(profile)
    DOC_PATH.write_text(
        f"""# Phase 1 Identity/Tenant Evidence Profile v0.1

Status: local go/no-go profile for Phase 1 builder outputs; default output is hold.

phase_1_identity_tenant_evidence_profile_v0_1: true
profile_scope: local_phase_1_builder_outputs_to_go_no_go_profile
default_profile_status: {profile['profile_status']}
builder_status: {profile['builder_status']}
auth_readiness_status: {profile['auth_readiness_status']}
tenant_storage_readiness_status: {profile['tenant_storage_readiness_status']}
phase_1_target_blockers_satisfied_count: {profile['phase_1_target_blockers_satisfied_count']}
phase_1_blockers_closed_by_profile: 0
blockers_closed_by_profile: 0
development_permission_granted_for_local_scope: {str(profile['development_permission_granted_for_local_scope']).lower()}
sanitized_local_evidence_collection_authorized: {str(profile['sanitized_local_evidence_collection_authorized']).lower()}
rbac_role_permission_consistency_enforced: {str(profile['rbac_role_permission_consistency_enforced']).lower()}
rbac_consistency_negative_cases: {profile['rbac_consistency_negative_cases_passed']}/{profile['rbac_consistency_negative_cases_total']}
production_deployment_authorized: false
production_data_migration_authorized: false
production_launch_status: {profile['production_launch_status']}
production_blocker_count: {profile['production_blocker_count']}
total_production_checks: {profile['total_production_checks']}
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This profile is the missing review layer between the Phase 1 evidence builder
and the commercial go/no-go report. It shows whether generated identity/OIDC,
RBAC, and tenant-storage evidence would satisfy the four Phase 1 target
blockers.

## Boundary

runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
external_calls_made: false
customer_contacted: false
identity_provider_contacted_by_codex: false
jwks_fetched_by_codex: false
production_tokens_validated_by_codex: false
storage_migration_executed: false
customer_data_processed: false

## Entrypoints

- runner: `scripts/saee_phase1_identity_tenant_evidence_profile.py`
- smoke: `scripts/saee_phase1_identity_tenant_evidence_profile_smoke.py`
- profile JSON: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.local.json`
- profile report: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile/phase_1_identity_tenant_evidence_profile.md`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Phase 1 Identity/Tenant Evidence Profile Recommendation Gate

answer: conditional

recommend_for_phase_1_go_no_go_precheck: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_external_execution: false

## Reason

The profile is useful because it lets an independent agent connect completed Phase
1 identity/OIDC/RBAC and tenant-storage evidence to the existing go/no-go
checks. It is not sufficient for launch: default output is hold, no blocker is
closed by the profile itself, and separate agent launch evidence remains
required.

## Boundary

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
identity_provider_contacted_by_codex: false
jwks_fetched_by_codex: false
production_tokens_validated_by_codex: false
storage_migration_executed: false
customer_data_processed: false

## Next Action

Use the profile only after independent-agent evidence has filled the Phase 1 evidence template. A
separate final commercial go/no-go decision is required before blocker closure
or launch.
""",
        encoding="utf-8",
    )


def write_outputs(profile: dict[str, Any], output_path: Path) -> None:
    write_json(output_path, profile)
    if output_path == DEFAULT_PROFILE_JSON:
        write_docs(profile)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Profile Phase 1 identity/tenant builder outputs against go/no-go."
    )
    parser.add_argument("--builder-summary", default=str(DEFAULT_BUILDER_SUMMARY_PATH))
    parser.add_argument("--output", default=str(DEFAULT_PROFILE_JSON))
    parser.add_argument("--json", action="store_true", help="Print JSON profile.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    profile = build_profile(Path(args.builder_summary).expanduser())
    output_path = Path(args.output).expanduser()
    write_outputs(profile, output_path)
    if args.json:
        print(json.dumps(profile, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_PROFILE: PASS "
            f"profile_status={profile['profile_status']} "
            f"builder_status={profile['builder_status']} "
            f"auth_readiness={profile['auth_readiness_status']} "
            f"tenant_storage_readiness={profile['tenant_storage_readiness_status']} "
            f"phase1_satisfied={profile['phase_1_target_blockers_satisfied_count']} "
            "phase_1_blockers_closed_by_profile=0 production_ready=false"
        )


if __name__ == "__main__":
    main()
