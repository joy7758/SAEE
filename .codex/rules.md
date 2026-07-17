# SAEE Codex Rules

## Constitutional Authority

Every Codex change must follow `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`.
Resolve `capability-package/manifest.json#canonical_inventory`, run the duplicate-build
check and the Agent Recommendation Gate, identify the affected evolution subsystem,
and define claims, non-claims and staged truth before changing behavior.

The Agent Evidence Project belongs to `SAEE Evidence and Immune Subsystem`.
This ownership does not mean its source code or runtime has been migrated. Reuse
existing SAEE evidence / trace / receipt capabilities before proposing migration.

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
2. Read the development constitution and canonical capability inventory.
3. Run the duplicate-build and Agent Recommendation gates.
4. Check task scope.
5. Confirm allowed and forbidden files.
6. Run `python3 scripts/saee_development_constitution_smoke.py` for constitutional,
   architecture, product-boundary or evidence-subsystem changes.
7. Run task-specific validation.

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
