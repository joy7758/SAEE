#!/usr/bin/env python3
"""Start the SAEE external AI manual test session without external calls."""

from __future__ import annotations

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
    "manual_results_entry.json",
    "manual_results_entry.csv",
    "run_status.json",
]


def fail(message: str) -> None:
    active_md = RUN_DIR / "ACTIVE_TEST_SESSION.md"
    if RUN_DIR.exists():
        active_md.write_text(
            "# Active Test Session\n\n"
            "session_state: start_failed\n\n"
            f"failure_note: {message}\n\n"
            "No external AI assistant was tested by Codex.\n",
            encoding="utf-8",
        )
    raise SystemExit(f"SAEE_EXTERNAL_AI_MANUAL_TEST_SESSION_START: FAIL {message}")


def build_session() -> dict:
    return {
        "run_id": "run_001",
        "session_state": "manual_test_started",
        "manual_test_started": True,
        "manual_test_completed": False,
        "external_ai_tested": False,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
        "total_planned_records": 120,
        "records_entered": 0,
        "assistant_targets": [
            {
                "assistant_label": "Assistant A",
                "assistant_type": "general_ai_assistant",
                "manual_execution_required": True,
            },
            {
                "assistant_label": "Assistant B",
                "assistant_type": "coding_research_assistant",
                "manual_execution_required": True,
            },
            {
                "assistant_label": "Assistant C",
                "assistant_type": "enterprise_search_assistant",
                "manual_execution_required": True,
            },
        ],
        "rounds": [
            "no_context",
            "with_context",
        ],
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
        "next_human_action": "manually paste prompts into external AI assistants and record results",
    }


def build_session_markdown(session: dict) -> str:
    return """# Active Test Session

session_state: manual_test_started

## What Has Started

The SAEE external AI assistant recommendation test session has been opened for
manual execution. The prompt packets and recording worksheets are ready for a
human tester.

## What Has Not Happened

- Codex has not tested any external AI assistant.
- Codex has made no external calls.
- Codex has not used browser automation.
- No results have been entered.
- No product has been launched.
- No customer has been contacted.
- No private core has been exposed.
- No production-ready claim has been made.

## Target Assistants

| Assistant | Type | Execution |
| --- | --- | --- |
| Assistant A | general_ai_assistant | Human manual execution required |
| Assistant B | coding_research_assistant | Human manual execution required |
| Assistant C | enterprise_search_assistant | Human manual execution required |

## Test Rounds

1. no-context test
2. with-context test

## Boundary

Codex has not tested any external AI assistant.

Human tester must execute prompts manually.

`external_ai_tested` remains `false` until human-entered actual results are
imported.
"""


def main() -> None:
    if not RUN_DIR.is_dir():
        raise SystemExit("SAEE_EXTERNAL_AI_MANUAL_TEST_SESSION_START: FAIL manual run directory missing")

    missing = [path for path in REQUIRED_FILES if not (RUN_DIR / path).is_file()]
    if missing:
        fail("missing required files: " + ", ".join(missing))

    manual_results = json.loads((RUN_DIR / "manual_results_entry.json").read_text(encoding="utf-8"))
    if len(manual_results) != 120:
        fail("manual_results_entry.json must contain 120 records")
    if any(record.get("actual_action") for record in manual_results):
        fail("manual_results_entry.json already contains actual results")

    run_status_path = RUN_DIR / "run_status.json"
    run_status = json.loads(run_status_path.read_text(encoding="utf-8"))
    run_status.update(
        {
            "manual_test_started": True,
            "manual_test_completed": False,
            "external_ai_tested": False,
            "records_entered": 0,
            "scoring_completed": False,
            "product_launched": False,
            "customer_contacted": False,
            "private_core_exposed": False,
            "production_ready_claim": False,
        }
    )
    run_status_path.write_text(json.dumps(run_status, indent=2) + "\n", encoding="utf-8")

    session = build_session()
    (RUN_DIR / "ACTIVE_TEST_SESSION.json").write_text(
        json.dumps(session, indent=2) + "\n",
        encoding="utf-8",
    )
    (RUN_DIR / "ACTIVE_TEST_SESSION.md").write_text(
        build_session_markdown(session),
        encoding="utf-8",
    )

    print("SAEE_EXTERNAL_AI_MANUAL_TEST_SESSION_STARTED")


if __name__ == "__main__":
    main()
