# Negative Results and Boundary Conditions

agent_readable:
  schema: saee.jaamas_submission.negative_results.v1
  target_venue: JAAMAS
  artifact_type: negative_result_boundary
  experimental_code_modified: false
  simulations_rerun_for_this_package: false
  results_files_modified: false
  real_world_deployment_claim: false
  production_claim: false
  broad_theory_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## DBI-3 Alignment Reduction

DBI-3 introduces a distinct interaction topology that reduces transition
alignment while preserving qualitative phase structure. This should be reported
as a finding, not as a failed replication.

| System | No-governance transition probability | Interpretation |
|---|---:|---|
| DBI-1 | `0.933333` | Strong transition presence in finite-resource ecology |
| DBI-2 | `1.0` | Strong transition presence in heterogeneous topology |
| DBI-3 | `0.886111` | Weaker alignment with preserved qualitative structure |

## Governance Suppression Is Not Uniform

Strong governance suppresses transitions in DBI-1 and DBI-3 under tested
settings but not in DBI-2. The manuscript should therefore state that
intervention response is architecture-dependent.

## `Phi` Is Non-Unique

`Phi` survives stress testing as an operational transition indicator, but the
experiments do not show that it is uniquely necessary or uniquely explanatory.
Entropy, dominance, and related macrostate variables remain relevant supporting
observables.

## Baselines Show Related Transition Behavior

Bond percolation and SIR also exhibit transition behavior under different
generative mechanisms. This contextualizes the DBI benchmark and prevents an
overclaim that transition-like behavior is exclusive to the proposed systems.

## Boundary Statement

The negative results strengthen the submission by defining the tested boundary:
the evidence supports empirically observed cross-system consistency within a
shared synthetic multi-agent modeling framework, not a model-independent claim.
