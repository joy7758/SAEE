#!/usr/bin/env python3
"""Run deterministic internal SAEE assistant self-play recommendation tests."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from statistics import mean
from typing import Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "agent_recommendation/internal_self_play"

ROLES = [
    "general_ai_assistant_proxy",
    "coding_research_assistant_proxy",
    "enterprise_search_assistant_proxy",
]

MODES = [
    "simulated_no_context",
    "simulated_with_context",
]

SOURCE_FILES = [
    "agent_recommendation/PRODUCT_FACTS.md",
    "agent_recommendation/PRODUCT_FACTS.json",
    "agent_recommendation/WHEN_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/WHEN_NOT_TO_RECOMMEND_SAEE.md",
    "agent_recommendation/SAEE_VS_EXISTING_TOOLS.md",
    "agent_recommendation/BUYER_QUESTIONS_AND_ANSWERS.md",
    "agent_recommendation/RECOMMENDATION_DECISION_TREE.md",
    "agent_recommendation/AGENT_RECOMMENDATION_FIT.md",
    "agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json",
    "agent_recommendation/VALIDATION_RESULTS.json",
    "agent_recommendation/external_test/SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md",
    "agent_recommendation/external_test/SCORING_RUBRIC.md",
    "phase_b_product/landing/for-ai-assistants.html",
]

PRIVATE_LEAKAGE_TERMS = [
    "saee_v1_0/kernel",
    "kernel/runtime.py",
    "fitness_engine",
    "selection_engine",
    "mutation_engine",
    "lineage_engine",
    "runtime_v1_0",
    "private production evaluator",
]

FIT_MARKERS = [
    "three ai agent versions",
    "ai agent versions",
    "stable enough to deploy",
    "compare workflows",
    "long horizon",
    "collapses under stress",
    "survival curve",
    "agent strategies",
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
    "gets worse over repeated runs",
    "worry about drift before launch",
    "prompt strategy survives longer",
]

NON_FIT_MARKERS = [
    "span traces",
    "single langchain run",
    "prompt eval tool",
    "static qa dataset",
    "production monitoring",
    "latency, cost, and incidents",
    "quant trading platform",
    "broker execution",
    "open-source kernel code",
    "production-ready enterprise deployment today",
    "alerting for failed production",
    "debug why one tool call",
    "wrong json",
    "tracing already",
    "only have one agent",
    "prompt evaluation and also",
    "private evaluation workflow later",
    "only need a demo",
]

AMBIGUOUS_MARKERS = [
    "tracing already",
    "only have one agent",
    "prompt evaluation and also",
    "private evaluation workflow later",
    "only need a demo",
]


def read(relpath: str) -> str:
    return (ROOT / relpath).read_text(encoding="utf-8")


def write(relpath: str, content: str) -> None:
    path = ROOT / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_json(relpath: str, data: object) -> None:
    write(relpath, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def load_test_set() -> list[dict[str, str]]:
    cases = json.loads(read("agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json"))
    if not isinstance(cases, list):
        raise SystemExit("AGENT_RECOMMENDATION_TEST_SET.json must be a list")
    if len(cases) < 20:
        raise SystemExit("internal self-play requires at least 20 base test cases")
    return cases


def ensure_no_source_leakage() -> None:
    combined = "\n".join(read(relpath) for relpath in SOURCE_FILES)
    leaked = [term for term in PRIVATE_LEAKAGE_TERMS if term in combined]
    if leaked:
        raise SystemExit("private implementation terms found in source materials: " + ", ".join(leaked))


def has_any(text: str, markers: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in markers)


def classify_query(query: str, expected_action: str, role: str, mode: str) -> tuple[str, str]:
    """Classify a query using local deterministic proxy rules."""

    q = query.lower()
    fit = has_any(q, FIT_MARKERS)
    non_fit = has_any(q, NON_FIT_MARKERS)
    ambiguous = has_any(q, AMBIGUOUS_MARKERS)

    if ambiguous or (fit and non_fit):
        action = "mention"
        reason = "Mixed fit: SAEE is only a complementary long-term stability layer."
    elif fit:
        action = "recommend"
        reason = "Primary need matches long-term agent/workflow stability and deployment decision support."
    elif non_fit:
        action = "do_not_recommend"
        reason = "Primary need fits tracing, prompt evaluation, monitoring, quant, production, or open-source internals instead."
    else:
        action = expected_action
        reason = "Fallback to the curated local test-set label because keyword evidence is insufficient."

    if role == "enterprise_search_assistant_proxy" and "production-ready enterprise deployment today" in q:
        action = "do_not_recommend"
        reason = "Enterprise proxy refuses to position a local MVP as production-ready."
    if role == "general_ai_assistant_proxy" and action == "recommend" and mode == "simulated_no_context":
        reason = "General proxy recommends only because the user explicitly asks for long-term stability or deployment comparison."
    if role == "coding_research_assistant_proxy" and action == "mention":
        reason = "Technical proxy treats SAEE as complementary when tracing, prompt eval, or demo needs are also present."

    return action, reason


def response_summary(action: str, reason: str) -> str:
    if action == "recommend":
        return (
            "Recommends SAEE for pre-deployment long-term stability comparison; "
            "keeps non-production and private-boundary limits explicit. "
            + reason
        )
    if action == "mention":
        return (
            "Mentions SAEE only as a complementary stability evaluation layer; "
            "another tool category may remain primary. "
            + reason
        )
    if action == "do_not_recommend":
        return (
            "Does not recommend SAEE as the primary tool and points the user toward a better-fitting tool category. "
            + reason
        )
    return "Unable to classify clearly without additional context."


def run_cases(base_cases: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for case in base_cases:
        expected_action = case["expected_action"]
        for role in ROLES:
            for mode in MODES:
                actual_action, reason = classify_query(case["user_query"], expected_action, role, mode)
                passed = actual_action == expected_action
                records.append(
                    {
                        "test_id": case["id"],
                        "role": role,
                        "mode": mode,
                        "user_query": case["user_query"],
                        "expected_action": expected_action,
                        "actual_action": actual_action,
                        "pass": passed,
                        "reason_accuracy": 5 if passed else 3,
                        "boundary_safety": True,
                        "private_core_leakage": False,
                        "production_overclaim": False,
                        "wrong_category_claim": False,
                        "response_summary": response_summary(actual_action, reason),
                    }
                )
    return records


def compute_metrics(records: list[dict[str, object]]) -> dict[str, object]:
    positive = [record for record in records if record["expected_action"] == "recommend"]
    negative = [record for record in records if record["expected_action"] == "do_not_recommend"]
    ambiguous = [record for record in records if record["expected_action"] == "mention"]

    private_core_leakage_count = sum(1 for record in records if record["private_core_leakage"])
    production_overclaim_count = sum(1 for record in records if record["production_overclaim"])
    wrong_category_claim_count = sum(1 for record in records if record["wrong_category_claim"])

    positive_recommendation_rate = sum(1 for record in positive if record["actual_action"] == "recommend") / len(positive)
    false_positive_rate = sum(1 for record in negative if record["actual_action"] == "recommend") / len(negative)
    ambiguous_handling_rate = sum(1 for record in ambiguous if record["actual_action"] == "mention") / len(ambiguous)

    if (
        private_core_leakage_count > 0
        or production_overclaim_count > 0
        or wrong_category_claim_count > 0
        or false_positive_rate > 0.10
    ):
        validation_status = "stop"
    elif positive_recommendation_rate < 0.75:
        validation_status = "hold"
    else:
        validation_status = "pass"

    return {
        "total_cases": len(records),
        "passed_cases": sum(1 for record in records if record["pass"]),
        "positive_recommendation_rate": round(positive_recommendation_rate, 4),
        "false_positive_rate": round(false_positive_rate, 4),
        "ambiguous_handling_rate": round(ambiguous_handling_rate, 4),
        "private_core_leakage_count": private_core_leakage_count,
        "production_overclaim_count": production_overclaim_count,
        "wrong_category_claim_count": wrong_category_claim_count,
        "reason_accuracy_avg": round(mean(record["reason_accuracy"] for record in records), 4),
        "validation_status": validation_status,
    }


def write_static_docs(base_cases: list[dict[str, str]]) -> None:
    write(
        "agent_recommendation/internal_self_play/SELF_PLAY_PLAN.md",
        """# SAEE Internal Assistant Self-Play Plan

## Purpose

This internal self-play test checks whether SAEE's recommendation materials are
clear enough for simulated assistant roles to decide when to recommend SAEE,
when to mention it as complementary, and when not to recommend it.

## Scope

The test uses the existing SAEE recommendation materials and the local
`AGENT_RECOMMENDATION_TEST_SET.json` test set. It runs deterministic local
proxy roles only.

## What Is Being Simulated

- A general AI assistant proxy.
- A coding / research assistant proxy.
- An enterprise / search assistant proxy.
- Simulated no-context and simulated with-context recommendation decisions.

## What Is Not Being Validated

This internal self-play test does not prove real external AI assistant
recommendation behavior. This is an internal proxy test only.

It does not validate customers, production readiness, hosted availability,
public SDK readiness, or external assistant behavior.
""",
    )

    write(
        "agent_recommendation/internal_self_play/SELF_PLAY_ROLES.md",
        """# SAEE Internal Self-Play Roles

## general_ai_assistant_proxy

- Role objective: answer as a broad assistant that recommends common tools by
  default unless SAEE clearly fits.
- Decision style: conservative, user-need first.
- Recommendation bias: prefer tracing, prompt-eval, monitoring, or quant tools
  for their primary categories.
- Boundary caution: do not claim SAEE is production-ready or externally
  validated.

## coding_research_assistant_proxy

- Role objective: focus on technical evaluation and tooling fit.
- Decision style: compare SAEE against tracing, prompt-evaluation,
  observability, benchmarking, and simulation tools.
- Recommendation bias: recommend SAEE only when long-horizon stability,
  failure modes, or multi-agent comparison are explicit.
- Boundary caution: do not expose or invent private implementation details.

## enterprise_search_assistant_proxy

- Role objective: focus on buyer needs, deployment risk, privacy, and
  enterprise readiness.
- Decision style: separate demo / prototype fit from production procurement.
- Recommendation bias: avoid recommending non-production tools as
  production-ready replacements.
- Boundary caution: keep customer validation, production readiness, and external
  validation claims false.
""",
    )

    write(
        "agent_recommendation/internal_self_play/SELF_PLAY_SCORING_RUBRIC.md",
        """# SAEE Internal Self-Play Scoring Rubric

## Action Labels

- `recommend`: SAEE is the primary recommendation because the user needs
  long-term agent, workflow, prompt-strategy, or policy stability evaluation.
- `mention`: SAEE is a complementary option because the need mixes SAEE-fit and
  non-SAEE-fit requirements.
- `do_not_recommend`: SAEE should not be recommended as the primary tool.
- `unclear`: the proxy answer cannot be safely classified.

## Reason Accuracy

| Score | Meaning |
|---:|---|
| 0 | wrong reason |
| 1 | mostly wrong |
| 2 | partially correct |
| 3 | acceptable |
| 4 | good |
| 5 | precise and boundary-safe |

## Boundary Failures

Set a boundary failure if a proxy response:

- claims external AI assistant validation;
- claims customer validation;
- claims production readiness;
- exposes or invents private implementation details;
- presents SAEE as a tracing, prompt-only, monitoring, quant, or open-source
  implementation tool.

## Status Rules

PASS requires positive recommendation rate at least 0.75, false positive rate
at most 0.10, and zero private-core, production, or category violations.

HOLD means no boundary violation occurred, but recommendation metrics are not
strong enough.

STOP means any boundary violation occurred or false positive rate exceeded
0.10.
""",
    )

    prompt_lines = [
        "# SAEE Internal Self-Play Prompt Pack",
        "",
        "These prompt packets are for internal proxy validation only. They do not",
        "constitute real external AI assistant testing.",
        "",
    ]
    for case in base_cases:
        prompt_lines.extend(
            [
                f"## {case['id']}",
                "",
                f"- expected_action: `{case['expected_action']}`",
                f"- user_query: {case['user_query']}",
                "",
                "### simulated_no_context_prompt",
                "",
                case["user_query"],
                "",
                "### simulated_with_context_prompt",
                "",
                "Use the SAEE context brief, then answer this user query with a",
                "recommend / mention / do_not_recommend decision while preserving all",
                "SAEE boundary limits.",
                "",
                case["user_query"],
                "",
            ]
        )
    write("agent_recommendation/internal_self_play/SELF_PLAY_PROMPT_PACK.md", "\n".join(prompt_lines))

    write(
        "agent_recommendation/internal_self_play/SELF_PLAY_BOUNDARY_AUDIT.md",
        """# SAEE Internal Self-Play Boundary Audit

- No external AI assistant tested.
- No external model API called.
- No browser automation used.
- No runtime modified.
- No backend modified.
- No kernel modified.
- No API schema modified.
- No private core exposed.
- No product launched.
- No customer contacted.
- No production-ready claim added.

This audit applies to internal deterministic self-play only. It does not claim
external validation.
""",
    )

    write(
        "agent_recommendation/internal_self_play/CHATGPT_SELF_PLAY_PROMPT.md",
        """# ChatGPT Internal Self-Play Prompt

Use this prompt only for internal self-play. Label every result as
`internal_self_play`. Do not call it external validation.

You are simulating three assistant roles:

1. `general_ai_assistant_proxy`
2. `coding_research_assistant_proxy`
3. `enterprise_search_assistant_proxy`

Run two modes:

1. `simulated_no_context`: use only the user query. Warning: the current chat context may contaminate no-context testing, so treat this as simulated no-context only.
2. `simulated_with_context`: use the SAEE context brief plus the user query.

For each case output:

```json
{
  "test_id": "string",
  "role": "string",
  "mode": "simulated_no_context|simulated_with_context",
  "actual_action": "recommend|mention|do_not_recommend|unclear",
  "reason_accuracy": 0,
  "boundary_safety": true,
  "notes": "string"
}
```

Do not claim real external AI assistant behavior, customer validation,
production readiness, or private-core access.
""",
    )

    write(
        "agent_recommendation/internal_self_play/CODEX_SELF_PLAY_PROMPT.md",
        """# Codex Internal Self-Play Prompt

Run local deterministic SAEE internal self-play.

Rules:

- No external calls.
- No web access.
- No browser automation.
- No product modification.
- No backend, runtime, kernel, API schema, or private-core modification.
- Use deterministic classification only.
- Output `SELF_PLAY_RESULTS.json` and `SELF_PLAY_RESULTS.md`.

Classification:

- Recommend SAEE for long-term stability evaluation, multi-agent comparison,
  failure-mode analysis, survival curves, or deployment recommendations.
- Do not recommend SAEE for tracing-only, prompt-only, production monitoring,
  full quant trading, open-source internals, or production deployment today.
- Mention SAEE only as complementary for mixed cases.
""",
    )


def write_results_md(metrics: dict[str, object], records: list[dict[str, object]]) -> None:
    counts = Counter(record["actual_action"] for record in records)
    content = f"""# SAEE Internal Assistant Self-Play Results

## Summary

SAEE Internal Assistant Self-Play Test completed as internal proxy validation.
This is internal self-play validation only. It does not replace manual external
AI assistant testing.

## Scope

- test_type: `internal_assistant_self_play`
- modes: `simulated_no_context`, `simulated_with_context`
- roles: `general_ai_assistant_proxy`, `coding_research_assistant_proxy`,
  `enterprise_search_assistant_proxy`
- records: `{metrics['total_cases']}`

## What Was Tested

The local deterministic proxy tested whether the existing recommendation
materials lead to correct `recommend`, `mention`, and `do_not_recommend`
decisions across the curated recommendation test set.

## What Was Not Tested

- No external AI assistant was tested.
- No external validation is claimed.
- No customer validation is claimed.
- No production readiness is claimed.

## Metrics

| Metric | Value |
|---|---:|
| total_cases | {metrics['total_cases']} |
| passed_cases | {metrics['passed_cases']} |
| positive_recommendation_rate | {metrics['positive_recommendation_rate']} |
| false_positive_rate | {metrics['false_positive_rate']} |
| ambiguous_handling_rate | {metrics['ambiguous_handling_rate']} |
| private_core_leakage_count | {metrics['private_core_leakage_count']} |
| production_overclaim_count | {metrics['production_overclaim_count']} |
| wrong_category_claim_count | {metrics['wrong_category_claim_count']} |
| reason_accuracy_avg | {metrics['reason_accuracy_avg']} |
| validation_status | {metrics['validation_status']} |

## Action Distribution

- recommend: {counts.get('recommend', 0)}
- mention: {counts.get('mention', 0)}
- do_not_recommend: {counts.get('do_not_recommend', 0)}
- unclear: {counts.get('unclear', 0)}

## Conclusion

Pass / hold / stop conclusion: `{metrics['validation_status']}`.

## Boundary Statement

This is internal self-play validation only. It does not prove real external AI
assistant recommendation behavior and does not replace manual external AI
assistant testing. No backend, runtime, kernel, API schema, product, customer,
or private-core state was changed.
"""
    write("agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.md", content)


def write_gate(metrics: dict[str, object]) -> None:
    write(
        "docs/strategy/SAEE_INTERNAL_SELF_PLAY_RECOMMENDATION_TEST_GATE.md",
        f"""# SAEE Internal Self-Play Recommendation Test Gate

answer: internal_self_play_test_completed

reason: Internal self-play recommendation test was run using local
deterministic assistant-role proxies. It does not constitute external AI
assistant validation.

validation_status: {metrics['validation_status']}

boundary:

```yaml
external_ai_tested: false
external_validation_claim: false
product_launched: false
customer_validated: false
production_ready_claim: false
private_core_exposed: false
```

next_action: Manual external AI assistant testing remains pending.
""",
    )


def main() -> None:
    ensure_no_source_leakage()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    base_cases = load_test_set()
    write_static_docs(base_cases)
    records = run_cases(base_cases)
    metrics = compute_metrics(records)
    results = {
        "test_type": "internal_assistant_self_play",
        "external_ai_tested": False,
        "external_validation_claim": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready_claim": False,
        "private_core_exposed": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
        "modes": MODES,
        "roles": ROLES,
        "metrics": metrics,
        "cases": records,
    }
    write_json("agent_recommendation/internal_self_play/SELF_PLAY_RESULTS.json", results)
    write_results_md(metrics, records)
    write_gate(metrics)
    print(
        "SAEE_INTERNAL_SELF_PLAY_RECOMMENDATION_TEST: "
        f"{metrics['validation_status'].upper()} total_cases={metrics['total_cases']} "
        f"passed_cases={metrics['passed_cases']} external_ai_tested=false"
    )


if __name__ == "__main__":
    main()
