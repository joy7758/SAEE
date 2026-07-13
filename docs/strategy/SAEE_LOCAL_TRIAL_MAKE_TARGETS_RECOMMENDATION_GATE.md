# SAEE Local Trial Make Targets Recommendation Gate

answer: recommend

recommend_for_local_trial_convenience: true
recommend_for_production: false

## Need

A local reviewer needs a discoverable, low-friction way to start, inspect, and
stop the existing SAEE local MVP trial session.

## Recommendation

Recommend adding Makefile aliases for the existing local trial session manager
because this improves local tryout ergonomics without changing product
behavior.

## Scope

- `make local-trial-preflight`
- `make try-local`
- `make local-trial-status`
- `make local-trial-stop`

`make try-local` starts the existing session manager with a 20-second local readiness window. This is a local robustness setting only, not a production deployment setting. The session manager uses detached local child processes so the demo remains available after the Make command returns, and `make local-trial-stop` remains the bounded stop path.

`make try-local`, `make local-trial-status`, and `make local-trial-stop`
refresh the read-only commercial trial operator status card after reporting or
changing the local session state. This keeps agent-readable status aligned with
the actual local tryout state without authorizing evidence collection, cloud
sync, blocker closure, or launch.

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

## Decision

This is recommendable as a local controlled-preview convenience surface. It is
not recommendable as a production deployment or customer-validation claim.
