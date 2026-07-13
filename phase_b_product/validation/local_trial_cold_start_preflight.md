# SAEE Local Trial Cold-Start Preflight

local_trial_cold_start_preflight_v0_1: true
snapshot_type: local_trial_cold_start_preflight
preflight_scope: local_mvp_cold_start_dependency_check
status: pass
cold_start_ready: true
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

This snapshot records whether the selected Python environment can start the
SAEE local MVP backend from a clean shell. It is stricter than the normal local
trial preflight because an already-running backend does not prove cold-start
readiness.

## Local Checks

- selected_python: `./.venv/bin/python`
- FastAPI import available: true
- Uvicorn import available: true
- required files present: true
- requirements file: `saee_backend/requirements.txt`

## Required Files

- backend_entrypoint: true
- backend_requirements: true
- landing_app: true
- landing_index: true

## Missing Or Blocking Items

- none

## Human Start Commands After Cold-Start Readiness

Backend:

```bash
./.venv/bin/python -m uvicorn saee_backend.main:app --host 127.0.0.1 --port 8000
```

Landing page:

```bash
cd phase_b_product/landing && python3 -m http.server 8765 --bind 127.0.0.1
```

## Boundary

This cold-start preflight uses only local file checks and Python import checks.
It does not install dependencies, start servers, open a browser, call external
services, contact customers, process customer data, modify backend behavior,
modify runtime/kernel/API schema, expose private core, launch product, close
production blockers, or claim production readiness.

## Next Human Action

If status is hold, prepare a controlled local Python environment with the backend requirements, then rerun this cold-start preflight. Do not treat an already-running backend as cold-start readiness.
