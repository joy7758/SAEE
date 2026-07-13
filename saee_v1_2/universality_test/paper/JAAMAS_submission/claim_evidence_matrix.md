# Claim-Evidence Matrix

agent_readable:
  schema: saee.jaamas_submission.claim_evidence_matrix.v1
  target_venue: JAAMAS
  artifact_type: reviewer_claim_boundary
  experimental_code_modified: false
  simulations_rerun_for_this_package: false
  results_files_modified: false
  real_world_deployment_claim: false
  production_claim: false
  broad_theory_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## Purpose

This matrix maps each manuscript claim to the evidence surface that supports it
and to the conservative wording that should be used in the submission.

| Claim area | Manuscript location | Evidence surface | Support level | Reviewer risk | Safe wording |
|---|---|---|---|---|---|
| DBI-1/2/3 transition pattern | `main_paper.md` Abstract and Results | `results/dbi3/dbi3_summary.json`; `results/statistics_upgrade/statistical_upgrade_summary.json` | Partial-to-strong within the shared synthetic family | Over-read as model-independent | Empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework |
| Governance heterogeneity | `main_paper.md` Results and Discussion | `results/dbi3/dbi3_summary.json`; `results/sensitivity_analysis.json` | Strong under tested DBI settings | Misread as a control guarantee | Governance is an intervention policy with architecture-dependent response |
| `Phi` robustness | `main_paper.md` Methods and Stress Tests | `results/phi_ablation/phi_ablation_summary.json`; `results/sensitivity_analysis.json` | Moderate-to-strong as a tested indicator | Misread as a unique theory variable | `Phi` is an operational transition indicator and is non-unique |
| Structural analog baselines | `main_paper.md` Baselines | `results/baselines/baseline_suite_summary.json` | Contextual support | Misread as direct superiority testing | Percolation, SIR, and MARL-lite are structural analog baselines, not competitors |
| Scope boundary | Abstract, Limitations, final package | `final_abstract.md`; `JAAMAS_FINAL_PACKAGE.md`; this matrix | Fully supported by wording | Inconsistent artifact framing | Synthetic benchmark only; no deployment validity, production readiness, or complete theory claim |

## Canonical Claim

```text
empirically observed cross-system consistency within a shared synthetic
multi-agent modeling framework
```

## Disallowed Expansion

The submission should not describe the result as a model-independent theory, a
deployment validation, a guaranteed governance mechanism, or a complete account
of multi-agent instability.
