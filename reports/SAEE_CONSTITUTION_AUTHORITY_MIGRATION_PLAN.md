# SAEE Constitution Authority Migration Plan

```text
plan_id=SAEE_CONSTITUTION_AUTHORITY_MIGRATION_PLAN
phase=Phase_0.5.3
plan_mode=DESIGN_ONLY
current_effective_authority=SAEE_Development_Constitution_v1.1
candidate_target=SAEE_Development_and_Ecosystem_Constitution_v2.x
candidate_status=PROPOSED_ONLY
authority_changed=false
constitution_changed=false
code_changed=false
ecosystem_entry_authorized=false
```

本文回答一个条件性问题：如果未来人类批准 `V2-F-001` 至 `V2-F-005`，SAEE 如何从
v1.1 权威体系安全迁移到 v2.x，而不破坏历史、能力事实、Evidence lineage、产品边界
和生态 staged truth。

本文不是 Constitution、Constitution Amendment、Frozen Decision、Decision Change
Proposal、implementation authorization 或 phase transition。当前有效权威仍为
`SAEE Development Constitution v1.1`；受控 SAEE / Agent Evidence integration 仍是
项目主线。

## 第一部分：迁移目标

### 1. 目标状态

在明确人工批准和独立执行授权后，把 repository development authority 从：

```text
SAEE Development Constitution v1.1
```

迁移到 additive successor（增量后继）：

```text
SAEE Development & Ecosystem Constitution v2.x
```

`v2.x` 不覆盖或删除 v1.1，而是以新文件、新 machine contract、新 schema、新
recommendation gate 和新 validator 构成可验证后继。只有通过 shadow validation、
authority consistency 和原子 pointer switch 后，v2.x 才能成为 active authority。

### 2. 必须保持的连续性

#### 历史连续性

- 保留 v1.1 Constitution、machine contract、schema、gate 和 validator；
- 保留所有 historical commit、tag、release、decision log、ADR 和 source provenance；
- 禁止 history rewrite、force push、删除历史或用新文件冒充旧版本；
- v2.x 必须声明 `supersedes` 关系和生效 commit，不静默重写 v1.1。

#### 能力事实连续性

- `capability-package/manifest.json#canonical_inventory` 继续是唯一 capability fact source；
- authority migration 本身不得把 `missing`、`partial` 或 `design_only` 升级；
- `agent-index.json#capability_progress_ledger_v1` 继续是 projection，不成为第二真源；
- Phase 1 authority batch 前后必须比较 canonical inventory digest，预期 `NO_CHANGE`。

#### Git 记录连续性

- 在独立、干净、可复现的 migration branch/worktree 中准备执行；
- 每个 migration phase 使用边界清晰的 additive commit；
- pointer activation 必须是一个可审计的原子变更，不允许长期混合 v1/v2 指针；
- rollback 使用后继 revert/correction commit，不使用 destructive reset。

#### Evidence 连续性

- Agent Evidence source commit、license、schema crosswalk、adapter 和 receipt lineage 保留；
- 历史 ARO、Evidence Object、Evidence Receipt、digest 和 provenance 名称不得被批量改写；
- 新术语通过 versioned crosswalk 连接历史对象；
- authority migration 不声明 source/runtime migration、external integration、customer
  validation、product launch 或 production readiness。

### 3. 迁移非目标

本计划不以迁移为理由执行以下事项：

- 新建 Agent Runtime、Evidence stack、Capability Registry 或第二 canonical MCP；
- 合并/复制 POP、ARO、Agent Evidence、Token Governor、FDO/MVK 等外部仓库；
- 修改 capability implementation status；
- 新增第四客户版本；
- 声明 official integration、marketplace listing、adoption 或 production readiness；
- 取代受控 SAEE / Agent Evidence integration 主线。

## 第二部分：权威层级设计

### 1. 未来分层结构

```text
Safety / Law / Explicit Human Authorization
                    ↓
Repository Development Authority
SAEE Development & Ecosystem Constitution v2.x
                    ↓
Machine Projection + Schema + Deterministic Validator
                    ↓
Scoped Fact Authorities
Capability Inventory / Product Registry / Repository-MCP Registries
                    ↓
Product Architecture and Ecosystem Projections
                    ↓
Project Memory Decision Routing
```

身份语义在 v2.x 内建议冻结为：

```text
Theory Identity
Silicon-Amplified Evolutionary Ecology
          ↓
Engineering Core
Digital Biosphere Evolution Engine + SAEE Architecture
          ↓
Product Identity
Agent Readiness Infrastructure
          ↓
Ecosystem Capability
SAEE Readiness Evaluation Capability
```

### 2. 哪个文件拥有最高权威？

未来候选：

```text
docs/architecture/SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_X.md
```

只有在人类批准、v2 machine family 完整、shadow validation 通过且 canonical pointers
完成原子切换后，该文件才成为 repository development authority。文件名中的 `V2_X`
必须在执行计划中替换为一个具体版本，例如 `V2_0`；不允许把浮动 `v2.x` 作为实际
机器契约版本。

其 machine-readable projection 候选为：

```text
agent-interface/governance/saee-development-and-ecosystem-constitution.v2.0.json
```

machine contract 是权威文档的封闭投影，不是第二 Constitution。

### 3. 哪个文件负责产品？

产品身份、三个客户版本和 non-claims 由 subordinate product architecture 承担：

```text
docs/product/SAEE_PRODUCT_ARCHITECTURE_V2.md
governance/registry/product-registry.json
```

- Product Architecture 解释产品结构；
- Product Registry 记录当前产品事实；
- 两者均不得覆盖 Constitution 或 capability facts；
- `Autonomous` 仅为 `FUTURE_MATURITY_HORIZON`，不是第四 customer version。

### 4. 哪个文件负责能力？

```text
capability-package/manifest.json#canonical_inventory
```

Constitution 规定能力治理规则，但不直接拥有 implementation status。任何 capability
事实变化仍必须先更新 canonical inventory，再同步 `agent-index.json` projection，并
提供代码、schema、tests 和 Agent-readable evidence。

### 5. 哪个文件负责生态？

生态策略和 adapter/channel 状态由 subordinate ecosystem surfaces 负责，例如：

```text
docs/ecosystem/SAEE_ECOSYSTEM_ENTRY_V2.md
governance/registry/mcp-registry.json
governance/registry/external-system-registry.json
provider/marketplace receipts
```

Ecosystem document 负责组合路线，registry/receipt 负责 scoped facts。MCP、cloud
channel、partner application 和 marketplace 均不是 Constitution authority。

### 6. 权威冲突处理

| 冲突类型 | 优先规则 |
|---|---|
| v2 Constitution 与安全/法律/明确人工授权冲突 | 安全、法律、明确人工授权优先 |
| Constitution 与 capability status 冲突 | Constitution 约束规则；当前 capability fact 以 canonical inventory 为准，并报告漂移 |
| Constitution 与 product registry 冲突 | 停止产品声明；通过受控 amendment/registry correction 解决 |
| Product/Ecosystem 文档与 Constitution 冲突 | Constitution 优先 |
| Project Memory 与权威事实冲突 | 对应权威事实优先，Project Memory 记录 Active Question |
| 外部平台状态与本地摘要冲突 | 当前带时间戳的授权 evidence surface 优先，使用窄状态 |

## 第三部分：迁移阶段设计

### Migration Phase 0 — Preparation / 事实冻结

#### 目标

在不改变权威的前提下，冻结输入、人工决定、文件范围、baseline digest 和回滚点。

#### 前置条件

- `V2-F-001` 至 `V2-F-005` 获得逐项人工确认或明确修改；
- 需要改变现有 Frozen Decision 的部分完成 human-confirmed Decision Change Proposal；
- Phase 0.5 formal-history blockers 已在其独立流程中解决；
- 使用干净、隔离、可复现的 migration branch/worktree；
- 获得 Phase 0.5.4 的显式执行授权。

#### 输入

- v1.1 Constitution family；
- approved V2 decisions/DCP；
- canonical capability inventory digest；
- registry、Project Memory 和 current-state baseline；
- 全部 authority pointer inventory；
- rollback owner 与验收人。

#### 输出

- immutable migration baseline manifest；
- file-by-file patch plan；
- v1.1 pointer map 和 expected v2 pointer map；
- pre-migration validator results；
- exact rollback procedure；
- `MIGRATION_PHASE_1_AUTHORIZED` 人工 gate。

#### 禁止

- 代码、schema、registry、MCP、产品或网站变化；
- 更新 capability facts；
- 生成 active v2 pointer；
- 清理或重写现有历史；
- 把 plan approval 当作 execution approval。

#### Exit gate

```text
PHASE_0_EXIT=HUMAN_APPROVED_BASELINE_AND_EXACT_PATCH_SCOPE
```

### Migration Phase 1 — Authority Update / 权威族更新

#### 目标

以 additive successor 方式建立完整 v2 authority family，并在 shadow validation 通过后
原子切换 repository pointers。

#### Future authorized batch

1. 新增具体版本的 v2 Constitution；
2. 新增 v2 machine contract；
3. 新增 v2 closed schema；
4. 新增 v2 recommendation gate；
5. 新增 v2 deterministic validator；
6. 新增 Authority Consistency Check；
7. 在 pointer switch 前同时运行 v1.1 与 v2 shadow validators；
8. 人工确认 shadow result；
9. 同一 activation batch 更新 `AGENTS.md`、`llms.txt`、`agent-index.json`、
   `.codex/rules.md`、`.codex/current_state.md`、README authority pointer 和
   `mainline_guard.py`；
10. 记录 v2 effective commit 与 v1.1 historical/superseded relationship。

#### 不变量

- v1.1 文件、schema、contract、gate 和 validator 保留；
- canonical inventory digest 不变；
- program mainline、三 customer versions、external-action boundary 和 staged truth 不因
  authority switch 自动改变；
- `source_code_migrated=false`、`runtime_integrated=false` 等字段继续以当前证据为准。

#### 失败条件

- 任何 pointer 仍混指 v1.1/v2；
- v2 validator 不能拒绝 identity/ARO/product-family negative cases；
- canonical inventory 意外变化；
- v1.1 historical family 缺失；
- mainline 被生态或治理副线取代；
- dirty/unrelated changes 混入 activation batch。

#### Exit gate

```text
PHASE_1_EXIT=V2_AUTHORITY_ACTIVE_POINTERS_CONSISTENT_V1_1_HISTORY_PRESERVED
```

Phase 1 完成不表示 capability、product、MCP 或 ecosystem 已迁移。

### Migration Phase 2 — Semantic Alignment / 语义与注册表对齐

#### 目标

在 v2 authority 激活后，统一术语、对象 crosswalk、product projection 和 registry
relationship，不改变未经证据支持的 capability status。

#### Future authorized work

- 新增 versioned Identity / SECO / Evidence / Evaluation / Discovery crosswalk；
- 新 SAEE 权威和产品文本禁止裸 `ARO`；
- 历史 ARO 使用 namespace/完整名称并保留；
- 将 `Agent Readiness Infrastructure` 固定为 product identity；
- 更新 product/asset/repository/capability-crosswalk/MCP registries 的关系字段；
- 更新 README、product architecture、MCP docs 和 Agent usage guidance；
- 为所有 terminology changes 增加 negative lint/validator；
- 对 `V2-F-001` 至 `V2-F-005` 的最终状态写入 Project Memory/decision log。

#### Capability rule

```text
AUTHORITY_OR_TERM_CHANGE_DOES_NOT_IMPLY_CAPABILITY_FACT_CHANGE
```

`SECO` 在 schema/implementation/test 完成前保持 `DESIGN_ONLY`；不得因为名称出现而写成
implemented。Existing services、schemas、tests 和 adapters 必须先经过 duplicate-build
check。

#### Exit gate

```text
PHASE_2_EXIT=TERMS_CROSSWALK_REGISTRIES_AND_AGENT_SURFACES_CONSISTENT
```

### Migration Phase 3 — Ecosystem Enablement / 生态启用

#### 目标

在 authority 和 semantics 全部稳定后，通过一个 canonical capability path 进入生态，
不创建新 runtime、Evaluator 或 MCP 真源。

#### 顺序

```text
Capability Contract
        ↓
Canonical SAEE MCP
        ↓
One Framework Adapter Validation
        ↓
Optional Cloud Channel
```

#### Future authorized work

1. 冻结两项现有 read-only operation 的 canonical contract；
2. 验证 canonical MCP discovery/invocation/interpretation/non-authorization；
3. 选择一个 framework 进行真实、受限、合成数据 compatibility test；
4. 通过后才考虑一个 cloud channel；
5. 每个渠道分别记录 configuration、process test、official integration、marketplace
   review、listing、adoption 和 production 状态。

#### 禁止

- 在 Phase 3 前进行新的生态开发；
- 创建第二 canonical MCP；
- 用 template/local smoke 证明 official integration；
- 用 partner approval/marketplace review 证明 listing 或 customer validation；
- 将 MCP、framework 或 cloud channel 写成 SAEE 本体。

#### Exit gate

```text
PHASE_3_EXIT=ONE_BOUNDED_ECOSYSTEM_PATH_VALIDATED_WITH_STAGED_TRUTH
```

## 第四部分：文件迁移矩阵

下表描述未来获授权迁移的候选动作；本任务不执行任何动作。

| 文件/表面 | 当前角色 | 未来角色 | 动作 | 阶段 |
|---|---|---|---|---|
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | 当前 active authority | 历史权威与回滚基线 | KEEP | 1 |
| `docs/architecture/SAEE_DEVELOPMENT_AND_ECOSYSTEM_CONSTITUTION_V2_0.md` | 不存在 | 唯一 active repository development authority | ADD | 1 |
| `agent-interface/governance/saee-development-constitution.v1.1.json` | v1.1 machine contract | 历史可验证 machine contract | KEEP | 1 |
| `agent-interface/governance/saee-development-and-ecosystem-constitution.v2.0.json` | 不存在 | v2 machine projection | ADD | 1 |
| `schemas/saee-development-constitution.schema.v1.1.json` | v1.1 closed schema | 历史/rollback schema | KEEP | 1 |
| `schemas/saee-development-and-ecosystem-constitution.schema.v2.0.json` | 不存在 | v2 closed schema | ADD | 1 |
| v1.1 recommendation gate | current gate | historical gate evidence | KEEP | 1 |
| v2 recommendation gate | 不存在 | v2 migration/development gate | ADD | 1 |
| `scripts/saee_development_constitution_smoke.py` | v1.1 validator | historical validator | KEEP | 1 |
| v2 Constitution validator | 不存在 | v2 deterministic/negative validator | ADD | 1 |
| Authority Consistency Check | 不存在 | cross-surface pointer/identity/term/product checker | ADD | 1 |
| `AGENTS.md` | v1.1 startup authority | v2 startup authority and unchanged mainline boundaries | UPDATE | 1 activation |
| `.codex/rules.md` | v1.1 Codex rules | v2 Layer/Object/duplicate/non-claims/validation rules | UPDATE | 1 activation |
| `.codex/current_state.md` | current authority snapshot | v2 activation state with explicit non-claims | UPDATE | 1 activation |
| `llms.txt` top authority block | v1.1 discovery pointer | v2 discovery pointer | UPDATE | 1 activation |
| `README.md` authority paragraph | v1.1 product/authority entry | v2 layered identity and authority pointer | UPDATE | 1 activation / 2 semantics |
| `agent-index.json#development_constitution_v1_1` | v1.1 machine entry | preserved historical entry | KEEP | 1 |
| new v2 `agent-index.json` entry | 不存在 | active v2 machine entry | ADD | 1 activation |
| `agent-index.json#capability_progress_ledger_v1` | capability projection | unchanged projection | NO_CHANGE | 1 |
| `capability-package/manifest.json#canonical_inventory` | sole capability fact source | same sole capability fact source | NO_CHANGE | 0-2 |
| `governance/project-memory/` | decision routing | approved/rejected migration decision history | UPDATE only after human decision | 0/2 |
| `governance/project-memory/frozen-decisions.md` | current Frozen Decisions | amended only through approved DCP | NO_CHANGE until approved DCP | 0 |
| governance asset/repository crosswalks | scoped relationship facts | v2 terminology/relationship mapping | UPDATE if approved and evidence-backed | 2 |
| `governance/registry/product-registry.json` | current product facts | same fact authority with v2 product identity | UPDATE semantics only; status unchanged | 2 |
| `governance/registry/mcp-registry.json` | current canonical/compatibility MCP facts | same owner-scoped MCP facts | UPDATE terminology only if needed | 2 |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` | current product architecture | historical product design | KEEP | 2 |
| `docs/product/SAEE_PRODUCT_ARCHITECTURE_V2.md` | 不存在 | layered product identity and three-version design | ADD | 2 |
| MCP implementation scripts | local canonical/compatibility transports | same implementations | NO_CHANGE | 0-2 |
| MCP docs and capability usage guides | v1 terminology/projections | v2 terminology and crosswalk | UPDATE | 2 |
| website | marketing/discovery projection | later bounded v2 projection | NO_CHANGE until separately authorized | 3+ |
| external GitHub repositories/assets | independent sources/references | preserved independent sources/references | NO_CHANGE | all |
| `scripts/mainline_guard.py` | invokes current authority checks | invokes v2 + authority consistency checks | UPDATE | 1 activation |

`DEPRECATE` 仅适用于新 SAEE 权威语境中的裸 `ARO` 和被明确 supersede 的旧 pointer；
不得用于删除 v1.1 历史文件或外部 ARO assets。

## 第五部分：术语迁移计划

### ARO

#### 当前

`ARO` 至少指向 `aro-v0.8` evidence export、ARO-Audit、Audit Record Object-style record
和候选 Agent Runtime Object，存在检索、schema 和引用歧义。

#### 未来规则

```text
BARE_ARO_IN_NEW_SAEE_AUTHORITY=PROHIBITED
HISTORICAL_ARO_NAMES=PRESERVED
NEW_EXECUTION_CONTEXT_OBJECT=SAEE_Execution_Context_Object_SECO
SECO_STATUS=DESIGN_ONLY_UNTIL_SEPARATE_IMPLEMENTATION_EVIDENCE
```

#### 迁移动作

1. 生成 ARO occurrence inventory；
2. 分类为 historical name、external asset、citation/quote、canonical field、new design；
3. historical/external/citation 项保持完整名称或 explicit namespace；
4. 新 v2 authority、product architecture、schema 和 registry 字段禁止裸 ARO；
5. 通过 crosswalk 把 historical evidence artifacts 映射到 Evidence/SECO references；
6. 增加 negative lint：新 canonical surface 出现未 allowlist 的 bare ARO 即失败；
7. 禁止批量重命名 Git history、DOI、release、external repository 或 historical artifact。

### Agent Readiness Infrastructure

未来固定为：

```text
IDENTITY_LAYER=PRODUCT_IDENTITY
ENGINEERING_CORE_REPLACED=false
THEORY_IDENTITY_REPLACED=false
```

所有产品/生态表面必须说明：Readiness result 是 decision context，不是 authorization、
security certification、deployment approval 或 proof of real-world truth。

### Autonomous

```text
AUTONOMOUS=FUTURE_MATURITY_HORIZON
AUTONOMOUS_IS_FOURTH_CUSTOMER_VERSION=false
```

新 v2 schema 和 validator 必须拒绝把 Autonomous 加入 target customer versions。

## 第六部分：产品族迁移

未来产品族继续为：

```text
SAEE Evidence
      ↓
SAEE Evaluation
      ↓
SAEE Governance
```

迁移规则：

- target customer version count 固定为 `3`；
- Agent Evidence Receipt 继续是 `legacy_external_migration_source`，不是第四版本；
- `SAEE Governance` 的 target status 不等于 implemented product；
- authority update 不修改 product implementation/customer/release status；
- Autonomous 只写入 future horizon，不进入 product registry 的 customer-version 集合；
- 任何产品事实变化必须有 product registry、code/contract、validation 和外部证据同步。

## 第七部分：能力迁移

能力迁移首先是 ownership/crosswalk 迁移，不是代码搬运。

| 资产 | 迁移分类 | v2 映射 | 允许动作 | 禁止推导 |
|---|---|---|---|---|
| SAEE Core | KEEP | Engineering Core / canonical local source | 保留现有 engine 和九段演化闭环 | readiness product 取代引擎 |
| POP | REFERENCE，未来可能 ADAPTER | Identity Contract reference | versioned identity crosswalk | POP 等于 authenticated identity |
| `aro-v0.8` / execution-integrity-core | REFERENCE | Execution Integrity + historical Evidence export | namespaced crosswalk | SAEE runtime 已迁移 |
| ARO-Audit / Audit Record Object | REFERENCE；bare label DEPRECATE | Evidence review/reference | 保留完整名称与历史 | 作为新 SECO 或生产 audit plane |
| Agent Evidence Project | ADAPTER + migration source | SAEE Evidence and Immune Subsystem | reuse/adapt/migrate/deprecate slices | 整仓复制、runtime integrated |
| `agent-evidence` | REFERENCE | Evidence compatibility/reference | 保留 release/citation identity | 成为 canonical SAEE fact source |
| Token Governor | REFERENCE，必要时 ADAPTER | Constraint/Policy reference | bounded policy crosswalk | 生产 governance runtime 已纳入 |
| FDO/MVK | REFERENCE，必要时 ADAPTER | Execution Integrity reference | trait/interface mapping | 端到端 SAEE execution runtime |
| Capability Registry | KEEP | Governance + Discovery fact source | 保留 canonical inventory | 创建第二 capability truth source |
| MCP | KEEP transport；docs UPDATE | Interface/Discovery | 复用 canonical SAEE MCP | MCP 等于 SAEE 本体或 trust authority |

任何 ADAPTER 必须复用 canonical domain service，具有 versioned schema、negative tests、
provenance、license boundary 和 deletion/supersession rule。

## 第八部分：生态迁移

### 未来路径

```text
Capability Contract
        ↓
Canonical SAEE MCP
        ↓
Framework Adapter
        ↓
Cloud Channel
```

### 每层职责

- **Capability Contract**：定义 should use / should not use、input/output、reason codes、
  non-claims 和 staged truth；
- **MCP**：提供 discovery/invocation transport，不产生 identity trust 或 authorization；
- **Framework Adapter**：把 framework configuration 映射到 canonical MCP，不复制 evaluator；
- **Cloud Channel**：可选 distribution surface，不拥有 Constitution、capability facts 或
  product truth。

### 生态启用前置门

- v2 authority active 且 pointers 一致；
- Authority Consistency Check PASS；
- Phase 2 terminology/crosswalk PASS；
- canonical MCP 唯一性 PASS；
- current capability truth re-read；
- selected framework Agent Recommendation Gate 至少 `recommend` for bounded test；
- external action另有明确授权。

### Staged truth

必须分别记录：

```text
configuration_prepared
local_protocol_tested
framework_process_tested
external_interoperability_validated
official_integration
partner_application
provider_approval
marketplace_submitted
marketplace_review
marketplace_listed
external_adoption_validated
customer_validated
production_ready
```

云市场不是权威；MCP 不是 SAEE 本体；partner/provider 状态不修改 capability facts。

## 第九部分：验证门

迁移后必须按以下顺序通过，任何前门失败均停止后续 phase。

### Constitution Check

Future command：

```text
python3 scripts/saee_development_and_ecosystem_constitution_v2_smoke.py
```

检查：v2 document/contract/schema/gate、identity hierarchy、mainline、three product versions、
external action boundary、truth boundary、negative cases 和 deterministic canonical form。

### Governance Registry Check

```text
python3 scripts/saee_governance_registry_check.py
```

检查：asset/repository/product/MCP ownership、one canonical source、no status promotion、
Agent Evidence runtime boundary。

### Capability Ledger Check

```text
python3 scripts/saee_capability_progress_ledger_smoke.py
```

检查：canonical inventory 与 projection 一致、authority-only batch 不改变 capability
facts、无 duplicate implementation/active stale roadmap。

### Project Memory Check

```text
python3 scripts/saee_project_memory_check.py
```

检查：V2 decisions 的 human status、DCP linkage、active question closure、append-only
decision log 和 authority precedence。

### Agent Recommendation Gate

必须分别评估：

1. authority migration；
2. semantic alignment；
3. selected ecosystem path。

任何 `conditional` / `do_not_recommend` 的 blocker 必须 fixed 或明确保持 internal-only，
不能由 validator PASS 覆盖。

### Authority Consistency Check

Future candidate：

```text
python3 scripts/saee_authority_consistency_check.py
```

必须检查：

- `AGENTS.md`、`llms.txt`、README、`.codex/*`、`agent-index.json`、mainline guard 指向
  同一个 active Constitution family；
- theory/engineering/product/ecosystem identity 不互相替代；
- 新 canonical surfaces 无未 allowlist 的裸 ARO；
- target customer versions 精确为三个；
- Autonomous 不在 customer-version 集合；
- canonical inventory digest 在 authority-only batch 前后相同；
- canonical SAEE MCP 恰好一个；
- v1.1 historical family 完整可读；
- v2 active effective commit 与 machine contract 匹配；
- no source/runtime/customer/production status promotion。

Negative cases 至少包含：

1. mixed v1.1/v2 active pointers；
2. Agent Readiness 覆盖 engineering core；
3. 新权威文本使用裸 ARO；
4. Autonomous 成为第四版本；
5. authority migration 修改 capability inventory；
6. 第二 canonical MCP；
7. v1.1 history/schema/validator 缺失；
8. governance/audit secondary displaces program mainline。

### Activation acceptance

```text
ALL_REQUIRED_CHECKS=PASS
HUMAN_REVIEW=APPROVED
UNRELATED_DIRTY_CHANGE_COUNT=0
ROLLBACK_DRY_RUN=PASS
```

Validator PASS 不能自我批准 activation；最终 authority switch 必须由独立人工 gate 授权。

## 第十部分：回滚设计

### 1. 回滚原则

- additive migration；
- no deletion；
- no history rewrite；
- narrowest failed phase rollback；
- use revert/correction commit；
- capability facts 和 Evidence lineage 默认保持不动。

### 2. Phase 1 authority rollback

如果 v2 activation 后出现 pointer、identity、validator 或 mainline failure：

1. 冻结后续 Phase 2/3；
2. 创建明确授权的 rollback commit；
3. 把 `AGENTS.md`、`llms.txt`、README、`.codex/*`、`agent-index.json` 和 mainline guard
   active pointer 恢复到 v1.1；
4. 保留 v2 files，标记为 inactive/rejected/superseded candidate，不删除；
5. 重跑 v1.1 Constitution、governance、capability ledger、Project Memory 和 authority
   consistency checks；
6. 在 append-only decision log 记录 failure 和 rollback commit；
7. canonical inventory digest 必须仍等于 baseline。

### 3. Phase 2 semantic rollback

如果 term/crosswalk/registry alignment 失败：

- revert Phase 2 semantic batch；
- 保留 v2 authority（仅当 Phase 1 本身仍一致）；
- 恢复上一版 product/MCP docs 和 registry relations；
- 不修改历史 ARO assets；
- `SECO` 回到 `DESIGN_ONLY`/inactive proposal；
- 记录 Active Question 后重新设计 crosswalk。

### 4. Phase 3 ecosystem rollback

如果 framework/cloud integration 失败：

- 禁用/撤回对应 adapter/channel projection；
- 保留 canonical capability and MCP；
- 将 status 降回最窄已证实阶段；
- 不回滚 Constitution，除非发现根本 authority conflict；
- 不把失败掩盖为 `official_integration` 或 `marketplace_listed`。

### 5. 必须保留

```text
V1_1_CONSTITUTION=PRESERVED
HISTORICAL_COMMITS=PRESERVED
OLD_SCHEMAS=PRESERVED
OLD_VALIDATORS=PRESERVED
CANONICAL_CAPABILITY_FACTS=PRESERVED
EVIDENCE_PROVENANCE=PRESERVED
EXTERNAL_REPOSITORY_HISTORY=PRESERVED
```

禁止通过删除历史来“完成”迁移。

## 第十一部分：风险矩阵

| 风险 | 原因 | 影响 | 措施 |
|---|---|---|---|
| 身份漂移 | product identity 覆盖 theory/engineering identity | SAEE 被改写为 evaluation/audit-only 产品 | v2 closed schema + identity hierarchy negative cases |
| 主线漂移 | ecosystem/governance 副线取代受控 Agent Evidence integration | 迁移失去 provenance/reuse/staged-truth 边界 | Constitution mainline field + role-prompt drift check |
| 术语漂移 | 裸 ARO 多义、SECO 文档先于事实 | Agent 路由错误、schema/citation 混乱 | namespaced ARO inventory + bare-term lint + SECO design_only |
| 权威分裂 | AGENTS/llms/index/.codex 指向不同版本 | 不同 Agent 执行不同规则 | shadow validation + atomic pointer switch + consistency check |
| 能力重复 | authority/term change 被当成新增 capability | 第二 Evidence stack、Evaluator 或 registry | canonical inventory digest freeze + duplicate-build gate |
| 能力状态升级 | 文档迁移推导 implemented/production | staged truth 失真 | authority batch `NO_CHANGE` capability rule |
| 生态过度承诺 | adapter template/local smoke 被当成 integration | 错误合作、采用和兼容声明 | staged ecosystem state machine + negative claims |
| MCP 重复入口 | 为 v2 新建第二 canonical server | discovery 和 ownership 冲突 | mcp-registry uniqueness check + reuse current canonical MCP |
| 商业声明过度 | partner approval/review 被写成 listing/launch | 市场、客户和生产事实失真 | owner-scoped external receipts + narrow status reporting |
| 产品族漂移 | Autonomous 被加入第四版本 | 冻结决定被静默改变 | exact-three schema and negative case |
| 历史丢失 | 覆盖/删除 v1.1、schema、commit | 无法审计或回滚 | additive successor + no deletion/history rewrite |
| 回滚失效 | pointer change 与 semantic/code change混在一批 | 不能局部撤销 | phase-separated commits + rollback dry run |
| Dirty worktree 混入 | 当前长期 dirty/staged baseline 未隔离 | 无法证明变更 ownership | clean isolated worktree + exact file allowlist |
| Validator 自我批准 | PASS 被当成 authority approval | SAEE 自我授权 | independent human activation gate |
| 外部事实过期 | cloud/marketplace snapshot 漂移 | 错误生态迁移判断 | activation 时实时重读授权 evidence surface |

## 第十二部分：Agent Recommendation Gate

### 模拟问题

如果潜在客户、集成伙伴或未来维护 Agent 需要 SAEE 在不丢失 v1.1 历史、能力事实和
Evidence lineage 的情况下迁移到分层 v2.x authority，是否推荐本迁移计划？

### 当前判断

```text
recommendation=HUMAN_REVIEW_REQUIRED
```

### 推荐理由

- additive successor 避免覆盖 v1.1；
- capability inventory 在 authority-only phase 明确 `NO_CHANGE`；
- shadow validation、atomic pointer switch 和 authority consistency 可检测 split brain；
- term/product/ecosystem work被推迟到后续 phase；
- rollback 保留历史、schema、capability facts 和 Evidence provenance。

### 不能直接 CONTINUE 的理由

- `V2-F-001` 至 `V2-F-005` 仍为 `PROPOSED_FREEZE`；
- Constitution 变化属于人工权威决定；
- Phase 0.5 formal-history blockers 尚未由本计划解除；
- 当前主工作树不是干净 migration baseline；
- v2 document/contract/schema/gate/validator 尚不存在；
- 本计划未获得 Phase 0.5.4 execution authorization。

### 阻塞分解

| Blocker | Required resolution | Owner/gate | Status |
|---|---|---|---|
| V2 decisions unapproved | human confirm/reject/revise each V2-F item | architecture commander | OPEN |
| Frozen Decision impact | approved DCP where required | human + Project Memory policy | OPEN |
| history stabilization | close Phase 0.5 formal-history gate | separate authorized workflow | BLOCKED |
| no exact v2 version | select concrete v2.0 contract/version | human migration approval | OPEN |
| no isolated baseline | create authorized clean migration worktree | Phase 0 preparation | NOT_STARTED |
| no execution authority | explicit Phase 0.5.4 scope/file authorization | human | NOT_GRANTED |

本计划只能进入人工审查，不能自行批准 authority migration。

## 第十三部分：最终输出

```text
MIGRATION_PLAN_STATUS=COMPLETE
AUTHORITY_CHANGE=NOT_EXECUTED
CONSTITUTION_CHANGE=NOT_EXECUTED
CODE_CHANGE=NOT_EXECUTED
ECOSYSTEM_ENTRY=NOT_AUTHORIZED
NEXT_ACTION=HUMAN_APPROVAL_OF_MIGRATION_PLAN
```

附加 staged truth：

```text
V2_DECISIONS=PROPOSED_ONLY
V2_AUTHORITY=NOT_ACTIVE
PHASE_0_5_4_AUTHORIZED=false
CAPABILITY_MANIFEST_CHANGE=NONE
SCHEMA_CHANGE=NONE
MCP_CHANGE=NONE
PRODUCT_CHANGE=NONE
PHASE_CHANGE=NONE
GIT_ACTION=NONE
```

## 第十四部分：验证

本 Phase 0.5.3 只新增本报告。应运行：

```text
python3 scripts/saee_project_memory_check.py
python3 scripts/saee_governance_registry_check.py
git diff --check
```

验收边界：

- Project Memory 与 governance registry 仍通过现有检查；
- 本报告无 whitespace error；
- 除本报告外，本任务不产生其他增量；
- 不执行 `git add`、`git commit`、`git push` 或 PR；
- 不改变 Constitution、AGENTS、registry、manifest、schema、validator、MCP、code、
  product、website、GitHub asset 或 Phase status；
- 验证 PASS 不授权 Phase 0.5.4。
