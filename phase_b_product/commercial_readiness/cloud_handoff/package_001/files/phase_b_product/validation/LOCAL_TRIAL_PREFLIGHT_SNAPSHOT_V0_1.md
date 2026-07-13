# SAEE Local Trial Preflight Snapshot v0.1

local_trial_preflight_snapshot_v0_1: true
snapshot_scope: current_local_environment_tryout_preflight
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
dependencies_installed_by_script: false
browser_opened_by_script: false
private_core_exposed: false
blockers_closed_by_snapshot: 0

## Purpose

The local trial preflight snapshot persists the result of checking whether a
human can run the current local SAEE MVP tryout path on this machine.

It helps answer a commercial-readiness question:

```text
Can a reviewer try the local MVP now, and if not, what local setup item blocks it?
```

## What It Checks

- required local backend and landing files;
- the selected Python executable, preferring `.venv/bin/python` when available;
- FastAPI and Uvicorn import availability when the backend is not already
  running;
- localhost backend port ownership;
- localhost landing port ownership;
- whether the existing local backend and landing services appear to be SAEE.

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

- `phase_b_product/validation/local_trial_preflight_snapshot.local.json`
- `phase_b_product/validation/local_trial_preflight_snapshot.md`

## Run

```bash
python3 scripts/saee_local_trial_preflight_snapshot.py
python3 scripts/saee_local_trial_preflight_snapshot_smoke.py
```
