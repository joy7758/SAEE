# Operational Definitions for the lb120 Reported Surfaces

Status: `repository_backed_clarification_only`

These definitions explain existing values. They do not introduce new
experiments, results, laws, or runtime behavior.

## Two evidence surfaces must not be collapsed

The submitted LBA compresses two local surfaces:

1. **Long-horizon v1.0 surface**: 100 generations, configured population 8,
   lineage DAG statistics, collapse checks, fitness-variance tendency, and
   population turnover.
2. **Phase II surface**: six analyzed generations derived from a v0.8 record,
   semantic-drift values, discrete state signatures, attractor candidates, and
   regime labels.

The phrase `stable_lineage_basin` is a later phase-diagram compression of
evidence from both surfaces. It is not the literal `attractor_id` emitted by
the Phase II attractor engine.

## Long-horizon v1.0 surface

### Configuration

```text
generation_count=100
population_size=8
deterministic_seed=enabled
logging_level=full_trace
seed_path=kernel/examples/seed_genome.json
output_dir=saee_experiments/output/demo-run
```

`deterministic_seed=enabled` is a required configuration flag. There is no
numeric RNG seed field in the configuration or experiment record. The v1.0
genome implementation derives child identifiers with a truncated SHA-256 digest
of parent ID, signal ID, generation index, and population index, and applies
deterministic weight shifts.

### Collapse event

For each logged generation, the stability analyzer records a collapse event if
either:

```text
population_count < 2
OR
selection_result.survivor_count == 0
```

The reported long-horizon artifact contains `collapse_event_count=0`. This
means no collapse was detected under this rule in this run. It is not a claim
that collapse is impossible.

### Fitness-variance tendency

Let `F_first` be the mean of per-generation fitness variance over the first ten
logged generations, and `F_last` the same quantity over the last ten. The label
is:

```text
converging      if F_last < 0.75 * F_first
diverging       if F_last > 1.25 * F_first
stable_variance otherwise
```

The current report labels the run `converging`. This label is specific to the
implemented comparison and does not prove convergence in a mathematical limit.

### Population turnover

For consecutive generations with genome-ID sets `P_(t-1)` and `P_t`, turnover
is the Jaccard distance:

```text
turnover_t = 1 - |P_(t-1) intersection P_t| / |P_(t-1) union P_t|
```

The first generation is assigned `0.0`. The reported mean over the full trace
is `0.545531`.

### Lineage accounting

The lineage report operates on `experiment_record.kernel_record.lineage_dag`:

```text
node_count = len(lineage_dag.nodes) = 808
edge_count = len(lineage_dag.edges) = 1590
branching_density = edge_count / node_count = 1.967822
```

Every edge contributes one directed parent-to-child relation. These counts are
not "retained nodes versus raw lineage events" and no deduplication stage is
defined by this report.

`lineage_integrity_preserved=true` means:

```text
lineage_dag.graph_type == "lineage_dag"
AND
every edge.from and edge.to identifier exists in the node-ID set
```

The reporting function does not independently run a cycle-detection algorithm;
therefore this flag should be described as endpoint integrity under a declared
DAG type, not as a complete graph-theoretic proof.

## Phase II surface

### Semantic drift

For each generation, let `A` be the identity anchor's reference-term set and
`D` the lowercased set of dominant terms in the feedback after any bounding
intervention. The implemented value is:

```text
semantic_drift_after = 1 - |D intersection A| / max(1, |A|)
```

Values are rounded to six decimals. The configured bound is `0.32`. The Phase
II record reports `semantic_drift_after=0.2` for each of generations 1--6, so
`semantic_drift_max=0.2` and the Phase II drift summary labels it `bounded`.
This is a set-overlap distance on dominant identity terms, not a vector-space
embedding distance and not a general semantic metric.

### Discrete state signature

For each Phase II trajectory point, the attractor engine builds exactly four
categorical components:

```text
identity = stable  if identity_break_count == 0
                    and mean_identity_score >= 0.58
           fragile otherwise

drift = bounded    if semantic_drift_after <= 0.32
        unbounded  otherwise

population = dense if population_count >= 10
             sparse otherwise

mutation = active  if explanation_driven_mutation_count > 0
           quiet   otherwise
```

The emitted signature is the concatenation:

```text
identity:<...>|drift:<...>|population:<...>|mutation:<...>
```

All six observed points have:

```text
identity:stable|drift:bounded|population:sparse|mutation:active
```

### Empirical attractor candidate

The attractor engine counts exact signature occurrences. A signature is emitted
as an attractor candidate when:

```text
support_count >= 2
```

There is no sliding window, continuous distance function, clustering algorithm,
dominance ratio, dispersion threshold, or recurrence-gap threshold in the
current implementation. The reported candidate has support `6/6` at generations
`[1, 2, 3, 4, 5, 6]` and is typed
`identity_stable_reflexive_attractor` because the signature contains
`identity:stable`.

Accordingly, `attractor` in lb120 must be read as **an empirical recurring
discrete state signature in one local record**, not a proof of a continuous
dynamical-system attractor.

### Regime classification

The point classifier evaluates rules in this order:

```text
1. chaotic_regime
   if identity_break_count > 0 OR semantic_drift_after > 0.55

2. collapse_regime
   if population_count <= 2

3. stable_regime
   if the generation supports an attractor candidate
   AND semantic_drift_after <= 0.32

4. exploratory_regime
   if mutation_event_count >= 4

5. stable_regime
   otherwise
```

Rule order matters. In the current artifact, mutation-event counts are at least
five, but the six points are classified `stable_regime` because rule 3 is
satisfied before rule 4 is evaluated.

The classifier records a transition only when adjacent regime labels differ.
All six labels are `stable_regime`, so the classifier reports zero cross-regime
transitions. The later phase-diagram projection describes the five adjacent
pairs as `stable_regime -> stable_regime` with `5/5 = 1.0`. That ratio is a
local descriptive ratio, not an externally estimated transition probability.

## `stable_lineage_basin` compression

`docs/science/phase_diagram/ATTRACTOR_BASIN_MAP.json` assigns the macro label
`stable_lineage_basin` from existing logs only. Its `stability_score=1.0` is
based on:

```text
population_count == 8 for 100/100 long-horizon generations
collapse_event_count == 0
lineage_integrity_preserved == true
Phase II signature support_count == 6
```

This score is an internal evidence compression rule, not a calibrated
probability, benchmark score, or formal basin-volume estimate.

## Interpretation boundary

The definitions support only the following statement:

> In the recorded local artifacts, the 100-generation v1.0 surface remained
> viable under its collapse rule and preserved declared-DAG endpoint integrity,
> while the six-generation Phase II surface repeated one bounded-drift discrete
> state signature and received six `stable_regime` labels.

They do not support cross-seed universality, cross-parameter robustness,
cross-substrate generality, external validation, open-ended evolution, formal
attractor existence, universal law, or algorithmic superiority.
