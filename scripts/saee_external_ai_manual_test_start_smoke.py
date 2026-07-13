#!/usr/bin/env python3
"""Smoke-check SAEE external AI manual test session start state."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001"
SESSION_PATH = RUN_DIR / "ACTIVE_TEST_SESSION.json"
RUN_STATUS_PATH = RUN_DIR / "run_status.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXTERNAL_AI_MANUAL_TEST_START_SMOKE: FAIL {message}")


def main() -> None:
    if not SESSION_PATH.is_file():
        fail("ACTIVE_TEST_SESSION.json is missing")
    if not RUN_STATUS_PATH.is_file():
        fail("run_status.json is missing")

    session = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
    expected_session = {
        "session_state": "manual_test_started",
        "manual_test_started": True,
        "manual_test_completed": False,
        "external_ai_tested": False,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
        "records_entered": 0,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    bad_session = [key for key, value in expected_session.items() if session.get(key) != value]
    if bad_session:
        fail("ACTIVE_TEST_SESSION.json flags drifted: " + ", ".join(bad_session))

    if session.get("total_planned_records") != 120:
        fail("ACTIVE_TEST_SESSION.json total_planned_records must be 120")
    if len(session.get("assistant_targets", [])) != 3:
        fail("ACTIVE_TEST_SESSION.json must list 3 assistant targets")
    if session.get("rounds") != ["no_context", "with_context"]:
        fail("ACTIVE_TEST_SESSION.json rounds must be no_context and with_context")

    status = json.loads(RUN_STATUS_PATH.read_text(encoding="utf-8"))
    expected_status = {
        "manual_test_prepared": True,
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
    bad_status = [key for key, value in expected_status.items() if status.get(key) != value]
    if bad_status:
        fail("run_status.json flags drifted: " + ", ".join(bad_status))

    print("SAEE_EXTERNAL_AI_MANUAL_TEST_START_SMOKE: PASS")


if __name__ == "__main__":
    main()
