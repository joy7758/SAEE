# SAEE Check Idempotency Fix Report

## 1. Preflight recommendation

Preflight result: `conditional`. Before this repair, an enterprise should not
use the repository check as a development or audit gate because it modified the
evidence scene and relied on ignored local Provider runtime evidence. See
`reports/CHECK_IDEMPOTENCY_PREFLIGHT.md`.

## 2. Root cause

The historical `make check` target directly ran a legacy validation graph whose
smoke scripts invoked generators in the caller's repository. The graph mixed
generation with validation and later required ignored `/output/` Provider run
files. The defect existed at `00d8d0467761fe044355aeb678f3cd12efc6c7cf`,
before the capability-governance work.

## 3. First mutating command

```text
make check
  -> scripts/mainline_guard.py
     -> scripts/saee_pricing_page_closure_review_packet_smoke.py
        -> scripts/saee_pricing_page_closure_review_packet.py
```

The first smoke alone changed seven tracked files by regenerating JSON and
agent-facing documentation.

## 4. 41 tracked files classification

- 37 files: dynamic `generated_at` values;
- 6 overlapping files: live host state in `detached_local_child_processes`
  and/or `local_trial_started_by_manager`;
- 1 overlapping file: JSON key-order and Unicode serialization drift in
  `agent-index.json`;
- all 41 were content modifications; there were no additions, deletions,
  renames, mode changes, or absolute-path insertions.

## 5. Makefile responsibility changes

| Target | Responsibility |
|---|---|
| `make check` | Complete read-only validation through a disposable local clone. |
| `make check-in-place` | Internal legacy validation graph used only inside isolation. |
| `make generate` | Explicit in-place refresh of mainline-derived tracked artifacts. |
| `make check-generated` | Isolated generation and canonical comparison. |
| `make check-provider-evidence` | Explicit strict Qianfan runtime-evidence validation. |

## 6. Generator isolation design

`scripts/saee_check_isolation.py` creates a local clone, overlays the caller's
tracked and non-ignored untracked development files, and runs validation there.
Ignored runtime output, secrets, caches, and `/output/` are not copied. Child
output replaces the random sandbox path with `<SAEE_CHECK_SANDBOX>`.

The caller is never cleaned after validation because it is never modified.
There is no `git restore`, `git checkout --`, or `git reset --hard` masking step.

`check-generated` snapshots tracked content before generation and compares it
afterward. JSON is compared canonically. Only the declared runtime metadata
fields `generated_at`, `detached_local_child_processes`, and
`local_trial_started_by_manager` are excluded. Any other difference fails and
is printed as `CHECK_GENERATED_DIFFERENCE=<path>`.

## 7. Qianfan evidence classification

The three `output/controlled-rehearsal/qianfan-*.run.json` files are
`External Provider Runtime Evidence`. They are ignored and untracked, are not
fixed repository fixtures, and are not copied into normal checks.

## 8. Normal check behavior

When the external evidence is absent, normal validation prints:

```text
external_provider_evidence_status=NOT_REQUIRED
external_provider_evidence_verified=false
```

The check continues to validate schemas, loaders, internal synthetic rehearsal
logic, documents, capability contracts, and all non-live assertions. It does
not claim the missing live evidence is verified.

## 9. Strict provider-evidence behavior

- absent: `NOT_AVAILABLE`, `EXTERNAL_EVIDENCE_NOT_AVAILABLE`, nonzero;
- partial: `PRESENT_UNVERIFIED`, nonzero;
- malformed or digest-invalid: `INVALID`, nonzero;
- fully supplied and valid: `VERIFIED`, zero.

An explicitly supplied existing Qianfan evidence root passed with 3/3 runs,
five Provider rounds, digest/schema/binding checks, zero external-world actions,
and zero credential leakage. This evidence is not copied or required by normal
validation.

## 10. Negative tests

- missing optional evidence: passed as `NOT_REQUIRED`;
- missing strict evidence: failed as `NOT_AVAILABLE`;
- three malformed evidence files: failed as `INVALID`;
- isolated command attempted to overwrite the pricing-page output: caller bytes remained unchanged;
- volatile-only JSON changes: normalized as non-canonical metadata;
- substantive JSON field change: detected;
- manual change of top-level `pricing_page_published` from `false` to `true`:
  `make check-generated` failed and named exactly
  `phase_b_product/commercial_readiness/billing_revenue_evidence/pricing_page_closure_review_packet.local.json`.

## 11. First clean-run result

Candidate-worktree `make check` run 1:

```text
exit=0
caller_status_unchanged=true
stderr_bytes=0
stdout_sha256=cd7c69fb8c2135d49dcdb9e6b80fe16f274be31b0f5782e4f96d81bffd45458d
```

Candidate-worktree direct `mainline_guard.py` run 1:

```text
exit=0
caller_status_unchanged=true
stderr_bytes=0
stdout_sha256=9ccc02893fdcc1bd4d00d0fa6b475927a1610aed969cf694df313217133fea9d
```

## 12. Second clean-run result

Candidate-worktree `make check` run 2 returned the same exit code and the same
stdout SHA-256 as run 1. Direct `mainline_guard.py` run 2 also returned the same
exit code and stdout SHA-256 as its first run.

## 13. Git status after every run

The development worktree contained only the intentional repair changes. Its
status snapshot was byte-identical before and after each of these operations:

1. `make check` run 1;
2. `make check` run 2;
3. `python3 scripts/mainline_guard.py` run 1;
4. `python3 scripts/mainline_guard.py` run 2;
5. positive `make check-generated`;
6. strict missing and explicitly supplied Provider evidence checks.

Final clean-clone acceptance used temporary candidate commit
`520f7d7f2eedb08b943d41fd7e6b17c02ac87ae0`. The clone started clean and
remained clean after every run:

| Run | Exit | tracked changes after | stdout SHA-256 | stderr bytes |
|---|---:|---:|---|---:|
| `make check` 1 | 0 | 0 | `cd7c69fb8c2135d49dcdb9e6b80fe16f274be31b0f5782e4f96d81bffd45458d` | 0 |
| `make check` 2 | 0 | 0 | `cd7c69fb8c2135d49dcdb9e6b80fe16f274be31b0f5782e4f96d81bffd45458d` | 0 |
| `mainline_guard.py` 1 | 0 | 0 | `9ccc02893fdcc1bd4d00d0fa6b475927a1610aed969cf694df313217133fea9d` | 0 |
| `mainline_guard.py` 2 | 0 | 0 | `9ccc02893fdcc1bd4d00d0fa6b475927a1610aed969cf694df313217133fea9d` | 0 |

## 14. Determinism result

- repeated `make check` output: byte-identical;
- repeated direct mainline output: byte-identical;
- `check-generated`: `raw_generated_changes=41`, `normalized_differences=0`;
- random sandbox paths do not leak into stable output;
- Python hash seed, timezone, and locale are fixed for isolated execution;
- substantive generated drift remains fail-closed.

## 15. Postflight recommendation

Postflight result: `recommend` for bounded repository code and capability-fact
validation only. See `reports/CHECK_IDEMPOTENCY_POSTFLIGHT.md`.

## 16. Remaining limitations

- canonical `origin` and public-projection remote roles remain unresolved;
- the legacy internal validation graph still generates inside its disposable
  clone; this repair isolates that behavior rather than rewriting 125 smokes;
- tracked reports retain historical `generated_at` and local runtime fields,
  but those fields are explicitly non-canonical during generated comparison;
- no legal tracked real-Provider fixture exists, so none was invented or
  committed; strict success was tested only with explicitly supplied existing
  runtime evidence;
- build idempotency does not establish Agent execution truth, production safety,
  compliance, customer validation, adoption, or production readiness.

## 17. Branch

```text
fix/check-idempotency-v1
```

Base:

```text
00d8d0467761fe044355aeb678f3cd12efc6c7cf
```

## 18. Commit SHA

Validated clean-candidate commit:

```text
520f7d7f2eedb08b943d41fd7e6b17c02ac87ae0
```

The authoritative branch commit is created with subject
`fix: make SAEE validation checks clean and idempotent` and is reported by
`git rev-parse HEAD` in the final handoff. It differs from the temporary
candidate only by incorporation of this final acceptance receipt. Embedding a
commit's own SHA inside a file contained by that same commit would change the
commit SHA.

## 19. Unexecuted items and reasons

- no remote configured: canonical remote is an owner decision;
- no push or PR: explicitly prohibited;
- no merge into capability-governance branch: repair must remain independent;
- no OTLP work or commercial capability development: outside scope;
- no `pytest`, `pre-commit`, or heavyweight dependency installed: undeclared;
- no tracked real-Provider fixture added: repository had no pre-approved legal
  sanitized fixture, and inventing one would falsify evidence provenance.

## Explicit answers

1. `make check` is read-only for the caller: **YES**.
2. Two consecutive runs are identical: **YES**, including exit and stdout hash.
3. `mainline_guard.py` still depends on ignored Provider files: **NO**.
4. Missing Qianfan evidence: normal check=`NOT_REQUIRED` and continues without a verification claim; strict check=`NOT_AVAILABLE` and fails.
5. This repair can be reviewed independently: **YES**.
6. The capability-governance branch can be re-reviewed after this repair is integrated into the selected canonical mainline: **YES**.
