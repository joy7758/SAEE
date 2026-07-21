# Reproducibility guide

## Scope

This guide reproduces a 16-pair/32-case synthetic construct-validation result.
It does not reproduce a real agent run, external event, identity check,
authorization, cross-harness comparison, customer validation, or production
decision.

## Pinned source boundary

```text
repository=joy7758/SAEE
evaluator_component_commit=be6ab57878dc7346da733e2f3b134aa3d3049af8
public_snapshot=f6ac41f4b068377e7778e8c3d83b99bd8382debc
dataset=experiment/dataset.v0.1.json
runner=experiment/run_experiment.py
network_required=false
external_repository_execution=false
```

The runner pins SHA-256 values for the evaluator, four profiles, and four
passing fixtures. It stops if those pre-study components drift.

## Primary reproduction

From the SAEE repository root:

```bash
python3 paper_reconstructability_readiness/experiment/run_experiment.py \
  --repetitions 5 \
  --output paper_reconstructability_readiness/experiment/results.v0.1.json
python3 paper_reconstructability_readiness/experiment/verify_artifact.py
```

Expected headline output:

```text
pairs=16/16
cases=32/32
reconstructability_complete=32/32
pairwise_semantic_divergence=16/16
field_complete_false_supports=16
type_and_shape_false_supports=16
decision_aware_false_supports=14
semantic_profile_false_supports=0
deterministic_runs=5/5
canonical_result_sha256=4d101bb8633e4acf6cf4d38c08734afddb47d52c6c8b1748d23f6494c4962f44
boundary_violation_count=0
production_ready=false
```

The runner's canonical-JSON dataset hash is:

```text
1d9cf1ddd52636a1504b78c7b2e7ed577300e6fecdb81b67c2bd222c03f687b0
```

## Environment and data contracts

```text
environment=experiment/environment.v0.1.json
dependency_pin=experiment/requirements.reproduction.txt
data_dictionary=experiment/DATA_DICTIONARY.md
analysis_plan=ANALYSIS_PLAN.md
```

The tested environment is Python `3.14.5` with `jsonschema==4.26.0` on macOS
`26.5.2`. This is a tested configuration, not a claim that other Python or
operating-system versions have been validated.

## Isolated-directory rehearsal

On 2026-07-19, the experiment package, evaluator modules, profiles, schemas,
and fixtures were copied into a new temporary directory and executed from that
directory. The verifier passed with the canonical result hash unchanged. See
`COLD_START_REPRODUCTION_REPORT.md`.

This establishes isolated-directory reproducibility on the same host and
Python environment. It is not a fresh operating-system reproduction, a clean
virtual-environment dependency installation, or cross-platform validation.

## Existing independent regression

The repository's earlier 12-scenario evidence-adequacy regression remains a
separate, non-pooled check:

```bash
python3 scripts/saee_evidence_adequacy_benchmark_smoke.py
```

It covers missing fields and evidence-level variation. It is not presented as
an independent benchmark for the new matched-pair theorem.

## Falsification conditions

The artifact fails if any pair changes its required-field vector or JSON
key/type signature, lacks divergent authored labels, returns an unexpected
semantic verdict/reason code, produces different repeat hashes, drifts from
the pinned evaluator components, or sets a protected authority field to true.

A pass supports only the manuscript's controlled abstraction-separation claim.
