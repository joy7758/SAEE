# Experimental Setup Overview

Status: Zenodo academic publication package draft, local only.

## Purpose

This overview describes the experiment at the level needed for academic
interpretation without exposing implementation details.

## Allowed Description

The public setup can be described as:

```text
A constrained computational evolutionary object observed for 100 generations
through a passive long-horizon experiment layer.
```

The observation tracked:

- population count;
- aggregate variance tendency;
- collapse events;
- lineage graph summary;
- regime labels;
- attractor basin labels;
- invariant candidates.

## Constitution

```text
kernel_modified: false
new_evolution_mechanics: false
observer_feedback_into_kernel: false
core_loop_count: 1
lineage_model: single_lineage_dag
observation_only: true
```

## Reproducible Description

The package provides a reproducible description of the observation outputs, not
a reproducible implementation of the private system.

Reproducible public elements:

- reported generation count;
- reported aggregate population size;
- reported collapse count;
- reported lineage node and edge counts;
- reported phase-space labels;
- reported candidate laws and falsification conditions.

## Not Disclosed

This overview does not disclose:

- source code;
- runtime logic;
- kernel structure;
- scoring formulas;
- selection procedures;
- mutation procedures;
- lineage construction procedures;
- reproduction procedures;
- deployment or operational procedures.

## Upload Boundary

This file is ready for human review before a Zenodo upload. It does not itself
perform upload, DOI reservation, publication, or external validation.

