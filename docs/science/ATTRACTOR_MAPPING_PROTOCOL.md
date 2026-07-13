# Attractor Mapping Protocol

## Purpose

Attractor mapping identifies repeated or convergent state signatures in SAEE
run records. It is observation-only.

## State Vector

The minimum attractor state vector is:

```text
generation_index
mean_fitness
fitness_variance
population_count
population_turnover
lineage_branching_density
collapse_event_count
dominant_persistent_structure
```

Optional Phase II vectors may add regime labels, semantic drift, identity
scores, and attractor signatures, but those remain side-layer evidence and do
not enter v1.0 runtime.

## Mapping Steps

1. Read immutable trace and report files.
2. Project each generation into the state vector.
3. Group similar state vectors into candidate basins.
4. Mark recurring basins as candidate attractors.
5. Require repeated runs before raising a candidate attractor to local
   empirical status.
6. Reject attractor claims when new runs show inconsistent basin membership.

## Claim Status

Attractor claims must use one of these statuses:

- `candidate_attractor`: one local run indicates convergence or recurrence;
- `local_empirical_attractor`: repeated local runs reproduce the basin;
- `rejected_attractor`: repeated runs fail to reproduce the basin;
- `external_validated_attractor`: externally reproduced; currently no SAEE
  claim has this status.

## Current Local Attractor Note

The v1.0 long-horizon run shows a converging fitness variance tendency with no
collapse events and preserved lineage integrity. This supports:

```text
candidate_attractor: stable_population_lineage_basin
claim_status: candidate_attractor
```

The Phase II side-layer demo also reports one attractor with stable regime
classification across six generations. Because that source observes a v0.8
record, it is a side-layer reference, not direct proof of the v1.0 attractor.

## Boundary

Attractor mapping is not phase theory in runtime. It does not alter fitness,
selection, mutation, lineage, or population behavior.
