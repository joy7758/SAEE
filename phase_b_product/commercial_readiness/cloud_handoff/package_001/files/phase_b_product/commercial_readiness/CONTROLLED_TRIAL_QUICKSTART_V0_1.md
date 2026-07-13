# SAEE Controlled Trial Quickstart v0.1

Status: local controlled-trial quickstart, not production launch.

This file gives a human reviewer or pilot evaluator the shortest safe path to
try the SAEE local MVP demo. It is a commercial-readiness surface for trial
onboarding clarity. It does not change product behavior, backend logic, API
schema, runtime, kernel, private core, pricing, billing, or customer status.

## Purpose

SAEE can currently be tried as a local MVP decision demo:

```text
candidate agents / workflows / policies
-> local long-horizon competition simulation
-> ranking / recommended_agent / confidence_score / failure summary
```

The quickstart is intended for:

- internal product review;
- controlled pilot preparation;
- first-user demo rehearsal;
- agent-readable discovery of the safe local trial path.

It is not intended for:

- public production use;
- customer data processing;
- paid trial execution;
- external AI assistant validation;
- production monitoring;
- public SDK release.

## Local Trial Steps

From the repository root:

```bash
python3 -m uvicorn saee_backend.main:app --reload --port 8000
```

In a second terminal:

```bash
cd phase_b_product/landing
python3 -m http.server 8765
```

Open:

```text
http://127.0.0.1:8765/
```

Click:

```text
Run Demo Battle
```

Expected local result fields:

```text
decision_result: present
recommended_agent: present
confidence_score: present
ranking: present
failure_modes_summary: present
```

The demo request is defined in:

```text
phase_b_product/landing/app.js
```

The local API endpoint is:

```text
POST http://127.0.0.1:8000/experiment/run
```

## Current Boundary

```text
controlled_trial_quickstart_v0_1: true
trial_status: local_demo_available
local_backend_required: true
local_static_page_required: true
demo_endpoint: /experiment/run
demo_button: Run Demo Battle
decision_result_expected: true
production_ready: false
customer_validated: false
customer_contacted: false
customer_data_allowed: false
paid_trial_enabled: false
payment_provider_configured: false
product_launched: false
public_sdk_released: false
external_ai_assistant_tested: false
external_validation_claim: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
kernel_modified: false
external_calls_made: false
```

## What a Trial Reviewer Should Check

1. The local backend starts without changing environment defaults.
2. The landing page loads from localhost.
3. The `Run Demo Battle` button calls only the local API.
4. The result includes a recommended agent and ranking.
5. The reviewer understands that this is a local MVP trial, not a production
   deployment or customer validation result.

## What Must Not Be Claimed

- Do not claim SAEE is production-ready.
- Do not claim customer validation is complete.
- Do not claim external AI assistants have validated SAEE.
- Do not claim payment, checkout, or billing operations are ready.
- Do not claim public SDK availability.
- Do not claim the private evolution core is exposed or configurable.

## Commercial Readiness Role

This quickstart strengthens controlled trial onboarding and buyer evaluation
clarity. It helps a reviewer try the local decision loop without confusing
local MVP availability with production, sales, billing, or customer validation.
