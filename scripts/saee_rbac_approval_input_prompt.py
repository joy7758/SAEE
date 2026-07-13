#!/usr/bin/env python3
"""Build a human input prompt for RBAC approval evidence.

This prompt narrows the `rbac` production blocker to the exact human-filled
fields needed before the existing RBAC approval-input validator can pass. It
does not approve RBAC, enforce production RBAC, enable authentication, run the
Phase 1 evidence builder, close blockers, launch product, or claim production
readiness.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
TEMPLATE = EVIDENCE_DIR / "phase_1_identity_tenant_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "rbac_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "rbac_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "rbac_approval_input_prompt.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/RBAC_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RBAC_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "rbac_approval_input.human_filled.local.json"

METADATA_FIELDS = [
    "human_reviewer_name",
    "review_date",
    "evidence_source_notes",
]

RBAC_KEYS = [
    "rbac_policy_approved",
    "role_matrix_reviewed",
    "tenant_role_boundary_reviewed",
    "least_privilege_reviewed",
    "admin_recovery_policy_reviewed",
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
    "production_auth_enabled",
    "production_identity_provider_available",
    "oauth_oidc_available",
    "rbac_available",
    "rbac_approved",
    "rbac_policy_approved_by_codex",
    "rbac_available_by_prompt",
    "rbac_enforced_in_production",
    "production_rbac_enforcement_enabled",
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
            f"SAEE_RBAC_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_RBAC_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def template_rbac_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    notes = template.get("source_notes_by_key", {})
    if not isinstance(review, dict) or not isinstance(notes, dict):
        raise SystemExit("SAEE_RBAC_APPROVAL_INPUT_PROMPT: FAIL template evidence maps missing")
    missing = [key for key in RBAC_KEYS if key not in review or key not in notes]
    if missing:
        raise SystemExit(
            "SAEE_RBAC_APPROVAL_INPUT_PROMPT: FAIL template missing RBAC keys: "
            + ", ".join(missing)
        )
    return list(RBAC_KEYS)


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = template_rbac_keys(template)

    payload: dict[str, Any] = {
        "rbac_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_rbac_approval_input_prompt",
        "prompt_scope": "local_human_rbac_approval_input_prompt_only",
        "status": "hold_human_rbac_approval_input_required",
        "target_blocker_ids": ["rbac"],
        "category": "auth",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_rbac_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "validator_builder_ready": validation.get("builder_ready") is True,
        "builder_ready": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_rbac_evidence_item_count": len(keys),
        "completed_rbac_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "rbac_evidence_keys_to_review": [
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
            "python3 scripts/saee_rbac_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "evidence_builder_command_after_separate_approval": (
            "python3 scripts/saee_phase1_identity_tenant_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make rbac-approval-input-prompt",
        "check_target": "make check-rbac-approval-input-prompt",
        "next_human_action": (
            "Copy the Phase 1 identity/tenant template, fill the three review "
            "metadata fields, set only the five RBAC evidence_review keys after "
            "human approval, add source notes for those keys, then run the RBAC "
            "approval input validator. Stop before evidence builder execution."
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
    evidence_table = render_key_table(payload["rbac_evidence_keys_to_review"])
    content = f"""# SAEE RBAC Approval Input Prompt

rbac_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_ids: rbac
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_rbac_evidence_item_count: {payload['required_rbac_evidence_item_count']}
completed_rbac_evidence_item_count: {payload['completed_rbac_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
rbac_available: false
rbac_available_by_prompt: false
rbac_enforced_in_production: false
production_auth_ready: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the RBAC
approval portion of the Phase 1 identity/tenant evidence input before validator
use.

## Metadata Fields To Fill

{metadata}

## RBAC Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, RBAC enforcement, production
auth enablement, blocker closure, launch, and production-readiness claims require
separate approvals.

## Boundary

This prompt does not approve RBAC, fill evidence, enforce production RBAC,
enable authentication, contact identity providers, fetch JWKS, validate
production tokens, execute the evidence builder, close blockers, launch product,
modify runtime/backend/kernel/API schema, expose private core, or claim
production readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE RBAC Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_rbac_input_prompt: true
recommend_for_rbac_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_rbac_enforcement: false
recommend_for_auth_enablement: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the RBAC evidence
fields in the Phase 1 identity/tenant template. It makes the required metadata,
RBAC review keys, and source notes explicit without approving RBAC or enabling
auth.

## Boundary

- target_blocker_ids: rbac
- builder_ready: false
- ready_for_evidence_builder: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- rbac_available: false
- rbac_available_by_prompt: false
- rbac_enforced_in_production: false
- production_auth_ready: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_RBAC_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print("target_blocker_ids=" + ",".join(payload["target_blocker_ids"]))
    print("metadata_fields=" + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"]))
    print(
        "rbac_evidence_keys="
        + ",".join(item["evidence_key"] for item in payload["rbac_evidence_keys_to_review"])
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print("boundary=human_input_only_no_rbac_approval_no_auth_enablement_no_blocker_closure")


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
