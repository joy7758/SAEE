#!/usr/bin/env python3
"""Build Phase 1 auth/tenant evidence from human-filled local input.

This builder converts a local, human-filled JSON review packet into the
production auth and tenant-storage evidence shapes consumed by the commercial
go/no-go checks. It does not contact identity providers, fetch JWKS, validate
production tokens, run migrations, process customer data, modify backend or
runtime behavior, close blockers by default, or claim production readiness.
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
from saee_backend.services.production_auth_evidence import (
    AUTH_IDP_KEYS,
    FORBIDDEN_TRUE_KEYS as AUTH_FORBIDDEN_TRUE_KEYS,
    OAUTH_OIDC_KEYS,
    RBAC_KEYS,
    evaluate_production_auth_evidence,
)
from saee_backend.services.production_tenant_storage_evidence import (
    FORBIDDEN_TRUE_KEYS as TENANT_FORBIDDEN_TRUE_KEYS,
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
    evaluate_production_tenant_storage_evidence,
)


OUTPUT_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
INPUT_TEMPLATE_PATH = OUTPUT_DIR / "phase_1_identity_tenant_evidence_input.template.json"
DEFAULT_OUTPUT_PATH = OUTPUT_DIR / "phase_1_identity_tenant_evidence_builder_output.local.json"
DEFAULT_AUTH_OUTPUT_PATH = OUTPUT_DIR / "phase_1_identity_tenant_auth_evidence.from_input.local.json"
DEFAULT_TENANT_OUTPUT_PATH = (
    OUTPUT_DIR / "phase_1_identity_tenant_storage_evidence.from_input.local.json"
)
REPORT_PATH = OUTPUT_DIR / "phase_1_identity_tenant_evidence_builder_report.md"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_BUILDER_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PHASE_1_IDENTITY_TENANT_EVIDENCE_BUILDER_RECOMMENDATION_GATE.md"
)

AUTH_KEYS = AUTH_IDP_KEYS + OAUTH_OIDC_KEYS + RBAC_KEYS
TENANT_KEYS = (
    TENANT_STORAGE_MODEL_KEYS
    + TENANT_ISOLATION_TEST_KEYS
    + TENANT_OPERATIONS_KEYS
    + TENANT_SECURITY_PRIVACY_KEYS
)
ALL_EVIDENCE_KEYS = AUTH_KEYS + TENANT_KEYS
INPUT_FORBIDDEN_TRUE_KEYS = tuple(
    sorted(
        set(AUTH_FORBIDDEN_TRUE_KEYS)
        | set(TENANT_FORBIDDEN_TRUE_KEYS)
        | {
            "codex_contacted_identity_provider",
            "codex_fetched_jwks",
            "codex_validated_production_tokens",
            "codex_ran_storage_migration",
            "codex_inferred_missing_evidence",
            "identity_provider_contacted_by_codex",
            "jwks_fetched_by_codex",
            "production_tokens_validated_by_codex",
            "storage_migration_executed",
            "evidence_collection_authorized",
            "execution_authorized",
            "blockers_closed_by_builder",
        }
    )
)
TARGET_BLOCKERS = [
    "production_identity_provider",
    "oauth_oidc",
    "rbac",
    "tenant_storage_isolation",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_BUILDER: FAIL: " + message)


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_BUILDER: FAIL: invalid input {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), "input JSON must be an object")
    return data


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bool_value(data: dict[str, Any], key: str) -> bool:
    return data.get(key) is True


def evidence_review_flags(data: dict[str, Any]) -> dict[str, bool]:
    review = data.get("evidence_review", {})
    if not isinstance(review, dict):
        review = {}
    return {key: bool_value(review, key) for key in ALL_EVIDENCE_KEYS}


def source_notes(data: dict[str, Any]) -> dict[str, str]:
    notes = data.get("source_notes_by_key", {})
    if not isinstance(notes, dict):
        return {}
    return {key: str(notes.get(key, "")).strip() for key in ALL_EVIDENCE_KEYS}


def boundary_violations(data: dict[str, Any]) -> list[str]:
    violations = [key for key in INPUT_FORBIDDEN_TRUE_KEYS if data.get(key) is True]
    boundary = data.get("boundary_review", {})
    if not isinstance(boundary, dict):
        violations.append("boundary_review_missing")
        return violations
    for key in INPUT_FORBIDDEN_TRUE_KEYS:
        if boundary.get(key) is True:
            violations.append(f"boundary_review.{key}")
    return violations


def input_metadata_complete(data: dict[str, Any]) -> bool:
    reviewer = str(data.get("human_reviewer_name", "")).strip()
    review_date = str(data.get("review_date", "")).strip()
    notes = str(data.get("evidence_source_notes", "")).strip()
    return bool(reviewer and review_date and notes)


def complete_input(data: dict[str, Any]) -> bool:
    flags = evidence_review_flags(data)
    notes = source_notes(data)
    all_flags_true = all(flags.values())
    all_notes_present = all(bool(notes.get(key)) for key in ALL_EVIDENCE_KEYS)
    return (
        data.get("phase_1_identity_tenant_evidence_input_v0_1") is True
        and input_metadata_complete(data)
        and all_flags_true
        and all_notes_present
        and not boundary_violations(data)
    )


def input_template() -> dict[str, Any]:
    return {
        "phase_1_identity_tenant_evidence_input_v0_1": True,
        "input_status": "template_not_filled",
        "human_reviewer_name": "",
        "review_date": "",
        "evidence_source_notes": "",
        "evidence_review": {key: False for key in ALL_EVIDENCE_KEYS},
        "source_notes_by_key": {key: "" for key in ALL_EVIDENCE_KEYS},
        "boundary_review": {key: False for key in INPUT_FORBIDDEN_TRUE_KEYS},
        "codex_inferred_missing_evidence": False,
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "codex_ran_storage_migration": False,
        "identity_provider_contacted_by_codex": False,
        "jwks_fetched_by_codex": False,
        "production_tokens_validated_by_codex": False,
        "storage_migration_executed": False,
        "customer_data_processed": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
        "customer_contacted": False,
        "builder_note": (
            "A human owner must fill all evidence_review flags, source notes, "
            "review metadata, and boundary review fields. Codex must not infer "
            "missing production evidence."
        ),
    }


def build_auth_evidence(data: dict[str, Any], input_path: Path, *, complete: bool) -> dict[str, Any]:
    flags = evidence_review_flags(data)
    evidence: dict[str, Any] = {
        "auth_evidence_type": "production_auth_evidence",
        "evidence_scope": "human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_phase1_identity_tenant_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in AUTH_KEYS:
        evidence[key] = flags[key] and complete
    for key in AUTH_FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def build_tenant_evidence(data: dict[str, Any], input_path: Path, *, complete: bool) -> dict[str, Any]:
    flags = evidence_review_flags(data)
    evidence: dict[str, Any] = {
        "tenant_storage_evidence_type": "production_tenant_storage_evidence",
        "evidence_scope": "human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs",
        "evidence_version": "v0.1",
        "generated_by": "scripts/saee_phase1_identity_tenant_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "source_input_path": str(input_path),
        "human_filled_input_required": True,
        "human_reviewer_name_recorded": bool(str(data.get("human_reviewer_name", "")).strip()),
        "review_date_recorded": bool(str(data.get("review_date", "")).strip()),
        "codex_ran_storage_migration": False,
        "codex_inferred_missing_evidence": False,
    }
    for key in TENANT_KEYS:
        evidence[key] = flags[key] and complete
    for key in TENANT_FORBIDDEN_TRUE_KEYS:
        evidence[key] = False
    return evidence


def auth_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_auth_evidence(
        load_settings({"SAEE_PRODUCTION_AUTH_EVIDENCE_PATH": str(path)})
    )


def tenant_readiness(path: Path) -> dict[str, object]:
    return evaluate_production_tenant_storage_evidence(
        load_settings({"SAEE_PRODUCTION_TENANT_STORAGE_EVIDENCE_PATH": str(path)})
    )


def build_from_input(
    input_path: Path,
    output_path: Path,
    auth_output_path: Path,
    tenant_output_path: Path,
) -> dict[str, Any]:
    data = read_json(input_path)
    complete = complete_input(data)
    violations = boundary_violations(data)
    flags = evidence_review_flags(data)
    missing = [key for key in ALL_EVIDENCE_KEYS if not flags[key]]
    status = "stop" if violations else ("pass" if complete else "hold")

    auth_evidence = build_auth_evidence(data, input_path, complete=complete)
    tenant_evidence = build_tenant_evidence(data, input_path, complete=complete)
    write_json(auth_output_path, auth_evidence)
    write_json(tenant_output_path, tenant_evidence)

    auth_status = auth_readiness(auth_output_path)
    tenant_status = tenant_readiness(tenant_output_path)
    summary: dict[str, Any] = {
        "phase_1_identity_tenant_evidence_builder_v0_1": True,
        "builder_scope": "human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs",
        "generated_by": "scripts/saee_phase1_identity_tenant_evidence_builder.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "input": str(input_path),
        "output": str(output_path),
        "auth_evidence_output": str(auth_output_path),
        "tenant_storage_evidence_output": str(tenant_output_path),
        "status": status,
        "input_complete": complete,
        "metadata_complete": input_metadata_complete(data),
        "required_evidence_item_count": len(ALL_EVIDENCE_KEYS),
        "auth_required_evidence_item_count": len(AUTH_KEYS),
        "tenant_required_evidence_item_count": len(TENANT_KEYS),
        "provided_evidence_item_count": sum(1 for value in flags.values() if value),
        "missing_required_evidence_count": len(missing),
        "missing_required_evidence": missing,
        "input_boundary_violation_count": len(violations),
        "input_boundary_violations": violations,
        "auth_readiness_status": auth_status["status"],
        "auth_production_ready_for_review": auth_status["production_auth_ready"],
        "tenant_storage_readiness_status": tenant_status["status"],
        "tenant_storage_production_ready_for_review": tenant_status[
            "production_tenant_storage_evidence_complete"
        ],
        "target_blocker_ids": TARGET_BLOCKERS,
        "blockers_closed_by_builder": 0,
        "accepted_for_blocker_closure_count": 0,
        "human_review_required": True,
        "separate_go_no_go_profile_required": True,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "public_sdk_released": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
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
        "next_action": (
            "If a human fills all 33 evidence items with source notes, use the generated "
            "auth and tenant evidence files only as go/no-go input; do not treat this "
            "builder as production launch approval."
        ),
    }
    write_json(output_path, summary)
    return summary


def write_readme() -> None:
    README_PATH.write_text(
        """# SAEE Phase 1 Identity/Tenant Evidence Builder

Status: local builder available; default output is hold.

This directory contains a human-fillable evidence input template and generated
local outputs for the Phase 1 production identity/OIDC/RBAC/tenant-storage
evidence path. It converts human-approved evidence into the existing
production-auth and production-tenant-storage evidence shapes.

Boundary:

- no identity provider contacted
- no JWKS fetched
- no production token validation
- no storage migration
- no customer data processing
- no blocker closure by default
- no production-ready claim
- no backend, runtime, kernel, API schema, landing page, or private core change

Generated default output remains `hold` until a human owner provides complete
production evidence for all 33 required items.

Related pre-builder checks:

- `oauth_oidc_approval_input_validation.local.json` validates the five
  OAuth/OIDC evidence fields before builder use. It is a local completeness and
  boundary-safety check only; it does not contact an identity provider, fetch
  JWKS, validate production tokens, enable production auth, close blockers, or
  claim production readiness.
- `rbac_approval_input_validation.local.json` validates the five RBAC evidence
  fields before builder use. It is a local completeness and boundary-safety
  check only; it does not enforce production RBAC, enable production auth,
  close blockers, or claim production readiness.
- `tenant_storage_approval_input_validation.local.json` validates the 18 tenant
  storage evidence fields before builder use. It is a local completeness and
  boundary-safety check only; it does not implement production multi-tenancy,
  modify storage behavior, run migrations, process customer data, close
  blockers, or claim production readiness.
""",
        encoding="utf-8",
    )


def report_markdown(summary: dict[str, Any]) -> str:
    return f"""# SAEE Phase 1 Identity/Tenant Evidence Builder Report

Status: local builder available; default output is hold.

## Summary

- builder_scope: human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs
- required_evidence_item_count: {summary['required_evidence_item_count']}
- auth_required_evidence_item_count: {summary['auth_required_evidence_item_count']}
- tenant_required_evidence_item_count: {summary['tenant_required_evidence_item_count']}
- input_complete: {str(summary['input_complete']).lower()}
- status: {summary['status']}
- auth_readiness_status: {summary['auth_readiness_status']}
- tenant_storage_readiness_status: {summary['tenant_storage_readiness_status']}
- blockers_closed_by_builder: 0

## What This Adds

This builder gives human reviewers a concrete input file for Phase 1 production
identity provider, OAuth/OIDC, RBAC, and tenant storage isolation evidence. It
then emits local evidence files that the existing readiness checkers can parse.

## What It Does Not Do

It does not contact identity providers, fetch JWKS, validate production tokens,
run storage migrations, process customer data, close blockers, or mark SAEE as
production ready.

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

## Next Action

Human owners must fill `phase_1_identity_tenant_evidence_input.template.json`
with real production evidence and source notes before these outputs can be used
as a go/no-go evidence profile.
"""


def write_docs(summary: dict[str, Any]) -> None:
    write_readme()
    REPORT_PATH.write_text(report_markdown(summary), encoding="utf-8")
    DOC_PATH.write_text(
        f"""# Phase 1 Identity/Tenant Evidence Builder v0.1

Status: local builder available; default output is hold.

phase_1_identity_tenant_evidence_builder_v0_1: true
builder_scope: human_filled_phase_1_identity_tenant_evidence_to_go_no_go_inputs
required_evidence_item_count: {summary['required_evidence_item_count']}
auth_required_evidence_item_count: {summary['auth_required_evidence_item_count']}
tenant_required_evidence_item_count: {summary['tenant_required_evidence_item_count']}
default_output_status: {summary['status']}
blockers_closed_by_builder: 0
accepted_for_blocker_closure_count: 0

## Purpose

This builder converts a human-filled Phase 1 evidence input into local evidence
files for the existing production auth and tenant-storage readiness checkers.
It is a commercial-readiness evidence intake surface, not product execution.

## Recommendation Gate Answer

answer: conditional
recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false

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

## Entrypoints

- input template: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json`
- builder output: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_builder_output.local.json`
- auth evidence output: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_auth_evidence.from_input.local.json`
- tenant storage evidence output: `phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_storage_evidence.from_input.local.json`
- script: `scripts/saee_phase1_identity_tenant_evidence_builder.py`
- smoke: `scripts/saee_phase1_identity_tenant_evidence_builder_smoke.py`
""",
        encoding="utf-8",
    )
    GATE_PATH.write_text(
        """# SAEE Phase 1 Identity/Tenant Evidence Builder Recommendation Gate

answer: conditional

recommend_for_human_evidence_input: true
recommend_for_blocker_closure: false
recommend_for_production_launch: false
recommend_for_external_execution: false

## Reason

The builder is useful because it gives human reviewers a concrete way to
provide production identity/OIDC/RBAC and tenant-storage evidence in a
machine-checkable shape. It is not sufficient for blocker closure by itself:
the default template is incomplete, and any complete evidence still requires a
separate go/no-go evidence profile and human launch review.

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

Human owners may fill the input template with real evidence. Codex must not
infer missing evidence or treat this builder as production launch approval.
""",
        encoding="utf-8",
    )


def write_template() -> dict[str, Any]:
    template = input_template()
    write_json(INPUT_TEMPLATE_PATH, template)
    return template


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Build local Phase 1 identity/tenant evidence from human-filled input."
    )
    parser.add_argument("--input", default=str(INPUT_TEMPLATE_PATH))
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT_PATH))
    parser.add_argument("--auth-output", default=str(DEFAULT_AUTH_OUTPUT_PATH))
    parser.add_argument("--tenant-output", default=str(DEFAULT_TENANT_OUTPUT_PATH))
    parser.add_argument("--json", action="store_true", help="Print JSON summary.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    write_template()
    summary = build_from_input(
        Path(args.input).expanduser(),
        Path(args.output).expanduser(),
        Path(args.auth_output).expanduser(),
        Path(args.tenant_output).expanduser(),
    )
    write_docs(summary)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(
            "SAEE_PHASE1_IDENTITY_TENANT_EVIDENCE_BUILDER: PASS "
            f"status={summary['status']} "
            f"required_items={summary['required_evidence_item_count']} "
            f"auth_readiness={summary['auth_readiness_status']} "
            f"tenant_storage_readiness={summary['tenant_storage_readiness_status']} "
            "blockers_closed_by_builder=0 production_ready=false"
        )


if __name__ == "__main__":
    main()
