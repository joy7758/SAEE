# SAEE Phase 0 Governance Foundation

`governance/` is the Agent-readable architecture governance entry for SAEE.
It records ownership, canonical-source boundaries, cross-system relationships
and migration decisions without moving repositories or changing runtime
behavior.

## Read order for every Agent

1. `../docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
2. `constitution/constitution-alignment.md`
3. `registry/asset-registry.json`
4. `registry/repository-registry.json`
5. `../capability-package/manifest.json#canonical_inventory`
6. `registry/capability-crosswalk.json`
7. `registry/mcp-registry.json`
8. `registry/product-registry.json`
9. `migration/forbidden-actions.md`
10. `codex/codex-governance-rules.md`

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

## Directory map

```text
governance/
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
