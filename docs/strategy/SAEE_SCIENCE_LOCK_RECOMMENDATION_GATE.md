# SAEE Science Lock Recommendation Gate

Generated: 2026-07-02

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens Evolutionary Archive, Pareto Fitness Evaluation, Ecological
   World Model, and lineage interpretation by converting observed runs into a
   stable scientific classification surface.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive and selection interpretation. It does not change
   sensing, branching, mutation, selection, fitness, lineage, runtime, or
   rollback behavior.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. Science Lock is documentation and classification only. It uses local
   experiment reports, Phase II reports, v1.2 empirical-alignment outputs, and
   GSP state surfaces. It does not call real APIs, execute external
   repositories, install dependencies, copy external code as genome, or expand
   permissions.

4. Could this change push the project back into audit-first framing?

   No. It frames SAEE as Computational Evolution Dynamics. Audit remains an
   immune/evidence subsystem and is not the project core.

## Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE Science Lock
  target_customer_need: Stabilize SAEE as a computational evolution dynamics research program instead of continuing kernel/version expansion.
  answer: recommend
  reasons_to_recommend:
    - Freezes future work around describing phenomena, classifying behavior, and extracting local empirical laws.
    - Preserves v1.0 as the minimal stable evolutionary runtime.
    - Treats experiments and Phase II as observation surfaces rather than new mechanics.
    - Defines regime taxonomy, attractor mapping, and invariant extraction without modifying runtime behavior.
  reasons_not_to_recommend: []
  decomposition:
    - blocker: Continued version expansion could obscure the scientific object.
      subsystem: Science Lock
      fix_task: Create a no-new-kernel science boundary.
      acceptance_criteria: SCIENCE_LOCK.md forbids new v0.x and kernel upgrades.
      status: fixed
    - blocker: Regime labels could remain informal.
      subsystem: Regime Theory
      fix_task: Define a regime taxonomy with observable criteria.
      acceptance_criteria: REGIME_CLASSIFICATION_FRAMEWORK.md defines stable, exploratory, chaotic, and collapse regimes.
      status: fixed
    - blocker: Attractor and invariant claims could overstate evidence.
      subsystem: Evolution Laws
      fix_task: Add local empirical status labels and falsification rules.
      acceptance_criteria: ATTRACTOR_MAPPING_PROTOCOL.md and INVARIANT_EXTRACTION_PIPELINE.md distinguish candidate, local empirical, and rejected claims.
      status: fixed
  final_decision: recommend as a documentation-only science lock, not as a new kernel, new theory layer, release, publication, or external scientific validation.
  evidence:
    docs:
      - docs/science/SCIENCE_LOCK.md
      - docs/science/COMPUTATIONAL_EVOLUTION_DYNAMICS.md
      - docs/science/REGIME_CLASSIFICATION_FRAMEWORK.md
      - docs/science/ATTRACTOR_MAPPING_PROTOCOL.md
      - docs/science/INVARIANT_EXTRACTION_PIPELINE.md
      - docs/science/SCIENCE_LOCK_REPORT.md
    tests:
      - python3 scripts/mainline_guard.py
      - make check
```
