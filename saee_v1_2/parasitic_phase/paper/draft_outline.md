# Draft Outline: Synthetic Parasitic Phase Transitions in a Digital Biosphere Instance

agent_readable:
  schema: saee.parasitic_phase.paper_outline.v1
  artifact_type: publication_skeleton
  module: saee_v1_2/parasitic_phase
  source_results: saee_v1_2/parasitic_phase/results
  external_validation_claim: false
  production_claim: false

## Abstract

- Define the problem: bounded multi-agent ecosystems can drift from cooperative
  resource sharing into parasitic concentration under local reward pressure.
- Present the method: a minimal Digital Biosphere Instance (DBI) with finite
  resources, cooperative/selfish/mutating agents, bounded `Phi`, and governance
  operator `G`.
- Present the result: no governance enters parasitic phase quickly; weak
  governance delays transition; strong governance blocks transition in the
  current stochastic closure run.
- State the boundary: all results are synthetic and local to the sampled
  parameter space.

## Introduction

- Multi-agent systems can become unstable when local reward optimization
  compounds over repeated interaction.
- Existing discussions often describe alignment, cooperation, or safety at the
  policy layer, but phase-level observables are less explicit.
- This work asks whether a minimal synthetic ecology can produce an observable,
  bounded, and controllable parasitic phase transition.
- Contribution summary:
  - DBI formalization.
  - Bounded `Phi` parasitic index.
  - Governance operator `G`.
  - Stochastic closure over A/B/C governance regimes.
  - Trace-aligned causal evidence through SAEE observation outputs.

## Methods

### Digital Biosphere Instance

- Environment: finite resource pool, low replenishment, discrete timesteps.
- Agents:
  - cooperative agents optimize global reward share,
  - selfish agents optimize local reward share,
  - mutating agents modify reward vectors over time.
- Interactions: resource claims, survival cost, replication threshold,
  mutation, extinction.

### Bounded Phi System

- `Phi(t) = alpha RC(t) + beta RD(t) + gamma AD(t)`.
- `RC`: resource concentration.
- `RD`: reward drift.
- `AD`: agent dominance.
- `Phi(t) in [0, 1]`.
- Transition detector: `Phi(t) > Phi_c and dPhi/dt > epsilon`.

### Governance Operator

- `G = (cap_rep, theta_mono, p_mono, lambda_drift)`.
- Control dimensions:
  - replication cap,
  - monopoly penalty,
  - reward-drift damping.
- Regimes:
  - A: no governance,
  - B: weak governance,
  - C: strong governance.

### SAEE Trace Alignment

- Each timestep stores agent actions, resource allocations, reward updates,
  governance actions, metrics, and transition events.
- `causal_phi_graph.json` aligns action summaries, reward changes, and
  `Phi` contributions.

## Results

### A/B/C Governance Closure

- A no governance:
  - transition rate: `0.90`
  - mean transition step: `34.555556`
  - 95% CI: `26.433516` to `42.677595`
- B weak governance:
  - transition rate: `0.766667`
  - mean transition step: `46.260870`
  - 95% CI: `37.009848` to `55.511891`
- C strong governance:
  - transition rate: `0.0`
  - mean transition step: `null`

### Parameter Sweep

- 27 sampled parameter combinations.
- 14 combinations crossed the phase boundary.
- Mutation-rate sweep:
  - `mu=0.0`: 0/9 crossing.
  - `mu=0.1`: 6/9 crossing.
  - `mu=0.3`: 8/9 crossing.

### Main Figure

- `results/figures/paper_main_figure.svg`
- Panels:
  - bounded `Phi(t)` with `Phi_c`,
  - entropy curve,
  - dominance curve.

## Discussion

- The DBI demonstrates a controllable synthetic phase transition rather than a
  biological analogy.
- Weak governance shows constraint lag: intervention can delay crossing while
  still permitting parasitic transition.
- Strong governance can suppress crossing in the current stochastic closure
  setting.
- The observed regularities should be framed as sampled synthetic patterns, not broad
  claims.

## Limitations

- Synthetic system only.
- No external validation.
- No production-governance claim.
- Results depend on current agent dynamics, `Phi` weights, and sampled
  parameter grid.
- Stronger claims require broader sweeps, ablations, independent replication,
  and external review.

## Candidate Submission Preparation Notes

- Main artifact: `saee_v1_2/parasitic_phase`.
- Primary figure: `results/figures/paper_main_figure.svg`.
- Primary statistical evidence: `results/scientific-closure-demo/statistical_summary.json`.
- Primary causal evidence: `results/scientific-closure-demo/causal_phi_graph.json`.
- Claim language: "synthetic phase-transition system" and "observed in sampled
  DBI parameter space"; avoid broad theory claims without proof and independent
  validation.
