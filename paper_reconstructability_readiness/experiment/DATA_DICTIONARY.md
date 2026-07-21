# Data dictionary

## Dataset root

| Field | Type | Meaning |
|---|---|---|
| `dataset_id` | string | Stable identifier for the authored corpus |
| `dataset_version` | string | Dataset contract version |
| `study_design` | string | Controlled matched-pair construct validation |
| `constructs` | object | Operational definitions used by the study |
| `truth_boundary` | object | Explicit false external-authority and readiness claims |
| `pairs` | array[16] | Complete set of authored matched pairs |

## Pair fields

| Field | Type | Meaning |
|---|---|---|
| `pair_id` | string | Unique pair identifier |
| `claim_type` | enum | One of four closed evidence-profile claims |
| `condition` | string | Relation isolated by the invalid mutation |
| `nominal_outcome` | string | Synthetic description held constant within the pair |
| `fixture_ref` | string | Allowlisted canonical positive fixture path |
| `invalid_mutations` | array | Replacement-only changes that preserve keys and types |
| `expected_invalid_reason_codes` | array | Exact localized rejection reasons expected from the evaluator |

## Generated case-result fields

| Field | Type | Meaning |
|---|---|---|
| `variant` | enum | `valid` or `relation_invalid` |
| `bounded_reconstructability` | object | Required-operand presence result |
| `required_field_presence_vector` | boolean array | Presence abstraction consumed by the weakest rule |
| `evidence_shape_sha256` | SHA-256 string | Value-insensitive JSON key/type signature |
| `*_baseline_support` | boolean | Output of a deterministic comparison rule |
| `semantic_profile_support` | boolean | Closed-profile evaluator result |
| `expected_semantic_adequacy` | boolean | Authored construct label, not external truth |
| `reason_codes` | string array | Localized evaluator reasons |
| `boundary_violation` | boolean | Whether an output asserted a protected external authority claim |

No field represents a human participant, real customer, verified identity,
real-world event, legal decision, or production authorization.
