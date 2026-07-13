# SAEE v0.5 System Spec

Status: local-only open-ended evolution physics prototype.

## Identity

SAEE v0.5 is an Open-Ended Evolution Physics prototype. It keeps the v0.4
phase-transition boundary, but moves the generated object up one more level:
evolution laws, fitness functions, selection mechanisms, dimensions, and
regimes are generated from observed lineage dynamics.

It is not production runtime, real external sensing, autonomous deployment,
unbounded permission expansion, or verified true open-ended evolution.

## Closed Loop

```text
Abstract signal observation
-> Novelty detection
-> Dimension birth / merge / collapse
-> Evolution law generation
-> Phase emergence detection
-> Regime self-construction
-> Fitness function generation
-> Generated variation and composition
-> Selection mechanism evolution
-> Selection resolution
-> Hypergraph lineage update
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Evolution Law Generator | `physics/evolution_laws/generator.py` | Generates law records from observation signatures and lineage novelty. |
| Self-Generated Fitness Engine | `physics/fitness_generators/engine.py` | Generates expression-term fitness functions from laws and runtime dimensions. |
| Selection Mechanism Evolution Layer | `physics/selection_evolution/layer.py` | Generates selection mechanisms as evolvable entities with parents and mutation records. |
| Evolution Dimension Birth System | `physics/dimension_birth/system.py` | Births, merges, and collapses dimensions from novelty tokens and pressure. |
| Regime Self-Construction Engine | `physics/regime_constructor/engine.py` | Constructs and regenerates regimes from attractor signatures. |
| Novelty Detector | `emergence/novelty_detector.py` | Produces local novelty tokens from population and abstract signals. |
| Phase Emergence Engine | `emergence/phase_emergence_engine.py` | Records irreversible structure-space phase transitions. |
| Hypergraph Lineage | `lineage/hyper_graph.py` | Records generated physics objects and their hyperedges. |
| Runtime | `runtime/physics_loop.py` | Runs the local reproducible v0.5 closed loop. |

## Validation Contract

v0.5 is valid only when a run record proves:

- generated evolution laws are produced from runtime observations;
- evolution laws are generated from observations and contain generated clauses;
- fitness functions are generated internally and contain expression terms;
- selection mechanisms mutate and reproduce as entities;
- new dimensions appear at runtime;
- dimensions can merge and collapse;
- regimes can collapse and regenerate;
- at least one irreversible phase transition is recorded.

## Reproducibility

Run:

```bash
python3 saee_v0_5/bootstrap/v0_5_bootstrap.py --generations 6 --output-dir saee_v0_5/output/demo-run
```

Outputs:

- `run_record.json`
- `population.json`
- `hyper_graph.json`
- `generated_laws.json`
- `generated_fitness_functions.json`
- `selection_mechanisms.json`
- `dimensions.json`
- `regimes.json`
- `emergence_report.json`

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
- not verified true open-ended evolution;
- local reproducible simulation only.
