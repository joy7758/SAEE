# SAEE Phase Diagram v1.0

Status: Science Lock compliant local phase-space compression.

## Boundary

This artifact does not modify SAEE runtime, kernel, fitness, selection,
mutation, lineage, or experiment behavior.

No new data generation was performed. The phase diagram compresses existing
observational outputs only.

## Sources

- `saee_experiments/output/demo-run/evolution_trace.jsonl`
- `saee_experiments/reports/stability_report.json`
- `saee_experiments/reports/lineage_statistics.json`
- `saee_experiments/output/demo-run/drift_report.json`
- `saee_experiments/output/demo-run/emergence_report.json`
- `saee_phase2/output/demo-run/regime_transition_log.json`
- `saee_phase2/output/demo-run/attractor_map.json`
- `saee_phase2/output/demo-run/invariants.json`
- `saee_v0_6/output/demo-run/observability_summary.json`
- `saee_v0_7/output/demo-run/reflexive_summary.json`
- `saee_v0_8/output/demo-run/stability_summary.json`

## Regime Transition Graph

Observed nodes:

- `stable_regime`

Configured but unobserved nodes:

- `exploratory_regime`
- `chaotic_regime`
- `collapse_regime`

Observed edge:

```text
stable_regime -> stable_regime
probability: 1.0
transition_count: 5 / 5
confidence: local_observation
```

No cross-regime transition is present in existing logs.

## Attractor Basin Map

Observed primary basin:

```text
stable_lineage_basin
stability_score: 1.0
evidence: population_count=8 for 100/100 generations, collapse_event_count=0, lineage_integrity_preserved=true
```

Observed secondary behavior:

```text
exploration_basin
stability_score: 0.545531
evidence: mean_population_turnover=0.545531, branching_density=1.967822
```

Unobserved sink:

```text
collapse_sink
stability_score: 0.0
evidence: collapse_event_count=0, collapse_events.log empty
```

## Invariant Cluster Space

| Invariant | Category | Classification | Stability Score |
| --- | --- | --- | --- |
| lineage_integrity_invariant | lineage_statistics | local_observation | 1.0 |
| population_viability_invariant | population_stability | local_observation | 1.0 |
| fitness_convergence_tendency | fitness_convergence_trends | candidate_pattern | 0.616639478 |
| branching_density_range | branching_density | candidate_pattern | 1.0 |

## Unified Phase Space

The unified machine-readable representation is:

- `docs/science/phase_diagram/SAEE_PHASE_SPACE_V1.json`

## Non-Claims

- No runtime extension.
- No new simulation.
- No speculative physics.
- No external validation.
- No universal law.
- No phase boundary estimation beyond existing observations.
