#!/usr/bin/env python3
"""Smoke test for the production restore policy approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_production_restore_policy_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/data_operations_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "production_restore_policy_approval_input_prompt.html"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(
        "SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message
    )


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

    payload = read_json(OUTPUT_JSON)
    expected = {
        "production_restore_policy_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_production_restore_policy_approval_input_prompt",
        "prompt_scope": "local_human_restore_policy_approval_input_prompt_only",
        "status": "hold_human_restore_policy_approval_input_required",
        "target_blocker_id": "production_restore_policy",
        "category": "data_ops",
        "validation_status": "pass",
        "builder_ready": False,
        "policy_draft_available": True,
        "production_restore_policy_available": False,
        "production_restore_policy_approved": False,
        "local_static_production_restore_policy_approval_input_prompt_html": True,
        "browser_readable_production_restore_policy_approval_input_prompt": True,
        "plain_language_production_restore_policy_approval_input_prompt_v0_2": True,
        "production_restore_policy_human_review_step_count": 4,
        "required_metadata_field_count": 7,
        "completed_metadata_field_count": 0,
        "required_policy_evidence_item_count": 6,
        "completed_policy_evidence_item_count": 0,
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
        "policy_approved_by_codex": False,
        "restore_policy_published_by_codex": False,
        "live_restore_authorized_by_codex": False,
        "live_restore_performed": False,
        "restore_to_live_path_enabled": False,
        "production_data_path_modified": False,
        "credentials_restored": False,
        "private_core_restored": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    metadata = payload.get("metadata_fields_to_fill")
    require(isinstance(metadata, list), "metadata_fields_to_fill must be list")
    require(len(metadata) == 7, "metadata_fields_to_fill must have seven fields")
    require(all(item.get("human_must_provide") is True for item in metadata), "metadata requires human input")
    require(all(item.get("codex_may_fill") is False for item in metadata), "metadata codex_may_fill false")

    keys = payload.get("policy_evidence_keys_to_review")
    require(isinstance(keys, list), "policy_evidence_keys_to_review must be list")
    require(len(keys) == 6, "policy_evidence_keys_to_review must have six keys")
    require(all(item.get("codex_may_fill") is False for item in keys), "policy keys codex_may_fill false")
    require(
        all(item.get("human_source_note_required") is True for item in keys),
        "policy source notes required",
    )
    require(
        all(item.get("policy_evidence_slot_required") is True for item in keys),
        "policy evidence slots required",
    )

    require("production_restore_policy_approval_input.template.json" in payload.get("copy_template_command", ""), "copy command missing template")
    require("production_restore_policy_approval_input.human_filled.local.json" in payload.get("copy_template_command", ""), "copy command missing human input")
    require("saee_production_restore_policy_approval_input_validator.py" in payload.get("validator_command", ""), "validator command missing")
    require("production_restore_policy_approval_input_prompt.html" in payload.get("source_production_restore_policy_approval_input_prompt_html", ""), "HTML source path missing")
    require("生产恢复策略还没有人工批准" in payload.get("plain_language_status_label", ""), "plain language status missing")
    require("确认前不要运行恢复" in payload.get("plain_language_next_action", ""), "plain language next action missing")
    require("填完并验证输入后停止" in payload.get("plain_language_stop_point", ""), "plain language stop point missing")

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "production_restore_policy_approval_input_prompt_v0_1: true",
            "status: hold_human_restore_policy_approval_input_required",
            "target_blocker_id: production_restore_policy",
            "required_metadata_field_count: 7",
            "required_policy_evidence_item_count: 6",
            "builder_ready: false",
            "production_restore_policy_available: false",
            "production_restore_policy_approved: false",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<title>SAEE 生产恢复策略人工审批入口</title>",
        "先确认怎么恢复，再谈正式商用。",
        "等待人工填写",
        "必须由人填写的字段",
        "必须由人审查的恢复策略证据",
        "人工操作顺序",
        "到这里必须停下",
        "production_restore_policy_available",
        "production_restore_policy_approved",
        "live_restore_performed",
        "production_data_path_modified",
        "customer_contacted",
        "production_ready",
        "private_core_exposed",
        "blockers_closed_by_prompt",
    ]:
        require(token in html, f"html missing {token}")
    for token in [
        "answer: recommend",
        "recommend_for_human_restore_policy_input_prompt: true",
        "recommend_for_policy_approval_by_codex: false",
        "recommend_for_evidence_builder_execution: false",
        "recommend_for_restore_execution: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]:
        require(token in gate, f"gate missing {token}")

    forbidden = [
        "production_ready: true",
        '"production_ready": true',
        "product_launched: true",
        '"product_launched": true',
        "customer_validated: true",
        '"customer_validated": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "production_restore_policy_available: true",
        '"production_restore_policy_available": true',
        "production_restore_policy_approved: true",
        '"production_restore_policy_approved": true',
        "builder_ready: true",
        '"builder_ready": true',
        "live_restore_performed: true",
        '"live_restore_performed": true',
        "recommend_for_policy_approval_by_codex: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_restore_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    html_forbidden = [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "mailto:",
        "saee_v1_0",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]
    found_html = [token for token in html_forbidden if token in html]
    require(not found_html, "HTML forbidden tokens found: " + ", ".join(found_html))

    combined = "\n".join([json.dumps(payload), markdown, html, top_doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_PRODUCTION_RESTORE_POLICY_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
