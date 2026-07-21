# Phase 0.5.2 Formal History Split Gate

## Gate Result

```text
CURRENT_STATE=HEAD_f6ac41f4_DIRTY_17_STAGED_0
SPLIT_READY=NO
BLOCKERS=AGENT_INDEX_MIXED_SCOPE;ALIBABA_68657_STATUS_TRUTH_DRIFT
NEXT_ACTION=CONFIRM_ALIBABA_LATEST_STATUS_AND_CLASSIFY_AGENT_INDEX_RESIDUALS
PHASE0_5_2_STATUS=BLOCKED
```

## 1. Can Commit Splitting Start?

No. Family A can be isolated with hunk staging, but the complete two-family
split is not ready. Starting now risks either contaminating Constitution history
with unrelated `agent-index.json` residuals or committing a commercial repair
whose current truth surfaces disagree.

## 2. Is The Split Design Clear?

Partially:

- Family A has an exact whole-file list plus one Constitution-only
  `agent-index.json` hunk.
- Family B has five clear repair-package files.
- Family B's surrounding current-vs-historical Alibaba status ownership is not
  yet resolved.

## 3. Are There Blockers?

Yes.

### Blocker 1: `agent-index.json` mixed responsibility

The file adds `development_constitution_v1_1`, changes
`commercial_trial_operator_status_v0_1.generated_at`, and contains a
semantically neutral Alibaba key-order rewrite. Only the Constitution object
belongs in Family A. The other hunks have no approved disposition.

### Blocker 2: Alibaba 68657 staged-truth drift

The governance asset registry and repair files record rejected/repair/not
listed. Multiple current Agent-readable and readiness surfaces still record
`审核中` / review in progress. This audit did not re-read the external console,
so it cannot decide which current state is authoritative or which records are
historical snapshots.

## 4. Is A Human Decision Required?

Yes, before any `git add`:

1. confirm the latest authoritative review state for product `68657` /
   `cmfw00074657` and its evidence timestamp;
2. approve whether the non-Constitution `agent-index.json` timestamp and
   formatting hunks are deferred, separately preserved or removed in a later
   authorized cleanup.

No decision is required about Agent Evidence migration, MCP, API, website,
remote or Phase 1 because all remain out of scope and unauthorized.

## 5. What Is The Next Command?

```text
NEXT_COMMAND=NONE_UNTIL_HUMAN_DECISIONS_RECORDED
```

After those decisions and a refreshed read-only audit, the first staging action
may be exact-path staging for Family A followed by `git add -p agent-index.json`.
That action was not executed here.

## History Integrity

- Constitution history can remain continuous after the A hunk is isolated.
- Alibaba history is not yet coherent enough for a current-state repair commit.
- Dogfooding commit `f6ac41f4…` and assessed commit `e12f62a2…` remain intact.
- Capability inventory and ledger are outside both families.
- Governance registry structure is unchanged.
- Remote preparation remains a later independent gate.

## Audit Integrity

```text
original_status_sha256_before=46b2a025582f6698a41b2f16ce0e3f11ded1dcb66db321fee5c617a126c48b82
original_status_sha256_after=46b2a025582f6698a41b2f16ce0e3f11ded1dcb66db321fee5c617a126c48b82
original_dirty_content_sha256_before=1fb068d8a5f002e7b312fa5099ec7040b771645cadc4d0cd97a451989c5ec830
original_dirty_content_sha256_after=1fb068d8a5f002e7b312fa5099ec7040b771645cadc4d0cd97a451989c5ec830
original_dirty_count_before=17
original_dirty_count_after=17
staged_count_after=0
new_requested_report_count=6
```

The full `git status` output necessarily gains the six requested untracked
reports. After excluding only those named outputs, the original status and
content fingerprints are identical. No original dirty file changed.

## Final

```text
CURRENT_STATE=HEAD_f6ac41f4_DIRTY_17_STAGED_0
SPLIT_READY=NO
BLOCKERS=AGENT_INDEX_MIXED_SCOPE;ALIBABA_68657_STATUS_TRUTH_DRIFT
NEXT_ACTION=CONFIRM_ALIBABA_LATEST_STATUS_AND_CLASSIFY_AGENT_INDEX_RESIDUALS
PHASE0_5_2_STATUS=BLOCKED
```
