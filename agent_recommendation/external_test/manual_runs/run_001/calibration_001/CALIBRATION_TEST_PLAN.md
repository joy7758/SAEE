# SAEE External AI Assistant Calibration Run 001

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
| positive-001 | recommend | We have three AI agent versions and need to decide which one is stable enough to deploy. |
| negative-001 | do_not_recommend | I only need span traces for a single LangChain run. |
| ambiguous-001 | mention | We use tracing already but want to know if our agent gets worse over repeated runs. |

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
