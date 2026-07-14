# SAEE Phase 0 Migration Policy

## Purpose

This policy converts architecture decisions into safe preconditions for future
migration. Phase 0 records; it does not move, merge, rename or delete.

## Required sequence

1. Resolve `capability-package/manifest.json#canonical_inventory`.
2. Run the capability progress and duplicate-build validator.
3. Identify the affected evolution subsystem.
4. Complete the Agent Recommendation Gate.
5. Define claims and non-claims.
6. Resolve the repository, asset, MCP and product registry entries.
7. Freeze source provenance, license, clean commit and backup evidence.
8. Specify adapter-first reuse and compatibility behavior.
9. Add a migration receipt and rollback criteria.
10. Only then propose behavior or directory changes.

## Migration states

- `KEEP`: preserve identity and route to the asset.
- `MIGRATE`: prepare an explicit, reversible migration; no movement is implied.
- `MERGE`: consolidate authority or contract only as stated in the decision;
  repository merging requires a separate authorization.
- `DEPRECATE`: retain compatibility until usage and replacement evidence pass.
- `UNKNOWN`: collect evidence; do not delete or reinterpret.

## Required migration evidence

- source and destination repository IDs, HEADs and remotes;
- dirty/ahead status and protected untracked files;
- license and provenance manifest;
- schema/API compatibility report;
- caller and usage evidence;
- test and Agent-readable projection agreement;
- external system and product impact;
- rollback command or restoration artifact;
- owner approval for consequential external actions.

## Phase 0 disposition

```text
code_migration=false
repository_merge=false
runtime_integration=false
mcp_change=false
product_change=false
external_action=false
production_ready=false
```
