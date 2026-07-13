# SAEE Controlled Trial Observation Runner v0.1

controlled_trial_observation_runner_v0_1: true
observation_status: local_observation_recorded
observation_scope: local_mvp_demo_observation
production_ready: false
customer_validated: false
customer_contacted: false
customer_data_collected: false
production_data_collected: false
paid_trial_enabled: false
payment_provider_configured: false
product_launched: false
public_sdk_released: false
external_ai_assistant_tested: false
external_validation_claim: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
backend_modified: false
kernel_modified: false
external_calls_made: false
blockers_closed_by_observation: 0

## Purpose

The observation runner records one local controlled-trial demo observation as
machine-checkable JSON and Markdown. It converts the existing operator packet
from a manual template into a repeatable local observation artifact.

This runner does not launch product, contact customers, collect customer data,
test external AI assistants, call external services, close production blockers,
claim customer validation, or claim production readiness.

## What It Runs

The runner uses the existing controlled-trial demo payload and public MVP
service layer:

```text
scripts/saee_controlled_trial_observation_runner.py
```

It imports the same demo request used by:

```text
scripts/saee_controlled_trial_local_e2e_smoke.py
```

It uses:

- public request models;
- public experiment service;
- request limit validation;
- in-memory experiment store;
- the controlled trial operator packet template.

It does not start Uvicorn, open a browser, run the landing page, call external
systems, or inspect private core internals.

## Outputs

Generated outputs:

```text
phase_b_product/validation/controlled_trial_observations/README.md
phase_b_product/validation/controlled_trial_observations/local_trial_observation_input.json
phase_b_product/validation/controlled_trial_observations/local_trial_observation_result.json
phase_b_product/validation/controlled_trial_observations/local_trial_observation_result.md
```

Expected local demo result:

```text
status: completed
recommended_agent: agent-b
ranking_top: agent-b
agent_count: 3
stored_run_count: 15
```

Expected visible output fields:

```text
decision_result
recommended_agent
confidence_score
ranking
failure_modes_summary
survival_curves
```

## What This Strengthens

Evolution subsystem strengthened:

```text
Evolutionary Archive / Rollback Immune System
```

Commercial readiness function strengthened:

```text
local trial evidence capture
```

The runner creates a reproducible record of what the local MVP demo produced,
so a human reviewer can compare future trial observations without relying on
memory or screenshots.

## What It Does Not Prove

This runner does not prove:

- production readiness;
- customer validation;
- pilot success;
- paid trial readiness;
- production monitoring readiness;
- production auth readiness;
- external AI assistant recommendation behavior;
- private-core readiness or exposure;
- closure of any commercial launch blocker.

## Local Commands

Generate the current local observation:

```bash
python3 scripts/saee_controlled_trial_observation_runner.py
```

Validate generated observation artifacts:

```bash
python3 scripts/saee_controlled_trial_observation_runner_smoke.py
```

Run the full local guard:

```bash
python3 scripts/mainline_guard.py
```

## Boundary

This is a local observation recorder for the controlled trial demo. It may make
trial evidence easier to review, but it changes no product behavior and closes
zero blockers by default.
