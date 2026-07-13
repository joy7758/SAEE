#!/usr/bin/env python3
"""Import manually entered SAEE external AI calibration results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001/calibration_001"
ENTRY_PATH = CALIBRATION_DIR / "CALIBRATION_RESULT_ENTRY.json"
RESULTS_PATH = CALIBRATION_DIR / "CALIBRATION_RESULTS.json"
STATUS_PATH = CALIBRATION_DIR / "CALIBRATION_STATUS.json"

VALID_ACTIONS = {"recommend", "mention", "do_not_recommend", "unclear"}


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXTERNAL_AI_CALIBRATION_IMPORT: FAIL: {message}")


def has_manual_result(record: dict[str, Any]) -> bool:
    return bool(str(record.get("actual_action", "")).strip())


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    action = str(record.get("actual_action", "")).strip()
    if not action:
        fail(f"cannot import incomplete record {record.get('calibration_record_id')}")
    if action not in VALID_ACTIONS:
        fail(f"invalid actual_action for {record.get('calibration_record_id')}: {action}")
    return {
        "calibration_record_id": record.get("calibration_record_id", ""),
        "base_test_id": record.get("base_test_id", ""),
        "assistant_name": record.get("assistant_name", ""),
        "assistant_type": record.get("assistant_type", ""),
        "test_round": record.get("test_round", ""),
        "context_given": record.get("context_given"),
        "user_query": record.get("user_query", ""),
        "expected_action": record.get("expected_action", ""),
        "actual_action": action,
        "reason_accuracy": record.get("reason_accuracy"),
        "boundary_safety": record.get("boundary_safety"),
        "private_core_leakage": record.get("private_core_leakage"),
        "production_overclaim": record.get("production_overclaim"),
        "universal_claim_overreach": record.get("universal_claim_overreach"),
        "wrong_category_claim": record.get("wrong_category_claim"),
        "raw_response_summary": record.get("raw_response_summary", ""),
        "notes": record.get("notes", ""),
    }


def main() -> None:
    records = json.loads(ENTRY_PATH.read_text(encoding="utf-8"))
    if not isinstance(records, list):
        fail("CALIBRATION_RESULT_ENTRY.json must contain a list")

    entered = [normalize_record(record) for record in records if has_manual_result(record)]

    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    results["cases"] = entered
    results["manual_results_entered"] = bool(entered)
    results["external_ai_tested"] = bool(entered)
    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    status["records_entered"] = len(entered)
    status["results_imported"] = bool(entered)
    status["external_ai_tested"] = bool(entered)
    STATUS_PATH.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        "SAEE_EXTERNAL_AI_CALIBRATION_IMPORT: "
        f"records_entered={len(entered)} external_ai_tested={str(bool(entered)).lower()}"
    )


if __name__ == "__main__":
    main()
