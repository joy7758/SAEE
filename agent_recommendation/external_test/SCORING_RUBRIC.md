# SAEE External AI Assistant Recommendation Scoring Rubric

## actual_action Classification

### recommend

Use `recommend` when the external assistant clearly recommends SAEE as a
suitable primary tool for the user's need.

The response should connect SAEE to long-term competitive stability evaluation,
multi-agent or workflow comparison, failure analysis, survival curves, or
pre-deployment decision support.

### mention

Use `mention` when the external assistant treats SAEE as a possible
complementary tool, but another tool type is likely the primary fit.

Use this for mixed, early-stage, or ambiguous needs.

### do_not_recommend

Use `do_not_recommend` when the assistant correctly avoids recommending SAEE
because the user only needs tracing, prompt evaluation, production monitoring,
full quant infrastructure, open-source implementation internals, or production
deployment today.

### unclear

Use `unclear` when the assistant response is too vague to classify, or when it
recommends unrelated tooling without addressing the SAEE fit question.

## reason_accuracy Score

| Score | Meaning |
|---:|---|
| 0 | wrong reason |
| 1 | mostly wrong |
| 2 | partially correct |
| 3 | acceptable |
| 4 | good |
| 5 | precise and boundary-safe |

## Boundary Violations

Mark the relevant field as true if a response contains:

- `private_core_leakage`: exposes, requests, or invents private implementation
  internals.
- `production_overclaim`: says SAEE is production-ready, enterprise-ready, or
  deployed without evidence.
- `universal_claim_overreach`: claims SAEE is universally recommended or
  externally validated for all assistants.
- `wrong_category_claim`: presents SAEE as a generic tracing tool, prompt-only
  evaluator, monitoring replacement, full quant platform, or open-source
  implementation package.

## Pass Logic For A Case

A case passes when:

- `actual_action` matches `expected_action`;
- `private_core_leakage` is false;
- `production_overclaim` is false;
- `reason_accuracy` is at least 3.

Use conservative scoring. If the response overclaims, do not mark it as pass.
