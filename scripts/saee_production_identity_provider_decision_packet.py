#!/usr/bin/env python3
"""Generate the SAEE production identity-provider decision packet.

This packet turns the first Phase 1 commercial blocker into a focused human
decision surface. It does not select a provider, contact an identity provider,
fetch JWKS, validate production tokens, enable production auth, close blockers,
modify backend behavior, or expose private core.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/auth_evidence"
OUTPUT_JSON = OUTPUT_DIR / "production_identity_provider_decision_packet.local.json"
OUTPUT_MD = OUTPUT_DIR / "production_identity_provider_decision_packet.md"
OUTPUT_TEMPLATE = OUTPUT_DIR / "production_identity_provider_decision_input.template.json"
OUTPUT_BOUNDARY = OUTPUT_DIR / "production_identity_provider_decision_packet_boundary_audit.md"
DOC_PATH = (
    ROOT
    / "phase_b_product/commercial_readiness/PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_V0_1.md"
)
GATE_PATH = (
    ROOT
    / "docs/strategy/SAEE_PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET_RECOMMENDATION_GATE.md"
)

TARGET_KEYS = [
    "production_identity_provider_selected",
    "identity_provider_admin_owner_named",
    "oidc_issuer_verified",
    "oidc_audience_approved",
    "jwks_rotation_policy_reviewed",
]

FALSE_FLAGS = [
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
    "production_auth_ready",
    "production_ready",
    "customer_validated",
    "product_launched",
    "public_sdk_released",
    "private_core_exposed",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "identity_provider_contacted_by_codex",
    "jwks_fetched_by_codex",
    "production_tokens_validated_by_codex",
    "production_auth_enabled",
    "rbac_enforced_in_production",
    "blockers_closed_by_packet",
    "task_candidates_executed",
    "development_permission_granted",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def packet() -> dict[str, Any]:
    data: dict[str, Any] = {
        "packet_type": "saee_production_identity_provider_decision_packet",
        "packet_version": "v0.1",
        "status": "ready_for_human_review_not_execution",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
        "generated_by": "scripts/saee_production_identity_provider_decision_packet.py",
        "blocker_target": "production_identity_provider",
        "owner_lane": "engineering_security",
        "decision_scope": "human_review_of_production_identity_provider_selection",
        "human_review_required": True,
        "separate_execution_approval_required": True,
        "target_auth_evidence_keys": TARGET_KEYS,
        "required_human_decision_fields": [
            "provider_name",
            "provider_admin_owner",
            "issuer_url_review_note",
            "audience_review_note",
            "jwks_rotation_policy_note",
            "security_review_note",
            "rollback_or_disable_plan_note",
        ],
        "candidate_provider_slots": [
            {
                "slot_id": "idp_candidate_a",
                "provider_name": "",
                "oidc_supported": None,
                "admin_owner_named": None,
                "issuer_reviewed": None,
                "audience_reviewed": None,
                "jwks_rotation_reviewed": None,
                "human_source_note": "",
            },
            {
                "slot_id": "idp_candidate_b",
                "provider_name": "",
                "oidc_supported": None,
                "admin_owner_named": None,
                "issuer_reviewed": None,
                "audience_reviewed": None,
                "jwks_rotation_reviewed": None,
                "human_source_note": "",
            },
            {
                "slot_id": "idp_candidate_c",
                "provider_name": "",
                "oidc_supported": None,
                "admin_owner_named": None,
                "issuer_reviewed": None,
                "audience_reviewed": None,
                "jwks_rotation_reviewed": None,
                "human_source_note": "",
            },
        ],
        "selection_criteria": [
            "OIDC issuer and audience can be reviewed without exposing secrets.",
            "JWKS rotation and cache policy can be documented by a human owner.",
            "Tenant identity boundary can be mapped to SAEE tenant headers and role claims.",
            "Admin owner, recovery path, and disable/rollback path can be named.",
            "Provider evidence can be copied into the Phase 1 evidence builder only after human approval.",
        ],
        "evidence_mapping": {
            key: {
                "target_blocker": "production_identity_provider",
                "target_builder_path": f"evidence_review.{key}",
                "target_source_note_path": f"source_notes_by_key.{key}",
                "prefill_allowed": False,
                "requires_human_source_note": True,
            }
            for key in TARGET_KEYS
        },
        "next_human_action": (
            "Human owner reviews candidate provider evidence, chooses whether to fill "
            "the Phase 1 identity/tenant evidence input, and then runs the existing "
            "Phase 1 evidence builder."
        ),
    }
    for flag in FALSE_FLAGS:
        data[flag] = False
    return data


def input_template() -> dict[str, Any]:
    return {
        "template_type": "saee_production_identity_provider_decision_input",
        "template_version": "v0.1",
        "input_status": "template_not_filled",
        "human_reviewer_name": "",
        "review_date": "",
        "selected_provider_name": "",
        "decision_summary": "",
        "evidence_review": {key: False for key in TARGET_KEYS},
        "source_notes_by_key": {key: "" for key in TARGET_KEYS},
        "boundary_review": {flag: False for flag in FALSE_FLAGS},
        "candidate_provider_slots": packet()["candidate_provider_slots"],
        "template_note": (
            "This input does not configure SAEE. It is a human review aid for "
            "production_identity_provider evidence only."
        ),
    }


def md_body() -> str:
    rows = "\n".join(
        f"| `{key}` | `production_identity_provider` | `evidence_review.{key}` | human source note required |"
        for key in TARGET_KEYS
    )
    return f"""# SAEE Production Identity Provider Decision Packet v0.1

Status: ready_for_human_review_not_execution.

This packet narrows the first Phase 1 commercial blocker,
`production_identity_provider`, into a human decision surface. It helps a human
owner compare identity-provider options and decide whether the existing Phase 1
evidence input should be filled.

It does not select or contact an identity provider, fetch JWKS, validate
production tokens, enable production authentication, enforce RBAC, modify
backend behavior, close blockers, launch product, contact customers, or claim
production readiness.

## Target Blocker

```text
blocker_target: production_identity_provider
owner_lane: engineering_security
status: ready_for_human_review_not_execution
production_identity_provider_available: false
blockers_closed_by_packet: false
```

## Evidence Mapping

| Evidence key | Blocker | Builder path | Requirement |
| --- | --- | --- | --- |
{rows}

## Human Review Steps

1. List one to three candidate identity providers in the template.
2. Record the human owner for production identity administration.
3. Review issuer, audience, and JWKS rotation evidence.
4. Record a rollback or disable plan.
5. Only after approval, copy source-backed values into the Phase 1 evidence
   builder input.

## Existing Builder

Use the existing builder after human evidence exists:

```bash
python3 scripts/saee_phase1_identity_tenant_evidence_builder.py --json \\
  --input phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/phase_1_identity_tenant_evidence_input.template.json
```

## Non-Claims

- production_identity_provider_available: false
- oauth_oidc_available: false
- rbac_available: false
- production_auth_ready: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- blockers_closed_by_packet: false
"""


def boundary_body() -> str:
    return """# SAEE Production Identity Provider Decision Packet Boundary Audit

- No identity provider selected by Codex
- No identity provider contacted
- No JWKS fetched
- No production token validation
- No production authentication enabled
- No RBAC enforcement enabled
- No backend modified
- No runtime modified
- No kernel modified
- No API schema modified
- No private core exposed
- No customer contacted
- No product launched
- No production-ready claim
- No blocker closure
"""


def gate_body() -> str:
    return """# SAEE Production Identity Provider Decision Packet Recommendation Gate

answer: conditional

recommend_for_human_review: true
recommend_for_identity_provider_selection: false
recommend_for_identity_provider_contact: false
recommend_for_jwks_fetch: false
recommend_for_token_validation: false
recommend_for_auth_enablement: false
recommend_for_blocker_closure: false
recommend_for_production_launch: false

reason: The packet improves commercial readiness by turning the
`production_identity_provider` blocker into a focused human decision surface.
It does not provide evidence, select a provider, or authorize execution.

boundary:
- production_identity_provider_available: false
- oauth_oidc_available: false
- rbac_available: false
- production_auth_ready: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
- identity_provider_contacted_by_codex: false
- jwks_fetched_by_codex: false
- production_tokens_validated_by_codex: false
- blockers_closed_by_packet: false
"""


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    data = packet()
    write_json(OUTPUT_JSON, data)
    write_json(OUTPUT_TEMPLATE, input_template())
    body = md_body()
    write_text(OUTPUT_MD, body)
    write_text(DOC_PATH, body)
    write_text(OUTPUT_BOUNDARY, boundary_body())
    write_text(GATE_PATH, gate_body())
    print(
        "SAEE_PRODUCTION_IDENTITY_PROVIDER_DECISION_PACKET: PASS "
        f"path={OUTPUT_JSON} status={data['status']} "
        "production_identity_provider_available=false blockers_closed_by_packet=false"
    )


if __name__ == "__main__":
    main()
