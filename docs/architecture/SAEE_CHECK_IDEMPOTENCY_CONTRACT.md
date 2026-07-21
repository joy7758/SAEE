# SAEE Check Idempotency Contract v1

## Purpose

This contract makes repository validation portable and preserves the evidence
scene. It strengthens the Evolutionary Archive / Rollback Immune System; it is
not a new audit product capability.

## Commands

| Command | Writes caller tracked paths | External Provider evidence | Purpose |
|---|---:|---|---|
| `make check` | no | `NOT_REQUIRED` | Run the complete legacy validation graph in a disposable tracked-only local clone. |
| `python3 scripts/mainline_guard.py` | no | `NOT_REQUIRED` | Run the mainline guard through the same isolation boundary. |
| `make generate` | yes | optional | Explicitly refresh mainline-derived artifacts in the current worktree. |
| `make check-generated` | no | optional | Generate in a disposable clone and compare canonical content with the caller's tracked artifacts. |
| `make check-provider-evidence` | no | required | Strictly validate explicitly supplied local external Provider runtime evidence. |

Normal checks copy tracked and non-ignored untracked development files into a
local disposable clone. They do not copy `/output/`, secrets, caches, local
runtime state, or any other ignored file.

## Generated-content comparison

`check-generated` compares the source snapshot with results generated in the
disposable clone. It canonicalizes JSON ordering and excludes only three
declared runtime metadata fields from the equality decision:

- `generated_at`
- `detached_local_child_processes`
- `local_trial_started_by_manager`

These values describe generation time or the operator machine, not canonical
repository capability truth. Any other generated-content difference is
reported by path and fails the check. No `git restore`, `git checkout`, or
`git reset` cleanup is used.

## External Provider evidence states

- `NOT_REQUIRED`: normal offline check does not require the evidence.
- `NOT_AVAILABLE`: strict validation requires evidence, but none was supplied.
- `PRESENT_UNVERIFIED`: some expected evidence exists but the complete set has not been verified.
- `VERIFIED`: all supplied external evidence passed digest, schema, binding, truth-boundary, and credential-leak checks.
- `INVALID`: supplied evidence exists but fails validation.

Absence in normal mode is not reported as successful Provider validation.
Absence in strict mode exits nonzero with `EXTERNAL_EVIDENCE_NOT_AVAILABLE`.

## Boundaries

Clean and repeatable repository checks establish build and capability-fact
validation reliability only. They do not establish Agent execution truth,
production safety, regulatory compliance, customer validation, marketplace
publication, or production readiness.
