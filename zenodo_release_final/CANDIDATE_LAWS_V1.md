# Candidate Laws v1

Status: Zenodo academic publication package draft, local only.

## Boundary

These are falsifiable candidate laws derived from the frozen empirical phase
space object. They are not universal laws and are not externally validated.

No implementation details are disclosed.

## Law 1: Attractor Dominance

Statement:

Under bounded variation entropy, stable pressure, and no external diversity
perturbation, the observed system converges to one dominant attractor basin.

Observed expression:

```text
stable_lineage_basin dominates the observed phase space
```

Falsification condition:

An unchanged constrained observation shows more than one dominant attractor
basin, or the collapse basin becomes dominant.

## Law 2: Regime Non-Transition

Statement:

Regime transitions vanish when variance contracts into the observed stability
region and variation does not introduce directional bias.

Observed expression:

```text
stable_regime -> stable_regime
probability: 1.0
```

Falsification condition:

An unchanged constrained observation records a cross-regime transition while
variance remains in the current convergent range.

## Law 3: Lineage Stability

Statement:

Lineage topology remains structurally stable when reproduction remains
constrained, branching is bounded, and cross-lineage recombination is absent.

Observed expression:

```text
node_count: 808
edge_count: 1590
lineage_integrity_preserved: true
```

Falsification condition:

A lineage edge references a missing endpoint, branching density grows without
bound, or the graph ceases to be a DAG under unchanged constraints.

## Law 4: Bounded Diversity

Statement:

Population diversity remains bounded when behavior space is compressed and
variation does not explore orthogonal dimensions.

Observed expression:

```text
population_count: 8 for 100/100 generations
collapse_event_count: 0
```

Falsification condition:

Population count escapes configured bounds, collapse occurs, or additional
dominant basins appear under unchanged constraints.

## Law 5: Fitness Convergence

Statement:

Observed variance decreases over time when environmental signals are static or
abstracted and variation magnitude remains low.

Observed expression:

```text
convergence_tendency: converging
first_10_variance_mean: 0.000001839
last_10_variance_mean: 0.000000705
variance_ratio: 0.383360522
```

Falsification condition:

Variance diverges, or last-window variance repeatedly exceeds first-window
variance while stated constraints remain unchanged.

## Non-Claims

- Candidate laws only.
- Not universal laws.
- Not external validation.
- Not open-ended evolution.
- Not implementation disclosure.

