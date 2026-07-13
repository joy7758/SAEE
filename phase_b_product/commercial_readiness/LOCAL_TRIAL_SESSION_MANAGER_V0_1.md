# SAEE Local Trial Session Manager v0.1

local_trial_session_manager_v0_1: true
local_trial_session_preflight_v0_1: true
preflight_scope: local_controlled_trial_demo_operator_check
session_scope: local_controlled_trial_demo_operator_tool
prefers_local_venv_python: true
trial_status: local_demo_available
local_backend_required: true
local_static_page_required: true
demo_endpoint: /experiment/run
demo_button: Run Demo Battle
detached_local_child_processes: true
detached local child processes: enabled
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
external_calls_made: false
browser_opened_by_script: false
dependencies_installed_by_script: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
backend_modified: false
kernel_modified: false

## Purpose

This file describes the local operator tool for trying the SAEE MVP demo as a
repeatable localhost session. It improves trial onboarding by turning the
existing backend and landing-page commands into a discoverable start/status/stop
workflow.

It does not change SAEE product behavior, backend logic, API schema, runtime,
kernel, private core, pricing, billing, customer status, or production
readiness.

## Commands

Describe the local trial session manager:

```bash
python3 scripts/saee_local_trial_session.py --json describe
```

Check whether this machine is ready to start the local trial session:

```bash
python3 scripts/saee_local_trial_session.py --json preflight
```

The preflight checks only local files, the selected Python executable, FastAPI
and Uvicorn import availability when the backend is not already running, and
whether the backend and landing ports are either unused or already owned by the
SAEE local services.

By default, the session manager prefers `.venv/bin/python` when that local
virtual environment exists. If it does not exist, it falls back to the current
Python interpreter. This keeps `make try-local` aligned with the cold-start
preflight without installing dependencies automatically.

Check whether the local trial session is already running:

```bash
python3 scripts/saee_local_trial_session.py status
```

Start the local backend and local static landing page:

```bash
python3 scripts/saee_local_trial_session.py start --wait-seconds 20
```

The default start readiness window is 20 seconds. This only affects local
localhost startup robustness and does not change product behavior or production
readiness.

The start command launches the backend and static landing page as detached local
child processes with closed standard input. This keeps the local trial session
available after the start command returns in short-lived operator shells. The
recorded process IDs remain owned by the session manager and should be stopped
with the stop command.

If your default `python3` environment does not include FastAPI and Uvicorn, use
a prepared local virtual environment explicitly:

```bash
python3 scripts/saee_local_trial_session.py start --python /path/to/python --wait-seconds 20
```

Stop only the processes started by the local trial session manager:

```bash
python3 scripts/saee_local_trial_session.py stop
```

## Human Trial Flow

1. Run the start command.
2. If start fails, run the preflight command and resolve local Python or port
   issues manually.
3. Open `http://127.0.0.1:8765/` manually in a browser.
4. Click `Run Demo Battle`.
5. Confirm the page renders `recommended_agent`, `confidence_score`, ranking,
   and failure-mode summary.
6. Run the stop command when finished.

The backend demo endpoint is:

```text
POST http://127.0.0.1:8000/experiment/run
```

## Boundary

The session manager is local-only. It does not open a browser, install
dependencies, call external services, contact customers, process customer data,
enable payment, publish a product, release an SDK, modify API schema, modify
runtime behavior, modify backend logic, modify kernel logic, or expose private
core.

The session manager improves usability for local review and controlled trial
rehearsal only. It is not a production deployment tool.
