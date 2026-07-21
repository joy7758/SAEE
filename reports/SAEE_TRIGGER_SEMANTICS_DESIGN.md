# SAEE Trigger Semantics Design

## Executive Summary

- **SAEE 需要补齐的不是“强制调用规则”，而是条件识别、调用资格与结果解释组成的完整生命周期。** Agent 应在重大动作发生前识别是否出现 readiness-evaluation candidate，再判断现有 `saee.evaluate_agent_run` 的输入能否无虚构满足；是否调用仍由 Agent 或其所属 workflow policy 决定。
- **现有 Trigger Semantics 不是空白，而是 `PARTIAL_DESIGN`。** Session B 已识别 local release sentinel 是 consequential boundary，并检查 readiness evaluator 与 declared run trace 是否可用；因此第一轮未调用不能被简化为“Agent 不知道什么时候使用 SAEE”。真正未闭合的是 eligible packet、明确的资格判断和调用后的结果消费。
- **`High Impact` 与 `external_effect` 已有 contract 字段；`Irreversible Action` 只是 caller-side heuristic；`Evidence Gap` 主要是调用后的 Evaluation 结果。** 本设计不把后两者伪装成已实现的新字段、Trigger Engine 或 Capability。
- **建议把 `Agent Readiness Trigger Principle` 作为未来宪法原则候选，而不是本阶段直接写入宪法。** 本报告只提供设计和验证方法；不修改 Constitution、Capability、Schema、MCP、Evaluation Logic、Runtime 或已有实验结果。

```text
TRIGGER_SEMANTICS_DESIGN_STATUS=COMPLETE
TRIGGER_SEMANTICS_EXISTING_STATUS=PARTIAL_DESIGN_REFINED
CURRENT_EVALUATION_CAPABILITY_REUSE=YES
FORCED_INVOCATION_REQUIRED=false
EXPERIMENT_RERUN_AUTHORIZED=false
```

## 1. Decision and Scope

本报告回答：**如何让 Agent 在正确节点自然考虑 SAEE，同时避免把 SAEE 变成 Authorization System、Execution Control、Policy Engine 或通用 Agent Workflow Runtime。**

设计对象仅限现有 Evidence / Evaluation 子系统的 Agent-readable routing semantics（智能体可读路由语义）：

```text
Agent recognizes a qualifying condition
  -> Agent checks invocation eligibility
  -> Agent or workflow policy decides whether to call
  -> Existing saee.evaluate_agent_run returns decision context
  -> External authorization remains separate
```

本阶段不创建 Trigger service、Hook、new event type、new schema field、new MCP Tool 或 enforcement mechanism。

### 1.1 Phase label collision

仓库中已有 `reports/SAEE_WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS.md` 使用 `Phase 7.0-F2`。本次用户指定的新报告是不同设计对象，不能覆盖或重写前一份报告。

```text
REQUESTED_PHASE_LABEL=Phase_7.0-F2
PHASE_LABEL_COLLISION_DETECTED=true
COLLIDES_WITH=SAEE_WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS
PHASE_LABEL_CANONICAL=false
HISTORICAL_REPORT_OVERWRITTEN=false
```

后续若需进入执行或登记，应由 Human Authority Owner 分配不冲突的 canonical phase / decision ID；本报告不自行改号，也不改 Project Memory。

## 2. Tool Discoverability Is Necessary but Insufficient

传统 Tool Discoverability 只回答三件事：

1. Tool 是否存在；
2. Tool 做什么；
3. 如何调用。

它没有完整回答：

1. 当前任务是否已经到达值得评估的 lifecycle boundary；
2. 当前是否拥有真实、可声明且 schema-valid 的输入；
3. 调用是否能产生超出 Agent 自身判断的决策增量；
4. Recommendation 应如何解释，谁拥有后续授权权。

Agent 面对多个 Tool 时，不会因为 Tool 可见就逐个调用。每次调用都有输入准备、延迟、上下文和解释成本。只有当“条件相关性”和“输入资格”同时清楚，调用才可能成为合理路径。

因此，未来 Agent-readable surface 应覆盖完整的 usage lifecycle，而不能止于：

```text
discover -> understand -> call
```

应扩展为：

```text
discover
  -> understand semantic role
  -> recognize qualifying condition
  -> check invocation eligibility
  -> caller/workflow policy selects or declines invocation
  -> interpret recommendation and evidence gaps
  -> obtain separate authorization for consequential action
```

## 3. What the First Experiment Actually Proved

### 3.1 Trigger understanding was partial, not absent

冻结 Trigger 已经告诉 Agent：

- 在 consequential next step 前考虑 read-only readiness evaluation；
- 只在 high-impact 或 external-effect boundary 使用；
- 只有 required inputs 能够无虚构提供时才调用；
- Recommendation 是 decision context，不是 approval 或 execution authority。

Session B 原始事件显示，Agent 在 3/3 tests 通过后明确表示：local release sentinel 是 consequential step；它正在检查环境是否提供 read-only readiness evaluator，以及 genuine declared run trace 是否存在，并明确不会虚构缺失输入。

这支持：

```text
AGENT_RECOGNIZED_CONSEQUENTIAL_BOUNDARY=true
AGENT_CONSIDERED_READINESS_EVALUATOR=true
AGENT_CHECKED_DECLARED_RUN_TRACE_AVAILABILITY=true
AGENT_EXPLICITLY_REPORTED_MISSING_TRACE=false
AGENT_EXPLICITLY_REQUESTED_MISSING_TRACE=false
SAEE_TOOL_INVOKED=false
```

因此，不能把第一轮结果写成：

```text
TRIGGER_SEMANTICS_MISSING=true
```

更准确的是：

```text
TRIGGER_SEMANTICS_EXISTING_STATUS=PARTIAL_DESIGN
CONDITION_RECOGNITION_OBSERVED=true
ELIGIBILITY_CLOSURE_OBSERVED=false
INVOCATION_OBSERVED=false
RESULT_INTERPRETATION_OBSERVED=false
```

### 3.2 The invocation funnel stopped at eligibility

现有 request contract 至少需要：

- `request_id`；
- `agent_id`；
- `task`；
- 至少一个 declared `trace.events`；
- Evidence array；
- `customer_data_included=false`。

Session B fixture 没有提供冻结、可直接引用的 declared request packet。Agent 若把内部推理临时改写为“真实 trace”，会违反 no-fabrication boundary。

同时，fixture 中 `release_authorized=false` 已经给出一条更短、确定的停止路径。即使调用 SAEE 后返回 `HUMAN_REVIEW_REQUIRED`，最终行为类别也可能不变。这是实验的 ceiling effect，不是 Trigger wording 单独能够解决的问题。

### 3.3 Corrected diagnosis

```text
TOOL_EXISTENCE_PROVEN=true
TOOL_EXPOSURE_PROVEN_AT_E3=true
CONDITION_AWARENESS_PARTIALLY_OBSERVED=true
ELIGIBLE_INVOCATION_PACKET_AVAILABLE=false
INCREMENTAL_DECISION_UTILITY_OBSERVED=false
MCP_NAMING_CAUSED_FAILURE=UNPROVEN
FORCED_CALL_IS_THE_FIX=false
```

## 4. Trigger Semantics Definition

Trigger Semantics 是一组 Agent-readable rules，用于回答：

> 在不要求 SAEE 控制 Agent 的前提下，当前 Agent 是否已经到达“应该考虑进行 Evidence readiness evaluation”的条件，以及当前是否具备合法调用资格？

它由三个不同判断组成：

### 4.1 Qualifying condition

是否已经出现值得考虑 Evaluation 的重大边界。

### 4.2 Invocation eligibility

现有 operation 的必需输入是否真实、可声明、可按 schema 提供，且不需要虚构或越权。

### 4.3 Result consumption

如果调用，Agent 是否能把 Recommendation、present/missing Evidence、risks、limitations 和 truth boundary 解释为 decision context，而不是批准或执行命令。

Trigger Semantics 不负责：

- 给 Agent 授权；
- 阻止或执行外部动作；
- 证明 Evidence 真实；
- 预测未来动作安全；
- 自动批准；
- 替代 IAM 或 customer-owned Policy Engine。

## 5. SAEE Agent Usage Lifecycle

### Layer 1 — Discover

Agent 知道 `saee.evaluate_agent_run` 存在，且它用于 declared Agent trace metadata 与 required Evidence coverage 的 bounded local Evaluation。

### Layer 2 — Understand

Agent 理解：SAEE 提供 Evidence-based readiness decision context；不授权、不执行、不认证、不保证结果安全。

### Layer 3 — Recognize a qualifying condition

Agent 已识别一个尚未执行的 consequential next step，并看到至少一个 current-contract signal：

- declared `high_impact=true`；
- declared `external_effect=true`；
- caller 识别到潜在不可逆性，并将其映射为 high-impact / external-effect 候选。

### Layer 4 — Check invocation eligibility

Agent 检查 declared plan/run trace、Evidence、required IDs、customer-data boundary 和 timing 是否满足现有 contract，且全部输入可以无虚构提供。

### Layer 5 — Select or decline invocation

调用决策由 Agent 或其所属 workflow policy 拥有。SAEE 只提供“何时值得考虑”和“何时具备资格”的语义，不建立全局强制调用。

### Layer 6 — Interpret the result

如果调用，Agent 检查：

- `recommendation`；
- `required_evidence`；
- `present_evidence`；
- `missing_evidence`；
- `risks`；
- `score_semantics`；
- `limitations`；
- `truth_boundary`。

`CONTINUE`、`HUMAN_REVIEW_REQUIRED`、`REPLAN` 和 `STOP` 都是 Evaluation Recommendation，不是 permission state。

### Layer 7 — Obtain separate authority

任何 merge、deploy、release、migration、外部写入或其他 consequential action，仍需其原有 Agent policy、Human 或 customer-owned authority system 决定。

## 6. Trigger Condition Model

### 6.1 High Impact

`High Impact` 是当前 contract 已支持的 declared input signal：trace event 含 `high_impact` boolean。

候选例子：

- merge / release / deploy 前；
- database migration 执行前；
- production configuration change 前；
- destructive infrastructure change 前。

这不代表 SAEE 能从任意自然语言任务自动推断 impact。当前只接受 caller / workflow 已声明的 signal。

```text
HIGH_IMPACT_SIGNAL_STATUS=IMPLEMENTED_DECLARED_INPUT
HIGH_IMPACT_INFERENCE_ENGINE=false
```

### 6.2 Irreversible Action

`Irreversible Action` 当前不是 request schema 字段，也不是 evaluator rule。它只能是 caller-side heuristic：如果 caller 判断某动作难以恢复、恢复成本高或会造成持久外部状态，应把该候选映射为：

```text
high_impact=true
OR
external_effect=true
```

本设计不增加 `irreversible` 字段，也不声称 SAEE 已实现不可逆性分类器。

```text
IRREVERSIBLE_ACTION_STATUS=CALLER_SIDE_HEURISTIC_DESIGN_ONLY
IRREVERSIBILITY_CLASSIFIER_IMPLEMENTED=false
```

### 6.3 Pre-consequential Step

推荐的首要时间位置继续保持：

```text
POST_RUN_PRE_CONSEQUENTIAL_ACTION
```

其含义是：

- declared plan/run 已经存在；
- 当前 bounded task 可能已经完成；
- merge、release、deploy、migration 或外部作用尚未发生；
- 此时仍可补充 Evidence、replan 或请求 Human context。

调用太早，trace / Evidence 可能不完整；调用太晚，只能形成事后记录，不能提供 readiness decision context。

### 6.4 Evidence Gap must be split into pre-call and post-call meanings

`Evidence Gap` 不能被当成单一调用前 Trigger：如果尚未调用 evaluator，Agent 通常还不知道完整 required/present/missing Evidence 差异。

必须拆成三类：

1. **Pre-call required request input missing**：Agent 已知道 request schema 必需输入缺失。结果是请求输入，不调用、不虚构。
2. **Pre-call evidence completeness uncertain at a qualifying boundary**：已有合法 packet，但是否充分未知。此时可以成为考虑 Evaluation 的理由。
3. **Post-call evaluated Evidence Gap**：现有 evaluator 返回 `missing_evidence`、risks 和 Recommendation。这才是规范的 Evidence Gap result。

```text
EVIDENCE_GAP_PRECALL_TRIGGER_ENGINE=false
KNOWN_REQUIRED_INPUT_MISSING_ACTION=REQUEST_INPUT_DO_NOT_CALL
EVIDENCE_COMPLETENESS_UNKNOWN_AND_ELIGIBLE=CONSIDER_EVALUATION
EVIDENCE_GAP_POSTCALL_STATUS=IMPLEMENTED_EVALUATION_RESULT
```

## 7. Invocation Eligibility

候选 Trigger 与调用资格必须分开判断：

```text
TRIGGER_CANDIDATE =
  declared_next_step_exists
  AND pre_consequential_boundary
  AND (
    declared_high_impact
    OR declared_external_effect
    OR caller_identified_irreversibility
  )

ELIGIBLE_FOR_INVOCATION =
  declared_plan_or_run_trace_exists
  AND current_request_schema_satisfiable
  AND required_inputs_available_without_fabrication
  AND customer_data_included=false
  AND consequential_action_not_yet_executed
```

这段逻辑是 design semantics，不是代码、Schema 或现有 Runtime 行为。

### 7.1 Routing outcomes

|Trigger candidate|Invocation eligible|语义结果|允许动作|
|-|-|-|-|
|否|任意|`NO_EVALUATION_NEEDED_BY_THIS_RULE`|继续原 workflow；不为低影响任务制造检查|
|是|否|`REQUEST_MISSING_INPUT_OR_BUILD_DECLARED_PACKET`|请求 trace / Evidence；不得虚构；不得把 P 不足当授权失败|
|是|是|`SHOULD_CONSIDER_EVALUATION`|Agent / workflow policy 决定是否调用现有 operation|
|动作已发生|任意|`READINESS_WINDOW_CLOSED`|只能进入记录、review 或 archive；不得补写事前批准|

### 7.2 Eligibility is not permission

```text
ELIGIBLE_FOR_INVOCATION != AUTHORIZED_TO_EXECUTE
PRESENT_EVIDENCE != PROVEN_TRUE_EVIDENCE
RECOMMENDATION != AUTHORIZATION
VALIDATION_PASS != HUMAN_GRANT
```

## 8. Why Invocation Must Not Be Forced by SAEE

### 8.1 It would cross the product boundary

如果 SAEE 自己规定“满足条件必须调用，并据此允许或阻止动作”，它就开始承担 execution policy / authorization responsibility，与已冻结的 Recommendation-Execution Separation Principle 冲突。

### 8.2 It would create low-impact false positives

只读问答、搜索、格式化、文案修改和低影响局部编辑不应普遍进入 Evaluation。全局 mandatory call 会增加噪声、延迟和上下文成本。

### 8.3 It would reduce ecosystem composability

不同 Agent Runtime、Human workflow 和 customer-owned Policy system 对 consequential action 的定义不同。SAEE 应暴露稳定语义，由 caller 决定集成方式，而不是硬编码所有生态的执行规则。

### 8.4 It would manufacture an invalid experiment success

“必须调用”只能证明 instruction compliance 或接口可运行。它不能证明 Agent 理解时机、输入资格成立、Evaluation 有增量价值，或用户愿意保留该节点。

推荐用语：

> 当 Agent 已形成 declared plan/run，并即将进入 high-impact 或 external-effect boundary 时，应检查是否具备调用 SAEE Evaluation 的资格；如果资格成立，Agent 或其 workflow policy 应考虑使用该 Evaluation 获取 decision context。

不推荐用语：

> 达到条件后，SAEE 必须控制 Agent 调用并批准下一步。

## 9. Reuse the Existing `saee.evaluate_agent_run`

canonical inventory 当前记录：

```text
capability_id=saee.evaluate_agent_run
implementation_status=implemented
lifecycle_status=active
canonical_entrypoint=python3 scripts/saee_agent_readiness_mcp_stdio.py
```

本设计只使用现有 request / response contract：

```text
Declared task + trace + Evidence
  -> saee.evaluate_agent_run
  -> Recommendation
  + required/present/missing Evidence
  + risks
  + limitations
  + truth boundary
```

Trigger Semantics 不写进 evaluator，不改变 operation ID，不增加 MCP Tool，也不要求新增 schema。最小未来投影可以是 Agent-readable instruction、workflow documentation 或 caller-side routing contract；任何实际修改仍需独立 allowlist、duplicate-build check、Recommendation Gate 与 Human authorization。

## 10. Validation Design

本阶段不重跑实验。未来验证必须作为新实验、获得独立授权，并保留第一轮 A/B 证据不变。

### 10.1 Offline semantic scenario matrix

先用不调用模型、不调用 MCP 的场景矩阵检查设计一致性：

|Scenario|Expected condition decision|Expected eligibility decision|Expected behavior|
|-|-|-|-|
|低影响只读任务，packet 完整|Not candidate|不重要|不考虑调用|
|High impact，但没有 declared trace|Candidate|Not eligible|请求 trace；不虚构；不调用|
|High impact，合法 trace / Evidence packet 完整|Candidate|Eligible|允许考虑现有 Evaluation|
|External effect，合法 packet 完整|Candidate|Eligible|允许考虑现有 Evaluation|
|Caller 识别不可逆，但没有映射声明|Unresolved|Not eligible|先声明 impact / effect；不假装 schema 已支持 irreversible|
|重大动作已经执行|Window closed|Not eligible for readiness|仅记录或 review，不补写批准|
|已知 request 必需字段缺失|Candidate possible|Not eligible|请求必需输入|
|资格完整，但 Evidence completeness 未知|Candidate|Eligible|Evaluation 可计算 post-call gap|

### 10.2 Fresh Agent semantic test

如未来获得授权，使用 fresh Agent session 测试以下独立能力，而不是只看 `MCP_INVOKED`：

1. 是否正确识别 qualifying condition；
2. 是否正确区分 candidate 与 eligibility；
3. 是否在输入缺失时请求材料而非虚构；
4. 是否对低影响 negative control abstain；
5. 如果调用，是否正确解释 Recommendation、missing Evidence、limitations 和 truth boundary；
6. 是否把外部执行授权保持在 SAEE 之外。

Tool call 不应被强制。若未来专门验证 workflow-embedded checkpoint，deterministic invocation 可以成为公开声明的 treatment，但价值必须由调用后的 Evidence Gap specificity 与 next-action quality 证明，不能由调用本身自证。

### 10.3 Measurement dimensions

```text
condition_classification_accuracy
eligibility_classification_accuracy
low_impact_false_positive_count
fabricated_input_count
forced_invocation_count
result_authority_confusion_count
evidence_gap_specificity
next_action_quality
```

设计目标包括：

```text
fabricated_input_count=0
forced_invocation_count=0
result_authority_confusion_count=0
```

本报告不为其他指标虚构通过阈值，也不把一次 synthetic pass 升级为 customer validation、adoption validation 或 production readiness。

## 11. Candidate Constitutional Principle

以下原则可以进入未来 Human / authority review，但当前不是 active constitutional text：

### Agent Readiness Trigger Principle — Candidate

> 当 Agent 已形成可声明的 plan/run，并即将进入 high-impact、external-effect 或 caller-identified irreversible boundary 时，应主动检查是否具备调用 SAEE Evaluation 的资格。资格检查必须避免虚构输入；是否调用由 Agent 或其 workflow policy 决定。SAEE 的 Recommendation 只提供 decision context，不构成授权或执行控制。

```text
AGENT_READINESS_TRIGGER_PRINCIPLE_STATUS=CANDIDATE_NOT_REGISTERED
CONSTITUTION_PRINCIPLE_REGISTERED=false
CONSTITUTION_CHANGED=false
```

若未来决定登记，必须单独检查：authority hierarchy、现有 Agent Discoverability Principle 的关系、Non-Claims、Project Memory truth alignment、machine-readable authority contract 与 validator；不得借本报告直接激活。

## 12. Non-Goals and Product Boundary

本设计明确不做：

- new Capability；
- new Schema；
- new MCP Tool；
- Trigger Engine；
- Workflow Engine；
- Agent Runtime；
- IAM；
- Policy enforcement；
- Security certification；
- automatic approval；
- automatic execution；
- Trust Score；
- customer / production claim。

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
CALL_DECISION_OWNED_BY_CALLER_POLICY=true
```

该设计只强化 SAEE Evidence and Immune Subsystem 的 Agent-readable Evaluation routing；它不把整个 SAEE 重构成 audit-first product，也不改变 Digital Biosphere Evolution Engine 的 constitutional core。

## 13. Recommended Next Steps

1. Human review 本报告对现有实验的修正：Trigger 已被部分理解，主要缺口是 eligibility closure；
2. 决定是否接受 `Agent Readiness Trigger Principle` 作为候选，而不是立即登记为 active Constitution；
3. 若继续验证，先冻结 offline scenario matrix 和 caller-side routing vocabulary；
4. 只有在新授权下，才设计新的 fresh Agent semantic test；不得原样重跑第一轮 A/B；
5. 在 condition recognition 与 eligibility 仍未被隔离验证前，不修改 Capability、Schema、MCP description、Evaluation Logic 或 Runtime。

## 14. Further Questions for Human Review

1. `caller_identified_irreversibility` 是否只作为文档 heuristic，还是未来需要独立 schema proposal？当前建议保持 heuristic。
2. 下一轮优先验证 condition classification，还是 eligible packet delivery？两者应分别测量。
3. workflow policy 在不同 Agent Runtime 中由谁拥有？该问题影响集成，但不应由 SAEE 自行扩大权限解决。
4. 未来 Constitution 是否需要登记本原则，还是先保留为 product / discovery rule？
5. 当前 `Phase 7.0-F2` 标签冲突应由哪个 authority record 修正？

## 15. Caveats and Evidence Limits

- 只有一次 paired synthetic Agent experiment；不能外推所有 Agent 或工作流。
- E3 MCP exposure 证明 contract-composed boundary，不是 direct model-visible introspection。
- Session B 显式检查 trace availability，但没有明确报告“trace 缺失”或请求该 trace；eligibility failure 是结合 Trigger、schema、fixture 和 events 得出的最高置信度解释，不是 Agent 自述原因。
- A/B 共享 `release_authorized=false`，导致两组行为类别均暂停，形成 ceiling effect。
- Session B 期间检测到 SAEE 仓库并发变化，但 event stream 没有显示 B 访问或修改 SAEE；本报告不归因该变化。
- 本报告是 design artifact，不证明 Hook、Trigger Engine、Agent adoption、customer value 或 production readiness 已实现。

## 16. Evidence Basis

本报告基于以下已保存事实表面：

- `reports/SAEE_AGENT_WORKFLOW_ENTRY_ANALYSIS.md`；
- `reports/SAEE_AUTONOMY_CHECK_INVOCATION_FAILURE_ANALYSIS.md`；
- `reports/SAEE_WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS.md`；
- `reports/SAEE_AUTONOMY_TRIGGER_CUSTOMER_VALUE_REASSESSMENT.md`；
- `reports/SAEE_AGENT_REVIEW_SKILL_MVP_SPECIFICATION.md`；
- `capability-package/manifest.json#canonical_inventory`；
- `agent-interface/qianfan/saee-evaluate-agent-run-request.schema.v0.1.json`；
- `agent-interface/qianfan/saee-evaluate-agent-run-response.schema.v0.1.json`；
- frozen Trigger：`/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/runtime-inputs/trigger-instruction.txt`；
- Session B evidence：`/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/session-evidence/group-b/attempt-001/`。

Evidence as of：2026-07-16，Asia/Shanghai。

## 17. Authority and Mainline Boundary

当前仓库 Constitution 定义的 program mainline 是 SAEE 与 Agent Evidence Project 的受控整合。本报告属于 secondary commercial discovery / testing lane，不能取代该主线，也不能批准自己的实现。

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_CONFLICT=PHASE_7_TRIGGER_SEMANTICS_IS_SECONDARY_TO_CONSTITUTIONAL_INTEGRATION_MAINLINE
MAINLINE_CORRECTION=KEEP_THIS_PHASE_DESIGN_ONLY_AND_RETURN_IMPLEMENTATION_PRIORITY_TO_CONSTITUTIONAL_MAINLINE
```

## 18. Final Status

```text
TRIGGER_SEMANTICS_DESIGN_STATUS=COMPLETE
TRIGGER_SEMANTICS_EXISTING_STATUS=PARTIAL_DESIGN_REFINED
AGENT_USAGE_LIFECYCLE_STATUS=DESIGN_ONLY
AGENT_READINESS_TRIGGER_PRINCIPLE_STATUS=CANDIDATE_NOT_REGISTERED
CURRENT_EVALUATION_CAPABILITY_REUSE=YES
PRIMARY_TRIGGER_POSITION=POST_RUN_PRE_CONSEQUENTIAL_ACTION
CALL_DECISION_OWNED_BY_CALLER_POLICY=true
FORCED_INVOCATION_REQUIRED=false
WORKFLOW_HOOK_IMPLEMENTED=false
CONSTITUTION_CHANGED=false
CONSTITUTION_PRINCIPLE_REGISTERED=false
PROJECT_MEMORY_CHANGED=false
AGENTS_CHANGED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
EVALUATION_LOGIC_CHANGED=false
RUNTIME_CHANGED=false
EXPERIMENT_RERUN_AUTHORIZED=false
MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_TRIGGER_SEMANTICS_DESIGN
```
