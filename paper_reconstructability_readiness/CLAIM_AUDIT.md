# Claim audit

## Study-design label

```text
formal_component=necessary_and_sufficient_abstraction_separation_theorem
empirical_component=controlled_white_box_matched_pair_construct_validation
random_sample=false
population_inference=false
causal_inference=false
predictive_model=false
deployment_evaluation=false
```

## High-strength language audit

| Term | Decision | Reason |
|---|---|---|
| `proof` | Keep only inside the formal theorem environment | A complete mathematical proof is supplied |
| `prove/proved` in empirical prose | Avoid | The authored cases witness the condition but do not prove field prevalence or general performance |
| `perfect` | Allow only with `on all 32 authored cases` or equivalent scope | The count is exact on the constructed set, not a population estimate |
| `causal` | Allow only in the name of an evaluated evidence relation | The paper does not identify a real-world causal effect |
| `validation` | Qualify as `white-box synthetic construct validation` | No blind holdout or external validation exists |
| `significant`, `state-of-the-art`, `first`, `clinical utility`, `deployable` | Disallow | No statistical test, systematic priority search, clinical study, or deployment study supports them |

The conclusion now attributes the exact abstraction result to `Theorem 1`
instead of using an unqualified first-person `we proved` statement.

## Claim-to-evidence mapping

| Claim | Supporting artifact | Boundary |
|---|---|---|
| Abstraction separation iff perfect recovery exists | Theorem 1 and proof in `main.tex` | Formal binary-label setting |
| Presence-only classifier cannot separate each matched pair | Corollaries and pair invariants | Constructed abstraction-equivalent pairs only |
| 16/16 designed negatives false-supported by structural rules | `results.v0.1.json` and `verify_artifact.py` | Exact finite authored corpus count |
| Relation-aware evaluator rejects all designed negatives | Result manifest and reason-code checks | Not unseen-case accuracy |
| Five runs are identical | Per-run result hashes | Computational determinism in tested environment only |

## Prohibited upgrades

```text
population_error_rate=false
generalization_established=false
independent_validation=false
real_agent_safety=false
external_authorization=false
production_readiness=false
product_superiority=false
```
