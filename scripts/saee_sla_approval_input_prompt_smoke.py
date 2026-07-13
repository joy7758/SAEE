#!/usr/bin/env python3
"""Smoke test for the SLA approval input prompt."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_sla_approval_input_prompt.py"
EVIDENCE_DIR = ROOT / "phase_b_product/commercial_readiness/support_evidence"
OUTPUT_JSON = EVIDENCE_DIR / "sla_approval_input_prompt.local.json"
OUTPUT_MD = EVIDENCE_DIR / "sla_approval_input_prompt.md"
OUTPUT_HTML = EVIDENCE_DIR / "sla_approval_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/SLA_APPROVAL_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_SLA_APPROVAL_INPUT_PROMPT_RECOMMENDATION_GATE.md"


def fail(message: str) -> None:
    raise SystemExit("SAEE_SLA_APPROVAL_INPUT_PROMPT_SMOKE: FAIL " + message)


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
        "sla_approval_input_prompt_v0_1": True,
        "prompt_type": "saee_sla_approval_input_prompt",
        "prompt_scope": "local_human_sla_input_prompt_only",
        "status": "hold_human_sla_input_required",
        "target_blocker_id": "sla",
        "category": "support",
        "source_sla_approval_input_prompt_html": "phase_b_product/commercial_readiness/support_evidence/sla_approval_input_prompt.html",
        "local_static_sla_approval_input_prompt_html": True,
        "browser_readable_sla_approval_input_prompt": True,
        "plain_language_sla_approval_input_prompt_v0_2": True,
        "validation_status": "hold",
        "builder_ready": False,
        "ready_for_evidence_builder": False,
        "sla_available": False,
        "sla_approved": False,
        "sla_published": False,
        "legal_review_completed": False,
        "support_hours_published": False,
        "response_targets_published": False,
        "support_operations_started": False,
        "required_metadata_field_count": 5,
        "completed_metadata_field_count": 0,
        "required_sla_evidence_item_count": 6,
        "completed_sla_evidence_item_count": 0,
        "sla_human_review_step_count": 4,
        "plain_language_status_label": "SLA 还没有批准，也没有发布，不能对外承诺服务响应。",
        "human_review_required": True,
        "separate_validator_required": True,
        "separate_evidence_builder_request_required": True,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "private_core_exposed": False,
        "product_launched": False,
        "production_ready": False,
        "customer_validated": False,
        "customer_contacted": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "execution_authorized": False,
        "evidence_collection_authorized": False,
        "sla_approved_by_codex": False,
        "sla_published_by_codex": False,
        "legal_review_completed_by_codex": False,
        "support_hours_published_by_codex": False,
        "response_targets_published_by_codex": False,
        "production_sla_claim_published": False,
        "production_support_claim_published": False,
        "production_support_available": False,
        "support_contact_available": False,
        "customer_support_available": False,
        "on_call_rotation_available": False,
        "blockers_closed_by_prompt": 0,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")

    metadata = payload.get("metadata_fields_to_fill")
    require(isinstance(metadata, list), "metadata_fields_to_fill must be list")
    require(len(metadata) == 5, "metadata_fields_to_fill must have five fields")
    require(
        all(item.get("human_must_provide") is True for item in metadata),
        "metadata requires human input",
    )
    require(
        all(item.get("codex_may_fill") is False for item in metadata),
        "metadata codex_may_fill false",
    )

    keys = payload.get("sla_evidence_keys_to_review")
    require(isinstance(keys, list), "sla_evidence_keys_to_review must be list")
    require(len(keys) == 6, "sla_evidence_keys_to_review must have six keys")
    for flag in [
        "set_evidence_review_to_true_only_after_human_approval",
        "human_source_note_required",
        "sla_evidence_slot_required",
        "owner_named_required",
        "legal_or_commercial_review_required",
        "reviewed_by_human_required",
    ]:
        require(all(item.get(flag) is True for item in keys), f"{flag} required")
    require(all(item.get("codex_may_fill") is False for item in keys), "keys codex false")

    require(
        "sla_evidence_input.template.json" in payload.get("copy_template_command", ""),
        "copy command missing template",
    )
    require(
        "sla_evidence_input.human_filled.local.json"
        in payload.get("copy_template_command", ""),
        "copy command missing human input",
    )
    require(
        "saee_sla_approval_input_validator.py" in payload.get("validator_command", ""),
        "validator command missing",
    )

    markdown = OUTPUT_MD.read_text(encoding="utf-8")
    html = OUTPUT_HTML.read_text(encoding="utf-8")
    top_doc = TOP_DOC.read_text(encoding="utf-8")
    gate = GATE.read_text(encoding="utf-8")
    for text, name in [(markdown, "markdown"), (top_doc, "top_doc")]:
        for token in [
            "sla_approval_input_prompt_v0_1: true",
            "status: hold_human_sla_input_required",
            "target_blocker_id: sla",
            "required_metadata_field_count: 5",
            "required_sla_evidence_item_count: 6",
            "builder_ready: false",
            "ready_for_evidence_builder: false",
            "sla_available: false",
            "sla_approved: false",
            "sla_published: false",
            "legal_review_completed: false",
            "support_hours_published: false",
            "response_targets_published: false",
            "support_operations_started: false",
            "source_sla_approval_input_prompt_html: phase_b_product/commercial_readiness/support_evidence/sla_approval_input_prompt.html",
            "local_static_sla_approval_input_prompt_html: true",
            "browser_readable_sla_approval_input_prompt: true",
            "plain_language_sla_approval_input_prompt_v0_2: true",
            "sla_human_review_step_count: 4",
            "plain_language_status_label: SLA 还没有批准，也没有发布，不能对外承诺服务响应。",
            "blockers_closed_by_prompt: 0",
            "production_ready: false",
        ]:
            require(token in text, f"{name} missing {token}")
    for token in [
        "<!doctype html>",
        "<html lang=\"zh-CN\">",
        "SAEE SLA 人工审批入口",
        "先把服务承诺审清楚，再谈对外 SLA。",
        "SLA 还没有批准，也没有发布，不能对外承诺服务响应。",
        "Codex 可代执行：<code>false</code>",
        "sla_available: <code>false</code>",
        "sla_approved: <code>false</code>",
        "sla_published: <code>false</code>",
        "support_operations_started: <code>false</code>",
        "customer_contacted: <code>false</code>",
        "production_ready: <code>false</code>",
        "private_core_exposed: <code>false</code>",
        "不批准 SLA",
        "不声明正式商用",
    ]:
        require(token in html, f"html missing {token}")
    for token in [
        "<script",
        "fetch(",
        "XMLHttpRequest",
        "mailto:",
        "saee_v1_0",
        "selection_engine",
        "mutation_engine",
        "lineage_engine",
        "fitness_engine",
    ]:
        require(token not in html, f"html contains forbidden token {token}")
    for token in [
        "answer: recommend",
        "recommend_for_human_sla_input_prompt: true",
        "recommend_for_sla_approval_by_codex: false",
        "recommend_for_sla_publication: false",
        "recommend_for_legal_review_completion: false",
        "recommend_for_support_hours_publication: false",
        "recommend_for_response_targets_publication: false",
        "recommend_for_support_operations_start: false",
        "recommend_for_evidence_builder_execution: false",
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
        "sla_available: true",
        '"sla_available": true',
        "sla_approved: true",
        '"sla_approved": true',
        "sla_published: true",
        '"sla_published": true',
        "legal_review_completed: true",
        '"legal_review_completed": true',
        "support_hours_published: true",
        '"support_hours_published": true',
        "response_targets_published: true",
        '"response_targets_published": true',
        "support_operations_started: true",
        '"support_operations_started": true',
        "production_support_available: true",
        '"production_support_available": true',
        "builder_ready: true",
        '"builder_ready": true',
        "ready_for_evidence_builder: true",
        '"ready_for_evidence_builder": true',
        "recommend_for_sla_approval_by_codex: true",
        "recommend_for_sla_publication: true",
        "recommend_for_legal_review_completion: true",
        "recommend_for_support_hours_publication: true",
        "recommend_for_response_targets_publication: true",
        "recommend_for_support_operations_start: true",
        "recommend_for_evidence_builder_execution: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    combined = "\n".join([json.dumps(payload), markdown, top_doc, gate])
    found = [token for token in forbidden if token in combined]
    require(not found, "forbidden claims found: " + ", ".join(found))

    print("SAEE_SLA_APPROVAL_INPUT_PROMPT_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
