# SAEE Experiment Boundary

## Core Rule

SAEE v1.0 is the immutable evolution machine.

`saee_experiments/` is a passive observation layer.

## Allowed

- Run `saee_v1_0.runtime.saee_runtime` with deterministic local inputs.
- Write per-generation trace logs.
- Analyze fitness variance, population collapse, lineage branching density,
  mutation accumulation, structural drift, repeated patterns, and persistent
  genome structures.
- Produce local reports for human and agent review.

## Forbidden

- Modifying `saee_v1_0/kernel/*`.
- Adding mutation, selection, fitness, lineage, phase, physics, reflexive,
  semantic, epistemic, or observer-feedback mechanics.
- Feeding analysis results back into the v1.0 runtime.
- Calling real external APIs.
- Executing external repositories.
- Installing untrusted dependencies.
- Expanding permissions.
- Copying external code as genome.
- Claiming release, DOI, package upload, publication, production deployment,
  universal laws, or external validation.

## Agent-Readable Contract

Agents may treat this layer as an experiment harness only. It may generate evidence about long-horizon v1.0 behavior, but it must not change the behavior being measured.
