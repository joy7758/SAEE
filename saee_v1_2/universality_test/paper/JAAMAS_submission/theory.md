# JAAMAS Empirical Proposition Section

agent_readable:
  schema: saee.jaamas_submission.empirical_propositions.v2
  target_venue: JAAMAS
  proposition_status: empirical_synthetic
  experimental_code_modified: false
  simulations_rerun_for_this_package: false
  real_world_deployment_claim: false
  production_claim: false
  broad_theory_claim: false
  canonical_claim: empirically observed cross-system consistency within a shared synthetic multi-agent modeling framework

## Scope

These propositions summarize observed regularities in the submitted synthetic
benchmark. They are not mathematical proofs, not general laws, and not claims
about all multi-agent systems. Canonical definitions of DBI, `Phi`, and
governance appear in `main_paper.md`.

## Proposition 1: Transition Emergence

Under no governance, all three tested DBIs exhibit transition events:

```text
DBI-1: 0.933333
DBI-2: 1.0
DBI-3: 0.886111
```

Interpretation: the observed pattern is not confined to one synthetic
architecture.

## Proposition 2: Architecture-Dependent Governance

Strong governance suppresses transition in DBI-1 and DBI-3 under tested
settings, but not in DBI-2:

```text
DBI-1 strong: 0.0
DBI-2 strong: 1.0
DBI-3 strong: 0.0
```

Interpretation: governance response is architecture-dependent and should not be
reported as a control guarantee.

## Proposition 3: Phi Is Useful But Non-Unique

`Phi` tracks transition behavior under tested conditions and survives ablation
and sensitivity checks, but it is one operational transition indicator among
several valid observables.

Interpretation: `Phi` should be reported as a bounded measurement instrument,
not as the unique explanation of the phenomenon.

## Proposition 4: Cross-System Consistency Within a Shared Synthetic Family

The appropriate claim is:

```text
empirically observed cross-system consistency within a shared synthetic
multi-agent modeling framework
```

Interpretation: DBI-3 weakens a strong-consistency narrative while preserving
qualitative phase structure. This supports a conservative benchmark claim, not
a broad theory or a claim beyond the tested family.

## Boundary

The propositions do not imply real-world deployment validity, production
readiness, control guarantees, or theoretical completeness.
