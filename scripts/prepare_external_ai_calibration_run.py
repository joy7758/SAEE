#!/usr/bin/env python3
"""Prepare SAEE external AI assistant calibration run 001 files."""

from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CALIBRATION_DIR = ROOT / "agent_recommendation/external_test/manual_runs/run_001/calibration_001"
TEST_SET = ROOT / "agent_recommendation/AGENT_RECOMMENDATION_TEST_SET.json"
CONTEXT_BRIEF = ROOT / "agent_recommendation/external_test/SAEE_CONTEXT_BRIEF_FOR_ASSISTANTS.md"

CSV_COLUMNS = [
    "calibration_record_id",
    "base_test_id",
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
    if not isinstance(cases, list):
        raise SystemExit("AGENT_RECOMMENDATION_TEST_SET.json must contain a list")
    return cases


def select_cases(cases: list[dict[str, str]]) -> list[dict[str, str]]:
    selected: list[dict[str, str]] = []
    for expected in ["recommend", "do_not_recommend", "mention"]:
        match = next((case for case in cases if case.get("expected_action") == expected), None)
        if match is None:
            raise SystemExit(f"missing calibration case for expected_action={expected}")
        selected.append(match)
    return selected


def planned_records(cases: list[dict[str, str]]) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    counter = 1
    for test_round, context_given in [("no_context", False), ("with_context", True)]:
        for case in cases:
            records.append(
                {
                    "calibration_record_id": f"CAL-{counter:03d}",
                    "base_test_id": case["id"],
                    "assistant_name": "",
                    "assistant_type": "general_ai_assistant",
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
            counter += 1
    return records


def write_text(name: str, content: str) -> None:
    (CALIBRATION_DIR / name).write_text(content, encoding="utf-8")


def write_json(name: str, data: object) -> None:
    write_text(name, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def write_plan(cases: list[dict[str, str]]) -> None:
    rows = "\n".join(
        f"| {case['id']} | {case['expected_action']} | {case['user_query']} |" for case in cases
    )
    write_text(
        "CALIBRATION_TEST_PLAN.md",
        f"""# SAEE External AI Assistant Calibration Run 001

## Purpose

Start a small manual calibration run before the full 120-record external AI
assistant test.

This calibration run does not test external AI assistants automatically.
Human tester must manually paste prompts and record results.

## Test Size

- assistant target: 1 external AI assistant chosen manually by the human tester
- no-context prompts: 3
- with-context prompts: 3
- total planned records: 6

## Selected Cases

| Base Test ID | Expected Action | User Query |
|---|---|---|
{rows}

## No-Context Round

Open a fresh external AI assistant conversation. Do not provide SAEE context.
Paste each no-context prompt exactly and record the answer manually.

## With-Context Round

Open a new fresh external AI assistant conversation. Paste the SAEE context
brief first, then paste each with-context prompt and record the answer
manually.

## What Human Tester Must Do

1. Choose one external AI assistant manually.
2. Run the 3 no-context prompts.
3. Run the 3 with-context prompts in a fresh conversation after pasting the
   SAEE context brief.
4. Fill `CALIBRATION_RESULT_ENTRY.json` or `CALIBRATION_RESULT_ENTRY.csv`.

## What Codex Must Not Do

- Codex must not call external AI assistants.
- Codex must not automate browser sessions.
- Codex must not scrape web assistants.
- Codex must not contact customers.
- Codex must not claim external validation completed.
- Codex must not claim production readiness.
""",
    )


def write_prompts(cases: list[dict[str, str]]) -> None:
    no_context_lines = [
        "# Calibration Prompts: No Context",
        "",
        "Open a fresh external AI assistant conversation. Do not provide SAEE context.",
        "Paste each prompt exactly and record the answer manually.",
        "",
    ]
    for idx, case in enumerate(cases, start=1):
        no_context_lines.extend(
            [
                f"## CAL-{idx:03d}",
                "",
                f"- calibration_record_id: `CAL-{idx:03d}`",
                f"- base_test_id: `{case['id']}`",
                f"- expected_action: `{case['expected_action']}`",
                "- tester_instruction: Open a fresh external AI assistant conversation. Do not provide SAEE context. Paste this prompt exactly. Record the answer manually.",
                "",
                "prompt_to_copy:",
                "",
                "```text",
                case["user_query"],
                "```",
                "",
            ]
        )
    write_text("CALIBRATION_PROMPTS_NO_CONTEXT.md", "\n".join(no_context_lines))

    context = CONTEXT_BRIEF.read_text(encoding="utf-8").strip()
    with_context_lines = [
        "# Calibration Prompts: With Context",
        "",
        "## SAEE Context Brief",
        "",
        "```text",
        context,
        "```",
        "",
        "Open a new fresh external AI assistant conversation. First paste the SAEE context brief.",
        "Then paste each prompt and record the answer manually.",
        "",
    ]
    for offset, case in enumerate(cases, start=4):
        with_context_lines.extend(
            [
                f"## CAL-{offset:03d}",
                "",
                f"- calibration_record_id: `CAL-{offset:03d}`",
                f"- base_test_id: `{case['id']}`",
                f"- expected_action: `{case['expected_action']}`",
                "- tester_instruction: Open a new fresh external AI assistant conversation. First paste the SAEE context brief. Then paste this prompt. Record the answer manually.",
                "",
                "prompt_to_copy:",
                "",
                "```text",
                case["user_query"],
                "```",
                "",
            ]
        )
    write_text("CALIBRATION_PROMPTS_WITH_CONTEXT.md", "\n".join(with_context_lines))


def write_entries(records: list[dict[str, object]]) -> None:
    write_json("CALIBRATION_RESULT_ENTRY.json", records)
    with (CALIBRATION_DIR / "CALIBRATION_RESULT_ENTRY.csv").open("w", encoding="utf-8", newline="") as fp:
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
                if csv_record[key] is None:
                    csv_record[key] = ""
            writer.writerow(csv_record)


def write_status_and_results() -> None:
    status = {
        "calibration_run_id": "calibration_001",
        "status": "started_pending_human_execution",
        "manual_execution_required": True,
        "external_ai_tested": False,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
        "planned_records": 6,
        "records_entered": 0,
        "results_imported": False,
        "scoring_completed": False,
        "product_launched": False,
        "customer_contacted": False,
        "private_core_exposed": False,
        "production_ready_claim": False,
    }
    write_json("CALIBRATION_STATUS.json", status)

    results = {
        "calibration_run_id": "calibration_001",
        "test_type": "manual_external_ai_assistant_calibration",
        "external_ai_tested": False,
        "manual_results_entered": False,
        "external_validation_claim": False,
        "customer_validated": False,
        "product_launched": False,
        "production_ready_claim": False,
        "private_core_exposed": False,
        "external_calls_made_by_codex": False,
        "browser_automation_used": False,
        "metrics": {
            "total_cases": 0,
            "passed_cases": 0,
            "positive_recommendation_rate": None,
            "false_positive_rate": None,
            "ambiguous_handling_rate": None,
            "private_core_leakage_count": 0,
            "production_overclaim_count": 0,
            "universal_claim_overreach_count": 0,
            "wrong_category_claim_count": 0,
            "validation_status": "pending",
        },
        "cases": [],
    }
    write_json("CALIBRATION_RESULTS.json", results)
    write_text(
        "CALIBRATION_RESULTS.md",
        """# Calibration Results

Calibration test is started but not executed yet.

No external AI assistant has been tested by Codex.
Human execution is required.

Current status:

```text
calibration_run_id: calibration_001
status: started_pending_human_execution
external_ai_tested: false
records_entered: 0
validation_status: pending
```
""",
    )


def write_guides() -> None:
    write_text(
        "CALIBRATION_RECORDING_GUIDE.md",
        """# Calibration Recording Guide

## actual_action

- `recommend`: assistant clearly recommends SAEE as the primary fit.
- `mention`: assistant mentions SAEE as complementary.
- `do_not_recommend`: assistant avoids SAEE or recommends another primary tool.
- `unclear`: response cannot be classified safely.

## reason_accuracy

Use a 0-5 score:

- 0 = wrong reason
- 1 = mostly wrong
- 2 = partially correct
- 3 = acceptable
- 4 = good
- 5 = precise and boundary-safe

## Boundary Flags

- `private_core_leakage`
- `production_overclaim`
- `universal_claim_overreach`
- `wrong_category_claim`

Important warning: Do not mark external_ai_tested = true until actual human
results are imported.
""",
    )
    write_text(
        "CALIBRATION_IMPORT_AND_SCORE_GUIDE.md",
        """# Calibration Import And Score Guide

After human fills `CALIBRATION_RESULT_ENTRY.json`, run:

```bash
python3 scripts/import_external_ai_calibration_results.py
python3 scripts/score_external_ai_calibration_results.py
python3 scripts/saee_external_ai_calibration_run_smoke.py
python3 scripts/mainline_guard.py
make check
```

The import step copies human-entered results into `CALIBRATION_RESULTS.json`.
The scoring step computes calibration metrics.

No external calls are made by scripts.
""",
    )


def write_gate() -> None:
    gate_path = ROOT / "docs/strategy/SAEE_EXTERNAL_AI_CALIBRATION_RUN_001_GATE.md"
    gate_path.write_text(
        """# SAEE External AI Calibration Run 001 Gate

answer: calibration_run_started_pending_human_execution

reason: A 6-record manual external AI assistant calibration run has been
prepared and started, but Codex has not tested external assistants and no
results have been entered yet.

boundary:

```yaml
external_ai_tested: false
external_calls_made_by_codex: false
browser_automation_used: false
product_launched: false
customer_contacted: false
private_core_exposed: false
production_ready_claim: false
```

next_action: Human tester must manually run the 3 no-context and 3 with-context
prompts against one external AI assistant and record results.
""",
        encoding="utf-8",
    )


def main() -> None:
    CALIBRATION_DIR.mkdir(parents=True, exist_ok=True)
    selected = select_cases(load_cases())
    records = planned_records(selected)
    write_plan(selected)
    write_prompts(selected)
    write_entries(records)
    write_status_and_results()
    write_guides()
    write_gate()
    print("SAEE_EXTERNAL_AI_CALIBRATION_RUN_PREPARED: calibration_001 planned_records=6 external_ai_tested=false")


if __name__ == "__main__":
    main()
