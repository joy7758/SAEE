# SAEE Local Trial Preflight Snapshot

local_trial_preflight_snapshot_v0_1: true
snapshot_type: local_trial_preflight_snapshot
preflight_scope: local_controlled_trial_demo_operator_check
status: pass
ready_to_start: true
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

This snapshot records whether the current local machine appears ready for a
human to run the SAEE local MVP trial path. It is an operator preflight record,
not product validation and not a production readiness claim.

## Local Checks

- selected_python: `./.venv/bin/python`
- selected_python_source: `local_venv`
- prefers local `.venv` Python: true
- FastAPI import available: true
- Uvicorn import available: true
- backend port: 8000
- backend port open: false
- backend owned by SAEE: false
- backend port usable: true
- landing port: 8765
- landing port open: false
- landing owned by SAEE: false
- landing port usable: true
- required files present: true

## Required Files

- backend_entrypoint: true
- backend_requirements: true
- landing_app: true
- landing_index: true

## Missing Or Blocking Items

- none

## Boundary

This snapshot uses only local file checks, Python import checks, and localhost
loopback probes. It does not install dependencies, start servers, open a
browser, call external services, contact customers, process customer data,
modify backend behavior, modify runtime/kernel/API schema, expose private core,
launch product, close production blockers, or claim production readiness.

## Next Human Action

If status is pass, a human may start or use the local trial demo; if status is hold, resolve missing local dependencies or port conflicts first.
