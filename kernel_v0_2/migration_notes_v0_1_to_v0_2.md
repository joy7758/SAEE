# Migration Notes: SAEE Kernel v0.1 to v0.2

## Summary

v0.1 is a deterministic single-genome loop:

```text
Sense -> Branch -> Evaluate -> Select -> Lineage -> Update
```

v0.2 is a population ecology runtime:

```text
Sense -> Signal Interpretation -> Population Expansion -> Mutation/Recombination
-> Sandbox Evaluation -> Dynamic Fitness Scoring -> Selection Pressure Resolution
-> Lineage Graph Update -> Population Reconfiguration
```

## Main Changes

| v0.1 | v0.2 |
| --- | --- |
| Single genome state | Population pool with active, dormant, and extinct lineage states |
| Mock sensing dict | Abstract signal stream objects plus interpreted environment state |
| Static weighted score | Dynamic landscape depending on time, environment, population pressure, and lineage competition |
| One selected genome | Survival, extinction, dormancy, and revival sets |
| Linear lineage list | Directed acyclic lineage graph |
| One output selected genome | Population, lineage graph, and full run record |

## Compatibility

v0.2 reuses the v0.1 seed genome at `kernel/examples/seed_genome.json` as the
default founder genome. v0.1 remains runnable and is not removed.

## Non-Claims

v0.2 is not production runtime, real external ecological sensing, API
integration, open-ended evolution, or public release. It is a local abstract
evolutionary ecology runtime.

