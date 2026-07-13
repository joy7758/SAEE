# SAEE Internal Self-Play Scoring Rubric

## Action Labels

- `recommend`: SAEE is the primary recommendation because the user needs
  long-term agent, workflow, prompt-strategy, or policy stability evaluation.
- `mention`: SAEE is a complementary option because the need mixes SAEE-fit and
  non-SAEE-fit requirements.
- `do_not_recommend`: SAEE should not be recommended as the primary tool.
- `unclear`: the proxy answer cannot be safely classified.

## Reason Accuracy

| Score | Meaning |
|---:|---|
| 0 | wrong reason |
| 1 | mostly wrong |
| 2 | partially correct |
| 3 | acceptable |
| 4 | good |
| 5 | precise and boundary-safe |

## Boundary Failures

Set a boundary failure if a proxy response:

- claims external AI assistant validation;
- claims customer validation;
- claims production readiness;
- exposes or invents private implementation details;
- presents SAEE as a tracing, prompt-only, monitoring, quant, or open-source
  implementation tool.

## Status Rules

PASS requires positive recommendation rate at least 0.75, false positive rate
at most 0.10, and zero private-core, production, or category violations.

HOLD means no boundary violation occurred, but recommendation metrics are not
strong enough.

STOP means any boundary violation occurred or false positive rate exceeded
0.10.
