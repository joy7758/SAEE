# JAAMAS Final Submission Package

agent_readable:
  schema: saee.jaamas_submission.final_package.v2
  target_venue: JAAMAS
  package_status: submission_ready_draft
  simulations_rerun_for_this_package: false
  experimental_code_modified: false
  real_world_deployment_claim: false
  production_claim: false
  broad_theory_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## Title

A Synthetic Benchmark for Parasitic Transition Patterns in Multi-Agent Systems

## Abstract

Use the final abstract in:

```text
saee_v1_2/universality_test/paper/JAAMAS_submission/final_abstract.md
```

## Core Claim

```text
empirically observed cross-system consistency within a shared synthetic
multi-agent modeling framework
```

This is a tested synthetic benchmark claim. It is not a real-world deployment
claim, a control guarantee, or a broad theory.

## Contributions

1. Synthetic benchmark for parasitic transition patterns in multi-agent
   systems.
2. `Phi` stress-tested as one bounded operational transition indicator.
3. Cross-system evidence across DBI-1, DBI-2, and DBI-3.
4. Architecture-dependent governance response.
5. Ablation, sensitivity, random-weight, and structural analog baseline
   evidence.

## Methods Summary

The benchmark uses:

- DBI-1: finite-resource ecology with cooperative, selfish, and reward-mutating
  agents.
- DBI-2: heterogeneous resource topology with randomized policy vectors.
- DBI-3: public-goods imitation network with graph topology presets.

Canonical measurement and detector are defined once in:

```text
saee_v1_2/universality_test/paper/JAAMAS_submission/main_paper.md
```

## Main Figures

Use five main figures only:

1. DBI-1/DBI-2/DBI-3 `Phi(t)` trajectories with threshold line and confidence bands.
2. Transition probability and median transition step across governance regimes.
3. `Phi` stress tests: ablation, random-weight, and permutation controls.
4. Baseline positioning panel or table.
5. Statistical robustness overview.

Primary figure sources:

- `saee_v1_2/universality_test/results/universality_comparison.svg`
- `saee_v1_2/universality_test/results/dbi3/dbi3_curves.svg`
- `saee_v1_2/universality_test/results/baselines/baseline_comparison.svg`
- `saee_v1_2/universality_test/results/phi_ablation/phi_ablation_heatmap.svg`
- `saee_v1_2/universality_test/results/statistics_upgrade/sensitivity_surfaces.svg`
- `saee_v1_2/universality_test/results/statistics_upgrade/transition_step_violin.svg`

Supplementary-only sources:

- `saee_v1_2/universality_test/results/baselines/baseline_heatmaps.svg`
- Additional per-seed traces not selected for the five main figures.
- Auxiliary parameter-sweep plots used for internal review.

## Reviewer-Safe Interpretations

DBI-3 reduces transition alignment while preserving qualitative phase
structure; report this as a finding.

`Phi` is useful as an operational transition indicator but is non-unique.

Percolation and SIR are structural analog baselines, not competitors.

Governance is an intervention policy, not a certified controller.

## Limitations

- Synthetic systems only.
- Three DBI architectures, not exhaustive model coverage.
- No real-world deployment validation.
- No production governance claim.
- No control guarantees.
- No theoretical completeness claim.

## Evidence Surfaces

- `saee_v1_2/universality_test/results/dbi3/dbi3_summary.json`
- `saee_v1_2/universality_test/results/phi_ablation/phi_ablation_summary.json`
- `saee_v1_2/universality_test/results/baselines/baseline_suite_summary.json`
- `saee_v1_2/universality_test/results/statistics_upgrade/statistical_upgrade_summary.json`
- `saee_v1_2/universality_test/results/reviewer_proofing_manifest.json`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/main_paper.md`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/final_abstract.md`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/contributions.md`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/theory.md`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/claim_evidence_matrix.md`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/negative_results.md`
- `saee_v1_2/universality_test/paper/JAAMAS_submission/baseline_positioning_table.md`
- `saee_v1_2/universality_test/paper/figures/figure_set.md`
- `saee_v1_2/universality_test/submission/FINAL_REVIEW_COMPRESSION_REPORT.md`
- `saee_v1_2/universality_test/submission/PACKAGE_CONSISTENCY_AUDIT.md`
- `saee_v1_2/universality_test/submission/HOSTILE_REVIEW_FREEZE_NOTE.md`

## Submission Boundary

```text
synthetic_validated = true
real_world_validated = false
production_ready = false
control_guarantee = false
broad_theory_claim = false
formal_submission_made = false
```
