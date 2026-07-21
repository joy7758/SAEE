# ADR-0004: Configured Public Remote Boundary

## Status

Accepted for current governance truth reconciliation on 2026-07-22.

## Context

The active engineering worktree is now located at `/Users/zhangbin/GitHub/SAEE`
and has a configured `origin`:

```text
configured_git_remote=https://github.com/joy7758/SAEE.git
configured_remote_role=PUBLIC_PROJECTION_AND_REVIEW_SURFACE
```

The configured remote proves that a Git transport and public collaboration
surface exist. It does not prove that the remote is the canonical recovery
authority. The local full-history branch and the public repository retain
different lineages and scopes.

## Decision

```text
canonical_engineering_source=/Users/zhangbin/GitHub/SAEE
canonical_source_scope=LOCAL_ENGINEERING_AUTHORITY
configured_git_remote=https://github.com/joy7758/SAEE.git
configured_remote_role=PUBLIC_PROJECTION_AND_REVIEW_SURFACE
canonical_git_remote=NOT_ESTABLISHED
remote_ready=false
public_repository_inheritance=PROHIBITED_WITHOUT_VERIFIED_LINEAGE
```

`origin` may be used for explicitly authorized public branches, tags and
review workflows. Its presence does not authorize pushing the current full
engineering branch, merging unrelated histories, force-pushing, publishing
private evidence or treating the public tree as a complete recovery copy.

## Agent-readable distinction

- `configured_git_remote` answers whether this worktree has a reachable Git
  remote.
- `canonical_git_remote` answers whether a verified recovery and authority
  remote exists for the full engineering lineage.
- `remote_ready` requires verified import, clone/fetch recovery, branch and
  credential protections, and a governed public-projection contract.

## Claims and non-claims

Claims:

- `origin` is configured at `https://github.com/joy7758/SAEE.git`;
- the configured remote is a public projection and review surface;
- the local GitHub worktree remains the current engineering authority.

Non-claims:

- the public remote is not declared the canonical recovery origin;
- the complete local history is not claimed to be recoverable from `origin`;
- no push, merge, force-push or publication is authorized by this decision;
- capability, runtime, customer-validation and production truth are unchanged.
