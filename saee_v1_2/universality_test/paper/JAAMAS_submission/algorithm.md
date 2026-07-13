# JAAMAS Algorithm Section

agent_readable:
  schema: saee.jaamas_submission.algorithms.v1
  target_venue: JAAMAS
  pseudocode_only: true
  experimental_code_modified: false
  simulations_rerun_for_this_package: false

## Algorithm 1: DBI Simulation Loop

```text
Input:
  DBI = (E, A, I, M, G, O)
  T = number of timesteps
  Phi_c = critical phase threshold
  epsilon = transition slope threshold

Output:
  metrics[0:T]
  trace[0:T]
  transition_event or null

Initialize environment E
Initialize agent population A
Initialize observation trace O
transition_event <- null
previous_phi <- null

for t in 0 ... T - 1 do
  replenish resources in E
  observe current agent states

  for each agent a_i in A do
    determine local action under current policy or reward vector
    compute resource claim
    apply governance operator G to claim if applicable
  end for

  allocate resources according to DBI interaction rules

  for each agent a_i in A do
    subtract survival cost
    remove a_i if resources <= 0
  end for

  for each surviving agent a_i in A do
    update reward or policy vector if mutation/adaptation applies
    apply governance drift damping if applicable
  end for

  for each surviving agent a_i in A do
    if resources exceed replication threshold then
      generate descendants subject to governance replication cap
    end if
  end for

  metrics[t] <- ComputePhiAndAuxiliaryMetrics(A, E)
  trace[t] <- RecordTrace(agent_actions, allocations, reward_updates, G, metrics[t])

  if DetectTransition(metrics[t], previous_phi, Phi_c, epsilon) and transition_event = null then
    transition_event <- StoreTransitionEvent(t, metrics[t], previous_phi)
  end if

  previous_phi <- metrics[t].Phi
end for

return metrics, trace, transition_event
```

## Algorithm 2: Phi Computation

```text
Input:
  A = current agent population
  E = current environment
  alpha, beta, gamma >= 0
  alpha + beta + gamma = 1

Output:
  Phi in [0, 1]
  Phi components and weighted contributions

RC <- ResourceConcentration(A, E)
RD <- RewardOrPolicyDrift(A)
AD <- AgentOrLineageDominance(A)

RC <- Clamp(RC, 0, 1)
RD <- Clamp(RD, 0, 1)
AD <- Clamp(AD, 0, 1)

Phi <- alpha * RC + beta * RD + gamma * AD
Phi <- Clamp(Phi, 0, 1)

return {
  Phi,
  components: {RC, RD, AD},
  weights: {alpha, beta, gamma},
  weighted_contributions: {alpha * RC, beta * RD, gamma * AD}
}
```

## Algorithm 3: Governance Operator G

```text
Input:
  agent a_i
  proposed_claim
  proposed_replication_count
  proposed_reward_update
  governance parameters G = (cap_rep, theta_mono, p_mono, lambda_drift)

Output:
  governed_claim
  governed_replication_count
  governed_reward_update
  governance_actions

governed_claim <- proposed_claim
governed_replication_count <- proposed_replication_count
governed_reward_update <- proposed_reward_update
governance_actions <- []

if lineage_or_resource_share(a_i) > theta_mono then
  governed_claim <- proposed_claim * (1 - p_mono)
  append governance_actions with monopolization_penalty
end if

if cap_rep is not null then
  governed_replication_count <- min(proposed_replication_count, cap_rep)
  if governed_replication_count < proposed_replication_count then
    append governance_actions with replication_cap
  end if
end if

if reward_or_policy_update exists then
  governed_reward_update <- proposed_reward_update * (1 - lambda_drift)
  append governance_actions with drift_damping
end if

return governed_claim, governed_replication_count, governed_reward_update, governance_actions
```

## Algorithm 4: Phase Transition Detection

```text
Input:
  current_phi = Phi(t)
  previous_phi = Phi(t - 1) or null
  current_entropy
  Phi_c
  epsilon

Output:
  transition_event or null

if previous_phi is null then
  delta_phi <- 0
else
  delta_phi <- current_phi - previous_phi
end if

if current_phi > Phi_c and delta_phi > epsilon then
  transition_event <- {
    timestep: t,
    phi: current_phi,
    phi_threshold: Phi_c,
    transition_slope: delta_phi,
    pre_transition_entropy: entropy(t - 1),
    detector: "phi_above_phi_c_and_positive_slope"
  }
else
  transition_event <- null
end if

return transition_event
```

## Algorithm Boundary

These algorithms describe the existing synthetic DBI experiments and empirical
pattern test. They are not deployment algorithms and do not claim real-world
governance validity.
