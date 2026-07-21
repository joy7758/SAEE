# SAEE Authority Pointer Map

```text
map_id=SAEE_AUTHORITY_POINTER_MAP_V1_TO_V2_X
current_authority=SAEE_Development_Constitution_v1.1
future_candidate=SAEE_Development_and_Ecosystem_Constitution_v2.x
map_status=PREPARATION_ONLY
NO_SWITCH_EXECUTED=true
```

该表描述未来迁移可能触及的 authority surfaces。`Future migration requirement` 是候选
patch design，不是当前授权；本阶段对每一项的实际动作均为 `NONE`。

## Canonical successor family candidates

| Role | Current v1.1 | Future candidate | Current action |
|---|---|---|---|
| Human-readable authority | `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | `docs/architecture/SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_0.md` | `NONE` |
| Machine contract | `agent-interface/governance/saee-development-constitution.v1.1.json` | `agent-interface/governance/saee-development-and-ecosystem-constitution.v2.0.json` | `NONE` |
| Closed schema | `schemas/saee-development-constitution.schema.v1.1.json` | `schemas/saee-development-and-ecosystem-constitution.schema.v2.0.json` | `NONE` |
| Recommendation gate | `docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md` | versioned v2 recommendation gate | `NONE` |
| Deterministic validator | `scripts/saee_development_constitution_smoke.py` | versioned v2 validator | `NONE` |
| Cross-surface checker | not present | versioned authority consistency checker | `NONE` |

候选文件名只是准备约定；未来执行前必须冻结具体版本。浮动 `v2.x` 不能成为机器契约版本。

## Pointer inventory

| Surface | Current role | Future migration requirement | Activation rule | Current action |
|---|---|---|---|---|
| `AGENTS.md` | 声明 v1.1、machine contract、gate、validator 与主线 | 原子更新为具体 v2 family，并保留 mainline、duplicate-build、staged-truth 规则 | activation batch | `NONE` |
| `.codex/rules.md` | Codex 的 v1.1 启动与边界规则 | 与 `AGENTS.md` 同批切换，不允许混指 | activation batch | `NONE` |
| `.codex/current_state.md` | 当前 authority/state 快照 | 同批记录具体 v2 active 状态和 effective commit | activation batch | `NONE` |
| `llms.txt` | Agent discovery 顶部权威入口 | 只更新 authority pointer/启动规则，不复制 live capability status | activation batch | `NONE` |
| `README.md` | 人类入口与 staged-truth 表面 | 只更新权威入口和分层身份；产品/生态事实仍按证据窄写 | activation + later semantic batch | `NONE` |
| `governance/README.md` | 治理读取顺序与真源边界 | 更新 read order 和 successor pointer；不提升 Project Memory 权威 | activation batch | `NONE` |
| `agent-index.json#development_constitution_v1_1` | v1.1 机器入口 | additive v2 entry + active authority pointer；capability ledger projection 不变 | activation batch | `NONE` |
| `scripts/mainline_guard.py` | 强制运行 v1.1 Constitution smoke | 在保留 v1.1 historical check 的同时路由 active v2 与 consistency check | activation batch | `NONE` |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | 当前产品架构 | 未来新增/迁移到 v2 product architecture，保持 exactly three targets | semantic batch | `NONE` |
| `governance/registry/product-registry.json` | 当前产品事实 | 只做已批准关系字段对齐，不升级实现/发布状态 | semantic batch | `NONE` |
| `governance/project-memory/` | decision routing 与历史 | 通过明确授权的 DCP/decision log 同步 approved/frozen 状态 | semantic/decision batch | `NONE` |
| `capability-package/manifest.json#canonical_inventory` | 唯一 capability fact source | authority-only batch 预期 digest `NO_CHANGE` | never switched by authority migration | `NONE` |
| `governance/registry/mcp-registry.json` 与 MCP scripts | interface/runtime scoped facts | Phase 0.5.4 与 authority batch 均 `NO_CHANGE`；后续另行授权语义或生态验证 | later separate batch | `NONE` |

## Atomic-switch requirement

未来 active pointer switch 必须在一个边界清晰的 activation batch 内同时处理：

```text
AGENTS.md
.codex/rules.md
.codex/current_state.md
llms.txt
README.md authority entry
governance/README.md
agent-index.json authority entry
scripts/mainline_guard.py
```

切换前必须双轨验证；切换后不得出现 mixed v1.1/v2 active pointers。v1.1 Constitution、
machine contract、schema、gate 和 validator 必须保留为 historical/rollback family。

## Rollback pointer

未来 rollback 通过授权的 revert/correction commit 把上述 active pointers 一致恢复到
v1.1，不删除 v2 artifacts、不重写历史、不执行 destructive reset，并记录 failed check、
effective commit 与 rollback commit。

```text
AUTHORITY_POINTERS_CHANGED=false
V1_1_HISTORY_PRESERVED=true
CANONICAL_CAPABILITY_INVENTORY_CHANGE=NONE
NO_SWITCH_EXECUTED=true
```
