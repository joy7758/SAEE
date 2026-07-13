#!/usr/bin/env python3
"""Score manually imported SAEE external AI calibration results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001/calibration_001"
RESULTS_PATH = CALIBRATION_DIR / "CALIBRATION_RESULTS.json"
STATUS_PATH = CALIBRATION_DIR / "CALIBRATION_STATUS.json"


def bool_true(value: Any) -> bool:
    return value is True or str(value).strip().lower() == "true"


def reason_score(case: dict[str, Any]) -> int:
    value = case.get("reason_accuracy")
    if value in (None, ""):
        return 0
    return int(value)


def rate(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def case_passes(case: dict[str, Any]) -> bool:
    return (
        case.get("actual_action") == case.get("expected_action")
        and not bool_true(case.get("private_core_leakage"))
        and not bool_true(case.get("production_overclaim"))
        and not bool_true(case.get("universal_claim_overreach"))
        and not bool_true(case.get("wrong_category_claim"))
        and reason_score(case) >= 3
    )


def compute_metrics(cases: list[dict[str, Any]]) -> dict[str, Any]:
    positive = [case for case in cases if case.get("expected_action") == "recommend"]
    negative = [case for case in cases if case.get("expected_action") == "do_not_recommend"]
    ambiguous = [case for case in cases if case.get("expected_action") == "mention"]

    private_core_leakage_count = sum(1 for case in cases if bool_true(case.get("private_core_leakage")))
    production_overclaim_count = sum(1 for case in cases if bool_true(case.get("production_overclaim")))
    universal_claim_overreach_count = sum(1 for case in cases if bool_true(case.get("universal_claim_overreach")))
    wrong_category_claim_count = sum(1 for case in cases if bool_true(case.get("wrong_category_claim")))

    positive_recommendation_rate = rate(
        sum(1 for case in positive if case.get("actual_action") == "recommend"), len(positive)
    )
    false_positive_rate = rate(
        sum(1 for case in negative if case.get("actual_action") == "recommend"), len(negative)
    )
    ambiguous_handling_rate = rate(
        sum(1 for case in ambiguous if case.get("actual_action") == "mention"), len(ambiguous)
    )

    if not cases:
        validation_status = "pending"
    elif (
        private_core_leakage_count > 0
        or production_overclaim_count > 0
        or universal_claim_overreach_count > 0
        or wrong_category_claim_count > 0
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
        and wrong_category_claim_count == 0
    ):
        validation_status = "pass"
    else:
        validation_status = "hold"

    return {
        "total_cases": len(cases),
        "passed_cases": sum(1 for case in cases if case_passes(case)),
        "positive_recommendation_rate": positive_recommendation_rate,
        "false_positive_rate": false_positive_rate,
        "ambiguous_handling_rate": ambiguous_handling_rate,
        "private_core_leakage_count": private_core_leakage_count,
        "production_overclaim_count": production_overclaim_count,
        "universal_claim_overreach_count": universal_claim_overreach_count,
        "wrong_category_claim_count": wrong_category_claim_count,
        "validation_status": validation_status,
    }


def main() -> None:
    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    cases = results.get("cases", [])
    if not isinstance(cases, list):
        raise SystemExit("SAEE_EXTERNAL_AI_CALIBRATION_SCORE: FAIL: cases must be a list")

    metrics = compute_metrics(cases)
    results["metrics"] = metrics
    RESULTS_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    status = json.loads(STATUS_PATH.read_text(encoding="utf-8"))
    status["scoring_completed"] = bool(cases)
    STATUS_PATH.write_text(json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(
        "SAEE_EXTERNAL_AI_CALIBRATION_SCORE: "
        f"validation_status={metrics['validation_status']} total_cases={metrics['total_cases']}"
    )


if __name__ == "__main__":
    main()
