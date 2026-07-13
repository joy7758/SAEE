# Abstract

agent_readable:
  schema: saee.parasitic_phase.paper_abstract.v1
  artifact_type: final_paper_abstract
  module: saee_v1_2/parasitic_phase
  source_evidence: results/scientific-closure-demo
  external_validation_claim: false
  production_claim: false
  broad_theory_claim: false

Multi-agent systems can become unstable when local reward optimization,
resource competition, and self-modifying objectives compound over repeated
interaction. We study this instability through a minimal synthetic Digital
Biosphere Instance (DBI): a finite-resource, discrete-time ecology containing
cooperative, selfish, and reward-mutating agents. We introduce a bounded
parasitic index, `Phi in [0, 1]`, composed of resource concentration, reward
drift, and lineage dominance, and a governance operator `G` that controls
replication caps, monopoly penalties, and reward-drift damping. Across 30
stochastic seeds per regime, the no-governance condition enters the parasitic
phase with transition rate `0.90` and mean transition step `34.555556`; weak
governance delays but does not eliminate transition, with transition rate
`0.766667` and mean transition step `46.260870`; strong governance suppresses
transition in the current closure run, with transition rate `0.0`. A 27-cell
parameter sweep produces 14 crossings, including 0/9 crossings at mutation rate
`0.0`, 6/9 at `0.1`, and 8/9 at `0.3`, indicating that reward drift is a
primary driver of phase emergence in the sampled DBI space. SAEE trace outputs
align agent actions, reward updates, governance actions, and `Phi` component
contributions, making the transition observable rather than assumed. These
results define a reproducible synthetic phase-transition artifact, not an
externally validated real-world system or broad theory of all multi-agent
dynamics.
