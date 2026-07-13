#!/usr/bin/env python3
"""Smoke check for the SAEE RBAC approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_rbac_approval_input_prompt.py"
EVIDENCE_DIR = (
    ROOT
    / "phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder"
)
OUTPUT_JSON = EVIDENCE_DIR / "rbac_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "rbac_approval_input_prompt.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/RBAC_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_RBAC_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_RBAC_APPROVAL_INPUT_PROMPT_SMOKE: FAIL: " + message)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"invalid JSON {path}: {exc}")
    require(isinstance(value, dict), f"{path} must be object")
    return value


def main() -> int:
    result = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        fail("runner failed")

    prompt = read_json(OUTPUT_JSON)
    expected = {
        "rbac_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_rbac_approval_input_prompt",
        "prompt_scope": "local_human_rbac_approval_input_prompt_only",
        "status": "hold_human_rbac_approval_input_required",
        "validation_status": "hold",
        "validator_builder_ready": False,
        "builder_ready": False,
        "required_metadata_field_count": 3,
        "completed_metadata_field_count": 0,
        "required_rbac_evidence_item_count": 5,
        "completed_rbac_evidence_item_count": 0,
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "ready_for_evidence_builder": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "public_sdk_released": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "codex_contacted_identity_provider": False,
        "codex_fetched_jwks": False,
        "codex_validated_production_tokens": False,
        "production_auth_enabled": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "rbac_available": False,
        "rbac_approved": False,
        "rbac_policy_approved_by_codex": False,
        "rbac_available_by_prompt": False,
        "rbac_enforced_in_production": False,
        "production_rbac_enforcement_enabled": False,
        "production_auth_ready": False,
        "phase_1_evidence_builder_run_by_prompt": False,
        "production_auth_evidence_built_by_prompt": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(prompt.get(key) == value, f"{key} must be {value}")

    require(prompt.get("target_blocker_ids") == ["rbac"], "target blocker changed")

    metadata = prompt.get("metadata_fields_to_fill")
    require(isinstance(metadata, list) and len(metadata) == 3, "metadata count")
    for item in metadata:
        require(item.get("human_must_provide") is True, "metadata must require human")
        require(item.get("codex_may_fill") is False, "metadata codex_may_fill false")

    keys = prompt.get("rbac_evidence_keys_to_review")
    require(isinstance(keys, list) and len(keys) == 5, "rbac key count")
    for item in keys:
        require(item.get("codex_may_fill") is False, "key codex_may_fill false")
        require(item.get("human_source_note_required") is True, "source note required")
        require(
            item.get("set_evidence_review_to_true_only_after_human_approval") is True,
            "human approval required",
        )

    command_text = "\n".join(
        [
            prompt.get("copy_template_command", ""),
            prompt.get("validator_command", ""),
            prompt.get("evidence_builder_command_after_separate_approval", ""),
        ]
    )
    for token in [
        "phase_1_identity_tenant_evidence_input.template.json",
        "rbac_approval_input.human_filled.local.json",
        "saee_rbac_approval_input_validator.py",
        "saee_phase1_identity_tenant_evidence_builder.py",
    ]:
        require(token in command_text, "missing command token: " + token)

    docs = "\n".join(path.read_text(encoding="utf-8") for path in [OUTPUT_MD, TOP_DOC, GATE])
    for token in [
        "rbac_approval_input_prompt_v0_1: true",
        "status: hold_human_rbac_approval_input_required",
        "target_blocker_ids: rbac",
        "required_metadata_field_count: 3",
        "required_rbac_evidence_item_count: 5",
        "builder_ready: false",
        "ready_for_evidence_builder: false",
        "rbac_available: false",
        "rbac_available_by_prompt: false",
        "rbac_enforced_in_production: false",
        "production_auth_ready: false",
        "blockers_closed_by_prompt: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_rbac_input_prompt: true",
        "recommend_for_rbac_approval_by_codex: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_rbac_enforcement: false",
        "recommend_for_auth_enablement: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]:
        require(token in docs, "missing doc token: " + token)

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "builder_ready: true",
        '"builder_ready": true',
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "rbac_available: true",
        '"rbac_available": true',
        "rbac_available_by_prompt: true",
        '"rbac_available_by_prompt": true',
        "rbac_enforced_in_production: true",
        '"rbac_enforced_in_production": true',
        "production_auth_ready: true",
        '"production_auth_ready": true',
        "recommend_for_rbac_approval_by_codex: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_rbac_enforcement: true",
        "recommend_for_auth_enablement: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    combined = "\n".join([json.dumps(prompt), docs])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden true claim present: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    for path in [
        "/phase_b_product/commercial_readiness/RBAC_APPROVAL_INPUT_PROMPT_V0_1.md",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_prompt.local.json",
        "/phase_b_product/commercial_readiness/phase_1_identity_tenant_evidence_builder/rbac_approval_input_prompt.md",
        "/docs/strategy/SAEE_RBAC_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md",
        "/scripts/saee_rbac_approval_input_prompt.py",
        "/scripts/saee_rbac_approval_input_prompt_smoke.py",
    ]:
        require(path in llms, f"llms.txt missing {path}")

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("rbac_approval_input_prompt_v0_1", {})
    for key, value in {
        "status": "hold_human_rbac_approval_input_required",
        "prompt_type": "saee_rbac_approval_input_prompt",
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "blockers_closed_by_prompt": 0,
        "rbac_available": False,
        "rbac_available_by_prompt": False,
        "rbac_enforced_in_production": False,
        "production_auth_ready": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "external_calls_made": False,
    }.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")
    require(entry.get("target_blocker_ids") == ["rbac"], "agent-index target blocker")

    print("SAEE_RBAC_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
