# SAEE v0.8 Backward Compatibility Map

## v0.7 Compatibility

v0.8 wraps `saee_v0_7.runtime.reflexive_kernel.ReflexiveEvolutionKernel`.
It does not remove v0.7 explanation-driven mutation, epistemic fitness,
semantic selection, observer-in-the-loop feedback, recursive self-modeling, or
explanation-influenced lineage.

v0.8 adds post-cycle identity constraints and writes bounded feedback,
bounded self-model state, and identity-filtered population state back into the
next v0.7 generation.

## Earlier Compatibility

- v0.1 remains the local single-loop seed contract.
- v0.2 remains the local population ecology contract.
- v0.3 remains guarded meta-evolution.
- v0.4 remains mutable evolution-space dynamics.
- v0.5 remains generated evolution physics.
- v0.6 remains observability.
- v0.7 remains reflexive evolution.

## New Constraint

Identity continuity is now a first-class selection and lineage constraint:

```text
reflexive change is allowed
identity-core mutation is not allowed
semantic drift is bounded
self-model recursion is bounded
```

## Boundary

v0.8 is a local prototype. It does not claim self-awareness, verified identity
continuity, real semantic causality, production use, release, DOI, or external
publication.

