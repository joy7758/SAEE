# Phase 0.5.2 Change Readiness Design

```text
ASSESSMENT_LEVEL=DESIGN_LEVEL
EXECUTION_ASSESSED=false
COMMIT_CREATED=false
STAGING_PERFORMED=false
```

## Intent

Create two auditable future histories: one for the Constitution governance
baseline and one for Alibaba product 68657 commercial repair, without changing
the Phase 0, Phase 0.5.1 or Dogfooding commits.

## Scope

- 17 pre-existing dirty paths.
- File and hunk responsibility only.
- No business, capability, MCP, runtime, Agent Evidence, product console,
  remote or history mutation.

## Evidence Needed Before Execution

1. Original status and content fingerprints still match.
2. Human confirmation of the latest authoritative Alibaba review status.
3. Classification of each `审核中` surface as current or historical.
4. Human disposition for the non-Constitution `agent-index.json` timestamp and
   formatting residuals.
5. Exact staged path/hunk inventory for Family A.
6. Staged JSON parse and Constitution, Codex, governance and ledger validation.
7. Exact staged path inventory for Family B and Alibaba-specific validation.
8. Post-commit ancestry and residual-worktree evidence.

## Risks

| Risk | Level | Control |
|---|---|---|
| Whole-file staging of `agent-index.json` contaminates Family A | High | Hunk-stage only the Constitution entry. |
| B commits rejected/repair state while current Agent-readable surfaces say review-in-progress | High | Confirm latest external truth and reconcile current-vs-historical surfaces first. |
| Full mainline guard rewrites local reconciliation snapshots | Medium | Run final mainline in an isolated disposable worktree. |
| Untracked Constitution files are omitted from A | High | Use the explicit Family A file list and staged-name audit. |
| Historical `审核中` observation is overwritten as if it never occurred | High | Preserve time-bounded observations and update only current truth surfaces. |
| A/B split is mistaken for Phase 1 readiness | Medium | Keep remote, Agent Evidence provenance and Phase 1 gates separate. |

## Recommendation

```text
DESIGN_LEVEL_RECOMMENDATION=BLOCK_EXECUTION_PENDING_TRUTH_AND_RESIDUAL_DECISIONS
```

The responsibility design is sufficient to identify the intended families,
but not sufficient to execute them. This is not a `CONTINUE` decision and does
not invoke or establish `saee.evaluate_change_readiness`.
