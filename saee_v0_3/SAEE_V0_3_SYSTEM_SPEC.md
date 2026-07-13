# SAEE v0.3 System Spec

Status: local-only meta-evolution bootstrap.

## Identity

SAEE v0.3 is a Meta-Evolution System. It keeps the v0.2 population ecology
runtime and adds rule genomes so evolution can modify evolution rules under
explicit drift guards.

It is not production runtime, real external sensing, autonomous deployment, or
unbounded self-modification.

## Closed Loop

```text
Sense environment
-> Interpret abstract signal state
-> Expand population
-> Mutate and recombine genomes
-> Run local sandbox checks
-> Score dynamic multi-objective fitness
-> Resolve selection pressure
-> Update genome lineage DAG
-> Propose rule-genome mutation
-> Run counterfactual rule trial
-> Apply drift guard
-> Adopt or reject rule mutation
-> Record rule lineage graph
```

## Core Objects

| Object | File | Purpose |
| --- | --- | --- |
| Genome | `genome/contracts.py` | Normalized agent-readable genome with parents, mutation history, selection events, and rule history. |
| Rule Genome | `genome/contracts.py` | Mutable evolution-rule object containing fitness weights, selection thresholds, mutation pressure, and guards. |
| Population | `population/pool.py` | Active and dormant genome pool with mutation and recombination. |
| Environment | `sensors/abstract_sensorium.py` | Local abstract GitHub/news/history/paper signal state. |
| Fitness Record | `fitness/landscape.py` | Dynamic score with components, weights, population pressure, and lineage competition. |
| Selection Decision | `selection/pressure.py` | Survival, dormancy, extinction, and revival sets. |
| Lineage DAG | `lineage/dag.py` | Genome DAG plus rule-genome DAG. |
| Drift Guard | `meta_evolution/drift_guard.py` | Invariant checks for population mode, DAG, fitness vector, abstract sensing, and no external execution. |

## Meta-Evolution Boundary

v0.3 may mutate only:

- fitness weights;
- selection extinction threshold;
- selection dormancy threshold;
- carrying capacity;
- mutation pressure.

v0.3 may not mutate:

- genome schema identity;
- lineage graph structure contract;
- sensing boundary;
- safety constraints;
- direct execution permissions.

## Reproducibility

The bootstrap is deterministic for the same seed, generation count, and initial
population size. It uses only Python standard-library code and local JSON
output.

Run:

```bash
python3 saee_v0_3/KERNEL_BOOTSTRAP_SCRIPT.py --generations 3 --output-dir saee_v0_3/output/demo-run
```

Outputs:

- `run_record.json`
- `population.json`
- `lineage_graph.json`
- `rule_genome.json`
- `drift_guard.json`

## Safety Boundary

The runtime records these hard boundaries:

- abstract signal objects only;
- no real API calls;
- no network access;
- no external repository execution;
- no permission expansion;
- no publication claim;
- not production runtime;
- not unbounded self-modification.

