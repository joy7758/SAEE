# SAEE Data Descriptor

Status: observational descriptor, implementation excluded.

## Object Name

SAEE: Silicon-Amplified Evolutionary Ecology.

## Object Type

```text
frozen_empirical_phase_space_object
```

## Observation Type

```text
local-only long-horizon observational experiment
```

## Observed Measures

| Measure | Value |
| --- | --- |
| Generations | 100 |
| Final population | 8 |
| Collapse events | 0 |
| Fitness variance tendency | converging |
| Lineage graph type | lineage DAG |
| Lineage nodes | 808 |
| Lineage edges | 1590 |
| Branching density | 1.967822 |
| Mean population turnover | 0.545531 |

## Phase-Space Labels

| Field | Value |
| --- | --- |
| Dominant regime | `stable_regime` |
| Dominant basin | `stable_lineage_basin` |
| Observed transition | `stable_regime -> stable_regime` |
| Cross-regime transition observed | false |
| Collapse observed | false |

## Invariant Candidates

| Invariant | Classification | Stability Score |
| --- | --- | --- |
| lineage_integrity_invariant | local_observation | 1.0 |
| population_viability_invariant | local_observation | 1.0 |
| fitness_convergence_tendency | candidate_pattern | 0.616639478 |
| branching_density_range | candidate_pattern | 1.0 |

## Data Boundary

This descriptor provides aggregate observations and labels only. It does not
include event-level private traces, code, runtime logic, kernel structure, or
private implementation details.

