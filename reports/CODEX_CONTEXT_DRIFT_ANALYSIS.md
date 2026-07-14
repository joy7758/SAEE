# Codex Context Drift Analysis

## Scope

Compared without modification:

- `.codex/context.md`
- `scripts/codex_context_check.py`
- `AGENTS.md`
- `README.md`
- `llms.txt`
- `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`

## 1. Current identity definition

The current constitutional hierarchy is:

```text
theory_identity=Silicon-Amplified Evolutionary Ecology
engineering_core=Digital Biosphere Evolution Engine
external_capability_projection=Agent Readiness Infrastructure / Capability
evidence_role=SAEE Evidence and Immune Subsystem
audit_first_reframe=false
```

`.codex/context.md` and `AGENTS.md` follow this hierarchy. `README.md` and the
top of `llms.txt` still lead with the external Agent Readiness product surface,
but both preserve Digital Biosphere as the engineering core elsewhere.

## 2. Old identity

The exact legacy sentence required by `scripts/codex_context_check.py` is:

```text
SAEE is an AI agent long-term stability evaluation and decision infrastructure system.
```

That sentence remains historical compatibility language in a later section of
`llms.txt`, but it is no longer the canonical root identity in
`.codex/context.md`.

## 3. Why drift occurred

The Constitution v1.1 work updated `.codex/context.md` from the old evaluation
infrastructure identity to the theory/core/projection hierarchy. The exact-token
validator was not updated in the same change. As a result:

```text
context_contract=new_identity
validator_contract=old_identity
atomic_sync=false
```

This is validation/governance drift caused by a non-atomic update, not runtime
or evaluator failure.

## 4. Which identity complies with the Constitution?

The Constitution-compatible future canonical identity is:

1. SAEE implements Silicon-Amplified Evolutionary Ecology.
2. Its engineering core is Digital Biosphere Evolution Engine.
3. Agent Readiness is an external capability/product projection.
4. Evidence and audit remain an Evidence/Immune subsystem.

`Agent Readiness Infrastructure` is valid as a product projection, not as a
replacement for the theory identity or engineering core. The old long-term
stability sentence may remain as historical or explanatory text, but must not
be the mandatory canonical identity token.

## 5. What should future Codex read?

In order:

1. `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
2. `governance/README.md`
3. `.codex/context.md`
4. `capability-package/manifest.json#canonical_inventory`
5. relevant asset/repository/MCP/product registries

The checker should validate this authority chain and stable identity fields,
not one deprecated prose sentence.

## 6. Does Phase 0.5 need a repair?

Yes, but this audit task explicitly forbids making the repair.

The next bounded stabilization PR should:

- change `scripts/codex_context_check.py` to require the constitutional theory,
  engineering-core and product-projection tokens;
- reject audit-first or product-replaces-core drift;
- preserve `AGENTS.md`, `.codex/context.md`, README and `llms.txt` roles without
  requiring identical marketing headings;
- commit the pending Constitution v1.1 authority package atomically;
- run the full `make check` chain.

## Reproduction

```text
$ python3 scripts/codex_context_check.py
SAEE_CODEX_CONTEXT_CHECK: FAIL: .codex/context.md missing tokens: AI agent long-term stability evaluation
```

## Classification

```text
root_cause=GOVERNANCE_VALIDATION_CONTRACT_DRIFT
business_code_bug=false
runtime_bug=false
identity_decision_required=false
identity_validator_alignment_required=true
repair_phase=PHASE0_5
blocks_phase1=true
```
