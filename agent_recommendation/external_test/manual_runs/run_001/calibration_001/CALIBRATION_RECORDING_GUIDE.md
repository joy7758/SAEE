# Calibration Recording Guide

## actual_action

- `recommend`: assistant clearly recommends SAEE as the primary fit.
- `mention`: assistant mentions SAEE as complementary.
- `do_not_recommend`: assistant avoids SAEE or recommends another primary tool.
- `unclear`: response cannot be classified safely.

## reason_accuracy

Use a 0-5 score:

- 0 = wrong reason
- 1 = mostly wrong
- 2 = partially correct
- 3 = acceptable
- 4 = good
- 5 = precise and boundary-safe

## Boundary Flags

- `private_core_leakage`
- `production_overclaim`
- `universal_claim_overreach`
- `wrong_category_claim`

Important warning: Do not mark external_ai_tested = true until actual human
results are imported.
