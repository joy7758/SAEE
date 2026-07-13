# SAEE External Evaluation Claims Boundary v0.1

## Supported statements

The repository may state that:

- an external-evaluation methodology has been designed;
- three research questions have been defined;
- a Code Agent Tool Execution scenario has been specified;
- four planned evidence conditions and three conceptual baselines have been defined;
- four primary metrics, dataset requirements, annotation procedures, threats, and future phases have been documented;
- the design is machine-readable and locally validated for completeness.

## Unsupported statements

The repository must not state or imply that:

- external validation has been completed;
- any external dataset has been selected, downloaded, processed, or evaluated;
- any real agent, collector, external tool, API, or unknown repository has been run;
- a baseline has been implemented or a comparison has been completed;
- SAEE improves production effectiveness or outperforms another approach;
- the planned metrics have measured values;
- the protocol establishes regulatory evidence, legal proof, compliance, certification, or production readiness;
- an independent evaluator has reproduced results.

## Required state

```text
evaluation_protocol_defined=true
status=design_only
executed=false
dataset_collected=false
baseline_implemented=false
results_available=false
external_data_used=false
external_validation_completed=false
independent_validation_completed=false
benchmark_superiority_claimed=false
production_effectiveness_claimed=false
regulatory_evidence_claimed=false
production_ready=false
```

## Promotion rule

No prose edit, local smoke, protocol approval, or prototype implementation may change an external-result flag. Each later phase requires separately reviewable execution evidence and its own recommendation gate.

```text
Evaluation Design ≠ Evaluation Result
Planned Experiment ≠ Completed Experiment
Planned Baseline ≠ Completed Comparison
```
