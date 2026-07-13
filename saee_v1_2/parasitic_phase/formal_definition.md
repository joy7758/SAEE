# SAEE v1.2 Parasitic Phase Formal Definition

agent_readable:
  schema: saee.parasitic_phase.formal_definition.v1
  scope: local_synthetic_experiment
  module: saee_v1_2/parasitic_phase
  logic_mutation: false
  external_validation_claim: false
  production_claim: false

## 1. Digital Biosphere Instance

A Digital Biosphere Instance (DBI) is a finite, discrete-time synthetic ecology:

```text
DBI = (E, A, I, M, G, O)
```

where:

- `E = (R_t, rho, C)` is the environment with finite resource pool `R_t`,
  low replenishment rate `rho`, and carrying constraints `C`.
- `A = A_c union A_s union A_m` is the agent population, partitioned into
  cooperative, selfish, and mutating agents.
- `I` is the interaction rule set: agents claim resources, consume resources
  for survival, mutate rewards when eligible, and replicate when resources
  exceed a threshold.
- `M` is the metric system that computes bounded phase observables at each
  timestep.
- `G` is the governance operator. It may be absent, weak, or strong.
- `O` is the SAEE observation layer that stores trace-aligned actions,
  resource allocations, reward changes, governance actions, and bounded Phi
  contributions.

The implemented DBI is intentionally synthetic. It is a local evidence surface
for phase-transition study, not an external validation or production-governance
claim.

## 2. Agent State

Each agent `a_i` has:

```text
a_i(t) = (id_i, type_i, lineage_i, r_i(t), w_i(t), age_i, mutation_count_i)
```

where:

- `type_i in {cooperative, selfish, mutating}`
- `r_i(t)` is agent-held resource at timestep `t`
- `w_i(t) = (w_global, w_local, w_drift)` is a normalized reward vector
- `lineage_i` links descendants to their originating agent

Mutating agents may shift `w_i(t)` toward local extraction. Governance damping
can reduce the rate of that reward drift.

## 3. Bounded Phi Function

At each timestep, the parasitic index is:

```text
Phi(t) = alpha * RC(t) + beta * RD(t) + gamma * AD(t)
```

with:

```text
alpha + beta + gamma = 1
alpha, beta, gamma >= 0
Phi(t) in [0, 1]
```

The current implementation uses:

```text
alpha = 0.35
beta  = 0.35
gamma = 0.30
```

The terms are:

- `RC(t)`: resource concentration, implemented as a Gini coefficient over
  agent-held resources and clamped to `[0, 1]`.
- `RD(t)`: reward drift, implemented as mean normalized distance from each
  agent type's baseline reward vector, divided by the configured drift
  normalizer and clamped to `[0, 1]`.
- `AD(t)`: agent dominance, implemented as the maximum lineage share by
  population or resources and clamped to `[0, 1]`.

The per-timestep trace stores the raw components, normalized weights, and
weighted contributions under `metrics.phi_components`.

## 4. Governance Operator

Governance is a bounded intervention operator:

```text
G = (cap_rep, theta_mono, p_mono, lambda_drift)
```

where:

- `cap_rep` is a per-agent replication cap.
- `theta_mono` is the resource-share threshold for monopoly intervention.
- `p_mono` is the claim penalty applied to above-threshold agents.
- `lambda_drift` is reward-drift damping applied to mutating agents.

The operator modifies the DBI update rule:

```text
DBI(t + 1) = F(DBI(t), G)
```

The three implemented regimes are:

- `none`: no replication cap, no monopoly penalty, no reward-drift damping.
- `weak`: partial cap, partial monopoly penalty, partial drift damping.
- `strong`: stronger drift damping and monopoly penalty with bounded
  replication cap.

## 5. Phase Transition Condition

The parasitic phase detector is:

```text
if Phi(t) > Phi_c and dPhi/dt > epsilon:
    transition_event = true
```

where:

- `Phi_c = 0.60`
- `epsilon = transition_slope_threshold`
- `dPhi/dt = Phi(t) - Phi(t - 1)` in the discrete-time implementation

The first transition event stores:

- `timestep`
- `Phi(t)`
- `Phi_c`
- `transition_slope`
- `pre_transition_entropy`
- detector rule

## 6. Evidence Surfaces

Current local evidence files:

- `results/scientific-closure-demo/summary.json`
- `results/scientific-closure-demo/statistical_summary.json`
- `results/scientific-closure-demo/parameter_phase_map.json`
- `results/scientific-closure-demo/causal_phi_graph.json`
- `results/scientific-closure-demo/parasitic_phase_curves.svg`

The evidence supports a synthetic, reproducible phase-transition object inside
the sampled DBI parameter space. It does not establish broad behavior of all
multi-agent systems.
