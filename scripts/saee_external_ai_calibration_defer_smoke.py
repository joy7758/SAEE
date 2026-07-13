#!/usr/bin/env python3
"""Validate the historical defer record after calibration was later reopened."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001/calibration_001"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXTERNAL_AI_CALIBRATION_DEFER_SMOKE: FAIL: {message}")


def load_json(relpath: str) -> dict:
    return json.loads((CALIBRATION_DIR / relpath).read_text(encoding="utf-8"))


def require_false_flags(data: dict, flags: list[str], source: str) -> None:
    bad = [flag for flag in flags if data.get(flag) is not False]
    if bad:
        fail(f"{source} must keep these flags false: {', '.join(bad)}")


def main() -> None:
    record_path = CALIBRATION_DIR / "CALIBRATION_DEFER_RECORD.json"
    if not record_path.is_file():
        fail("CALIBRATION_DEFER_RECORD.json is missing")

    record = load_json("CALIBRATION_DEFER_RECORD.json")
    expected = {
        "new_status": "deferred_by_human_decision",
        "superseded_by_human_results": True,
        "current_status": "completed_with_human_results_hold",
        "manual_external_test_performed": True,
        "records_entered": 6,
        "internal_self_play_status": "pass",
        "external_ai_tested": True,
        "external_validation_claim": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready_claim": False,
        "private_core_exposed": False,
    }
    bad_record = [key for key, value in expected.items() if record.get(key) != value]
    if bad_record:
        fail("CALIBRATION_DEFER_RECORD.json drifted: " + ", ".join(bad_record))

    status = load_json("CALIBRATION_STATUS.json")
    status_expected = {
        "status": "completed_with_human_results_hold",
        "manual_execution_required": False,
        "manual_execution_deferred": False,
        "external_ai_tested": True,
        "records_entered": 6,
        "results_imported": True,
        "scoring_completed": True,
        "external_validation_claim": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    bad_status = [key for key, value in status_expected.items() if status.get(key) != value]
    if bad_status:
        fail("CALIBRATION_STATUS.json defer state drifted: " + ", ".join(bad_status))

    results = load_json("CALIBRATION_RESULTS.json")
    require_false_flags(
        results,
        [
            "external_validation_claim",
            "customer_validated",
            "product_launched",
            "production_ready_claim",
            "private_core_exposed",
            "external_calls_made_by_codex",
            "browser_automation_used",
        ],
        "CALIBRATION_RESULTS.json",
    )
    if results.get("external_ai_tested") is not True:
        fail("CALIBRATION_RESULTS.json external_ai_tested must be true after human import")
    if results.get("manual_results_entered") is not True:
        fail("CALIBRATION_RESULTS.json manual_results_entered must be true after human import")
    if results.get("reopened_by_human_decision") is not True:
        fail("CALIBRATION_RESULTS.json reopened_by_human_decision must be true")
    if results.get("metrics", {}).get("validation_status") != "hold":
        fail("CALIBRATION_RESULTS.json validation_status must be hold")
    if len(results.get("cases", [])) != 6:
        fail("CALIBRATION_RESULTS.json cases must contain 6 imported records")

    self_play = json.loads((ROOT / "agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.json").read_text(encoding="utf-8"))
    if self_play.get("metrics", {}).get("validation_status") != "pass":
        fail("internal self-play status must remain pass")
    if self_play.get("external_ai_tested") is not False:
        fail("internal self-play must not claim external AI testing")

    print("SAEE_EXTERNAL_AI_CALIBRATION_DEFER_SMOKE: PASS")


if __name__ == "__main__":
    main()
