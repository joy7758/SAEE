# SAEE Local Trial Make Targets v0.1

Status: local convenience targets available.

This document records Makefile convenience targets for the existing local SAEE
trial session manager. These targets improve local reviewer usability only.
They do not modify product behavior, start external services, open a browser,
install dependencies, contact customers, close commercial blockers, launch the
product, or claim production readiness.

## Scope

- target scope: local trial command discoverability
- backing tool: `scripts/saee_local_trial_session.py`
- backend route exercised by the local demo: `/experiment/run`
- local landing page: `http://127.0.0.1:8765/`
- demo button: `Run Demo Battle`
- detached local child processes: true

## Make Targets

Check whether this machine can start the local demo:

```bash
make local-trial-preflight
```

Start the local backend and static landing page:

```bash
make try-local
```

`make try-local` uses the existing session manager with a 20-second local readiness window so slower local cold starts can become healthy before the command returns.
The session manager starts the backend and static landing page as detached local
child processes, so the trial remains available after `make try-local` returns
in short-lived operator shells. Use `make local-trial-stop` to stop the recorded
local PIDs.

After start, `make try-local` also refreshes the local commercial trial operator
status card through `scripts/saee_commercial_trial_operator_status.py`, so the
agent-readable operator surface reflects the currently running local trial
session without authorizing commercial execution.

Check whether the local trial session is running:

```bash
make local-trial-status
```

`make local-trial-status` also refreshes the same read-only commercial trial
operator status card after reporting the current local session state. This is
status bookkeeping only; it does not start a trial, stop a trial, close a
commercial blocker, or authorize production execution.

Stop only the local trial processes recorded by the session manager:

```bash
make local-trial-stop
```

After stop, the same operator status card is refreshed so it no longer reports
the local trial as running.

## Human Trial Flow

1. Run `make local-trial-preflight`.
2. If the preflight status is `pass`, run `make try-local`.
3. Open `http://127.0.0.1:8765/` manually.
4. Click `Run Demo Battle`.
5. Review the recommended agent and report summary.
6. Run `make local-trial-stop` when finished.

## Boundary

- production_ready: false
- customer_validated: false
- customer_contacted: false
- customer_data_allowed: false
- paid_trial_enabled: false
- payment_provider_configured: false
- product_launched: false
- public_sdk_released: false
- external_ai_assistant_tested: false
- external_validation_claim: false
- external_calls_made: false
- browser_opened_by_script: false
- dependencies_installed_by_script: false
- detached_local_child_processes: true
- refreshes_operator_status_on_start: true
- refreshes_operator_status_on_status: true
- refreshes_operator_status_on_stop: true
- private_core_exposed: false
- api_schema_modified: false
- runtime_modified: false
- backend_modified: false
- kernel_modified: false

## Non-Goal

These targets are not a deployment system, not a production launcher, not a
customer-validation path, and not a commercial blocker closure mechanism.
