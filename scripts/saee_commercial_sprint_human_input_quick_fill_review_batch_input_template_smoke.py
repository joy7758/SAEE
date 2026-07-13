#!/usr/bin/env python3
"""Smoke check for the quick-fill review batch input template."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template.py"
SPRINT_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_next_evidence_sprint"
OUT_JSON = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json"
OUT_MD = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.md"
OUT_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template.csv"
OUT_BOUNDARY = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_review_batch_input_template_boundary_audit.md"
TOP_DOC = (
    ROOT
    / "phase_b_product/commercial_readiness/"
    "COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_V0_1.md"
)
GATE = (
    ROOT
    / "docs/strategy/"
    "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_RECOMMENDATION_GATE.md"
)
SOURCE_CSV = SPRINT_DIR / "commercial_sprint_human_input_quick_fill_packet.csv"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    subprocess.run([sys.executable, str(RUNNER)], cwd=ROOT, check=True)

    for path in [OUT_JSON, OUT_MD, OUT_CSV, OUT_BOUNDARY, TOP_DOC, GATE]:
        require(path.exists(), f"missing input template file: {path}")

    payload = read_json(OUT_JSON)
    expected = {
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1": True,
        "template_type": "selected_quick_fill_review_batch_human_input_template",
        "template_scope": "blank_human_entry_template_only_no_values_no_apply_no_import",
        "status": "superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "commercial_status": "hold",
        "production_launch_status": "hold",
        "template_row_count": 0,
        "expected_template_row_count": 10,
        "blank_human_value_row_count": 0,
        "prefilled_human_value_row_count": 0,
        "notes_prefilled_row_count": 0,
        "selected_review_row_count": 0,
        "human_input_required": False,
        "human_review_required": True,
        "input_template_ready": False,
        "blockers_closed_by_input_template": 0,
        "boundary_violation_count": 0,
        "raw_values_recorded": False,
        "human_values_generated_by_codex": False,
        "quick_fill_values_entered_by_codex": False,
        "source_quick_fill_packet_modified": False,
        "batch_values_applied_to_source": False,
        "ready_for_safety_preflight": False,
        "ready_for_workbook_import": False,
        "workbook_import_authorized": False,
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

    rows = payload.get("template_rows", [])
    require(len(rows) == 0, "template_rows must be empty after review batch superseded")
    for row in rows:
        row_id = row.get("quick_fill_row_id")
        require(row.get("human_value_to_enter") == "", f"{row_id} value must be blank")
        require(row.get("notes_for_human") == "", f"{row_id} notes must be blank")
        require(row.get("codex_generated_value") is False, f"{row_id} must not be generated")
        require(row.get("applied_to_source_quick_fill") is False, f"{row_id} must not be applied")

    with OUT_CSV.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        csv_rows = list(reader)
    require(len(csv_rows) == 0, "template CSV must contain 0 rows after review batch superseded")
    require("human_value_to_enter" in (reader.fieldnames or []), "template CSV must expose human_value_to_enter")
    require("notes_for_human" in (reader.fieldnames or []), "template CSV must expose notes_for_human")
    require(all(row.get("human_value_to_enter", "") == "" for row in csv_rows), "template values must be blank")
    require(all(row.get("notes_for_human", "") == "" for row in csv_rows), "template notes must be blank")

    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as handle:
        source_rows = list(csv.DictReader(handle))
    require(len(source_rows) == 64, "source quick-fill CSV must still contain 64 rows")
    require(
        sum(1 for row in source_rows if row.get("human_value_to_enter", "").strip()) == 64,
        "source quick-fill CSV must contain 64 human-confirmed values",
    )

    combined = "\n".join(path.read_text(encoding="utf-8") for path in [OUT_MD, OUT_BOUNDARY, TOP_DOC, GATE])
    required_tokens = [
        "commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1: true",
        "template_scope: blank_human_entry_template_only_no_values_no_apply_no_import",
        "status: superseded_by_full_quick_fill_values_pending_workbook_import_approval",
        "template_row_count: 0",
        "blank_human_value_row_count: 0",
        "prefilled_human_value_row_count: 0",
        "input_template_ready: false",
        "blockers_closed_by_input_template: 0",
        "raw_values_recorded: false",
        "human_values_generated_by_codex: false",
        "quick_fill_values_entered_by_codex: false",
        "source_quick_fill_packet_modified: false",
        "batch_values_applied_to_source: false",
        "ready_for_workbook_import: false",
        "workbook_import_authorized: false",
        "validators_run_on_real_input: false",
        "evidence_collection_authorized: false",
        "execution_authorized: false",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
        "SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE: PASS",
    ]
    for token in required_tokens:
        require(token in combined, "missing documentation token: " + token)

    runner_text = RUNNER.read_text(encoding="utf-8")
    forbidden_runner_tokens = ["requests.", "urllib.", "httpx.", "webbrowser", "subprocess."]
    found = [token for token in forbidden_runner_tokens if token in runner_text]
    require(not found, "input template runner suggests external/process access: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_V0_1.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.local.json",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.md",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template.csv",
        "/phase_b_product/commercial_readiness/commercial_next_evidence_sprint/commercial_sprint_human_input_quick_fill_review_batch_input_template_boundary_audit.md",
        "/docs/strategy/SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_RECOMMENDATION_GATE.md",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template.py",
        "/scripts/saee_commercial_sprint_human_input_quick_fill_review_batch_input_template_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms.txt missing input template paths: " + ", ".join(missing))

    for required_file in ["README.md", "PROJECT_STATUS.md", "ROADMAP.md", "CHANGELOG.md", "agent-readable.md"]:
        text = (ROOT / required_file).read_text(encoding="utf-8")
        require(
            "commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1" in text,
            f"{required_file} missing input template token",
        )

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    require(
        "check-commercial-sprint-human-input-quick-fill-review-batch-input-template" in makefile,
        "Makefile missing input template check target",
    )

    index = read_json(ROOT / "agent-index.json")
    entry = index.get("commercial_sprint_human_input_quick_fill_review_batch_input_template_v0_1", {})
    for key, value in expected.items():
        require(entry.get(key) == value, f"agent-index input template {key} must be {value}")

    print("SAEE_COMMERCIAL_SPRINT_HUMAN_INPUT_QUICK_FILL_REVIEW_BATCH_INPUT_TEMPLATE_SMOKE: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
