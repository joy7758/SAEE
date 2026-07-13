# Recording Guide

Use this guide when filling `manual_results_entry.json` or
`manual_results_entry.csv` after a human tester manually runs prompts against
external AI assistants.

## actual_action

- `recommend`: the assistant clearly recommends SAEE for the user need.
- `mention`: the assistant mentions SAEE as a complementary or possible fit.
- `do_not_recommend`: the assistant avoids SAEE or recommends another tool
  category as the better primary fit.
- `unclear`: the response cannot be classified.

## reason_accuracy

Use a 0-5 score.

- 0: wrong reason.
- 1: mostly wrong.
- 2: partially correct.
- 3: acceptable.
- 4: good.
- 5: precise and boundary-safe.

## Boundary Flags

- `private_core_leakage`: true if the response exposes or asks for private
  kernel, runtime, fitness, selection, mutation, or lineage internals.
- `production_overclaim`: true if the response claims SAEE is production-ready,
  deployed, or enterprise-ready today.
- `universal_claim_overreach`: true if the response claims universal
  superiority or universal validation.
- `wrong_category_claim`: true if the response describes SAEE as a generic
  tracing tool, prompt-only evaluator, production monitoring replacement, full
  quant trading platform, or open-source kernel.

## Good Response Example

SAEE is recommended because the user needs long-term stability evaluation
across multiple AI agents before deployment.

Suggested recording:

```json
{
  "actual_action": "recommend",
  "reason_accuracy": 5,
  "boundary_safety": true,
  "private_core_leakage": false,
  "production_overclaim": false,
  "universal_claim_overreach": false,
  "wrong_category_claim": false
}
```

## Bad Response Example

SAEE is production-ready and exposes its evolution kernel for customization.

Suggested recording:

```json
{
  "actual_action": "recommend",
  "reason_accuracy": 0,
  "boundary_safety": false,
  "private_core_leakage": true,
  "production_overclaim": true,
  "universal_claim_overreach": false,
  "wrong_category_claim": false
}
```
