# SAEE Canonical Remote Strategy

Date: 2026-07-14
Decision mode: recommendation only; no remote was created or modified

## Current Facts

- The local SAEE repository has no configured Git remote.
- Local branch: `feat/canonical-capability-inventory-routing-v1`.
- Local Phase 0 HEAD: `307cebd6c1a6072958264b35eb2c38edd7195eb2`.
- The public repository `joy7758/SAEE` exists, uses `main`, and exposes a small public-facing tree.
- Public `main` was observed at `e503c22109bdb7c83dc465d66e2a22760a3c8d90` (`Publish agent discovery endpoints`).
- Public release evidence includes `v0.1.1-external-canonical`.
- The local and public histories are unrelated: neither observed HEAD is an ancestor of the other, there is no merge base, and the observed divergence count is `33 5` (local-only/public-only commits).
- The local repository contains about 5,281 tracked files, while the observed public tree contains 59 files. Treating the public projection as a drop-in origin would erase provenance or force a high-risk unrelated-history reconciliation.

These observations establish that the current state remains:

```text
CANONICAL_SOURCE=LOCAL_ONLY
REMOTE_READY=false
```

## Options

Scores use `1` as weak/high-risk and `5` as strong/low-risk. For `migration risk`, a higher score means safer migration.

| Option | Source integrity | Public visibility | Migration risk | Commercial suitability | Total |
|---|---:|---:|---:|---:|---:|
| A. New canonical origin + controlled public mirror | 5 | 4 | 3 | 5 | 17 |
| B. Use `joy7758/SAEE` directly as origin | 1 | 5 | 1 | 3 | 10 |
| C. Private canonical repository without formal mirror | 4 | 1 | 4 | 3 | 12 |

### Option A: New Canonical Origin + Controlled Public Mirror

Create a dedicated access-controlled canonical remote from the local repository's actual history. Retain `joy7758/SAEE` as an explicitly generated or curated public projection, with a documented publication boundary and provenance link.

Benefits:

- Preserves the full local history and governance truth surfaces.
- Separates private/internal evidence from intentionally public agent-readable discovery assets.
- Supports recovery, collaboration, protected branches, and later release automation.
- Avoids pretending the 59-file public projection is the 5,281-file canonical source.

Risks:

- Requires an authorized remote owner and access policy.
- Requires deliberate one-way mirror/projection tooling and leak prevention.
- The initial import and backup rehearsal must be verified before claiming remote readiness.

### Option B: Use `joy7758/SAEE` As Origin

This maximizes immediate visibility but conflicts with the observed unrelated histories and radically different repository scopes. It would require a risky history graft, force-push-like replacement, or destructive restructuring. It is not recommended.

### Option C: Private Canonical Repository Only

This provides reasonable integrity and migration safety, but it leaves agent discovery and public commercial visibility without a governed synchronization path. It is acceptable as a temporary containment posture, not as the preferred long-term topology.

## Recommendation

Recommend **Option A: a new canonical origin plus `joy7758/SAEE` as a controlled public mirror/projection**.

Proposed future topology:

```text
access-controlled canonical origin
        |
        | reviewed one-way publication contract
        v
joy7758/SAEE public projection
```

The public repository must be labeled as a public projection unless and until it is rebuilt from the canonical history by a verified publication process. The words `canonical` in an old release tag do not override current repository provenance.

## Authorization And Readiness Gate

This audit does not create remotes, push, rewrite history, or alter the public repository. `REMOTE_READY` may become `true` only after explicit authorization and all of the following evidence exists:

1. canonical remote owner, URL, access model, and retention policy are approved;
2. local history is imported without rewriting the current source lineage;
3. a second clone/fetch verifies recoverability and commit identity;
4. branch protection and credential boundaries are verified;
5. the public projection contract identifies allowlisted files and excluded private evidence;
6. a dry-run publication diff is reviewed before any public push.

Until then:

```text
REMOTE_STRATEGY=OPTION_A_RECOMMENDED_NOT_EXECUTED
REMOTE_READY=false
PHASE1_REMOTE_BLOCKER=true
```
