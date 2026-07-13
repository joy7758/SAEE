# SAEE Codex Rules

## Allowed

Can modify when the task scope permits:

- documentation
- landing pages
- scenario templates
- tests
- scripts
- agent-readable context and index surfaces

## Forbidden

Never modify without explicit instruction:

- private core
- kernel
- hidden algorithms
- scoring mechanism
- runtime behavior
- backend behavior
- API contract schema

## Before Changing Files

1. Check `.codex/current_state.md`.
2. Check task scope.
3. Confirm allowed and forbidden files.
4. Run validation.

## Never Claim

Never claim these unless explicitly proven by current authoritative evidence:

- production ready
- customer validated
- external validated
- product launched
- private core public

## Commercial State Separation

Keep these states separate:

- local smoke pass
- internal proxy validation
- manual human inspection
- external assistant validation
- customer validation
- production readiness

Passing one state does not imply another state.
