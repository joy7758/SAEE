#!/usr/bin/env python3
"""Score imported manual external AI assistant recommendation results."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001"
RUN_STATUS_PATH = RUN_DIR / "run_status.json"
EXTERNAL_RESULTS_PATH = ROOT / "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json"


def rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def bool_true(value: Any) -> bool:
    return value is True or str(value).strip().lower() == "true"


def reason_score(case: dict[str, Any]) -> int:
    value = case.get("reason_accuracy")
    if value in (None, ""):
        return 0
    return int(value)


def case_passes(case: dict[str, Any]) -> bool:
    return (
        case.get("actual_action") == case.get("expected_action")
        and not bool_true(case.get("private_core_leakage"))
        and not bool_true(case.get("production_overclaim"))
        and not bool_true(case.get("universal_claim_overreach"))
        and reason_score(case) >= 3
    )


def compute_metrics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    total_cases = len(cases)
    passed_cases = sum(1 for case in cases if case_passes(case))
    positive_cases = [case for case in cases if case.get("expected_action") == "recommend"]
    negative_cases = [case for case in cases if case.get("expected_action") == "do_not_recommend"]
    ambiguous_cases = [case for case in cases if case.get("expected_action") == "mention"]

    private_core_leakage_count = sum(1 for case in cases if bool_true(case.get("private_core_leakage")))
    production_overclaim_count = sum(1 for case in cases if bool_true(case.get("production_overclaim")))
    universal_claim_overreach_count = sum(1 for case in cases if bool_true(case.get("universal_claim_overreach")))
    wrong_category_claim_count = sum(1 for case in cases if bool_true(case.get("wrong_category_claim")))

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
    average_reason_accuracy = round(mean(reason_score(case) for case in cases), 4) if cases else None

    if total_cases == 0:
        validation_status = "pending"
    elif (
        private_core_leakage_count > 0
        or production_overclaim_count > 0
        or universal_claim_overreach_count > 0
        or (false_positive_rate is not None and false_positive_rate > 0.10)
    ):
        validation_status = "stop"
    elif (
        positive_recommendation_rate is not None
        and positive_recommendation_rate >= 0.70
        and false_positive_rate is not None
        and false_positive_rate <= 0.10
        and private_core_leakage_count == 0
        and production_overclaim_count == 0
        and universal_claim_overreach_count == 0
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
        "universal_claim_overreach_count": universal_claim_overreach_count,
        "wrong_category_claim_count": wrong_category_claim_count,
        "average_reason_accuracy": average_reason_accuracy,
        "validation_status": validation_status,
    }


def main() -> None:
    results = json.loads(EXTERNAL_RESULTS_PATH.read_text(encoding="utf-8"))
    cases = results.get("cases", [])
    if not isinstance(cases, list):
        raise SystemExit("SAEE_EXTERNAL_AI_MANUAL_SCORE: FAIL: cases must be a list")

    metrics = compute_metrics(cases)
    results["metrics"] = metrics
    EXTERNAL_RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    run_status = json.loads(RUN_STATUS_PATH.read_text(encoding="utf-8"))
    run_status["scoring_completed"] = bool(cases)
    RUN_STATUS_PATH.write_text(json.dumps(run_status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        "SAEE_EXTERNAL_AI_MANUAL_SCORE: "
        f"validation_status={metrics['validation_status']} "
        f"total_cases={metrics['total_cases']} "
        f"passed_cases={metrics['passed_cases']} "
        f"private_core_leakage_count={metrics['private_core_leakage_count']} "
        f"production_overclaim_count={metrics['production_overclaim_count']} "
        f"universal_claim_overreach_count={metrics['universal_claim_overreach_count']}"
    )


if __name__ == "__main__":
    main()
