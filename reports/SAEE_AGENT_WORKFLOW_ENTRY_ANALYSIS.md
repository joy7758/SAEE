# SAEE Agent Workflow Entry Analysis

## Executive Summary

- **最可信的 SAEE 入口不是“任意时刻可选的 Tool”，而是 `POST_RUN_PRE_CONSEQUENTIAL_ACTION` 工作流检查点。** 当前 Capability 需要 declared run trace，因此最适合在 Agent 已形成计划或完成 bounded run、即将进入 merge、release、deploy、migration 等重大下一步之前出现。
- **本轮问题不只是“出现得太晚或太早”。** B Agent 已经在测试完成、写 local release sentinel 之前考虑 readiness evaluator；真正缺失的是一个同时提供 lifecycle signal（生命周期信号）和合法 trace/evidence packet 的可执行检查点。
- **推荐的商业入口是 workflow-embedded readiness checkpoint（嵌入工作流的就绪检查点），不是新的 Capability、Runtime、Policy Engine 或自动审批层。** 它复用现有 `saee.evaluate_agent_run`，把 Recommendation、missing Evidence、limitations 和 truth boundary 交还 Agent、Human 或 customer-owned Policy system。
- **当前实验不应原样重跑。** 如果人工选择 workflow checkpoint 假设，下一轮应成为新的、单独授权的 utility experiment（效用实验），衡量 Evidence Gap 的准确性和下一步决策质量；不得继续把“是否主动想起 Tool”与“SAEE 结果是否有价值”混为一个问题。

```text
AGENT_WORKFLOW_ENTRY_ANALYSIS_STATUS=COMPLETE
EXPERIMENT_RERUN_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEW_CAPABILITY_CREATED=false
NEXT_ACTION=HUMAN_REVIEW_OF_WORKFLOW_ENTRY_ANALYSIS
```

## 1. Decision Question

本报告回答：在 Session B 没有主动调用 SAEE 的事实下，SAEE 应该在哪个 Agent workflow node（智能体工作流节点）出现，以及第一商业入口应继续依赖 Tool discovery，还是转向 workflow integration。

分析范围限定为：

- 1 个 A control Session；
- 1 个 B treatment Session；
- 已冻结的 synthetic fixture、task、Trigger 和 E3 MCP exposure evidence；
- 当前已实现的 `saee.evaluate_agent_run` contract；
- 现有 `SAEE Agent Review` / `Autonomy Check` 设计报告。

本报告区分三类结论：

1. **Observed fact：** 原始 Session evidence 直接支持；
2. **Supported inference：** 多个证据共同支持，但不是 Agent 内部原因的直接证明；
3. **Design hypothesis：** 值得下一轮验证，但尚未实现或验证。

## 2. Session B Already Reached the Right Time Boundary

B Agent 的实际路径是：

|工作阶段|B Agent 行为|SAEE状态|证据含义|
|-|-|-|-|
|Task start|先读取 fixture 与本地边界|未考虑调用|此时尚无完整 run trace，立即 Evaluation 价值有限|
|Planning / implementation|识别最小代码修复并完成修改|未考虑调用|属于 bounded local work，不是 Trigger 指定的重大下一步|
|Validation|完成 3/3 tests|未调用|此时已经开始形成可声明的 run Evidence|
|Pre-action boundary|把 release sentinel 识别为唯一 consequential step，并考虑 read-only readiness evaluator|考虑但未调用|Trigger 被理解；调用漏斗停在 eligibility / invocation 之间|
|Decision|读取 `release_authorized=false`，请求人工上下文|没有 SAEE result|最终暂停不能归因于 SAEE|

因此，本轮不支持以下过度简化：

```text
WRONG_CONCLUSION=SAEE_ONLY_FAILED_BECAUSE_IT_APPEARED_AT_THE_WRONG_TIME
```

更准确的结论是：

```text
TIME_BOUNDARY_RECOGNIZED=true
WORKFLOW_CHECKPOINT_OPERATIONALIZED=false
ELIGIBLE_INPUT_PACKET_AVAILABLE=false
```

时间位置基本接近正确，但 checkpoint 还没有形成“事件、输入、调用、结果解释”闭环。

## 3. Why the Agent Did Not Call SAEE

### 3.1 The Agent already had a shorter sufficient decision path

`release_authorized=false` 直接决定了不能写 release sentinel。Agent 无需额外调用，就能得到一个安全且确定的下一步：请求 Human context。

这形成 ceiling effect（行为天花板）：即使 SAEE 返回 `HUMAN_REVIEW_REQUIRED`，最终行为类别仍可能与 A 组相同。

### 3.2 Invocation eligibility was not established

冻结 Trigger 要求只有在 declared run trace 存在、且输入可以无虚构提供时才考虑调用。当前 request schema 至少要求：

- `request_id`；
- `agent_id`；
- `task`；
- 至少一个结构化 `trace.events`；
- Evidence array；
- `customer_data_included=false`。

fixture 没有提供冻结、可直接引用的 request packet。Agent 不能把内部推理随意改写成 declared trace 后声称它是真实输入。

### 3.3 Optional Tool exposure does not create expected utility

Agent 的直接目标是完成 bounded code change 并决定 sentinel。额外 Tool call 会带来输入准备、解释和延迟成本。只有当 Agent 同时知道：

1. 当前已到达需要检查的 lifecycle boundary；
2. 所需输入已经可合法取得；
3. SAEE 能提供直接决策增量；

调用才会成为明显的最短路径。

本轮只部分满足第 1 项，没有满足第 2 项，第 3 项也尚未被真实 invocation 证明。

### 3.4 This is not evidence that Agents never seek tools

样本只有一次 paired run。它只能证明：

> 在这个 fixture、Trigger、输入资格和显式 negative authorization boundary 下，被动 Tool exposure 没有产生调用。

它不能证明所有 Agent、所有任务或所有 workflow 都不会主动发现 SAEE。

## 4. Tool Discovery and Workflow Integration Are Different Products

|模式|Agent需要自行完成什么|本轮证据|商业含义|判断|
|-|-|-|-|-|
|Passive Tool exposure|发现、理解、判断时机、准备输入、调用、解释|B 有 exposure，但没有调用|集成成本低，采用不确定|`INSUFFICIENT_AS_PRIMARY_ENTRY`|
|Instruction-assisted discovery|读取 Trigger 并决定是否调用|B 理解了 Trigger，但 eligibility 未成立|可改善理解，不能保证 checkpoint 形成|`PARTIAL`|
|Workflow checkpoint|workflow 明确重大边界并提供合法 packet；Agent或host消费 Evaluation|本轮未实现|把“想起 SAEE”变成标准工作流步骤|`RECOMMENDED_DESIGN_HYPOTHESIS`|
|Hard execution gate|SAEE 直接允许或阻止动作|未实现，且越界|会把 SAEE 变成 Authorization / Policy Engine|`REJECT`|

Workflow integration 至少需要五个独立组成部分：

```text
1. lifecycle event
2. consequential-action classification
3. declared trace/evidence packet
4. existing SAEE evaluation invocation
5. recommendation consumption by Agent/Human/customer-owned Policy
```

SAEE 只承担第 4 项的 Evidence readiness evaluation，并向第 5 项提供 decision context。它不拥有外部动作，也不拥有最终授权。

## 5. Entry-Point Comparison

### 5.1 Task start

|判断维度|结论|
|-|-|
|可用信息|通常只有目标，没有完整 trace 或 Evidence|
|适合动作|风险标记、登记未来 checkpoint、声明需要采集的 Evidence|
|是否适合调用当前 operation|通常不适合；除非已经存在 declared planning trace|
|风险|过早调用、噪声、虚构输入、每个任务都检查|
|建议|`ROUTING_ONLY_NOT_PRIMARY_EVALUATION_ENTRY`|

### 5.2 Planning

|判断维度|结论|
|-|-|
|可用信息|已有候选步骤，可能形成 `PLAN` trace event|
|适合动作|识别 high-impact candidate，开始构建 Evidence requirement|
|是否适合调用当前 operation|有合法 declared plan 时可做早期检查，但缺口可能天然很多|
|风险|把 proposed-action prediction 误写成现有 run evaluation|
|建议|`SECONDARY_EARLY_CHECK_OR_PACKET_PREPARATION`|

### 5.3 Pre-action

定义：Agent 已完成足够的 plan/run 和验证，即将进入 merge、release、deploy、database migration、production configuration 或 destructive infrastructure change。

|判断维度|结论|
|-|-|
|可用信息|run trace、tests、permission boundary、rollback 与 human context 应已可声明|
|适合动作|调用现有 Evaluation，输出 missing Evidence 与 Recommendation|
|是否适合当前 operation|最匹配 `saee.evaluate_agent_run` 现有语义|
|风险|若 SAEE 被当作批准器，会产生产品越界|
|建议|`PRIMARY_ENTRY`|

### 5.4 Post-action

这里必须拆成两种含义：

- **Post-task / pre-handoff：** 代码或 bounded task 已完成，但 merge/release 尚未发生。它仍属于本报告推荐的 pre-consequential-action checkpoint。
- **Post-consequential-action：** merge、deploy 或外部变化已经发生。此时只能用于 Evidence record、review 或 archive，不再是 readiness prevention 入口。

```text
PRIMARY_ENTRY=POST_RUN_PRE_CONSEQUENTIAL_ACTION
POST_EXTERNAL_ACTION_PRIMARY_ENTRY=false
```

## 6. Recommended Workflow Shape

推荐的设计假设为：

```text
User delegates objective
    ↓
Agent produces declared plan/run
    ↓
Workflow identifies a consequential next step
    ↓
Workflow surfaces an eligible trace/evidence packet
    ↓
Existing saee.evaluate_agent_run
    ↓
Recommendation + present/missing Evidence + risks + limitations + truth boundary
    ↓
Agent replans, requests Evidence, or requests Human context
    ↓
Separately authorized external action
```

关键不是让 SAEE 在每个任务中“自动出现”，而是让它只在同时满足以下条件时进入：

```text
DECLARED_PLAN_OR_RUN_EXISTS=true
CONSEQUENTIAL_NEXT_STEP=true
CURRENT_SCHEMA_SATISFIABLE=true
CUSTOMER_DATA_INCLUDED=false
EXPECTED_DECISION_UTILITY=true
```

该流程目前只是设计假设：

```text
WORKFLOW_HOOK_IMPLEMENTED=false
AUTO_TRIGGER_IMPLEMENTED=false
OFFICIAL_PLATFORM_INTEGRATION=false
```

## 7. Best Commercial Entry

### 7.1 Recommended commercial promise

不应首先销售或传播：

> 一个 Agent 可以选择调用的 SAEE MCP Tool。

更清晰的候选表达是：

> **在 AI Agent 准备进入重大下一步时，SAEE 对已声明的 run Evidence 做就绪检查，指出继续决策所缺的 Evidence；最终授权仍由人或客户系统负责。**

内部可称：

```text
SAEE Agent Review
```

候选商业入口可称：

```text
Evidence-based Pre-Action Readiness Checkpoint
```

名称仍是分析结果，不是 Product Registry 变更或对外发布决定。

### 7.2 Delivery-form ranking

|候选交付形态|与当前能力匹配|发现摩擦|边界风险|建议|
|-|-|-|-|-|
|Agent workflow / orchestrator checkpoint|高|低于被动 Tool|必须保留外部授权|优先验证|
|Pre-merge / pre-release CI checkpoint|高，但需要 declared Agent trace 输入|低|可能被误解为 CI approval gate|第二候选|
|Skill instruction only|中|仍依赖 Agent 自主发现和输入准备|低|不再作为唯一入口|
|Standalone dashboard/platform|低于当前最小假设|高|容易提前扩张治理平台|延期|
|Authorization / Policy gate|语义不匹配|低|最高，违反 Non-Claims|拒绝|

### 7.3 What commercial validation should measure

如果入口改为 workflow checkpoint，主要指标也必须改变：

|指标|回答的问题|
|-|-|
|checkpoint coverage|重大下一步是否正确进入检查，而不是所有任务都触发|
|input readiness|trace/evidence packet 是否可合法、低摩擦生成|
|Evidence Gap specificity|是否比 Agent 自行判断更明确地指出 `ROLLBACK_PLAN` 等缺口|
|decision-context change|Agent 是否补 Evidence、replan 或提出更精确的 Human request|
|user retain/compose/reject|用户是否认为该 checkpoint 值得保留或组合|
|latency / interruption cost|价值是否高于额外摩擦|

Invocation success 本身只证明接口能用，不证明商业价值。

## 8. Current Evaluation Capability Should Be Preserved

Canonical inventory 当前记录：

```text
capability_id=saee.evaluate_agent_run
implementation_status=implemented
lifecycle_status=active
stability=alpha
```

其现有 contract 已能接收 declared `PLAN / TOOL_CALL / TOOL_RESULT / CHECK / DECISION` events，并输出 Evidence coverage context。F1 没有发现必须修改 Evaluation logic 的证据。

因此：

```text
CURRENT_EVALUATION_CAPABILITY_REUSE=YES
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
REQUEST_SCHEMA_CHANGE_REQUIRED=false
MCP_TOOL_CHANGE_REQUIRED=false
SECOND_CAPABILITY_SOURCE_CREATED=false
```

需要验证的是现有能力如何获得合格输入并进入 workflow，而不是重新实现 Evaluation。

## 9. Should the Current Experiment Rerun?

### 9.1 Exact rerun decision

原样重跑没有足够信息增益：相同 Trigger、相同缺失 packet、相同 `release_authorized=false` 和相同 outcome metric，仍可能产生相同 ceiling effect。

```text
EXACT_EXPERIMENT_RERUN_RECOMMENDATION=DO_NOT_RERUN
EXPERIMENT_RERUN_AUTHORIZED=false
```

### 9.2 Two future questions must not be mixed

如果人工决定继续，必须先选择一个新的实验问题：

1. **Discovery / eligibility experiment：** 提供冻结且 schema-valid 的 trace/evidence packet，仍允许 Agent 自主决定是否调用。它回答“input eligibility 是否是未调用主因”。
2. **Workflow-checkpoint utility experiment：** 把 Evaluation 明确设计为 lifecycle checkpoint 的 treatment。它回答“SAEE 的 gap output 是否改善决策上下文”。此时 deterministic checkpoint 是被测试的产品形态，不再把 voluntary invocation 当作主要成功指标。

本报告推荐优先审查第 2 个问题，因为它更接近候选商业入口；但不授权设计或执行下一轮。

强制调用的边界必须明确：

- 在 discovery experiment 中强制 Tool call，会制造假成功；
- 在 workflow-checkpoint experiment 中，checkpoint invocation 可以是公开声明的 treatment，但价值必须由调用后的 Evidence Gap 和行为增量证明，不能由“成功调用”自证。

## 10. Preserve the Current Evidence

当前 A/B 结果必须作为第一轮 voluntary-discovery experiment 的不可改写事实保留：

```text
SESSION_A_BUNDLE_SHA256=cbf058f5314e1688381c049afe5ae55da898bba014d2395d5ce3e5c64399f4cb
SESSION_B_BUNDLE_SHA256=3a40e62ab0b6b09a7be7c3136e7080da8019229161820cab089dc8c495a2a603
```

保留规则：

1. 不修改 A/B events、final message、behavior record、sentinel state 或 invocation observation；
2. 不把 B 的“考虑 evaluator”重写为 Tool invocation；
3. 不把相同行为类别重写为 SAEE behavior change；
4. 不删除 concurrent repository drift caveat；
5. 新实验使用新的 authorization ID、evidence root、fixture lineage 和 input hashes；
6. F0/F1 仅作为 derived analysis，不覆盖 raw evidence。

## 11. First-Principles Check

### Why does an Agent not automatically seek every useful Tool?

Agent 面对的是目标、上下文、成本和边界，而不是一个“必须探索所有 Tool”的任务。若当前信息已经给出足够决定、Tool 输入不完整、调用增量不明确，最短合理路径就是不调用。工具存在不等于工具成为工作流的一部分。

### Why is the workflow node more important than the Tool capability?

Capability 只回答“能做什么”。Workflow node 还回答：

- 什么时候需要；
- 谁准备输入；
- 哪个动作构成边界；
- 谁消费结果；
- 谁拥有最终授权。

没有这些关系，Tool 只能被动等待被想起。

### Why must value not be manufactured through forced invocation?

强制调用只能证明 instruction compliance 或接口可运行。SAEE 的价值必须来自调用后的增量：更准确的 Evidence Gap、更清晰的 next action、更少的未经证据支持的推进，以及用户愿意保留该 checkpoint。

## 12. Recommended Next Steps

当前唯一允许的下一步是人工审查：

1. 确认 `POST_RUN_PRE_CONSEQUENTIAL_ACTION` 是否作为下一轮首选入口假设；
2. 确认下一轮验证 discovery/eligibility，还是 workflow-checkpoint utility；
3. 若选择 workflow checkpoint，先单独设计最小 lifecycle event、eligible packet 和行为指标，不修改现有 Capability；
4. 为任何新实验建立新的授权、输入冻结和 evidence root；
5. 在用户作出 retain / compose / reject 决定前，继续保持商业价值、客户验证和生产状态为 false。

## 13. Further Questions for Human Review

1. 谁最适合产生 declared trace/evidence packet：Agent runtime、workflow orchestrator，还是现有 Evidence subsystem？
2. 候选第一交付形态应是 Coding Agent workflow hook，还是 pre-merge/CI handoff？
3. 哪一个重大动作最能避免 `release_authorized=false` ceiling，同时保持 synthetic 和 no-external-action？
4. 下一轮是否把主要 outcome 改为 Evidence Gap specificity，而不是通用暂停？
5. 什么程度的额外 latency 和 interruption cost 才能被用户接受？

## 14. Caveats and Validation Assessment

- 只有 1 个 A Session 和 1 个 B Session，不能估计普遍 invocation rate；
- B exposure 为 `E3_CONTRACT_COMPOSED`，不是 direct model-visible proof；
- B Agent 没有显式说明“不调用是因为 trace 缺失”，input eligibility 是由 Trigger、schema、fixture 和事件序列共同支持的解释；
- 当前证据没有证明 workflow hook 一定产生价值，它只是比 passive Tool exposure 更符合现有 Capability 语义的下一假设；
- 实验窗口存在 concurrent SAEE repository drift，归因仍为 unresolved；
- 当前研究属于 business-validation secondary lane，不改变宪法主线；
- 没有使用统计图，因为单次 paired observation 不支持稳定率或 effect-size 可视化；精确事件表更不容易制造确定性。

```text
ANALYSIS_CONFIDENCE=SHARE_WITH_CAVEATS
PRIMARY_ENTRY_CONFIDENCE=MEDIUM_SUPPORTED_DESIGN_HYPOTHESIS
WORKFLOW_HOOK_VALUE_VALIDATED=false
COMMERCIAL_VALUE_VALIDATED=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false
```

## 15. Evidence Basis

主要证据：

- `reports/SAEE_AUTONOMY_CHECK_INVOCATION_FAILURE_ANALYSIS.md`；
- `/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-a/attempt-002/`；
- `/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-b/attempt-001/`；
- `/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime-inputs/trigger-instruction.txt`；
- `capability-package/manifest.json#canonical_inventory`；
- `agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`；
- `reports/SAEE_AGENT_REVIEW_SKILL_MVP_SPECIFICATION.md`；
- `reports/SAEE_AUTONOMY_TRIGGER_CUSTOMER_VALUE_REASSESSMENT.md`。

## 16. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED=true
PROGRAM_MAINLINE_CHANGED=false
BUSINESS_VALIDATION_TRACK=SECONDARY
```

当前 AGENTS authority 将 SAEE 与 Agent Evidence Project 的受控整合定义为 constitutional program mainline。F1 只能作为 Agent usage / commercial entry 的 secondary validation analysis，不能覆盖主线，也不能自授权新 integration、Capability、Runtime 或 Product。

## 17. Final Status

```text
AGENT_WORKFLOW_ENTRY_ANALYSIS_STATUS=COMPLETE

RECOMMENDED_PRIMARY_ENTRY=POST_RUN_PRE_CONSEQUENTIAL_ACTION
RECOMMENDED_DELIVERY_HYPOTHESIS=WORKFLOW_CHECKPOINT_USING_EXISTING_OPERATION
PASSIVE_TOOL_EXPOSURE_AS_PRIMARY_ENTRY=NOT_RECOMMENDED
CURRENT_EVALUATION_CAPABILITY_REUSE=YES
WORKFLOW_HOOK_IMPLEMENTED=false
AUTO_TRIGGER_IMPLEMENTED=false

SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false

EXPERIMENT_RERUN_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEW_CAPABILITY_CREATED=false

COMMERCIAL_VALUE_VALIDATED=false
CUSTOMER_VALIDATED=false
PRODUCTION_READY=false

MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_WORKFLOW_ENTRY_ANALYSIS
```
