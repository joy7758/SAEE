# Codex Identity Alignment Test Report

Date: 2026-07-14
Phase: `0.5.1 Codex Identity Alignment`

## Baseline

```text
PHASE0_5_1_BASELINE_HEAD=be7b87ff2a7a31f9fd10594e3bf086071685632c
PHASE0_5_1_BASELINE_BRANCH=feat/canonical-capability-inventory-routing-v1
PHASE0_5_1_BASELINE_DIRTY_COUNT=21
RESET_RESTORE_CLEAN_PERFORMED=false
```

The 21 pre-existing changes were protected. Phase 0.5.1 intentionally absorbs
only the identity-contract subset (`.codex/context.md`, `AGENTS.md`, `README.md`
and `llms.txt`) plus the bounded validator, tests and reports.

## Before

Command:

```bash
python3 scripts/codex_context_check.py
```

Result:

```text
SAEE_CODEX_CONTEXT_CHECK: FAIL: .codex/context.md missing tokens: AI agent long-term stability evaluation
exit_code=1
```

Root cause: the active context had already moved to the constitutional identity,
while the validator still demanded the deprecated public/product sentence.

## After

| Command | Result |
|---|---|
| `python3 scripts/codex_context_check.py` | `SAEE_CODEX_CONTEXT_CHECK: PASS` |
| `python3 -m unittest tests/test_codex_context_check.py` | `4 tests`, `OK` |
| `make check-codex-context` | PASS; context check and `agent-index.json` parse succeeded |
| `python3 scripts/mainline_guard.py` | `MAINLINE_GUARD: PASS`; identity check and Constitution smoke passed inside the guard |
| `python3 scripts/saee_governance_registry_check.py` | PASS; registries `6/6`, capability source remains `LOCAL_ONLY` |
| `python3 -m unittest tests/test_governance_registry.py tests/test_codex_context_check.py` | `12 tests`, `OK` |
| `python3 scripts/saee_development_constitution_smoke.py` | PASS; `source_code_migrated=false`, `runtime_integrated=false`, `production_ready=false` |
| `python3 scripts/saee_capability_progress_ledger_smoke.py` | PASS; capability statuses `9/9`, duplicate-build prevention `true` |

The full mainline guard invokes reconciliation smokes that rewrite local status
snapshots even when they pass. All such validation-generated diffs were removed
with a path-bounded reverse patch after confirming those paths were clean before
the run. No `git reset`, `git restore` or `git clean` was used, and none of the
21 protected baseline changes was reverted.

## Negative Coverage

The focused test proves that the validator rejects:

1. `AI agent long-term stability evaluation` as an active Codex identity;
2. `SAEE is an Agent Readiness Infrastructure` as a replacement root identity;
3. duplicate `Development authority:` claims.

It also proves that the current constitutional context passes.

## Validation Boundary

```text
codex_identity_aligned=true
validator_strength_reduced=false
mainline_identity_drift_resolved=true
capability_fact_change=false
business_behavior_change=false
product_definition_change=false
production_ready=false
```
