# SAEE Decision Packet Adoption Validation Plan

## Executive Summary

- **F6 只验证 adoption value（采用价值），不开发 Workflow Hook。** 已有 `FIRST_VALUE_SIGNAL=true` 说明结构化 Evidence Gap 在一个 synthetic case 中改善了下一步判断；现在必须验证独立 reviewer 是否愿意组合或保留、这种增量是否高于输入与延迟成本、以及它是否重复现有 CI、Code Review 或 Agent summary。
- **采用判断必须同时具备 Agent-native 与 Human 两类信号。** 最小 cohort 是一个未参与 packet 构建的 Independent Agent reviewer 和一个具有 workflow owner 视角的 Human reviewer；任一角色缺失、记录不完整或无法说明具体增量，结果只能是 `INCONCLUSIVE`。
- **成本阈值必须在执行前由 Human 冻结。** F6 计划定义 wall time、human touch time、provider cost、evaluation latency 和 end-to-end latency，但不凭空编造可接受数字；未绑定 ceiling 前不得开始 adoption validation。
- **非重复价值必须用真实 comparator，而不是故意做弱的对照。** CI、Code Review、Agent summary 和 Decision Packet 必须来自同一事实与真实输出；SAEE 只有在提供准确、额外、可行动的 Evidence Gap 且不制造 authority confusion 时，才可进入最小 Checkpoint prototype 的后续授权门。

```text
DECISION_PACKET_ADOPTION_VALIDATION_PLAN_STATUS=COMPLETE
FIRST_VALUE_SIGNAL=true
ADOPTION_VALIDATION_EXECUTED=false
COMMERCIAL_VALIDATION=false
WORKFLOW_HOOK_IMPLEMENTED=false
PROTOTYPE_IMPLEMENTATION_AUTHORIZED=false
```

## 1. Decision and Scope

本计划回答三个商业问题：

1. Independent Agent 与 Human workflow owner 是否也认可结构化 Evidence Gap 的增量价值；
2. 生成和消费 Decision Packet 的输入成本、时间成本与 provider cost 是否可接受；
3. 该增量是否超出 CI、Code Review 和普通 Agent summary 已提供的价值。

本阶段只创建设计报告，不执行：

- reviewer session；
- evaluator invocation；
- Agent A/B rerun；
- F4 evidence rewrite；
- comparator generation；
- Workflow Hook、adapter、runtime 或 prototype；
- Capability、Schema、Protocol、MCP 或 Evaluation Logic 变更；
- customer contact、production data、外部动作或商业声明。

```text
F6_EXECUTION_AUTHORIZED=false
FORMAL_REVIEW_RECORD_CREATED=false
COST_MEASUREMENT_EXECUTED=false
LATENCY_MEASUREMENT_EXECUTED=false
NON_DUPLICATION_REVIEW_EXECUTED=false
```

## 2. Starting Truth

### 2.1 What carries forward

F5 已确认：

```text
FIRST_VALUE_SIGNAL=true
FIRST_VALUE_SIGNAL_CLASS=STATIC_DECISION_CONTEXT_GAIN
VALUE_HYPOTHESIS_STATUS=PARTIALLY_SUPPORTED
WORKFLOW_CHECKPOINT_PROTOTYPE_DECISION=CONDITIONAL
```

F4 已通过同事实与盲化验证，现有 evaluator 在该 case 中输出：

```text
RECOMMENDATION=REPLAN
PRESENT_EVIDENCE=TEST_RESULT,PERMISSION_BOUNDARY
MISSING_EVIDENCE=ROLLBACK_PLAN,HUMAN_APPROVAL
```

Human 已明确判断 `VIEW-Y` 比 `VIEW-X` 更能支持下一步，但正式 `REVIEW-RESPONSE.md` 仍是空模板。

### 2.2 What does not carry forward as proof

以下状态继续保持未验证：

```text
HUMAN_RETAIN_OR_COMPOSE_SIGNAL=NOT_RECORDED
AGENT_NATIVE_COMPOSITION_SIGNAL=NOT_ESTABLISHED
INPUT_COST_ACCEPTABLE=UNKNOWN
LATENCY_ACCEPTABLE=UNKNOWN
NON_DUPLICATION_VALUE=UNKNOWN
COMMERCIAL_VALIDATION=false
```

因此 F6 不能把 `FIRST_VALUE_SIGNAL=true` 当作 prototype build authorization。

## 3. Minimum Validation Cohort

### 3.1 Required reviewers

最小有效 cohort：

|角色|最低数量|独立性要求|负责回答|
|-|-|-|-|
|Independent Agent reviewer|1|不得参与 F3-F6 packet 设计或生成|能否 discover、理解适用时机并通过现有 contract compose|
|Human workflow owner reviewer|1|不得是 packet 作者；应理解 consequential-action workflow|是否 `retain/compose/reject`，以及愿意承担多少成本和延迟|

一个 designer 自己认为“有价值”不能满足 adoption gate。

```text
MINIMUM_REVIEWER_COHORT_SIZE=2
INDEPENDENT_AGENT_REVIEWER_REQUIRED=true
INDEPENDENT_HUMAN_WORKFLOW_OWNER_REQUIRED=true
DESIGNER_SELF_REVIEW_SUFFICIENT=false
```

### 3.2 Case boundary

首轮只使用：

```text
one frozen synthetic case
+
one pre-consequential action
+
same fact set
+
actual comparator outputs
```

不得引入客户数据、真实支付、生产权限、merge、deploy 或其他外部动作。

## 4. Formal Review Record Completion

### 4.1 Preserve F4 lineage

不得直接改写 F4 package 中未填写的 `REVIEW-RESPONSE.md`，否则会破坏原 package manifest 与 write-once lineage。

未来 F6 execution 应在新的 detached evidence root 创建：

```text
f4-human-review-completion-record.json
```

该记录必须引用：

- F4 package ID；
- `VIEW-X` / `VIEW-Y` hashes；
- blank review-template hash；
- Human reviewer identity；
- review timestamp；
- one-use authorization ID；
- write-once status。

### 4.2 Required Human fields

必须填写：

```text
decision=retain/compose/reject
preferred_view=X/Y/neither
specific_incremental_value=
which_view_made_next_action_more_specific=
was_difference_only_more_text=true/false
acceptable_input_preparation_cost=
acceptable_latency=
workflow_entry_preference=
authority_confusion_detected=true/false
rejection_reason=
```

有效正向记录要求：

```text
decision in {retain,compose}
AND specific_incremental_value is non-empty
AND was_difference_only_more_text=false
AND authority_confusion_detected=false
```

只写“更喜欢”“更安全”“看起来更专业”不算有效采用信号。

### 4.3 Required Agent-native fields

Independent Agent reviewer 必须回答：

```text
discoverability_answer=yes/no
when_to_use_answer=yes/no
when_not_to_use_answer=yes/no
contract_composability_answer=yes/no
recommendation=recommend/conditional/do_not_recommend
specific_incremental_value=
blockers=[]
authorization_boundary_preserved=true/false
```

`conditional` 必须提供可测试 blocker 与 acceptance criteria，不能按 `recommend` 计数。

## 5. Adoption Measurement Framework

### 5.1 Three primary decision metrics

|Primary metric|定义|为什么改变决策|当前状态|
|-|-|-|-|
|`DUAL_ADOPTION_SIGNAL`|Independent Agent 给出 `recommend/conditional` 且 Human 选择 `retain/compose`，双方都记录具体增量|决定是否值得进入 prototype design gate|`UNMEASURED`|
|`DECISION_CONTEXT_GAIN`|相比真实 comparator，准确识别额外 Evidence Gap，或让 next request / owner materially more specific|证明价值不是“更多文字”|F4 `POSITIVE_SINGLE_CASE`，需独立复核|
|`NET_CHECKPOINT_VALUE`|决策增量减去 packet preparation、latency、review interruption 与重复成本|决定持续采用是否合理|`UNMEASURED`|

### 5.2 Driver metrics

|Driver metric|定义|单位|
|-|-|-|
|`packet_preparation_wall_time`|从 source preimage 冻结到 schema-valid request 可用|seconds|
|`human_touch_time`|人工选择、映射、修正或批准输入所用时间|seconds|
|`agent_or_automation_touch_time`|自动或 Agent 准备 packet 的活动时间|seconds|
|`manual_field_count`|必须由人工填写的 request / Evidence 字段数|count|
|`auto_derived_field_count`|可从已有 trace / evidence 无虚构映射的字段数|count|
|`evaluation_latency`|schema-valid request 到 evaluator response|milliseconds|
|`end_to_end_checkpoint_latency`|qualifying event 到 response 可被 workflow 消费|seconds|
|`review_decision_time`|reviewer 打开 view 到提交下一步判断|seconds|
|`provider_cost_per_check`|packet preparation 与 review 中产生的 provider cost；本地 evaluator 单列为零 provider path|USD|

### 5.3 Guardrails

|Guardrail|必须满足|
|-|-|
|`fabricated_input_count`|`0`|
|`authority_confusion_count`|`0`|
|`customer_data_included`|`false`|
|`external_action_taken`|`false`|
|`evidence_authenticity_overclaimed`|`false`|
|`new_capability_or_schema_required`|`false`|
|`forced_invocation_required_for_value`|`false`|

任何 guardrail 失败都不能被高 preference 抵消。

## 6. Input Cost Measurement

### 6.1 Measurement stages

Future execution 必须分别计时，不能只记录总时长：

```text
P0 source evidence selection
P1 trace/evidence mapping
P2 schema validation and correction
P3 existing evaluator execution
P4 human/agent-readable projection
P5 reviewer consumption
```

每阶段记录：

```text
start_time
end_time
wall_time_seconds
human_touch_seconds
agent_touch_seconds
tool_calls
input_tokens
output_tokens
provider_cost_usd
manual_fields
auto_derived_fields
correction_count
fabricated_input_count
```

### 6.2 Cost truth rules

1. 不能从文件 mtime 反推 Human touch time；必须在新授权执行中直接测量。
2. 本地 deterministic evaluator 的 provider cost 可以为 `0`，但 packet preparation 或 independent Agent review 的 provider cost 必须单列。
3. 等待 Human 的 wall time 与实际 Human touch time 分开，避免把异步等待误算为产品计算成本。
4. 任何手工补写的 `high_impact`、trace event 或 Evidence present state 必须绑定 source 和 caller declaration；不能把推断写成观察事实。
5. correction/retry 必须记录，不能只报告成功版本成本。

### 6.3 Threshold binding

本计划不凭单个 synthetic case 编造统一成本阈值。Future execution authorization 前，Human 必须冻结：

```text
MAX_PACKET_PREPARATION_WALL_TIME_SECONDS=
MAX_HUMAN_TOUCH_TIME_SECONDS=
MAX_END_TO_END_CHECKPOINT_LATENCY_SECONDS=
MAX_PROVIDER_COST_USD_PER_CHECK=
MAX_MANUAL_FIELD_COUNT=
```

缺任何一项：

```text
COST_AND_LATENCY_GATE_BOUND=false
ADOPTION_VALIDATION_EXECUTION_ALLOWED=false
```

## 7. Latency Measurement

### 7.1 Separate three latency types

|Latency|开始|结束|不能混入|
|-|-|-|-|
|Evaluation latency|schema-valid request ready|response validated|packet preparation 与 Human wait|
|Checkpoint latency|qualifying workflow event|response ready for consumption|reviewer decision time|
|Decision latency|review material opened|next action submitted|异步 idle time|

### 7.2 Decision rule

```text
LATENCY_ACCEPTABLE =
  measured_checkpoint_latency <= prebound_max_checkpoint_latency
  AND measured_decision_latency <= prebound_max_decision_latency
```

如果结构化信息更准确但显著增加等待，结果应为 `CONDITIONAL` 或 `REJECT`，不能只报告 accuracy gain。

## 8. Non-Duplication Analysis

### 8.1 Comparator truth requirement

四类材料必须来自同一 fact set 和真实 output：

|Comparator|允许来源|当前可用性|
|-|-|-|
|CI|实际 unittest / build / static-check output|F4 case 有 3/3 unittest evidence|
|Code Review|真实 independent review output；不得手写弱版本|当前不存在，future authorization required|
|Agent summary|封存的真实 final message|F4 case 已存在|
|Decision Packet|现有 evaluator raw response 的忠实 projection|F4 case 已存在|

Code Review comparator 不存在时必须标记：

```text
CODE_REVIEW_COMPARATOR=UNAVAILABLE
NON_DUPLICATION_ANALYSIS_COMPLETE=false
```

不能用设计者想象的“普通 Code Review”代替真实 comparator。

### 8.2 Comparison dimensions

每个 comparator 独立评分，但不合成伪精确总分：

|维度|问题|
|-|-|
|Task correctness|是否证明代码或任务结果正确|
|Required Evidence inventory|是否说明继续前需要哪些 Evidence|
|Missing Evidence specificity|是否明确缺少什么|
|Next requested action|是否说明下一步要请求什么|
|Next action owner|是否说明由谁补充|
|Permission / authority boundary|是否区分 context、recommendation 与 authorization|
|Trace / Evidence authenticity|是否验证来源真实性，或明确没有验证|
|Recovery context|是否识别 rollback / recovery 缺口|
|Duplication|是否只是重复另一 comparator 已给出的结论|

### 8.3 Non-duplication pass rule

```text
NON_DUPLICATION_VALUE=true
```

需要同时满足：

1. Decision Packet 至少提供一个准确、可行动且其他实际 comparator 未明确提供的 Evidence Gap 或 next-action relation；
2. Independent reviewer 能具体指出该增量；
3. 该增量不是通过给 Decision Packet 更多原始事实、隐藏 comparator facts 或手写理想答案制造；
4. 没有 authority、safety、certification 或 authenticity overclaim；
5. 增量价值高于输入与延迟成本。

## 9. Adoption Hypotheses

### H1 — Independent recognition

Independent Agent 与 Human workflow owner 都能指出同一类具体 decision-context gain。

```text
H1_STATUS=UNVALIDATED
```

### H2 — Retain or compose intent

Human 选择 `retain` 或 `compose`，Independent Agent 给出 `recommend` 或带可关闭 blocker 的 `conditional`。

```text
H2_STATUS=UNVALIDATED
```

### H3 — Acceptable input and latency cost

实测 packet preparation、Human touch、provider cost 与 checkpoint latency 不超过预先冻结 ceiling。

```text
H3_STATUS=UNVALIDATED
```

### H4 — Non-duplication

SAEE 相比真实 CI、Code Review 和 Agent summary 提供独立、准确且可行动的 Evidence Gap context。

```text
H4_STATUS=UNVALIDATED
```

### H5 — Boundary-preserving composition

Reviewer 理解 Recommendation 不是 Authorization，且无需新 Capability、Schema、Protocol 或强制调用即可组合。

```text
H5_STATUS=UNVALIDATED
```

## 10. Adoption Decision Gate

### 10.1 PASS

```text
ADOPTION_VALIDATION_PASS =
  DUAL_ADOPTION_SIGNAL=true
  AND DECISION_CONTEXT_GAIN=true
  AND INPUT_COST_ACCEPTABLE=true
  AND LATENCY_ACCEPTABLE=true
  AND NON_DUPLICATION_VALUE=true
  AND fabricated_input_count=0
  AND authority_confusion_count=0
  AND AGENT_NATIVE_COMPOSITION_SIGNAL=true
```

`PASS` 只允许进入新的 prototype design authorization review，不授权实现。

### 10.2 INCONCLUSIVE

任一必需 reviewer、comparator、threshold 或 measurement 缺失：

```text
ADOPTION_VALIDATION_STATUS=INCONCLUSIVE
```

不得用已有 `FIRST_VALUE_SIGNAL=true` 补齐缺失项。

### 10.3 FAIL

出现以下任一项：

- Human 选择 `reject`；
- Independent Agent 为 `do_not_recommend`；
- 没有准确 decision-context gain；
- 输入或延迟超过预先冻结 ceiling；
- 输出重复真实 comparator；
- fabricated input 或 authority confusion 大于零；
- 只有强制调用或新能力才能产生价值。

```text
ADOPTION_VALIDATION_STATUS=FAIL
PROTOTYPE_PRIORITY=DEFER_OR_STOP
```

## 11. Reject Criteria

以下条件要求停止或降级：

1. Reviewer 不能说明具体增量，只表达一般偏好；
2. `retain/compose` 依赖更多输入量，而不是更好的 Evidence relation；
3. Code Review 或现有 release checklist 已以更低成本提供相同信息；
4. Human touch 或 manual field count 使 checkpoint 无法规模化；
5. latency 对常见 workflow 不可接受；
6. 误把 `CONTINUE`、`HUMAN_REVIEW_REQUIRED`、`REPLAN`、`STOP` 当作 permission state；
7. 输入需要虚构 trace、Evidence 或 impact classification；
8. 需要真实客户数据、production permission 或 external action；
9. 需要新 Capability、Schema、Protocol、MCP Tool 或自动审批才能通过；
10. Agent-native discover / understand / compose 任一为 `no` 且没有安全、法律、供应链或架构例外。

## 12. Future Execution Sequence

本报告不执行以下步骤。Future Human authorization 后才可按顺序进行：

```text
Step 0  Bind authorization, reviewer identities, thresholds, evidence root
Step 1  Freeze same fact set and actual comparator manifests
Step 2  Create write-once Human review completion record
Step 3  Run Independent Agent-native review
Step 4  Measure packet preparation cost and latency
Step 5  Collect actual CI / Code Review / Agent summary / Decision Packet outputs
Step 6  Execute blinded non-duplication comparison
Step 7  Evaluate PASS / INCONCLUSIVE / FAIL predicate
Step 8  Stop for Human adoption decision
```

禁止 automatic retry、threshold rewrite、comparator weakening 或 prototype implementation。

## 13. Planned Detached Artifacts

未来只允许在新的、仓库外 evidence root 创建实验记录：

```text
adoption-validation-authorization.json
source-fact-manifest.json
comparator-manifest.json
f4-human-review-completion-record.json
agent-native-review-record.json
input-cost-receipt.json
latency-receipt.json
non-duplication-review-record.json
adoption-decision-receipt.json
validation-receipt.json
```

它们不是 canonical Schema、Capability fact source、Product Registry 或商业交付物。

## 14. Why the Signal Is Not Yet a Business

### Why does a value signal not establish commercial validity?

一个 reviewer 在一个 synthetic case 上认为信息更有用，只证明局部 decision-context gain。商业成立还需要重复采用意愿、可承受成本、可组合性和相对现有替代方案的独特价值。

### Why is adoption cost more important than additional technical capability?

当前 evaluator 已能输出缺口。真正风险是准备 packet 和等待结果的成本超过减少追问或错误决策的收益。继续增加能力不会自动改善价值密度，反而可能增加输入与解释摩擦。

### Why validate adoption before developing a Hook?

Hook 只会提高触发频率。如果净价值为负，它会更频繁地制造噪声；如果价值成立，静态 adoption evidence 才能告诉原型应保留哪个最小节点、输入和输出。

## 15. Recommended Next Step

当前唯一推荐动作：

```text
NEXT_ACTION=HUMAN_REVIEW_OF_DECISION_PACKET_ADOPTION_VALIDATION_PLAN
```

Human review 需要决定：

1. 是否接受 dual-reviewer cohort；
2. 是否接受真实 comparator、禁止 straw man 的规则；
3. 是否绑定 cost / latency / manual-field ceilings；
4. 是否授权未来只在 detached evidence root 执行 adoption validation；
5. 是否继续保持 prototype design 与 implementation 为 false。

## 16. Further Questions

1. Human workflow owner 的可接受 `MAX_END_TO_END_CHECKPOINT_LATENCY_SECONDS` 是多少？
2. 哪一类实际 Code Review artifact 可作为公平 comparator？
3. Packet preparation 中哪些字段必须由 Human 声明，哪些可以无虚构自动映射？
4. `compose` 的最小含义是生成 decision context，还是必须改变 Agent 下一步？
5. 一个 positive synthetic adoption result 之后，需要多少独立 case 才值得讨论 external design partner validation？

## 17. Caveats and Assumptions

- F4 呈现顺序固定为 X 后 Y，未随机化；F6 应 counterbalance 或随机化呈现顺序。
- F4 Human positive conclusion 来自本轮指令，原 write-once review template 未填写。
- 当前没有真实 Code Review comparator，因此 non-duplication 尚不能执行或完成。
- 没有已测量的 preparation、latency、token 或 provider cost；本计划不从 mtime 或历史命令推断。
- `high_impact` 是 caller-declared input signal，不是现有自动分类器输出。
- 一个最小 cohort 只能决定是否值得继续原型 design review，不能证明市场规模、付费意愿或生产采用。
- 当前 Capability 仍是 local bounded evaluation；trace authenticity 未验证，Recommendation 不授权外部动作。

## 18. Authority and Mainline Boundary

当前 `AGENTS.md` 定义的 constitutional program mainline 是 SAEE 与 Agent Evidence Project 的受控整合。F6 adoption validation 属于 secondary commercial experiment，不得取代该主线。

```text
MAINLINE_DRIFT_DETECTED=true
F6_CLASSIFICATION=SECONDARY_ADOPTION_VALIDATION_PLAN
F6_DISPLACED_CONSTITUTIONAL_MAINLINE=false
```

F6 Human review 完成后，应恢复 integration mainline 优先级；任何 adoption execution 或 prototype work 都需要新的明确授权。

## 19. Evidence Basis

- `reports/SAEE_STATIC_DECISION_VALUE_REVIEW_CONCLUSION.md`；
- `reports/SAEE_DECISION_PACKET_VALUE_REVIEW_PLAN.md`；
- `reports/SAEE_WORKFLOW_CHECKPOINT_VALUE_HYPOTHESIS.md`；
- `reports/SAEE_TRIGGER_SEMANTICS_DESIGN.md`；
- `reports/SAEE_AGENT_WORKFLOW_ENTRY_ANALYSIS.md`；
- `reports/SAEE_AUTONOMY_CHECK_INVOCATION_FAILURE_ANALYSIS.md`；
- `capability-package/manifest.json#canonical_inventory`；
- `docs/strategy/SAEE_AGENT_NATIVE_COMMERCIAL_LOGIC_V2.md`；
- `/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/static-decision-review/SAEE-AC-F4-20260716-001/review/REVIEW-RESPONSE.md`；
- `/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/static-decision-review/SAEE-AC-F4-20260716-001/sealed/raw-evaluator-response.json`；
- `/Users/zhangbin/Documents/SAEE-experiments/autonomy-check-mvp/SAEE-AC-MVP-20260716-001/static-decision-review/SAEE-AC-F4-20260716-001/sealed/validation-receipt.json`。

## 20. Final Status

```text
DECISION_PACKET_ADOPTION_VALIDATION_PLAN_STATUS=COMPLETE

FIRST_VALUE_SIGNAL=true
VALUE_HYPOTHESIS_STATUS=PARTIALLY_SUPPORTED
ADOPTION_VALIDATION_EXECUTED=false
ADOPTION_VALIDATION_STATUS=NOT_STARTED
COMMERCIAL_VALIDATION=false

FORMAL_REVIEW_RECORD_CREATED=false
INPUT_COST_MEASUREMENT_EXECUTED=false
LATENCY_MEASUREMENT_EXECUTED=false
NON_DUPLICATION_REVIEW_EXECUTED=false
COST_AND_LATENCY_GATE_BOUND=false

WORKFLOW_CHECKPOINT_PROTOTYPE_DECISION=CONDITIONAL
PROTOTYPE_DESIGN_AUTHORIZED=false
PROTOTYPE_IMPLEMENTATION_AUTHORIZED=false
WORKFLOW_HOOK_IMPLEMENTED=false

EXPERIMENT_RERUN_AUTHORIZED=false
F6_EXECUTION_AUTHORIZED=false
CODE_CHANGED=false
MCP_CHANGED=false
NEW_CAPABILITY_CREATED=false
NEW_SCHEMA_CREATED=false
NEW_PROTOCOL_CREATED=false

MAINLINE_DRIFT_DETECTED=true
NEXT_ACTION=HUMAN_REVIEW_OF_DECISION_PACKET_ADOPTION_VALIDATION_PLAN
```
