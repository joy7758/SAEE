# SAEE v0.4 System Spec

Status: local-only phase-transition evolution-space bootstrap.

## Identity

SAEE v0.4 is a Phase Transition Evolution System. It keeps the v0.3
population and meta-evolution boundary, but moves the mutable object up one
level: the evolution space itself can change.

It is not production runtime, real external sensing, autonomous deployment,
unbounded self-modification, or a scalar optimization loop.

## Closed Loop

```text
Abstract signal sensing
-> Fitness geometry projection of current population
-> Ecological phase transition detection
-> Meta-regime switch
-> Evolution space mutation
-> Runtime mutation-operator selection
-> Population mutation / recombination
-> Fitness geometry projection of candidates
-> Selection topology resolution
-> Lineage graph update
-> Population reconfiguration
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Evolution Space | `evolution_space/model.py` | Mutable dimensions, geometry type, selection topology, and mutation operator mode. |
| Fitness Geometry | `fitness_geometry/geometry.py` | Projects genomes into a changing geometry over active dimensions and niches. |
| Selection Topology | `selection_topology/topology.py` | Resolves survival through niche, graph, pressure-field, or competition-field topology. |
| Mutation Space | `mutation_space/operators.py` | Provides runtime-extensible mutation operator modes. |
| Phase Detector | `phase_transition/detector.py` | Detects multi-niche emergence, divergence, convergence, and collapse pressure. |
| Regime Switch | `ecological_regimes/regime_switch.py` | Switches between optimization, exploration, diversification, and collapse/reset regimes. |
| Population Pool | `population/pool.py` | Maintains active and dormant genome lineages without collapsing to a single genome. |
| Lineage Graph | `lineage_graph/graph.py` | Records genome DAG plus evolution-space graph, phase events, and regime events. |
| Runtime | `kernel/runtime.py` | Runs the local reproducible v0.4 closed loop. |

## Validation Contract

v0.4 is valid only when a run record proves:

- fitness geometry changes structure through `geometry_type` and `active_dimensions`;
- selection topology changes structurally across generations;
- mutation operator modes change at runtime;
- population behavior includes a phase shift such as niche emergence or collapse pressure;
- at least two ecological regimes occur in one local run.

## Reproducibility

Run:

```bash
python3 saee_v0_4/KERNEL_BOOTSTRAP_SCRIPT.py --generations 5 --output-dir saee_v0_4/output/demo-run
```

Outputs:

- `run_record.json`
- `population.json`
- `lineage_graph.json`
- `evolution_space.json`
- `phase_transition_summary.json`
- `regime_switch_log.json`

## Safety Boundary

The runtime records these hard boundaries:

- abstract signal objects only;
- no real API calls;
- no network access;
- no external repository execution;
- no permission expansion;
- no external code as genome;
- not production runtime;
- not unbounded self-modification;
- local reproducible simulation only.
