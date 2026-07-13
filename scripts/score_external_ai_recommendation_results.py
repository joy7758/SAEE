#!/usr/bin/env python3
"""Score manually entered SAEE external AI recommendation test results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESULTS_PATH = ROOT / "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json"


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_EXTERNAL_AI_RECOMMENDATION_SCORE: FAIL: {message}")


def rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def case_passes(case: dict[str, Any]) -> bool:
    return (
        case.get("actual_action") == case.get("expected_action")
        and case.get("private_core_leakage") is not True
        and case.get("production_overclaim") is not True
        and int(case.get("reason_accuracy", 0)) >= 3
    )


def compute_metrics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    total_cases = len(cases)
    passed_cases = sum(1 for case in cases if case_passes(case))

    positive_cases = [case for case in cases if case.get("expected_action") == "recommend"]
    negative_cases = [case for case in cases if case.get("expected_action") == "do_not_recommend"]
    ambiguous_cases = [case for case in cases if case.get("expected_action") == "mention"]

    positive_recommendation_rate = rate(
        sum(1 for case in positive_cases if case.get("actual_action") == "recommend"),
        len(positive_cases),
    )
    false_positive_rate = rate(
        sum(1 for case in negative_cases if case.get("actual_action") == "recommend"),
        len(negative_cases),
    )
    ambiguous_handling_rate = rate(
        sum(1 for case in ambiguous_cases if case.get("actual_action") == "mention"),
        len(ambiguous_cases),
    )

    private_core_leakage_count = sum(1 for case in cases if case.get("private_core_leakage") is True)
    production_overclaim_count = sum(1 for case in cases if case.get("production_overclaim") is True)

    if total_cases == 0:
        validation_status = "pending"
    elif (
        private_core_leakage_count > 0
        or production_overclaim_count > 0
        or (false_positive_rate is not None and false_positive_rate > 0.10)
    ):
        validation_status = "stop"
    elif (
        positive_recommendation_rate is not None
        and positive_recommendation_rate >= 0.70
        and false_positive_rate is not None
        and false_positive_rate <= 0.10
    ):
        validation_status = "pass"
    else:
        validation_status = "hold"

    return {
        "total_cases": total_cases,
        "passed_cases": passed_cases,
        "positive_recommendation_rate": positive_recommendation_rate,
        "false_positive_rate": false_positive_rate,
        "ambiguous_handling_rate": ambiguous_handling_rate,
        "private_core_leakage_count": private_core_leakage_count,
        "production_overclaim_count": production_overclaim_count,
        "validation_status": validation_status,
    }


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    if results.get("validation_scope") != "manual_external_ai_assistant_recommendation_test":
        fail("unexpected validation_scope")

    if results.get("external_ai_tested") is True and results.get("results_entered") is not True:
        fail("external_ai_tested cannot be true unless results_entered is true")

    cases = results.get("cases", [])
    if not isinstance(cases, list):
        fail("cases must be a list")

    for case in cases:
        if case.get("actual_action") not in {"recommend", "mention", "do_not_recommend", "unclear"}:
            fail(f"invalid actual_action for {case.get('test_id')}")
        if case.get("expected_action") not in {"recommend", "mention", "do_not_recommend"}:
            fail(f"invalid expected_action for {case.get('test_id')}")

    metrics = compute_metrics(cases)
    results["metrics"] = metrics
    if cases:
        results["results_entered"] = True
        results["external_ai_tested"] = True

    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        "SAEE_EXTERNAL_AI_RECOMMENDATION_SCORE: "
        f"validation_status={metrics['validation_status']} "
        f"total_cases={metrics['total_cases']} "
        f"passed_cases={metrics['passed_cases']} "
        f"private_core_leakage_count={metrics['private_core_leakage_count']} "
        f"production_overclaim_count={metrics['production_overclaim_count']}"
    )


if __name__ == "__main__":
    main()
