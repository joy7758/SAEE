# Regime Classification Framework

## Purpose

The Regime Classification Framework classifies observed SAEE behavior without
modifying the evolution runtime.

It consumes local reports and traces, especially:

- `saee_experiments/output/demo-run/evolution_trace.jsonl`
- `saee_experiments/reports/stability_report.json`
- `saee_experiments/reports/lineage_statistics.json`
- `saee_phase2/output/demo-run/regime_transition_log.json`

## Regime Taxonomy

### stable_regime

Definition: population remains viable, lineage integrity is preserved, and
fitness variance does not expand over the observation window.

Observable criteria:

- collapse event count is zero;
- final population remains at configured size;
- lineage integrity is preserved;
- variance tendency is stable or converging.

### exploratory_regime

Definition: population remains viable while turnover, mutation accumulation, or
branching density indicates active search.

Observable criteria:

- collapse event count is zero;
- population turnover remains nonzero;
- branching density remains above zero;
- persistent structures do not fully dominate all generations.

### chaotic_regime

Definition: population remains alive but state signatures and fitness variance
show unstable oscillation.

Observable criteria:

- collapse event count may be zero;
- variance tendency is diverging;
- regime labels alternate frequently;
- lineage branching density changes abruptly.

### collapse_regime

Definition: population viability fails or selection produces an empty or
near-empty survivor set.

Observable criteria:

- collapse event count is greater than zero;
- survivor count reaches zero or population drops below the viable threshold;
- lineage continuity may become impossible to preserve.

## Current Local Classification

Based on `saee_experiments/reports/stability_report.json` and
`saee_experiments/reports/lineage_statistics.json`, the current v1.0
long-horizon run is classified as:

```text
primary_regime: stable_regime
secondary_behavior: exploratory_regime
claim_status: local_observation
```

Evidence:

- generation_count: 100
- collapse_event_count: 0
- final_population: 8
- convergence_tendency: converging
- lineage_integrity_preserved: true
- branching_density: 1.967822

The secondary exploratory label is descriptive only. It reflects sustained
population turnover and nonzero lineage branching, not a new runtime regime.

## Classification Boundary

Regime classification must not feed back into mutation, selection, fitness, or
lineage logic. It is a label on observed behavior, not an evolution mechanic.
