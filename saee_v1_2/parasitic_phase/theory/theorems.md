# SAEE v1.2 Parasitic Phase Empirical Propositions

agent_readable:
  schema: saee.parasitic_phase.empirical_propositions.v1
  artifact_type: empirical_scientific_theory_package
  module: saee_v1_2/parasitic_phase
  proposition_status: empirical_synthetic
  experiment_logic_modified: false
  external_validation_claim: false
  broad_theory_claim: false
  production_claim: false

## Scope

These are empirical synthetic propositions for the current Digital Biosphere
Instance (DBI) and its sampled parameter space. They formalize observed local
results. They are not mathematical proofs over all possible multi-agent
systems.

Primary evidence surfaces:

- `results/scientific-closure-demo/statistical_summary.json`
- `results/scientific-closure-demo/parameter_phase_map.json`
- `results/scientific-closure-demo/causal_phi_graph.json`
- `results/empirical_laws.json`
- `results/figures/paper_main_figure.svg`

## Proposition 1: Parasitic Phase Emergence

### Statement

In the current DBI, when reward drift and lineage/resource concentration
increase under absent or insufficient governance, the bounded parasitic index
crosses the critical boundary:

```text
exists t <= T such that Phi(t) > Phi_c and dPhi/dt > epsilon
```

where:

```text
Phi(t) = alpha RC(t) + beta RD(t) + gamma AD(t)
Phi(t) in [0, 1]
Phi_c = 0.60
```

### Conditions

- finite resource pool,
- low resource replenishment,
- agents compete for resources,
- mutating agents can modify reward vectors,
- governance is absent or insufficient to damp reward drift and concentration.

### Empirical Support

No-governance closure run:

```text
experiment: A_no_governance
sample_size: 30
transition_count: 27
transition_rate: 0.90
mean_transition_step: 34.555556
ci95: [26.433516, 42.677595]
single_seed_transition_step: 39
single_seed_final_phi: 0.640105
```

Parameter sweep:

```text
total_cells: 27
crossing_cells: 14
mutation_rate_0_0_crossing: 0/9
mutation_rate_0_1_crossing: 6/9
mutation_rate_0_3_crossing: 8/9
```

### Interpretation

The parasitic phase is an observed attractor-like regime in the sampled
synthetic DBI when local gain amplification is not strongly damped.

### Boundary

This proposition is empirical and synthetic. It does not prove that all real-world
multi-agent systems inevitably enter a parasitic phase.

## Proposition 2: Constraint Lag Instability

### Statement

If governance intervention responds more slowly or weakly than evolutionary
reward drift and replication pressure, then the transition time is delayed but
not eliminated:

```text
tau_governance > tau_evolution => Pr(tau < T | G_weak) > 0
```

with observed lag:

```text
E[tau_B | tau_B < T] - E[tau_A | tau_A < T] > 0
```

### Conditions

- weak governance applies bounded replication caps, monopoly penalties, and
  reward-drift damping,
- mutating lineages still retain enough drift capacity to increase local gain,
- the run horizon remains long enough for delayed crossing.

### Empirical Support

```text
A_no_governance:
  transition_rate: 0.90
  mean_transition_step: 34.555556

B_weak_governance:
  transition_rate: 0.766667
  mean_transition_step: 46.260870

observed_mean_delay:
  46.260870 - 34.555556 = 11.705314 timesteps
```

The weak-governance system delays transition by approximately `11.705314`
timesteps among observed crossings, but `23/30` weak-governance runs still
cross the boundary.

### Interpretation

Weak governance shifts the phase boundary in time but does not fully stabilize
the DBI. This is the operational meaning of constraint lag in the current
system.

### Boundary

This proposition characterizes the implemented weak-governance preset. Broader
claims require additional governance classes and independent sweeps.

## Proposition 3: Order Parameter Behavior

### Statement

`Phi` functions as one order parameter for the current multi-agent DBI because it
compresses micro-level agent dynamics into a bounded macro-level transition
signal:

```text
Phi(t) = f(RC(t), RD(t), AD(t))
```

where:

- `RC(t)` captures resource concentration,
- `RD(t)` captures reward drift,
- `AD(t)` captures agent or lineage dominance.

The parasitic phase is detected when:

```text
Phi(t) > Phi_c and dPhi/dt > epsilon
```

### Conditions

- the three components are normalized to `[0, 1]`,
- weights are non-negative and sum to one,
- SAEE trace alignment can map agent actions and reward updates to component
  contributions.

### Empirical Support

The system stores:

```text
metrics.phi_components.components
metrics.phi_components.weighted_contributions
metrics.delta_phi
events.transition_event
```

`causal_phi_graph.json` aligns each timestep with:

- agent action summary,
- reward change summary,
- governance action count,
- `Phi` contribution,
- entropy,
- dominance,
- transition events.

The main figure shows:

- `Phi(t)` crossing or staying below `Phi_c`,
- entropy response,
- dominance emergence or suppression,
- governance-dependent transition shift.

### Interpretation

`Phi` is not merely a reporting metric. In this DBI it is one macrostate
variable that marks the transition between distributed and parasitic regimes.

### Boundary

This proposition establishes order-parameter behavior for the implemented
synthetic DBI. It does not claim that the same `Phi` weights or components are
sufficient for every multi-agent system.

## Claim Discipline

Allowed:

```text
The SAEE v1.2 parasitic_phase module generates an observable, bounded, and
governance-sensitive synthetic parasitic phase transition in the sampled DBI
parameter space.
```

Forbidden:

```text
Broad parasitic inevitability is proven.
The system is real-world validated.
The governance operator is production ready.
The empirical propositions are complete mathematical proofs.
```
