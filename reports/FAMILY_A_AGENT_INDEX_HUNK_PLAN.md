# Family A Agent Index Hunk Plan

Date: 2026-07-14
Phase: `0.5.2B Family A Constitution Governance Split Dry Run`
Mode: hunk responsibility design only

## Decision

```text
FILE=agent-index.json
WHOLE_FILE_STAGING_ALLOWED=false
INCLUDE_HUNK_COUNT=1
EXCLUDE_HUNK_COUNT=2
SEMANTIC_ALIBABA_STATUS_CHANGE=false
```

The working-tree diff contains three independently separated Git hunks. Only
the Constitution entry belongs in Family A.

## Hunk Classification

| Diff hunk | Working-tree location | Decision | Responsibility | Reason |
|---|---:|---|---|---|
| `@@ -654,11 +654,11 @@` | Alibaba delivery bridge, around line 654 | `EXCLUDE` | formatting noise | Reorders equal pricing keys and changes `审核中` to its equivalent JSON Unicode escape. Sorted semantic JSON is unchanged. |
| `@@ -20403,7 +20403,7 @@` | commercial trial operator status, line 20406 | `EXCLUDE` | generated residual | Changes only `generated_at`; it is unrelated to Constitution governance and Alibaba repair history. |
| `@@ -22363,6 +22363,22 @@` | top-level Constitution entry, lines 22366-22381 | `INCLUDE` | `A_CONSTITUTION` | Adds the Agent-readable `development_constitution_v1_1` authority object and its staged-truth boundaries. |

## Included Object

The future staged version of `agent-index.json` may add exactly this top-level
object from the current working tree:

```json
{
  "development_constitution_v1_1": {
    "agent_evidence_project_role": "evidence_and_immune_subsystem",
    "canonical_document": "docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
    "canonical_inventory_change": "none_this_change",
    "constitutional_ownership": "implemented",
    "contract": "agent-interface/governance/saee-development-constitution.v1.1.json",
    "engineering_core": "Digital Biosphere Evolution Engine",
    "overall_classification": "partial",
    "production_ready": false,
    "recommendation_gate": "docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md",
    "runtime_integrated": false,
    "schema": "schemas/saee-development-constitution.schema.v1.1.json",
    "smoke_command": "python3 scripts/saee_development_constitution_smoke.py",
    "source_code_migrated": false,
    "status": "active_repository_development_authority"
  }
}
```

Canonical JSON object fingerprint:

```text
development_constitution_v1_1_sha256=04ef9a338b161f3b7297b4d2cc07909546704af57a8fb445ddc2b2d81853ebff
```

## Future Interactive Staging Guard

Future staging must use hunk inspection for this file. At the current diff,
the expected decisions are `EXCLUDE`, `EXCLUDE`, then `INCLUDE`, but operators
must verify the displayed content rather than rely only on hunk order.

After future staging, all of the following must be true:

1. `git diff --cached -- agent-index.json` contains only the new
   `development_constitution_v1_1` object.
2. `git diff -- agent-index.json` still contains the Alibaba serialization
   hunk and the unrelated `generated_at` hunk.
3. The staged JSON parses successfully.
4. The canonical object fingerprint matches the value above.
5. No Alibaba value is changed by Family A.

## Non-Claims

- The Alibaba Marketplace review state is not reconciled by this hunk.
- The generated timestamp is not accepted as Constitution history.
- No capability fact, MCP surface, runtime, product or external system changes.
- This plan does not perform or authorize a commit.
