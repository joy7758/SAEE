#!/usr/bin/env python3
"""Validate the manual external AI assistant recommendation test kit."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "agent_recommendation/external_test/EXTERNAL_AI_TEST_PLAN.md",
    "agent_recommendation/external_test/NO_CONTEXT_PROMPTS.md",
    "agent_recommendation/external_test/WITH_CONTEXT_PROMPTS.md",
    "agent_recommendation/external_test/SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md",
    "agent_recommendation/external_test/MANUAL_RESULT_TEMPLATE.json",
    "agent_recommendation/external_test/MANUAL_RESULT_TEMPLATE.csv",
    "agent_recommendation/external_test/SCORING_RUBRIC.md",
    "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json",
    "agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.md",
    "agent_recommendation/external_test/README.md",
    "docs/strategy/SAEE_EXTERNAL_AI_RECOMMENDATION_TEST_GATE.md",
    "scripts/score_external_ai_recommendation_results.py",
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

FORBIDDEN_AUTOMATION_PATTERNS = [
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
    raise SystemExit(f"SAEE_EXTERNAL_AI_RECOMMENDATION_TEST_SMOKE: FAIL: {message}")


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def load_json(relpath: str) -> object:
    return json.loads(read(relpath))


def main() -> None:
    missing = [path for path in REQUIRED_FILES if not (ROOT / path).is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    if not (ROOT / "agent_recommendation/external_test").is_dir():
        fail("external test directory is missing")

    results = load_json("agent_recommendation/external_test/EXTERNAL_VALIDATION_RESULTS.json")
    required_flags = {
        "external_ai_tested": False,
        "manual_test_prepared": True,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    bad_flags = [flag for flag, expected in required_flags.items() if results.get(flag) is not expected]
    if bad_flags:
        fail("EXTERNAL_VALIDATION_RESULTS.json flags drifted: " + ", ".join(bad_flags))

    metrics = results.get("metrics", {})
    if metrics.get("validation_status") != "pending":
        fail("external validation must remain pending before manual results are entered")
    if results.get("results_entered") is not False:
        fail("results_entered must remain false before manual results are entered")

    no_context = read("agent_recommendation/external_test/NO_CONTEXT_PROMPTS.md")
    with_context = read("agent_recommendation/external_test/WITH_CONTEXT_PROMPTS.md")
    if no_context.count("## Prompt ") < 20:
        fail("NO_CONTEXT_PROMPTS.md must contain at least 20 prompts")
    if with_context.count("## Prompt ") < 20:
        fail("WITH_CONTEXT_PROMPTS.md must contain at least 20 prompts")

    combined_public = "\n".join(
        read(path)
        for path in REQUIRED_FILES
        if not path.startswith("scripts/")
    )
    private_hits = [term for term in FORBIDDEN_PRIVATE_TERMS if term in combined_public]
    if private_hits:
        fail("private implementation terms leaked: " + ", ".join(private_hits))

    script_text = read("scripts/score_external_ai_recommendation_results.py")
    automation_hits = [term for term in FORBIDDEN_AUTOMATION_PATTERNS if term in script_text]
    if automation_hits:
        fail("external automation patterns found in scripts: " + ", ".join(automation_hits))

    print(
        "SAEE_EXTERNAL_AI_RECOMMENDATION_TEST_SMOKE: PASS "
        "manual_test_prepared=true external_ai_tested=false "
        "product_launched=false customer_contacted=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
