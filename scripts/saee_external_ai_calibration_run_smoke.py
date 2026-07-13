#!/usr/bin/env python3
"""Validate SAEE external AI calibration run 001 non-executed state."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001/calibration_001"

REQUIRED_FILES = [
    "CALIBRATION_TEST_PLAN.md",
    "CALIBRATION_PROMPTS_NO_CONTEXT.md",
    "CALIBRATION_PROMPTS_WITH_CONTEXT.md",
    "CALIBRATION_RESULT_ENTRY.json",
    "CALIBRATION_RESULT_ENTRY.csv",
    "CALIBRATION_STATUS.json",
    "CALIBRATION_RECORDING_GUIDE.md",
    "CALIBRATION_IMPORT_AND_SCORE_GUIDE.md",
    "CALIBRATION_RESULTS.json",
    "CALIBRATION_RESULTS.md",
    "CALIBRATION_DEFER_RECORD.json",
    "CALIBRATION_DEFER_RECORD.md",
]

FORBIDDEN_PRIVATE_TERMS = [
    "saee_v1_0/kernel",
    "kernel/runtime.py",
    "fitness_engine",
    "selection_engine",
    "mutation_engine",
    "lineage_engine",
    "runtime_v1_0",
    "private production evaluator",
]

FORBIDDEN_AUTOMATION_TERMS = [
    "requests.post(",
    "requests.get(",
    "urllib.request",
    "http.client",
    "openai.",
    "anthropic.",
    "google.generativeai",
    "webdriver",
    "selenium",
    "fetch(",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "GEMINI_API_KEY",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXTERNAL_AI_CALIBRATION_RUN_SMOKE: FAIL: {message}")


def read_calibration(relpath: str) -> str:
    return (CALIBRATION_DIR / relpath).read_text(encoding="utf-8")


def main() -> None:
    if not CALIBRATION_DIR.is_dir():
        fail("calibration directory missing")

    missing = [path for path in REQUIRED_FILES if not (CALIBRATION_DIR / path).is_file()]
    if missing:
        fail("missing calibration files: " + ", ".join(missing))

    status = json.loads(read_calibration("CALIBRATION_STATUS.json"))
    required_status = {
        "status": "completed_with_human_results_hold",
        "manual_execution_required": False,
        "manual_execution_deferred": False,
        "external_ai_tested": True,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
        "planned_records": 6,
        "records_entered": 6,
        "results_imported": True,
        "scoring_completed": True,
        "external_validation_claim": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    bad_status = [flag for flag, expected in required_status.items() if status.get(flag) != expected]
    if bad_status:
        fail("CALIBRATION_STATUS.json flags drifted: " + ", ".join(bad_status))

    records = json.loads(read_calibration("CALIBRATION_RESULT_ENTRY.json"))
    if not isinstance(records, list) or len(records) != 6:
        fail("CALIBRATION_RESULT_ENTRY.json must contain exactly 6 records")
    if sum(1 for record in records if record.get("test_round") == "no_context") != 3:
        fail("CALIBRATION_RESULT_ENTRY.json must contain 3 no_context records")
    if sum(1 for record in records if record.get("test_round") == "with_context") != 3:
        fail("CALIBRATION_RESULT_ENTRY.json must contain 3 with_context records")
    if any(not record.get("actual_action") for record in records):
        fail("CALIBRATION_RESULT_ENTRY.json must contain actual_action after human entry")

    with (CALIBRATION_DIR / "CALIBRATION_RESULT_ENTRY.csv").open(encoding="utf-8", newline="") as fp:
        csv_records = list(csv.DictReader(fp))
    if len(csv_records) != 6:
        fail("CALIBRATION_RESULT_ENTRY.csv must contain exactly 6 rows")

    results = json.loads(read_calibration("CALIBRATION_RESULTS.json"))
    if results.get("external_ai_tested") is not True:
        fail("CALIBRATION_RESULTS.json external_ai_tested must be true after import")
    if results.get("manual_results_entered") is not True:
        fail("CALIBRATION_RESULTS.json manual_results_entered must be true after import")
    if results.get("external_validation_claim") is not False:
        fail("CALIBRATION_RESULTS.json external_validation_claim must be false")
    if results.get("reopened_by_human_decision") is not True:
        fail("CALIBRATION_RESULTS.json reopened_by_human_decision must be true")
    if results.get("metrics", {}).get("validation_status") != "hold":
        fail("CALIBRATION_RESULTS.json validation_status must be hold")
    if len(results.get("cases", [])) != 6:
        fail("CALIBRATION_RESULTS.json cases must contain 6 imported records")

    defer_record = json.loads(read_calibration("CALIBRATION_DEFER_RECORD.json"))
    if defer_record.get("current_status") != "completed_with_human_results_hold":
        fail("CALIBRATION_DEFER_RECORD.json current_status must be completed_with_human_results_hold")
    if defer_record.get("manual_external_test_performed") is not True:
        fail("CALIBRATION_DEFER_RECORD.json manual_external_test_performed must be true")
    if defer_record.get("internal_self_play_status") != "pass":
        fail("CALIBRATION_DEFER_RECORD.json internal_self_play_status must be pass")

    combined = "\n".join(read_calibration(path) for path in REQUIRED_FILES)
    private_hits = [term for term in FORBIDDEN_PRIVATE_TERMS if term in combined]
    if private_hits:
        fail("private implementation terms leaked: " + ", ".join(private_hits))

    script_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [
            "scripts/prepare_external_ai_calibration_run.py",
            "scripts/import_external_ai_calibration_results.py",
            "scripts/score_external_ai_calibration_results.py",
        ]
    )
    automation_hits = [term for term in FORBIDDEN_AUTOMATION_TERMS if term in script_text]
    if automation_hits:
        fail("external automation terms found: " + ", ".join(automation_hits))

    print("SAEE_EXTERNAL_AI_CALIBRATION_RUN_SMOKE: PASS")


if __name__ == "__main__":
    main()
