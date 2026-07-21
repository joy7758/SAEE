# SAEE Authority Migration Preparation Package

```text
package_id=SAEE_AUTHORITY_MIGRATION_PREPARATION_PACKAGE
phase=Phase_0.5.4
package_status=PREPARATION_ONLY
v2_decision_status=APPROVED
approval_basis=explicit_human_phase_0_5_4_instruction
current_effective_authority=SAEE_Development_Constitution_v1.1
successor_status=DRAFT_ONLY_NOT_ACTIVE
constitution_v2_active=false
authority_migration_started=false
authority_switch_executed=false
code_change_authorized=false
ecosystem_phase_authorized=false
```

本目录是 SAEE 从 v1.1 到 v2.x 的权威迁移准备包。它把已人工批准的五项 V2
设计决定组织成可审查的 successor draft、pointer map、term crosswalk、shadow
validation plan 和 migration checklist，但不改变任何现行权威或运行行为。

## Authority boundary

当前唯一有效的 repository development authority 仍是：

```text
docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
```

本目录中的文件均为 non-normative preparation artifacts（非规范性准备材料）。它们不是
Constitution、machine contract、schema、Frozen Decision、capability fact source、产品
状态或生态开发授权。

## Approved preparation inputs

| Decision | Approved direction | This package does not claim |
|---|---|---|
| `V2-F-001` | Theory / Engineering / Product / Ecosystem 分层身份 | v2 已生效 |
| `V2-F-002` | SAEE 是主体，GitHub 资产是能力层、迁移源、adapter 或 demo | 外部仓库已合并或迁移 |
| `V2-F-003` | 新 SAEE 权威文本禁止未限定的历史缩写；`SECO` 为候选新对象名 | `SECO` 已有 schema、代码或 capability |
| `V2-F-004` | 目标产品族固定为 Evidence / Evaluation / Governance | 三个版本均已实现、发布或客户验证 |
| `V2-F-005` | `SAEE Capability + MCP/OpenAPI + optional Cloud Channel` 组合模式 | 已完成官方生态集成或 marketplace listing |

批准来源是本阶段的明确人工指令。现有
`governance/project-memory/v2-transition-decisions.md` 仍保留此前的
`PROPOSED_FREEZE` 文本，因为本阶段未授权修改旧决策登记；该 cross-surface 差异必须在
后续独立授权的 truth-surface alignment gate 中处理，不能由本准备包静默改写。

## Read order

1. `../../docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md`
2. `../../reports/V2_AUTHORITY_AND_TERM_CROSSWALK_DECISION_PACKET.md`
3. `../../reports/SAEE_CONSTITUTION_AUTHORITY_MIGRATION_PLAN.md`
4. `../project-memory/v2-transition-decisions.md`
5. `../project-memory/frozen-decisions.md`
6. `../../capability-package/manifest.json#canonical_inventory`
7. `v2-authority-successor-draft.md`
8. `term-crosswalk.md`
9. `authority-pointer-map.md`
10. `shadow-validation-plan.md`
11. `migration-checklist.md`

## Directory map

| File | Purpose | Status |
|---|---|---|
| `v2-authority-successor-draft.md` | 非规范性的 v2.x 语义草案 | `DRAFT_ONLY` |
| `authority-pointer-map.md` | 当前 v1.1 pointer 与未来候选切换面 | `NO_SWITCH_EXECUTED` |
| `term-crosswalk.md` | 身份、对象、产品与生态术语交叉映射 | `DESIGN_DIRECTION_ONLY` |
| `shadow-validation-plan.md` | v1.1 / v2 successor 双轨验证设计 | `PLAN_ONLY` |
| `migration-checklist.md` | 准备、切换与切换后验收清单 | `FUTURE_GATES_NOT_AUTHORIZED` |

## Non-claims

- 不修改、替换或 supersede v1.1；
- 不创建 active v2 authority、machine contract、schema 或 validator；
- 不修改 `AGENTS.md`、`.codex/`、`llms.txt`、`README.md` 或 `agent-index.json` pointer；
- 不修改 canonical capability inventory、registry、MCP、代码或产品状态；
- 不授权 Phase 0.5.5 执行、authority switch、生态开发或任何外部动作；
- 不把 preparation、local validation 或 shadow design 升级为 implementation、adoption
  或 production readiness。

## Next gate

```text
NEXT_ACTION=SHADOW_VALIDATION_REVIEW
PHASE_0_5_5_EXECUTION_AUTHORIZED=false
NO_SWITCH_EXECUTED=true
```
