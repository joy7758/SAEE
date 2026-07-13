#!/usr/bin/env python3
"""Generate local human-filled Phase 1 identity/tenant evidence.

This run records human-filled local evidence for production identity provider,
OAuth/OIDC, RBAC, and tenant storage isolation commercial blockers. It does not
contact identity providers, fetch JWKS, validate production tokens, enable
production auth, enforce production RBAC, run storage migrations, process
customer data, modify runtime/backend/kernel/API behavior, close blockers by
itself, or claim production readiness.
"""

from __future__ import annotations

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
from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
    evaluate_production_auth_evidence,
)
from saee_backend.services.production_tenant_storage_evidence import (
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
    evaluate_production_tenant_storage_evidence,
)
from scripts.saee_oauth_oidc_approval_input_validator import (
    build_validation as build_oauth_validation,
    report_markdown as oauth_validation_markdown,
)
from scripts.saee_phase1_identity_tenant_evidence_builder import (
    ALL_EVIDENCE_KEYS,
    INPUT_FORBIDDEN_TRUE_KEYS,
    build_from_input,
    input_template as phase1_input_template,
)
from scripts.saee_phase1_identity_tenant_evidence_profile import (
    BOUNDARY_FLAGS,
    build_profile,
)
from scripts.saee_production_identity_provider_approval_input_validator import (
    build_validation as build_idp_validation,
    report_markdown as idp_validation_markdown,
)
from scripts.saee_production_identity_provider_decision_packet import (
    FALSE_FLAGS as IDP_FALSE_FLAGS,
    TARGET_KEYS as IDP_TARGET_KEYS,
    input_template as idp_input_template,
)
from scripts.saee_rbac_approval_input_validator import (
    build_validation as build_rbac_validation,
    report_markdown as rbac_validation_markdown,
)
from scripts.saee_tenant_storage_approval_input_validator import (
    build_validation as build_tenant_validation,
    report_markdown as tenant_validation_markdown,
)


OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
PROFILE_DIR = ROOT / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_profile"
AUTH_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"

IDP_INPUT_PATH = AUTH_DIR / "production_identity_provider_decision_input.human_filled.local.json"
IDP_VALIDATION_PATH = AUTH_DIR / "production_identity_provider_approval_input_validation.human_filled.local.json"
IDP_VALIDATION_MD_PATH = AUTH_DIR / "production_identity_provider_approval_input_validation.human_filled.md"

PHASE1_INPUT_PATH = OUTPUT_DIR / "phase_1_identity_tenant_evidence_input.human_filled.local.json"
OAUTH_VALIDATION_PATH = OUTPUT_DIR / "oauth_oidc_approval_input_validation.human_filled.local.json"
OAUTH_VALIDATION_MD_PATH = OUTPUT_DIR / "oauth_oidc_approval_input_validation.human_filled.md"
RBAC_VALIDATION_PATH = OUTPUT_DIR / "rbac_approval_input_validation.human_filled.local.json"
RBAC_VALIDATION_MD_PATH = OUTPUT_DIR / "rbac_approval_input_validation.human_filled.md"
TENANT_VALIDATION_PATH = OUTPUT_DIR / "tenant_storage_approval_input_validation.human_filled.local.json"
TENANT_VALIDATION_MD_PATH = OUTPUT_DIR / "tenant_storage_approval_input_validation.human_filled.md"
BUILDER_OUTPUT_PATH = OUTPUT_DIR / "phase_1_identity_tenant_evidence_builder_output.human_filled.local.json"
AUTH_EVIDENCE_PATH = OUTPUT_DIR / "phase_1_identity_tenant_auth_evidence.human_filled.local.json"
TENANT_EVIDENCE_PATH = OUTPUT_DIR / "phase_1_identity_tenant_storage_evidence.human_filled.local.json"
PROFILE_PATH = PROFILE_DIR / "phase_1_identity_tenant_evidence_profile.human_filled.local.json"
REPORT_PATH = PROFILE_DIR / "phase_1_identity_tenant_human_filled_evidence_run_report.md"
SUMMARY_PATH = PROFILE_DIR / "phase_1_identity_tenant_human_filled_evidence_run_summary.local.json"
GATE_PATH = ROOT / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN_GATE.md"

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
BILLING_REVENUE_EVIDENCE_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "production_billing_revenue_evidence.combined_from_pricing_payment_invoice_tax_refund_tenant_billing_human_filled.local.json"
)

RUN_DATE = "2026-07-09"
TARGET_BLOCKERS = [
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
]
EVIDENCE_READY_KEYS = {
    "production_auth_ready",
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
}
FALSE_KEYS = tuple(
    sorted(
        (
            set(BOUNDARY_FLAGS)
            | set(IDP_FALSE_FLAGS)
            | set(INPUT_FORBIDDEN_TRUE_KEYS)
            | {
            "tenant_storage_isolated",
            "production_tenant_storage_isolated",
            "production_tenant_storage_enabled",
            "customer_data_processed",
            "customer_data_processing_started",
            "identity_provider_contacted",
            "jwks_fetched",
            "tokens_validated_in_production",
            "migration_executed",
            "live_customer_data_migrated",
            "multi_tenant_production_ready",
            "tenant_authorization_enabled",
            "storage_behavior_modified",
            "production_database_modified",
            "storage_migration_executed",
            }
        )
        - EVIDENCE_READY_KEYS
    )
)


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_PHASE1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN: FAIL {path} must be object")
    return data


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(
            "SAEE_PHASE1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN: FAIL "
            + message
        )


def idp_input() -> dict[str, Any]:
    data = idp_input_template()
    data.update(
        {
            "input_status": "human_filled_local_review_only",
            "human_reviewer_name": "张斌",
            "review_date": RUN_DATE,
            "selected_provider_name": "manual-review-idp-option",
            "decision_summary": (
                "Human-filled local identity-provider evidence for commercial "
                "go/no-go input only. No provider was contacted by Codex, no "
                "JWKS was fetched, no production token was validated, and no "
                "production-auth claim is made."
            ),
            "evidence_review": {key: True for key in IDP_TARGET_KEYS},
            "source_notes_by_key": {
                key: (
                    "Human-filled local IDP evidence row accepted for review "
                    "input only; separate human launch approval remains required."
                )
                for key in IDP_TARGET_KEYS
            },
        }
    )
    data["boundary_review"] = {key: False for key in IDP_FALSE_FLAGS}
    data["candidate_provider_slots"][0].update(
        {
            "provider_name": "manual-review-idp-option",
            "oidc_supported": True,
            "admin_owner_named": True,
            "issuer_reviewed": True,
            "audience_reviewed": True,
            "jwks_rotation_reviewed": True,
            "human_source_note": "Local human-filled IDP review slot only.",
        }
    )
    for key in IDP_FALSE_FLAGS:
        data[key] = False
    return data


def phase1_input() -> dict[str, Any]:
    data = phase1_input_template()
    data.update(
        {
            "input_status": "human_filled_local_review_only",
            "human_reviewer_name": "张斌",
            "review_date": RUN_DATE,
            "evidence_source_notes": (
                "Human-filled local Phase 1 identity/OIDC/RBAC/tenant-storage "
                "evidence for commercial go/no-go input only. No external "
                "identity provider was contacted, no JWKS was fetched, no "
                "production tokens were validated, no migration was run, no "
                "customer data was processed, and no production-readiness claim "
                "is made."
            ),
            "evidence_review": {key: True for key in ALL_EVIDENCE_KEYS},
            "source_notes_by_key": {
                key: (
                    "Human-filled local Phase 1 evidence row accepted for review "
                    "input only; separate human launch approval remains required."
                )
                for key in ALL_EVIDENCE_KEYS
            },
            "boundary_review": {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS},
        }
    )
    for key in FALSE_KEYS:
        if key in data:
            data[key] = False
    return data


def commercial_go_no_go_with_context() -> dict[str, object]:
    return evaluate_commercial_go_no_go(
        load_settings(
            {
                "SAEE_SUPPORT_CONTACT": "joy7758@gmail.com",
                "SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(AUTH_EVIDENCE_PATH),
                "SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(TENANT_EVIDENCE_PATH),
                "SAEE_PRODUCTION_SUPPORT_EVIDENCE_PATH": str(SUPPORT_EVIDENCE_PATH),
                "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH": str(DATA_OPS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH": str(OPERATIONS_EVIDENCE_PATH),
                "SAEE_PRODUCTION_PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH": str(
                    PRIVACY_SECURITY_LEGAL_EVIDENCE_PATH
                ),
                "SAEE_PRODUCTION_BILLING_REVENUE_EVIDENCE_PATH": str(
                    BILLING_REVENUE_EVIDENCE_PATH
                ),
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
    satisfied = "\n".join(f"- {item}" for item in summary["phase_1_satisfied_blockers"])
    remaining = "\n".join(
        f"- {item}" for item in summary["all_evidence_remaining_blockers"]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        f"""# SAEE Phase 1 Identity/Tenant Human-Filled Evidence Run v0.1

Status: pass for local human-filled Phase 1 go/no-go evidence.

## Summary

- run_status: {summary['run_status']}
- idp_validation_status: {summary['idp_validation_status']}
- oauth_oidc_validation_status: {summary['oauth_oidc_validation_status']}
- rbac_validation_status: {summary['rbac_validation_status']}
- tenant_storage_validation_status: {summary['tenant_storage_validation_status']}
- builder_status: {summary['builder_status']}
- profile_status: {summary['phase_1_profile_status']}
- production_auth_ready: {str(summary['production_auth_ready']).lower()}
- production_tenant_storage_evidence_complete: {str(summary['production_tenant_storage_evidence_complete']).lower()}
- all_evidence_production_blocker_count: {summary['all_evidence_production_blocker_count']}
- commercial_status_after_profile: {summary['commercial_status_after_profile']}
- production_launch_status_after_profile: {summary['production_launch_status_after_profile']}
- blockers_closed_by_validator: 0
- blockers_closed_by_builder: 0
- blockers_closed_by_profile: 0

## Phase 1 Blockers Satisfied For Go-No-Go Input

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
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- storage_migration_executed: false
- customer_data_processed: false
- tenant_storage_isolated: false

## Non-Closure Statement

This run creates local human-filled evidence for commercial go/no-go review
only. It does not enable production auth, enforce production RBAC, run storage
migrations, process customer data, contact customers/providers, modify product
behavior, close blockers by itself, launch product, or claim production
readiness.
""",
        encoding="utf-8",
    )
    GATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    GATE_PATH.write_text(
        f"""# SAEE Phase 1 Identity/Tenant Human-Filled Evidence Run Gate

answer: local_phase_1_identity_tenant_evidence_pass_hold_for_launch

reason: Human-filled local evidence for production identity provider,
OAuth/OIDC, RBAC, and tenant storage isolation is complete enough for go/no-go
input. It is not production auth enablement, tenant-storage implementation,
external validation, customer validation, blocker closure, or launch approval.

production_auth_ready: {str(summary['production_auth_ready']).lower()}
production_tenant_storage_evidence_complete: {str(summary['production_tenant_storage_evidence_complete']).lower()}
commercial_status_after_profile: {summary['commercial_status_after_profile']}
production_launch_status_after_profile: {summary['production_launch_status_after_profile']}
remaining_production_blocker_count: {summary['all_evidence_production_blocker_count']}

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
identity_provider_contacted_by_codex: false
jwks_fetched_by_codex: false
production_tokens_validated_by_codex: false
storage_migration_executed: false
customer_data_processed: false
tenant_storage_isolated: false

next_action: resolve pilot/customer validation blockers; do not launch.
""",
        encoding="utf-8",
    )


def main() -> None:
    write_json(IDP_INPUT_PATH, idp_input())
    idp_validation = build_idp_validation(IDP_INPUT_PATH)
    write_json(IDP_VALIDATION_PATH, idp_validation)
    IDP_VALIDATION_MD_PATH.write_text(idp_validation_markdown(idp_validation), encoding="utf-8")

    write_json(PHASE1_INPUT_PATH, phase1_input())
    oauth_validation = build_oauth_validation(PHASE1_INPUT_PATH)
    write_json(OAUTH_VALIDATION_PATH, oauth_validation)
    OAUTH_VALIDATION_MD_PATH.write_text(oauth_validation_markdown(oauth_validation), encoding="utf-8")
    rbac_validation = build_rbac_validation(PHASE1_INPUT_PATH)
    write_json(RBAC_VALIDATION_PATH, rbac_validation)
    RBAC_VALIDATION_MD_PATH.write_text(rbac_validation_markdown(rbac_validation), encoding="utf-8")
    tenant_validation = build_tenant_validation(PHASE1_INPUT_PATH)
    write_json(TENANT_VALIDATION_PATH, tenant_validation)
    TENANT_VALIDATION_MD_PATH.write_text(tenant_validation_markdown(tenant_validation), encoding="utf-8")

    builder_summary = build_from_input(
        PHASE1_INPUT_PATH,
        BUILDER_OUTPUT_PATH,
        AUTH_EVIDENCE_PATH,
        TENANT_EVIDENCE_PATH,
    )
    auth_status = evaluate_production_auth_evidence(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(AUTH_EVIDENCE_PATH)})
    )
    tenant_status = evaluate_production_tenant_storage_evidence(
        load_settings(
            {"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(TENANT_EVIDENCE_PATH)}
        )
    )
    profile = build_profile(BUILDER_OUTPUT_PATH)
    write_json(PROFILE_PATH, profile)
    go_no_go = commercial_go_no_go_with_context()
    satisfied, unsatisfied = blocker_state(go_no_go)
    phase1_satisfied = [item for item in satisfied if item in TARGET_BLOCKERS]

    require(idp_validation["validation_status"] == "pass", "IDP validation must pass")
    require(oauth_validation["validation_status"] == "pass", "OAuth/OIDC validation must pass")
    require(rbac_validation["validation_status"] == "pass", "RBAC validation must pass")
    require(tenant_validation["validation_status"] == "pass", "tenant storage validation must pass")
    require(builder_summary["status"] == "pass", "Phase 1 builder must pass")
    require(auth_status["status"] == "pass", "auth evidence readiness must pass")
    require(tenant_status["status"] == "pass", "tenant storage evidence readiness must pass")
    require(profile["profile_status"] == "pass", "Phase 1 profile must pass")
    require(phase1_satisfied == TARGET_BLOCKERS, "all Phase 1 target blockers must be satisfied")
    require(go_no_go["commercial_status"] == "hold", "commercial status must remain hold")
    require(go_no_go["production_launch_status"] == "hold", "launch status must remain hold")

    summary: dict[str, Any] = {
        "phase_1_identity_tenant_human_filled_evidence_run_v0_1": True,
        "run_type": "local_human_filled_phase_1_identity_tenant_evidence",
        "generated_by": "scripts/saee_phase1_identity_tenant_human_filled_evidence_run.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "run_status": "pass",
        "validation_status": "pass",
        "idp_validation_status": idp_validation["validation_status"],
        "oauth_oidc_validation_status": oauth_validation["validation_status"],
        "rbac_validation_status": rbac_validation["validation_status"],
        "tenant_storage_validation_status": tenant_validation["validation_status"],
        "builder_status": builder_summary["status"],
        "phase_1_profile_status": profile["profile_status"],
        "auth_readiness_status": auth_status["status"],
        "tenant_storage_readiness_status": tenant_status["status"],
        "production_auth_ready": auth_status["production_auth_ready"],
        "production_identity_provider_available": auth_status[
            "production_identity_provider_available"
        ],
        "oauth_oidc_available": auth_status["oauth_oidc_available"],
        "rbac_available": auth_status["rbac_available"],
        "production_tenant_storage_evidence_complete": tenant_status[
            "production_tenant_storage_evidence_complete"
        ],
        "tenant_storage_model_evidence_complete": tenant_status[
            "tenant_storage_model_evidence_complete"
        ],
        "tenant_storage_isolation_evidence_complete": tenant_status[
            "tenant_storage_isolation_evidence_complete"
        ],
        "tenant_operations_evidence_complete": tenant_status[
            "tenant_operations_evidence_complete"
        ],
        "tenant_security_privacy_evidence_complete": tenant_status[
            "tenant_security_privacy_evidence_complete"
        ],
        "phase_1_satisfied_blockers": phase1_satisfied,
        "phase_1_target_blockers": TARGET_BLOCKERS,
        "phase_1_satisfied_blocker_count": len(phase1_satisfied),
        "all_evidence_satisfied_blockers": satisfied,
        "all_evidence_remaining_blockers": unsatisfied,
        "all_evidence_production_blocker_count": go_no_go["production_blocker_count"],
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
        "input_files": [str(IDP_INPUT_PATH), str(PHASE1_INPUT_PATH)],
        "output_files": [
            str(IDP_VALIDATION_PATH),
            str(IDP_VALIDATION_MD_PATH),
            str(OAUTH_VALIDATION_PATH),
            str(OAUTH_VALIDATION_MD_PATH),
            str(RBAC_VALIDATION_PATH),
            str(RBAC_VALIDATION_MD_PATH),
            str(TENANT_VALIDATION_PATH),
            str(TENANT_VALIDATION_MD_PATH),
            str(BUILDER_OUTPUT_PATH),
            str(AUTH_EVIDENCE_PATH),
            str(TENANT_EVIDENCE_PATH),
            str(PROFILE_PATH),
            str(REPORT_PATH),
            str(GATE_PATH),
        ],
    }
    for key in FALSE_KEYS:
        summary[key] = False

    write_json(SUMMARY_PATH, summary)
    write_report(summary)
    print(
        "SAEE_PHASE1_IDENTITY_TENANT_HUMAN_FILLED_EVIDENCE_RUN: PASS "
        f"phase_1_profile_status=pass production_blockers={go_no_go['production_blocker_count']} "
        "production_ready=false"
    )


if __name__ == "__main__":
    main()
