# SAEE First Offer Validation Plan

```text
report_id=SAEE_FIRST_OFFER_VALIDATION_PLAN
requested_phase=Phase_6.0-C
workstream_role=NON_AUTHORIZING_OFFER_VALIDATION_DESIGN
current_effective_authority=SAEE_Development_Constitution_v1.1
program_mainline=controlled_SAEE_Agent_Evidence_integration
plan_created_at=2026-07-15
offer_validation_plan_executed=false
customer_contacted=false
interviews_conducted=0
```

本报告设计 SAEE 首个商业 Offer（报价/交付提议）的验证方法。它不销售产品、不创建
报价、不联系客户、不开发能力，也不授权 Phase 6.0-B。目标不是证明 SAEE “能做很多”，
而是用可证伪的真实行为证据判断：哪个受限场景最可能形成付费需求。

## Executive Decision

三个候选 Offer 中，**`Coding Agent Readiness Review` 是第一验证候选**，不是已经选定
开发或已经可以销售的产品。原因是它与当前 `saee.evaluate_agent_run`、
`saee.evaluate_evidence`、本地 Qoder 合成示例和现有四类 Evidence 的距离最短，能够在
不创建新 Capability 的前提下验证客户问题。

`Production Agent Change Review` 的潜在损失和风险最高，但当前缺少可信 trace、外部
身份/委托绑定和生产集成，进入企业流程也更深；`Customer Agent Response Review` 容易
理解，但当前公共 Evidence 集合不能直接表达政策来源、版本和适用范围，并且需与 RAG、
guardrail 和 response evaluation 等既有工具证明差异。

当前只能得出验证顺序，不能得出付费结论：

```text
VALIDATION_PRIORITY=CODING_AGENT_READINESS_REVIEW
DEVELOPMENT_PRIORITY=UNDECIDED
OFFER_SELECTED_FOR_DEVELOPMENT=false
PAIN_EXISTENCE=VALIDATED_BY_REAL_EVENTS
OFFER_DEMAND_VALIDATED=false
WILLINGNESS_TO_PAY=NOT_VALIDATED
PRICE=UNVALIDATED
EXPERIMENTAL_QUOTE_CREATED=false
```

## 0. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED
```

把 `Phase 6.0-C` 当作当前程序主线、把验证计划当作产品开发授权，或从本报告直接跳转
到 `Phase 6.0-B`，都会与 active Constitution 和当前治理门冲突：

- 当前 authority 仍是 `SAEE Development Constitution v1.1`；
- 当前 program mainline 仍是 SAEE 与 Agent Evidence Project 的受控整合；
- Phase 0.5 的迁移事实仍保持 `G1_EFFECTIVE=false`、
  `PHASE_0_5_7A_AUTHORIZED=false`；
- First Principles 在当前仓库中只是分析方法候选，不是 active Constitution 的新增最高
  条款；
- 商业验证不能反向改变 Capability、产品或生态真值。

因此本报告将请求解释为
`NON_AUTHORIZING_OFFER_VALIDATION_WORKSTREAM`。只有人工审查本计划后，才可以另行授权
客户发现；客户发现通过也不自动授权 Capability 开发、报价发布、Pilot、生产部署或
对外主张。

```text
MAINLINE_CORRECTION=NON_AUTHORIZING_OFFER_VALIDATION_WORKSTREAM
PROGRAM_MAINLINE_CHANGED=false
CURRENT_AUTHORITY_CHANGED=false
PHASE_6_0_B_AUTHORIZED=false
```

## 1. Evidence and Truth Baseline

### 1.1 Inputs

| Input | Role | SHA-256 at review |
|-|-|-|
| `reports/SAEE_PAIN_TO_SEMANTIC_MAPPING_REPORT.md` | 真实/相邻事件、损失和语义映射 | `5959d9113d0cea67bfddf853825c1937bfd34d51379be525ce15319f24395c11` |
| `reports/SAEE_READINESS_CONTRACT_INVENTORY_REPORT.md` | 现有原语、缺口与 contract 边界 | `a47d9aa9e24016c41e26171b02cee375c09aed3a2026289a917c7ca83b1ca6bf` |
| `capability-package/manifest.json` | 唯一 canonical capability 真源 | `fda5f5a2dca0c79ef98f6cdf1f2a5be80b3a3e672eeec2a7a76e63bf1b25fa70` |
| `docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md` | 当前宪法权威 | `37d9adb3049c5fdd871460f6756240a177264e4442cc38252786e9d7c86f378c` |

### 1.2 Current commercial truth

仓库当前多个 commercial truth surfaces 一致记录：

```text
customer_contacted=false
interviews_conducted=0
customer_validated=false
commercial_delivery_completed=false
market_validation=false
pricing_validated=false
```

历史内部 pricing/packaging 草案不是客户支付意愿证据，不进入本计划的价格判断。公开
事件证明痛点和潜在损失，不证明购买预算；本地 demo 证明可演示路径，不证明客户需求。

### 1.3 Current capability truth

| Surface | Canonical status | What this plan may claim | What this plan may not claim |
|-|-|-|-|
| `saee.evaluate_agent_run` | `implemented / active / local alpha` | 可对 declared trace metadata 和所需 Evidence 覆盖度做确定性本地评估 | trace 已认证、部署被授权、客户验证或生产就绪 |
| `saee.evaluate_evidence` | `implemented / active / local alpha` | 可检查封闭 Evidence bundle 是否覆盖显式要求，并返回缺失项 | 真实事件被证明、认证、合规/法律判断或行动授权 |
| canonical MCP | local stdio, `publicly_deployed=false` | Agent 可在本地通过规范入口调用两个只读工具 | 已发布公共服务、官方框架集成或外部互操作已验证 |
| Qoder example | local synthetic fixture | Coding Agent 场景已有可检索示例，缺 rollback/approval 时返回 `REPLAN` | Qoder runtime/官方集成/真实客户流程已验证 |

现有公开 readiness 路径的 Evidence types 是封闭集合：

```text
TEST_RESULT
ROLLBACK_PLAN
PERMISSION_BOUNDARY
HUMAN_APPROVAL
```

用户附件示例中的 `code review evidence` 不是当前 canonical Evidence type。本计划只把
“代码审查是否是客户必需证据”作为 discovery question；不得把它写成已有能力。若访谈
证明必须支持，仍需独立 contract、duplicate-build 和开发授权决策。

## 2. Offer A — Coding Agent Readiness Review

### Customer-facing definition

**中文名：** AI 编程智能体行动准备评估

> 在 AI 编程 Agent 的代码变更进入合并、数据库或生产流程前，检查当前提交的测试、
> 权限边界、回滚和审批证据是否足以进入下一步受控流程。

这不是 deployment approval、code review、security certification 或生产控制器。

### Offer card

| Field | Definition |
|-|-|
| Target Customer | 已实际使用 Coding Agent 的企业研发部门、内部 AI developer platform 团队、DevOps/platform engineering 团队、AI 编程平台提供方 |
| Pain | Agent 能写代码，但在合并、数据库和生产邻近动作前，团队缺少统一、可追溯的证据充分性判断；结果是禁止使用、重复人工检查、延迟发布或承担未经证据支持的动作风险 |
| Existing Event Evidence | Pain report 的 Replit 类公开事件（`evidence_level=B`）支持 action/data risk；本地 Qoder fixture 只证明可演示性，不能作为市场证据 |
| Decision Gap | “当前证据是否足以让这次变更进入下一步受控检查；缺什么；应该 `CONTINUE`、`HUMAN_REVIEW_REQUIRED`、`REPLAN` 还是 `STOP`？” |
| SAEE Fit | `HIGH_FOR_VALIDATION`：现有两个 Evaluation operations、四类 Evidence、missing evidence、reason/limitations 和本地 Qoder 路径可复用 |
| Buyer | 经济购买者候选：CTO、VP Engineering、Head of Developer Platform；Champion：AI platform/DevEx/DevOps lead；使用者：engineering lead/release owner；否决者：Security、Legal、Procurement |
| Validation Hypothesis | 若组织已有活跃 Coding Agent、发生过真实 block/revert/escalation 或持续投入人工 release checks，并能指出预算和采购路径，则会为一个受限、离线、非授权型 readiness review 推进具体付费 Pilot 评估 |

### First-principles check

1. **真实损失是什么？** 生产数据/服务损失、恢复成本、发布延迟、工程师重复检查时间，
   以及因为风险不可判断而完全禁用 Agent 所损失的效率。公开事件只支持风险存在，实际
   客户损失必须由访谈中的过去事件和当前花费证明。
2. **为什么现在存在？** Coding Agent 已从代码补全向多步骤修改、工具调用和生产邻近
   工作流扩展；权限和影响面增加快于团队现有 release evidence 的统一表达。该判断是
   待访谈验证的市场假设，不是普遍事实声明。
3. **为什么已有工具不能解决？** CI、code review、IAM、change management、scanner
   和 observability 分别覆盖测试、审批、权限或观测。SAEE 的候选差异是将已有证据映射
   为一个有缺口和限制的下一步建议。若客户现有 release gate 已完整完成该工作，则本
   Offer 没有独立购买理由。
4. **最小需要什么能力？** 复用 `saee.evaluate_agent_run`、
   `saee.evaluate_evidence`、四类现有 Evidence 和受限报告模板；不需要新 Capability。
   proposed action 与 declared run 的时间语义差距必须显式披露，不能伪装已经解决。
5. **为什么客户可能付费？** 只有当其当前人工检查、延迟、事故恢复或 Agent 禁用成本
   可量化，且大于评估和采购成本时才可能付费。当前没有直接支付证据。

### Critical disconfirming evidence

- Coding Agent 从未触达合并、数据库或发布邻近流程；
- 当前 CI/CD、IAM、review 和 change-management gate 已提供足够判断；
- 问题只需权限收窄，不需要独立 Evidence adequacy 解释；
- 没有可量化的人工、延迟或风险成本；
- 没有预算 owner，或采购成本高于问题损失；
- 客户必须要实时生产拦截、认证身份或可信 telemetry，而不是受限离线 review。

## 3. Offer B — Production Agent Change Review

### Customer-facing definition

**中文名：** 生产环境智能体变更评估

> 在 DevOps/operations Agent 提议删除资源、改变基础设施或执行高影响恢复动作前，
> 离线检查影响说明、权限边界、备份/回滚和审批证据是否齐全。

这不是 production control plane、IAM、policy enforcement、SRE automation 或动作授权。

### Offer card

| Field | Definition |
|-|-|
| Target Customer | 已在 cloud operations、SRE 或 infrastructure workflow 中试用 Agent 的中大型企业、云平台团队和受监管组织 |
| Pain | 高影响变更可能造成服务中断、数据丢失、资源误删和监管/恢复成本；现有工具输出分散，无法解释当前 action evidence 是否足够 |
| Existing Event Evidence | Replit 类生产数据事件是 Coding/Production 邻近信号；Cruise 事件支持高影响系统异常后继续动作和报告不完整的风险，但不是 DevOps Agent 直接市场证据 |
| Decision Gap | “这次高影响变更的理由、影响、权限、备份、回滚和独立审批是否足以进入执行前授权流程？” |
| SAEE Fit | `HIGH_CONCEPTUAL / LOW_CURRENT_DELIVERY`：现有 Evaluation 语义匹配，但 trusted trace、identity/delegation binding、生产集成均缺失 |
| Buyer | 经济购买者候选：CTO/CIO、VP Infrastructure、Head of Cloud/SRE；Champion：platform/SRE lead；否决者：Security、Risk、Compliance、Change Advisory Board、Procurement |
| Validation Hypothesis | 若组织已经让 Agent 生成或提交生产变更，且现有 change process 对 Agent 来源/证据缺口有明确成本，可能愿意为离线 preflight review 进入较长的安全和采购验证 |

### First-principles check

1. **真实损失是什么？** outage、数据/资源损失、恢复成本、SLA/监管影响和高额人工变更
   审查；必须由客户过去事件证明，不能从相邻事故推导其已发生。
2. **为什么现在存在？** Operations Agent 开始生成基础设施或成本优化变更，但高权限、
   高影响 workflow 的组织控制更严格。实际采用程度是首要 discovery question。
3. **为什么已有工具不能解决？** IaC plan、policy-as-code、IAM、change ticket、backup 和
   observability 都覆盖重要部分。只有当客户缺少跨这些证据的明确 decision context 时，
   SAEE 才有增量价值；若 policy engine 已能确定性阻断，不能重复建设。
4. **最小需要什么能力？** 概念上仍是现有 Evidence + Evaluation；但对真实生产 Offer，
   identity、delegation、trusted evidence 和安全集成是硬缺口。因此当前只可验证问题，
   不可承诺交付生产 gate。
5. **为什么客户可能付费？** 单次事故损失可能很高，风险和 SRE 预算也可能明确；相反，
   安全审查、采购和集成成本同样很高，可能使早期购买概率低于 Coding Agent。

### Critical disconfirming evidence

- 目标组织禁止 Agent 参与任何 production-adjacent workflow；
- Agent 只生成建议，现有人工 CAB 已充分处理；
- IaC/policy-as-code/IAM 已消除相关 decision gap；
- 客户只接受实时、认证、生产集成，而 SAEE 当前不具备；
- 销售和安全评审周期使小规模验证不经济。

## 4. Offer C — Customer Agent Response Review

### Customer-facing definition

**中文名：** 客服智能体回答准备评估

> 在高影响客户回答被使用前，检查其是否有可定位的官方依据、当前版本和适用范围，
> 并指出缺失证据与复核需求。

这不是客服机器人、RAG 系统、内容 moderation、法律意见或事实真伪认证。

### Offer card

| Field | Definition |
|-|-|
| Target Customer | 已上线或试点生成式客服的航空、金融、保险、公共服务、电商和 SaaS 客服团队，以及 conversational AI 平台方 |
| Pain | 错误或不一致回答可能造成赔付、投诉、监管/品牌成本；团队难以证明特定回答使用了当前、适用的官方依据 |
| Existing Event Evidence | Air Canada tribunal case 和 NYC MyCity audit 是直接的 response-risk 证据；它们证明问题存在，不证明任何目标客户预算 |
| Decision Gap | “该回答是否有当前政策/来源证据支持，是否适用于本用户和场景，还是必须重写或人工复核？” |
| SAEE Fit | `PARTIAL`：Evidence adequacy 语义匹配；当前四类 Evidence 不直接覆盖 policy source、version、scope 或 response consistency |
| Buyer | 经济购买者候选：Chief Customer Officer、VP Support、Head of AI Platform；Champion：CX automation/knowledge owner；否决者：Legal、Compliance、Security、Procurement |
| Validation Hypothesis | 若组织已有高影响生成式客服、持续投入 QA/人工复核，并且现有 RAG/eval 无法提供版本化证据充分性，则可能为受限 response-readiness review 推进 Pilot |

### First-principles check

1. **真实损失是什么？** 赔付、投诉处理、监管/法律成本、人工 QA 和品牌损失。Air Canada
   提供直接事件证据，客户自身损失仍需访谈验证。
2. **为什么现在存在？** 生成式客服扩大回答覆盖面，知识更新、版本、范围和一致性问题
   随之显露；但不同企业的 RAG 和 QA 成熟度差异很大。
3. **为什么已有工具不能解决？** RAG citation、knowledge governance、LLM eval、guardrail
   和 human QA 已覆盖大量场景。SAEE 只有在“证据充分性 + 缺口 + bounded next-step”未被
   当前 stack 覆盖时才有价值，竞争和替代风险最高。
4. **最小需要什么能力？** 需要 response claim、policy source/version/scope、一致性
   evidence 和 recommendation 的受限 contract。它不在当前四类 Evidence 的完整实现
   范围内，因此不能称为现有可售 Offer。
5. **为什么客户可能付费？** 当错误回答成本和持续人工 QA 花费可量化，且现有工具不能
   产生可追溯的使用决定时可能付费；当前没有预算证据。

### Critical disconfirming evidence

- 客户回答不产生高影响承诺，错误成本低；
- 现有 RAG/eval/QA 已提供来源、版本、范围和升级路径；
- 客户主要问题是知识库质量，不是 readiness decision；
- 所需 policy evidence contract 过于行业定制；
- 没有独立预算，或预算已锁定在现有 CX/LLMOps 平台。

## 5. Comparative Decision

评分是本轮相对优先级假设，不是市场统计或客户验证。`5` 表示更有利；“Current
delivery fit” 已对当前实现边界扣分。

| Criterion | Coding Agent | Production Agent | Customer Agent |
|-|-:|-:|-:|
| Real-event pain proximity | 4 | 4 | 5 |
| Potential loss severity | 4 | 5 | 4 |
| Current SAEE contract fit | 5 | 3 | 2 |
| Can validate without new Capability | 5 | 3 | 2 |
| Short sales/integration path | 4 | 1 | 3 |
| Differentiation hypothesis | 4 | 4 | 2 |
| **Validation-order total** | **26** | **20** | **18** |

Decision:

```text
FIRST_VALIDATION_CANDIDATE=SAEE_CODING_AGENT_READINESS_REVIEW_V0_1
RATIONALE=SHORTEST_TRUTHFUL_PATH_TO_TESTABLE_CUSTOMER_BEHAVIOR
HIGHEST_POTENTIAL_LOSS_CANDIDATE=PRODUCTION_AGENT_CHANGE_REVIEW
CUSTOMER_RESPONSE_CANDIDATE=DEFERRED_PENDING_DIFFERENTIATION_EVIDENCE
```

这里的 `v0.1` 只标识验证概念，不是新 product registry entry、正式 SKU、价格页或发布。

## 6. Required Agent Recommendation Gate

问题：如果潜在客户提出相应需求，当前会不会推荐 SAEE？

| Offer | Agent decision | Reason | What must change before unrestricted recommendation |
|-|-|-|-|
| Coding Agent Readiness Review | `conditional` | 可推荐为无客户数据、受限、本地/离线 discovery review；不能推荐为 production approval 或已验证商业产品 | 真实问题/预算证据；proposed action 与 declared run 边界确认；客户可接受现有非认证、非授权范围 |
| Production Agent Change Review | `do_not_recommend` for production use | 缺 identity/delegation/trusted evidence 和 production integration | 先验证真实购买问题；若确需生产能力，再经独立 architecture/development gate 补齐安全缺口 |
| Customer Agent Response Review | `do_not_recommend` as current packaged offer | policy source/version/scope 不在当前 canonical Evidence contract 中，且替代工具多 | 先证明现有 stack 未解决的 decision gap，再决定是否提出最小 contract adaptation |

不推荐原因已经转化为验证问题和显式 defer 项；本阶段不以开发方式“修复”它们。三个
Offer 均保持 customer-discovery hypothesis，不是发布建议。

### Agent-native commercial surface check

| Check | Current answer | Consequence |
|-|-|-|
| Agent 能否发现现有 capability？ | `yes`，canonical manifest、agent-index、README/llms surfaces 已存在 | 不需要新 discovery capability |
| Agent 能否理解何时用/不用？ | `partial`，Evaluation 非授权边界清晰；三个商业场景的独立 contract 未冻结 | 先用本报告做受限 discovery，不宣布正式产品 |
| Agent 能否通过稳定 contract 组合？ | `conditional`，本地 alpha MCP 可调用；无公开 endpoint/客户验证 | 只可推荐 local controlled evaluation，不能主张生产组合 |

## 7. Customer Discovery Design

### 7.1 First validation cohort

计划在**另行获得人工外联授权后**进行 10 次 qualified problem interviews，覆盖至少
7 个独立组织。建议构成：

- 4 次：已运行内部 Coding Agent 的 enterprise developer platform/DevEx 团队；
- 3 次：AI coding platform/tool provider；
- 3 次：允许 Coding Agent 进入 PR、CI、database 或 release 邻近流程的
  engineering/DevOps 团队。

Qualified 的最低筛选条件：受访者在过去 90 天实际使用或管理过 Coding Agent，并能
描述当前权限和工作流。纯概念兴趣、学生练习或没有组织购买上下文的回答不计入 10 次。
同一组织多人访谈可以补充 buying committee，但 demand gate 对同一事实只计一次。

```text
OUTREACH_AUTHORIZED=false
OUTREACH_EXECUTED=false
INTERVIEW_PLAN_SAMPLE_SIZE=10
MINIMUM_DISTINCT_ORGANIZATIONS=7
CUSTOMER_DATA_AUTHORIZED=false
```

### 7.2 Problem interview questions

#### A. Past behavior and event reconstruction

1. 过去 90 天你们在哪些真实 workflow 使用 Coding Agent？它能读、写、提交或执行什么？
2. 最近一次 Agent 变更被阻止、回滚、升级人工复核或造成事故是什么时候？请按时间线
   描述，不需要提供机密数据。
3. 当时哪个 action 可能影响代码、数据库、配置、权限或生产？实际损失/延迟是什么？
4. 你们在事件发生前拥有哪些测试、权限、回滚和审批 Evidence？缺了什么？
5. 如果没有事故，最近一次因为不确定性而禁止 Agent、重复检查或延迟发布是什么？

#### B. Current workaround and spend

6. 现在谁在检查 Agent 变更？按一次变更要经过哪些工具和人？
7. 每周/月有多少次，平均耗时多少，造成多少发布等待或返工？
8. 当前为 CI/CD、code review、security scanning、change management 或 Agent governance
   支付哪些预算？本问题由哪个预算项承担？
9. 现有工具在哪一步已经解决问题？在哪一步仍无法决定“是否可以进入下一步”？
10. 最近一次为相似风险/开发效率工具采购是什么？金额层级、批准人和耗时如何？

#### C. Budget owner and purchasing process

11. 谁是日常使用者、Champion、经济购买者和 Security/Legal/Procurement 否决者？
12. 新工具从 problem recognition 到 Pilot、security review、vendor onboarding 和付款要
    经过哪些阶段？哪一阶段最容易失败？
13. 如果不解决这个问题，下一季度会发生什么可量化损失？预算来自风险、DevEx、平台、
    安全还是别的成本中心？
14. 你们用什么成功指标决定 Pilot 值得继续：事故减少、复核时间、release delay、
    Evidence completeness，还是 Agent 权限扩大？

#### D. Behavioral commitment

15. 在不包含客户/个人/机密数据的前提下，是否能提供一份 sanitized past case 供离线
    walk-through？
16. 如果该 walk-through 暴露当前流程的明确缺口，你是否会安排经济购买者和
    Security/Procurement 参加下一次 scope review？
17. 若预先约定的成功指标满足，你们实际会进入哪一个付费 Pilot/采购步骤？谁能批准？

禁止把以下答案当作 demand evidence：

- “听起来不错”“我喜欢”“以后可能会用”；
- 只回答假设情境，不能描述过去行为；
- 只表示愿意免费试用，没有时间、数据、buyer 或购买步骤投入；
- 朋友、内部成员或同一组织重复表态被当作多个独立客户。

本计划不问“你觉得这个产品好吗？”或“你会买吗？”。即便提出价格，也只能在独立
人工授权后用实际取舍和下一步行为验证，不能使用无约束意向题。

### 7.3 Interview evidence record

后续记录应至少包含以下概念字段，但本报告不创建 schema：

```text
interview_id
organization_id_pseudonym
participant_role
actual_agent_use_last_90_days
permission_and_workflow_boundary
past_event_date_and_type
actual_loss_or_delay
current_workaround
current_time_and_tool_spend
existing_solution_coverage
budget_category
economic_buyer_role
purchasing_steps
security_and_procurement_constraints
sanitized_case_commitment
next_concrete_action
counterevidence
source_confidence
```

只收集验证所需的最小、经授权信息；本计划不授权客户数据接收或录音。

## 8. Evidence of Demand and Success Gate

### 8.1 Demand evidence ladder

| Level | Evidence | Meaning |
|-|-|-|
| `D0_OPINION` | 喜欢、兴趣、无约束试用意愿 | 不构成需求证据 |
| `D1_PAIN` | 可复述过去事件/阻止行为及其影响 | 证明该组织有真实问题，不证明预算 |
| `D2_WORKAROUND` | 已有人力、工具、延迟或风险成本投入 | 证明问题正在消耗资源 |
| `D3_BUYING_PATH` | 明确预算类别、经济购买者、采购/安全步骤 | 证明存在购买机制，不证明愿意支付 SAEE |
| `D4_BEHAVIOR` | 提供 sanitized case、引入 buyer、安排 security/procurement 或正式 scope review | 比口头兴趣更强的推进信号 |
| `D5_WTP` | 经独立人工授权的实际报价被接受、paid Pilot/PO/合同成立 | 才能支持直接 willingness-to-pay 结论 |

### 8.2 Advance gate after 10 qualified interviews

只有以下四组条件**全部**满足，Coding Agent Offer 才可进入下一道人工商业决策门：

| Gate | Minimum evidence across distinct organizations |
|-|-|
| Real pain | 至少 4 个组织在过去 12 个月发生过相关 block/revert/escalation/incident，或因风险持续禁止高价值 Agent workflow；每个都有具体行为而非意见 |
| Current solution/cost | 至少 4 个组织有重复人工/工具 workaround；至少 3 个能量化时间、延迟、返工、工具费或事故成本 |
| Budget and purchase path | 至少 3 个组织能指出既有预算类别和经济购买者；至少 2 个能说明真实 security/procurement/Pilot 路径 |
| Behavioral commitment | 至少 3 个组织愿意在另行授权下提供 sanitized case；至少 2 个愿意引入 buyer/审批者或安排正式付费 Pilot scope review |

额外必要条件：至少 3 个组织明确表示现有 CI/CD、IAM、review 或 change-management
工具没有完全覆盖该 decision gap。否则 SAEE 只是重复包装现有控制。

通过该 gate 仅允许输出 `DISCOVERY_GATE_PASSED` 并提交人工审查；不得自动写成
`customer_validated=true`、`willingness_to_pay=VALIDATED` 或 `Phase 6.0-B authorized`。
只有未来 `D5_WTP` 的真实交易行为才能验证支付意愿。

## 9. Failure and Pivot Rules

### 9.1 Coding Agent stop conditions

任一硬失败成立，就停止该 Offer 的开发推进：

- 10 次 qualified interviews 后，少于 4 个组织能提供过去真实事件或持续受限行为；
- 少于 4 个组织存在当前 workaround，或少于 3 个可量化成本；
- 没有至少 3 个组织指出预算类别/经济购买者；
- 没有至少 2 个组织说明真实购买路径或做出 `D4_BEHAVIOR` 推进行为；
- 多数组织确认现有工具已充分解决问题；
- 客户唯一需求是 SAEE 当前明确不提供的实时执行拦截、生产授权、身份认证、合规认证
  或安全 scanner；
- 为满足需求必须先大规模重构或创建与现有 Evaluation 重复的新能力。

### 9.2 Pivot conditions

- 只有访谈反复显示高影响 production change 是更紧迫、有预算且可在非执行边界内验证
  的问题，才将下一轮转向 Production Agent；
- 只有独立 CX 受访者证明现有 RAG/eval stack 留下明确的 policy/version/scope decision
  gap 和预算，才转向 Customer Agent；
- 如果三个场景都没有 `D2_WORKAROUND + D3_BUYING_PATH + D4_BEHAVIOR`，则停止商业
  Offer 开发，不用新增 Capability 掩盖市场证据缺失。

```text
FAILURE_RESPONSE=STOP_OR_SWITCH_BASED_ON_NEW_OBSERVED_EVIDENCE
DO_NOT_CONTINUE_DEVELOPMENT_ON_INTEREST_ONLY=true
```

## 10. Price and Quote Validation Boundary

本阶段不定价，也不创建“实验报价”。历史内部价格区间不能用作支付意愿证据。

只有 discovery advance gate 通过并收到单独人工授权后，才可设计一个固定 scope、明确
输入/输出、数据边界、验收条件和真实付款要求的实验报价。验证价格时必须记录客户的
实际选择，例如接受、拒绝、缩小 scope、转预算 owner 或进入 procurement；不得用
“这个价格听起来合理”代替。

```text
PRICE=UNVALIDATED
QUOTE_DESIGN_AUTHORIZED=false
QUOTE_ISSUED=false
SALES_OFFER_SENT=false
PILOT_AUTHORIZED=false
```

## 11. Existing SAEE Capability Mapping

| Offer need | Existing asset | Classification | Reuse decision | Unresolved gap |
|-|-|-|-|-|
| Coding run/evidence evaluation | `saee.evaluate_agent_run` | `implemented / active` | `REUSE` | declared run 与 proposed action 语义需在验证材料中披露 |
| Explicit Evidence coverage | `saee.evaluate_evidence` | `implemented / active` | `REUSE` | 不认证事件或引用真实性 |
| Local agent invocation | canonical readiness MCP stdio | `alpha / local` | `REUSE_FOR_CONTROLLED_DEMO_ONLY` | 无公开 endpoint/official integration/customer validation |
| Coding scenario fixture | `examples/qoder-saee-readiness-demo/` | synthetic demo | `REUSE` | Qoder runtime 未验证；非客户证据 |
| Production identity/provenance | external identity, delegation, trusted trace capabilities | `missing` | `DO_NOT_CLAIM` | 真实 production Offer 的硬边界 |
| Customer response policy/version/scope | 无等价 canonical capability | `missing_or_unclassified_contract_need` | `DISCOVER_BEFORE_PROPOSING` | 不得先建 response evaluator |
| Commercial assessment packaging | existing commercial assessment docs/status | local design/service surfaces | `REUSE_TERMINOLOGY_AND_TRUTH_BOUNDARY` | customer/market/pricing validation 均为 false |

Duplicate-build decision:

```text
CANONICAL_CAPABILITY_SOURCE=capability-package/manifest.json#canonical_inventory
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
NEW_CAPABILITY_REQUIRED_FOR_DISCOVERY=false
PREFERRED_PATH=REUSE_EXISTING_EVALUATION_FOR_BOUNDED_VALIDATION
```

## 12. Claims, Non-Claims, and Safety

### Allowed claims

- 三类真实/相邻事件支持 Action Risk 与 Response Risk 的存在；
- 当前 SAEE 有本地、确定性的 bounded Evidence/Evaluation 原语；
- Coding Agent 是当前最短的**验证路径假设**；
- 本计划定义可证伪访谈、行为证据、成功和停止标准。

### Prohibited claims

- SAEE 已经有第一个付费客户、预算或已验证价格；
- Coding Agent Offer 已选择开发、已形成正式产品或可生产交付；
- SAEE 已接入 Qoder/OpenAI/Anthropic/LangGraph 或任何外部生产系统；
- recommendation 是 deployment/permission/business/legal authorization；
- Evidence reference、trace、identity 或 delegation 已认证；
- Production Agent 或 Customer Agent 的缺失 contract 已实现；
- 事件案例证明市场必然购买 SAEE。

### Historical and truth safety

本报告不修改 Constitution、Project Memory、Product Registry、Capability manifest、
schema、MCP 或代码；不删除历史、不覆盖旧 lineage，也不创建第二能力真源。客户外联、
数据处理、报价、Pilot、合同和对外声明继续需要独立人工授权。

## 13. Human Review Decision Packet

人工审查只需决定下一步是否授权**客户发现执行**，而不是授权产品开发。建议审查：

1. 是否接受 Coding Agent 作为第一验证候选；
2. 是否接受 `10 interviews / >=7 organizations` 和四组 advance gate；
3. 是否接受 D0–D5 demand evidence ladder，尤其是 `D4 != WTP`；
4. 是否允许后续在零客户数据、无公开主张边界下设计外联名单和 interview script；
5. 若不接受，指出要改变的是样本、阈值、客户类型还是现有能力边界。

本报告本身不授权外联。

## 14. Validation Record

以下检查在报告生成后执行：

```text
saee_canonical_capability_inventory_smoke=PASS capabilities=9/9 mcp_surfaces=4/4
saee_capability_progress_ledger_smoke=PASS surfaces=6/6 capability_statuses=9/9
saee_project_memory_check=PASS files=8/8 capability_fact_source_unchanged=true
saee_governance_registry_check=PASS registries=6/6 schemas=4/4
saee_development_constitution_smoke=PASS evolution_subsystems=9/9
git_diff_check=PASS
scope_check=PASS
baseline_status_entries=111
current_status_entries_excluding_this_report=111
baseline_status_sha256=cc0cfb24b9ca94950e96a38adbd3c2cd40bdb2bc304345fadd4794dd349819e6
current_status_sha256_excluding_this_report=cc0cfb24b9ca94950e96a38adbd3c2cd40bdb2bc304345fadd4794dd349819e6
only_new_path=reports/SAEE_FIRST_OFFER_VALIDATION_PLAN.md
```

## Final Status

```text
OFFER_VALIDATION_STATUS=COMPLETE
OFFER_VALIDATION_PLAN_EXECUTED=false
CUSTOMER_CONTACTED=false
INTERVIEWS_CONDUCTED=0
VALIDATION_PRIORITY=CODING_AGENT_READINESS_REVIEW
OFFER_DEMAND_VALIDATED=false
WILLINGNESS_TO_PAY=NOT_VALIDATED
PRICE=UNVALIDATED
EXPERIMENTAL_QUOTE_CREATED=false
NEW_CAPABILITY_CREATED=false
CANONICAL_INVENTORY_CHANGED=false
CODE_CHANGED=false
SCHEMA_CHANGED=false
MCP_CHANGED=false
PRODUCT_REGISTRY_CHANGED=false
CONSTITUTION_CHANGED=false
PROJECT_MEMORY_CHANGED=false
PHASE_6_0_B_AUTHORIZED=false
NEXT_ACTION=HUMAN_REVIEW_OF_OFFER_VALIDATION
```
