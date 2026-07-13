#!/usr/bin/env python3
"""Generate a human decision runbook for production identity-provider input.

This runbook explains how a human owner can turn reviewed identity-provider
facts into a local validator input. It does not select or contact an identity
provider, fetch JWKS, validate production tokens, enable production auth,
collect evidence, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUTH_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"

OUTPUT_JSON = AUTH_DIR / "production_identity_provider_human_decision_runbook.local.json"
OUTPUT_MD = AUTH_DIR / "production_identity_provider_human_decision_runbook.md"
OUTPUT_CSV = AUTH_DIR / "production_identity_provider_human_decision_runbook.csv"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK_RECOMMENDATION_GATE.md"
)

CSV_FIELDS = [
    "step_id",
    "title",
    "human_action",
    "expected_output",
    "command_or_file",
    "boundary",
]

FALSE_FLAGS: dict[str, bool] = {
    "human_decision_recorded": False,
    "human_filled_input_generated": False,
    "identity_provider_selected_by_codex": False,
    "identity_provider_contacted": False,
    "identity_provider_contacted_by_codex": False,
    "jwks_fetched": False,
    "jwks_fetched_by_codex": False,
    "production_tokens_validated_by_codex": False,
    "tokens_validated_in_production": False,
    "production_auth_enabled": False,
    "production_auth_ready": False,
    "oauth_oidc_available": False,
    "rbac_available": False,
    "rbac_enforced_in_production": False,
    "evidence_collection_authorized": False,
    "execution_authorized": False,
    "development_permission_granted": False,
    "production_ready": False,
    "customer_validated": False,
    "customer_contacted": False,
    "product_launched": False,
    "public_sdk_released": False,
    "private_core_exposed": False,
    "runtime_modified": False,
    "backend_modified": False,
    "kernel_modified": False,
    "api_schema_modified": False,
    "external_calls_made_by_codex": False,
    "external_model_api_called": False,
    "external_ai_assistant_tested": False,
    "blockers_closed_by_runbook": False,
}


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def runbook_steps() -> list[dict[str, str]]:
    return [
        {
            "step_id": "PIDP-HUMAN-001",
            "title": "Review existing decision packet",
            "human_action": "Open the production identity-provider decision packet and inspect the candidate provider slots.",
            "expected_output": "Human understands which provider candidates can be reviewed.",
            "command_or_file": "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_packet.md",
            "boundary": "No provider contact or production configuration by Codex.",
        },
        {
            "step_id": "PIDP-HUMAN-002",
            "title": "Collect human-reviewed source notes",
            "human_action": "Human owner reviews IdP admin documentation or internal security decision records and writes short source notes.",
            "expected_output": "Source notes for selected provider, admin owner, issuer, audience, and JWKS rotation policy.",
            "command_or_file": "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_input_completion.csv",
            "boundary": "No web/API fetching or vendor contact by Codex.",
        },
        {
            "step_id": "PIDP-HUMAN-003",
            "title": "Provide required text fields",
            "human_action": "Human provides reviewer name, review date, selected provider name, and decision summary.",
            "expected_output": "Required text fields available for local validator input generation.",
            "command_or_file": "human_reviewer_name, review_date, selected_provider_name, decision_summary",
            "boundary": "No customer validation or launch claim.",
        },
        {
            "step_id": "PIDP-HUMAN-004",
            "title": "Generate local human-filled input",
            "human_action": "Run the completion helper with explicit human-provided fields and source notes.",
            "expected_output": "production_identity_provider_decision_input.human_filled.local.json",
            "command_or_file": "python3 scripts/saee_production_identity_provider_input_completion_helper.py --generate-input --human-reviewer-name '<human>' --review-date '<YYYY-MM-DD>' --selected-provider-name '<provider>' --decision-summary '<summary>' --selected-provider-slot idp_candidate_a --candidate-source-note '<source note>' --confirm-production-identity-provider-selected true --confirm-identity-provider-admin-owner-named true --confirm-oidc-issuer-verified true --confirm-oidc-audience-approved true --confirm-jwks-rotation-policy-reviewed true --source-note-production-identity-provider-selected '<source note>' --source-note-identity-provider-admin-owner-named '<source note>' --source-note-oidc-issuer-verified '<source note>' --source-note-oidc-audience-approved '<source note>' --source-note-jwks-rotation-policy-reviewed '<source note>'",
            "boundary": "Generated local input is not evidence collection, auth enablement, or blocker closure.",
        },
        {
            "step_id": "PIDP-HUMAN-005",
            "title": "Validate local human-filled input",
            "human_action": "Run the approval input validator against the generated local input.",
            "expected_output": "Validator status pass, hold, or stop.",
            "command_or_file": "python3 scripts/saee_production_identity_provider_approval_input_validator.py --input phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.human_filled.local.json",
            "boundary": "Validator pass does not itself close blockers.",
        },
        {
            "step_id": "PIDP-HUMAN-006",
            "title": "Request separate evidence-builder approval",
            "human_action": "If validator status is pass, create a separate human-approved evidence-builder request.",
            "expected_output": "Separate approved evidence request, or hold if validation is incomplete.",
            "command_or_file": "phase_b_product/commercial_readiness/PHASE_1_IDENTITY_TENANT_EVIDENCE_BUILDER_V0_1.md",
            "boundary": "No evidence builder execution from this runbook.",
        },
    ]


def build_payload() -> dict[str, Any]:
    payload: dict[str, Any] = {
        "production_identity_provider_human_decision_runbook_v0_1": True,
        "runbook_type": "saee_production_identity_provider_human_decision_runbook",
        "runbook_version": "v0.1",
        "runbook_scope": "local_human_identity_provider_decision_procedure",
        "status": "hold_human_identity_provider_decision_required",
        "target_blocker_id": "production_identity_provider",
        "runbook_ready": True,
        "step_count": 6,
        "completion_helper_available": True,
        "explicit_input_generation_supported": True,
        "approval_input_validator_available": True,
        "separate_evidence_builder_request_required": True,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_production_identity_provider_human_decision_runbook.py",
        "runbook_json": rel(OUTPUT_JSON),
        "runbook_report": rel(OUTPUT_MD),
        "runbook_csv": rel(OUTPUT_CSV),
        "source_completion_helper": "scripts/saee_production_identity_provider_input_completion_helper.py",
        "source_validator": "scripts/saee_production_identity_provider_approval_input_validator.py",
        "source_template": "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.template.json",
        "default_generated_input": "phase_b_product/commercial_readiness/auth_evidence/production_identity_provider_decision_input.human_filled.local.json",
        "next_action": "A human owner should follow PIDP-HUMAN-001 through PIDP-HUMAN-005, then request separate evidence-builder approval only if the validator passes.",
        "steps": runbook_steps(),
    }
    payload.update(FALSE_FLAGS)
    return payload


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, steps: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(steps)


def markdown_report(payload: dict[str, Any]) -> str:
    lines = [
        "# SAEE Production Identity Provider Human Decision Runbook",
        "",
        f"Status: {payload['status']}.",
        "",
        "This runbook gives the human-only path for turning reviewed production identity-provider facts into a local validator input. It does not select or contact an identity provider, fetch JWKS, validate production tokens, enable production auth, collect evidence, close blockers, launch product, or claim production readiness.",
        "",
        "## Summary",
        "",
        f"- runbook_type: {payload['runbook_type']}",
        f"- runbook_scope: {payload['runbook_scope']}",
        f"- target_blocker_id: {payload['target_blocker_id']}",
        "- runbook_ready: true",
        "- completion_helper_available: true",
        "- explicit_input_generation_supported: true",
        "- approval_input_validator_available: true",
        "- separate_evidence_builder_request_required: true",
        "- human_decision_recorded: false",
        "- human_filled_input_generated: false",
        "- identity_provider_selected_by_codex: false",
        "- identity_provider_contacted: false",
        "- jwks_fetched: false",
        "- production_auth_enabled: false",
        "- production_ready: false",
        "- blockers_closed_by_runbook: false",
        "",
        "## Human Procedure",
        "",
        "| Step | Title | Human Action | Expected Output | Command Or File | Boundary |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for step in payload["steps"]:
        lines.append(
            "| {step_id} | {title} | {human_action} | {expected_output} | `{command_or_file}` | {boundary} |".format(
                **step
            )
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- external_calls_made_by_codex: false",
            "- external_model_api_called: false",
            "- identity_provider_contacted_by_codex: false",
            "- jwks_fetched_by_codex: false",
            "- production_tokens_validated_by_codex: false",
            "- production_auth_enabled: false",
            "- evidence_collection_authorized: false",
            "- execution_authorized: false",
            "- production_ready: false",
            "- customer_validated: false",
            "- product_launched: false",
            "- private_core_exposed: false",
        ]
    )
    return "\n".join(lines) + "\n"


def write_top_doc(payload: dict[str, Any]) -> None:
    TOP_DOC.write_text(
        f"""# SAEE Production Identity Provider Human Decision Runbook v0.1

production_identity_provider_human_decision_runbook_v0_1: true
status: {payload['status']}
target_blocker_id: production_identity_provider
runbook_ready: true
step_count: 6
completion_helper_available: true
explicit_input_generation_supported: true
approval_input_validator_available: true
human_decision_recorded: false
human_filled_input_generated: false
identity_provider_selected_by_codex: false
identity_provider_contacted: false
jwks_fetched: false
production_auth_enabled: false
production_ready: false
blockers_closed_by_runbook: false

## Purpose

This runbook tells a human owner how to use the existing identity-provider
completion helper and approval-input validator to prepare the first
`production_identity_provider` decision input.

It is recommended for human execution guidance only. It is not recommended for
automated identity-provider selection, provider contact, JWKS fetch, production
token validation, production auth enablement, evidence-builder execution,
blocker closure, product launch, or production-readiness claims.

## Outputs

- runbook JSON: `{rel(OUTPUT_JSON)}`
- runbook report: `{rel(OUTPUT_MD)}`
- runbook CSV: `{rel(OUTPUT_CSV)}`

## Boundary

This runbook does not modify runtime, backend, kernel, API schema, landing page,
or private core. It does not call external services, contact identity
providers, fetch JWKS, validate production tokens, enable production auth,
collect evidence, close blockers, contact customers, launch product, or claim
production readiness.
""",
        encoding="utf-8",
    )


def write_gate(payload: dict[str, Any]) -> None:
    GATE.write_text(
        f"""# SAEE Production Identity Provider Human Decision Runbook Recommendation Gate

answer: recommend
recommend_for_human_identity_provider_decision_guidance: true
recommend_for_production: false
recommend_for_automated_provider_selection: false
recommend_for_identity_provider_contact: false
recommend_for_jwks_fetch: false
recommend_for_token_validation: false
recommend_for_auth_enablement: false
recommend_for_evidence_builder_execution: false
recommend_for_blocker_closure: false

## Reason

The `production_identity_provider` blocker remains the first unsatisfied
commercial launch blocker. The runbook makes the required human decision path
explicit without executing provider contact, production auth work, evidence
collection, or blocker closure.

## Scope

- status: {payload['status']}
- runbook_ready: true
- step_count: 6
- human_decision_recorded: false
- human_filled_input_generated: false
- identity_provider_selected_by_codex: false
- identity_provider_contacted: false
- jwks_fetched: false
- production_auth_enabled: false
- production_ready: false
- blockers_closed_by_runbook: false

## Boundary

This gate recommends the runbook only as a local human-guidance surface. It
does not recommend SAEE for production launch, automated identity-provider
selection, IdP contact, JWKS fetch, production token validation, auth
enablement, evidence-builder execution, blocker closure, or production-readiness
claims.
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_csv(OUTPUT_CSV, payload["steps"])
    OUTPUT_MD.write_text(markdown_report(payload), encoding="utf-8")
    write_top_doc(payload)
    write_gate(payload)
    print(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_HUMAN_DECISION_RUNBOOK: PASS "
        f"status={payload['status']} blockers_closed_by_runbook=false production_ready=false"
    )


if __name__ == "__main__":
    main()
