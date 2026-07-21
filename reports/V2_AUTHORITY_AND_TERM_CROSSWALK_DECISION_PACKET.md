# SAEE V2 Authority and Term Crosswalk Decision Packet

```text
packet_id=V2_AUTHORITY_AND_TERM_CROSSWALK_DECISION_PACKET
phase=Phase_0.5.2C
packet_type=decision_support_only
current_authority=SAEE_Development_Constitution_v1.1
candidate_target=SAEE_Development_and_Ecosystem_Constitution_v2.0
approval_status=HUMAN_REVIEW_REQUIRED
zero_behavior_change=true
zero_authority_change=true
```

本文件是 `Decision Packet`（决策包），不是 Constitution、ADR、Decision Change
Proposal、Frozen Decision、capability fact source 或实施授权。它只把候选 v2.0 迁移前
必须由人类架构指挥确认的问题组织成一个 Agent-readable 决策面。

当前项目主线仍为：在 provenance、license、schema crosswalk、reuse、migration 和
staged-truth gates 下受控完成 SAEE 与 Agent Evidence Project 的合并。本文不得取代该
主线，不得批准自身建议。

## 第一部分：问题背景

### 1. 为什么需要该决策

当前仓库同时存在四类合法但层级不同的身份表达：

1. **理论身份**：`Silicon-Amplified Evolutionary Ecology`；
2. **工程身份/工程核心**：`Digital Biosphere Evolution Engine`；
3. **产品身份**：`Agent Readiness Infrastructure` / `SAEE Agent Readiness Capability`；
4. **生态身份**：可被 Agent 发现和组合的只读 readiness evaluation capability。

这些表达并不必然冲突，但候选 v2.0 把 `Agent Readiness Infrastructure` 写成 SAEE 的
唯一最高身份，会与现行 v1.1 的理论身份、工程核心和九段演化闭环发生权威冲突。
如果不先冻结层级，后续 Agent 可能把产品投影误写成工程本体、把生态入口误写成运行
平台，或把 Evidence/Evaluation 副线提升为唯一使命。

### 2. 当前可确认事实

- 现行仓库权威仍是 `SAEE Development Constitution v1.1`；候选 v2.0 尚未成为文件化
  权威。
- `Agent Readiness Infrastructure` 已是当前仓库中的外部产品/商业方向，不是完全新概念。
- `saee.evaluate_agent_run` 与 `saee.evaluate_evidence` 在 canonical inventory 中均为
  `implemented`、`active` 的本地能力。
- `external_identity_binding`、`delegation_binding` 与
  `trusted_trace_to_evidence_conversion` 仍为 `missing`。
- 当前目标客户版本固定为 `SAEE Evidence / SAEE Evaluation / SAEE Governance`。
- Agent Evidence 的宪法归属已确定，但 source/runtime migration 尚不能由本文件宣称完成。
- Phase 0.5 stabilization 与 Phase 1 authorization 仍是独立 gate；本文件不改变其状态。

### 3. Agent Recommendation Gate

```yaml
recommendation_gate:
  feature_or_direction: candidate v2 authority and term migration
  target_customer_need: one discoverable SAEE identity, unambiguous object vocabulary, and one composable readiness capability boundary
  initial_answer: conditional
  reasons_to_recommend:
    - readiness product identity already has two implemented local read-only operations
    - canonical inventory, Agent-readable discovery, MCP stdio, schemas and examples already exist
    - layered identity can preserve the evolution engine while clarifying ecosystem value
  reasons_not_to_recommend:
    - candidate v2 is not repository authority
    - bare ARO has incompatible existing meanings
    - external identity, delegation and trusted trace conversion remain missing
    - three customer versions are frozen while Autonomous is only a candidate maturity stage
  final_decision: recommend this decision packet for human review; do not recommend authority or implementation migration yet
```

## 第二部分：SAEE 身份层级决策

### 方案 A：SAEE = Agent Readiness Infrastructure

#### 优点

- 对 Agent 平台和外部开发者易于理解；
- 与当前两项公开只读操作和 capability discovery 表面一致；
- 可直接回答“何时调用 SAEE、为什么调用 SAEE”；
- 有利于形成清晰的生态入口和产品叙事。

#### 缺点

- 将产品身份升级为唯一理论/工程身份；
- 压缩或遮蔽 Global Sensing、World Model、Counterfactual Simulation、Genome
  Branching、Sandbox Development、Pareto Selection、Archive/Rollback 等演化闭环；
- 容易把 Evidence/Evaluation 子系统误写成 SAEE 全部；
- 不能解释现有 Digital Biosphere 资产为什么仍属于主线架构。

#### 风险

- `audit_first_reframe` 或 evaluation-first regression；
- 当前受控 SAEE / Agent Evidence 合并主线被生态产品叙事取代；
- Agent 将 `readiness` 误解为 authorization、runtime control 或 security certification。

#### 分析结论

```text
OPTION_A_RECOMMENDATION=DO_NOT_ADOPT_AS_SOLE_IDENTITY
```

`Agent Readiness Infrastructure` 可以保留为产品/生态身份，但不建议作为对理论身份和
工程核心的单层替换。

### 方案 B：SAEE = Digital Biosphere Evolution Engine

#### 优点

- 与现行 v1.1 和九段演化闭环一致；
- 保留 SAEE 的理论差异化与长期架构连续性；
- Evidence、Evaluation、Governance 可以自然归入 selection、archive、rollback 和
  immune subsystem；
- 降低把 SAEE 重构成 audit SDK 或 generic Agent framework 的风险。

#### 缺点

- 对外部 Agent 和开发者的直接价值表达较抽象；
- “何时调用”与“输入/输出是什么”不如 readiness capability 明确；
- 容易让生态入口被宏大架构叙事淹没；
- 不能单独解决产品、协议与外部组合边界。

#### 风险

- 继续出现“架构正确但入口不清晰”；
- GitHub 项目可能再次被读成平行层级或项目集合；
- 生态开发可能继续分散为多个 adapter、demo 和 capability label。

#### 分析结论

```text
OPTION_B_RECOMMENDATION=KEEP_AS_ENGINEERING_CORE_NOT_SOLE_EXTERNAL_PRODUCT_IDENTITY
```

### 方案 C：分层身份模型

附件中的候选分层方向可解决冲突，但必须修正一个术语错误：`Digital Biosphere
Evolution Engine` 不是理论身份，而是现行 Constitution 定义的工程核心。

建议分析模型：

```text
Theory Identity
Silicon-Amplified Evolutionary Ecology
            ↓
Engineering Core / Engineering Identity
Digital Biosphere Evolution Engine + SAEE Architecture
            ↓
Product Identity
Agent Readiness Infrastructure
            ↓
Ecosystem Capability
SAEE Readiness Evaluation Capability / Service
```

#### 优点

- 保留理论与工程连续性；
- 让 Agent Readiness 成为清晰产品入口而不覆盖工程本体；
- GitHub 资产可作为内部能力、外部参考、migration source 或 adapter 归位；
- 产品状态、能力状态和生态分发状态可以分别治理；
- 与 `SAEE Evidence / Evaluation / Governance` 三版本目标兼容。

#### 缺点

- 需要严格维护四层名称，文档成本高于单一口号；
- 每个 README、schema、registry 和 capability surface 必须声明自己属于哪一层；
- 如果缺少 Agent-readable crosswalk，未来仍可能重新混用。

#### 风险

- 产品身份可能再次反向篡改理论/工程事实；
- “Ecosystem Capability / Service”可能被误写为已部署公共服务；
- 分层若只存在于文档而没有机器契约与 validator，会产生新的多真源。

#### 建议

```text
IDENTITY_MODEL_RECOMMENDATION=OPTION_C_LAYERED_MODEL
IDENTITY_MODEL_APPROVED=false
```

建议人类审查并确认方案 C。该建议不批准 Constitution 变更；若批准，必须通过正式
Decision Change Proposal / constitutional amendment workflow 更新权威文档、机器契约、
schema、入口指针、推荐门和 validator。

## 第三部分：SAEE 与 GitHub 资产关系

### 原则

SAEE 不是 GitHub 项目集合。统一性不来自整仓复制或取消独立历史，而来自：

```text
SAEE主体
  + 规范能力层
  + 外部参考/迁移来源
  + 生态适配与Demo
```

独立 repository、release、DOI、license、Git history、runtime owner 和 marketplace
状态可以保留。架构归属不自动等于 source migration、runtime integration 或产品发布。

### 能力映射表

| 资产 | 能力层 | 角色 | 是否独立产品 |
|---|---|---|---|
| SAEE Core | Engineering Core | canonical local Digital Biosphere Evolution Engine 与 SAEE 主体 | 是，作为 SAEE 主体；不是与子能力并列的拼盘成员 |
| POP / Persona Object Protocol | Identity | portable persona/identity object 外部协议参考；未来需 SAEE crosswalk | 否；保留独立协议、仓库和引用身份 |
| ARO-Audit | Evidence | receipt、replay、verification 与 audit-format 公共参考 | 否；保留独立参考仓库，不是 SAEE Execution Object |
| `aro-v0.8` / execution-integrity-core | Execution Integrity + Evidence | 外部 execution kernel 与 evidence export 参考；不是 SAEE runtime authority | 否；保留独立工程/研究身份 |
| Agent Evidence Project / `agent-evidence-layer` | Evidence and Immune | 受控迁移来源；必须走 provenance/license/schema/reuse gates | 否；历史外部产品/运行时状态在迁移完成前独立保存 |
| `agent-evidence` | Evidence | 公共 receipt/evidence reference implementation 与 compatibility source | 否；保留 release/citation identity |
| Agent Evidence Receipt | Evidence | `SAEE Evidence` 的 legacy external migration source，不是第四客户版本 | 否；迁移门通过前 runtime/marketplace owner 独立 |
| Token Governor | Constraint / Policy / Governance | budget-window 与 policy interface 参考，不是生产治理 runtime | 否；保留独立公共参考 |
| FDO/MVK | Execution Integrity | bounded execution-integrity、checksum、replay reference | 否；保留独立参考，不冒充端到端 runtime |
| Capability Registry | Governance + Discovery | `capability-package/manifest.json#canonical_inventory` 为唯一 capability fact source | 否；是 SAEE 一级产品表面 |
| MCP | Interface / Discovery Transport | canonical local stdio transport 与兼容适配层；不产生信任和授权 | 否；MCP 是入口，不是 SAEE 本体 |
| verifiable-agent-demo | Developer Experience | toy walkthrough 与跨层示例 | 否；保留独立 demo/paper identity |

### 决策建议

```text
GITHUB_ASSET_MODEL=SAEE_UMBRELLA_WITH_INTERNAL_CAPABILITIES_AND_EXTERNAL_REFERENCES
WHOLE_REPOSITORY_MERGE_RECOMMENDED=false
INDEPENDENT_HISTORY_PRESERVED=true
```

## 第四部分：ARO 术语决策

### 当前冲突

当前可验证的 `ARO` 含义至少包括：

1. `aro-v0.8`：execution-integrity-core / VAES 中的 Evidence Layer 和 export shape；
2. `ARO-Audit`：receipt/audit-format 参考；
3. `Audit Record Object` 或 ARO-compatible audit record：demo 与历史材料中的记录语义；
4. 候选 v2.0 新定义：`Agent Runtime Object`。

在没有 namespace 的情况下，这四类语义不可安全互换。

### 候选 1：Agent Runtime Object

#### 优点

- 表面上与 Identity → Execution → Evidence 对象链匹配；
- 对运行上下文对象有直观指向。

#### 问题

- 与现有 ARO Evidence/Audit 语义直接冲突；
- `Runtime` 暗示 SAEE 运行或控制 Agent，与“SAEE 不是 Agent Runtime”边界冲突；
- 会让检索 Agent、citation Agent 和迁移工具误路由到错误仓库或 schema；
- 需要大量历史文档和外部项目重命名，收益小于风险。

```text
AGENT_RUNTIME_OBJECT_RECOMMENDATION=DO_NOT_ADOPT
```

### 候选 2：Audit Record Object

#### 优点

- 与部分历史 demo 和 receipt 语义一致；
- 可描述后置审阅 artifact。

#### 问题

- 不能代表执行前后的完整 context；
- 会强化 audit-first framing；
- 与 Evidence Object、Evidence Receipt、ARO-Audit 职责重复；
- 不能成为候选 v2 Execution Layer 的规范对象。

```text
AUDIT_RECORD_OBJECT_RECOMMENDATION=KEEP_HISTORICAL_NAMESPACE_ONLY
```

### 候选 3：继续保留 ARO 但命名空间化

示例：

```text
vaes.aro.v0_8
aro_audit.receipt_profile
legacy.audit_record_object
saee.agent_runtime_object
```

#### 优点

- 可保留历史兼容；
- 不要求外部仓库立即改名；
- 有利于 provenance 和 citation 连续性。

#### 问题

- 新 SAEE 对象仍会继承高歧义 acronym；
- 人类口语和短文档仍会使用裸 `ARO`；
- namespace discipline 需要 validator 才能可靠执行。

```text
NAMESPACED_ARO_RECOMMENDATION=KEEP_EXISTING_HISTORICAL_FAMILIES_ONLY
```

### 候选 4：SAEE Execution Context Object (SECO)

#### 优点

- 不与现有 ARO 资产冲突；
- `Context` 明确表示 SAEE 接收和评估执行上下文，不负责执行 Agent；
- 可承载 agent reference、intent reference、action/tool declaration、environment、
  policy reference、permission declaration、trace/evidence references 和 limitations；
- 与 Evidence、Evaluation、Capability Discovery 契约容易组合；
- 允许现有 ARO family 通过 adapter/crosswalk 进入，而不被重命名或复制。

#### 问题

- 是新术语，必须证明没有与现有 SAEE 对象重复；
- 需要未来 schema、crosswalk、examples 和 validator；
- 不能被误写为已经实现的 capability。

#### 推荐方案

```text
ARO_TERM_RECOMMENDATION=DEPRECATE_BARE_ARO_IN_NEW_SAEE_AUTHORITY_TEXT
HISTORICAL_ARO_ASSETS=PRESERVE_WITH_EXPLICIT_NAMESPACE
NEW_EXECUTION_OBJECT_RECOMMENDATION=SAEE_EXECUTION_CONTEXT_OBJECT_SECO
SECO_IMPLEMENTATION_STATUS=DESIGN_ONLY_PROPOSAL
TERM_CHANGE_APPROVED=false
```

本建议仅适用于未来 SAEE 权威文本和新契约。它不要求重命名外部 repository、release、
DOI、historical schema 或已发布 artifact。

## 第五部分：产品族决策

### 当前冻结状态

现行 v1.1 和 Project Memory 已冻结三个目标客户版本：

```text
SAEE Evidence
      ↓
SAEE Evaluation
      ↓
SAEE Governance
```

这些是 target customer versions，不代表已经全部实现、发布、客户验证或生产就绪。

### 候选：增加 Autonomous Edition

#### A. 作为第四产品版本

优点：成熟度叙事完整，长期愿景明确。

缺点和风险：

- 修改现有 Frozen Decision；
- 在 external identity、delegation、trusted evidence、customer validation 和 Governance
  产品均未完成时制造提前产品化压力；
- 容易被解释为自动执行、自动授权或生产自治；
- 把未来研究方向变成当前 roadmap 资源竞争者。

```text
AUTONOMOUS_AS_FOURTH_PRODUCT_RECOMMENDATION=DO_NOT_ADOPT_NOW
```

#### B. 作为未来成熟度阶段

优点：保留长期愿景，同时不改变当前三个客户版本和主线优先级。

边界：

- `FUTURE_ONLY`；
- 不是当前 SKU、customer version、release 或 phase authorization；
- 不授权自动现实执行、自动 permission、自动 deployment 或 self-approval；
- 未来重新评估必须有独立 Constitution/Decision Change Proposal。

```text
AUTONOMOUS_RECOMMENDATION=FUTURE_MATURITY_HORIZON
TARGET_CUSTOMER_VERSION_COUNT=3
PRODUCT_FAMILY_CHANGE_APPROVED=false
```

### 建议

保持三个客户版本不变。把 Autonomous 写成 future maturity horizon，而不是第四产品版本。

## 第六部分：生态战略决策

### 方案 A：作为独立平台

#### 优点

- 品牌和用户入口集中；
- 能统一文档、计费与支持叙事。

#### 缺点/风险

- 容易滑向 Agent Runtime、observability platform、authorization system 或通用平台；
- 需要公共服务、身份、租户、存储、SLA 和生产证据，当前均未建立；
- 与“SAEE 成为 Agent 平台的能力，而不是 Agent 平台”冲突。

```text
ECOSYSTEM_OPTION_A=NOT_RECOMMENDED_AS_DEFAULT
```

### 方案 B：作为 Agent 生态能力

#### 优点

- 与两项只读 readiness 操作一致；
- 可通过 MCP/OpenAPI/Capability Contract 被不同 Agent 组合；
- 保留外部 runtime 和 authorization owner；
- 最符合 Agent-readable First。

#### 缺点/风险

- 必须提供稳定契约和清晰 non-claims；
- 容易被平台方当成一个普通 tool，弱化 SAEE 主体品牌；
- 仍需真实 interoperability 证据。

```text
ECOSYSTEM_OPTION_B=RECOMMENDED_CORE_MODE
```

### 方案 C：作为云厂商插件

#### 优点

- 进入现有分发、开发者和客户工作流；
- 可以复用云平台 Agent/MCP 入口。

#### 缺点/风险

- 单一云厂商绑定；
- plugin、marketplace、partner、official integration 等状态容易混报；
- 当前 Bailian、OpenAI Agents、LangGraph、CrewAI 等仍缺少正式互操作验证。

```text
ECOSYSTEM_OPTION_C=CHANNEL_ONLY_NOT_CORE_IDENTITY
```

### 方案 D：组合模式

建议结构：

```text
SAEE主体与规范能力真源
        ↓
Agent生态能力（核心消费模式）
        ↓
MCP / OpenAPI / local adapters
        ↓
Cloud plugin / marketplace / partner channels（可选分发）
```

#### 优点

- 保留 SAEE 统一主体、canonical capability facts 和品牌；
- 以 Agent capability 为核心，不建立平行 runtime；
- 云厂商插件只是分发适配，不反向成为架构权威；
- 可逐个平台验证，不需要一次性大规模重构。

#### 缺点/风险

- 必须严格维护 canonical core 与 adapter projection；
- 多渠道状态更需要 staged truth 和 owner-scoped registry；
- 若没有兼容性测试，会变成大量“配置存在但未验证”的表面资产。

#### 建议

```text
ECOSYSTEM_ENTRY_RECOMMENDATION=OPTION_D_COMBINATION_MODE
CORE_CONSUMPTION_MODE=AGENT_ECOSYSTEM_CAPABILITY
CLOUD_PLUGIN_ROLE=OPTIONAL_DISTRIBUTION_CHANNEL
INDEPENDENT_AGENT_PLATFORM=false
ECOSYSTEM_ENTRY_APPROVED=false
```

## 第七部分：Capability Contract 影响

以下契约仅为 future design inventory，不是新 capability、schema 或 implementation。

### 1. Identity Contract

目的：描述 Agent/persona 的声明身份、版本和引用关系。

候选字段：

- `identity_contract_version`；
- `agent_ref`；
- `pop_ref` / `persona_version_ref`；
- `issuer_declaration`；
- `identity_evidence_refs`；
- `delegation_ref`；
- `authentication_status`；
- `limitations`。

Non-claims：声明身份不等于 authenticated identity；POP projection 不等于 external
identity binding。

```text
IDENTITY_CONTRACT_STATUS=DESIGN_ONLY_PROPOSAL
```

### 2. Execution Context Contract

建议名称：`SAEE Execution Context Object (SECO)`。

目的：描述待评估行动的上下文，不运行或授权 Agent。

候选字段：

- `seco_version`；
- `execution_context_id`；
- `agent_ref` / `identity_ref`；
- `intent_ref`；
- `action_or_tool_declaration`；
- `environment_ref`；
- `policy_ref`；
- `permission_declaration`；
- `trace_refs` / `evidence_refs`；
- `external_effect_class`；
- `limitations`。

Non-claims：context 不等于 execution；permission declaration 不等于 authorization；
trace reference 不等于 authenticated event。

```text
EXECUTION_CONTEXT_CONTRACT_STATUS=DESIGN_ONLY_PROPOSAL
```

### 3. Evidence Contract

目的：描述 Observation/Evidence/Claim/Profile 的关系、provenance、integrity、source
completeness 和 non-claims。

候选要点：复用现有 Evidence Adequacy、receipt、Agent Evidence crosswalk 和 canonical
reason codes；不得创建第二 Evidence stack。

Non-claims：digest/signature 不自动证明 reality、source identity、completeness 或 legal
truth。

```text
EVIDENCE_CONTRACT_STATUS=PARTIAL_EXISTING_FUTURE_CROSSWALK_REQUIRED
```

### 4. Evaluation Contract

目的：把 Identity/Execution Context/Evidence/Policy 输入映射为 bounded decision
context。

候选输出：

- evidence quality / coverage；
- missing evidence；
- stable reason codes；
- readiness recommendation；
- truth boundary；
- limitations；
- independent authorization required。

当前 `evaluate_agent_run` 存在 `CONTINUE / HUMAN_REVIEW_REQUIRED / REPLAN / STOP`，
`evaluate_evidence` 返回 evidence quality。未来是否统一 enum 必须单独做兼容性决策，
本文不静默删除 `STOP` 或改写现有行为。

```text
EVALUATION_CONTRACT_STATUS=PARTIAL_EXISTING_NORMALIZATION_DECISION_REQUIRED
```

### 5. Capability Discovery Contract

目的：让 Agent 发现 capability、理解 SHOULD/SHOULD_NOT USE、解析 schema、选择
transport 并保留 non-claims。

必须复用：

- `capability-package/manifest.json#canonical_inventory`；
- `agent-index.json#capability_progress_ledger_v1`；
- canonical local SAEE MCP route；
- OpenAPI、capability card、examples 和 `llms.txt` 指针。

Non-claims：discovery 不等于 interoperability、adoption、public service、marketplace
listing 或 production readiness。

```text
CAPABILITY_DISCOVERY_CONTRACT_STATUS=PARTIAL_EXISTING_FUTURE_V2_ALIGNMENT_ONLY
```

## 第八部分：冻结决策建议

Project Memory 已存在 `F-001` 至 `F-005`。为避免 ID 冲突，本包使用 `V2-F-001` 至
`V2-F-005`；括号中的 F-001...F-005 仅对应附件要求的包内顺序。它们均为
`PROPOSED_FREEZE`，不是现行 Frozen Decision。

### V2-F-001（包内 F-001）：SAEE 身份

```yaml
status: PROPOSED_FREEZE
proposal: >-
  Preserve Silicon-Amplified Evolutionary Ecology as theory identity,
  Digital Biosphere Evolution Engine as engineering core,
  Agent Readiness Infrastructure as product identity, and
  SAEE Readiness Evaluation Capability as ecosystem capability.
human_confirmed: false
```

### V2-F-002（包内 F-002）：GitHub 资产关系

```yaml
status: PROPOSED_FREEZE
proposal: >-
  SAEE is the umbrella subject. GitHub repositories are internal capability
  references, migration sources, adapters or demos with independent provenance;
  they are not equal strategic products and are not copied wholesale.
human_confirmed: false
```

### V2-F-003（包内 F-003）：ARO 术语

```yaml
status: PROPOSED_FREEZE
proposal: >-
  Deprecate bare ARO in new SAEE authority text, preserve historical ARO assets
  under explicit namespaces, and use SAEE Execution Context Object (SECO) for
  the proposed non-runtime execution-context object.
human_confirmed: false
```

### V2-F-004（包内 F-004）：产品族

```yaml
status: PROPOSED_FREEZE
proposal: >-
  Keep exactly three target customer versions: SAEE Evidence, SAEE Evaluation,
  and SAEE Governance. Autonomous remains a future maturity horizon, not a
  fourth customer version.
human_confirmed: false
```

### V2-F-005（包内 F-005）：生态入口

```yaml
status: PROPOSED_FREEZE
proposal: >-
  Use combination mode: SAEE remains the canonical subject, Agent ecosystem
  capability is the core consumption mode, MCP/OpenAPI/adapters are interfaces,
  and cloud plugins/marketplaces are optional distribution channels.
human_confirmed: false
```

## 第九部分：影响范围

如果且仅当人类批准本包的冻结建议，未来可能影响以下文件类别。这里列出的路径不表示
全部必须修改，也不授权当前修改。

### Documentation

候选范围：

- Constitution successor or formal amendment document；
- `README.md`；
- `AGENTS.md`；
- `llms.txt`；
- `docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md` 或后继版本；
- Agent-readable architecture/term crosswalk；
- Project Memory Decision Change Proposal、decision log 和 frozen decisions。

### Schema

候选范围：

- successor Constitution schema；
- Identity Contract schema；
- SECO schema；
- Evidence crosswalk schema；
- Evaluation decision-context schema；
- Capability Discovery projection schema。

任何 schema 前必须先查 canonical inventory、现有 `agent-interface/schemas/`、AOP/POP/
Agent Evidence crosswalk 和相关 tests，禁止重复建设。

### Registry

候选范围：

- asset/repository/capability-crosswalk/product/MCP registry 的术语和关系字段；
- `agent-index.json` authority pointer/projection；
- canonical inventory 仅在 capability fact 真正变化时更新。

身份或文档迁移不自动授权 capability status 变化。

### Validator

候选范围：

- successor Constitution smoke；
- governance registry check；
- capability ledger smoke；
- authority/term crosswalk validator；
- negative cases：裸 ARO、新身份越权、Autonomous 第四版本、MCP/marketplace 状态升级。

### Code

当前不需要代码变化。未来若 contract 经批准且发现真实 missing behavior，只允许在
duplicate-build check、recommendation gate 和 capability fact sync 后做最小 adapter 或
normalization change。

### MCP

当前不修改。未来只允许在 canonical tool namespace、schema compatibility 和一个真实
interoperability slice 明确后调整 projection；不得创建第二 canonical SAEE MCP entrance。

### 当前授权边界

```text
ZERO_CHANGE_AUTHORIZED=true
CONSTITUTION_CHANGE_AUTHORIZED=false
AGENTS_CHANGE_AUTHORIZED=false
REGISTRY_CHANGE_AUTHORIZED=false
CAPABILITY_MANIFEST_CHANGE_AUTHORIZED=false
SCHEMA_CHANGE_AUTHORIZED=false
VALIDATOR_CHANGE_AUTHORIZED=false
CODE_CHANGE_AUTHORIZED=false
MCP_CHANGE_AUTHORIZED=false
PRODUCT_CHANGE_AUTHORIZED=false
WEBSITE_CHANGE_AUTHORIZED=false
GITHUB_ASSET_CHANGE_AUTHORIZED=false
EXTERNAL_ACTION_AUTHORIZED=false
```

`ZERO_CHANGE_AUTHORIZED` 表示本决策包不授权后续变更；它不否认本任务被明确授权新增
这一份报告文件。

## 第十部分：最终 Gate

```text
V2_DECISION_PACKET_STATUS=COMPLETE
AUTHORITY_CHANGE=NOT_EXECUTED
TERM_CHANGE=NOT_EXECUTED
PRODUCT_CHANGE=NOT_EXECUTED
CODE_CHANGE=NOT_EXECUTED
NEXT_ACTION=HUMAN_REVIEW_OF_DECISION_PACKET
```

建议人工审查只回答四个冻结点：

1. 是否接受分层身份模型，并确认理论身份与工程核心的正确层级；
2. 是否废弃新 SAEE 权威文本中的裸 `ARO`，并采用 `SECO` 作为候选执行上下文对象；
3. 是否保持三个目标客户版本，并把 Autonomous 限定为未来成熟度；
4. 是否在 Phase 0.5 gate 和正式 authority migration 完成后，采用组合模式进入生态阶段。

在人工确认前：

```text
PHASE_0_5_3_AUTHORIZED=false
CONSTITUTION_AUTHORITY_MIGRATION_AUTHORIZED=false
ECOSYSTEM_PHASE_ENTRY_AUTHORIZED=false
```

## 第十一部分：验证与 Non-Claims

### 本文件可声明

- 候选身份、术语、产品族和生态入口已经形成可审查的决策选项；
- 五项建议均标记为 `PROPOSED_FREEZE`；
- 当前 Constitution、capability facts、MCP、code 和 product 状态未由本文件改变。

### 本文件不能声明

- v2.0 已被批准或生效；
- Constitution authority 已迁移；
- `SECO` 已成为 schema 或 implemented capability；
- 三个客户版本已经全部实现、发布或客户验证；
- Autonomous 已成为产品；
- MCP、OpenAI、LangGraph、CrewAI、Qianfan、Bailian 或任何云厂商已完成官方集成；
- marketplace review 等于 listing；
- local/synthetic validation 等于 external adoption 或 production readiness；
- 当前 SAEE worktree clean。

### Git 边界

本任务只允许新增本报告。不执行 `git add`、`git commit`、`git push` 或 PR。验收应比较
审计前后的 status delta：除本报告外，不应由本任务产生其他新增或修改项。仓库原有
dirty entries 是受保护输入，不能被清理或误报为本任务变化。
