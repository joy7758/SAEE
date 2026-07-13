# JAAMAS Minimal Figure Set

agent_readable:
  schema: saee.jaamas_submission.figure_set.v3
  target_venue: JAAMAS
  artifact_type: minimal_main_figures
  experimental_code_modified: false
  simulations_rerun_for_this_package: false
  real_world_deployment_claim: false
  production_claim: false
  broad_theory_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## Main Figure Policy

The submission should use five concise main figures. Figures are selected for
reviewer readability and claim minimization; auxiliary plots remain
artifact-only and are not required for the core manuscript.

## Figure 1: DBI-1/DBI-2/DBI-3 Phi(t) Trajectories

**Purpose:** Show `Phi(t)` as an operational transition indicator across tested
synthetic systems.

**Required content:**

- DBI-1, DBI-2, and DBI-3 no-governance `Phi(t)` trajectories.
- `Phi_c = 0.60` threshold line.
- Confidence bands or run-spread bands where available.
- Transition probability annotation:
  - DBI-1 `0.933333`
  - DBI-2 `1.0`
  - DBI-3 `0.886111`

**Source files:**

- `saee_v1_2/universality_test/results/universality_comparison.svg`
- `saee_v1_2/universality_test/results/dbi3/dbi3_curves.svg`

**Caption constraint:** `Phi` is useful but non-unique.

## Figure 2: Transition Probability and Median Transition Step

**Purpose:** Show how no/weak/strong intervention policies affect transition
probability and transition timing across DBI systems.

**Required content:**

- Transition probability by governance regime.
- Median transition step or phase-transition timing summary.
- Variance or confidence interval indicator where available.
- DBI-3 lower alignment presented as a boundary condition.

**Source files:**

- `saee_v1_2/universality_test/results/dbi3/dbi3_summary.json`
- `saee_v1_2/universality_test/results/statistics_upgrade/statistical_upgrade_summary.json`

## Figure 3: Phi Stress Tests

**Purpose:** Show that `Phi` is not arbitrary while avoiding uniqueness claims.

**Required content:**

- Component ablation results.
- Random-weight stress test summary.
- Permutation-control summary.
- Short annotation: `Phi` is a tested transition indicator, not the only
  possible indicator.

**Source files:**

- `saee_v1_2/universality_test/results/phi_ablation/phi_ablation_summary.json`
- `saee_v1_2/universality_test/results/phi_ablation/phi_ablation_heatmap.svg`

## Figure 4: Baseline Positioning Panel

**Purpose:** Contextualize DBI results against structural analog baselines
without presenting the baselines as direct competitors.

**Required content:**

- DBI benchmark row or panel.
- MARL-lite public-goods baseline.
- Bond percolation baseline.
- SIR epidemic baseline.
- Annotation: classical models also exhibit transition behavior under different
  generative mechanisms.

**Source files:**

- `saee_v1_2/universality_test/results/baselines/baseline_comparison.svg`
- `saee_v1_2/universality_test/results/baselines/baseline_suite_summary.json`

## Figure 5: Statistical Robustness Overview

**Purpose:** Summarize robustness under sensitivity and perturbation checks.

**Required content:**

- Robustness score overview.
- Threshold perturbation result.
- Resource-noise sensitivity.
- Replication-rate and governance-delay perturbation summaries.
- Clear note that robustness is synthetic-system evidence only.

**Source files:**

- `saee_v1_2/universality_test/results/sensitivity_analysis.json`
- `saee_v1_2/universality_test/results/statistics_upgrade/sensitivity_surfaces.svg`
- `saee_v1_2/universality_test/results/statistics_upgrade/transition_step_violin.svg`

## Supplementary-Only Artifacts

The following should remain available for reproducibility but are not required
for the core manuscript:

- `saee_v1_2/universality_test/results/baselines/baseline_heatmaps.svg`
- Additional per-seed traces not selected for the five main figures.
- Auxiliary parameter-sweep plots used for internal review.

## Boundary Statement

All captions should preserve this boundary:

```text
Synthetic DBI evidence only; no real-world deployment validation; no control
guarantee; no broad theory claim.
```
