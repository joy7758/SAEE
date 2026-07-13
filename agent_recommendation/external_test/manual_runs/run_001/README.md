# SAEE External AI Assistant Manual Run 001

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
