#!/usr/bin/env python3
"""Smoke check for the commercial sprint quick-fill review batch."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_RECOMMENDATION_GATE.md"
)
QUICK_FILL_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)

    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing quick-fill review batch file: {path}")

    payload = read_json(OUT_JSON)
    expected = {
        "commercial_sprint_human_input_quick_fill_review_batch_v0_1": True,
        "review_batch_type": "bounded_manual_quick_fill_review_batch",
        "review_batch_scope": "human_entry_batch_only_no_values_no_import_no_execution",
        "status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "quick_fill_row_count": 64,
        "expected_quick_fill_row_count": 64,
        "missing_value_row_count": 0,
        "completed_value_row_count": 64,
        "review_batch_size": 10,
        "selected_review_row_count": 0,
        "remaining_missing_after_selected_batch": 0,
        "human_input_required": False,
        "human_review_required": True,
        "quality_gate_passed": True,
        "review_batch_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "blockers_closed_by_review_batch": 0,
        "boundary_violation_count": 0,
        "raw_values_recorded": False,
        "human_values_generated_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "source_quick_fill_packet_modified": False,
        "ready_for_safety_preflight": False,
        "ready_for_workbook_import": False,
        "safe_to_import_after_human_approval": False,
        "workbook_import_authorized": False,
        "workbook_import_performed": False,
        "validators_run_on_real_input": False,
        "evidence_collection_authorized": False,
        "execution_authorized": False,
        "blocker_closure_authorized": False,
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
        "external_ai_assistant_tested": False,
        "production_ready_claim": False,
        "customer_validation_claim": False,
    }
    for key, value in expected.items():
        require(payload.get(key) == value, f"{key} must be {value}")
    require(payload.get("boundary_violations") == [], "boundary violations must be empty")

    rows = payload.get("selected_rows", [])
    require(len(rows) == 0, "selected_rows must be empty after full source completion")
    for row in rows:
        row_id = row.get("quick_fill_row_id")
        require("human_value_to_enter" not in row, f"{row_id} must not expose human_value_to_enter")
        require(row.get("source_field_to_fill") == "human_value_to_enter", f"{row_id} field target drifted")
        require(row.get("source_value_currently_blank") is True, f"{row_id} must be blank source value")
        require(row.get("codex_generated_value") is False, f"{row_id} must not be Codex generated")
        require(row.get("source_quick_fill_packet_modified") is False, f"{row_id} must not modify source packet")
        require(row.get("workbook_import_performed") is False, f"{row_id} must not import workbook")

    with OUT_CSV.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        csv_rows = list(reader)
    require(len(csv_rows) == 0, "review batch CSV must contain 0 rows after full source completion")
    require("human_value_to_enter" not in (reader.fieldnames or []), "review batch CSV must not record raw values")

    with QUICK_FILL_CSV.open(encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    require(len(source_rows) == 64, "source quick-fill CSV must still contain 64 rows")
    require(
        sum(1 for row in source_rows if row.get("human_value_to_enter", "").strip()) == 64,
        "source quick-fill CSV must contain 64 human-confirmed values",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_review_batch_v0_1: true",
        "review_batch_scope: human_entry_batch_only_no_values_no_import_no_execution",
        "status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "missing_value_row_count: 0",
        "completed_value_row_count: 64",
        "selected_review_row_count: 0",
        "remaining_missing_after_selected_batch: 0",
        "quality_gate_passed: true",
        "review_batch_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "blockers_closed_by_review_batch: 0",
        "raw_values_recorded: false",
        "human_values_generated_by_codex: false",
        "quick_fill_values_entered_by_codex: false",
        "source_quick_fill_packet_modified: false",
        "ready_for_workbook_import: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH: PASS",
    ]
    for token in required_tokens:
        require(token in combined, "missing documentation token: " + token)

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found = [token for token in forbidden_runner_tokens if token in runner_text]
    require(not found, "review batch runner suggests external/process access: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms.txt missing review batch paths: " + ", ".join(missing))

    for required_file in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        require(
            "commercial_sprint_human_input_quick_fill_review_batch_v0_1" in text,
            f"{required_file} missing review batch token",
        )

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    require(
        "check-commercial-sprint-human-input-quick-fill-review-batch" in makefile,
        "Makefile missing review batch check target",
    )

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_sprint_human_input_quick_fill_review_batch_v0_1", {})
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index review batch {key} must be {value}")

    print("SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
