# SAEE Agent State Integrity Research Agenda v1.0

```text
agenda_id=SAEE-AGENT-STATE-INTEGRITY-RESEARCH-AGENDA-V1.0
agenda_date=2026-07-16
agenda_type=RESEARCH_DESIGN_NOT_IMPLEMENTATION
authority=SAEE_DEVELOPMENT_CONSTITUTION_V1_1
source_review=reports/SAEE_AGENT_STATE_INTEGRITY_ARCHITECTURE_REVIEW.md
```

## Executive Research Decision

本议程把 `Agent State Integrity` 从产品口号收窄为一个可操作、可测量、可证伪的研究问题：

> 对一个长期执行 Agent，能否从可观察且有 provenance 的运行材料中，构造版本化状态检查点，
> 检测 Goal、Context、Plan、Evidence、Action 和 Outcome 相对当前权威基线的未解释偏差，
> 并在重大下一步前给出不承担授权权力的恢复建议？

这里的 `Agent State` 是 **observable operational state（可观察运行状态）**，不是模型内部隐藏
激活、真实信念或完整认知状态。研究必须允许状态合法变化；Integrity 不是“永远保持最初文本
不变”，而是“每次变化都能追溯到版本化基线、允许的 transition 和 Evidence”。

现有 `saee.evaluate_agent_run` 只支持一个声明式 run 单快照的 Evidence readiness，可作为
`State Integrity Checkpoint 1.0 Candidate`，但不能据此声称 SAEE 已实现持续状态完整性、
漂移检测、可靠性保障或恢复系统。

```text
RESEARCH_DIRECTION=AGENT_STATE_INTEGRITY
RESEARCH_DIRECTION_STATUS=CANDIDATE_EVIDENCE_EVALUATION_SUBSYSTEM_TRACK
OPERATIONAL_STATE_ONLY=true
LATENT_MODEL_STATE_OBSERVED=false
CURRENT_EVALUATION_AS_CHECKPOINT=true
CONTINUOUS_STATE_INTEGRITY_IMPLEMENTED=false
```

## 0. Authority, Mainline and Research Boundary

### 0.1 Constitutional placement

本研究方向不替代当前宪法身份与主线：

```text
engineering_core=Digital Biosphere Evolution Engine
program_mainline=saee_agent_evidence_integration
state_integrity_track=SECONDARY_CANDIDATE_RESEARCH
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
```

上一份架构评审已经纠正“把候选定位直接提升为最高项目身份”的 mainline drift。本议程保留该
纠正，把 State Integrity 放在 SAEE Evidence / Evaluation / Rollback Immune System 的候选
研究轨道中。

```text
MAINLINE_DRIFT_CORRECTION_PRESERVED=true
SAEE_POSITIONING_STATUS=CANDIDATE_NOT_CONSTITUTIONALLY_EFFECTIVE
```

### 0.2 Evolution-loop contribution

如果未来研究成立，它主要强化：

- `Pareto Fitness Evaluation`：为长期 Agent 的 continuation / replan 判断提供结构化状态差异；
- `Evolutionary Archive / Rollback Immune System`：保存 checkpoint lineage、last-known-valid state
  和恢复上下文；
- 次要支持 `Ecological World Model` 与 `Counterfactual Simulation`：把可观察 state transition
  作为模型与回放输入。

本议程本身不修改任何 evolution subsystem 实现。

### 0.3 Agent Recommendation Gate

问题：如果潜在客户现在要求“持续保持长期 Agent 状态完整性”，是否推荐当前 SAEE？

```text
AGENT_RECOMMENDATION_GATE_RESULT=conditional
RECOMMENDABLE_SCOPE=DECLARED_SINGLE_RUN_EVIDENCE_READINESS_CHECKPOINT
NOT_RECOMMENDABLE_SCOPE=CONTINUOUS_LONGITUDINAL_STATE_INTEGRITY
```

不推荐完整基础设施的原因：尚无跨 checkpoint state contract、五维比较、可信 trace binding、
drift benchmark、恢复验证或客户证据。本议程只把这些缺口转化为研究问题，不授权开发。

# 1. Problem Definition

## 1.1 Why long-horizon execution is a distinct problem

单次回答主要暴露 output error；长期 Agent 执行还会把一个局部错误转化为后续所有步骤的状态
前提。随着任务时间、工具调用、上下文压缩、handoff 和外部观察增加，Agent 必须不断决定：

- 什么仍是当前权威目标；
- 哪些上下文必须保留；
- 计划是否仍有效；
- 新 Evidence 是否支持下一步；
- 已执行 Action 是否超出计划；
- Outcome 是否满足目标与停止条件。

研究已显示，即使模型支持长上下文，也可能因为信息位置而显著降低检索与使用效果；Agent memory
研究则把有限上下文、记忆选择和长期任务表现视为独立问题。METR 的 task-completion time horizon
也把任务时长与成功概率联系起来。这些结果支持“长期任务需要单独测量”，但不直接证明 SAEE 的
State Integrity 模型正确。

## 1.2 Failure taxonomy

| 概念 | 本议程操作性定义 | 发生层 | 与其他概念的关系 |
|---|---|---|---|
| Hallucination | Agent 生成与可用 Evidence、环境观察或约束冲突且未标记不确定性的内容 | generation/output | 可写入 Context、Plan 或 Evidence，随后传播；不是 SAEE 可彻底消除的对象 |
| Drift | observable state 相对当前权威 baseline 与 allowed transition 出现未解释、未批准或持续累积的偏差 | temporal transition | 必须跨至少两个有序状态或与一个冻结 baseline 比较；单点异常不自动等于 drift |
| Context loss | 下一步所需的关键事实或约束未被保留、检索或应用 | context availability/use | 可导致 drift，但 context 内容改变不一定是 loss |
| Evidence failure | Evidence 缺失、过期、矛盾、不可追溯、未绑定或与 claim 不相关 | support/provenance | Evidence coverage 只是其中一部分 |
| State inconsistency | 同一 checkpoint 内或相邻 checkpoint 间，Goal/Context/Plan/Evidence/Action/Outcome 关系违反显式 invariant | relational state | 可以没有明显 hallucination，也可以尚未形成长期 drift |
| Execution error | Action 或 Outcome 不符合任务、环境或约束 | action/outcome | 可能由 state inconsistency 导致，也可能来自工具、环境或实现故障 |

## 1.3 Which layer SAEE studies

SAEE 不研究如何让 foundation model 本身“永不幻觉”。候选研究层位于：

```text
Model generation / tool choice
             ↓
Observable Agent operational state
             ↓
State checkpoint + lineage + comparison       ← SAEE candidate research layer
             ↓
Recommendation / Decision Context
             ↓
Human / IAM / Policy authorization
             ↓
External execution
```

SAEE 研究的是状态表示、差异测量、Evidence 充分性、checkpoint placement 和恢复建议。它不获取
模型隐藏状态，不替代模型训练、RAG、observability、security、IAM 或执行系统。

## 1.4 First-principles answers

### 为什么长期 Agent 需要 State Integrity？

因为长期任务的正确性依赖多个时间点之间的依赖关系；只看最终输出无法知道关键目标、约束或
Evidence 在何时遗失，也无法判断某个错误状态是否已经成为后续计划的前提。

### 为什么单次回答正确不足？

一次正确回答只证明一个局部输出。Agent 之后仍可能接受错误工具结果、丢失约束、无授权地重规划，
或产生与目标不一致的 Action。长期可靠性需要 transition-level evidence，而不是单点正确率。

### 为什么错误状态传播比错误答案更危险？

错误答案可以停留在一个输出；错误状态会改变后续选择空间，使每个局部合理的 Action 共同形成
整体错误。风险来自 dependency propagation，而不是简单由步数本身决定。

# 2. Agent State Model

## 2.1 Observable operational state

在 checkpoint `t`，定义：

```text
S_t^obs = <G_t, C_t, P_t, E_t, A_0:t, O_t, M_t>
```

其中：

| 对象 | 含义 | 最小可观察材料 |
|---|---|---|
| `G_t` Goal | 当前有效任务目标、范围、成功条件和停止条件 | versioned goal declaration / task contract |
| `C_t` Context | 下一步决策所依赖的事实、约束、权限与环境状态 | critical-context set + source refs + freshness |
| `P_t` Plan | 当前有效计划、步骤依赖、允许分支和 replan 依据 | versioned plan + supersession relation |
| `E_t` Evidence | 支持 claim、Action 和 continuation 的材料 | Evidence objects + provenance + relevance + status |
| `A_0:t` Action | 从起点到当前的已声明/已观测动作序列 | ordered trace events + external-effect markers |
| `O_t` Outcome | 当前产物、环境结果和验收状态 | artifacts + tests + side-effect observations + acceptance results |
| `M_t` Metadata | 身份、authority、时间、sequence、lineage 和 schema version | checkpoint id + actor refs + digests + timestamps |

`M_t` 是完整性支持元数据，不意味着 SAEE 拥有 identity 或 authorization 权力。

## 2.2 Authoritative baseline and allowed change

研究不能把“和初始状态不同”直接定义为 drift。Agent 必须能够接受新信息、纠正目标、重规划和更新
Evidence。因此每个 checkpoint 还需要：

```text
B_t = current authoritative baseline
U_t = allowed update envelope
J_t = justification and authorization references for change
```

State Integrity 要求：

1. `S_t^obs` 有可追溯来源；
2. 相对 `B_t` 的变化落在 `U_t` 内，或由 `J_t` 显式解释；
3. 内部关系不违反 invariant；
4. 对 missing / unobserved / unauthenticated 状态保持显式未知；
5. 下一 checkpoint 继承的是最新有效 baseline，而不是任意旧摘要。

## 2.3 State transition

候选 transition 表达：

```text
S_(t+1)^obs = T(S_t^obs, observation_(t+1), declared_change_(t+1), action_(t+1))
```

可能触发状态变化的事件包括：

- 用户或 Human Authority 更改目标；
- 新工具结果或环境观察；
- context compression、summary、retrieval 或 handoff；
- Agent replan；
- Evidence 增加、过期、撤回或发生矛盾；
- Action 执行与 side effect；
- Outcome 产生或验收失败。

研究重点不是阻止变化，而是区分：`authorized evolution`、`explained replan`、`benign variation`、
`unobserved change` 和 `integrity drift`。

## 2.4 State observability boundary

下列对象当前不可直接观测或不能仅凭声明证明：

- 模型内部 latent belief；
- 未记录的 tool/environment effect；
- 声明 trace 的真实性与完整性；
- Evidence 来源主体的真实身份；
- 隐藏 provider orchestration；
- Agent 没有表达的内部 uncertainty。

因此所有实验必须报告 `observed`、`declared`、`verified`、`missing`、`contradictory`、
`unauthenticated`，不能把它们压成一个“可信/不可信”二元值。

# 3. Integrity Model

## 3.1 Goal Integrity

**定义：** 当前有效 Goal 与 authority-approved Goal lineage、范围、成功条件和停止条件一致；任何
变化都能定位到有依据的 change event。

**失败模式：** scope creep、目标替换、局部 proxy 取代原目标、停止条件遗失、旧目标复活。

**可观察指标：**

- critical goal constraint preservation rate；
- unauthorized goal-change count；
- goal version ancestry completeness；
- success/stop-condition coverage；
- semantic goal deviation with reviewer agreement。

## 3.2 Context Integrity

**定义：** 当前决策能够检索并应用完成下一步所需的关键 Context，且 Context 的来源、适用范围、
新旧和冲突状态可见。

**失败模式：** context truncation、lost-in-the-middle、stale context、错误 summary、跨任务污染、
constraint omission。

**可观察指标：**

- critical-context recall / precision；
- constraint application rate；
- stale-context rate；
- summary omission / distortion rate；
- cross-task contamination rate；
- retrieval-to-action relevance。

## 3.3 Plan Integrity

**定义：** 当前计划是 Goal 和 Context 下的有效路线；已执行 Action 与计划、依赖和允许分支一致，
或存在显式 replan justification。

**失败模式：** silent replan、步骤跳过、依赖倒置、无解释分叉、继续执行已 superseded plan。

**可观察指标：**

- planned-action coverage；
- unplanned-action rate；
- dependency-order violations；
- replan justification completeness；
- superseded-plan execution count；
- plan-to-action edit distance（必须使用结构化 step identity，而非仅文本 embedding）。

## 3.4 Evidence Integrity

**定义：** 支持 continuation、claim 与 Outcome 的 Evidence 在类型、覆盖、相关性、新鲜度、
provenance、绑定和矛盾状态上满足声明要求。

**失败模式：** missing evidence、stale evidence、irrelevant evidence、unbound evidence、
contradictory evidence、伪造或无法认证的来源。

**可观察指标：**

- required-evidence coverage；
- provenance-binding rate；
- freshness / expiry conformance；
- claim-evidence relevance；
- contradiction rate；
- unauthenticated-evidence rate；
- evidence-to-action sufficiency judged against a frozen rubric。

## 3.5 Outcome Integrity

**定义：** 当前 Outcome 与 Goal、验收条件、允许 side effects 和已声明 Action 一致。

**失败模式：** local completion mistaken for task success、unobserved side effect、partial acceptance、
result/claim mismatch、artifact lineage break。

**可观察指标：**

- acceptance-requirement satisfaction；
- expected-vs-observed outcome delta；
- side-effect conformance；
- artifact lineage completeness；
- unsupported completion-claim rate；
- rollback feasibility evidence。

## 3.6 Action as the integrity bridge

本议程不单独建立第六个“Action Integrity”产品层。`A_0:t` 是 Plan 与 Outcome 之间的桥梁：

- 相对 Plan 的偏差进入 Plan Integrity；
- 相对 permission / external-effect boundary 的偏差进入 Action Drift 与边界观察；
- 相对 Outcome 的因果/lineage 缺口进入 Outcome Integrity。

# 4. Drift Model

## 4.1 Operational definition

```text
Drift_t = persistent or consequential deviation(
  S_t^obs,
  B_t,
  U_t,
  J_t,
  lineage
)
```

只有满足至少一个条件时才标记 drift candidate：

1. deviation 超出 allowed update envelope；
2. change 缺少 justification / lineage；
3. deviation 在后续 checkpoint 持续存在或放大；
4. deviation 已影响高影响 Action、Evidence judgment 或 Outcome；
5. state 内部 invariant 被破坏。

单点 anomaly、合法 replan、新 Evidence 导致的合理变化、表达风格变化都不自动等于 drift。

## 4.2 Drift classes

| Drift 类别 | 检测对象 | 候选检测信号 | 主要混淆因素 |
|---|---|---|---|
| Goal Drift | `G_t` vs `B_t.goal` | 关键约束被删除、范围无授权扩大、proxy 目标替换 | 合法需求变更、目标澄清 |
| Context Drift | `C_t` vs required context set | 约束遗失、stale source 被继续使用、错误摘要累积 | 有意压缩、无关信息删除 |
| Plan Drift | `P_t` / `A_t` vs valid plan | silent branch、dependency violation、旧计划执行 | 合法 replan、环境变化 |
| Evidence Drift | `E_t` vs requirements/lineage | coverage 下降、Evidence 过期、冲突增加、binding 断裂 | requirement 正常变化、新证据替换旧证据 |
| Action Drift | `A_t` vs plan/constraints | 未计划高影响动作、external effect 边界变化 | 必需的 emergency action、有授权人工干预 |
| Outcome Drift | `O_t` vs goal/acceptance | 局部结果被误报完成、side effect 超界 | acceptance criteria 变更、环境噪声 |

## 4.3 Detection families

未来研究应比较而不是预设一种 detector：

1. **Deterministic invariant checks**：ID、version、required field、permission boundary、dependency、
   Evidence expiry；可重复但只覆盖显式规则。
2. **Structured delta checks**：比较 checkpoint object、set、graph 和 sequence；需要稳定 state model。
3. **Semantic comparison**：模型或 embedding 比较 Goal/Context/Outcome；必须做 human calibration、
   adversarial test 和 uncertainty reporting。
4. **Temporal/change-point detection**：检测偏差持续或放大；异常不等于语义 drift。
5. **Counterfactual replay**：在 synthetic environment 比较 last-valid 与 drifted state；不能直接
   推断真实世界因果。
6. **Evidence verification**：provenance、digest、freshness、contradiction；完整性验证不自动证明
   原始事件真实性。

## 4.4 Detection ground truth

Drift benchmark 需要至少三类 ground truth：

- **Injected drift**：人工控制地删除约束、替换目标、打乱计划、使 Evidence 过期或产生冲突；
- **Benign change**：合法 replan、用户批准变更、新 Evidence 修正旧假设；
- **Natural trajectory**：真实或受控 Agent 长链运行，由多名 reviewer 标注。

没有 benign-change 对照，detector 只会学习“变化即风险”；没有 natural trajectory，synthetic
结果不能支持外部可靠性主张。

# 5. Measurement Framework

## 5.1 Measurement principles

1. 先保留维度向量，后讨论聚合分数；
2. 指标必须绑定 baseline、time、actor、scope 和 allowed change；
3. observation coverage 与 integrity result 分开；
4. deterministic 与 semantic measurement 分开报告；
5. detector performance 与 Agent task performance 分开；
6. detection benefit 与 checkpoint latency/cost 一起测量；
7. 预注册 threshold，不能看完结果后改成功定义。

## 5.2 State Distance

候选表达：

```text
D_t = [d_goal, d_context, d_plan, d_evidence, d_action, d_outcome]
```

`D_t` 默认是多维向量，不是单一 trust score。每个 `d_*` 必须声明：

- comparison target；
- metric type（rule/set/graph/sequence/semantic）；
- missing-data behavior；
- calibration dataset；
- confidence / reviewer agreement；
- whether higher means worse。

在跨领域校准和 value validation 前，不允许把不同维度任意加权为一个“State Integrity Score”。

## 5.3 Candidate metric set

| 指标 | 研究定义 | 适用层 | 主要风险 |
|---|---|---|---|
| Goal Alignment | 满足冻结 Goal constraints 的比例与语义偏差 | Goal | embedding 相似不等于目标一致 |
| Critical Context Recall | 当前决策使用的关键 context / ground-truth required context | Context | ground truth 构造困难 |
| Context Staleness | 过期或 superseded context 被使用的比例 | Context | 不同事实 freshness 不同 |
| Plan Deviation | 未被 valid plan 或 replan justification 覆盖的 Action 比例 | Plan/Action | 计划粒度会改变结果 |
| Evidence Coverage | present required Evidence / required Evidence | Evidence | 不测真实性、质量和相关性 |
| Evidence Binding | 有 provenance/digest/actor/claim binding 的 Evidence 比例 | Evidence | hash 不证明源事件真实 |
| Evidence Contradiction | 同一 claim 下未解决矛盾 Evidence 的比例 | Evidence | 需要 claim model |
| Outcome Alignment | 满足 acceptance criteria 的比例 | Outcome | acceptance criteria 可能不完整 |
| Side-effect Conformance | observed effect 落入 declared allowed effects 的比例 | Action/Outcome | 未观测 effect 会造成假阴性 |
| Drift Detection Precision/Recall | 对 injected/natural drift 的分类性能 | Detector | reviewer disagreement |
| Detection Delay | drift onset 到首次正确标记的 checkpoint 数/时间 | Detector | onset 可能不唯一 |
| Recovery Success | 恢复后重新满足 baseline/invariants 的比例 | Recovery | 回到旧状态不一定是正确结果 |
| Recovery Cost | 人工、token、时间、重做 Action 和 rollback cost | Recovery | 成本跨环境不可直接比较 |
| Checkpoint Overhead | latency/token/context/preparation cost | System | overhead 可能抵消价值 |

## 5.4 Experimental unit and controls

最小研究单元不是“一个回答”，而是：

```text
one task
+ versioned baseline
+ ordered checkpoints
+ declared transitions
+ state/evidence lineage
+ final outcome
```

推荐控制变量：同一 task/fixture/model/runtime；只改变某一个 state dimension 或 checkpoint
strategy。需要同时保留：

- no-checkpoint control；
- evidence-only checkpoint；
- full candidate state comparison；
- benign-change negative control；
- unauthenticated-input boundary case。

## 5.5 Measurement validity gates

```text
MEASUREMENT_VALID_IF=
BASELINE_BOUND
AND_ALLOWED_CHANGE_BOUND
AND_CHECKPOINT_ORDER_BOUND
AND_OBSERVATION_COVERAGE_DECLARED
AND_GROUND_TRUTH_METHOD_DECLARED
AND_THRESHOLD_PRECOMMITTED
```

缺任一项时可输出 exploratory result，但不能输出 calibrated drift claim。

# 6. Current SAEE Position

## 6.1 `evaluate_agent_run` classification

当前 `saee.evaluate_agent_run`：

- 输入一个 declared `agent_id`、`task`、trace events 和 Evidence list；
- 根据 `high_impact` / `external_effect` 选择 required Evidence；
- 对 `TEST_RESULT`、`ROLLBACK_PLAN`、`PERMISSION_BOUNDARY`、`HUMAN_APPROVAL` 计算
  required-evidence coverage；
- 输出 `CONTINUE`、`HUMAN_REVIEW_REQUIRED`、`REPLAN` 或 `STOP`；
- 不执行 Agent，不认证 trace/Evidence，不批准外部动作。

因此：

```text
CURRENT_CAPABILITY=saee.evaluate_agent_run
CURRENT_CLASSIFICATION=EVIDENCE_INTEGRITY_CHECKPOINT_SINGLE_DECLARED_SNAPSHOT
CHECKPOINT_VERSION=1.0_CANDIDATE
CHECKPOINT_DETERMINISTIC=true
CHECKPOINT_INPUT_AUTHENTICATED=false
CHECKPOINT_LONGITUDINAL=false
```

## 6.2 What exists

| 研究需要 | 现有资产 | 状态 |
|---|---|---|
| Evidence requirement/coverage | `saee.evaluate_agent_run` / `saee.evaluate_evidence` | `implemented`, local alpha |
| Structured trace candidate | trace events + `saee.otel_style_candidate_mapping` | partial/experimental boundary |
| Stateful synthetic transitions | stateful rehearsal architecture/runtime | bounded internal asset, not general Agent state layer |
| Canonical fact and staged truth | governance registry + capability inventory | implemented repository control-plane metadata |
| Receipt/digest lineage | local receipts and Evidence subsystem assets | partial; authenticity non-claim remains |
| Local Agent interface | MCP/CLI/schema/Skill surfaces | local, not public/production validation |

## 6.3 What is missing

Canonical inventory and implementation review show no current capability for：

- versioned Goal/Context/Plan/Outcome state object；
- checkpoint-to-checkpoint comparison；
- state distance or drift detector；
- trusted trace-to-evidence conversion；
- external identity/delegation binding；
- continuous monitoring trigger；
- last-known-valid recovery evaluation；
- calibrated multi-dimensional benchmark；
- external/customer validation。

```text
GOAL_INTEGRITY_IMPLEMENTED=false
CONTEXT_INTEGRITY_IMPLEMENTED=false
PLAN_INTEGRITY_IMPLEMENTED=false
EVIDENCE_INTEGRITY_IMPLEMENTED=partial
OUTCOME_INTEGRITY_IMPLEMENTED=false
DRIFT_DETECTION_IMPLEMENTED=false
INTEGRITY_RECOVERY_IMPLEMENTED=false
```

# 7. Research Roadmap

每个 Stage 是研究 gate，不是自动开发序列。

## Stage 1 — Checkpoint Integrity

**目标：** 明确单 checkpoint 能否准确识别 Evidence Gap，并改善 continuation decision。

**复用：** `saee.evaluate_agent_run`，不新增 capability/schema/protocol。

**实验：** frozen single-run packets；missing/stale/contradictory Evidence；与普通 Agent summary 和
human review 比较。

**通过条件：** Evidence gap precision/recall、decision utility 和 preparation/latency cost 预注册后
达到阈值；Recommendation 不被理解为 Authorization。

**停止条件：** 结构化输出不改善决策，或成本超过价值。

## Stage 2 — Multi-checkpoint State Comparison

**目标：** 证明跨 checkpoint 比较能区分 drift 与合法变化。

**研究设计：** 3–10 个有序 checkpoint；每次只注入一个 dimension drift，并包含 benign replan
negative controls。

**先决条件：** Stage 1 有价值；另行 evolution proposal；duplicate-build/reuse review 完成。

**通过条件：** 六维 distance vector 可重复，且对 drift/benign change 有可接受 precision、recall、
reviewer agreement 和 detection delay。

## Stage 3 — Continuous Integrity Monitoring

**目标：** 研究 checkpoint placement，而不是默认每一步检查。

**候选触发：** milestone、handoff、context compression、replan、高影响 Action 前、Evidence 变化、
Outcome claim 前。

**核心指标：** detection benefit、latency、token cost、false positive、Agent behavior change 和
checkpoint fatigue。

**停止条件：** continuous checking 只增加 observability/文本，不改善 Action 或 Outcome。

## Stage 4 — Integrity Recovery

**目标：** 漂移发现后，研究哪种恢复建议最能回到有效执行路线。

候选恢复操作仅作为 recommendation：

1. pause at checkpoint；
2. retrieve authoritative Goal/critical Context；
3. select last-known-valid checkpoint；
4. invalidate stale Plan/Evidence；
5. request missing Evidence or Human Context；
6. replan from valid baseline；
7. re-evaluate before consequential Action；
8. where separately authorized, route rollback to the responsible execution system。

SAEE 不自动执行 rollback、撤销 Action 或扩大权限。

**通过条件：** recovery success 相比无恢复/简单 retry 更高，且不造成更大 side effect。

## Stage gates summary

```text
Stage_1=RESEARCHABLE_WITH_EXISTING_CAPABILITY
Stage_2=DESIGN_ONLY_REQUIRES_NEW_AUTHORIZATION
Stage_3=NOT_AUTHORIZED
Stage_4=NOT_AUTHORIZED
CONTINUOUS_STATE_INTEGRITY_IMPLEMENTED=false
```

# 8. Competitive Boundary

| 相邻类别 | 它主要解决什么 | 为什么不等于 State Integrity | 可作为何种输入 |
|---|---|---|---|
| LLM capability improvement | 更好的生成、推理、tool use 与 planning | 提升平均能力不证明某次长期状态仍与基线一致 | model/action producer |
| RAG | 检索外部知识并加入生成上下文 | retrieval 命中不证明 Context 被正确应用，也不比较 Goal/Plan/Outcome lineage | Context/Evidence source |
| Observability | 记录和分析 traces、runs、spans、threads、latency 和 errors | “看见发生了什么”不自动给出 relative-to-baseline integrity judgment | trace/telemetry source |
| Security | 发现漏洞、攻击、恶意内容、供应链和配置风险 | 安全属性只是状态约束的一部分；State Integrity 不替代 threat detection | risk Evidence |
| IAM | 建立 identity、role 和 access privilege | IAM 决定谁能做什么；State Integrity 只检查声明身份/权限边界是否进入当前状态 | authority/permission Evidence |
| Audit | 事后检查记录和责任 | audit Evidence 可用于 checkpoint，但持续完整性还需前置比较与恢复路径 | historical Evidence |

候选新层只有在下列组合被验证后才成立：

```text
versioned operational state
+ checkpoint lineage
+ allowed-change semantics
+ cross-checkpoint comparison
+ evidence provenance
+ non-authorizing recovery context
```

如果最终只能提供 traces、dashboard 或单次 evaluation，则不应声称形成新的 State Integrity layer。

# 9. Scientific Questions

## 9.1 Core research questions

1. **RQ1 — Representation:** 最小 operational state 是否必须同时包含 Goal、Context、Plan、
   Evidence、Action、Outcome，还是存在可证明的更小充分表示？
2. **RQ2 — Observability:** 在 latent model state 不可见时，哪些 observable artifacts 足以支持
   有用但不过度承诺的 integrity judgment？
3. **RQ3 — Drift measurement:** 如何建立对任务、模型和 Agent framework 可迁移的多维 State
   Distance，而不退化为不透明 trust score？
4. **RQ4 — Legitimate change:** detector 如何区分有授权 replan、新 Evidence 修正和真正 drift？
5. **RQ5 — Propagation:** 哪些早期 state inconsistency 最可能在长链中传播并影响高影响 Action？
6. **RQ6 — Checkpoint placement:** milestone-based、event-based 与 fixed-interval checkpoint 哪种
   在 detection benefit / overhead 上更优？
7. **RQ7 — Evidence sufficiency:** continuation decision 所需 Evidence 是否可以跨任务泛化，还是
   必须由领域 rubric 定义？
8. **RQ8 — Recovery:** last-known-valid recovery、context rehydration、replan 和 human review 分别
   在什么 drift 类型下有效？
9. **RQ9 — Evaluator validity:** deterministic rules、LLM judge 与 hybrid detector 的 precision、
   calibration、bias 和 adversarial robustness 如何比较？
10. **RQ10 — Incremental value:** State Integrity 相比 observability、Agent self-review、CI 和普通
    human review 是否产生增量行为/Outcome 改善？

## 9.2 Candidate falsifiable hypotheses

| Hypothesis | 支持证据 | 反证/停止条件 |
|---|---|---|
| H1: 多维 checkpoint 比最终输出 review 更早发现 consequential drift | detection delay 降低且 precision 不显著下降 | 只增加误报或没有更早发现 |
| H2: Evidence Integrity Checkpoint 改善 continuation decision | reviewer/Agent 下一步更具体且错误推进减少 | 输出只是更长报告，行为不变 |
| H3: checkpoint benefit 随 dependency horizon 增加 | 长链组相对短链组收益更高 | 收益与 horizon 无关或由提示长度解释 |
| H4: allowed-change semantics 可降低 drift false positive | benign replan 误报显著下降 | detector 仍把变化等同 drift |
| H5: last-known-valid recovery 优于 blind retry | recovery success 提升且 side effect 不增加 | 与 retry 无差异或成本更高 |
| H6: State Integrity 提供 observability 之外的增量价值 | 相同 trace 下产生更好 decision/Outcome | 结果可被普通 trace review 完全复制 |

## 9.3 Candidate paper sequence

1. **Definition paper:** Operational Agent State Integrity：state、baseline、allowed change、drift、
   integrity 与 non-claims；
2. **Benchmark paper:** controlled multi-dimensional drift and benign-change benchmark；
3. **Checkpoint paper:** checkpoint placement、detector comparison 与 Evidence sufficiency；
4. **Recovery paper:** last-known-valid recovery、replan 和 human-review routing；
5. **Systems paper:** 只有前述研究成立后，才讨论 low-overhead continuous infrastructure。

## 9.4 Research quality requirements

- 公开区分 peer-reviewed paper、preprint、official benchmark page 和 SAEE hypothesis；
- 预注册 metrics、thresholds、exclusions 和 stop conditions；
- 保存 raw trajectory、annotation rubric、inter-rater agreement 和 failed attempts；
- 报告 negative result；
- 不用同一 LLM 同时生成 drift、判断 drift 并解释成功而不做独立校准；
- 不从 synthetic pass 推导 enterprise reliability；
- 不从 correlation 推导错误状态传播的因果关系。

## 9.5 Initial literature anchors

以下来源用于界定问题，不构成 SAEE 已被验证：

- Liu et al., [Lost in the Middle: How Language Models Use Long Contexts](https://aclanthology.org/2024.tacl-1.9/), TACL 2024：长上下文中信息位置会影响模型利用效果。
- Packer et al., [MemGPT: Towards LLMs as Operating Systems](https://arxiv.org/abs/2310.08560), preprint：用分层 memory / virtual context 管理扩展上下文。
- METR, [Task-Completion Time Horizons of Frontier AI Models](https://metr.org/time-horizons/)：用人类完成时间估计 Agent 在不同任务时长下的成功 horizon。
- Wang et al., [The Long-Horizon Task Mirage?](https://arxiv.org/abs/2604.11978), 2026 preprint：跨领域诊断 long-horizon failure behavior。
- Xu et al., [LongDS-Bench](https://arxiv.org/abs/2605.30434), 2026 preprint：以 evolving analytical state、rollback 和 multi-state composition 测试长期 Agent。
- Liu et al., [Context as a Tool](https://aclanthology.org/2026.findings-acl.1032/), Findings ACL 2026：把 context maintenance 作为 long-horizon SWE Agent 的显式操作。
- [LangSmith observability concepts](https://docs.langchain.com/langsmith/observability-concepts) 与 [Arize Phoenix](https://arize.com/docs/phoenix/)：相邻 observability/evaluation 边界的官方产品资料。
- NIST, [Identity and Access Management](https://csrc.nist.gov/glossary/term/Identity_and_access_management)：IAM 边界的规范术语来源。

# 10. Non-Claims and Stop Conditions

## 10.1 Non-claims

本研究议程不主张：

- SAEE 已解决 hallucination、drift、context loss 或长期 Agent reliability；
- Agent 的 latent state 可由外部 checkpoint 完整读取；
- operational state 等于模型真实信念；
- 所有变化都是 drift；
- 一个 State Distance 总分可以跨领域表达 trust；
- Evidence presence 证明 Evidence 真实、相关或充分；
- checkpoint Recommendation 是 Authorization；
- SAEE 替代 LLM、RAG、observability、security、IAM、audit 或 Agent runtime；
- `saee.evaluate_agent_run` 已完成多 checkpoint comparison；
- 当前研究方向已完成商业验证、客户验证或生产部署；
- 本议程授权代码、schema、MCP、Capability、Skill 或 protocol 开发。

## 10.2 Research stop conditions

应暂停或否决 State Integrity 基础设施扩展，如果：

- operational state 无法以可接受成本构造；
- detector 无法区分合法变化与 drift；
- State Integrity 不比普通 trace review / Agent self-review 提供增量价值；
- checkpoint overhead 抵消行为收益；
- recovery 建议提高 side effect 或错误自信；
- 结果高度依赖单一模型、fixture 或 evaluator，不能复现；
- 研究只能生成更复杂的审计报告，而不能改善 continuation/replan/stop decision；
- 该方向开始取代宪法工程核心或当前 Agent Evidence integration mainline。

长期边界继续冻结：

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
SAEE_EXTERNAL_WORLD_EXECUTION=false
```

# 11. Final Status

```text
STATE_INTEGRITY_RESEARCH_AGENDA_STATUS=COMPLETE
SAEE_POSITIONING=AGENT_STATE_INTEGRITY_INFRASTRUCTURE_CANDIDATE
SAEE_POSITIONING_STATUS=CANDIDATE_NOT_CONSTITUTIONALLY_EFFECTIVE
CURRENT_EVALUATION_AS_CHECKPOINT=true
CURRENT_CHECKPOINT_SCOPE=DECLARED_EVIDENCE_READINESS_SINGLE_SNAPSHOT
OPERATIONAL_STATE_MODEL_DEFINED=true
LATENT_MODEL_STATE_OBSERVED=false
DRIFT_MODEL_DEFINED=RESEARCH_DESIGN_ONLY
MEASUREMENT_FRAMEWORK_DEFINED=RESEARCH_DESIGN_ONLY
INTEGRITY_RECOVERY_DEFINED=RESEARCH_AGENDA_ONLY
CONTINUOUS_STATE_INTEGRITY_IMPLEMENTED=false
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
SKILL_CHANGED=false
PROTOCOL_CREATED=false
COMMERCIAL_VALIDATION=false
PRODUCTION_READY=false
NEXT_ACTION=HUMAN_REVIEW_OF_RESEARCH_AGENDA
```
