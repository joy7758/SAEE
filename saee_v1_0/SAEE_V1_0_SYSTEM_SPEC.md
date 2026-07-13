# SAEE v1.0 System Spec

Status: local-only stable evolutionary runtime.

## Identity

SAEE v1.0 is not a new theory layer. It is the minimal stable evolutionary
machine:

```text
Sense -> Mutate -> Evaluate -> Select -> Lineage -> Update
```

## Runtime Contract

v1.0 keeps only:

- one evolution loop;
- one population pool;
- one unified fitness function;
- one ranked selection pass;
- one lineage DAG;
- one local runtime entrypoint.

## Core Files

| File | Role |
| --- | --- |
| `kernel/evolution_loop.py` | Runs the only v1.0 loop. |
| `kernel/genome.py` | Seeds and mutates the single population pool. |
| `kernel/fitness.py` | Defines `fitness(genome, signals) -> score`. |
| `kernel/selection.py` | Selects the next population. |
| `kernel/lineage.py` | Records one lineage DAG. |
| `runtime/saee_runtime.py` | Loads seed genomes and writes outputs. |
| `bootstrap/v1_0_bootstrap.py` | Reproducible local entrypoint. |

## Reproducibility

Run:

```bash
python3 saee_v1_0/bootstrap/v1_0_bootstrap.py --generations 12 --population-size 8 --output-dir saee_v1_0/output/demo-run
```

Outputs:

- `run_record.json`
- `population.json`
- `lineage_dag.json`
- `fitness_scores.json`
- `generation_log.json`
- `stability_summary.json`

## Boundary

v1.0 does not include phase theory, generated physics, observability,
reflexive, epistemic, semantic, identity-stability, or behavior-science systems
in the core runtime. Those systems are side-layer archive references only.

