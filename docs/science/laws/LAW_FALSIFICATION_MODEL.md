# SAEE Law Falsification Model

## Purpose

This file defines how SAEE Law Set v1.0 can be disproved or downgraded.

It is a modeling surface only. It does not run new experiments.

## Claim Status Labels

- `candidate_law`: supported by current phase-space artifacts but not repeated
  enough for local empirical law status.
- `local_empirical_law`: reproduced across multiple controlled local runs.
- `rejected_law`: contradicted by controlled evidence.
- `external_validated_law`: independently reproduced outside this local
  repository. Current count: 0.

## General Downgrade Rules

A candidate law must be downgraded or rejected if:

- new controlled evidence contradicts its observed expression;
- the law requires a condition not present in logs;
- the law relies on an unobserved transition;
- the law implies external validation;
- the law depends on modifying runtime behavior.

## Law-Specific Tests

### Attractor Dominance Law

Reject if more than one dominant basin appears under unchanged constraints.

### Regime Non-Transition Law

Reject if cross-regime transitions appear under unchanged constraints while
variance remains in the current convergent range.

### Lineage Stability Law

Reject if lineage DAG integrity fails under unchanged constraints.

### Bounded Diversity Law

Reject if population escapes configured bounds or unbounded structural
diversification appears without perturbation.

### Fitness Convergence Law

Reject if fitness variance repeatedly diverges under unchanged constraints.

## Boundary

This falsification model is not a test runner and not an experiment protocol.
It is a rule surface for future evidence classification.
