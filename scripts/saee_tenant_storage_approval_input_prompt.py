#!/usr/bin/env python3
"""Build a human input prompt for tenant storage approval evidence.

This prompt narrows the `tenant_storage_isolation` production blocker to the
exact human-filled fields needed before the existing tenant storage
approval-input validator can pass. It does not implement production
multi-tenancy, modify storage behavior, run migrations, process customer data,
run the Phase 1 evidence builder, close blockers, launch product, or claim
production readiness.
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

from saee_backend.services.production_tenant_storage_evidence import (
    TENANT_ISOLATION_TEST_KEYS,
    TENANT_OPERATIONS_KEYS,
    TENANT_SECURITY_PRIVACY_KEYS,
    TENANT_STORAGE_MODEL_KEYS,
)

EVIDENCE_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
TEMPLATE = EVIDENCE_DIR / "phase_1_identity_tenant_evidence_input.template.json"
VALIDATION = EVIDENCE_DIR / "tenant_storage_approval_input_validation.local.json"
OUTPUT_JSON = EVIDENCE_DIR / "tenant_storage_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "tenant_storage_approval_input_prompt.md"
TOP_DOC = (
    ROOT / "phase_b_product/commercial_readiness/TENANT_STORAGE_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_TENANT_STORAGE_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)
HUMAN_FILLED_INPUT = EVIDENCE_DIR / "tenant_storage_approval_input.human_filled.local.json"

TARGET_EVIDENCE_KEYS = (
    TENANT_STORAGE_MODEL_KEYS
    + TENANT_ISOLATION_TEST_KEYS
    + TENANT_OPERATIONS_KEYS
    + TENANT_SECURITY_PRIVACY_KEYS
)
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
    "tenant_storage_approved",
    "tenant_storage_approved_by_prompt",
    "tenant_storage_available",
    "tenant_storage_available_by_prompt",
    "tenant_storage_isolated",
    "production_tenant_storage_isolated",
    "production_tenant_storage_enabled",
    "multi_tenant_production_ready",
    "tenant_authorization_enabled",
    "customer_data_processed",
    "customer_data_processing_started",
    "production_database_modified",
    "storage_behavior_modified",
    "migration_executed",
    "storage_migration_executed",
    "live_customer_data_migrated",
    "production_tenant_storage_evidence_built_by_prompt",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_TENANT_STORAGE_APPROVAL_INPUT_PROMPT: FAIL {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(
            f"SAEE_TENANT_STORAGE_APPROVAL_INPUT_PROMPT: FAIL {rel(path)} must be object"
        )
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def template_tenant_storage_keys(template: dict[str, Any]) -> list[str]:
    review = template.get("evidence_review", {})
    notes = template.get("source_notes_by_key", {})
    if not isinstance(review, dict) or not isinstance(notes, dict):
        raise SystemExit(
            "SAEE_TENANT_STORAGE_APPROVAL_INPUT_PROMPT: FAIL template evidence maps missing"
        )
    keys = list(TARGET_EVIDENCE_KEYS)
    missing = [key for key in keys if key not in review or key not in notes]
    if missing:
        raise SystemExit(
            "SAEE_TENANT_STORAGE_APPROVAL_INPUT_PROMPT: FAIL template missing tenant storage keys: "
            + ", ".join(missing)
        )
    return keys


def build_payload() -> dict[str, Any]:
    template = read_json(TEMPLATE)
    validation = read_json(VALIDATION)
    keys = template_tenant_storage_keys(template)

    payload: dict[str, Any] = {
        "tenant_storage_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_tenant_storage_approval_input_prompt",
        "prompt_scope": "local_human_tenant_storage_approval_input_prompt_only",
        "status": "hold_human_tenant_storage_approval_input_required",
        "target_blocker_ids": ["tenant_storage_isolation"],
        "category": "tenant",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_tenant_storage_approval_input_prompt.py",
        "source_template": rel(TEMPLATE),
        "source_validation": rel(VALIDATION),
        "human_filled_input_path": rel(HUMAN_FILLED_INPUT),
        "validation_status": validation.get("validation_status", "hold"),
        "validator_builder_ready": validation.get("builder_ready") is True,
        "builder_ready": False,
        "required_metadata_field_count": len(METADATA_FIELDS),
        "completed_metadata_field_count": 0,
        "required_tenant_storage_evidence_item_count": len(keys),
        "completed_tenant_storage_evidence_item_count": 0,
        "metadata_fields_to_fill": [
            {"field_name": field, "human_must_provide": True, "codex_may_fill": False}
            for field in METADATA_FIELDS
        ],
        "tenant_storage_evidence_keys_to_review": [
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
            "python3 scripts/saee_tenant_storage_approval_input_validator.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "evidence_builder_command_after_separate_approval": (
            "python3 scripts/saee_phase1_identity_tenant_evidence_builder.py "
            f"--input {rel(HUMAN_FILLED_INPUT)}"
        ),
        "make_target": "make tenant-storage-approval-input-prompt",
        "check_target": "make check-tenant-storage-approval-input-prompt",
        "next_human_action": (
            "Copy the Phase 1 identity/tenant template, fill the three review "
            "metadata fields, set only the eighteen tenant storage evidence_review "
            "keys after human approval, add source notes for those keys, then run "
            "the tenant storage approval input validator. Stop before evidence "
            "builder execution, storage behavior changes, migrations, or customer "
            "data processing."
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
    evidence_table = render_key_table(payload["tenant_storage_evidence_keys_to_review"])
    content = f"""# SAEE Tenant Storage Approval Input Prompt

tenant_storage_approval_input_prompt_v0_1: true
status: {payload['status']}
target_blocker_ids: tenant_storage_isolation
required_metadata_field_count: {payload['required_metadata_field_count']}
completed_metadata_field_count: {payload['completed_metadata_field_count']}
required_tenant_storage_evidence_item_count: {payload['required_tenant_storage_evidence_item_count']}
completed_tenant_storage_evidence_item_count: {payload['completed_tenant_storage_evidence_item_count']}
builder_ready: false
ready_for_evidence_builder: false
tenant_storage_approved: false
tenant_storage_approved_by_prompt: false
tenant_storage_available: false
tenant_storage_available_by_prompt: false
tenant_storage_isolated: false
production_tenant_storage_isolated: false
production_tenant_storage_enabled: false
multi_tenant_production_ready: false
tenant_authorization_enabled: false
customer_data_processed: false
customer_data_processing_started: false
production_database_modified: false
storage_behavior_modified: false
migration_executed: false
storage_migration_executed: false
live_customer_data_migrated: false
production_tenant_storage_evidence_built_by_prompt: false
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false
private_core_exposed: false

## Purpose

This prompt gives a human reviewer the shortest safe path for filling the
tenant storage approval portion of the Phase 1 identity/tenant evidence input
before validator use.

## Metadata Fields To Fill

{metadata}

## Tenant Storage Evidence Keys To Review

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

After validation, stop. Evidence-builder execution, storage behavior change,
storage migration, customer data processing, production tenant storage
enablement, blocker closure, launch, and production-readiness claims require
separate approvals.

## Boundary

This prompt does not approve tenant storage isolation, fill evidence, modify
storage behavior, run migrations, process customer data, enable tenant storage,
execute the evidence builder, close blockers, launch product, modify
runtime/backend/kernel/API schema, expose private core, or claim production
readiness.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        f"""# SAEE Tenant Storage Approval Input Prompt Recommendation Gate

answer: recommend
recommend_for_human_tenant_storage_input_prompt: true
recommend_for_tenant_storage_approval_by_codex: false
recommend_for_evidence_builder_execution: false
recommend_for_storage_behavior_change: false
recommend_for_storage_migration: false
recommend_for_customer_data_processing: false
recommend_for_tenant_storage_enablement: false
recommend_for_tenant_storage_isolation_claim: false
recommend_for_blocker_closure: false
recommend_for_production: false

## Reason

The prompt is recommendable as a local human-input guide for the tenant storage
evidence fields in the Phase 1 identity/tenant template. It makes the required
metadata, tenant storage review keys, and source notes explicit without
approving tenant storage isolation, changing storage behavior, running
migrations, processing customer data, or enabling production multi-tenancy.

## Boundary

- target_blocker_ids: tenant_storage_isolation
- builder_ready: false
- ready_for_evidence_builder: false
- evidence_collection_authorized: false
- execution_authorized: false
- blockers_closed_by_prompt: 0
- tenant_storage_approved: false
- tenant_storage_approved_by_prompt: false
- tenant_storage_available: false
- tenant_storage_available_by_prompt: false
- tenant_storage_isolated: false
- production_tenant_storage_isolated: false
- production_tenant_storage_enabled: false
- multi_tenant_production_ready: false
- tenant_authorization_enabled: false
- customer_data_processed: false
- storage_behavior_modified: false
- migration_executed: false
- production_ready: false
- customer_validated: false
- product_launched: false
- private_core_exposed: false
""",
        encoding="utf-8",
    )


def print_prompt(payload: dict[str, Any]) -> None:
    print("SAEE_TENANT_STORAGE_APPROVAL_INPUT_PROMPT: READY")
    print(f"status={payload['status']}")
    print("target_blocker_ids=" + ",".join(payload["target_blocker_ids"]))
    print(
        "metadata_fields="
        + ",".join(item["field_name"] for item in payload["metadata_fields_to_fill"])
    )
    print(
        "tenant_storage_evidence_keys="
        + ",".join(
            item["evidence_key"]
            for item in payload["tenant_storage_evidence_keys_to_review"]
        )
    )
    print("copy_template_command:")
    print(payload["copy_template_command"])
    print("validator_command:")
    print(payload["validator_command"])
    print(
        "boundary=human_input_only_no_storage_behavior_change_no_migration_"
        "no_customer_data_processing_no_tenant_storage_enablement_no_blocker_closure"
    )


def main() -> int:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    print_prompt(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
