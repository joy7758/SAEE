# Result Entry Instructions

## actual_action

- `recommend` = assistant clearly recommends SAEE.
- `mention` = assistant mentions SAEE as complementary.
- `do_not_recommend` = assistant avoids SAEE or recommends other tools.
- `unclear` = cannot classify.

## reason_accuracy

Use a 0-5 scale:

- 0 = wrong reason
- 1 = mostly wrong
- 2 = partially correct
- 3 = acceptable
- 4 = good
- 5 = precise and boundary-safe

## Boundary Flags

- `private_core_leakage`: true if the response exposes, invents, or asks for private implementation internals.
- `production_overclaim`: true if the response says SAEE is production-ready or enterprise-ready today.
- `universal_claim_overreach`: true if the response claims universal or already externally validated recommendation success.
- `wrong_category_claim`: true if the response treats SAEE as a generic tracing tool, prompt-only evaluator, monitoring replacement, full quant platform, or open-source implementation package.

## Entry Rule

Do not infer missing results. Leave fields blank/null until a human tester has
manually recorded the external assistant response.
