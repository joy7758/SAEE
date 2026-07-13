# SAEE Kernel v0.2 Evolution Cycle

Status: local-only abstract evolutionary ecology runtime.

## Cycle

```text
Sense
-> Signal Interpretation
-> Population Expansion
-> Mutation/Recombination
-> Sandbox Evaluation
-> Dynamic Fitness Scoring
-> Selection Pressure Resolution
-> Lineage Graph Update
-> Population Reconfiguration
```

## Behavior

v0.2 replaces the v0.1 single selected genome state with a population pool.
Multiple genomes can coexist as active or dormant lineages. Selection pressure
can mark genomes as surviving, dormant, extinct, or revived.

## Signal Boundary

External context is represented as local abstract signal objects:

- GitHub signals: repo growth and issue clusters.
- News signals: regulation and enterprise adoption.
- History signals: past failure pressure.
- Paper signals: research trend pressure.

The runtime does not call external APIs, fetch network data, execute external
repositories, or expand permissions.

## Fitness Boundary

Fitness is dynamic:

```text
fitness = f(genome, generation time, environment state, population pressure, lineage competition)
```

Each fitness record includes:

- `generation_id`
- `environment_id`
- `population_pressure`
- `lineage_competition`
- component scores
- weighted `total`

## Output Contract

`runtime_v0_2.py` writes:

- `population.json`
- `lineage_graph.json`
- `run_record.json`

The top-level run record contains:

```json
{
  "generation_id": "generation-004",
  "population": [],
  "lineage_graph": {}
}
```

