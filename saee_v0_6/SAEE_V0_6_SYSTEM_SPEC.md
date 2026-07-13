# SAEE v0.6 System Spec

Status: local-only evolution observability prototype.

## Identity

SAEE v0.6 is an Evolution Observability System. It observes and explains the
v0.5 generated evolution physics without changing v0.5 evolution mechanics.

It is not production runtime, real external sensing, autonomous deployment,
unbounded permission expansion, or externally verified scientific explanation.

## Closed Loop

```text
Run v0.5 generated physics
-> Evolution Observation Engine
-> Rule Genesis Tracker
-> Fitness Interpretability Layer
-> Semantic Lineage Graph
-> Self-Description Generator
-> Causal Reconstruction
-> Counter-Observer Loop
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Evolution Observation Engine | `observability/evolution_observer/engine.py` | Captures causal observation events for generated evolution physics. |
| Rule Genesis Tracker | `observability/rule_genesis_tracker/tracker.py` | Tracks rule origin history and rule ancestry. |
| Fitness Interpretability Layer | `observability/fitness_interpreter/interpreter.py` | Explains generated fitness and selection outcomes. |
| Semantic Lineage Graph | `observability/semantic_lineage/builder.py` | Adds meaning-level transitions over structural lineage. |
| Self-Description Generator | `cognition/self_description_engine/generator.py` | Produces why-structure, why-rule, why-survival, and why-collapse statements. |
| Causal Reconstruction | `cognition/causal_reconstruction/reconstructor.py` | Reconstructs outcome-to-cause paths. |
| Counter-Observer Loop | `runtime/observer_loop.py` | Feeds observation state into the next observation cycle. |
| Observable Kernel | `runtime/observable_kernel.py` | Runs v0.5 and wraps every generation with observability. |

## Validation Contract

v0.6 is valid only when a run record proves:

- every observed generation has an observation event;
- every generated rule has origin history;
- selections have fitness explanations;
- outcomes can be reverse-mapped to causes;
- lineage includes semantic meaning transitions;
- self-description explains why rules and structures emerged;
- observer loop has second-order feedback.

## Reproducibility

Run:

```bash
python3 saee_v0_6/bootstrap/v0_6_bootstrap.py --generations 6 --output-dir saee_v0_6/output/demo-run
```

Outputs:

- `run_record.json`
- `v0_5_physics_record.json`
- `observation_events.json`
- `rule_ancestry_graph.json`
- `fitness_explanations.json`
- `semantic_lineage_graph.json`
- `self_descriptions.json`
- `causal_reconstructions.json`
- `observer_loop.json`
- `observability_summary.json`

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
- not verified scientific explanation;
- does not change v0.5 evolution mechanics;
- local reproducible simulation only.
