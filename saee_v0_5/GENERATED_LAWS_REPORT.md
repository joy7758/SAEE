# Generated Laws Report

Generated: 2026-07-02

## Runtime Evidence

Command:

```bash
python3 saee_v0_5/bootstrap/v0_5_bootstrap.py --generations 6 --output-dir saee_v0_5/output/demo-run
```

Observed local pass:

```text
SAEE_V0_5_BOOTSTRAP: PASS generation=v05-generation-006 population=15 laws=6 dimensions=48 regenerations=4
```

## What Counts As Generated

A law is generated when it records:

- a runtime `law_id`;
- `origin_observation`;
- source terms derived from novelty, dimensions, and phase signals;
- clauses derived from observation signatures;
- parent law references after early generations.

## Validation Surface

Machine-readable proof is written to:

- `saee_v0_5/output/demo-run/generated_laws.json`
- `saee_v0_5/output/demo-run/generated_fitness_functions.json`
- `saee_v0_5/output/demo-run/selection_mechanisms.json`
- `saee_v0_5/output/demo-run/emergence_report.json`

## Interpretation Boundary

This report proves a local generated-physics prototype. It does not claim
production deployment, real environmental causality, or externally verified
true open-ended evolution.
