# SAEE v1.2 Empirical Invariance Test

agent_readable:
  schema: saee.universality_test.readme.v1
  module: saee_v1_2/universality_test
  source_system: saee_v1_2/parasitic_phase
  modifies_parasitic_phase: false
  external_validation_claim: false
  broad_theory_claim: not_proven
  production_claim: false

## Purpose

This module performs a tested-system empirical invariance check for the SAEE
v1.2 parasitic phase research system.

It compares:

- `DBI-1`: the existing `saee_v1_2/parasitic_phase` system, imported without
  changing its implementation.
- `DBI-2`: an independent Digital Biosphere Instance with randomized policy
  vectors, per-agent replication thresholds, non-uniform resource topology, and
  a small-world interaction graph.
- `DBI-3`: a public-goods imitation network with graph-local interaction,
  mutate-policy actions, and ER/WS/BA topology presets.

## Recommendation Gate

```text
answer: conditional
recommendation: conditional_internal_experiment
```

Recommend for:

- internal scientific replication,
- invariance testing,
- publication-preparation evidence.

Do not recommend for:

- real-world validation claims,
- production governance,
- broad multi-agent theory claims.

## Run

```bash
PYTHONDONTWRITEBYTECODE=1 python3 saee_v1_2/universality_test/run_universality_experiment.py
```

Legacy DBI-1/DBI-2 outputs:

- `results/universality_metrics.json`
- `results/universality_report.md`
- `results/universality_comparison.svg`

## Claim Boundary

Allowed:

```text
The tested-system check asks whether the parasitic phase signature is observed
across DBI-1, DBI-2, and DBI-3 under sampled seeds and governance settings.
```

Forbidden:

```text
Broad invariance is proven.
The result validates real-world multi-agent systems.
The governance intervention policy is production ready.
```
