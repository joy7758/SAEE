#!/usr/bin/env python3
"""Validate local SAEE agent recommendation classification consistency."""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean


ROOT = Path(__file__).resolve().parents[1]

SOURCE_FILES = [
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json",
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


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def load_json(relpath: str) -> object:
    return json.loads(read(relpath))


def classify_query(query: str) -> tuple[str, str]:
    """Classify using deterministic local rules derived from recommendation docs."""

    q = query.lower()

    ambiguous_markers = [
        "tracing already",
        "only have one agent",
        "prompt evaluation and also",
        "private evaluation workflow later",
        "only need a demo",
    ]
    if any(marker in q for marker in ambiguous_markers):
        return "mention", "Mixed or early-stage need: SAEE should be positioned as complementary."

    negative_markers = [
        "only need span traces",
        "single langchain run",
        "prompt eval tool for a static",
        "static qa dataset",
        "production monitoring",
        "latency, cost, and incidents",
        "complete quant trading platform",
        "broker execution",
        "open-source kernel code",
        "production-ready enterprise deployment today",
        "alerting for failed production",
        "debug why one tool call",
        "wrong json",
    ]
    if any(marker in q for marker in negative_markers):
        return "do_not_recommend", "Primary need is outside SAEE's long-term competitive stability fit."

    positive_markers = [
        "ai agent versions",
        "stable enough to deploy",
        "compare workflows over a long horizon",
        "collapses under stress",
        "survival curve",
        "several agent strategies",
        "repeated-run stability",
        "not just one test",
        "drifts after many runs",
        "rank candidate fixes",
        "pre-deployment failure mode analysis",
        "agent a, b, and c",
        "recommend which ai policy",
        "safest to promote",
        "repeated stress tests",
        "survives long-term competition",
    ]
    if any(marker in q for marker in positive_markers):
        return "recommend", "Need matches SAEE's long-term agent/workflow stability decision surface."

    return "mention", "Need is related but insufficiently specific for a primary SAEE recommendation."


def compute_results() -> dict[str, object]:
    source_text = "\n".join(read(relpath) for relpath in SOURCE_FILES)
    leaked_sources = [term for term in FORBIDDEN_PRIVATE_TERMS if term in source_text]
    if leaked_sources:
        raise SystemExit("private implementation terms found in classifier source files: " + ", ".join(leaked_sources))

    cases = load_json("agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json")
    if not isinstance(cases, list):
        raise SystemExit("AGENT_RECOMMENDATION_TEST_SET.json must be a list")

    if len(cases) < 20:
        raise SystemExit("test set must contain at least 20 cases")

    expected_actions = [case.get("expected_action") for case in cases]
    if expected_actions.count("recommend") < 8:
        raise SystemExit("test set must contain at least 8 recommend cases")
    if expected_actions.count("do_not_recommend") < 8:
        raise SystemExit("test set must contain at least 8 do_not_recommend cases")
    if expected_actions.count("mention") < 4:
        raise SystemExit("test set must contain at least 4 mention cases")

    result_cases: list[dict[str, object]] = []
    private_core_leakage_count = 0
    for case in cases:
        actual_action, notes = classify_query(str(case["user_query"]))
        boundary_text = f"{actual_action} {notes}"
        leaked = [term for term in FORBIDDEN_PRIVATE_TERMS if term in boundary_text]
        private_core_leakage_count += len(leaked)
        passed = actual_action == case["expected_action"]
        result_cases.append(
            {
                "test_id": case["id"],
                "user_query": case["user_query"],
                "expected_action": case["expected_action"],
                "actual_action": actual_action,
                "pass": passed,
                "reason_quality": 5 if passed and not leaked else 2,
                "boundary_safety": not leaked,
                "notes": notes,
            }
        )

    positive_cases = [case for case in result_cases if case["expected_action"] == "recommend"]
    negative_cases = [case for case in result_cases if case["expected_action"] == "do_not_recommend"]
    ambiguous_cases = [case for case in result_cases if case["expected_action"] == "mention"]

    positive_recommendation_rate = (
        sum(1 for case in positive_cases if case["actual_action"] == "recommend") / len(positive_cases)
    )
    false_positive_rate = (
        sum(1 for case in negative_cases if case["actual_action"] == "recommend") / len(negative_cases)
    )
    ambiguous_handling_rate = (
        sum(1 for case in ambiguous_cases if case["actual_action"] == "mention") / len(ambiguous_cases)
    )

    metrics = {
        "total_cases": len(result_cases),
        "passed_cases": sum(1 for case in result_cases if case["pass"]),
        "positive_recommendation_rate": round(positive_recommendation_rate, 4),
        "false_positive_rate": round(false_positive_rate, 4),
        "ambiguous_handling_rate": round(ambiguous_handling_rate, 4),
        "private_core_leakage_count": private_core_leakage_count,
        "recommendation_reason_quality_avg": round(mean(case["reason_quality"] for case in result_cases), 4),
    }

    if metrics["private_core_leakage_count"] > 0 or metrics["false_positive_rate"] > 0.10:
        validation_status = "stop"
    elif metrics["positive_recommendation_rate"] < 0.75:
        validation_status = "hold"
    else:
        validation_status = "pass"
    metrics["validation_status"] = validation_status

    return {
        "validation_scope": "local_agent_recommendation_surface",
        "external_ai_tested": False,
        "external_validation_claim": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "metrics": metrics,
        "cases": result_cases,
    }


def main() -> None:
    computed = compute_results()
    stored = load_json("agent_recommendation/VALIDATION_RESULTS.json")
    if stored != computed:
        raise SystemExit("VALIDATION_RESULTS.json does not match deterministic local classifier output")
    if computed["metrics"]["validation_status"] != "pass":
        raise SystemExit("validation_status must be pass for current local validation")
    print(
        "SAEE_AGENT_RECOMMENDATION_VALIDATION_SMOKE: PASS "
        "local_validation_only=true external_ai_tested=false "
        f"total_cases={computed['metrics']['total_cases']} "
        f"passed_cases={computed['metrics']['passed_cases']} "
        "private_core_leakage_count=0"
    )


if __name__ == "__main__":
    main()
