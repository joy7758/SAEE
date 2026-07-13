# SAEE v0.7 System Spec

Status: local-only reflexive evolution prototype.

## Identity

SAEE v0.7 is a Reflexive Evolution System. It turns v0.6 explanations into
causal inputs for mutation probability, epistemic fitness, semantic selection,
self-model updates, and interpretation-influenced lineage.

It is not production runtime, self-aware cognition, autonomous deployment,
unbounded permission expansion, or externally verified semantic causality.

## Closed Loop

```text
Meaning feedback
-> Reflexive Mutation Engine
-> Epistemic Fitness Layer
-> Semantic Selection Engine
-> Observer-in-the-Loop System
-> Self-model update
-> Explanation-influenced lineage
-> Next meaning feedback
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Reflexive Mutation Engine | `reflexive_core/reflexive_mutation_engine/engine.py` | Makes explanation quality change mutation probability. |
| Observer-in-the-Loop System | `reflexive_core/observer_loop/system.py` | Embeds v0.6 observer in the evolution runtime. |
| Epistemic Fitness Layer | `reflexive_core/epistemic_fitness/layer.py` | Adds explainability quality and self-model alignment as fitness pressure. |
| Semantic Selection Engine | `reflexive_core/semantic_selection/engine.py` | Makes semantic coherence influence survival. |
| Meaning Feedback Loop | `cognition/meaning_feedback_loop.py` | Converts explanations into next-generation semantic feedback. |
| Interpretation Pressure Engine | `cognition/interpretation_pressure_engine.py` | Converts feedback and self-model uncertainty into pressure. |
| Evolution Self-Model | `self_model/evolution_self_model/model.py` | Maintains recursive understanding state. |
| Recursive Understanding Graph | `self_model/recursive_understanding_graph/graph.py` | Records self-model updates over time. |
| Explanation-Influenced DAG | `lineage/explanation_influenced_dag/dag.py` | Records interpretation influence on mutation and selection lineage. |
| Reflexive Kernel | `runtime/reflexive_kernel.py` | Runs the local reproducible v0.7 closed loop. |

## Validation Contract

v0.7 is valid only when a run record proves:

- explanations influence mutation probabilities;
- well-explained structures can stabilize;
- observer is embedded in the loop;
- semantic feedback influences selection;
- epistemic fitness changes at least one survival outcome;
- self-model updates across generations;
- lineage records interpretation history.

## Reproducibility

Run:

```bash
python3 saee_v0_7/bootstrap/v0_7_bootstrap.py --generations 6 --output-dir saee_v0_7/output/demo-run
```

Outputs:

- `run_record.json`
- `reflexive_cycles.json`
- `reflexive_mutations.json`
- `epistemic_fitness.json`
- `semantic_selection.json`
- `meaning_feedback.json`
- `interpretation_pressure.json`
- `self_model.json`
- `recursive_understanding_graph.json`
- `explanation_influenced_dag.json`
- `observer_in_loop.json`
- `reflexive_summary.json`

## Safety Boundary

The runtime records these hard boundaries:

- abstract signal objects only;
- no real API calls;
- no network access;
- no external repository execution;
- no permission expansion;
- no external code as genome;
- no publication claim;
- not production runtime;
- not self-aware system;
- not verified semantic causality;
- local reproducible simulation only.
