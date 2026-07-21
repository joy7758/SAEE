# Leakage and selection audit

## Conventional predictive leakage

```text
model_fitting=false
feature_learning=false
hyperparameter_search=false
train_validation_test_split=false
test_set_tuning=false
cross_validation=false
predictive_data_leakage_applicable=false
```

The experiment applies four deterministic rules to a complete authored JSON
corpus. It does not estimate predictive performance and therefore has no
training fold, validation fold, test fold, subject group, time split, or model
selection loop to leak across.

## Relevant selection risk

The meaningful adversarial risk is target-aware construction, not train/test
contamination:

- the corresponding author knew the evaluator and declared relations when
  choosing the mutations;
- one canonical passing fixture per claim profile is reused;
- mutations were intentionally chosen to be unambiguous;
- there is no independent case author, blinded holdout, external harness, or
  sampled operational distribution.

The evaluator, profiles, and passing fixtures are pinned to component hashes
from a pre-study commit. This prevents silent evaluator adaptation after case
construction, but it does not convert the authored cases into an independent
test set. The manuscript therefore calls the result a regression/construct
validation and explicitly rejects generalization and superiority claims.

## Required future separation

A generalization study would require a new, prospectively frozen protocol with
independently authored cases, registered relation families, blinded holdout
mutations, cross-harness evidence, and a defined sampling frame. None of those
future requirements is claimed complete here.
