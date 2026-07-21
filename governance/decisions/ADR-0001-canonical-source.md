# ADR-0001: Canonical Source Boundary

## Status

Accepted for the Phase 0 baseline. Current configured-remote truth is clarified
by `ADR-0004-configured-public-remote-boundary.md` without changing this
historical decision.

## Context

The local SAEE worktree contains the current engineering source and governance
changes, but it has no Git remote. A smaller public `joy7758/SAEE` repository
exists as a public surface, and several adjacent repositories have independent
origins and releases. Automatically treating a public repository as the local
source authority would risk history loss and unsupported synchronization.

## Decision

```text
canonical_engineering_source=/Users/zhangbin/Documents/SAEE
canonical_source_scope=LOCAL_ONLY
canonical_git_remote=NOT_ESTABLISHED
canonical_capability_source=capability-package/manifest.json#canonical_inventory
public_repository_inheritance=PROHIBITED_WITHOUT_EXPLICIT_DECISION
```

The local SAEE repository is canonical for current local engineering and
governance. The capability manifest remains the sole source for capability
facts. Public repositories, site remotes and adjacent projects are reference,
external or unknown until an explicit lineage decision records their role.

## Consequences

- Agents may read public repositories for reference, but may not push, merge,
  mirror or infer authority from naming alone.
- A future remote decision must preserve the current branch, dirty changes,
  tags, releases and public abstraction history.
- `repository-registry.json` records the baseline but is not a live Git sync
  service.

The later presence of a configured public `origin` does not retroactively
change this Phase 0 observation or establish a canonical recovery remote.

## Non-goals

- selecting or creating a remote;
- pushing current changes;
- rewriting Git history;
- declaring the public repository obsolete;
- changing capability facts.
