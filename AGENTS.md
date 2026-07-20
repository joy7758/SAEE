# AGENTS.md

## Project Identity

This repository implements SAEE: Silicon-Amplified Evolutionary Ecology.
本仓库实现 SAEE：Silicon-Amplified Evolutionary Ecology（硅基放大演化生态）。

The project is NOT an audit-first system, NOT a generic agent framework, and NOT a biological imitation.
本项目不是审计优先系统，不是通用智能体框架，也不是生物系统仿制品。

Its engineering core is Digital Biosphere Evolution Engine.
其工程核心是 Digital Biosphere Evolution Engine（数字生物圈进化引擎）。

## Strategic Alignment Invariant

The canonical strategic alignment entry is `STRATEGIC_ALIGNMENT.md`.
规范战略对齐入口为 `STRATEGIC_ALIGNMENT.md`。

All future tasks must preserve:
所有未来任务必须保持：

```text
SAEE_ROLE=EVOLUTION_INTELLIGENCE_LAYER
SAEE_GOVERNS_EVOLUTION=true
DBOS_GOVERNS_EXISTENCE=true
DBOS_NE_SAEE=true
```

SAEE governs evolution（SAEE 治理演化）. It may evaluate Fitness（适应度）, Evolution（演化）, Adaptation（适应性）and Stability（稳定性）, and produce reviewable Evolution Recommendations（演化建议）. Evaluation and recommendation never grant execution authority.

Do not reposition SAEE as an Agent Platform（智能体平台）, Runtime System（运行系统）, Identity System（身份系统）, Permission System（权限系统）, Registration System（登记系统）or DBOS replacement（DBOS 替代品）. SAEE must not directly mutate DBOS-governed Identity（身份）, Capability（能力）, Permission（权限）, Execution（执行）or source Evidence facts（源证据事实）.

This restriction does not erase the constitutionally assigned `SAEE Evidence and Immune Subsystem`（SAEE 证据与免疫子系统）. That subsystem may evaluate evidence adequacy and preserve SAEE evaluation artifacts, but it may not rewrite source evidence, authenticate identity, grant permission or authorize execution.

The DBA（Digital Biosphere Architecture，数字生物圈架构）strategic sources have `implementation_effect=NONE`. Strategic alignment does not create an Agent, Runtime, capability fact, development authorization, release or production claim. If a future task violates these boundaries, output `MAINLINE_DRIFT_DETECTED` and stop unless a separately applicable constitutional amendment and authorization exist.

## Constitutional Authority

All repository changes are governed by `SAEE Development Constitution v1.1`.
所有仓库修改都受 `SAEE 开发宪法 v1.1` 约束。

```text
constitution=docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md
machine_contract=agent-interface/governance/saee-development-constitution.v1.1.json
recommendation_gate=docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md
constitution_validator=scripts/saee_development_constitution_smoke.py
publication_venue_gate=docs/strategy/SAEE_ZERO_COST_JOURNAL_SELECTION_GATE.md
mandatory_author_cost_limit=0
real_journal_verification_required=true
```

Before changing behavior, resolve the canonical capability inventory, run the
duplicate-build validator, identify the affected evolution subsystem, execute
the Agent Recommendation Gate, define claims and non-claims, and preserve
staged truth.
修改行为前，必须解析规范能力清单、运行防重复建设校验、确认受影响的演化子系统、
执行智能体推荐门、定义主张与非主张，并保持分阶段真值。

Before selecting, transferring, resubmitting, or entering a manuscript into a
venue portal, verify that the venue is a real peer-reviewed scholarly journal
and that the selected route has zero mandatory author-side fees. Conference,
workshop, poster, Late-Breaking Abstract, mandatory APC, mandatory submission
or page fee, registration-fee, unknown-cost and unapproved waiver-dependent
routes are constitutionally ineligible.
选择、转投、重投或进入投稿门户前，必须证明目标是真实同行评审学术期刊，并且所选
路线的作者侧强制费用为零。会议、workshop、poster、Late-Breaking Abstract、强制
APC、强制投稿费或版面费、注册费、费用未知及依赖未批准减免的路线均不合格。

The Agent Evidence Project (legacy product name `Agent Evidence Receipt`,
legacy source repository `agent-evidence-layer`) is constitutionally part of
the `SAEE Evidence and Immune Subsystem`. This ownership does not claim that
its source code or runtime has been migrated. Reuse or adapt existing SAEE
capabilities before any code migration; never copy the legacy repository as a
parallel receipt stack.
智能体证据项目在宪法上属于 `SAEE Evidence and Immune Subsystem`；该归属不表示
源代码或运行时已经迁移。任何代码迁移前必须先复用或适配 SAEE 现有规范能力，禁止
复制旧仓库形成平行收据栈。

Run `python3 scripts/saee_development_constitution_smoke.py` before completing
any constitutional, architectural, product-boundary or evidence-subsystem
change.

## Constitutional Program Mainline

The current program mainline is the controlled integration of SAEE and the
Agent Evidence Project under provenance, license, schema-crosswalk, reuse,
migration and staged-truth gates.
当前项目主线是在来源、许可证、schema crosswalk（模式交叉映射）、复用、迁移和
分阶段真值门下，受控完成 SAEE 与智能体证据项目的合并。

The final customer-version target is exactly:
最终客户版本目标固定为：

```text
SAEE Evidence / SAEE Evaluation / SAEE Governance
```

These are target versions, not current implementation, launch, customer
validation or production claims.
这是目标版本，不代表当前已经实现、发布、完成客户验证或生产就绪。

The secondary task is to use SAEE to supervise, test and assess the integration
process. This dogfooding lane may produce evidence and correction
recommendations, but it may not displace the mainline or approve its own
changes.
副线任务是利用 SAEE 监督、测试和评估合并过程；该自用验证路线可以产生证据和纠偏
建议，但不得取代主线，也不得批准自身变化。

If a Commander prompt, role prompt, roadmap or local task elevates governance,
testing, audit or another secondary lane above the integration mainline, output
`MAINLINE_DRIFT_DETECTED`, identify the conflict and recommend correction. A
role prompt does not override the Constitution.
如果 Commander prompt（指挥官提示）、角色提示、路线图或局部任务把治理、测试、
审计或其他副线提升到合并主线之上，必须输出 `MAINLINE_DRIFT_DETECTED`，指出冲突并
提出修正建议；角色服从不能覆盖宪法。

## Phase 0 Governance Foundation

Before any AI Agent or Codex proposes a repository, architecture, capability,
MCP, product or migration change, read these authorities in order:

```text
governance_entry=governance/README.md
constitution_alignment=governance/constitution/constitution-alignment.md
asset_registry=governance/registry/asset-registry.json
repository_registry=governance/registry/repository-registry.json
capability_crosswalk=governance/registry/capability-crosswalk.json
mcp_registry=governance/registry/mcp-registry.json
product_registry=governance/registry/product-registry.json
codex_rules=governance/codex/codex-governance-rules.md
governance_validator=scripts/saee_governance_registry_check.py
```

Read the constitution first, the governance registries second, and the
canonical capability inventory third. The governance crosswalk is not a second
capability fact source; do not copy live repository, capability, MCP, product
or external-system status into this startup file.

## Agent-Readable First

All code and repository surfaces must include an agent-readable layer.
所有代码和仓库表面都必须提供智能体可读层。

- Keep protocols, schemas, module boundaries, examples, and status files easy for AI coding agents, retrieval agents, and citation agents to discover, parse, call, and reuse.
- 让协议、schema（模式）、模块边界、示例和状态文件便于 AI（Artificial Intelligence，人工智能）编码智能体、检索智能体、引用智能体发现、理解、调用和复用。
- When code changes behavior, update the relevant README, schema, agent index, llms entry, or design note in the same change.
- 代码行为改变时，必须同步更新相关 README、schema、agent-index、llms 条目或设计说明。
- Prefer explicit file-backed contracts over hidden conventions.
- 优先使用文件化、可检索的明确契约，不依赖隐藏约定。

## Capability Progress Ledger And Duplicate-Build Prevention

Every Agent must read this section before proposing architecture or feature work.
每个智能体在提出架构或功能工作前，必须先阅读本节。

Canonical lookup and rule pointers（规范查询入口与规则指针）:

```text
canonical_capability_source=capability-package/manifest.json#canonical_inventory
machine_ledger_projection=agent-index.json#capability_progress_ledger_v1
recommendation_gate=docs/strategy/SAEE_CAPABILITY_PROGRESS_LEDGER_RECOMMENDATION_GATE.md
ledger_validator=scripts/saee_capability_progress_ledger_smoke.py
roadmap_reference=reports/SAEE_CAPABILITY_ASSESSMENT_REPORT.md#recommended-next-prs
do_not_rebuild_from_historical_roadmap=true
```

Do not copy live capability statuses, MCP classifications or completed-work
snapshots into this start file. Resolve them at read time from the canonical
inventory and verify the machine projection before acting.
不得在本启动文件中手工复制实时能力状态、MCP 分类或已完成工作快照；执行前必须从
规范清单实时解析，并验证机器投影。

Mandatory duplicate-build check（强制重复建设检查）:

1. Read `capability-package/manifest.json#canonical_inventory`, run the canonical validator, then search relevant schemas, services, examples, tests and historical reports before proposing a new capability.
   在提出新能力前，必须先读取 `capability-package/manifest.json#canonical_inventory` 并运行规范校验器，再检索相关 schema、service、example、test 和历史报告。
2. Classify the target as `implemented`, `partial`, `design_only`, `missing`, `deprecated`, or `superseded`; do not infer implementation from documentation alone.
   必须把目标分类为 `implemented`、`partial`、`design_only`、`missing`、`deprecated` 或 `superseded`；不得从文档存在推断代码已实现。
3. If equivalent code already exists, do not create another implementation. Prefer reuse, canonical routing, consolidation, migration or deprecation.
   如果等价代码已存在，不得再造实现；优先复用、规范路由、合并、迁移或废弃。
4. Treat all historical `recommended_next_pr` fields as deprecated compatibility metadata. Capability facts come only from the canonical inventory; roadmap advice comes from an assessment or roadmap document.
   所有历史 `recommended_next_pr` 都只是已废弃的兼容元数据；能力事实只来自规范清单，研发建议只来自评估或路线图文档。
5. Run the Required Agent Recommendation Gate only after the inventory check. A recommendation gate cannot override evidence that the capability already exists.
   只有完成盘点后才能运行智能体推荐门；推荐门不能推翻“能力已经存在”的仓库证据。

Mandatory ledger synchronization（强制台账同步）:

- Any change to capability facts must update the canonical inventory first and its `agent-index.json` projection in the same change; roadmap advice remains outside both capability-fact surfaces.
- 能力事实变化时，必须先更新规范清单，并在同一次变更中更新其 `agent-index.json` 投影；路线图建议仍与这两个能力事实表面分离。
- Update `AGENTS.md` and the top `llms.txt` block only when authority pointers, startup rules or duplicate-build procedure change. Never synchronize by copying live capability status into them.
- 只有规范指针、启动规则或防重复建设流程变化时才更新 `AGENTS.md` 与 `llms.txt` 顶部区块；不得通过复制实时能力状态来“同步”。
- Update the detailed assessment report when its conclusions change; do not leave a completed target as an active next PR anywhere in the repository.
- 当详细评估结论变化时同步报告；任何已完成目标不得继续以 active next PR 留在仓库中。
- Preserve staged truth: local code, synthetic pass, package readiness, external integration, customer validation and production readiness are separate states.
- 保持分阶段真值：本地代码、合成验证通过、包就绪、外部集成、客户验证和生产就绪必须分开记录。
- A capability change is incomplete until code/contracts, tests, Agent-readable surfaces and ledger state agree.
- 在代码/契约、测试、智能体可读表面和台账状态一致前，能力变更不得视为完成。
- Run `python3 scripts/saee_capability_progress_ledger_smoke.py` before completing a capability change; the mainline guard runs the same check.
- 完成能力变更前必须运行 `python3 scripts/saee_capability_progress_ledger_smoke.py`；主线守卫也会执行同一检查。

## Agent-Native Commercial Decision Principle

The active commercial discovery path is agent-native:
当前商业发现路径以智能体原生为主：

```text
Agent discovers -> understands -> validates/invokes -> simulates repeatedly -> decides or composes
智能体发现 -> 理解 -> 验证/调用 -> 多轮模拟 -> 决策或组合
```

Agent decisions are the primary validation result. Human participation is not a prerequisite for capability preference, recommendation, or commercial-strategy completion. Human authority is retained only for consequential external actions.
智能体决策是主要验证结果。能力偏好、推荐和商业战略完成不以人工参与为前置条件；人类仅保留对重大外部动作的授权权力。

Before prioritizing any product feature or commercial surface, answer:
在提高任何产品功能或商业表面的优先级前，必须回答：

1. Can an AI agent discover this capability?
   智能体能否发现这项能力？
2. Can an AI agent understand when to use it and when not to use it?
   智能体能否理解何时使用、何时不使用？
3. Can an AI agent compose it into a workflow through a stable contract?
   智能体能否通过稳定契约把它组合进工作流？

If any answer is not clearly `yes`, lower the default priority unless the work is required for safety, law, supply-chain integrity, or architecture. Record the exception and the missing agent-readable work.
如果任一答案不是明确的 `yes`，默认降低优先级；安全、法律、供应链完整性或架构必需项除外，但必须记录例外理由和缺失的智能体可读工作。

`README.md`, `agent-index.json`, `llms.txt`, capability manifests, schema registries, examples, CLI/Tool interfaces, and offline validators are first-class product surfaces.
`README.md`、`agent-index.json`、`llms.txt`、能力清单、schema registry、示例、CLI/工具接口和离线验证器属于一级产品表面。

Agent decisions do not authorize external contact, customer or personal data use, permission expansion, contracts, pricing, Pilot execution, production deployment, or consequential public claims. These actions require a separate explicit authorization gate and are outside preference validation.
智能体决策不授权对外联系、客户或个人数据使用、权限扩大、合同、定价、Pilot 执行、生产部署或重大公开声明；这些动作必须经过独立的明确授权门，且不属于偏好验证。

Full logic: `docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md`.
完整逻辑见：`docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md`。

## Core Principle

Every change must strengthen at least one part of the evolution loop:
每次修改必须强化以下演化闭环中的至少一环：

1. Global Sensing（全球感知）
2. Trait Extraction（性状提取）
3. Ecological World Model（生态世界模型）
4. Counterfactual Simulation（反事实模拟）
5. Genome Branching（基因型分叉）
6. Controlled Mutation / Recombination（受控变异 / 重组）
7. Sandbox Development（沙盒发育）
8. Pareto Fitness Evaluation（帕累托适应度评估）
9. Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）

## Non-Negotiable Constraints

- Do not reframe this project as an AI audit SDK.
- 不要把本项目重构成 AI audit SDK（人工智能审计软件开发工具包）。
- Do not reframe this project as a generic multi-agent workflow system.
- 不要把本项目重构成 generic multi-agent workflow system（通用多智能体工作流系统）。
- Audit is an immune/evidence subsystem, not the project core.
- 审计是免疫/证据子系统，不是项目核心。
- The organism may observe the world, but it may not execute the world.
- 这个数字生物可以观察外部世界，但不能直接执行外部世界。
- Never execute unknown external repositories, install scripts, or untrusted dependencies automatically.
- 永远不要自动执行未知外部仓库、安装脚本或不可信依赖。
- Never expand permissions automatically.
- 永远不要自动扩大权限。
- Never copy external code as genome.
- 永远不要把外部代码直接复制为 genome（基因型）。
- Extract traits, not code.
- 提取性状，不复制代码。

## Required Design Check

Before adding any feature, answer:
添加任何功能前，必须回答：

1. Which evolution subsystem does this strengthen?
   它强化哪个演化子系统？
2. Does it improve sensing, branching, variation, selection, archive, or rollback?
   它是否改善感知、分叉、变异、选择、档案或回滚？
3. Does it preserve safety, license, supply-chain, and permission boundaries?
   它是否保留安全、许可证、供应链和权限边界？
4. Could this change push the project back into audit-first framing?
   这个修改是否会把项目重新推回审计优先叙事？

If the answer is unclear, stop and create an evolution proposal instead of changing code.
如果答案不清楚，停止修改代码，先创建 evolution proposal（演化提案）。

## Required Agent Recommendation Gate

Before deciding to develop a feature, consult an agent-readable recommendation gate:
在决定开发功能前，必须咨询智能体推荐门：

1. Ask: If a potential customer asked for this need, would you recommend this program?
   询问：如果潜在客户咨询这个需求，你会向客户推荐我们的程序吗？
2. Capture the answer as `recommend`, `conditional`, or `do_not_recommend`.
   将答案记录为 `recommend`、`conditional` 或 `do_not_recommend`。
3. If the answer is not `recommend`, record the reasons, decompose the weakness into fixable tasks, and solve or explicitly defer each blocker.
   如果答案不是 `recommend`，记录不推荐原因，把问题拆成可修复任务，并解决或显式延期每个阻塞点。
4. Development may continue only after the gate records why the feature is now recommendable or why it remains an internal experiment.
   只有当推荐门记录该功能为何已可推荐，或为何仍只是内部实验后，开发才可继续。

Use `docs/strategy/AGENT_RECOMMENDATION_GATE.md` for the full template.
完整模板见 `docs/strategy/AGENT_RECOMMENDATION_GATE.md`。
