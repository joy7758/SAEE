# SAEE Universal Law Extraction v1.0

Status: candidate law set derived from a Frozen Empirical Phase Space Object.

## Boundary

This artifact does not extend SAEE, modify runtime, add mechanisms, run new
experiments, or claim external validation.

It extracts falsifiable candidate laws from existing artifacts only:

- `docs/science/phase_diagram/SAEE_PHASE_SPACE_V1.json`
- `docs/science/phase_diagram/REGIME_TRANSITION_GRAPH.json`
- `docs/science/phase_diagram/ATTRACTOR_BASIN_MAP.json`
- `docs/science/phase_diagram/INVARIANT_CLUSTER_SPACE.json`
- `saee_experiments/reports/stability_report.json`
- `saee_experiments/reports/lineage_statistics.json`
- `saee_experiments/output/demo-run/drift_report.json`
- `saee_phase2/output/demo-run/attractor_map.json`
- `saee_phase2/output/demo-run/regime_transition_log.json`

## System Characterization

SAEE under current kernel constraints behaves as a non-open-ended evolutionary
system with strong attractor dominance.

Observed phase-space facts:

```text
dominant_regime: stable_regime
dominant_basin: stable_lineage_basin
observed_transition: stable_regime -> stable_regime
collapse_observed: false
cross_regime_transition_observed: false
lineage_integrity_preserved: true
```

## Candidate Laws

### 1. Attractor Dominance Law

In a constrained evolutionary kernel with stable selection pressure, bounded
mutation entropy, a smooth monotonic selection function, and no external
diversity perturbation, the system converges to a single dominant attractor
basin.

Observed expression:

```text
stable_lineage_basin dominates the observed phase space
```

Falsification condition:

An unchanged constrained run shows more than one dominant attractor basin or
the collapse basin becomes dominant.

### 2. Regime Non-Transition Law

Regime transitions vanish when fitness variance contracts below the observed
stability region and mutation does not introduce directional bias.

Observed expression:

```text
stable_regime -> stable_regime
probability: 1.0
```

Falsification condition:

An unchanged constrained run records any cross-regime transition while fitness
variance remains in the current convergent range.

### 3. Lineage Stability Law

Lineage DAGs remain structurally stable when reproduction is constrained by
single-loop selection, branching factor is bounded, and cross-lineage
recombination is absent.

Observed expression:

```text
node_count: 808
edge_count: 1590
lineage_integrity_preserved: true
```

Falsification condition:

A lineage edge references a missing endpoint, branching density grows without
bound, or the graph ceases to be a DAG under unchanged constraints.

### 4. Bounded Diversity Law

Population diversity remains bounded when the fitness function compresses
behavioral space, selection pressure favors convergence, and mutation does not
explore orthogonal dimensions.

Observed expression:

```text
population_count: 8 for 100/100 generations
mean_population_turnover: 0.545531
collapse_event_count: 0
```

Falsification condition:

Population count escapes configured bounds, collapse occurs, or additional
dominant basins appear under unchanged constraints.

### 5. Fitness Convergence Law

Fitness variance decreases over time when selection is deterministic or
near-deterministic, environmental signals are static or abstracted, and
mutation magnitude is low.

Observed expression:

```text
convergence_tendency: converging
first_10_variance_mean: 0.000001839
last_10_variance_mean: 0.000000705
variance_ratio: 0.383360522
```

Falsification condition:

Fitness variance diverges, or last-window variance repeatedly exceeds
first-window variance, while all stated constraints remain unchanged.

## Non-Claims

- These are candidate laws, not externally validated laws.
- This is not a universal-law claim.
- This is not open-ended evolution.
- This is not a new kernel or system layer.
- This is not generated from new data.
