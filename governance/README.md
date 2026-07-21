# SAEE Phase 0 Governance Foundation

`governance/` is the Agent-readable architecture governance entry for SAEE.
It records ownership, canonical-source boundaries, cross-system relationships
and migration decisions without moving repositories or changing runtime
behavior.

## Read order for every Agent

1. `project-memory/`
2. `../docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
3. `constitution/constitution-alignment.md`
4. `registry/asset-registry.json`
5. `registry/repository-registry.json`
6. `../capability-package/manifest.json#canonical_inventory`
7. `registry/capability-crosswalk.json`
8. `registry/mcp-registry.json`
9. `registry/product-registry.json`
10. `migration/forbidden-actions.md`
11. `codex/codex-governance-rules.md`

For the active SAEE and Agent Evidence integration mainline, resolve the
tracked-source freeze and reuse-first crosswalk before any source movement:

```text
agent_evidence_source_freeze=migration/agent-evidence-source-provenance.v1.json
agent_evidence_migration_crosswalk=migration/agent-evidence-migration-crosswalk.v1.json
agent_evidence_schema_compatibility=migration/agent-evidence-schema-compatibility.v1.json
three_version_integration_plan=migration/saee-three-version-integration-plan.v1.json
m03_owner_decision=migration/agent-evidence-m03-owner-decision.v1.json
agent_evidence_merge_validator=../scripts/saee_agent_evidence_merge_readiness_check.py
```

These files authorize analysis only. They do not authorize source copying,
runtime integration, MCP changes, marketplace transfer, staging or commit.

`project-memory/` records decision status and routes Agents away from repeated
discussion. Reading it first is an orientation step, not an authority
override. It is not a capability, marketplace, runtime or external-system fact
database. The Constitution, registry-specific authorities and canonical
capability inventory retain their defined precedence.

The crosswalk and registries in this directory do not replace the canonical
capability inventory. Current capability status, lifecycle and routing facts
come only from:

```text
capability-package/manifest.json#canonical_inventory
```

## PHASE0_BASELINE

```yaml
captured_at: 2026-07-14T00:00:00+08:00
repository: /Users/zhangbin/Documents/SAEE
branch: feat/canonical-capability-inventory-routing-v1
git_head: 85677aaadfaee3a7d7bc4197da21e1c9328c70d7
git_remote: NOT_ESTABLISHED
worktree_clean: false
dirty_entry_count_before_phase0: 21
baseline_action: recorded_only
reset_restore_or_cleanup_performed: false
```

The pre-existing dirty worktree is protected input. Phase 0 does not claim
that those changes belong to this governance implementation, and it does not
clean, reset, restore or stage them automatically.

## Current configured remote truth

The Phase 0 block above is a dated historical baseline. Current verified
remote truth is:

```text
observed_at=2026-07-22
canonical_engineering_source=/Users/zhangbin/GitHub/SAEE
configured_git_remote=https://github.com/joy7758/SAEE.git
configured_remote_role=PUBLIC_PROJECTION_AND_REVIEW_SURFACE
canonical_git_remote=NOT_ESTABLISHED
remote_ready=false
decision=decisions/ADR-0004-configured-public-remote-boundary.md
```

A configured remote is not the same as a verified canonical recovery remote.
The public and full local engineering histories remain separate until an
explicit lineage and recoverability gate proves otherwise.

## Directory map

```text
governance/
├── project-memory/  long-term decision state, open questions and rejected routes
├── constitution/   constitutional alignment and recommendation gate
├── registry/       asset, repository, capability crosswalk, MCP, product and external-system records
├── decisions/      migration decision records
├── migration/      policy, protected assets and forbidden actions
├── codex/          mandatory change rules and template
└── schemas/        strict registry schemas
```

## Validation

```bash
python3 scripts/saee_governance_registry_check.py
python3 -m unittest tests/test_governance_registry.py
python3 scripts/saee_project_memory_check.py
python3 -m unittest tests/test_project_memory.py
python3 scripts/saee_agent_evidence_merge_readiness_check.py
python3 -m unittest tests/test_agent_evidence_merge_readiness.py
```

Validation is local, offline and read-only. A PASS means that the checked-in
governance records are internally consistent. It is not a production,
customer, marketplace, security, compliance or external-integration result.

## Phase boundary

```text
PHASE0_STATUS=governance_foundation_only
ARCHITECTURE_REWRITE=NOT_STARTED
REPOSITORY_MERGE=NOT_STARTED
RUNTIME_CHANGE=NONE
MCP_CHANGE=NONE
PRODUCT_CHANGE=NONE
PRODUCTION_READY=false
```
