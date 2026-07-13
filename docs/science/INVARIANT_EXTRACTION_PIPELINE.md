# Invariant Extraction Pipeline

## Purpose

The Invariant Extraction Pipeline turns observed SAEE runs into falsifiable
candidate laws.

It does not create new evolution rules.

## Inputs

- `saee_experiments/reports/stability_report.json`
- `saee_experiments/reports/lineage_statistics.json`
- `saee_experiments/output/demo-run/evolution_trace.jsonl`
- `saee_phase2/output/demo-run/invariants.json`
- `saee_phase2/output/demo-run/evolution_laws.json`
- `saee_v1_2/results/` if local empirical-alignment runs exist

## Pipeline

1. Collect local run records.
2. Normalize each record into comparable state vectors.
3. Identify repeated stable relations.
4. Assign each relation a claim status.
5. Test the relation against additional local runs.
6. Downgrade or reject relations contradicted by new evidence.
7. Promote only repeated local relations to `local_empirical_law`.

## Candidate Invariant Families

### lineage_integrity_invariant

Question: does the lineage graph preserve valid parent-child endpoints across
long runs?

Current evidence: `lineage_integrity_preserved == true`.

Current status: `local_observation`.

### population_viability_invariant

Question: does the population remain at configured size under the v1.0
selection loop?

Current evidence: final population is 8 after 100 generations.

Current status: `local_observation`.

### collapse_absence_condition

Question: under deterministic v1.0 settings, what conditions avoid collapse?

Current evidence: collapse_event_count is 0 in the current 100-generation run.

Current status: `candidate_pattern`.

### branching_density_range

Question: does the lineage DAG settle into a reproducible edge-to-node range?

Current evidence: branching_density is 1.967822 in the current
100-generation run.

Current status: `candidate_pattern`.

## Falsification Rules

A candidate invariant must be downgraded or rejected if:

- a deterministic rerun with the same config produces contradictory output;
- a controlled local run in the allowed generation range breaks the relation;
- lineage integrity fails;
- collapse appears under the same claimed conditions;
- the claim relies on a side-layer that modifies runtime behavior.

## Boundary

No invariant extracted here is an external universal law. All current claims
are local observations or candidate patterns unless reproduced across multiple
controlled local runs and explicitly promoted.
