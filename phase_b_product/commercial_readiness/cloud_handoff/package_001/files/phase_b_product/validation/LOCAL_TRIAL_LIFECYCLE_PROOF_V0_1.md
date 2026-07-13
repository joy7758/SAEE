# SAEE Local Trial Lifecycle Proof v0.1

local_trial_lifecycle_proof_v0_1: true
proof_scope: local_trial_session_start_status_stop
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
external_calls_made: false
browser_opened_by_script: false
dependencies_installed_by_script: false
private_core_exposed: false
blockers_closed_by_lifecycle_proof: 0
detached_local_child_processes: true

## Purpose

This proof records whether the local tryout session can be started, observed as
running, stopped, and observed as not running. It strengthens controlled-preview
trial operations without changing product behavior.

It also verifies detached local child processes so `make try-local` remains
usable after the command returns in short-lived operator shells.

## Run

```bash
python3 scripts/saee_local_trial_lifecycle_proof.py
python3 scripts/saee_local_trial_lifecycle_proof_smoke.py
```

## Boundary

The proof uses localhost only. It does not open a browser, call external
services, install dependencies, contact customers, process customer data, close
commercial blockers, launch product, or claim production readiness.

It does not call external services and does not claim production readiness.
