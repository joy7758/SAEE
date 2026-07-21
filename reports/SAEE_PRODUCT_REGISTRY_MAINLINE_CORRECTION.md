# SAEE Product Registry Mainline Correction

## Drift

```text
MAINLINE_DRIFT_DETECTED=true
DRIFT_SOURCE=governance/registry/product-registry.json
CONFLICT=SAEE_Governance_was_excluded_while_Constitution_requires_it_as_a_target_version
```

`SAEE Development Constitution v1.1.1` fixes the final customer-version target
to exactly:

```text
SAEE Evidence
SAEE Evaluation
SAEE Governance
```

The pre-correction product registry and validator still rejected `SAEE
Governance` as a future concept. That rule would prevent the integration
mainline from ever reaching its constitutional product outcome.

## Correction

The product registry now separates three concepts:

1. `SAEE` is the umbrella Digital Biosphere Evolution Engine, not one of the
   three customer-version targets.
2. `SAEE Evidence`, `SAEE Evaluation` and `SAEE Governance` are the exact
   target customer-version set.
3. `Agent Evidence Receipt` remains a legacy external alpha product and
   migration source during the transition. It is not a fourth target version,
   and its runtime has not been transferred.

`SAEE Governance` is recorded as `target_not_implemented`. This makes the
target discoverable without upgrading implementation, launch, customer or
production truth.

## Agent Recommendation Gate

Decision: `recommend` for the bounded registry correction.

An Agent can now discover the target family, understand that the legacy
Receipt product is transitional, and route future work toward the correct
version without inventing a fourth product. No runtime or capability behavior
changes.

## Non-claims

- `SAEE Governance` is not implemented, customer-validated, launched or
  production-ready.
- Agent Evidence source code and runtime are not migrated.
- The Receipt MCP and Aliyun product `68658` are not transferred.
- The product registry is not a capability fact source.
