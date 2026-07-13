#!/usr/bin/env python3
"""Import manually entered external AI assistant recommendation results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001"
ENTRY_PATH = RUN_DIR / "manual_results_entry.json"
RUN_STATUS_PATH = RUN_DIR / "run_status.json"
EXTERNAL_RESULTS_PATH = ROOT / "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json"

VALID_ACTIONS = {"recommend", "mention", "do_not_recommend", "unclear"}


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXTERNAL_AI_MANUAL_IMPORT: FAIL: {message}")


def has_manual_result(record: dict[str, Any]) -> bool:
    return bool(str(record.get("actual_action", "")).strip())


def normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    action = str(record.get("actual_action", "")).strip()
    if action and action not in VALID_ACTIONS:
        fail(f"invalid actual_action for {record.get('test_id')}: {action}")
    if not action:
        fail(f"cannot import incomplete record {record.get('test_id')}")
    return {
        "test_id": record.get("test_id", ""),
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
        fail("manual_results_entry.json must contain a list")

    entered = [normalize_record(record) for record in records if has_manual_result(record)]

    external_results = json.loads(EXTERNAL_RESULTS_PATH.read_text(encoding="utf-8"))
    external_results["cases"] = entered
    external_results["results_entered"] = bool(entered)
    external_results["external_ai_tested"] = bool(entered)

    EXTERNAL_RESULTS_PATH.write_text(json.dumps(external_results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    run_status = json.loads(RUN_STATUS_PATH.read_text(encoding="utf-8"))
    run_status["manual_test_started"] = bool(entered)
    run_status["external_ai_tested"] = bool(entered)
    run_status["records_entered"] = len(entered)
    run_status["manual_test_completed"] = len(entered) == run_status.get("total_planned_records")
    RUN_STATUS_PATH.write_text(json.dumps(run_status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        "SAEE_EXTERNAL_AI_MANUAL_IMPORT: "
        f"records_entered={len(entered)} external_ai_tested={str(bool(entered)).lower()}"
    )


if __name__ == "__main__":
    main()
