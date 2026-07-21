# Retrospective frozen analysis plan

```text
plan_status=retrospective_frozen_specification
preregistered=false
random_sampling=false
stochastic_training=false
hypothesis_significance_testing=false
multiple_testing=false
population_inference=false
```

This file documents the complete analysis after construction of the artifact.
It is not a preregistration and must never be cited as one.

## Primary questions

1. Do all 16 positive/negative pairs preserve required-field presence?
2. Do all 16 pairs preserve complete JSON key/type shape?
3. Does the authored semantic label diverge within every pair?
4. How many of the 16 designed negatives are false-supported by each of four
   deterministic rules?
5. Do semantic verdicts and localized reason codes match all authored
   expectations?
6. Are five complete executions byte-stable at the canonical-result level?
7. Do any outputs set a protected authority-boundary field to true?

## Complete analysis set

- 16 matched pairs and 32 cases; no exclusions.
- Four claim profiles, exactly four pairs per profile.
- Four rules: field presence, type/shape, affirmative-decision ablation, and
  the existing relation-aware profile evaluator.
- Exact confusion counts and false-support counts for the complete authored
  corpus.
- Pair invariants, reason-code matches, component hashes, run hashes, and
  protected boundary fields.

## Statistical boundary

The cases are constructed witnesses rather than a random sample. Counts and
rates are descriptive properties of the complete authored corpus. Confidence
intervals, p-values, power calculations, and repeated-run variance are not
reported because no sampling frame or stochastic data-generating mechanism is
defined. Five repetitions test determinism; they are not independent samples.

## Selection disclosure

The corresponding author knew the evaluator during case construction. Pinned
pre-study evaluator/profile/fixture hashes prevent implementation drift, not
case-selection bias. No blinded holdout or independent external validation is
claimed.
