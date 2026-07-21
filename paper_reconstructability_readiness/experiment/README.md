# Presence-equivalence matched-pair experiment

Companion experiment for *Evidence Presence Is Not Semantic Support*.

```bash
python3 paper_reconstructability_readiness/experiment/run_experiment.py \
  --repetitions 5 \
  --output paper_reconstructability_readiness/experiment/results.v0.1.json
python3 paper_reconstructability_readiness/experiment/verify_artifact.py
```

Environment and data contracts:

```text
environment=environment.v0.1.json
dependency_pin=requirements.reproduction.txt
data_dictionary=DATA_DICTIONARY.md
analysis_plan=../ANALYSIS_PLAN.md
```

## Design

The dataset contains 16 positive/negative pairs, four for each claim profile.
Within every pair, both cases retain:

- the same required-field presence vector;
- the same complete JSON key/type signature; and
- the same nominal descriptive outcome.

The negative replaces one value to violate a digest, time, scope, decision,
identity, reference, URI, or causal relation. The runner compares field
presence, type/shape, affirmative-decision, and full relation-aware rules.

## Controlled result

```text
pairs=16
cases=32
identical_presence_vector=16/16
identical_json_shape=16/16
field_complete_false_supports=16
type_and_shape_false_supports=16
decision_aware_false_supports=14
semantic_profile_false_supports=0
boundary_violations=0
deterministic_runs=5/5
```

The runner reads only local allowlisted fixtures and pinned profile files. It
does not access a network, dereference a URI, start a subprocess, install a
dependency, or execute candidate code. These results are white-box synthetic
construct validation, not population performance or production readiness.

The dataset is a complete authored corpus, not a random sample. Repetition
checks determinism only. Population confidence intervals, statistical power,
and significance tests are not identified by this design.
