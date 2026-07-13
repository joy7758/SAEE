# Robustness and Sensitivity Analysis

agent_readable:
  schema: saee.jaamas_submission.robustness_section.v1
  target_venue: JAAMAS
  source: saee_v1_2/universality_test/results/sensitivity_analysis.json
  analysis_mode: post_hoc_existing_outputs_only
  simulations_rerun_for_this_section: false
  experimental_code_modified: false
  real_world_deployment_claim: false
  broad_theory_claim: false

## Robustness Summary

We performed a post-hoc sensitivity analysis over existing outputs without
rerunning simulations or modifying DBI, `Phi`, or governance logic. The analysis
tests whether the observed phase-transition signature remains stable under
threshold perturbation, resource-concentration noise, replication-rate
variation from the existing parameter sweep, and governance delay variation
from the existing empirical pattern test.

The overall robustness score is:

```text
overall_robustness_score = 0.913273
```

This score is a reviewer-facing stability index for the current synthetic
evidence package. It is not a real-world validation score.

## Phi Threshold Sensitivity

The phase threshold was perturbed by `+/- 10%` around `Phi_c = 0.60`:

```text
Phi_c in {0.54, 0.60, 0.66}
```

The transition-presence stability score is:

```text
threshold_presence_stability_score = 0.733333
```

Interpretation: the phase transition remains observable under threshold
perturbation, but threshold choice affects transition timing and marginal cases.
This supports the use of `Phi_c` as an operational threshold while motivating
future threshold sensitivity analysis in a larger appendix.

## Resource Noise Sensitivity

Resource noise was tested by post-hoc scaling of the resource concentration
component in existing DBI-1 traces:

```text
resource_noise in {-20%, -10%, -5%, +5%, +10%, +20%}
```

The transition-presence stability score is:

```text
resource_noise_presence_stability_score = 0.833333
```

Interpretation: `Phi` remains robust under tested resource-component noise, but
the transition boundary can shift in timing. No environment resources were
changed and no simulation was rerun. `Phi` is treated as one operational
transition indicator rather than a unique explanatory variable.

## Replication-Rate Sensitivity

Replication-rate sensitivity uses the existing 27-cell parameter sweep. All
three replication levels show at least one transition:

```text
low:    crossing present
medium: crossing present
high:   crossing present
```

The replication presence stability score is:

```text
replication_presence_stability_score = 1.0
```

Interpretation: phase transition presence is robust across the tested
replication-rate levels, while crossing frequency depends on mutation and
constraint settings.

## Governance Delay Sensitivity

Governance delay is robust across DBI-1 and DBI-2:

```text
governance_delay_stability_score = 1.0
```

Governance suppression is not robust across architectures:

```text
governance_suppression_stability_score = 0.0
```

Interpretation: governance can shift transition timing in the tested systems,
but the ability of strong governance to suppress transition is
architecture-dependent. This supports the paper's observed-pattern claim:
instability emergence is robust under tested conditions, while intervention
effectiveness is heterogeneous.

## Phi_c Variance

The configured critical threshold is identical across systems:

```text
configured_phi_c_variance_across_systems = 0.0
```

Observed transition `Phi` variance across DBI-1 and DBI-2 is:

```text
observed_transition_phi_variance_across_systems = 0.000003
```

This supports `Phi` as a stable operational transition indicator in the current
tested-system evidence package, without implying uniqueness or necessity.

## DBI-3 Interpretation

DBI-3 introduces a distinct interaction topology that reduces transition
alignment while preserving qualitative phase structure. Its no-governance
transition probability is `0.886111`, compared with `0.933333` in DBI-1 and
`1.0` in DBI-2. This reduction is reported as a finding, not a failure.

## Structural Analog Baseline Interpretation

Percolation and SIR are structural analog baselines, not competitors. Classical
models such as percolation and SIR also exhibit transition behavior, but under
different generative mechanisms.

## Submission Claim

The reviewer-safe claim is:

```text
The phase-transition signature is empirically observed in two synthetic DBI
systems, extended by a third DBI stress test, and is robust under tested
post-hoc perturbations. Governance can delay transition across systems, but
suppression is architecture-dependent.
```

The paper does not claim real-world validation, production governance, or a
broad theory over all multi-agent systems.
