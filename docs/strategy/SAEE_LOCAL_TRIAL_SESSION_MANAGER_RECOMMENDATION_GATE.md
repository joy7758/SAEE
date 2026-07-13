# SAEE Local Trial Session Manager Recommendation Gate

recommendation_gate:
  feature_or_direction: local_trial_session_manager_v0_1
  target_customer_need: "A reviewer wants a simple local way to start, inspect, and stop the SAEE demo session."
  answer: recommend
  recommend_for_local_trial_onboarding: true
  recommend_for_production: false
  recommend_for_customer_validation_claim: false
  recommend_for_external_validation_claim: false
  reasons_to_recommend:
    - "It makes the existing local backend and landing-page demo easier to try without changing product behavior."
    - "It preserves a clear localhost-only boundary and does not open browsers or call external services."
    - "It gives AI agents a machine-readable entrypoint for local trial operation."
    - "It now includes a local preflight command so operators can see missing Python dependencies or port conflicts before attempting a demo."
    - "It prefers `.venv/bin/python` when present, aligning the start path with cold-start preflight while still installing no dependencies automatically."
    - "It uses a 20-second local readiness window for slower localhost cold starts."
    - "It launches local trial child processes in a detached local session so the demo remains available after the start command returns."
  reasons_not_to_recommend:
    - "It is not a production deployment path."
    - "It does not prove customer validation or external AI assistant validation."
    - "It requires runtime dependencies to already exist in the selected Python environment."
  decomposition:
    - blocker: "Potential confusion with production deployment."
      subsystem: "Controlled trial onboarding"
      fix_task: "Document localhost-only scope and false production/customer/external-validation claims."
      acceptance_criteria: "Docs, smoke, and agent-index keep production_ready=false and product_launched=false."
      status: fixed
    - blocker: "Automatic dependency installation could create supply-chain risk."
      subsystem: "Trial operator tooling"
      fix_task: "Do not install dependencies from the session manager."
      acceptance_criteria: "Smoke verifies dependencies_installed_by_script=false and no pip install token in the script."
      status: fixed
    - blocker: "Automatic browser opening could blur human-controlled trial boundaries."
      subsystem: "Trial operator tooling"
      fix_task: "Require humans to open the local URL manually."
      acceptance_criteria: "Smoke verifies browser_opened_by_script=false and no webbrowser.open token in the script."
      status: fixed
    - blocker: "First-time trial failures can be hard to diagnose when dependencies or ports are not ready."
      subsystem: "Trial operator tooling"
      fix_task: "Add a local-only preflight command that checks required files, selected Python dependency availability, and localhost port ownership."
      acceptance_criteria: "Smoke verifies preflight is exposed by describe output and reports boundary-safe local-only status."
      status: fixed
  final_decision: "Recommend for local trial onboarding only; do not recommend as production launch or customer validation evidence."
  evidence:
    docs:
      - phase_b_product/commercial_readiness/LOCAL_TRIAL_SESSION_MANAGER_V0_1.md
    tests:
      - scripts/saee_local_trial_session_smoke.py
    examples:
      - "python3 scripts/saee_local_trial_session.py --json describe"
      - "python3 scripts/saee_local_trial_session.py --json preflight"

Boundary:

```yaml
local_trial_session_manager_v0_1: true
local_trial_session_preflight_v0_1: true
session_scope: local_controlled_trial_demo_operator_tool
prefers_local_venv_python: true
detached_local_child_processes: true
production_ready: false
customer_validated: false
customer_contacted: false
product_launched: false
public_sdk_released: false
external_validation_claim: false
external_calls_made: false
browser_opened_by_script: false
dependencies_installed_by_script: false
private_core_exposed: false
api_schema_modified: false
runtime_modified: false
backend_modified: false
kernel_modified: false
recommend_for_production: false
```
