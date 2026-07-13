#!/usr/bin/env python3
"""Build terminal and browser prompts for the current commercial human-input step."""

from __future__ import annotations

import json
import html
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_action_summary"
OUTPUT_JSON = OUTPUT_DIR / "commercial_next_human_input_prompt.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_next_human_input_prompt.md"
OUTPUT_HTML = OUTPUT_DIR / "commercial_next_human_input_prompt.html"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT_RECOMMENDATION_GATE.md"

SUMMARY_JSON = OUTPUT_DIR / "commercial_next_action_summary.local.json"
QUICK_FILL_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_packet.csv"
)
REVIEW_BATCH_TEMPLATE_CSV = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
)
FILL_CARD_MD = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_human_fill_card.md"
)
FILL_CARD_HTML = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint/"
    "commercial_review_batch_human_fill_card.html"
)

FALSE_FLAGS = [
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
    "owner_contacted_by_codex",
    "owner_assigned_by_codex",
    "blockers_closed_by_prompt",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT: FAIL {rel(path)}: {exc}") from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT: FAIL {rel(path)} must be object")
    return data


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_payload() -> dict[str, Any]:
    summary = read_json(SUMMARY_JSON)
    action = summary["next_actions"][0]
    payload: dict[str, Any] = {
        "commercial_next_human_input_prompt_v0_1": True,
        "prompt_type": "saee_commercial_next_human_input_prompt",
        "prompt_scope": (
            "local_terminal_validator_missing_input_completion_prompt_with_related_sequence_context"
            if summary.get("status")
            == "hold_validator_input_evidence_completion_required"
            else "local_terminal_validator_outputs_review_prompt_with_related_sequence_context"
            if summary.get("status") == "hold_validator_outputs_review_required"
            else "local_terminal_validator_approval_review_prompt_with_related_sequence_context"
            if summary.get("status") == "hold_validator_approval_required"
            else "local_terminal_evidence_builder_request_prompt_with_related_sequence_context"
            if summary.get("status") == "ready_for_separate_evidence_builder_request"
            else "local_terminal_template_transfer_applier_execution_prompt_with_related_sequence_context"
        ),
        "status": summary.get(
            "status", "ready_for_template_transfer_execution"
        ),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_next_human_input_prompt.py",
        "source_next_action_summary": rel(SUMMARY_JSON),
        "source_quick_fill_csv": rel(QUICK_FILL_CSV),
        "source_review_batch_template_csv": rel(REVIEW_BATCH_TEMPLATE_CSV),
        "source_review_batch_human_fill_card": rel(FILL_CARD_MD),
        "source_review_batch_human_fill_card_html": rel(FILL_CARD_HTML),
        "local_static_next_action_html": True,
        "next_action_html": rel(OUTPUT_HTML),
        "source_related_human_sequence_entrypoint": summary.get(
            "related_human_sequence_entrypoint"
        ),
        "action_id": action.get("action_id", "NEXT-RBT-001"),
        "sequence_step_id": action.get("sequence_step_id", "AHI-001"),
        "first_blocker_id": action.get(
            "blocker_id", "commercial_sprint_review_batch_template"
        ),
        "category": action.get(
            "category", "commercial_sprint_review_batch_template_human_input"
        ),
        "parallel_human_input_lane_count": int(summary.get("parallel_human_input_lane_count", 1)),
        "primary_human_input_lane": summary.get(
            "primary_human_input_lane", "commercial_sprint_quick_fill"
        ),
        "related_human_sequence_lane": summary.get("related_human_sequence_lane"),
        "related_human_sequence_step_id": summary.get("related_human_sequence_step_id"),
        "related_human_sequence_blocker_id": summary.get(
            "related_human_sequence_blocker_id"
        ),
        "related_human_sequence_status": summary.get("related_human_sequence_status"),
        "related_human_sequence_command_template_available": summary.get(
            "related_human_sequence_command_template_available"
        )
        is True,
        "related_human_sequence_missing_human_field_count": int(
            summary.get("related_human_sequence_missing_human_field_count", 0)
        ),
        "related_human_sequence_step": summary.get("related_human_sequence_step", {}),
        "commercial_status": summary.get("commercial_status", "hold"),
        "production_launch_status": summary.get("production_launch_status", "hold"),
        "production_blocker_count": int(summary.get("production_blocker_count", 24)),
        "preferred_human_input_path": summary.get(
            "preferred_human_input_path", "review_batch_10_row_template"
        ),
        "preferred_batch_size": int(summary.get("preferred_batch_size", 10)),
        "preferred_template_row_count": int(
            summary.get("preferred_template_row_count", 10)
        ),
        "preferred_template_value_present_row_count": int(
            summary.get("preferred_template_value_present_row_count", 0)
        ),
        "preferred_template_missing_value_row_count": int(
            summary.get("preferred_template_missing_value_row_count", 10)
        ),
        "ready_for_preferred_template_human_fill": (
            summary.get("ready_for_preferred_template_human_fill") is True
        ),
        "full_quick_fill_missing_value_row_count": int(
            summary.get("full_quick_fill_missing_value_row_count", 64)
        ),
        "quick_fill_row_count": int(summary.get("quick_fill_row_count", 64)),
        "selected_blocker_count": int(summary.get("selected_blocker_count", 5)),
        "completed_value_row_count": int(summary.get("completed_value_row_count", 0)),
        "missing_value_row_count": int(summary.get("missing_value_row_count", 64)),
        "required_human_field_count": len(action.get("required_human_fields", [])),
        "required_human_fields": action.get("required_human_fields", []),
        "ready_for_safety_preflight": summary.get("ready_for_safety_preflight") is True,
        "ready_for_workbook_import": summary.get("ready_for_workbook_import") is True,
        "ready_for_workbook_import_approval": (
            summary.get("ready_for_workbook_import_approval") is True
        ),
        "requires_human_input": True,
        "requires_review_batch_template_e2e_dry_run": False,
        "requires_separate_local_output_apply_request": False,
        "requires_full_quick_fill_source_path_review": False,
        "requires_safety_preflight": False,
        "requires_quick_fill_validator": False,
        "requires_import_dry_run": False,
        "requires_workbook_import_approval_review": False,
        "requires_separate_workbook_import_execution_request": False,
        "requires_separate_template_transfer_execution_request": (
            summary.get("separate_template_transfer_execution_request_required") is True
        ),
        "ready_for_template_transfer_request": summary.get("ready_for_template_transfer_request")
        is True,
        "ready_for_template_transfer_execution": summary.get("ready_for_template_transfer_execution")
        is True,
        "ready_for_separate_human_template_transfer_execution_request": summary.get(
            "ready_for_separate_human_template_transfer_execution_request"
        )
        is True,
        "human_template_transfer_execution_request_recorded": summary.get(
            "human_template_transfer_execution_request_recorded"
        )
        is True,
        "human_template_transfer_execution_authorized": summary.get(
            "human_template_transfer_execution_authorized"
        )
        is True,
        "source_workbook_import_performed": summary.get("source_workbook_import_performed")
        is True,
        "source_workbook_written": summary.get("source_workbook_written") is True,
        "template_transfer_authorized": summary.get("template_transfer_authorized") is True,
        "template_transfer_performed": summary.get("template_transfer_performed") is True,
        "template_transfer_values_transferred": summary.get("template_transfer_values_transferred") is True,
        "template_transfer_human_filled_templates_written": summary.get(
            "template_transfer_human_filled_templates_written"
        )
        is True,
        "template_transfer_values_transferred_count": int(
            summary.get("template_transfer_values_transferred_count", 0) or 0
        ),
        "template_transfer_templates_written_count": int(
            summary.get("template_transfer_templates_written_count", 0) or 0
        ),
        "template_transfer_execution_allowed": (
            summary.get("template_transfer_execution_allowed") is True
        ),
        "template_transfer_applier_execution_allowed": (
            summary.get("template_transfer_applier_execution_allowed") is True
        ),
        "ready_for_validator_approval": summary.get("ready_for_validator_approval") is True,
        "ready_for_validator_execution": False,
        "validator_execution_run_status": summary.get("validator_execution_run_status"),
        "validator_hold_output_review_status": summary.get(
            "validator_hold_output_review_status"
        ),
        "validator_hold_output_review_completed": summary.get(
            "validator_hold_output_review_completed"
        )
        is True,
        "validator_outputs_review_required": summary.get("validator_outputs_review_required") is True,
        "validator_missing_input_completion_required": summary.get(
            "validator_missing_input_completion_required"
        )
        is True,
        "rerun_validators_after_completion_required": summary.get(
            "rerun_validators_after_completion_required"
        )
        is True,
        "local_validators_run": summary.get("local_validators_run") is True,
        "planned_validator_count": int(summary.get("planned_validator_count", 0) or 0),
        "ready_validator_count": int(summary.get("ready_validator_count", 0) or 0),
        "validator_approval_request_count": int(
            summary.get("validator_approval_request_count", 0) or 0
        ),
        "approved_validator_count": int(summary.get("approved_validator_count", 0) or 0),
        "validator_execution_authorized_count": int(
            summary.get("validator_execution_authorized_count", 0) or 0
        ),
        "validators_run": summary.get("validators_run") is True,
        "validators_run_count": int(summary.get("validators_run_count", 0) or 0),
        "validator_hold_count": int(summary.get("validator_hold_count", 0) or 0),
        "validator_pass_count": int(summary.get("validator_pass_count", 0) or 0),
        "validator_stop_count": int(summary.get("validator_stop_count", 0) or 0),
        "builder_ready_count": int(summary.get("builder_ready_count", 0) or 0),
        "blockers_closed_by_validator_run": int(
            summary.get("blockers_closed_by_validator_run", 0) or 0
        ),
        "requires_validator_approval_review": summary.get("requires_validator_approval_review")
        is True,
        "requires_validator_output_review": summary.get("requires_validator_output_review") is True,
        "requires_validator_input_completion": summary.get(
            "requires_validator_input_completion"
        )
        is True,
        "requires_validator_rerun_after_completion": summary.get(
            "requires_validator_rerun_after_completion"
        )
        is True,
        "requires_separate_validator_execution_request": summary.get(
            "requires_separate_validator_execution_request"
        )
        is True,
        "requires_separate_evidence_builder_request": summary.get(
            "requires_separate_evidence_builder_request"
        )
        is True,
        "total_missing_metadata_field_count": int(
            summary.get("total_missing_metadata_field_count", 0) or 0
        ),
        "total_missing_evidence_item_count": int(
            summary.get("total_missing_evidence_item_count", 0) or 0
        ),
        "total_missing_source_note_count": int(
            summary.get("total_missing_source_note_count", 0) or 0
        ),
        "make_target": "make commercial-next-human-input",
        "check_target": "make check-commercial-next-human-input-prompt",
        "next_human_action": summary.get("next_human_action"),
    }
    for flag in FALSE_FLAGS:
        payload[flag] = False
    payload["validators_run_on_real_input"] = payload.get("validators_run") is True
    payload["blockers_closed_by_prompt"] = 0
    payload["entrypoints"] = {
        "next_action_html": payload["next_action_html"],
        "review_batch_human_fill_card_html": payload[
            "source_review_batch_human_fill_card_html"
        ],
    }
    return payload


def write_markdown(payload: dict[str, Any]) -> None:
    content = f"""# SAEE Commercial Next Human Input Prompt

commercial_next_human_input_prompt_v0_1: true
local_static_next_action_html: true
status: {payload['status']}
prompt_scope: {payload['prompt_scope']}
action_id: {payload['action_id']}
sequence_step_id: {payload['sequence_step_id']}
first_blocker_id: {payload['first_blocker_id']}
parallel_human_input_lane_count: {payload['parallel_human_input_lane_count']}
primary_human_input_lane: {payload['primary_human_input_lane']}
preferred_human_input_path: {payload['preferred_human_input_path']}
preferred_batch_size: {payload['preferred_batch_size']}
preferred_template_row_count: {payload['preferred_template_row_count']}
preferred_template_value_present_row_count: {payload['preferred_template_value_present_row_count']}
preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}
ready_for_preferred_template_human_fill: {str(payload['ready_for_preferred_template_human_fill']).lower()}
full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
related_human_sequence_lane: {payload['related_human_sequence_lane']}
related_human_sequence_step_id: {payload['related_human_sequence_step_id']}
related_human_sequence_blocker_id: {payload['related_human_sequence_blocker_id']}
related_human_sequence_status: {payload['related_human_sequence_status']}
related_human_sequence_missing_human_field_count: {payload['related_human_sequence_missing_human_field_count']}
quick_fill_row_count: {payload['quick_fill_row_count']}
selected_blocker_count: {payload['selected_blocker_count']}
completed_value_row_count: {payload['completed_value_row_count']}
missing_value_row_count: {payload['missing_value_row_count']}
required_human_field_count: {payload['required_human_field_count']}
ready_for_safety_preflight: {str(payload['ready_for_safety_preflight']).lower()}
ready_for_workbook_import: {str(payload['ready_for_workbook_import']).lower()}
ready_for_workbook_import_approval: {str(payload['ready_for_workbook_import_approval']).lower()}
ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
ready_for_separate_human_template_transfer_execution_request: {str(payload['ready_for_separate_human_template_transfer_execution_request']).lower()}
human_template_transfer_execution_request_recorded: {str(payload['human_template_transfer_execution_request_recorded']).lower()}
human_template_transfer_execution_authorized: {str(payload['human_template_transfer_execution_authorized']).lower()}
source_workbook_import_performed: {str(payload['source_workbook_import_performed']).lower()}
source_workbook_written: {str(payload['source_workbook_written']).lower()}
requires_workbook_import_approval_review: {str(payload['requires_workbook_import_approval_review']).lower()}
requires_separate_workbook_import_execution_request: {str(payload['requires_separate_workbook_import_execution_request']).lower()}
requires_separate_template_transfer_execution_request: {str(payload['requires_separate_template_transfer_execution_request']).lower()}
workbook_import_authorized: false
workbook_written: false
template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
template_transfer_values_transferred: {str(payload['template_transfer_values_transferred']).lower()}
template_transfer_human_filled_templates_written: {str(payload['template_transfer_human_filled_templates_written']).lower()}
template_transfer_values_transferred_count: {payload['template_transfer_values_transferred_count']}
template_transfer_templates_written_count: {payload['template_transfer_templates_written_count']}
template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
planned_validator_count: {payload['planned_validator_count']}
ready_validator_count: {payload['ready_validator_count']}
validator_approval_request_count: {payload['validator_approval_request_count']}
approved_validator_count: {payload['approved_validator_count']}
validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
validators_run: {str(payload['validators_run']).lower()}
validator_execution_run_status: {payload['validator_execution_run_status']}
validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
validator_hold_output_review_completed: {str(payload['validator_hold_output_review_completed']).lower()}
validator_outputs_review_required: {str(payload['validator_outputs_review_required']).lower()}
validator_missing_input_completion_required: {str(payload['validator_missing_input_completion_required']).lower()}
rerun_validators_after_completion_required: {str(payload['rerun_validators_after_completion_required']).lower()}
total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
total_missing_source_note_count: {payload['total_missing_source_note_count']}
local_validators_run: {str(payload['local_validators_run']).lower()}
validators_run_count: {payload['validators_run_count']}
validator_hold_count: {payload['validator_hold_count']}
validator_pass_count: {payload['validator_pass_count']}
validator_stop_count: {payload['validator_stop_count']}
builder_ready_count: {payload['builder_ready_count']}
blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
requires_validator_approval_review: {str(payload['requires_validator_approval_review']).lower()}
requires_validator_output_review: {str(payload['requires_validator_output_review']).lower()}
requires_validator_input_completion: {str(payload['requires_validator_input_completion']).lower()}
requires_validator_rerun_after_completion: {str(payload['requires_validator_rerun_after_completion']).lower()}
requires_separate_validator_execution_request: {str(payload['requires_separate_validator_execution_request']).lower()}
requires_separate_evidence_builder_request: {str(payload['requires_separate_evidence_builder_request']).lower()}
validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}
evidence_collection_authorized: false
execution_authorized: false
blockers_closed_by_prompt: 0
production_ready: false
customer_validated: false
product_launched: false

## Review File

`{payload['preferred_human_input_path']}`

All confirmed values have already been imported into the local workbook, and
the controlled template-transfer applier has written the local human-filled
template files. The five approved local validators have also run and all remain
hold. The validator hold-output review is complete and found the missing
metadata fields, evidence review items, and source notes that must be completed
before rerunning local validators. This prompt does not authorize evidence
builders, evidence collection, blocker closure, customer contact, launch, or
production claims.

## Browser Companion

Open this local static page when a human needs the shortest next-action view:

`{payload['next_action_html']}`

It points to the current human-review lane:

`{payload['source_review_batch_human_fill_card_html']}`

## Related Smaller Human Sequence Lane

The primary commercial readiness lane is now validator missing-input completion.
The completed 64-row quick-fill packet, template transfer outputs, local
validator run, and validator hold-output review remain source context only. No
owner contact, evidence builder execution, evidence collection, blocker
closure, customer contact, launch, or production-readiness claim is authorized.
For a smaller first-owner action, the related lane is:

- lane: `{payload['related_human_sequence_lane']}`
- blocker: `{payload['related_human_sequence_blocker_id']}`
- step: `{payload['related_human_sequence_step_id']}`
- status: `{payload['related_human_sequence_status']}`
- entrypoint: `{payload['source_related_human_sequence_entrypoint']}`
- missing_human_field_count: `{payload['related_human_sequence_missing_human_field_count']}`

This related lane is human input only. It does not authorize owner contact,
evidence collection, execution, blocker closure, customer contact, launch, or
production-readiness claims.

## Next Controlled Local Action

Complete the missing validator input evidence listed in
`commercial_sprint_validator_hold_output_review.md`, then rerun the local
validators. If evidence-builder execution is desired later, create a separate
explicit human execution request. Do not create production evidence from this
prompt.

## Stop Point

Stop at validator missing-input completion and validator rerun preparation.
Evidence builders, evidence collection, blocker closure, customer/vendor
contact, product launch, and production-readiness claims require separate human
approval.
"""
    OUTPUT_MD.write_text(content, encoding="utf-8")
    TOP_DOC.write_text(content, encoding="utf-8")
    GATE.write_text(
        content
        + f"""
## Recommendation Gate

answer: recommend
recommend_for_human_input_prompt: true
recommend_for_review_batch_template_human_input: false
recommend_for_workbook_import_approval_review: false
recommend_for_template_transfer_execution_request_review: false
recommend_for_quick_fill_human_input: false
recommend_for_related_human_sequence_context: true
recommend_for_owner_assignment_by_codex: false
recommend_for_template_transfer_execution: false
recommend_for_validator_approval_review: {str(payload['requires_validator_approval_review']).lower()}
recommend_for_validator_outputs_review: {str(payload['requires_validator_output_review']).lower()}
recommend_for_validator_execution: false
recommend_for_workbook_import_execution: false
recommend_for_evidence_collection: false
recommend_for_execution: false
recommend_for_blocker_closure: false
recommend_for_production: false
""",
        encoding="utf-8",
    )


def esc(value: Any) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def write_html(payload: dict[str, Any]) -> None:
    html_content = f"""<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SAEE 商用下一步</title>
    <style>
      :root {{
        color-scheme: light;
        --bg: #f6f8f4;
        --panel: #ffffff;
        --soft: #eef2ed;
        --text: #111310;
        --muted: #5f6b62;
        --line: #dce5dc;
        --accent: #0a6f5b;
        --danger: #8b2f24;
      }}
      * {{ box-sizing: border-box; }}
      body {{
        margin: 0;
        background: var(--bg);
        color: var(--text);
        font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        line-height: 1.55;
      }}
      main {{
        width: min(1080px, calc(100% - 32px));
        margin: 0 auto;
        padding: 40px 0 56px;
      }}
      .hero {{
        display: grid;
        grid-template-columns: minmax(0, 1.2fr) minmax(280px, 0.8fr);
        gap: 18px;
        align-items: stretch;
      }}
      .panel {{
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel);
        box-shadow: 0 18px 48px rgba(20, 42, 32, 0.07);
      }}
      .intro {{ padding: clamp(24px, 5vw, 46px); }}
      .status {{ padding: 22px; background: var(--soft); }}
      h1, h2, h3, p {{ margin-top: 0; }}
      h1 {{ margin-bottom: 18px; font-size: clamp(34px, 5vw, 62px); line-height: 1.04; letter-spacing: 0; }}
      h2 {{ margin-bottom: 12px; font-size: 22px; }}
      h3 {{ margin-bottom: 8px; font-size: 16px; }}
      p {{ color: var(--muted); }}
      .kicker {{ color: var(--accent); font-size: 13px; font-weight: 800; }}
      .badge {{
        display: inline-flex;
        align-items: center;
        min-height: 32px;
        padding: 0 10px;
        border-radius: 999px;
        background: #e2f2ec;
        color: var(--accent);
        font-size: 12px;
        font-weight: 800;
      }}
      .grid {{
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 12px;
        margin-top: 18px;
      }}
      .card {{
        min-height: 126px;
        padding: 18px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel);
      }}
      .step-list {{
        display: grid;
        gap: 12px;
        padding: 0;
        margin: 20px 0 0;
        list-style: none;
      }}
      .step-list li {{
        display: grid;
        grid-template-columns: 38px minmax(0, 1fr);
        gap: 12px;
        padding: 16px;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: var(--panel);
      }}
      .step-list span {{
        width: 38px;
        height: 38px;
        display: grid;
        place-items: center;
        border-radius: 10px;
        background: var(--accent);
        color: #fff;
        font-weight: 900;
      }}
      code {{
        padding: 2px 5px;
        border-radius: 6px;
        background: var(--soft);
        color: var(--text);
        overflow-wrap: anywhere;
      }}
      pre {{
        overflow: auto;
        margin: 12px 0 0;
        padding: 14px;
        border-radius: 10px;
        background: #111d18;
        color: #eef8f4;
        font-size: 13px;
      }}
      .stop {{
        margin-top: 18px;
        padding: 18px;
        border: 1px solid #ecd4cf;
        border-radius: 10px;
        background: #fff4f1;
      }}
      .stop strong {{ color: var(--danger); }}
      .meta {{
        display: grid;
        gap: 10px;
        margin: 0;
      }}
      .meta div {{
        display: flex;
        justify-content: space-between;
        gap: 14px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--line);
      }}
      .meta div:last-child {{ border-bottom: 0; padding-bottom: 0; }}
      .meta dt {{ color: var(--muted); }}
      .meta dd {{ margin: 0; font-weight: 800; text-align: right; }}
      a {{ color: var(--accent); font-weight: 800; text-decoration: none; }}
      @media (max-width: 820px) {{
        .hero, .grid {{ grid-template-columns: 1fr; }}
      }}
    </style>
  </head>
  <body>
    <main>
      <section class="hero">
        <div class="panel intro">
          <p class="kicker">SAEE 商用下一步</p>
          <h1>审查 validator hold 输出。</h1>
          <p>
            当前最短路径不是开发新功能，也不是继续执行。5 个本地 validator 已经运行；
            结果全部是 hold。现在只需要人审查这些 hold 原因，决定下一步补哪些证据。
          </p>
          <p>
            Codex 不能直接执行 evidence builder。只有你明确发出单独执行请求后，后续脚本
            才能继续。现在不能收集证据、关闭 blocker、联系客户或发布产品。
          </p>
          <div class="grid">
            <div class="card">
              <h3>缺失值</h3>
              <p><strong>{esc(payload['missing_value_row_count'])}</strong> 行</p>
            </div>
            <div class="card">
              <h3>下一步</h3>
              <p><strong>人工审查</strong> validator hold 输出</p>
            </div>
            <div class="card">
              <h3>上线状态</h3>
              <p><strong>未生产可用</strong>，仍有 {esc(payload['production_blocker_count'])} 个 blocker</p>
            </div>
          </div>
        </div>
        <aside class="panel status">
          <span class="badge">{esc(payload['status'])}</span>
          <h2>当前边界</h2>
          <dl class="meta">
            <div><dt>生产可用</dt><dd>false</dd></div>
            <div><dt>客户验证</dt><dd>false</dd></div>
            <div><dt>产品发布</dt><dd>false</dd></div>
            <div><dt>模板转写已完成</dt><dd>{esc(str(payload['template_transfer_performed']).lower())}</dd></div>
            <div><dt>validator 本地运行</dt><dd>{esc(str(payload['validators_run']).lower())}</dd></div>
            <div><dt>证据收集授权</dt><dd>false</dd></div>
            <div><dt>关闭 blocker</dt><dd>0</dd></div>
          </dl>
        </aside>
      </section>

      <section>
        <ol class="step-list">
          <li>
            <span>1</span>
            <div>
              <h2>打开 validator hold 输出</h2>
              <p>
                先看当前人工审查路径：
                <code>{esc(payload['preferred_human_input_path'])}</code>
              </p>
            </div>
          </li>
          <li>
            <span>2</span>
            <div>
              <h2>确认边界</h2>
              <p>确认本次只做审批记录，不运行验证、不生成证据、不上线。</p>
            </div>
          </li>
          <li>
            <span>3</span>
            <div>
              <h2>审批后仍然停止</h2>
              <p>即使审批通过，validator 执行和证据收集仍需要单独请求。</p>
              <pre>只审查 validator 批准请求
停止在 execution / evidence / closure 之前</pre>
            </div>
          </li>
        </ol>
        <div class="stop">
          <h2>停止点</h2>
          <p>
            <strong>到 validator 审批审查就停。</strong>
            现在不运行真实输入 validator、
            不收集证据、不关闭 blocker、不联系客户、不发布产品、不声明生产可用。
            后续任何一步都需要单独人工批准。
          </p>
        </div>
      </section>
    </main>
  </body>
</html>
"""
    OUTPUT_HTML.write_text(html_content, encoding="utf-8")


def main() -> None:
    payload = build_payload()
    write_json(OUTPUT_JSON, payload)
    write_markdown(payload)
    write_html(payload)
    print(
        "SAEE_COMMERCIAL_NEXT_HUMAN_INPUT_PROMPT: PASS "
        f"status={payload['status']} missing_value_row_count={payload['missing_value_row_count']} "
        "workbook_import_authorized=false production_ready=false"
    )


if __name__ == "__main__":
    main()
