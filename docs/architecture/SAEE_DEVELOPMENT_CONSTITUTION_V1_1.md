# SAEE 开发宪法 v1.1

## SAEE Development Constitution v1.1

```text
constitution_id=saee-development-constitution-v1.1
effective_date=2026-07-14
authority=repository_development_governance
engineering_core=Digital Biosphere Evolution Engine
agent_evidence_project_role=evidence_and_immune_subsystem
audit_first_reframe=false
external_world_execution=false
production_ready=false
program_mainline=saee_agent_evidence_integration
program_secondary=saee_supervises_and_tests_integration
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
```

机器契约：`agent-interface/governance/saee-development-constitution.v1.1.json`
Schema：`schemas/saee-development-constitution.schema.v1.1.json`
推荐门：`docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md`
确定性校验：`python3 scripts/saee_development_constitution_smoke.py`

## 序言：宪法解决什么

本宪法是 SAEE 的产品真源约束、技术方向约束、Codex 工作规则、变更审查标准和架构决策依据。它约束未来开发，不以人员配置、融资计划、组织规模或销售流程作为技术优先级依据。

智能体的发现、理解、调用、验证和推荐是能力方向的主要验证结果；人员不是能力偏好或技术战略完成的前置条件。对外联系、客户数据、合同、定价、权限扩张、生产部署和重大公开声明仍属于后果性外部动作，必须经过独立的明确授权门。

## 第一章：最高身份与根本使命

### 第一条：最高身份

SAEE 的理论身份是 `Silicon-Amplified Evolutionary Ecology`，工程核心是 `Digital Biosphere Evolution Engine`。

SAEE 的根本使命不是单独判断一项 Agent 行动是否具有证据，而是构造一个受控数字生物圈，使候选系统能够被感知、提取性状、建模、反事实模拟、分叉、变异、沙盒发育、选择、归档和回滚。

证据评估服务于演化选择和回滚免疫，不得取代演化闭环成为项目唯一使命。

### 第二条：唯一允许的核心闭环

每次修改必须强化至少一个环节：

1. Global Sensing（全球感知）
2. Trait Extraction（性状提取）
3. Ecological World Model（生态世界模型）
4. Counterfactual Simulation（反事实模拟）
5. Genome Branching（基因型分叉）
6. Controlled Mutation / Recombination（受控变异 / 重组）
7. Sandbox Development（沙盒发育）
8. Pareto Fitness Evaluation（帕累托适应度评估）
9. Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）

如果无法说明强化哪一环，停止编码并先写 evolution proposal（演化提案）。

## 第二章：Agent-Readable First

### 第三条：智能体可读层是一级产品表面

协议、schema、能力清单、模块边界、状态、示例、CLI / Tool 接口、非主张和离线校验器必须文件化、可发现、可解析、可调用、可引用。

行为改变必须在同一次变更中同步相关 README、schema、`agent-index.json`、`llms.txt`、能力清单或设计说明。隐藏约定不得成为唯一契约。

### 第四条：能力进入优先级前的三个问题

1. 智能体能否发现这项能力？
2. 智能体能否理解何时使用、何时不使用？
3. 智能体能否通过稳定契约把它组合进工作流？

任一答案不是明确的 `yes` 时，默认降低优先级；安全、法律、供应链完整性或架构必需项除外，但必须记录例外和缺失的智能体可读工作。

## 第三章：智能体证据项目正式归属

### 第五条：归属决定

`Agent Evidence Project`（历史产品名 `Agent Evidence Receipt`，历史源仓库名 `agent-evidence-layer`）从本宪法起不再被定义为 SAEE 的平行竞争产品。它在 SAEE 中的正式角色是：

```text
SAEE Evidence and Immune Subsystem
SAEE 证据与免疫子系统
```

该归属是架构和治理层的正式合并。源代码历史、许可证、commit、发布记录和独立仓库可以在完成迁移门之前保留，不得用品牌归属替代代码来源证明。

### 第六条：在演化闭环中的位置

```text
Observation / Rehearsal Output
              ↓
Normalization + Provenance Envelope
              ↓
Evidence Object / Evidence Receipt
              ↓
Integrity + Completeness Verification
              ↓
Evidence Adequacy Evaluation
              ↓
Fitness Context / Selection Evidence
              ↓
Evolutionary Archive / Rollback Decision
```

证据子系统为 sensing、simulation、fitness、archive 和 rollback 提供可复核上下文。它不得直接批准、拒绝或执行外部世界动作。

### 第七条：纳入范围

允许纳入的职责：

- 规范化后的 Agent 运行事件与 artifact 清单；
- Evidence Object、Evidence Receipt 和 verification receipt；
- canonicalization、digest、签名验证结果、provenance 和 source completeness；
- 证据引用、组合、确定性校验和篡改检测；
- 为 Evidence Adequacy、fitness selection、lineage archive 和 rollback 提供输入。

不得由此推导的职责：

- 通用 tracing / APM / observability 平台；
- IAM、OAuth、RBAC、Cloud IAM 或执行授权；
- 自动部署、Agent Runtime 或外部动作执行；
- 法律事实认定、合规认证或责任裁决；
- 仅凭 hash 或 signature 证明原始事件真实、完整或由声明主体产生。

`signature_valid=true` 最多说明被验证的签名关系成立；它不自动等于 `event_authentic=true`、`source_identity_authenticated=true`、`complete=true` 或 `legally_proven=true`。

### 第八条：当前分阶段真值

本次更新的目标分类是 `partial`：

- 宪法归属：`implemented`；
- SAEE 内已有 Evidence Adequacy、局部 receipt 与 observed-trace 能力：必须复用；
- `agent-evidence-layer` 源代码纳入 SAEE：`design_only`，本次未复制；
- 统一运行时接入：`missing`；
- 可信 trace 到 evidence 的完整转换：以 `capability-package/manifest.json#canonical_inventory` 的实时状态为准；
- 外部互操作、客户验证与生产就绪：未由本宪法建立。

```text
source_code_migrated=false
runtime_integrated=false
external_integration_validated=false
customer_validated=false
product_launched=false
production_ready=false
```

能力事实只能从规范清单读取。本节不得被解释为对 `canonical_inventory` 的替代快照。

## 第四章：防重复建设与迁移纪律

### 第九条：先复用，再迁移，最后才新增

任何证据项目代码迁移前，必须先解析并复用以下规范能力或其后继项：

- `saee.evaluate_evidence`；
- `saee.general_trace_normalization`；
- `saee.trusted_trace_to_evidence_conversion`；
- `saee_backend/services/resource_resolution_receipt.py`；
- `agent-interface/schemas/*receipt*`；
- `docs/standards/SAEE_AGENT_RECEIPT_*`。

存在等价实现时，不得复制一份新实现。只能选择规范路由、adapter、合并、迁移或废弃，并用 ADR 记录来源、许可证、兼容性、替代关系和删除条件。

### 第十条：证据项目迁移门

1. `CONSTITUTIONAL_INTEGRATION`：本宪法和机器契约通过校验。
2. `SOURCE_PROVENANCE_FREEZE`：从干净、可复现的 source commit 建立文件和许可证 manifest。
3. `SCHEMA_CROSSWALK`：逐项判定 reuse / adapt / migrate / deprecate，禁止整仓复制。
4. `INTERNAL_ADAPTER`：只在 SAEE 内部边界接入，保持无外部执行和最小权限。
5. `CANONICAL_CAPABILITY_UPDATE`：代码、schema、测试、Agent-readable 表面和台账一致后，才能先改规范清单再改机器投影。
6. `EXTERNAL_VALIDATION`：与本地测试、合成 pass、package-ready、customer validation 和 production readiness 分开记录。

未通过前一门，不得宣称后一门完成。

## 第五章：标准优先但不虚构合规

### 第十一条：标准对齐顺序

在适用且已核对具体版本时，优先使用：

- OpenTelemetry：trace 与 resource 语义；
- MCP：Agent 能力发现和调用运输；
- JSON Schema：对象交换与离线验证；
- SPDX / CycloneDX：来源、许可证与供应链描述。

概念相似不等于合规，mapping 不等于 adoption，local validation 不等于 interoperability。任何外部标准声明必须记录规范版本、来源、字段 crosswalk、差异和测试证据。

## 第六章：开发前强制协议

### 第十二条：每次修改必须先回答

1. 影响哪个演化子系统？
2. 是否改善 sensing、branching、variation、selection、archive 或 rollback？
3. 影响哪个规范对象、schema、接口或 capability？
4. 规范清单当前把目标分类为什么？
5. 是否存在可复用实现；删除或废弃什么重复能力？
6. 智能体是否会向目标需求推荐 SAEE；若不是 `recommend`，阻塞点如何拆解？
7. 是否保持 safety、license、supply-chain 和 permission 边界？
8. 是否把项目推回 audit-first 或 generic agent framework？
9. 本次明确的 claims、non-claims 和 staged truth 是什么？
10. 哪些确定性、negative 和 schema 校验证明变更成立？

无法回答时，不得修改行为代码。

### 第十三条：Codex 启动句

未来 SAEE 修改任务应从以下约束开始：

```text
You are modifying SAEE under SAEE Development Constitution v1.1.
Resolve the canonical capability inventory, run duplicate-build validation,
identify the affected evolution subsystem, execute the Agent Recommendation
Gate, define claims and non-claims, preserve staged truth, and run deterministic
validation before completion.
```

## 第七章：测试与真值宪法

### 第十四条：可验证、可解释、可限制

每项能力必须具有 schema validation、negative cases、deterministic validation、稳定 reason code 或等价解释，以及明确 non-claims。

以下状态永久分开：

```text
design_only
local_implementation
synthetic_pass
package_ready
external_integration
customer_validated
production_ready
```

不得从前一状态自动升级到后一状态。

## 第八章：不可逾越边界

### 第十五条：数字生物可观察世界，但不得执行世界

SAEE 可以接收受控观察、模拟、评估和归档材料，但不得自动：

- 执行未知外部仓库或安装脚本；
- 扩大权限；
- 把外部代码复制为 genome；
- 联系客户或使用客户/个人数据；
- 批准部署、签署合同、发布重大声明或执行现实动作。

提取 traits，不复制 code。Evidence 和 Evaluation 产生 decision context，不产生 execution authority。

## 第九章：修宪与执行

### 第十六条：宪法优先级

本宪法低于安全、法律和显式用户授权边界，高于 roadmap、商业计划、历史推荐字段和局部模块惯例。发生冲突时，先停止修改并记录 ADR 或修宪提案。

### 第十七条：修宪条件

修宪必须同时更新：

- 本文件；
- `agent-interface/governance/saee-development-constitution.v1.1.json` 或其后继版本；
- `AGENTS.md` 与 `llms.txt` 的权威指针；
- `agent-index.json` 的机器入口；
- 推荐门和确定性 smoke。

修宪本身不更新任何能力实现状态。能力事实仍必须先更新 `capability-package/manifest.json#canonical_inventory`，再同步 `agent-index.json#capability_progress_ledger_v1`。

## 第十章：主线任务、客户版本与纠偏义务

### 第十八条：当前项目主线

SAEE 当前项目主线是：在保留来源、许可证、供应链、权限、runtime 和 staged truth
边界的前提下，完成 SAEE 与 Agent Evidence Project 的受控合并。

这里的“合并”不是整仓复制，也不是用架构归属冒充代码迁移完成。它必须依次通过
source provenance freeze、schema crosswalk、reuse/adapt/migrate/deprecate 判定、内部
adapter、canonical capability update 和外部验证门。

```text
program_mainline=saee_agent_evidence_integration
merge_completed=false
source_code_migrated=false
runtime_integrated=false
```

Digital Biosphere Evolution Engine 仍是工程核心；当前主线说明项目正在完成什么，不把
SAEE 重构为 audit-first system。

### 第十九条：最终三个客户版本目标

受控合并完成后的目标客户版本固定为三个：

1. `SAEE Evidence`：面向证据对象、收据、来源、完整性与免疫档案的客户版本。
2. `SAEE Evaluation`：面向就绪度、证据充分性、可靠性与选择上下文的客户版本。
3. `SAEE Governance`：面向受控变更、决策边界、演化档案与回滚治理的客户版本。

这是 target product family（目标产品族），不是当前发布状态。除非规范产品注册表、
代码、契约、测试、客户验证和发布证据一致，不得声称三个版本已经实现、可购买、已
发布或生产就绪。

```text
target_customer_version_count=3
target_customer_versions=SAEE_Evidence;SAEE_Evaluation;SAEE_Governance
three_versions_implemented=false
three_versions_customer_validated=false
three_versions_product_launched=false
```

### 第二十条：副线任务与 Dogfooding 边界

副线任务是利用 SAEE 监督、测试并评估 SAEE 与 Agent Evidence 的合并过程。这既是
合并治理，也是对 SAEE 自身 sensing、evaluation、archive 和 rollback 能力的测试。

副线只能产生 evidence、assessment、drift signal 和 correction recommendation；不能
批准自己的变更，也不能取代主线。不得因为治理报告、validator、Dogfooding 或测试
数量增长，就把“监督测试合并”改写为项目最终目标。

```text
program_secondary=saee_supervises_and_tests_integration
secondary_displaces_mainline=false
self_assessment_authorizes_change=false
```

### 第二十一条：指令漂移纠偏

Commander、role prompt、roadmap、历史报告或局部任务说明都不能覆盖本章主线。任何
AI Agent 发现任务把治理、测试、审计、商业表面或其他副线提升为主线，或者让合并
失去受控迁移边界时，必须：

1. 明确输出 `MAINLINE_DRIFT_DETECTED`；
2. 指出偏离了哪一条主线或 truth boundary；
3. 提出回到“受控合并 → 三个客户版本目标”的修正建议；
4. 在人类明确修改宪法前，不得用角色服从替代宪法判断。

纠偏义务不授权 Agent 拒绝安全、法律或明确人类外部动作 gate，也不授权自行执行代码
迁移、发布或部署。
