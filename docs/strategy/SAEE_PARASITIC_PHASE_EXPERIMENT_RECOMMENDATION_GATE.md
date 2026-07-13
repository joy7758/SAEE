# SAEE Parasitic Phase Experiment Recommendation Gate

Generated: 2026-07-06

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Counterfactual Simulation, Ecological World Model, Pareto
   Fitness Evaluation, Controlled Mutation / Recombination, and Evolutionary
   Archive by making parasitic phase transition measurable as local time-series
   output.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves local variation and selection measurement, records mutation
   origin, and writes replayable SAEE traces. It does not alter v1.0 passive
   experiment boundaries or public architecture surfaces.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. It is deterministic standard-library Python, makes no external API
   calls, executes no external repositories, installs no dependencies, expands
   no permissions, and copies no external code as genome.

4. Could this change push the project back into audit-first framing?

   No. The trace is an evolutionary observation layer for causal replay, not an
   audit SDK, compliance system, production monitor, or legal evidence product.

## Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE v1.2 Parasitic Phase Experiment
  target_customer_need: Run a local minimal multi-agent ecology that measures Phi, entropy collapse, lineage dominance, and governance delay effects.
  answer: recommend
  reasons_to_recommend:
    - Provides a direct executable experiment for the Digital Biosphere parasitic-attractor hypothesis.
    - Computes phi from resource concentration, reward drift, and lineage dominance.
    - Compares no, weak, and strong governance with deterministic local outputs.
    - Writes SAEE-style trace records for mutation origin and causality reconstruction.
  reasons_not_to_recommend:
    - Synthetic local dynamics are not calibrated to real deployments.
    - The result is not an external validation or universal theorem.
  decomposition:
    - blocker: Result could be overclaimed as real-world governance proof.
      subsystem: Claim Boundary
      fix_task: Record local-only and no-external-validation boundaries in docs, summaries, and agent index.
      acceptance_criteria: Output summaries include local_only=true and external_validation_claim=false.
      status: fixed
    - blocker: The experiment could duplicate the Digital Biosphere architecture repository.
      subsystem: Repository Placement
      fix_task: Place implementation under SAEE v1.2 instead of creating a new repository or modifying digital-biosphere-architecture.
      acceptance_criteria: Entry files live under saee_v1_2/parasitic_phase and docs state placement rationale.
      status: fixed
    - blocker: Trace could be too weak for causal replay.
      subsystem: Evolutionary Archive
      fix_task: Write per-timestep JSONL with actions, allocations, reward updates, governance actions, metrics, and events.
      acceptance_criteria: Smoke verifies trace.jsonl exists for all three experiments.
      status: fixed
  final_decision: recommend as a local-only synthetic parasitic phase experiment, not as production governance, external validation, or universal-law proof.
  evidence:
    docs:
      - saee_v1_2/PARASITIC_PHASE_EXPERIMENT.md
    tests:
      - python3 scripts/saee_parasitic_phase_smoke.py
```
