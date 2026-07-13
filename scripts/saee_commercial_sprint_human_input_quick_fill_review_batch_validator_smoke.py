#!/usr/bin/env python3
"""Smoke check for the quick-fill review batch validator."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_validation_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_RECOMMENDATION_GATE.md"
)

SAFE_VALUES = {
    "QF-001": "support operations owner assigned and approved reference",
    "QF-002": "internal support owner contact reference approved by human",
    "QF-003": "2026-07-15",
    "QF-004": "scope acknowledged by support owner on 2026-07-06",
    "QF-005": "approval reference support-contact-review-2026-07-06",
    "QF-006": "human reviewer reference approved",
    "QF-007": "2026-07-06",
    "QF-008": "support channel decision approved with internal reference",
    "QF-009": "decision summary approved: support path held pending publication",
    "QF-010": "evidence reference path defined in support contact review",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_fixture(path: Path, unsafe: bool = False) -> None:
    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
        fieldnames = handle.seek(0) or csv.DictReader(handle).fieldnames
    if not fieldnames:
        raise SystemExit("source CSV has no fields")
    for row in rows:
        row_id = row.get("quick_fill_row_id", "")
        if row_id in SAFE_VALUES:
            row["human_value_to_enter"] = SAFE_VALUES[row_id]
            row["notes_for_human"] = "synthetic fixture only; not real commercial evidence"
    if unsafe:
        rows[0]["human_value_to_enter"] = "production_ready=true and private core exposed"
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_runner(csv_path: Path | None = None) -> dict:
    cmd = [sys.executable, str(RUNNER)]
    if csv_path is not None:
        cmd.extend(["--quick-fill-csv", str(csv_path)])
    subprocess.run(cmd, cwd=ROOT, check=True)
    return read_json(OUT_JSON)


def require_common_false_flags(payload: dict) -> None:
    for key in [
        "raw_values_recorded",
        "human_values_generated_by_codex",
        "quick_fill_values_entered_by_codex",
        "source_quick_fill_packet_modified",
        "ready_for_safety_preflight",
        "ready_for_workbook_import",
        "workbook_import_authorized",
        "validators_run_on_real_input",
        "evidence_collection_authorized",
        "execution_authorized",
        "blocker_closure_authorized",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "private_core_exposed",
        "product_launched",
        "production_ready",
        "customer_validated",
        "customer_contacted",
        "external_calls_made",
        "external_ai_assistant_tested",
    ]:
        require(payload.get(key) is False, f"{key} must be false")


def main() -> int:
    default_payload = run_runner()
    expected = {
        "commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1": True,
        "validator_type": "selected_quick_fill_review_batch_validator",
        "validator_scope": "selected_batch_value_presence_and_boundary_only_no_raw_value_storage_no_import",
        "status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "source_quick_fill_row_count": 64,
        "review_batch_size": 10,
        "selected_review_row_count": 0,
        "completed_batch_value_row_count": 0,
        "missing_batch_value_row_count": 0,
        "batch_quality_pass_row_count": 0,
        "batch_quality_review_row_count": 0,
        "batch_quality_stop_row_count": 0,
        "batch_quality_issue_count": 0,
        "batch_validator_passed": False,
        "review_batch_superseded": True,
        "ready_for_workbook_import_approval_review": True,
        "full_quick_fill_completed_value_row_count": 64,
        "full_quick_fill_missing_value_row_count": 0,
        "human_input_required": False,
        "human_review_required": True,
        "boundary_violation_count": 0,
        "blockers_closed_by_batch_validator": 0,
    }
    for key, value in expected.items():
        require(default_payload.get(key) == value, f"default {key} must be {value}")
    require(default_payload.get("boundary_violations") == [], "default boundary violations must be empty")
    require_common_false_flags(default_payload)

    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing batch validator file: {path}")

    rows = default_payload.get("validation_rows", [])
    require(len(rows) == 0, "default validation rows must be empty after review batch superseded")
    for row in rows:
        row_id = row.get("quick_fill_row_id")
        require("human_value_to_enter" not in row, f"{row_id} must not expose raw value")
        require(row.get("value_present") is False, f"{row_id} must be missing by default")
        require(
            row.get("batch_validation_status") == "missing_batch_human_value",
            f"{row_id} default status must be missing",
        )

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        csv_rows = list(reader)
    require(len(csv_rows) == 0, "batch validator CSV must contain 0 rows after review batch superseded")
    require("human_value_to_enter" not in (reader.fieldnames or []), "validator CSV must not record raw values")

    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    require(
        sum(1 for row in source_rows if row.get("human_value_to_enter", "").strip()) == 64,
        "source quick-fill CSV must contain 64 human-confirmed values",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1: true",
        "validator_scope: selected_batch_value_presence_and_boundary_only_no_raw_value_storage_no_import",
        "status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "selected_review_row_count: 0",
        "completed_batch_value_row_count: 0",
        "missing_batch_value_row_count: 0",
        "batch_validator_passed: false",
        "review_batch_superseded: true",
        "ready_for_workbook_import_approval_review: true",
        "full_quick_fill_completed_value_row_count: 64",
        "full_quick_fill_missing_value_row_count: 0",
        "blockers_closed_by_batch_validator: 0",
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
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR: PASS",
    ]
    for token in required_tokens:
        require(token in combined, "missing documentation token: " + token)

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found = [token for token in forbidden_runner_tokens if token in runner_text]
    require(not found, "batch validator runner suggests external/process access: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_validation.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_validation.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_validation.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_validation_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_validator_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms.txt missing batch validator paths: " + ", ".join(missing))

    for required_file in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        require(
            "commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1" in text,
            f"{required_file} missing batch validator token",
        )

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    require(
        "check-commercial-sprint-human-input-quick-fill-review-batch-validator" in makefile,
        "Makefile missing batch validator check target",
    )

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_sprint_human_input_quick_fill_review_batch_validator_v0_1", {})
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index batch validator {key} must be {value}")

    print("SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_VALIDATOR_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
