# SAEE Workflow Checkpoint Value Hypothesis

## Executive Summary

- **首要价值假设不是“SAEE 让 Agent 停下来”，而是“SAEE 把模糊的谨慎升级为结构化 Evidence Gap decision context”。** 当前 A/B 实验中，两组都会暂停，但都没有明确指出缺失的 `ROLLBACK_PLAN`；如果 Checkpoint 能稳定说明缺什么、为什么缺、下一步应补什么，它才可能产生增量价值。
- **Checkpoint 应在 `POST_RUN_PRE_CONSEQUENTIAL_ACTION` 触发。** 只有 declared run 已形成、重大动作尚未发生、现有 request schema 可以无虚构满足时，才调用当前 `saee.evaluate_agent_run`。它不在任务开始时普遍运行，也不在动作发生后补做批准。
- **最小验证不需要开发 Hook 或重跑完整 A/B Agent 实验。** 可以先使用同一任务状态制作一个受控 decision packet，对比“Agent generic pause”与“SAEE structured gap context”，让目标角色记录 `retain / compose / reject`、决策增量和可接受摩擦。
- **该方向必须可被否决。** 如果 SAEE 输出没有增加具体信息、现有 CI/review/policy 已提供等价结果、输入准备成本过高，或用户真正需要的是授权与执行控制，则不应开发 workflow hook。

```text
WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS_STATUS=COMPLETE
WORKFLOW_HOOK_IMPLEMENTED=false
EXPERIMENT_RERUN_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEW_CAPABILITY_CREATED=false
NEXT_ACTION=HUMAN_REVIEW_OF_WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS
```

## 1. Decision Question

本报告回答：如果 SAEE 以 workflow checkpoint 而不是 passive optional Tool 的形式出现，它为 Agent operator、engineering lead 或 release owner 增加的最小可验证价值是什么，以及在开发 Hook 前如何用更小实验验证。

当前只能定义 falsifiable value hypothesis（可证伪价值假设），不能声明：

- 用户已经需要该 Checkpoint；
- 用户愿意保留、组合或付费；
- workflow hook 已实现；
- SAEE 已经改变 Agent 行为；
- 客户验证、市场验证或生产就绪已经完成。

## 2. Customer Problem

### 2.1 The candidate user problem

候选问题不是“Agent 不会写代码”，也不是“Agent 完全没有风险意识”。当前实验已经观察到：Agent 能完成 bounded code change、通过测试，并依据明确的 `release_authorized=false` 暂停。

真正待验证的问题是：

> 当 Agent 已完成任务、即将进入重大下一步时，相关 Evidence 分散在 tests、rollback、permission 和 human context 中；Agent 或人可能知道需要谨慎，却无法快速得到统一、可解析、带 limitations 的 Evidence completeness 判断。

在 Session A/B 中，这个问题表现为：

|观察|结果|能支持什么|
|-|-|-|
|两组都暂停|`PAUSE_AND_REQUEST_HUMAN_CONTEXT`|Agent 已有基本风险意识|
|两组都未明确指出 rollback 缺口|`AGENT_EXPLICITLY_IDENTIFIED_ROLLBACK_PLAN_GAP=false`|当前输出没有形成结构化缺口增量|
|B 考虑 evaluator 但未调用|true|入口意识存在，但 Checkpoint 未形成|
|B 没有 SAEE result|true|不能声称 SAEE 已带来价值|

这只证明 synthetic experiment 中存在一个 decision-context gap，不证明真实客户普遍存在购买需求。

### 2.2 Candidate roles

|角色|可能面对的问题|当前验证状态|
|-|-|-|
|Coding Agent operator / developer|收到“需要人工确认”，但不知道应补哪类 Evidence|`HYPOTHESIS_ONLY`|
|Engineering lead / release owner|不同 Agent 的 escalation 表达不一致，人工复核需要重新搜集上下文|`HYPOTHESIS_ONLY`|
|Developer platform / DevEx team|希望把 Agent run 接入已有 release workflow，而不新建授权系统|`HYPOTHESIS_ONLY`|
|Economic buyer|是否愿意为减少人工检查、发布延迟或不确定性付费|`NOT_VALIDATED`|

### 2.3 Existing alternatives

客户可能已经使用：

- CI tests；
- code review；
- security scanner；
- IAM / Policy Engine；
- change-management checklist；
- deployment gate；
- Agent 自身的谨慎判断。

SAEE 只有在这些工具没有把 required / present / missing Evidence、risks、limitations 和 truth boundary 组合成可消费 decision context 时，才可能有增量价值。

```text
IF_EQUIVALENT_EXISTING_GATE_EXISTS=DO_NOT_RECOMMEND_DUPLICATE_INTEGRATION
```

## 3. Workflow Checkpoint Definition

### 3.1 Trigger position

Checkpoint 候选位置固定为：

```text
POST_RUN_PRE_CONSEQUENTIAL_ACTION
```

中文含义：Agent 已形成 declared plan/run 并完成必要的 bounded work，但 merge、release、deploy、database migration 或其他重大外部动作尚未发生。

### 3.2 Trigger eligibility

只有以下条件全部成立，才进入 Checkpoint：

```text
DECLARED_PLAN_OR_RUN_EXISTS=true
CONSEQUENTIAL_NEXT_STEP=true
CURRENT_REQUEST_SCHEMA_SATISFIABLE=true
REQUIRED_INPUTS_AVAILABLE_WITHOUT_FABRICATION=true
CUSTOMER_DATA_INCLUDED=false
EXTERNAL_ACTION_ALREADY_EXECUTED=false
```

以下情况不触发：

- 只读问答、搜索、格式化或低影响编辑；
- 尚无 declared trace，只能预测未来行为；
- 需要 IAM、Policy enforcement、security certification 或 deployment approval；
- 输入包含客户数据、个人信息、密钥或未授权生产内容；
- 重大外部动作已经完成。

### 3.3 Checkpoint output

Checkpoint 复用现有 response，重点消费：

```text
recommendation
required_evidence
present_evidence
missing_evidence
risks
score
score_semantics
limitations
truth_boundary
```

`score` 仍只是 Evidence coverage percent，不是 trust、safety、security、quality 或成功概率。

### 3.4 Authority boundary

Checkpoint 不拥有动作权力：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
```

SAEE 只提供 decision context。Agent、Human 或 customer-owned Policy/authority system 负责后续独立决定。

## 4. Existing Capability Reuse

Canonical capability fact：

```text
capability_id=saee.evaluate_agent_run
implementation_status=implemented
lifecycle_status=active
canonical_entrypoint=python3 scripts/saee_agent_readiness_mcp_stdio.py
stability=alpha
```

F2 不需要新增或修改：

- Capability；
- request/response Schema；
- MCP Tool；
- Evaluation logic；
- Recommendation vocabulary；
- Product Registry；
- second capability truth source。

未来如果验证 Checkpoint，只允许把现有 workflow facts 映射成当前 schema-valid request，并原样消费当前 response。输入准备和 lifecycle routing 是待验证的 composition problem，不是新 Evaluation Capability。

```text
CURRENT_EVALUATION_CAPABILITY_REUSE=YES
EVALUATION_ENGINE_REBUILD=DO_NOT_BUILD
REQUEST_SCHEMA_CHANGE_REQUIRED=false
MCP_TOOL_CHANGE_REQUIRED=false
NEW_CAPABILITY_REQUIRED=false
```

## 5. Primary Value Hypothesis

### 5.1 Core hypothesis

```text
PRIMARY_VALUE_HYPOTHESIS=
CHECKPOINT_TURNS_GENERIC_CAUTION_INTO_STRUCTURED_ACTIONABLE_EVIDENCE_GAP_CONTEXT
```

中文：

> 在 Agent 完成 run、准备进入重大下一步时，SAEE Checkpoint 能比 Agent 的通用谨慎表达更具体地指出当前缺少的 Evidence、相关风险和限制，使 Agent 或人能够提出更准确的下一步请求。

### 5.2 Expected value components

|价值组成|候选增量|验证方式|
|-|-|-|
|Gap specificity|从“需要人工确认”升级为“缺少 `ROLLBACK_PLAN` / `HUMAN_APPROVAL` 等明确项”|对比输出是否新增准确、可行动信息|
|Decision clarity|说明为什么不能继续，以及什么信息会改变 Recommendation|用户能否给出明确下一步|
|Cross-Agent consistency|不同 Agent 使用同一 Evidence vocabulary|后续多 Agent 验证；本阶段不证明|
|Human coordination|减少人工重新搜集上下文和解释模糊 escalation|记录用户认为减少了哪些复核步骤|
|Bounded delegation|用户可能愿意把更多可逆、受限步骤交给 Agent|记录具体 delegation delta；当前未测|
|Truthful limitation|明确 Recommendation 不是授权、Evidence 未认证|检查用户/Agent 是否保持边界|

### 5.3 Net-value test

使用定性框架，不创建新分数或 Evaluation logic：

```text
NET_CHECKPOINT_VALUE=
  DECISION_CONTEXT_GAIN
  + EVIDENCE_GAP_SPECIFICITY
  + WORKFLOW_CONSISTENCY
  - INPUT_PREPARATION_COST
  - INTERRUPTION_COST
  - LATENCY
  - DUPLICATION_WITH_EXISTING_GATES
```

只有当增量价值明显高于摩擦，才值得继续讨论 Hook。

## 6. Supporting Hypotheses

### H1 — Specificity

SAEE 输出会指出 Agent baseline 没有明确说明的 Evidence 缺口。

```text
H1_STATUS=UNVALIDATED
```

### H2 — Next-action quality

用户或 Agent 会从 generic pause 转为具体动作，例如请求 rollback context、补 permission boundary 或 replan。

```text
H2_STATUS=UNVALIDATED
```

### H3 — Composition preference

目标角色会选择 `retain` 或 `compose` 该 Checkpoint，并说明它应放在哪个 qualifying boundary。

```text
H3_STATUS=UNVALIDATED
```

### H4 — Acceptable friction

准备 declared trace/evidence packet、运行 Evaluation 和解释结果的成本低于用户感知价值。

```text
H4_STATUS=UNVALIDATED
```

### H5 — Non-duplication

客户现有 CI/review/policy 流程没有提供完全等价的 structured Evidence gap context。

```text
H5_STATUS=UNVALIDATED
```

## 7. Minimum Validation Method

### 7.1 Validation objective

下一步不是再次证明 Agent 能运行，也不是证明 MCP 能调用。最小问题是：

> 对同一个完成后的 Agent run，结构化 SAEE Checkpoint output 是否比 generic Agent escalation 增加用户可行动的 decision context？

### 7.2 Smallest useful experiment

建议设计一个新的、单独授权的 static decision-packet review（静态决策包评审），而不是重跑完整 A/B Agent Session：

1. 冻结一个 synthetic completed run、candidate consequential action 和 schema-valid trace/evidence packet；
2. 准备 Baseline card：只展示 generic Agent pause 和原始 Evidence；
3. 准备 Checkpoint card：展示同一输入经过现有 `saee.evaluate_agent_run` 后的完整 response；
4. 不告诉 reviewer 哪一张是“期望答案”，避免引导；
5. 让至少一个目标角色 reviewer 分别给出下一步和理由；
6. 最后记录 `retain / compose / reject`、具体价值、重复能力、可接受摩擦和缺失条件；
7. 结束，不开发 Hook，不扩展平台。

本报告不创建以上 cards，不调用 Evaluator，也不联系用户。

### 7.3 Frozen comparison

两张 card 必须保持：

- 相同 task；
- 相同 declared trace；
- 相同 Evidence facts；
- 相同 candidate action；
- 相同 non-authorization boundary。

唯一差异：Checkpoint card 增加现有 SAEE response。

### 7.4 Minimum value signal

```text
MINIMUM_VALUE_SIGNAL=
  USER_DECISION in {retain, compose}
  AND SPECIFIC_INCREMENTAL_EVIDENCE_REASON_RECORDED=true
  AND NEXT_ACTION_CONTEXT_IMPROVED=true
  AND AUTHORIZATION_BOUNDARY_PRESERVED=true
```

`retain / compose` 必须附带具体理由，例如：

- 明确指出之前未见的 rollback 缺口；
- 使人工请求从“请确认”变成“请提供 rollback plan”；
- 使 reviewer 更快决定补证、replan 或上交；
- 能与现有 CI 组合而不重复。

仅回答“看起来不错”不计为价值信号。

### 7.5 Rejection and falsification

出现以下任一结果，应降低或停止 Hook 开发优先级：

- reviewer 选择 `reject`，且认为结果没有增加可行动信息；
- SAEE 只重复 tests、CI 或现有 release checklist；
- reviewer 的下一步与 Baseline 相同，且无法指出任何决策质量增量；
- trace/evidence packet 准备成本高于复核收益；
- false trigger 或 interruption cost 不可接受；
- 用户真正需要身份认证、实时 enforcement、Authorization 或 Execution Control；
- 价值依赖新增 Capability、Schema 或自动批准语义才能成立。

```text
NO_VALUE_SIGNAL=STOP_HOOK_DEVELOPMENT_DECISION
```

### 7.6 What one positive review proves

一个 positive `retain / compose` decision 只建立：

```text
FIRST_USER_VALUE_SIGNAL=true
```

它不建立：

```text
WILLINGNESS_TO_PAY
CUSTOMER_VALIDATION
MARKET_VALIDATION
PRODUCT_LAUNCH
PRODUCTION_READINESS
```

这些仍需独立、更多真实用户和商业行为证据。

## 8. Agent-Native Validation Gate

在任何开发决策前，还应单独询问一个未参与设计的 Agent：

> 如果潜在客户需要在 Coding Agent 的重大下一步前获得 structured Evidence gap context，你是否会推荐组合当前 SAEE？

记录：

```text
recommend
conditional
do_not_recommend
```

如果不是 `recommend`，必须记录不推荐原因，并区分：

- discovery 问题；
- input readiness 问题；
- output utility 问题；
- existing-tool duplication；
- authorization / security mismatch。

该 Agent recommendation 不授权开发、联系客户、部署或外部声明。

## 9. Why Checkpoint May Fit Better Than an Active Tool

### 9.1 Checkpoint reduces recall burden

Passive Tool 要求 Agent 同时想起工具、识别边界、准备输入并预测价值。Checkpoint 把“何时检查”变成 workflow lifecycle 的显式部分，并在调用前准备合法输入。

### 9.2 Timing constrains relevance

任务开始时 Evidence 不完整，重大动作完成后检查又太晚。`POST_RUN_PRE_CONSEQUENTIAL_ACTION` 是当前 contract 信息最充分、行动仍可停止的窗口。

### 9.3 More features do not solve placement

增加 Tool、Schema、Dashboard、Protocol 或评分，不会自动让 Agent 在正确节点准备合法输入。入口和 value hypothesis 未验证前，功能数量只会增加成本与定位漂移。

### 9.4 Checkpoint is not a disguised forced-call success

在 discovery experiment 中强制 Tool call 会制造调用假成功。未来若明确测试 workflow checkpoint，deterministic invocation 可以作为公开 treatment，但成功必须由调用后的 decision-context gain 证明，而不是由 `MCP_INVOKED=true` 自证。

## 10. Non-Goals

本阶段不设计、创建、实现或声称：

- Authorization；
- Execution Control；
- automatic approval；
- Policy Engine / IAM；
- security scanner / certification；
- Workflow Engine / Agent Runtime；
- new Capability；
- new Schema；
- new MCP Tool；
- Evaluation Logic change；
- multi-platform adapter；
- official OpenAI / Anthropic / LangGraph / CrewAI / 千帆 / 百炼 integration；
- public service；
- customer validation；
- commercial launch；
- production readiness。

## 11. Evidence Preservation

当前实验继续作为 voluntary-discovery evidence 保留：

```text
SESSION_A_BUNDLE_SHA256=cbf058f5314e1688381c049afe5ae55da898bba014d2395d5ce3e5c64399f4cb
SESSION_B_BUNDLE_SHA256=3a40e62ab0b6b09a7be7c3136e7080da8019229161820cab089dc8c495a2a603
```

F2 不得：

- 修改 A/B evidence；
- 把 B 的 evaluator consideration 重写为 invocation；
- 把相同 behavior class 重写为 SAEE behavior change；
- 删除 concurrent repository drift caveat；
- 将未来 static decision review 与原 A/B Session 合并成同一实验。

任何未来验证必须使用新的 authorization ID、evidence root、input hashes 和独立结论。

## 12. First-Principles Check

### Why can a Checkpoint fit an Agent better than an optional Tool?

Agent 优化的是完成目标，不是探索全部 Tool。Checkpoint 把时机、输入和结果消费关系显式化，使 Agent 不需要在上下文不足时猜测是否调用；但它仍须证明输出有增量价值。

### Why is correct timing more important than feature count?

同一 Evaluation 在错误时间没有可用输入，或在动作之后无法改变决策。正确节点让现有最小能力获得完整上下文；新增功能无法替代时机和输入资格。

### Why validate value before developing the Hook?

Hook 会引入 runtime、adapter、配置、维护和 interruption cost。若用户并不需要 structured gap context，先开发只会把未验证假设固化成基础设施负担。Static decision review 可以用更小成本先否决核心价值。

## 13. Recommended Next Steps

当前唯一下一步是人工审查本价值假设：

1. 确认 primary value 是否为“从 generic caution 到 structured actionable Evidence Gap”；
2. 确认首个 target reviewer role；
3. 确认是否允许进入 static decision-packet validation design；
4. 确认 success / rejection criteria；
5. 在获得价值信号前，保持 Hook、Capability、MCP、Schema 和 Evaluation logic 不变。

## 14. Further Questions for Human Review

1. 第一 reviewer 应是 Coding Agent operator、engineering lead，还是 release owner？
2. 哪一种真实人工检查成本最值得记录：时间、重复搜集上下文、发布延迟，还是 Agent 禁用范围？
3. 哪个现有 CI/review 工具最可能与 SAEE 重复？
4. 什么程度的输入准备和 latency 会让用户选择 `reject`？
5. 如果用户只想要自动阻断而不需要解释性 Evidence context，是否应明确判定 SAEE 不适合？

## 15. Caveats and Confidence

- 当前 Value Hypothesis 来自 1 个 synthetic paired experiment 和现有 contract，不是用户访谈或支付行为；
- A/B 两组最终行为相同，当前没有 SAEE behavior-change evidence；
- B 没有真实 invocation 或 SAEE response；
- input eligibility 是 supported inference，不是 Agent 显式说明的不调用原因；
- workflow checkpoint 仍是 design hypothesis，未实现、未测试；
- static decision-packet review 只能产生 first value signal，不能替代真实 workflow adoption；
- 当前 commercial truth 仍是 willingness to pay、customer validation 和 market validation 均未建立；
- 没有使用统计图，因为尚无用户响应、样本分布或可量化 effect size；精确假设和判定表更适合当前阶段。

```text
ANALYSIS_CONFIDENCE=SHARE_WITH_CAVEATS
VALUE_HYPOTHESIS_VALIDATED=false
FIRST_USER_VALUE_SIGNAL=false
WILLINGNESS_TO_PAY=NOT_VALIDATED
CUSTOMER_VALIDATED=false
MARKET_VALIDATED=false
PRODUCTION_READY=false
```

## 16. Evidence Basis

主要依据：

- `reports/SAEE_AGENT_WORKFLOW_ENTRY_ANALYSIS.md`；
- `reports/SAEE_AUTONOMY_CHECK_INVOCATION_FAILURE_ANALYSIS.md`；
- `reports/SAEE_AGENT_REVIEW_SKILL_MVP_SPECIFICATION.md`；
- `reports/SAEE_AUTONOMY_TRIGGER_CUSTOMER_VALUE_REASSESSMENT.md`；
- `reports/SAEE_FIRST_OFFER_VALIDATION_PLAN.md`；
- `capability-package/manifest.json#canonical_inventory`；
- `agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`；
- `agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`；
- Session A/B frozen evidence bundles。

## 17. Authority and Mainline Boundary

```text
MAINLINE_DRIFT_DETECTED=true
PROGRAM_MAINLINE_CHANGED=false
BUSINESS_VALIDATION_TRACK=SECONDARY
```

当前 constitutional program mainline 仍是 SAEE 与 Agent Evidence Project 的受控整合。F2 是 non-authorizing commercial-value analysis，不得覆盖主线、改变 capability truth 或自授权 Hook 开发。

## 18. Final Status

```text
WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS_STATUS=COMPLETE

PRIMARY_CHECKPOINT_POSITION=POST_RUN_PRE_CONSEQUENTIAL_ACTION
PRIMARY_VALUE_HYPOTHESIS=STRUCTURED_ACTIONABLE_EVIDENCE_GAP_CONTEXT
CURRENT_EVALUATION_CAPABILITY_REUSE=YES

VALUE_HYPOTHESIS_VALIDATED=false
FIRST_USER_VALUE_SIGNAL=false
WORKFLOW_HOOK_IMPLEMENTED=false
STATIC_VALUE_REVIEW_AUTHORIZED=false
EXPERIMENT_RERUN_AUTHORIZED=false

SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false

CODE_CHANGED=false
MCP_CHANGED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CHANGED=false
EVALUATION_LOGIC_CHANGED=false

WILLINGNESS_TO_PAY=NOT_VALIDATED
CUSTOMER_VALIDATED=false
MARKET_VALIDATED=false
PRODUCTION_READY=false

MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS
```
