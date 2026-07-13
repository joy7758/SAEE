#!/usr/bin/env python3
"""Validate SAEE external AI assistant manual run package."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001"

REQUIRED_FILES = [
    "README.md",
    "TESTER_CHECKLIST.md",
    "ASSISTANT_TARGETS.md",
    "no_context_prompt_packets.md",
    "with_context_prompt_packets.md",
    "manual_results_entry.csv",
    "manual_results_entry.json",
    "result_entry_instructions.md",
    "run_status.json",
    "run_summary.md",
    "ACTIVE_TEST_SESSION.md",
    "ACTIVE_TEST_SESSION.json",
    "HUMAN_EXECUTION_STEPS.md",
    "RECORDING_GUIDE.md",
    "POST_TEST_IMPORT_GUIDE.md",
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
    raise SystemExit(f"SAEE_EXTERNAL_AI_MANUAL_RUN_SMOKE: FAIL: {message}")


def read_run(relpath: str) -> str:
    return (RUN_DIR / relpath).read_text(encoding="utf-8")


def main() -> None:
    if not RUN_DIR.is_dir():
        fail("manual run directory is missing")

    missing = [path for path in REQUIRED_FILES if not (RUN_DIR / path).is_file()]
    if missing:
        fail("missing manual run files: " + ", ".join(missing))

    json_records = json.loads(read_run("manual_results_entry.json"))
    if not isinstance(json_records, list) or len(json_records) != 120:
        fail("manual_results_entry.json must contain 120 planned records")

    with (RUN_DIR / "manual_results_entry.csv").open(encoding="utf-8", newline="") as fp:
        csv_records = list(csv.DictReader(fp))
    if len(csv_records) != 120:
        fail("manual_results_entry.csv must contain 120 planned rows")

    status = json.loads(read_run("run_status.json"))
    required_flags = {
        "manual_test_prepared": True,
        "manual_test_started": True,
        "manual_test_completed": False,
        "external_ai_tested": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    bad_flags = [flag for flag, expected in required_flags.items() if status.get(flag) is not expected]
    if bad_flags:
        fail("run_status.json flags drifted: " + ", ".join(bad_flags))
    if status.get("total_planned_records") != 120:
        fail("run_status.json total_planned_records must be 120")
    if status.get("records_entered") != 0:
        fail("run_status.json records_entered must remain 0 before result entry")

    session = json.loads(read_run("ACTIVE_TEST_SESSION.json"))
    if session.get("session_state") != "manual_test_started":
        fail("ACTIVE_TEST_SESSION.json session_state must be manual_test_started")
    if session.get("external_ai_tested") is not False:
        fail("ACTIVE_TEST_SESSION.json external_ai_tested must remain false")
    if session.get("external_calls_made_by_codex") is not False:
        fail("ACTIVE_TEST_SESSION.json external_calls_made_by_codex must remain false")
    if session.get("browser_automation_used") is not False:
        fail("ACTIVE_TEST_SESSION.json browser_automation_used must remain false")
    if session.get("records_entered") != 0:
        fail("ACTIVE_TEST_SESSION.json records_entered must remain 0")

    combined_public = "\n".join(read_run(path) for path in REQUIRED_FILES)
    private_hits = [term for term in FORBIDDEN_PRIVATE_TERMS if term in combined_public]
    if private_hits:
        fail("private implementation terms leaked: " + ", ".join(private_hits))

    script_text = "\n".join(
        (ROOT / path).read_text(encoding="utf-8")
        for path in [
            "scripts/prepare_external_ai_manual_run.py",
            "scripts/import_external_ai_manual_results.py",
            "scripts/score_external_ai_manual_run.py",
        ]
    )
    automation_hits = [term for term in FORBIDDEN_AUTOMATION_TERMS if term in script_text]
    if automation_hits:
        fail("external automation terms found: " + ", ".join(automation_hits))

    print(
        "SAEE_EXTERNAL_AI_MANUAL_RUN_SMOKE: PASS "
        "run_id=run_001 planned_records=120 external_ai_tested=false "
        "manual_test_started=true manual_test_completed=false"
    )


if __name__ == "__main__":
    main()
