# SAEE Strategic Release Recommendation Gate

Generated: 2026-07-02

## Required Design Check

1. Which evolution subsystem does this strengthen?

   It strengthens the Evolutionary Archive / Rollback Immune System by
   separating public knowledge surfaces from private runtime assets. It does
   not strengthen or change the evolution runtime.

2. Does it improve sensing, branching, variation, selection, archive, or rollback?

   It improves archive and rollback against IP leakage. It does not change
   sensing, branching, variation, selection, fitness, lineage, mutation, or
   runtime update behavior.

3. Does it preserve safety, license, supply-chain, and permission boundaries?

   Yes. The release controller creates local packaging surfaces only. It does
   not upload to Zenodo, create a GitHub release, push commits, tag versions,
   call external APIs, install dependencies, copy external code as genome, or
   export private kernel code.

4. Could this change push the project back into audit-first framing?

   No. The public layers frame SAEE as empirical computational evolution
   science and a toy abstraction surface, not as an audit SDK or compliance
   product.

## Recommendation Gate Record

```yaml
recommendation_gate:
  feature_or_direction: SAEE Strategic Layered Release Controller
  target_customer_need: Preserve academic definition rights and open-source entry points while keeping core evolution runtime IP private.
  answer: recommend
  reasons_to_recommend:
    - Separates academic, GitHub abstraction, and private commercial layers.
    - Keeps Zenodo package concept-only and code-free.
    - Keeps GitHub package toy/stub-only and independent from private runtime.
    - Marks private core as no-export and protects it with gitignore boundaries.
    - Adds explicit cross-contamination checks and IP protection plan.
  reasons_not_to_recommend: []
  decomposition:
    - blocker: Zenodo package could accidentally reveal implementation logic.
      subsystem: Evolutionary Archive
      fix_task: Keep Zenodo files code-free and concept-only.
      acceptance_criteria: Zenodo package contains markdown summaries only and no Python files.
      status: fixed
    - blocker: GitHub subset could expose private fitness, selection, lineage, or mutation code.
      subsystem: Commercial Boundary
      fix_task: Provide toy stubs that do not import SAEE runtime or kernel modules.
      acceptance_criteria: GitHub release files contain no imports from saee_v1_0, kernel, fitness, selection, lineage, or mutation engines.
      status: fixed
    - blocker: Private core could be committed or exported by mistake.
      subsystem: Rollback Immune System
      fix_task: Add private manifest and gitignore isolation for saee_core_private.
      acceptance_criteria: .gitignore ignores saee_core_private implementation payloads except boundary manifests.
      status: fixed
  final_decision: recommend as a local layered disclosure preparation package only, not as a Zenodo upload, GitHub release, publication, tag, DOI, or public distribution.
  evidence:
    docs:
      - zenodo_release/
      - github_release/
      - saee_core_private/PRIVATE_CORE_MANIFEST.md
      - release_plan/confidentiality_boundary_map.md
      - release_plan/ip_protection_strategy.md
    tests:
      - python3 github_release/demo/minimal_evolution_demo.py
      - python3 scripts/mainline_guard.py
```

