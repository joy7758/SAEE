# SAEE Controlled Trial Operator Packet

Status: local trial operator packet available; not customer validation and not
production launch.

## Purpose

This folder gives a human operator a consistent way to run one local SAEE MVP
trial and record the result. It connects the existing local quickstart and local
E2E proof to a concrete observation sheet.

## Use

1. Start the local backend.
2. Serve the local landing page.
3. Click `Run Demo Battle`.
4. Record the result in `local_trial_session_template.json` or
   `local_trial_observation_sheet.md`.
5. Keep all boundary flags false unless a reviewer actually observed a boundary
   violation.

## Files

- `local_trial_session_template.json`: machine-readable session record.
- `local_trial_observation_sheet.md`: human-readable observation sheet.

## Boundary

This packet does not contact customers, collect customer data, process
production data, call external services, test external AI assistants, launch
SAEE, release an SDK, expose private core, or mark SAEE production-ready.
