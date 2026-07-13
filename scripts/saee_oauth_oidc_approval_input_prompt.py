#!/usr/bin/env python3
"""Build a human input prompt for OAuth/OIDC approval evidence.

This prompt narrows the `oauth_oidc` production blocker to the exact
human-filled fields needed before the existing OAuth/OIDC approval-input
validator can pass. It does not contact an identity provider, fetch JWKS,
validate production tokens, enable authentication, run the Phase 1 evidence
builder, close blockers, launch product, or claim production readiness.
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

from saee_backend.services.production_auth_evidence import OAUTH_OIDC_KEYS

EVIDENCE_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
TEMPLATE = EVIDENCE_DIR / "phase_1_identity_tenant_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "oauth_oidc_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "oauth_oidc_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "oauth_oidc_approval_input_prompt.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/OAUTH_OIDC_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_OAUTH_OIDC_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "oauth_oidc_approval_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "evidence_source_notes",
]

BOUNDARY_FALSE_FLAGS = [
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "api_schema_modified",
    "private_core_exposed",
    "product_launched",
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "public_sdk_released",
    "external_calls_made",
    "external_model_api_called",
    "external_ai_assistant_tested",
    "task_candidates_executed",
    "development_permission_granted",
    "execution_authorized",
    "evidence_collection_authorized",
    "codex_contacted_identity_provider",
    "codex_fetched_jwks",
    "codex_validated_production_tokens",
    "identity_provider_contacted_by_codex",
    "jwks_fetched_by_codex",
    "production_tokens_validated_by_codex",
    "production_auth_enabled",
    "production_identity_provider_available",
    "oauth_oidc_approved",
    "oauth_oidc_approved_by_prompt",
    "oauth_oidc_available",
    "oauth_oidc_available_by_prompt",
    "oauth_oidc_flow_approved_by_codex",
    "rbac_available",
    "rbac_enforced_in_production",
    "production_auth_ready",
    "phase_1_evidence_builder_run_by_prompt",
    "production_auth_evidence_built_by_prompt",
    "blockers_closed_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_OAUTH_OIDC_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_OAUTH_OIDC_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def template_oauth_oidc_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    notes = template.get("source_notes_by_key", {})
    if not isinstance(review, dict) or not isinstance(notes, dict):
        raise SystemExit(
            "SAEE_OAUTH_OIDC_APPROVAL_INPUT_PROMPT: FAIL template evidence maps missing"
        )
    keys = list(OAUTH_OIDC_KEYS)
    missing = [key for key in keys if key not in review or key not in notes]
    if missing:
        raise SystemExit(
            "SAEE_OAUTH_OIDC_APPROVAL_INPUT_PROMPT: FAIL template missing OAuth/OIDC keys: "
            + ", ".join(missing)
        )
    return keys


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = template_oauth_oidc_keys(template)

    payload: dict[str, Any] = {
        "oauth_oidc_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_oauth_oidc_approval_input_prompt",
        "prompt_scope": "local_human_oauth_oidc_approval_input_prompt_only",
        "status": "hold_human_oauth_oidc_approval_input_required",
        "target_blocker_ids": ["oauth_oidc"],
        "category": "auth",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_oauth_oidc_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "validator_builder_ready": validation.get("builder_ready") is True,
        "builder_ready": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_oauth_oidc_evidence_item_count": len(keys),
        "completed_oauth_oidc_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "oauth_oidc_evidence_keys_to_review": [
            {
                "evidence_key": key,
                "set_evidence_review_to_true_only_after_human_approval": True,
                "human_source_note_required": True,
                "codex_may_fill": False,
            }
            for key in keys
        ],
        "copy_template_command": f"cp {rel(TEMPLATE)} {rel(HUMAN_FILLED_INPUT)}",
        "validator_command": (
            "python3 scripts/saee_oauth_oidc_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "evidence_builder_command_after_separate_approval": (
            "python3 scripts/saee_phase1_identity_tenant_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make oauth-oidc-approval-input-prompt",
        "check_target": "make check-oauth-oidc-approval-input-prompt",
        "next_human_action": (
            "Copy the Phase 1 identity/tenant template, fill the three review "
            "metadata fields, set only the five OAuth/OIDC evidence_review keys "
            "after human approval, add source notes for those keys, then run the "
            "OAuth/OIDC approval input validator. Stop before evidence builder execution."
        ),
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
    }
    for flag in BOUNDARY_FALSE_FLAGS:
        payload[flag] = False
    payload["blockers_closed_by_prompt"] = 0
    return payload


def render_metadata_list(fields: list[dict[str, Any]]) -> str:
    return "\n".join(f"- `{field['field_name']}`" for field in fields)


def render_key_table(keys: list[dict[str, Any]]) -> str:
    rows = [
        "| Evidence Key | Review Flag | Source Note | Codex May Fill |",
        "| --- | --- | --- | --- |",
    ]
    for item in keys:
        key = item["evidence_key"]
        rows.append(f"| `{key}` | set true only after human approval | required | false |")
    return "\n".join(rows)


def write_markdown(payload: dict[str, Any]) -> None:
    metadata = render_metadata_list(payload["metadata_fields_to_fill"])
    evidence_table = render_key_table(payload["oauth_oidc_evidence_keys_to_review"])
    content = f"""# SAEE OAuth/OIDC Approval Input Prompt

oauth_oidc_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_ids: oauth_oidc
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_oauth_oidc_evidence_item_count: {payload['required_oauth_oidc_evidence_item_count']}
completed_oauth_oidc_evidence_item_count: {payload['completed_oauth_oidc_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
oauth_oidc_available: false
oauth_oidc_available_by_prompt: false
production_identity_provider_available: false
production_tokens_validated_by_codex: false
production_auth_ready: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
OAuth/OIDC approval portion of the Phase 1 identity/tenant evidence input before
validator use.

## Metadata Fields To Fill

{metadata}

## OAuth/OIDC Evidence Keys To Review

{evidence_table}

## Copy Template

```bash
{payload['copy_template_command']}
```

## Validate Human-Filled Input

```bash
{payload['validator_command']}
```

## Stop Point

After validation, stop. Evidence-builder execution, identity-provider contact,
JWKS fetch, production token validation, authentication enablement, blocker
closure, launch, and production-readiness claims require separate approvals.

## Boundary

This prompt does not approve OAuth/OIDC, fill evidence, contact identity
providers, fetch JWKS, validate production tokens, enable authentication,
execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, or claim production
readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE OAuth/OIDC Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_oauth_oidc_input_prompt: true
recommend_for_oauth_oidc_approval_by_codex: false
recommend_for_identity_provider_contact: false
recommend_for_jwks_fetch: false
recommend_for_token_validation: false
recommend_for_evidence_builder_execution: false
recommend_for_auth_enablement: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the OAuth/OIDC
evidence fields in the Phase 1 identity/tenant template. It makes the required
metadata, OAuth/OIDC review keys, and source notes explicit without approving
OAuth/OIDC, contacting an identity provider, fetching JWKS, validating
production tokens, or enabling auth.

## Boundary

- target_blocker_ids: oauth_oidc
- builder_ready: false
- ready_for_evidence_builder: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- oauth_oidc_available: false
- oauth_oidc_available_by_prompt: false
- production_identity_provider_available: false
- production_tokens_validated_by_codex: false
- production_auth_ready: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_OAUTH_OIDC_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print("target_blocker_ids=" + ",".join(payload["target_blocker_ids"]))
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "oauth_oidc_evidence_keys="
        + ",".join(
            item["evidence_key"] for item in payload["oauth_oidc_evidence_keys_to_review"]
        )
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(
        "boundary=human_input_only_no_idp_contact_no_jwks_fetch_"
        "no_token_validation_no_auth_enablement_no_blocker_closure"
    )


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
