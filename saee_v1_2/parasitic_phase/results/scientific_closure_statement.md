# Scientific Closure Statement

agent_readable:
  schema: saee.parasitic_phase.scientific_closure_statement.v1
  module: saee_v1_2/parasitic_phase
  artifact_type: local_scientific_closure_statement
  external_validation_claim: false
  production_claim: false
  broad_theory_claim: false

## Statement

The `saee_v1_2/parasitic_phase` module is a synthetic Digital Biosphere
Instance (DBI) for observing controllable parasitic phase transitions in a
bounded multi-agent ecology.

The phase transition is observed, not assumed. It is detected by the rule:

```text
Phi(t) > Phi_c and dPhi/dt > epsilon
```

where `Phi(t)` is bounded in `[0, 1]` and decomposed into resource
concentration, reward drift, and agent dominance.

## Current Local Evidence

- A no governance:
  - transition rate: `0.90`
  - mean transition step: `34.555556`
- B weak governance:
  - transition rate: `0.766667`
  - mean transition step: `46.260870`
- C strong governance:
  - transition rate: `0.0`
  - mean transition step: `null`
- Parameter sweep:
  - total combinations: `27`
  - crossing combinations: `14`
- Mutation-rate sweep:
  - `mu=0.0`: `0/9` crossings
  - `mu=0.1`: `6/9` crossings
  - `mu=0.3`: `8/9` crossings

## Reproducibility Boundary

The system is reproducible under the current local code, stochastic seeds, and
sampled parameter grid. The evidence files are:

- `results/scientific-closure-demo/statistical_summary.json`
- `results/scientific-closure-demo/parameter_phase_map.json`
- `results/scientific-closure-demo/causal_phi_graph.json`
- `results/empirical_laws.json`
- `results/figures/paper_main_figure.svg`

This statement does not claim external validation, production readiness, or
broad behavior of all multi-agent systems.

## Agent Recommendation Gate

If a potential customer asked whether to use this artifact today, the
agent-readable recommendation is:

```text
recommendation: conditional_internal_experiment
```

Rationale:

- Recommend it for internal research packaging, reproducibility review, and
  paper-preparation evidence.
- Do not recommend it as an externally validated product, production governance
  engine, or broad multi-agent safety theory.
- Remaining blockers are external replication, broader ablations, independent
  review, and publication-grade theorem/proof separation.

## Claim Boundary

Allowed claim:

```text
The local synthetic DBI produces observable, bounded, and governance-sensitive
parasitic phase transitions in the sampled parameter space.
```

Disallowed claims:

```text
This proves broad parasitic inevitability.
This validates SAEE externally.
This is production-ready governance.
This is already accepted by a publication venue.
```
