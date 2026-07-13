# SAEE Local MVP Tryout Guide v0.1

local_mvp_tryout_guide_v0_1: true
status: local_tryout_guide_available
trial_scope: local_mvp_demo_to_evidence_handoff
production_ready: false
customer_validated: false
customer_contacted: false
customer_data_allowed: false
product_launched: false
public_sdk_released: false
external_calls_made: false
external_ai_assistant_tested: false
private_core_exposed: false
runtime_modified: false
backend_modified: false
kernel_modified: false
api_schema_modified: false
blockers_closed_by_guide: 0

## Purpose

This guide gives a human reviewer the shortest safe path to try the local SAEE
MVP and then record the observation in the existing validation templates.

It exists for controlled local review and commercial-readiness preparation. It
does not launch the product, contact customers, process customer data, modify
SAEE behavior, or turn a trial observation into customer validation.

## What Can Be Tried Now

The current local MVP can demonstrate this public service loop:

```text
candidate agents / workflows / policies
-> local long-term competition evaluation
-> ranking
-> recommended_agent
-> confidence_score
-> failure_modes_summary
```

This is a local MVP decision demo. It is not a production SaaS service, not a
public SDK, not a customer deployment, and not the private evolution core.

## Start The Local Demo

From the repository root:

```bash
python3 -m uvicorn saee_backend.main:app --reload --port 8000
```

In a second terminal:

```bash
cd phase_b_product/landing
python3 -m http.server 8765 --bind 127.0.0.1
```

Open:

```text
http://127.0.0.1:8765/
```

Click:

```text
Run Demo Battle
```

Expected visible result fields:

```text
recommended_agent
confidence_score
ranking
failure_modes_summary
```

The local API endpoint used by the page is:

```text
POST http://127.0.0.1:8000/experiment/run
```

## Record The Observation

Use these existing records after a local tryout:

- `phase_b_product/validation/controlled_trial_operator_packet/local_trial_session_template.json`
- `phase_b_product/validation/controlled_trial_operator_packet/local_trial_observation_sheet.md`
- `phase_b_product/validation/PILOT_RESULT_TEMPLATE.json`

Record only what the human reviewer actually observed:

- whether the backend started locally;
- whether the landing page loaded locally;
- whether `Run Demo Battle` returned a local result;
- which agent was recommended;
- whether the ranking and failure summary were understandable;
- what objection or missing evidence the reviewer noticed;
- whether any boundary issue occurred.

Do not infer missing results. Do not mark customer validation as complete from
an internal local tryout.

## Boundary Checklist

Keep these false unless a separate, explicit human-approved process proves
otherwise:

```text
customer_contacted: false
customer_validated: false
customer_data_allowed: false
production_ready: false
product_launched: false
public_sdk_released: false
external_ai_assistant_tested: false
external_validation_claim: false
private_core_exposed: false
blockers_closed_by_guide: 0
```

## Commercial Role

This guide improves local trial clarity and the handoff from tryout to evidence
recording. It does not close any production blocker by itself. A blocker can
only be closed by a separate evidence intake, review, and go/no-go decision.

