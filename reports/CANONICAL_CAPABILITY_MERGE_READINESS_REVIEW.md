# Canonical Capability Inventory — Merge Readiness Review

Date: 2026-07-14

## Executive Decision

```text
capability_change_reviewable=true
canonical_capability_checks_pass=true
draft_pr_ready=false
merge_ready=false
published=false
```

Status:
`blocked_incompatible_remote_and_non_idempotent_full_check`.

The capability inventory and routing implementation can enter local code review,
but it must not be described as pushed, proposed in a Draft PR, merged or
published. Two independent merge blockers remain: no verified compatible Git
remote, and a non-idempotent full-check sequence.

## Scope Reviewed

Branch: `feat/canonical-capability-inventory-routing-v1`

Commits reviewed through:
`a383ee0dd` (`docs: keep agent startup files as truth pointers`).

Local comparison base: `main` at `00d8d0467`.

The branch was four commits ahead of local `main` at review time. The local PR
diff contained 27 files, 3,419 insertions and 32 deletions before this review
report was added. `git diff --check main...HEAD` passed, and the diff scan found
no absolute local-home path, private-key marker, GitHub token pattern or AWS
access-key pattern.

## Finding 1 — Startup Files Were Becoming A Second Truth Source

Severity: `MERGE_REVIEW_FIX_APPLIED`

The first implementation copied live capability status, OTEL status, completion
state and a dated snapshot into `AGENTS.md` and `llms.txt`. That contradicted the
decision that `capability-package/manifest.json#canonical_inventory` is the sole
capability-fact authority.

Fix applied in commit `a383ee0dd`:

- `AGENTS.md` now contains only authority pointers, startup rules and the
  duplicate-build procedure.
- `llms.txt` now contains only discovery pointers and working rules.
- live capability status and MCP classification must be resolved at task start;
  they are not copied into either startup file.
- the ledger validator rejects reintroduction of dated or live-status snapshots.
- ledger adversarial coverage increased from `5/5` to `7/7`.

This preserves the user's requirement that Agents see progress immediately
while preventing the start file from becoming another capability ledger.

## Finding 2 — No Compatible Remote Is Verified

Severity: `BLOCKING`

Initial state:

```text
git remote -v -> no configured remote
gh authenticated account -> joy7758
```

Read-only GitHub discovery found one exact-name candidate:

```text
repository=joy7758/SAEE
url=https://github.com/joy7758/SAEE
default_branch=main
remote_main=e503c22109bdb7c83dc465d66e2a22760a3c8d90
```

The candidate cannot safely be assigned as `origin`:

```text
local_main=00d8d0467761fe044355aeb678f3cd12efc6c7cf
remote_candidate_main=e503c22109bdb7c83dc465d66e2a22760a3c8d90
merge_base=NONE
remote_contains_local_baseline=false
remote_contains_AGENTS.md=false
```

The remote is a smaller public canonical-layer history, not a compatible
upstream for this full working tree. No remote was added, no branch was pushed
and no PR was created.

Required resolution: the repository owner must identify the actual upstream for
this full checkout, or explicitly choose a publication strategy that reconciles
the unrelated histories. That choice cannot be inferred by an Agent.

## Finding 3 — Declared Test Tooling Does Not Include Pytest Or Pre-commit

Severity: `ENVIRONMENT_AND_REPOSITORY_GAP`

Repository dependency audit found:

```text
dependency_manifest=saee_backend/requirements.txt
declared_runtime_dependencies=fastapi,uvicorn,pydantic,jsonschema
pytest_declared=false
pre_commit_declared=false
pre_commit_config_present=false
pytest_style_files=1
```

The one filename matching a pytest-style search is
`scripts/saee_internal_self_play_recommendation_test.py`; it is a standalone
generator/test script, not evidence of a configured pytest suite.

Exact command results:

```text
python3 -m pytest -> No module named pytest (exit 1)
pytest -> command not found (exit 127)
pre-commit run --all-files -> command not found (exit 127)
```

Installing `pytest` and `pre-commit` ad hoc would not validate a declared
project workflow because neither tool nor a pre-commit configuration is present
in repository dependency metadata. This review did not add undeclared supply
chain dependencies merely to manufacture green command output.

Required resolution: either document these commands as non-applicable for this
repository, or add an intentional development-dependency/test configuration in
a separate scoped change.

## Finding 4 — Full Check Is Not Idempotent

Severity: `BLOCKING_FOR_CLEAN_MERGE_GATE`

The review created a detached worktree at `a383ee0dd` and ran the repository's
declared checks.

First pass:

```text
make check -> exit 0
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: PASS
SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: PASS
MAINLINE_GUARD: PASS
```

After `make check`, the isolated worktree contained 41 tracked modifications,
primarily generated commercial-readiness timestamps and local state. Some
existing scripts also wrote generated output back to the primary checkout,
where 190 tracked test-side-effect files had to be restored without committing
them.

A direct second guard run in the same isolated sequence failed:

```text
python3 scripts/mainline_guard.py -> exit 1
SAEE_CONTROLLED_REASONING_LIVE_EVIDENCE_SMOKE: FAIL
missing output/controlled-rehearsal/qianfan-baseline-metadata-v0.2.run.json
```

Interpretation: `make check` can report success from a clean starting state but
does not leave a clean, immediately repeatable state. The failure is outside the
canonical capability implementation and appears to come from existing generated
commercial/rehearsal state. This PR does not rewrite those unrelated systems.

Required resolution before merge: identify and fix or explicitly isolate the
generator/order dependency so that the declared merge sequence finishes with a
clean worktree and a repeated guard pass.

## Capability-Specific Verification

The following remained green after the startup-file fix and after the full-check
side effects:

```text
SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: PASS
negative_cases=16/16
required_coverage=24/24
deterministic_runs=5/5

SAEE_CAPABILITY_PROGRESS_LEDGER_SMOKE: PASS
surfaces=6/6
negative_cases=7/7

SAEE_OTEL_CANDIDATE_MAPPING_SMOKE: PASS
SAEE_EVIDENCE_ADEQUACY_SMOKE: PASS
SAEE_MCP_STDIO_SMOKE: PASS
SAEE_CAPABILITY_MCP_ADAPTER_SMOKE: PASS
SAEE_QIANFAN_READINESS_MCP_SMOKE: PASS
SAEE_QODER_ADAPTER_SMOKE: PASS
SAEE_PUBLIC_CAPABILITY_SURFACE_SMOKE: PASS
SAEE_CAPABILITY_TRUTH_CONSISTENCY_SMOKE: PASS
```

The Evidence Adequacy smoke emitted the existing `jsonschema.RefResolver`
deprecation warning and still passed.

## Merge Gate

Before push or Draft PR:

1. identify a compatible upstream with a real common ancestor, or obtain an
   explicit owner decision for unrelated-history publication;
2. make the declared full-check sequence idempotent and worktree-clean, or
   formally define an isolated non-writing merge check;
3. decide whether `pytest` and `pre-commit` are required project tooling; if so,
   declare and configure them instead of installing them ad hoc;
4. rerun capability-specific checks, the selected full check and a final
   `git status --short` in a clean checkout;
5. only then push and create a Draft PR with the actual remote default branch.

## OTLP Decision

Read-only OTLP ingestion/normalization remains blocked as a next development
task. The current priority is repository lineage and merge-check integrity, not
another runtime entry. No OTLP work is authorized by this review.

## Final One-Line Judgment

SAEE's capability governance change is locally reviewable and its targeted
guards are strong, but it is not Draft-PR-ready until the correct upstream and
an idempotent clean full-check path are established.
