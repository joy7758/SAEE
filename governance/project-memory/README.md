# SAEE Project Memory

`governance/project-memory/` is the Agent-readable long-term decision memory
for SAEE. It helps future AI Agents distinguish frozen decisions, open
questions, rejected routes and historical decisions before proposing work.

本目录是 SAEE 的智能体可读长期决策记忆层，用于让未来 AI Agent 在提出工作前先
区分已冻结决策、开放问题、已拒绝路线和历史决策，减少跨对话重复讨论。

## Read order

Use this orientation order at the beginning of governance work:

1. `governance/project-memory/`
2. `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
3. `governance/registry/`
4. `capability-package/manifest.json#canonical_inventory`

The first read is a routing step, not an authority override. If project memory
conflicts with the Constitution, a registry authority or the canonical
capability inventory, the authoritative source wins and the memory conflict
must be recorded for human review.

第一步读取项目记忆只是路由，不表示项目记忆高于开发宪法、治理注册表或规范能力
清单。发生冲突时，以对应权威真源为准，并把记忆冲突记录为待人工审查问题。

## Files

- `current-state.md`: current phase, blockers and prohibited phase transition.
- `frozen-decisions.md`: decisions that must not be reopened without a change proposal.
- `active-questions.md`: unresolved questions only.
- `rejected-options.md`: rejected routes and their bounded reasons.
- `decision-log.md`: append-only human-readable decision chronology.
- `memory-policy.md`: use, precedence, amendment and truth-boundary rules.
- `v2-transition-decisions.md`: candidate v2 transition decisions awaiting human confirmation.
- `decision-change-proposals/`: human-confirmed proposals that amend Frozen Decisions.

## V2 Transition Decisions

`v2-transition-decisions.md` records candidate v2 identity, asset, terminology,
product-family and ecosystem-entry decisions at `PROPOSED_FREEZE` status.

These entries are routing material for human review. They are not Frozen
Decisions, do not amend the Constitution and do not override
`frozen-decisions.md`. A candidate may become authoritative only through the
separate human-confirmed Decision Change Proposal and constitutional amendment
workflow required by `memory-policy.md`.

## Authority boundary

Project Memory records decision status and routing context. It is not:

- a capability fact source;
- a live marketplace or external-system status database;
- a replacement for ADRs, registries, schemas or source evidence;
- an authorization surface;
- proof of implementation, external validation or production readiness.

Capability facts remain authoritative only in
`capability-package/manifest.json#canonical_inventory`. External state must be
re-read from its authorized evidence surface before it is treated as current.

## Validation

```bash
python3 scripts/saee_project_memory_check.py
python3 -m unittest tests/test_project_memory.py
```
