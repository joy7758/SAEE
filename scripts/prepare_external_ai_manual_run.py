#!/usr/bin/env python3
"""Prepare SAEE external AI assistant manual test run files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUN_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001"
TEST_SET = ROOT / "agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json"
CONTEXT_BRIEF = ROOT / "agent_recommendation/external_test/SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md"

ASSISTANT_TARGETS = [
    ("Assistant A", "general_ai_assistant", "general AI assistant"),
    ("Assistant B", "coding_research_assistant", "coding/research assistant"),
    ("Assistant C", "enterprise_search_assistant", "enterprise/search assistant"),
]

CSV_COLUMNS = [
    "test_id",
    "assistant_name",
    "assistant_type",
    "test_round",
    "context_given",
    "user_query",
    "expected_action",
    "actual_action",
    "reason_accuracy",
    "boundary_safety",
    "private_core_leakage",
    "production_overclaim",
    "universal_claim_overreach",
    "wrong_category_claim",
    "raw_response_summary",
    "notes",
]


def load_cases() -> list[dict[str, str]]:
    cases = json.loads(TEST_SET.read_text(encoding="utf-8"))
    if not isinstance(cases, list) or len(cases) < 20:
        raise SystemExit("AGENT_RECOMMENDATION_TEST_SET.json must contain at least 20 cases")
    return cases


def planned_records(cases: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for assistant_name, assistant_type, _label in ASSISTANT_TARGETS:
        for test_round, context_given in [("no_context", False), ("with_context", True)]:
            for case in cases:
                records.append(
                    {
                        "test_id": case["id"],
                        "assistant_name": assistant_name,
                        "assistant_type": assistant_type,
                        "test_round": test_round,
                        "context_given": context_given,
                        "user_query": case["user_query"],
                        "expected_action": case["expected_action"],
                        "actual_action": "",
                        "reason_accuracy": None,
                        "boundary_safety": None,
                        "private_core_leakage": None,
                        "production_overclaim": None,
                        "universal_claim_overreach": None,
                        "wrong_category_claim": None,
                        "raw_response_summary": "",
                        "notes": "",
                    }
                )
    return records


def write_readme() -> None:
    (RUN_DIR / "README.md").write_text(
        """# SAEE External AI Assistant Manual Run 001

## Purpose

This package prepares a manual execution run for testing whether external AI
assistants recommend SAEE in the right situations and avoid recommending it in
the wrong situations.

This package does not execute external tests.
Human tester must manually paste prompts into external AI assistants.

## Test Scope

- 3 generic assistant targets.
- 20 no-context prompts per assistant.
- 20 with-context prompts per assistant.
- 120 planned manual records.

## What The Human Tester Should Do

1. Open each external assistant manually.
2. Paste no-context prompts first.
3. Record the assistant responses manually.
4. Start a fresh conversation for with-context prompts.
5. Paste the SAEE context brief.
6. Paste each with-context prompt.
7. Enter results into `manual_results_entry.csv` or `manual_results_entry.json`.
8. Run the import and scoring scripts after manual entry.

## What Must Not Be Automated

- Do not call external model APIs.
- Do not automate browser sessions.
- Do not scrape external assistants.
- Do not contact customers.
- Do not launch a product.
- Do not claim external validation completed.

## Safety Boundary

This run is a manual testing packet only. It does not modify SAEE runtime,
backend, API contracts, execution loop, private core, or product UI.
""",
        encoding="utf-8",
    )


def write_checklist() -> None:
    (RUN_DIR / "TESTER_CHECKLIST.md").write_text(
        """# Tester Checklist

## Step 1

Open one external AI assistant in a fresh conversation.

## Step 2

Run no-context prompts first.

## Step 3

Record actual responses.

## Step 4

Start a new fresh conversation for with-context tests.

## Step 5

Paste SAEE context brief first.

## Step 6

Paste each with-context prompt.

## Step 7

Record results in `manual_results_entry.csv` or `manual_results_entry.json`.

## Step 8

Run scoring script after manual entry.

## Boundary

All external assistant interactions must be performed manually by a human
tester. Do not automate the test.
""",
        encoding="utf-8",
    )


def write_targets() -> None:
    lines = [
        "# Assistant Targets",
        "",
        "Do not hardcode accounts or API keys.",
        "",
        "| Slot | Assistant Type | Manual Requirement |",
        "|---|---|---|",
    ]
    for assistant_name, _assistant_type, label in ASSISTANT_TARGETS:
        lines.append(f"| {assistant_name} | {label} | Test manually in a fresh conversation. |")
    lines.extend(
        [
            "",
            "Each target must be tested manually.",
            "No API keys, browser automation, scraping, or customer contact are allowed.",
        ]
    )
    (RUN_DIR / "ASSISTANT_TARGETS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_prompt_packets(cases: list[dict[str, str]]) -> None:
    no_context_lines = [
        "# Run 001 No-Context Prompt Packets",
        "",
        "Use these prompts without giving SAEE context.",
        "",
    ]
    for case in cases:
        no_context_lines.extend(
            [
                f"## {case['id']}",
                "",
                f"- test_id: `{case['id']}`",
                f"- expected_action: `{case['expected_action']}`",
                "- tester_note: Copy only the prompt below into a fresh external AI assistant conversation. Do not include SAEE context.",
                "",
                "prompt_to_copy:",
                "",
                "```text",
                case["user_query"],
                "```",
                "",
            ]
        )
    (RUN_DIR / "no_context_prompt_packets.md").write_text("\n".join(no_context_lines), encoding="utf-8")

    context = CONTEXT_BRIEF.read_text(encoding="utf-8").strip()
    with_context_lines = [
        "# Run 001 With-Context Prompt Packets",
        "",
        "Paste the context brief once at the start of a fresh conversation before running the prompts.",
        "",
        "## SAEE Context Brief",
        "",
        "```text",
        context,
        "```",
        "",
    ]
    for case in cases:
        with_context_lines.extend(
            [
                f"## {case['id']}",
                "",
                f"- test_id: `{case['id']}`",
                f"- expected_action: `{case['expected_action']}`",
                "- context_instruction: Paste the SAEE context brief first in a fresh conversation.",
                "- tester_note: After the context brief, copy only the prompt below and record the response manually.",
                "",
                "prompt_to_copy:",
                "",
                "```text",
                case["user_query"],
                "```",
                "",
            ]
        )
    (RUN_DIR / "with_context_prompt_packets.md").write_text("\n".join(with_context_lines), encoding="utf-8")


def write_manual_entries(records: list[dict[str, object]]) -> None:
    with (RUN_DIR / "manual_results_entry.csv").open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for record in records:
            csv_record = dict(record)
            for key in [
                "actual_action",
                "reason_accuracy",
                "boundary_safety",
                "private_core_leakage",
                "production_overclaim",
                "universal_claim_overreach",
                "wrong_category_claim",
            ]:
                csv_record[key] = ""
            writer.writerow(csv_record)

    (RUN_DIR / "manual_results_entry.json").write_text(
        json.dumps(records, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def write_result_instructions() -> None:
    (RUN_DIR / "result_entry_instructions.md").write_text(
        """# Result Entry Instructions

## actual_action

- `recommend` = assistant clearly recommends SAEE.
- `mention` = assistant mentions SAEE as complementary.
- `do_not_recommend` = assistant avoids SAEE or recommends other tools.
- `unclear` = cannot classify.

## reason_accuracy

Use a 0-5 scale:

- 0 = wrong reason
- 1 = mostly wrong
- 2 = partially correct
- 3 = acceptable
- 4 = good
- 5 = precise and boundary-safe

## Boundary Flags

- `private_core_leakage`: true if the response exposes, invents, or asks for private implementation internals.
- `production_overclaim`: true if the response says SAEE is production-ready or enterprise-ready today.
- `universal_claim_overreach`: true if the response claims universal or already externally validated recommendation success.
- `wrong_category_claim`: true if the response treats SAEE as a generic tracing tool, prompt-only evaluator, monitoring replacement, full quant platform, or open-source implementation package.

## Entry Rule

Do not infer missing results. Leave fields blank/null until a human tester has
manually recorded the external assistant response.
""",
        encoding="utf-8",
    )


def write_status_and_summary() -> None:
    status = {
        "run_id": "run_001",
        "manual_test_prepared": True,
        "manual_test_started": False,
        "manual_test_completed": False,
        "external_ai_tested": False,
        "total_planned_records": 120,
        "records_entered": 0,
        "scoring_completed": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    (RUN_DIR / "run_status.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
    (RUN_DIR / "run_summary.md").write_text(
        """# Run 001 Summary

Manual external AI assistant test run prepared, not executed.

## Planned Assistant Targets

- Assistant A: general AI assistant
- Assistant B: coding/research assistant
- Assistant C: enterprise/search assistant

## Planned Case Count

- 3 assistant targets
- 20 test cases
- 2 rounds: no_context and with_context
- 120 planned manual records

## Current Status

```text
manual_test_prepared: true
manual_test_started: false
manual_test_completed: false
external_ai_tested: false
records_entered: 0
scoring_completed: false
product_launched: false
customer_contacted: false
private_core_exposed: false
production_ready_claim: false
```

## Next Manual Action

Open `TESTER_CHECKLIST.md` and manually run no-context and with-context tests.
""",
        encoding="utf-8",
    )


def main() -> None:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    cases = load_cases()
    records = planned_records(cases)
    if len(records) != 120:
        raise SystemExit(f"expected 120 planned records, got {len(records)}")
    write_readme()
    write_checklist()
    write_targets()
    write_prompt_packets(cases)
    write_manual_entries(records)
    write_result_instructions()
    write_status_and_summary()
    print("SAEE_EXTERNAL_AI_MANUAL_RUN_PREPARED: run_id=run_001 planned_records=120 external_ai_tested=false")


if __name__ == "__main__":
    main()
