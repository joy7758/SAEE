# SAEE V1.1 / V2 Successor Shadow Validation Plan

```text
plan_id=SAEE_V1_1_V2_SUCCESSOR_SHADOW_VALIDATION_PLAN
phase_target=Phase_0.5.5
plan_status=DESIGN_ONLY
current_active_authority=SAEE_Development_Constitution_v1.1
v2_shadow_authority=false
v2_active=false
pointer_switch_allowed=false
phase_0_5_5_execution_authorized=false
```

## 1. Objective

在不切换 active authority、不修改能力事实、不修改代码/MCP/产品状态的情况下，证明：

1. v1.1 authority family 继续独立通过现有验证；
2. 候选 v2 successor family 在 shadow mode 中内部一致；
3. 两者可共同保留，且 planned pointer switch 不产生 split-brain；
4. v2 不破坏 mainline、历史、capability truth、产品边界和 staged truth。

Shadow validation 是只读兼容性验证，不是 authority activation，也不赋予 successor
任何规范权力。

## 2. Preconditions

- 获得 Phase 0.5.5 的单独人工执行授权；
- 在干净、隔离、可复现的 worktree 中冻结 HEAD、status、authority pointers 与 file hashes；
- v2 使用具体版本，不使用浮动 `v2.x` machine identifier；
- successor Constitution、machine contract、closed schema、recommendation gate 与 validator
  形成完整但 inactive 的 additive family；
- approved decisions 与 Project Memory/decision log 的状态差异已通过授权流程处理；
- canonical inventory digest、product target list、MCP registry 与 mainline baseline 已记录；
- exact file allowlist、rollback owner 和验收人已确认。

当前 Phase 0.5.4 未创建上述 v2 machine family 或 validator，因此本文件只设计验证，不执行
Phase 0.5.5。

## 3. Dual-track execution model

| Track | Input | Validator | Expected result | Authority effect |
|---|---|---|---|---|
| A: v1.1 baseline | current v1.1 Constitution, contract, schema, gate, pointers | existing `scripts/saee_development_constitution_smoke.py` + governance checks | `PASS` | v1.1 remains active |
| B: v2 successor shadow | inactive concrete v2 family | future versioned v2 validator | `PASS` | none |
| C: coexistence | both families + expected pointer map | future authority consistency checker using a read-only model | `PASS` | none |
| D: negative cases | mutated in-memory/temp fixtures only | v2 + consistency validators | deterministic rejection | none |

Pointer simulation must use in-memory data or disposable temporary copies outside repository-tracked
surfaces. It may not edit `AGENTS.md`, `.codex/`, `llms.txt`, `README.md`,
`agent-index.json` or `mainline_guard.py`.

## 4. Validation matrix

| Check family | Required assertions | Failure condition |
|---|---|---|
| Identity consistency | Theory, Engineering, Product, Ecosystem 层级完整；readiness 不覆盖 evolution core | 单层身份、audit-first/evaluation-first 重构 |
| Capability consistency | canonical inventory 是唯一能力真源；shadow 前后 digest 相同；missing/partial 不升级 | 文档/宪法推导 implementation status |
| Product consistency | exactly three targets；Autonomous future only；registry 不虚构实现/发布 | 出现第四目标产品或状态升级 |
| Term consistency | 新权威正文不使用未限定历史缩写；历史全名/namespace 保留；SECO design-only | 历史被删除、SECO 被写成 implemented/runtime |
| Non-Claims consistency | authority、runtime、identity、evidence、external integration、product truth 的 non-claims 齐全 | 草案遗漏关键否定边界 |
| Ecosystem claims consistency | Capability 核心；MCP/OpenAPI 接口；cloud 可选渠道；各 staged state 分离 | local/template/review 被升级为 official/listed/adopted |
| Mainline consistency | 受控 SAEE/Agent Evidence integration 仍是 mainline；secondary 不 self-approve | governance/ecosystem secondary 取代主线 |
| History and rollback | v1.1 family 保留；supersedes/effective commit 可追溯；rollback model 完整 | 删除历史、依赖 destructive reset |
| Pointer consistency | 模拟 active pointers 全部指向同一具体 family；historical pointers 明确标记 | mixed v1.1/v2 active pointers |

## 5. Required negative cases

未来 shadow fixtures 至少必须证明 validator 会拒绝：

1. 把 `Agent Readiness Infrastructure` 写成唯一理论与工程身份；
2. 把 Evidence/Audit secondary lane 提升为 program mainline；
3. 在新 authority 正文中使用未限定历史缩写作为新对象；
4. 把 `SAEE Execution Context Object (SECO)` 写成 runtime、implemented capability 或 MCP Tool；
5. 把 `SAEE Autonomous` 写成第四目标客户版本；
6. 把 MCP/local smoke 写成 official integration；
7. 把 marketplace review 写成 listing/adoption/customer validation；
8. authority-only shadow run 改变 canonical inventory digest；
9. 任一 active pointer 仍指 v1.1、其余指 v2，或反向混指；
10. 删除 v1.1 historical family 或使用 history rewrite 作为 rollback。

## 6. Evidence package

每次授权的 shadow run 应输出一个只读结果包，至少含：

- git HEAD、branch、worktree cleanliness、file allowlist 与 timestamp；
- v1.1/v2 family 文件 hash 和 validator version；
- canonical inventory before/after digest（必须相同）；
- product target list 与 MCP canonical-surface comparison；
- 每个 validation family 的 PASS/FAIL、reason code 与 evidence path；
- negative-case deterministic results；
- expected pointer simulation matrix；
- rollback dry-run result；
- claims、non-claims 与 unresolved blockers；
- 明确的 `AUTHORITY_SWITCH_AUTHORIZED=false`，直到后续人工 gate 单独改变。

## 7. Exit gate

```text
V1_1_VALIDATION=PASS
V2_SUCCESSOR_SHADOW_VALIDATION=PASS
COEXISTENCE_VALIDATION=PASS
NEGATIVE_CASES=PASS
CANONICAL_INVENTORY_DIGEST=NO_CHANGE
V1_1_HISTORY=PRESERVED
ROLLBACK_DRY_RUN=PASS
HUMAN_SHADOW_REVIEW=APPROVED
```

通过这些条件只说明具备安全迁移条件，不自动执行 pointer switch。authority activation 仍需
独立、明确、file-scoped 的人工授权。

## 8. Current phase non-claims

```text
SHADOW_VALIDATION_EXECUTED=false
V2_VALIDATOR_IMPLEMENTED=false
AUTHORITY_CONSISTENCY_CHECK_IMPLEMENTED=false
ROLLBACK_REHEARSED=false
AUTHORITY_SWITCH_EXECUTED=false
```
