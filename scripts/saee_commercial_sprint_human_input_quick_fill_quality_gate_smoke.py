#!/usr/bin/env python3
"""Smoke check for the commercial sprint quick-fill quality gate."""

from __future__ import annotations

import csv
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
RUNNER = ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py"
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_quality_gate_boundary_audit.md"
TOP_DOC = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_RECOMMENDATION_GATE.md"


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_SMOKE: FAIL {message}")
        sys.exit(1)


def run_gate(*args: str) -> dict:
    subprocess.run([sys.executable, str(RUNNER), *args], cwd=ROOT, check=True)
    return json.loads(OUT_JSON.read_text(encoding="utf-8"))


def synthetic_good_value(row: dict[str, str]) -> str:
    input_key = row.get("input_key", "").lower()
    input_kind = row.get("input_kind", "").lower()
    context = f"{input_key} {input_kind}"
    if "date" in context:
        return "2026-07-06"
    if any(token in context for token in ["owner", "contact"]):
        return "assigned owner review reference for commercial readiness"
    if any(token in context for token in ["approval", "approved", "decision", "acknowledged"]):
        return "approved decision reference recorded for human review"
    return "evidence review status recorded with local artifact reference"


def run_synthetic_fixture_checks() -> None:
    with tempfile.TemporaryDirectory(prefix="saee_quality_gate_") as temp:
        fixture = Path(temp) / "quick_fill_quality_fixture.csv"
        shutil.copyfile(SOURCE_CSV, fixture)
        with fixture.open("r", encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
            fields = list(rows[0].keys())

        for row in rows:
            row["human_value_to_enter"] = synthetic_good_value(row)
        with fixture.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

        good_payload = run_gate("--quick-fill-csv", str(fixture))
        require(
            good_payload.get("status")
            == "pass_quality_gate_pending_safety_preflight_and_human_import_approval",
            "synthetic complete fixture should pass quality gate pending safety preflight",
        )
        require(good_payload.get("completed_value_row_count") == 64, "synthetic complete fixture must have 64 completed rows")
        require(good_payload.get("missing_value_row_count") == 0, "synthetic complete fixture must have no missing rows")
        require(good_payload.get("quality_pass_row_count") == 64, "synthetic complete fixture must have 64 quality-pass rows")
        require(good_payload.get("quality_gate_passed") is True, "synthetic complete fixture must set quality_gate_passed true")
        require(good_payload.get("ready_for_safety_preflight") is True, "synthetic complete fixture must be ready for safety preflight")
        require(good_payload.get("ready_for_workbook_import") is False, "quality gate must not authorize workbook import")
        require(good_payload.get("safe_to_import_after_human_approval") is False, "quality gate must not mark safe_to_import")
        require(good_payload.get("raw_values_recorded") is False, "quality gate must not record raw values")
        require(good_payload.get("production_ready") is False, "synthetic complete fixture must not claim production readiness")

        rows[0]["human_value_to_enter"] = (
            "production_ready=true sk-proj-THISISANONREALFAKESECRETKEYFORSCANNERONLY"
        )
        with fixture.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

        unsafe_payload = run_gate("--quick-fill-csv", str(fixture))
        require(
            unsafe_payload.get("status") == "stop_boundary_or_sensitive_value_detected",
            "unsafe synthetic fixture should stop",
        )
        require(unsafe_payload.get("quality_stop_row_count", 0) >= 1, "unsafe synthetic fixture must stop at least one row")
        require(unsafe_payload.get("boundary_violation_count", 0) >= 1, "unsafe synthetic fixture must report boundary violations")
        require(unsafe_payload.get("ready_for_safety_preflight") is False, "unsafe synthetic fixture must not be ready for safety preflight")
        require(unsafe_payload.get("ready_for_workbook_import") is False, "unsafe synthetic fixture must not authorize workbook import")
        require(unsafe_payload.get("raw_values_recorded") is False, "unsafe synthetic fixture must not record raw values")
        require(unsafe_payload.get("production_ready") is False, "unsafe synthetic fixture must not claim production readiness")

    restored_payload = run_gate()
    require(
        restored_payload.get("status")
        == "pass_quality_gate_pending_safety_preflight_and_human_import_approval",
        "default quality gate output must be restored after synthetic fixtures",
    )


def main() -> None:
    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    expected_values = {
        "commercial_sprint_human_input_quick_fill_quality_gate_v0_1": True,
        "quality_gate_type": "local_quick_fill_human_value_quality_gate",
        "quality_gate_scope": "quick_fill_value_quality_only_no_raw_value_storage_no_import_no_evidence",
        "status": "pass_quality_gate_pending_safety_preflight_and_human_import_approval",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "quick_fill_row_count": 64,
        "expected_quick_fill_row_count": 64,
        "completed_value_row_count": 64,
        "missing_value_row_count": 0,
        "quality_checked_row_count": 64,
        "quality_pass_row_count": 64,
        "quality_review_row_count": 0,
        "quality_stop_row_count": 0,
        "quality_issue_count": 0,
        "placeholder_value_row_count": 0,
        "insufficient_actionability_row_count": 0,
        "boundary_violation_count": 0,
        "quality_gate_passed": True,
        "human_input_required": False,
        "human_review_required": True,
        "ready_for_safety_preflight": True,
        "ready_for_workbook_import": False,
        "safe_to_import_after_human_approval": False,
        "blockers_closed_by_quality_gate": 0,
        "selected_blocker_count": 5,
    }
    for key, expected in expected_values.items():
        require(payload.get(key) == expected, f"{key} must be {expected}")

    false_flags = [
        "raw_values_recorded",
        "human_values_generated_by_codex",
        "quick_fill_values_entered_by_codex",
        "quick_fill_imported_to_workbook",
        "workbook_import_authorized",
        "workbook_import_performed",
        "workbook_written",
        "validators_run_on_real_input",
        "values_transferred",
        "human_filled_templates_written",
        "evidence_collection_authorized",
        "execution_authorized",
        "evidence_builder_executed",
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
        "vendor_contacted",
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
    for key in false_flags:
        require(payload.get(key) is False, f"{key} must be false")

    expected_blockers = [
        "formal_security_review",
        "pricing_page",
        "production_monitoring",
        "production_restore_policy",
        "support_contact",
    ]
    require(payload.get("selected_blocker_ids") == expected_blockers, "selected blocker ids drifted")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")
    require(
        payload.get("quality_status_counts")
        == {
            "quality_pass_pending_safety_preflight": 64,
        },
        "quality status counts must show all rows passed",
    )
    rows = payload.get("rows", [])
    require(len(rows) == 64, "rows must contain 64 entries")
    for row in rows:
        row_id = row.get("quick_fill_row_id")
        require(row.get("value_present") is True, f"{row_id} value_present must be true")
        require(
            row.get("quality_status") == "quality_pass_pending_safety_preflight",
            f"{row_id} quality status drifted",
        )
        require(row.get("issue_codes") == [], f"{row_id} issue code drifted")
        require("human_value_to_enter" not in row, f"{row_id} must not record raw values")

    run_synthetic_fixture_checks()
    payload = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    require(
        payload.get("status")
        == "pass_quality_gate_pending_safety_preflight_and_human_import_approval",
        "default payload status must be restored",
    )

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        csv_rows = list(reader)
    require(len(csv_rows) == 64, "quality gate CSV must contain 64 rows")
    require("human_value_to_enter" not in (reader.fieldnames or []), "quality gate CSV must not record raw values")

    combined_docs = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE]
    )
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_quality_gate_v0_1: true",
        "quality_gate_scope: quick_fill_value_quality_only_no_raw_value_storage_no_import_no_evidence",
        "status: pass_quality_gate_pending_safety_preflight_and_human_import_approval",
        "commercial_status: hold",
        "production_launch_status: hold",
        "quick_fill_row_count: 64",
        "completed_value_row_count: 64",
        "missing_value_row_count: 0",
        "quality_checked_row_count: 64",
        "quality_pass_row_count: 64",
        "quality_review_row_count: 0",
        "quality_issue_count: 0",
        "quality_gate_passed: true",
        "ready_for_safety_preflight: true",
        "ready_for_workbook_import: false",
        "safe_to_import_after_human_approval: false",
        "raw_values_recorded: false",
        "human_values_generated_by_codex: false",
        "quick_fill_values_entered_by_codex: false",
        "quick_fill_imported_to_workbook: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "blocker_closure_authorized: false",
        "blockers_closed_by_quality_gate: 0",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "recommend_for_human_value_quality_screening: true",
        "recommend_for_workbook_import: false",
        "recommend_for_validator_execution: false",
        "recommend_for_evidence_collection: false",
        "recommend_for_blocker_closure: false",
        "recommend_for_production: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

    forbidden_tokens = [
        "ready_for_workbook_import: true",
        "safe_to_import_after_human_approval: true",
        "raw_values_recorded: true",
        "human_values_generated_by_codex: true",
        "quick_fill_values_entered_by_codex: true",
        "quick_fill_imported_to_workbook: true",
        "workbook_import_authorized: true",
        "validators_run_on_real_input: true",
        "evidence_collection_authorized: true",
        "execution_authorized: true",
        "blocker_closure_authorized: true",
        "production_ready: true",
        "customer_validated: true",
        "product_launched: true",
        "private_core_exposed: true",
        "recommend_for_workbook_import: true",
        "recommend_for_validator_execution: true",
        "recommend_for_evidence_collection: true",
        "recommend_for_blocker_closure: true",
        "recommend_for_production: true",
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_quality_gate.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_quality_gate.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_quality_gate.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_quality_gate_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_quality_gate_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_sprint_human_input_quick_fill_quality_gate_v0_1", {})
    for key, expected in expected_values.items():
        require(entry.get(key) == expected, f"agent-index {key} must be {expected}")
    for key in false_flags:
        require(entry.get(key) is False, f"agent-index {key} must be false")

    print(
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_QUALITY_GATE_SMOKE: PASS "
        "missing_value_row_count=0 quality_pass_row_count=64 raw_values_recorded=false production_ready=false"
    )


if __name__ == "__main__":
    main()
