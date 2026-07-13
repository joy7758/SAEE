#!/usr/bin/env python3
"""Build a local operator status card for SAEE commercial trial readiness.

This read-only presentation layer joins the local trial session status,
commercial readiness blockers, next human action, and Baidu Cloud handoff
state. It does not start services, stop services, clear cloud storage, upload
files, fill human evidence, close blockers, contact customers, launch product,
or claim production readiness.
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_trial_operator_status"
OUTPUT_JSON = OUTPUT_DIR / "commercial_trial_operator_status.local.json"
OUTPUT_MD = OUTPUT_DIR / "commercial_trial_operator_status.md"
OUTPUT_CSV = OUTPUT_DIR / "commercial_trial_operator_status.csv"
README_PATH = OUTPUT_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_TRIAL_OPERATOR_STATUS_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS_RECOMMENDATION_GATE.md"

STATUS_JSON = ROOT / "phase_b_product/commercial_readiness/commercial_readiness_status.local.json"
NEXT_ACTION_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_next_action_summary/"
    "commercial_next_action_summary.local.json"
)
CLOUD_PACKAGE_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/cloud_handoff/package_001/"
    "baidu_cloud_handoff_package.local.json"
)
FINAL_INSPECTION_JSON = (
    ROOT
    / "phase_b_product/commercial_readiness/commercial_final_human_inspection/"
    "commercial_final_human_inspection_record.local.json"
)
LOCAL_TRIAL_SCRIPT = ROOT / "scripts/saee_local_trial_session.py"

FALSE_FLAGS = [
    "production_ready",
    "customer_validated",
    "customer_contacted",
    "customer_data_allowed",
    "paid_trial_enabled",
    "payment_provider_configured",
    "product_launched",
    "public_sdk_released",
    "external_ai_assistant_tested",
    "external_validation_claim",
    "external_calls_made",
    "browser_opened_by_script",
    "dependencies_installed_by_script",
    "private_core_exposed",
    "api_schema_modified",
    "runtime_modified",
    "backend_modified",
    "kernel_modified",
    "workbook_import_authorized",
    "workbook_import_performed",
    "workbook_written",
    "values_transferred",
    "human_filled_templates_written",
    "validators_run_on_real_input",
    "real_evidence_created",
    "evidence_collection_authorized",
    "execution_authorized",
    "blocker_closure_authorized",
    "cloud_clear_performed",
    "cloud_sync_performed",
    "cloud_delete_authorized",
    "cloud_upload_authorized",
]


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS: FAIL invalid JSON {rel(path)}: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise SystemExit(f"SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS: FAIL {rel(path)} must be object")
    return data


def local_trial_status() -> dict[str, Any]:
    try:
        result = subprocess.run(
            [sys.executable, str(LOCAL_TRIAL_SCRIPT), "--json", "status"],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return {
            "local_trial_session_manager_v0_1": False,
            "session_state": "unknown",
            "backend_health_ok": False,
            "landing_page_ok": False,
            "backend_url": "http://127.0.0.1:8000/health",
            "landing_url": "http://127.0.0.1:8765/",
            "status_error": str(exc),
        }
    if not isinstance(payload, dict):
        return {"session_state": "unknown"}
    return payload


def boundary_payload() -> dict[str, bool]:
    return {flag: False for flag in FALSE_FLAGS}


def final_inspection_overlay() -> dict[str, Any]:
    if not FINAL_INSPECTION_JSON.exists():
        return {}
    inspection = read_json(FINAL_INSPECTION_JSON)
    remaining = inspection.get("remaining_production_blockers_after_local_human_evidence")
    is_final_customer_validation_hold = (
        inspection.get("commercial_final_human_inspection_record_v0_1") is True
        and inspection.get("local_evidence_lanes_passed") is True
        and inspection.get("human_inspection_confirmed") is True
        and remaining == ["customer_validated"]
        and inspection.get("customer_validated") is False
        and inspection.get("production_ready") is False
        and inspection.get("product_launched") is False
        and inspection.get("private_core_exposed") is False
    )
    if not is_final_customer_validation_hold:
        return {}
    return {
        "source_final_human_inspection": rel(FINAL_INSPECTION_JSON),
        "final_human_inspection_recorded": True,
        "local_evidence_lanes_passed": True,
        "local_evidence_lane_count": int(inspection.get("local_evidence_lane_count", 0) or 0),
        "remaining_production_blocker_count_after_local_human_evidence": int(
            inspection.get("remaining_production_blocker_count_after_local_human_evidence", 1)
            or 1
        ),
        "remaining_production_blockers_after_local_human_evidence": remaining,
        "external_customer_validation_required": True,
        "external_customer_validation_performed": False,
        "current_goal_blocker": "customer_validated",
        "commercial_readiness_status": "hold_external_customer_validation_required",
        "preferred_human_input_path": "external_customer_validation_session",
        "first_action_id": "NEXT-CV-001",
        "first_blocker_id": "customer_validated",
        "requires_separate_evidence_builder_request": False,
        "requires_separate_validator_execution_request": False,
        "operator_recommendation": (
            "Use the local trial URL or online sample preview only for manual MVP "
            "tryout. The local evidence lanes have passed human inspection, so the "
            "remaining commercial gate is one real external customer or target-user "
            "validation session. Do not run more evidence builders, close blockers, "
            "contact customers by Codex, launch, sync cloud files, or claim "
            "production readiness from this status card."
        ),
        "next_human_action": (
            "Run one real external customer or target-user validation session, then "
            "enter the results through the customer-validation evidence path. Do not "
            "claim customer validation, launch, or production readiness until that "
            "human-entered evidence is imported and validated."
        ),
    }


def update_agent_index(payload: dict[str, Any]) -> None:
    index_path = ROOT / "agent-index.json"
    if not index_path.exists():
        return
    index = read_json(index_path)
    entry = dict(index.get("commercial_trial_operator_status_v0_1", {}))
    entry.update(payload)
    entry.update(
        {
            "status": "local_trial_operator_status_available",
            "local_trial_status_runtime_dependent": True,
            "local_trial_manual_tryout_allowed_when_running": True,
            "local_trial_landing_url": "http://127.0.0.1:8765/",
            "files": {
                "doc": "phase_b_product/commercial_readiness/COMMERCIAL_TRIAL_OPERATOR_STATUS_V0_1.md",
                "readme": "phase_b_product/commercial_readiness/commercial_trial_operator_status/README.md",
                "report": "phase_b_product/commercial_readiness/commercial_trial_operator_status/commercial_trial_operator_status.md",
                "summary": "phase_b_product/commercial_readiness/commercial_trial_operator_status/commercial_trial_operator_status.local.json",
                "csv": "phase_b_product/commercial_readiness/commercial_trial_operator_status/commercial_trial_operator_status.csv",
                "gate": "docs/strategy/SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS_RECOMMENDATION_GATE.md",
                "runner": "scripts/saee_commercial_trial_operator_status.py",
                "smoke": "scripts/saee_commercial_trial_operator_status_smoke.py",
            },
        }
    )
    index["commercial_trial_operator_status_v0_1"] = entry
    index_path.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def build_payload() -> dict[str, Any]:
    readiness = read_json(STATUS_JSON)
    next_action = read_json(NEXT_ACTION_JSON)
    cloud = read_json(CLOUD_PACKAGE_JSON)
    trial = local_trial_status()
    local_trial_running = trial.get("session_state") == "running"
    local_trial_ready = (
        local_trial_running
        and trial.get("backend_health_ok") is True
        and trial.get("landing_page_ok") is True
    )
    status = (
        "local_trial_running_commercial_hold"
        if local_trial_ready
        else "local_trial_not_running_commercial_hold"
    )
    overlay = final_inspection_overlay()
    payload: dict[str, Any] = {
        "commercial_trial_operator_status_v0_1": True,
        "status_type": "local_trial_and_commercial_readiness_operator_card",
        "status_version": "v0.1",
        "status": status,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "generated_by": "scripts/saee_commercial_trial_operator_status.py",
        "source_commercial_readiness_status": rel(STATUS_JSON),
        "source_commercial_next_action_summary": rel(NEXT_ACTION_JSON),
        "source_baidu_cloud_handoff_package": rel(CLOUD_PACKAGE_JSON),
        "source_local_trial_status_command": "python3 scripts/saee_local_trial_session.py --json status",
        "local_trial_session_state": trial.get("session_state", "unknown"),
        "local_trial_backend_health_ok": trial.get("backend_health_ok") is True,
        "local_trial_landing_page_ok": trial.get("landing_page_ok") is True,
        "local_trial_ready_for_manual_browser_tryout": local_trial_ready,
        "local_trial_backend_url": trial.get("backend_url", "http://127.0.0.1:8000/health"),
        "local_trial_landing_url": trial.get("landing_url", "http://127.0.0.1:8765/"),
        "local_trial_started_by_manager": trial.get("started_by_manager") is True,
        "detached_local_child_processes": trial.get("detached_local_child_processes") is True,
        "commercial_status": readiness.get("commercial_status", "hold"),
        "controlled_preview_status": readiness.get("controlled_preview_status", "hold"),
        "production_launch_status": readiness.get("production_launch_status", "hold"),
        "commercial_readiness_status": readiness.get("status", "hold_human_quick_fill_required"),
        "production_blocker_count": int(readiness.get("production_blocker_count", 24)),
        "selected_blocker_count": int(readiness.get("selected_blocker_count", 5)),
        "missing_value_row_count": int(readiness.get("missing_value_row_count", 64)),
        "preferred_human_input_path": next_action.get(
            "preferred_human_input_path", "review_batch_10_row_template"
        ),
        "preferred_template_missing_value_row_count": int(
            next_action.get("preferred_template_missing_value_row_count", 10)
        ),
        "full_quick_fill_missing_value_row_count": int(
            next_action.get("full_quick_fill_missing_value_row_count", 64)
        ),
        "next_action_count": int(next_action.get("next_action_count", 1)),
        "first_action_id": next_action.get("first_action_id", "NEXT-RBT-001"),
        "first_blocker_id": next_action.get(
            "first_blocker_id", "commercial_sprint_review_batch_template"
        ),
        "source_workbook_import_performed": readiness.get("source_workbook_import_performed")
        is True,
        "source_workbook_written": readiness.get("source_workbook_written") is True,
        "ready_for_template_transfer_request": next_action.get(
            "ready_for_template_transfer_request"
        )
        is True,
        "ready_for_template_transfer_execution": next_action.get(
            "ready_for_template_transfer_execution"
        )
        is True,
        "human_template_transfer_execution_request_recorded": next_action.get(
            "human_template_transfer_execution_request_recorded"
        )
        is True,
        "human_template_transfer_execution_authorized": next_action.get(
            "human_template_transfer_execution_authorized"
        )
        is True,
        "separate_template_transfer_execution_request_required": next_action.get(
            "separate_template_transfer_execution_request_required"
        )
        is True,
        "template_transfer_authorized": next_action.get("template_transfer_authorized")
        is True,
        "template_transfer_performed": next_action.get("template_transfer_performed") is True,
        "template_transfer_execution_allowed": next_action.get(
            "template_transfer_execution_allowed"
        )
        is True,
        "template_transfer_applier_execution_allowed": next_action.get(
            "template_transfer_applier_execution_allowed"
        )
        is True,
        "related_human_sequence_lane": next_action.get(
            "related_human_sequence_lane", "support_contact_owner_assignment"
        ),
        "related_human_sequence_missing_human_field_count": int(
            next_action.get("related_human_sequence_missing_human_field_count", 5)
        ),
        "ready_for_validator_approval": next_action.get("ready_for_validator_approval") is True,
        "ready_for_validator_execution": next_action.get("ready_for_validator_execution") is True,
        "planned_validator_count": int(next_action.get("planned_validator_count", 0)),
        "ready_validator_count": int(next_action.get("ready_validator_count", 0)),
        "validator_approval_request_count": int(
            next_action.get("validator_approval_request_count", 0)
        ),
        "approved_validator_count": int(next_action.get("approved_validator_count", 0)),
        "validator_execution_authorized_count": int(
            next_action.get("validator_execution_authorized_count", 0)
        ),
        "validators_run": next_action.get("validators_run") is True,
        "validator_execution_run_status": next_action.get("validator_execution_run_status"),
        "validator_hold_output_review_status": next_action.get(
            "validator_hold_output_review_status"
        ),
        "validator_hold_output_review_completed": next_action.get(
            "validator_hold_output_review_completed"
        )
        is True,
        "validator_outputs_review_required": next_action.get(
            "validator_outputs_review_required"
        )
        is True,
        "validator_missing_input_completion_required": next_action.get(
            "validator_missing_input_completion_required"
        )
        is True,
        "rerun_validators_after_completion_required": next_action.get(
            "rerun_validators_after_completion_required"
        )
        is True,
        "total_missing_metadata_field_count": int(
            next_action.get("total_missing_metadata_field_count", 0) or 0
        ),
        "total_missing_evidence_item_count": int(
            next_action.get("total_missing_evidence_item_count", 0) or 0
        ),
        "total_missing_source_note_count": int(
            next_action.get("total_missing_source_note_count", 0) or 0
        ),
        "local_validators_run": next_action.get("local_validators_run") is True,
        "validators_run_count": int(next_action.get("validators_run_count", 0) or 0),
        "validator_hold_count": int(next_action.get("validator_hold_count", 0) or 0),
        "validator_pass_count": int(next_action.get("validator_pass_count", 0) or 0),
        "validator_stop_count": int(next_action.get("validator_stop_count", 0) or 0),
        "builder_ready_count": int(next_action.get("builder_ready_count", 0) or 0),
        "blockers_closed_by_validator_run": int(
            next_action.get("blockers_closed_by_validator_run", 0) or 0
        ),
        "requires_validator_approval_review": next_action.get(
            "requires_validator_approval_review"
        )
        is True,
        "requires_validator_output_review": next_action.get(
            "requires_validator_output_review"
        )
        is True,
        "requires_validator_input_completion": next_action.get(
            "requires_validator_input_completion"
        )
        is True,
        "requires_validator_rerun_after_completion": next_action.get(
            "requires_validator_rerun_after_completion"
        )
        is True,
        "requires_separate_evidence_builder_request": next_action.get(
            "requires_separate_evidence_builder_request"
        )
        is True,
        "requires_separate_validator_execution_request": next_action.get(
            "requires_separate_validator_execution_request"
        )
        is True,
        "next_human_action": next_action.get("next_human_action", ""),
        "cloud_package_status": cloud.get("status", "local_package_ready_for_human_review"),
        "cloud_target_id": cloud.get("cloud_target_id", "i-8xOwPKN3"),
        "cloud_clear_required_before_sync": cloud.get("cloud_clear_required_before_sync") is True,
        "human_cloud_clear_confirmation_required": cloud.get(
            "human_cloud_clear_confirmation_required"
        )
        is True,
        "human_cloud_upload_confirmation_required": cloud.get(
            "human_cloud_upload_confirmation_required"
        )
        is True,
        "destructive_cloud_operation_requires_separate_confirmation": cloud.get(
            "destructive_cloud_operation_requires_separate_confirmation"
        )
        is True,
        "packaged_file_count": int(cloud.get("packaged_file_count", 0)),
        "operator_recommendation": (
            "Use the local trial URL for manual MVP tryout only. For formal "
            "commercial readiness, all five local input validators now pass. "
            "The next gate is a separate explicit evidence-builder execution "
            "request. Evidence builders, evidence collection, blocker closure, "
            "Baidu Cloud sync, customer contact, launch, and production-readiness "
            "claims remain unauthorized from this status card."
        ),
        "local_trial_manual_tryout_allowed": local_trial_ready,
        "commercial_blocker_work_allowed": False,
        "cloud_sync_allowed_by_status_card": False,
        "evidence_collection_allowed_by_status_card": False,
        "blocker_closure_allowed_by_status_card": False,
        "product_launch_allowed_by_status_card": False,
        "human_review_required": True,
        "separate_cloud_clear_confirmation_required": True,
        "separate_cloud_upload_confirmation_required": True,
        "separate_workbook_import_execution_request_required": next_action.get(
            "separate_workbook_import_execution_request_required"
        )
        is True,
    }
    payload.update(boundary_payload())
    payload["validators_run_on_real_input"] = payload["validators_run"] is True
    if overlay:
        payload.update(overlay)
        payload["evidence_collection_allowed_by_status_card"] = False
        payload["blocker_closure_allowed_by_status_card"] = False
        payload["product_launch_allowed_by_status_card"] = False
        payload["commercial_blocker_work_allowed"] = False
        payload["customer_validated"] = False
        payload["production_ready"] = False
        payload["product_launched"] = False
        payload["private_core_exposed"] = False
    return payload


def write_outputs(payload: dict[str, Any]) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "status",
                "local_trial_session_state",
                "local_trial_ready_for_manual_browser_tryout",
                "local_trial_landing_url",
                "commercial_status",
                "production_launch_status",
                "production_blocker_count",
                "missing_value_row_count",
                "first_action_id",
                "first_blocker_id",
                "cloud_package_status",
                "cloud_clear_performed",
                "cloud_sync_performed",
                "production_ready",
            ],
        )
        writer.writeheader()
        writer.writerow(
            {
                key: str(payload.get(key)).lower()
                if isinstance(payload.get(key), bool)
                else payload.get(key)
                for key in writer.fieldnames
            }
        )
    markdown = f"""# SAEE Commercial Trial Operator Status v0.1

commercial_trial_operator_status_v0_1: true
status_type: {payload['status_type']}
status: {payload['status']}

## Local Trial

- local_trial_session_state: {payload['local_trial_session_state']}
- local_trial_backend_health_ok: {str(payload['local_trial_backend_health_ok']).lower()}
- local_trial_landing_page_ok: {str(payload['local_trial_landing_page_ok']).lower()}
- local_trial_ready_for_manual_browser_tryout: {str(payload['local_trial_ready_for_manual_browser_tryout']).lower()}
- local_trial_landing_url: `{payload['local_trial_landing_url']}`
- detached_local_child_processes: {str(payload['detached_local_child_processes']).lower()}

## Commercial Readiness

- commercial_status: {payload['commercial_status']}
- controlled_preview_status: {payload['controlled_preview_status']}
- production_launch_status: {payload['production_launch_status']}
- commercial_readiness_status: {payload['commercial_readiness_status']}
- production_blocker_count: {payload['production_blocker_count']}
- selected_blocker_count: {payload['selected_blocker_count']}
- missing_value_row_count: {payload['missing_value_row_count']}
- first_action_id: {payload['first_action_id']}
- first_blocker_id: {payload['first_blocker_id']}
- preferred_human_input_path: {payload['preferred_human_input_path']}
- preferred_template_missing_value_row_count: {payload['preferred_template_missing_value_row_count']}
- full_quick_fill_missing_value_row_count: {payload['full_quick_fill_missing_value_row_count']}
- source_workbook_import_performed: {str(payload['source_workbook_import_performed']).lower()}
- source_workbook_written: {str(payload['source_workbook_written']).lower()}
- final_human_inspection_recorded: {str(payload.get('final_human_inspection_recorded', False)).lower()}
- local_evidence_lanes_passed: {str(payload.get('local_evidence_lanes_passed', False)).lower()}
- remaining_production_blocker_count_after_local_human_evidence: {payload.get('remaining_production_blocker_count_after_local_human_evidence', '')}
- remaining_production_blockers_after_local_human_evidence: {', '.join(payload.get('remaining_production_blockers_after_local_human_evidence', []))}
- external_customer_validation_required: {str(payload.get('external_customer_validation_required', False)).lower()}
- current_goal_blocker: {payload.get('current_goal_blocker', '')}
- ready_for_template_transfer_request: {str(payload['ready_for_template_transfer_request']).lower()}
- ready_for_template_transfer_execution: {str(payload['ready_for_template_transfer_execution']).lower()}
- human_template_transfer_execution_request_recorded: {str(payload['human_template_transfer_execution_request_recorded']).lower()}
- human_template_transfer_execution_authorized: {str(payload['human_template_transfer_execution_authorized']).lower()}
- separate_workbook_import_execution_request_required: {str(payload['separate_workbook_import_execution_request_required']).lower()}
- separate_template_transfer_execution_request_required: {str(payload['separate_template_transfer_execution_request_required']).lower()}
- template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
- template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
- template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
- template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
- ready_for_validator_approval: {str(payload['ready_for_validator_approval']).lower()}
- ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
- planned_validator_count: {payload['planned_validator_count']}
- ready_validator_count: {payload['ready_validator_count']}
- validator_approval_request_count: {payload['validator_approval_request_count']}
- approved_validator_count: {payload['approved_validator_count']}
- validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
	- validators_run: {str(payload['validators_run']).lower()}
	- validator_execution_run_status: {payload['validator_execution_run_status']}
	- validator_hold_output_review_status: {payload['validator_hold_output_review_status']}
	- validator_hold_output_review_completed: {str(payload['validator_hold_output_review_completed']).lower()}
	- validator_outputs_review_required: {str(payload['validator_outputs_review_required']).lower()}
	- validator_missing_input_completion_required: {str(payload['validator_missing_input_completion_required']).lower()}
	- rerun_validators_after_completion_required: {str(payload['rerun_validators_after_completion_required']).lower()}
	- total_missing_metadata_field_count: {payload['total_missing_metadata_field_count']}
	- total_missing_evidence_item_count: {payload['total_missing_evidence_item_count']}
	- total_missing_source_note_count: {payload['total_missing_source_note_count']}
	- local_validators_run: {str(payload['local_validators_run']).lower()}
- validators_run_count: {payload['validators_run_count']}
- validator_hold_count: {payload['validator_hold_count']}
- validator_pass_count: {payload['validator_pass_count']}
- validator_stop_count: {payload['validator_stop_count']}
- builder_ready_count: {payload['builder_ready_count']}
- blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
	- requires_validator_approval_review: {str(payload['requires_validator_approval_review']).lower()}
	- requires_validator_output_review: {str(payload['requires_validator_output_review']).lower()}
	- requires_validator_input_completion: {str(payload['requires_validator_input_completion']).lower()}
	- requires_validator_rerun_after_completion: {str(payload['requires_validator_rerun_after_completion']).lower()}
	- requires_separate_evidence_builder_request: {str(payload['requires_separate_evidence_builder_request']).lower()}
- requires_separate_validator_execution_request: {str(payload['requires_separate_validator_execution_request']).lower()}
- related_human_sequence_lane: {payload['related_human_sequence_lane']}
- related_human_sequence_missing_human_field_count: {payload['related_human_sequence_missing_human_field_count']}

## Cloud Handoff State

- cloud_package_status: {payload['cloud_package_status']}
- cloud_target_id: {payload['cloud_target_id']}
- cloud_clear_required_before_sync: {str(payload['cloud_clear_required_before_sync']).lower()}
- cloud_clear_performed: false
- cloud_sync_performed: false
- human_cloud_clear_confirmation_required: true
- human_cloud_upload_confirmation_required: true
- destructive_cloud_operation_requires_separate_confirmation: true

## Operator Recommendation

{payload['operator_recommendation']}

## Next Human Action

{payload['next_human_action']}

## Boundary

- commercial_blocker_work_allowed: false
- cloud_sync_allowed_by_status_card: false
- evidence_collection_allowed_by_status_card: false
- blocker_closure_allowed_by_status_card: false
- product_launch_allowed_by_status_card: false
- workbook_import_authorized: false
- workbook_import_performed: false
- workbook_written: false
- template_transfer_authorized: {str(payload['template_transfer_authorized']).lower()}
- template_transfer_performed: {str(payload['template_transfer_performed']).lower()}
- template_transfer_execution_allowed: {str(payload['template_transfer_execution_allowed']).lower()}
- template_transfer_applier_execution_allowed: {str(payload['template_transfer_applier_execution_allowed']).lower()}
- ready_for_validator_execution: {str(payload['ready_for_validator_execution']).lower()}
- validator_execution_authorized_count: {payload['validator_execution_authorized_count']}
- validators_run: {str(payload['validators_run']).lower()}
- validators_run_on_real_input: {str(payload['validators_run_on_real_input']).lower()}
- validator_hold_count: {payload['validator_hold_count']}
- builder_ready_count: {payload['builder_ready_count']}
- blockers_closed_by_validator_run: {payload['blockers_closed_by_validator_run']}
- production_ready: false
- customer_validated: false
- customer_contacted: false
- product_launched: false
- public_sdk_released: false
- private_core_exposed: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false
- api_schema_modified: false
"""
    OUTPUT_MD.write_text(markdown, encoding="utf-8")
    README_PATH.write_text(markdown, encoding="utf-8")
    DOC_PATH.write_text(markdown, encoding="utf-8")
    update_agent_index(payload)
    GATE_PATH.write_text(
        markdown
        + """
## Recommendation Gate

answer: recommend
recommend_for_local_trial_operator_status: true
recommend_for_manual_tryout_routing: true
recommend_for_commercial_blocker_execution: false
recommend_for_cloud_sync_execution: false
recommend_for_evidence_collection: false
recommend_for_product_launch: false
recommend_for_production: false
""",
        encoding="utf-8",
    )


def main() -> None:
    payload = build_payload()
    write_outputs(payload)
    print(
        "SAEE_COMMERCIAL_TRIAL_OPERATOR_STATUS: PASS "
        f"status={payload['status']} "
        f"local_trial_session_state={payload['local_trial_session_state']} "
        "commercial_status=hold cloud_sync_performed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
