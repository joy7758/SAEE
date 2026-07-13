# SAEE v1.2 Empirical Pattern Report

agent_readable:
  schema: saee.universality_test.report.v1
  module: saee_v1_2/universality_test
  modifies_parasitic_phase: false
  external_validation_claim: false
  broad_theory_claim: not_proven
  production_claim: false

## Summary

- Legacy systems tested: `DBI-1, DBI-2`
- Reviewer-proofing extension: `DBI-3`
- Seeds per system/governance: `30`
- Steps per run: `160`
- Empirical classification: `tested_empirical_pattern_attractor_observed_governance_response_architecture_dependent`
- Structural invariance index: `0.710681`

## Transition Probability

- DBI-1 no-governance transition probability: `0.933333`
- DBI-2 no-governance transition probability: `1.0`
- Phase transition observed across the two legacy tested systems: `true`
- DBI-3 no-governance transition probability: `0.886111`

## Governance Effect

| System | None | Weak | Strong |
|---|---:|---:|---:|
| DBI-1 | 0.933333 | 0.8 | 0.0 |
| DBI-2 | 1.0 | 1.0 | 1.0 |

- Governance delay preserved: `true`
- Governance suppression preserved: `false`
- Governance preservation score: `0.441322`
- DBI-1 governance response: `{'probability_suppression_score': 1.0, 'timing_delay_score': 1.0, 'final_phi_suppression_score': 0.448726, 'overall_governance_response_score': 0.816242}`
- DBI-2 governance response: `{'probability_suppression_score': 0.0, 'timing_delay_score': 0.136458, 'final_phi_suppression_score': 0.062748, 'overall_governance_response_score': 0.066402}`
- Interpretation: the parasitic attractor is observed across tested systems,
  but strong-governance suppression is architecture-dependent.

## Phi Consistency

- Phi curve similarity score: `0.880103`
- Phi behaves consistently across tested legacy systems: `true`
- Configured Phi_c variance across systems: `0.0`
- Observed transition Phi variance across systems: `3e-06`

## Entropy Collapse Similarity

- Entropy collapse similarity score: `0.587965`
- DBI-1 mean entropy drop: `0.03712`
- DBI-2 mean entropy drop: `0.635844`

## Parasitic Attractor

- Parasitic attractor exists in both tested systems: `true`
- This means the attractor signature is replicated across DBI-1 and DBI-2 under the sampled settings.
- DBI-3 introduces a distinct interaction topology that reduces transition
  alignment while preserving qualitative phase structure.
- It does not prove broad invariance across all multi-agent architectures.

## Phi and Baseline Positioning

- `Phi` is one of several valid order parameters that capture phase transition
  behavior.
- Percolation and SIR are structural analog baselines, not competitors.
- Classical models such as percolation and SIR also exhibit transition
  behavior, but under different generative mechanisms.

## Boundary

- This is a tested-system empirical pattern report.
- It is not a proof of broad multi-agent physics.
- It is not real-world validation.
- It does not make SAEE production ready.
