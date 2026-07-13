#!/usr/bin/env python3
"""Smoke test for the commercial review batch post-fill validation runbook."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_review_batch_post_fill_validation_runbook.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.local.json"
OUT_MD = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.md"
OUT_CSV = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.csv"
OUT_HTML = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook.html"
OUT_BOUNDARY = SPRINT_DIR / "commercial_review_batch_post_fill_validation_runbook_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK_RECOMMENDATION_GATE.md"
)


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK_SMOKE: FAIL: {message}")


def require_file(path: Path) -> None:
    if not path.is_file():
        fail(f"missing {path.relative_to(ROOT)}")


def main() -> None:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)

    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_HTML, OUT_BOUNDARY, TOP_DOC, GATE]:
        require_file(path)

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected = {
        "commercial_review_batch_post_fill_validation_runbook_v0_1": True,
        "runbook_scope": "post_human_fill_local_validation_sequence_only_no_values_no_import_no_execution",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "template_row_count": 0,
        "expected_template_row_count": 10,
        "filled_human_value_row_count": 0,
        "missing_human_value_row_count": 0,
        "post_fill_validation_ready": False,
        "post_fill_runbook_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "human_input_required": False,
        "local_static_post_fill_html": True,
        "browser_readable_post_fill_entrypoint": True,
        "dry_run_command_count": 2,
        "separate_approval_only_command_count": 0,
        "blockers_closed_by_runbook": 0,
    }
    for key, expected_value in expected.items():
        if payload.get(key) != expected_value:
            fail(f"{key} must be {expected_value!r}, got {payload.get(key)!r}")
    if payload.get("status") != "superseded_by_full_quick_fill_values_pending_workbook_import_approval":
        fail("status must record superseded post-fill runbook")
    false_flags = [
        "human_values_generated_by_codex",
        "quick_fill_values_entered_by_codex",
        "source_quick_fill_packet_modified",
        "batch_values_applied_to_source",
        "local_quick_fill_output_written",
        "workbook_import_authorized",
        "workbook_import_performed",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "blockers_closed",
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
        "development_permission_granted",
        "task_candidates_executed",
        "payment_collected",
        "revenue_validated",
        "production_ready_claim",
        "customer_validation_claim",
    ]
    for flag in false_flags:
        if payload.get(flag) is not False:
            fail(f"{flag} must be false")
    if payload.get("boundary_violations") != []:
        fail("boundary_violations must be empty")

    commands = [item.get("command", "") for item in payload.get("dry_run_commands", [])]
    required_commands = [
        "python3 scripts/saee_commercial_sprint_workbook_import_approval_request_packet.py",
        "python3 scripts/mainline_guard.py",
    ]
    missing_commands = [cmd for cmd in required_commands if cmd not in commands]
    if missing_commands:
        fail("dry_run_commands missing: " + ", ".join(missing_commands))

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 2:
        fail("command CSV must contain two local confirmation rows after supersession")
    if any(row.get("execution_boundary") != "dry_run_no_write" for row in rows):
        fail("superseded command rows must remain dry-run no-write")

    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_HTML, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_review_batch_post_fill_validation_runbook_v0_1: true",
        "post_human_fill_local_validation_sequence_only_no_values_no_import_no_execution",
        "10 行填写流程已停用。",
        "post_fill_runbook_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "local_static_post_fill_html: true",
        "browser_readable_post_fill_entrypoint: true",
        "SAEE 商用准备 · 填写后本地检查",
        "10 行填写流程已停用。",
        "等待人工确认是否允许导入工作簿",
        "workbook_import_authorized: false",
        "evidence_collection_authorized: false",
        "blockers_closed_by_runbook: 0",
        "production_ready: false",
        "private_core_exposed: false",
    ]
    missing_tokens = [token for token in required_tokens if token not in combined]
    if missing_tokens:
        fail("generated docs missing tokens: " + ", ".join(missing_tokens))

    print(
        "SAEE_COMMERCIAL_REVIEW_BATCH_POST_FILL_VALIDATION_RUNBOOK_SMOKE: PASS "
        "status=superseded_by_full_quick_fill_values_pending_workbook_import_approval "
        "missing_human_value_row_count=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
