# Usage Examples

Status: conceptual usage examples only.

These examples describe how a developer would use a public SAEE abstraction.
They are not executable SDK calls and do not expose implementation logic.

## Example 1: Request a Bounded Run

Intent:

```text
Run a bounded evolution experiment with deterministic configuration.
```

Conceptual request:

```text
generation_count: 100
population_size: fixed
deterministic_seed: enabled
logging_level: summary
report_profile: phase_space
```

Conceptual response:

```text
run_status: completed
dominant_regime: stable_regime
dominant_basin: stable_lineage_basin
collapse_events: 0
```

## Example 2: Read Stability Summary

Intent:

```text
Inspect whether a run stayed within the stable regime.
```

Conceptual output:

```text
population_stability: stable
fitness_variance_tendency: converging
lineage_integrity: preserved
```

## Example 3: Export Academic-Safe Summary

Intent:

```text
Create a report for review without exposing the private kernel.
```

Allowed fields:

- aggregate population statistics;
- regime labels;
- attractor labels;
- candidate regularity labels;
- non-claim boundaries.

Forbidden fields:

- implementation source;
- runtime orchestration;
- fitness calculation;
- selection procedure;
- mutation procedure;
- lineage construction internals.
