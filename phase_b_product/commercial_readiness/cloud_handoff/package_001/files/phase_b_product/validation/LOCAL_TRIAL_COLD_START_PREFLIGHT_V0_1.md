# SAEE Local Trial Cold-Start Preflight v0.1

local_trial_cold_start_preflight_v0_1: true
snapshot_scope: local_mvp_cold_start_dependency_check
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
dependencies_installed_by_script: false
server_started_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_cold_start_preflight: 0

## Purpose

The local trial cold-start preflight records whether a reviewer can start the
SAEE MVP backend from the selected Python environment, independent of any
already-running local service.

It helps answer a commercial-readiness question:

```text
Can a fresh local reviewer reproduce the SAEE MVP tryout from this Python environment?
```

## What It Checks

- required local backend and landing files;
- the selected Python executable;
- FastAPI import availability;
- Uvicorn import availability;
- the backend requirements file.

## What It Does Not Do

- does not install dependencies;
- does not start backend or landing services;
- does not open a browser;
- does not call external services;
- does not contact customers;
- does not process customer data;
- does not modify product behavior;
- does not modify runtime, backend logic, kernel, or API schema;
- does not close commercial blockers;
- does not claim customer validation, external validation, product launch, or
  production readiness.

## Generated Outputs

- `phase_b_product/validation/local_trial_cold_start_preflight.local.json`
- `phase_b_product/validation/local_trial_cold_start_preflight.md`

## Run

```bash
python3 scripts/saee_local_trial_cold_start_preflight.py
python3 scripts/saee_local_trial_cold_start_preflight_smoke.py
```
