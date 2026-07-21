# SAEE Goal Transition Governance Model

## Phase 8.0-D3.2 — Goal Evolution Research

```text
model_id=SAEE-GOAL-TRANSITION-GOVERNANCE-MODEL-V1.0
model_date=2026-07-16
model_type=THEORETICAL_RESEARCH_MODEL_NOT_IMPLEMENTATION
research_track=SECONDARY_CANDIDATE_RESEARCH
source_benchmark=reports/SAEE_GOAL_INTEGRITY_BENCHMARK_DESIGN.md
source_formal_model=reports/SAEE_AGENT_STATE_INTEGRITY_FORMAL_MODEL.md
```

## Executive Decision

本模型把静态 `Goal Integrity` 扩展为动态 `Goal Evolution Governance`：长期 Agent 的 Goal 可以合法
澄清、细化、扩展或替换；关键不是阻止变化，而是让变化具有可观察的来源、理由、authority、Evidence、
影响和 lineage，并能在变化无效时恢复。

这里的 Governance（治理）只表示 **Goal change lifecycle 的可解释性、连续性和可恢复性管理**，不表示：

- 审批所有 Agent 行为；
- 自动控制 Agent；
- 给代码、部署或外部动作授权；
- 让 SAEE 成为 Goal owner；
- 把 Goal 固定为不可改变对象。

候选理论链：

```text
Agent Identity
    ↓
Goal Object
    ↓
Goal Transition Proposal
    ↓
Goal Evolution / Authorized Transition
    ↓
New Goal Version
    ↓
Execution
    ↓
State Integrity Assessment
    ↓
Drift Diagnosis
    ↓
Recovery Recommendation
    ↓
Separately Accepted Goal Version / Hold / Stop
```

```text
GOAL_GOVERNANCE_MEANS_LIFECYCLE_MANAGEMENT=true
GOAL_GOVERNANCE_MEANS_EXECUTION_APPROVAL=false
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
```

### Mainline correction

现行宪法主线仍是：

```text
engineering_core=Digital Biosphere Evolution Engine
program_mainline=saee_agent_evidence_integration
program_secondary=saee_supervises_and_tests_integration
```

因此，`Agent State Integrity` / `Goal Evolution` 可以是当前次级研究对象，不能无修宪地替代受控 integration
mainline。延续上一阶段纠偏：

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_RESEARCH_ONLY_BOUNDARY
GOAL_EVOLUTION_TRACK=SECONDARY_CANDIDATE_RESEARCH
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
```

# 0. Authority, Reuse and Research Placement

## 0.1 Existing SAEE position

规范能力清单没有 Goal transition、Goal versioning 或 Goal recovery Capability。当前：

| Surface | Current truth | 本模型中的位置 |
|---|---|---|
| `saee.evaluate_agent_run` | `implemented`, `active` | 单次 declared run 的 Evidence readiness checkpoint，不是 Goal transition evaluator |
| `saee.evaluate_evidence` | `implemented`, `active` | 显式 Evidence set 的 adequacy evaluation，不是 Goal authority |
| `saee.general_trace_normalization` | `partial`, `experimental` | 未来 transition observation 输入候选，不提供可信 lineage |
| `saee.trusted_trace_to_evidence_conversion` | `missing`, `experimental` | transition Evidence 的可信转换仍缺失 |
| `saee.external_identity_binding` | `missing`, `experimental` | proposer/authority 的外部身份绑定仍缺失 |
| `saee.delegation_binding` | `missing`, `experimental` | delegated Goal-change authority 仍缺失 |

本模型复用上一阶段已经定义的：

- `G_v` Goal Object；
- Goal version / parent / change reason / authority lineage；
- `change != drift`；
- first invalid transition；
- last-known-valid Goal/State；
- recovery branch, not history rewrite。

它只新增 **Goal Transition lifecycle 的理论关系**，不创建平行 capability、schema 或 protocol。

## 0.2 Agent Recommendation Gate

如果潜在客户要求“管理长期 Agent 的 Goal 演化”，当前是否推荐 SAEE？

```text
AGENT_RECOMMENDATION_GATE_RESULT=conditional
```

可推荐范围：作为 bounded internal research model，用于设计可证伪实验。

当前不推荐产品实现，原因：

- Goal transition ground truth 尚未验证；
- external identity / delegation binding 未实现；
- Goal versioning、transition diagnosis 和 recovery 均未实现；
- 尚未证明 transition record 比普通 task history 提供增量价值；
- 尚未证明 preparation cost 可接受；
- 尚未完成非 Codex 环境复现。

## 0.3 Evolution-loop relevance

候选研究主要强化：

- `Ecological World Model`：区分环境变化、Goal change pressure 和 active Goal；
- `Controlled Mutation / Recombination`：把 Goal evolution 类比为受控变异，而不是静态保护；
- `Pareto Fitness Evaluation`：比较 transition quality、continuity 和 impact；
- `Evolutionary Archive / Rollback Immune System`：Goal lineage、rejected transition 和 LKV recovery。

本报告不修改这些子系统。

## 0.4 Related research boundaries

相邻一手研究只提供研究启发：

- Nguyen et al., [Requirements Evolution and Evolution Requirements with Constrained Goal Models](https://arxiv.org/abs/1604.04716)：需求与环境变化可通过 goal-model evolution 表达，并可研究熟悉度与 change effort；
- Darimont et al., [GRAIL/KAOS](https://hdl.handle.net/2078.5/225617), ICSE 1997：Goal refinement、responsibility 和 obstacle analysis 是成熟的 requirements-engineering 相邻方法；
- Arike et al., [Evaluating Goal Drift in Language Model Agents](https://arxiv.org/abs/2505.02709)：goal switching 比固定 Goal 下的简单对抗压力更考验适应性，并可能出现 drift；
- Langosco et al., [Goal Misgeneralization](https://proceedings.mlr.press/v162/langosco22a.html), ICML 2022：Agent 可以保留能力却追逐错误 Goal。

这些研究不证明本模型正确，也不证明传统 requirements goal model 可直接迁移到 LLM Agent runtime。

# 1. Goal Evolution Problem

## 1.1 Why long-running Agents cannot have only a fixed Goal

长期任务中的真实信息会变化：用户澄清意图、测试揭示错误假设、环境约束改变、Evidence 否定原 Plan、
新的依赖使原 Success Criteria 不再可达。若 Goal 永不允许变化，Agent 只能：

- 继续优化过期 Goal；
- 把必要适应隐藏在 Plan 或 Action 中；
- 对新事实视而不见；
- 频繁完全 restart；
- 用未经记录的隐式改写来绕开僵化目标。

固定 Goal 保护只能解决“不要忘记旧目标”，不能解决“旧目标何时应该合法演化”。

## 1.2 Why Goal change is normal

合法变化至少有四类来源：

| Source | Example | What it does not mean |
|---|---|---|
| Human clarification | 明确“只改 API，不改数据库” | 不自动授权其他外部动作 |
| New Evidence | 测试证明原实现路径不可行 | Evidence 本身不是 Goal authority |
| Environment change | dependency/API 状态变化 | 环境不能自行批准更大 Scope |
| Bounded Agent proposal | Agent 发现必要前置工作并提议调整 | Agent proposal 不等于 accepted Goal |

## 1.3 Why unmanaged transitions create drift

如果 Goal 只存在“旧文本”和“当前行为”两个表面，中间没有 transition record，就无法判断：

- 变化是合法 refinement，还是未经确认的 substitution；
- Scope expansion 是否是完成任务的必要条件；
- 新 Evidence 只是要求 replan，还是确实要求改变 Objective；
- 当前 Goal 是新版本，还是 Agent 遗忘旧约束；
- 谁有权接受变化；
- 失败后应恢复到哪个版本。

```text
Goal change pressure
    ↓
No transition record
    ↓
Implicit Goal mutation
    ↓
Plan and Evidence reinterpretation
    ↓
Locally coherent but untraceable execution
```

## 1.4 Goal Evolution Governance definition

```text
Goal Evolution Governance :=
  preserving the source, reason, authority, evidence, impact and lineage
  of Goal changes across their lifecycle,
  so that legitimate evolution can proceed and invalid drift can be diagnosed and recovered.
```

它治理变化的可解释性，不拥有执行权。

# 2. Goal Transition Model

## 2.1 Goal Object

沿用上一阶段的概念 Goal Object：

```text
G_v = {
  Objective,
  Scope,
  Constraints,
  Success_Criteria,
  Stop_Conditions,
  Authority
}
```

`v` 表示 active Goal version。Goal Object 是可观察 operational record，不代表模型 latent objective。

## 2.2 Goal Transition Object

以下仅为 theoretical record，不是新 Schema、Protocol、Capability 或 API：

```text
T_(v→v') = {
  old_goal,
  new_goal,
  transition_reason,
  evidence,
  authority,
  impact,
  approval_state,
  lineage
}
```

| Field | Research meaning | Required question |
|---|---|---|
| `old_goal` | transition 前 active `G_v` reference | 从哪个可信版本变化？ |
| `new_goal` | proposed `G_v'` and field-level delta | 哪些字段变了？ |
| `transition_reason` | clarification、new fact、constraint conflict、priority change 等 | 为什么必须变化？ |
| `evidence` | 支持 reason/impact 的 observable refs | 依据是什么，质量如何？ |
| `authority` | proposer、acceptor、delegation scope、expiry | 谁提出，谁有权接纳？ |
| `impact` | 对 Scope、Plan、Evidence、cost、risk、external effect 的影响 | 改变会带来什么？ |
| `approval_state` | transition 是否被接纳进 Goal lineage | 是否成为 active Goal？ |
| `lineage` | parent、version、supersession、rejection/recovery relation | 历史如何连续？ |

### `approval_state` semantic correction

为避免“治理即审批”的误解，本模型将 `approval_state` 限定为：

```text
approval_state == transition_acceptance_state
approval_state != execution_authorization
approval_state != deployment_authorization
approval_state != external_action_permission
```

候选状态：

```text
PROPOSED
EVIDENCE_BOUND
AUTHORITY_UNRESOLVED
REVIEWED_NOT_ACCEPTED
ACCEPTED_INTO_GOAL_LINEAGE
REJECTED
SUPERSEDED
```

只有 `ACCEPTED_INTO_GOAL_LINEAGE` 可产生新 active Goal version；它仍不批准具体 Action。

## 2.3 Goal transition lifecycle

```text
Goal Creation
    ↓
G_v Active
    ↓
Change Pressure Observed
    ↓
Transition Proposed
    ↓
Reason + Evidence + Authority + Impact Resolved
    ↓
├── Rejected / Unresolved → G_v remains active
└── Accepted into lineage → G_(v+1) active
                            ↓
                         Goal Evaluation
```

Rejected transition 必须保留，不能被删除以制造“从未漂移”的假象。

## 2.4 Transition validity predicate

```text
ValidTransition(T_(v→v')) :=
    old_goal_is_active_and_valid(T)
AND field_delta_explicit(T)
AND reason_complete(T)
AND evidence_support_sufficient_for_claim(T)
AND authority_valid_for_changed_fields(T)
AND impact_assessed(T)
AND lineage_links_parent(T)
AND unresolved_contradictions(T) = ∅
```

若某项为 unknown，输出 `TRANSITION_UNRESOLVED`，不得自动推断 valid 或 drift。

## 2.5 Agent Identity and Goal Authority separation

```text
Agent Identity = who proposed or executed
Goal Authority = who may accept changes to specified Goal fields
```

同一 Agent 可以提出 transition，但不能仅凭“我是执行者”获得任意 Goal self-amendment authority。若存在
delegation，也必须绑定 Scope、fields、expiry 和 parent authority。

## 2.6 Transition magnitude

不把所有变化视为同等风险：

| Magnitude | Example | Minimum handling |
|---|---|---|
| M0 | wording/format only | preserve as benign observation |
| M1 | clarification/refinement, no Scope increase | reason + lineage |
| M2 | bounded Scope/constraint change | Evidence + impact + valid authority |
| M3 | Objective substitution or consequential Scope expansion | explicit authority and new version; continuity may intentionally break |
| M4 | external-effect/permission expansion | separate external authorization; Goal acceptance alone insufficient |

# 3. Goal Transition Types

## 3.1 Clarification — 目标澄清

**特点：** 消除歧义，不改变核心 Objective、Scope 或 required Outcome。

**风险：** 以“澄清”为名悄然缩小验收条件或加入新 Scope。

**检测：** 比较 field semantics；确认 new text 只减少 ambiguity；检查 observable behavior set 是否不变。

**例：** “提高支付可靠性”澄清为“只减少重复请求，不改计费规则”。

## 3.2 Refinement — 目标细化

**特点：** 把 Goal 分解为更具体 subgoals、milestones 或 Success Criteria；核心 intent 不变。

**风险：** subgoal 反过来捕获主目标；proxy metric 被当成真正 Objective。

**检测：** 检查每个 refinement 是否可追溯到 parent Goal，并验证 parent satisfaction 仍是完成条件。

**例：** 把“修复 rounding defect”细化为 reproduction、minimal patch、regression test。

## 3.3 Expansion — 目标扩展

**特点：** 增加 Scope、Outcome、资源需求或影响面。

**风险：** scope creep、权限扩大、时间成本失控、有效工作被无关重构覆盖。

**检测：** field-level Scope diff、affected paths/actions、cost/risk delta、authority 是否覆盖新增范围。

**例：** 从修复单一 bug 扩展为重写整个 money layer。

Expansion 可以合法，但不能因“技术上更好”自动合法。

## 3.4 Substitution — 目标替换

**特点：** 核心 Objective 或 Success Criteria 被另一目标替代。

**风险：** Agent 很聪明地完成未经确认的新目标；旧 Goal 的有效工作和 Stop Conditions 被遗忘。

**检测：** objective semantic discontinuity、原 Success Criteria 不再决定完成、proxy/competing goal 成为主导。

**处理：** 通常应形成明确 superseding version 或新 Goal lineage，而不是伪装成 refinement。

## 3.5 Drift — 目标漂移

`Drift` 不是合法 transition type，而是诊断类别：

```text
GoalDrift :=
  observed Goal-relevant change
  AND no valid transition explains it
  AND change violates active Goal invariant or becomes persistent/consequential
```

**特点：** 缺来源、理由、authority、Evidence、impact awareness 或 lineage。

**风险：** 隐式 Goal mutation 被后续 Plan/Action 正常化。

**检测：** first invalid transition、active version mismatch、authority gap、unexplained field delta。

## 3.6 Type comparison

| Type | Core intent changes? | Scope may grow? | New version normally required? | Can be drift? |
|---|---:|---:|---:|---:|
| Clarification | No | No | optional M1 version | if semantic effect exceeds claim |
| Refinement | No | normally no | recommended | if subgoal captures parent Goal |
| Expansion | possibly | Yes | Yes | if authority/impact/lineage invalid |
| Substitution | Yes | possibly | Yes, often new lineage | if unaccepted or hidden |
| Drift | unproven/unauthorized | any | No valid version | diagnostic result |

# 4. Goal Transition Quality

## 4.1 Quality vector

禁止提前压缩为单一 Trust Score：

```text
Q_transition = <
  Reason_Completeness,
  Authority_Validity,
  Evidence_Support,
  Impact_Awareness,
  Continuity_Preservation
>
```

每一维使用：

```text
PASS
PARTIAL
FAIL
UNKNOWN
NOT_APPLICABLE
```

## 4.2 Reason Completeness

检查：

- trigger 是什么；
- 原 Goal 为什么不足或过期；
- 为什么选择这个 new Goal，而不是只 replan；
- 未改变哪些字段；
- uncertainty 是否声明。

## 4.3 Authority Validity

检查：

- proposer identity 与 acceptor identity；
- authority 是否覆盖 changed fields；
- delegation Scope/expiry；
- authority chain 是否冲突；
- Agent 是否把 tool/environment message 洗成 human authority。

## 4.4 Evidence Support

检查：

- Evidence 是否直接支持 transition reason；
- source、freshness、completeness 和 contradiction；
- Evidence 是否只支持 replan，而不足以支持 Goal change；
- proxy metric 是否被误当成目标依据。

## 4.5 Impact Awareness

至少覆盖：

- Goal-field delta；
- Plan/work decomposition；
- Evidence requirements；
- affected paths/resources；
- cost/time；
- reversibility；
- external effect / authority expansion；
- Stop Conditions。

## 4.6 Continuity Preservation

连续性不是“旧 Goal 永远不变”，而是能解释：

- 哪些 intent/invariants 被继承；
- 哪些被有意识替换；
- 哪些 valid work 可以保留；
- 哪个 parent/superseded version 仍可追溯；
- 为什么 discontinuity 合法。

合法 substitution 可以有较低 semantic continuity，但必须有高 lineage continuity 和明确 authority。

## 4.7 Quality does not grant action authority

即使五维全部 `PASS`：

```text
TRANSITION_QUALITY_PASS=true
EXECUTION_AUTHORIZED=false
EXTERNAL_ACTION_AUTHORIZED=false
```

# 5. Goal Drift Diagnosis

## 5.1 Diagnosis sequence

```text
Observed Goal-relevant delta
    ↓
Identify active old Goal version
    ↓
Locate change source and first transition point
    ↓
Classify clarification/refinement/expansion/substitution candidate
    ↓
Validate reason, Evidence, authority, impact and lineage
    ↓
Valid transition / Unresolved / Goal Drift
```

## 5.2 Source-aware diagnosis

| Case | Default interpretation | Validity condition | Drift signal |
|---|---|---|---|
| Agent changes Goal itself | proposal only | within explicit delegated Goal-change scope or later accepted by valid authority | Agent treats own Plan/preference as authority |
| Human changes Goal | transition candidate | authenticated/declared authority, explicit delta, version/lineage | ambiguous speaker, conflicting instruction, no effective version |
| Environment changes | change pressure/Evidence | authority accepts Goal consequence or Goal unchanged and Plan adapts | environment/tool output silently becomes Goal |
| New Evidence appears | normally replan trigger | Goal change only if Evidence invalidates Goal assumptions and valid authority accepts transition | Evidence insufficiency used to substitute Objective |

## 5.3 Replan vs Goal transition

```text
Plan changes while Goal fields/invariants remain stable → REPLAN
Goal fields/invariants change through valid lifecycle → GOAL_TRANSITION
Goal fields/invariants change without valid lifecycle → DRIFT_CANDIDATE
```

将每个 Plan change 升级为 Goal version 会造成治理噪声；将 Goal change 隐藏在 Plan 又会失去 lineage。

## 5.4 Diagnostic outputs

理论输出应包含：

```text
active_goal_version
observed_delta
candidate_transition_type
source_class
first_invalid_transition
quality_vector
authority_status
evidence_status
impact_summary
diagnosis=VALID_TRANSITION|UNRESOLVED|GOAL_DRIFT
uncertainty
recommended_next_review
```

本轮不创建该输出 Schema。

## 5.5 Failure modes

- **Self-amendment laundering：** Agent 把自己的 Plan 解释成 Goal authority；
- **Authority laundering：** tool/comment/environment output 被当作 human instruction；
- **Evidence laundering：** Evidence 只支持局部问题，却被用于扩张 Goal；
- **Proxy capture：** benchmark/coverage/latency 取代真实 Outcome；
- **Version fork：** 两个新 Goal 都声称 supersede 同一 parent；
- **Stale baseline：** detector 保护已过期 Goal；
- **Silent discontinuity：** substitution 被标为 refinement；
- **Governance overload：** 微小 benign change 产生大量无价值 transition。

# 6. Goal Recovery

## 6.1 Recovery objective

Goal recovery 不是盲目回到最旧 Goal。它要恢复最近可信 Goal lineage、吸收 drift 后仍有效的新 Evidence，
排除 invalid transition，并形成可审查的 next Goal/Plan candidate。

## 6.2 Recovery sequence

```text
1. Select last-known-valid Goal version
2. Reject or quarantine invalid transition
3. Preserve valid work and new Evidence
4. Restore Goal baseline fields and authority boundary
5. Decide: restore old Goal or propose authorized new Goal version
6. Replan under recovered Goal
7. Re-evaluate Goal + Evidence integrity
8. Separately decide continue / hold / stop
```

## 6.3 Recovery modes

| Mode | Use when | Goal result | Execution result |
|---|---|---|---|
| Baseline restoration | invalid transition added no indispensable new fact | restore `G_v` | recommendation only |
| Forward recovery | new Evidence/environment invalidates assumptions, but transition was malformed | propose corrected `G_(v+1)` with valid lineage | await acceptance and separate execution authority |
| Goal fork | both objectives remain legitimate but cannot share one Scope | create explicit child/new lineage candidate | no automatic branching execution |
| Hold unresolved | authority/Evidence conflict persists | retain LKV, mark unresolved proposal | hold/ask recommendation |
| Stop bounded flow | recovery risk exceeds Scope | no new active Goal | stop recommendation |

## 6.4 Reject invalid transition without erasing history

```text
G_v active
  ├── T_bad → G_bad        rejected/quarantined lineage
  └── T_recovery → G_v'    accepted recovery candidate, new lineage
```

不得覆盖 `T_bad` 或假装 drift 没发生。

## 6.5 Restore Goal Baseline

恢复对象包括：

- Objective；
- Scope；
- Constraints；
- Success Criteria；
- Stop Conditions；
- Authority；
- parent/version/lineage；
- still-valid work and Evidence references。

## 6.6 Create New Goal Version

只有当恢复过程确认 old Goal 已因合法新事实需要更新，并完成 transition validity 条件时，才生成新 active
Goal version。`Recovery Recommendation` 本身不能接受新 Goal。

## 6.7 Recovery hazards

- LKV 已过期；
- 新 Evidence 被错误丢弃；
- valid work preservation 引入 drift 残留；
- recovery proposal 伪装成新的 unauthorized expansion；
- 人类因“系统已恢复”产生错误自信；
- recovery 成本高于 clean restart。

这些必须由未来实验验证。

# 7. Goal Pull Request Concept

## 7.1 Research analogy

`Goal Pull Request` 是 platform-neutral 的研究类比，更准确的中性名称是：

```text
Goal Transition Proposal (GTP)
```

它像 code PR 一样把差异、理由、Evidence、影响和 review 放在一个可审查表面，但它不是 Git feature，
也不是产品承诺。

## 7.2 Candidate contents

```text
proposal_id
proposer_identity
old_goal_ref
new_goal_candidate
field_level_diff
transition_type
reason
evidence_refs
impact_analysis
authority_claim
review_findings
transition_acceptance_state
lineage_parent
```

只作为理论概念，禁止创建 Schema。

## 7.3 Candidate lifecycle

```text
Draft Proposal
    ↓
Evidence and Impact Bound
    ↓
Authority Resolved
    ↓
Review
    ↓
Accept into Goal lineage / Request clarification / Reject / Supersede
```

## 7.4 What review means

Goal Transition Review 回答：

- change 是什么；
- 为什么需要；
- Evidence 是否支持；
- authority 是否覆盖；
- impact 是否已知；
- continuity 是否清楚；
- 应恢复、接受还是保持 unresolved。

它不回答：“允许 Agent 现在部署吗？”

## 7.5 Thresholding

不是每个 micro replan 都创建 Goal PR。候选触发阈值：

- Objective 变化；
- Scope/Constraints/Success Criteria/Stop Conditions 任一关键字段变化；
- authority/delegation 变化；
- consequential Action 前发生 Goal-field delta；
- substitution 或 M2+ expansion；
- drift recovery 需要新 Goal version。

## 7.6 Goal PR risks

- 过度文档化和 latency；
- Agent 生成形式完备但内容空洞的 proposal；
- review 成为自动 rubber stamp；
- approval wording 被误解为执行许可；
- 平台绑定压过跨 Agent 目标。

若它不改善 change/drift 区分或 recovery，只是更长报告，应停止开发。

# 8. Codex Observation Mapping

## 8.1 Why Codex is useful

Codex 长任务提供可观察的：用户目标、Plan、阶段状态、commentary、tool/file Action、diff、测试结果、
stop point 和 final message，适合研究 Goal transition 在 coding trajectory 中如何出现。

## 8.2 Candidate mapping

| Codex-visible surface | Goal-transition observation | Trust boundary |
|---|---|---|
| user request/follow-up | Objective、Scope、authority claim、change reason | 需要识别当前 user/authority 与冲突 |
| Goal/task metadata | active Goal candidate、status | 不是天然可信或 canonical authority |
| plan updates | refinement/replan signals | Plan change 不自动等于 Goal change |
| commentary | stated reason/impact awareness | self-report 不等于实际 behavior |
| file/tool actions | observed Goal-relevant behavior | observation 可能不完整 |
| diff/tests | impact and Outcome Evidence | test pass 不证明 Goal continuity |
| final message | stated active Goal/Outcome | 最终叙述不能覆盖 trajectory |

## 8.3 Required metadata

Codex Goal 信息只有绑定以下材料后才可用于 transition research：

```text
version
parent
lineage
change_reason
proposer_identity
authority_reference
effective_transition
```

## 8.4 Observation boundary

```text
CODEX_AS_FIRST_OBSERVATION_ENVIRONMENT=true
CODEX_AS_PRODUCT_BINDING=false
CODEX_GOAL_STATE_INHERENTLY_TRUSTED=false
LATENT_GOAL_OBSERVED=false
```

SAEE 只能研究可观察 operational Goal state，不能读取模型内部思想或真实 intent。

## 8.5 Cross-platform requirement

任何未来通用结论必须在至少一个非 Codex Agent runtime 复现，并使用相同 transition semantics。
否则只能报告 `CODEX_OBSERVATION_RESULT`，不能声称 Agent-universal。

# 9. Research Hypotheses

| ID | Hypothesis | Minimum comparison | Support condition | Falsifier / stop condition |
|---|---|---|---|---|
| H1 | Goal Transition record 降低 Goal Drift | unrecorded change vs versioned transition record | persistent/consequential drift 和 unexplained expansion 下降，Outcome 不恶化 | 无差异、只增加文本或 latency |
| H2 | Versioned Goal 提高 change/drift 区分能力 | static/unversioned vs version+lineage | precision/recall 提高，benign/authorized change FP 下降 | versioning 无增量或 stale version 使结果更差 |
| H3 | Goal Transition Review 优于 final-result review | blinded final result vs trace+transition vs diagnosis | onset localization、decision accuracy、actionability 提高 | final review 相同/更好，transition review 只增加主观信心 |
| H4 | Goal Recovery 优于 restart | matched drift snapshot: restart vs LKV transition recovery | recovery success、valid-work preservation 或 cost 更优，re-drift 不增加 | restart 相同/更好，LKV stale 或 recovery 引入新 drift |
| H5 | 多维 transition quality 优于二元 approval | vector review vs accepted/rejected flag | fault localization 和 calibrated reliance 更好 | vector 无增量或复杂度抵消收益 |
| H6 | Goal PR 对 M2+ change 有价值但对 micro replan 无价值 | thresholded vs always-on vs no proposal | M2+ drift 降低且微变化 overhead 受控 | always/no-proposal 相同，或 threshold 漏掉关键 transition |

## 9.1 Hypothesis order

优先 H2/H3，确认 transition 可观察且能区分合法变化；再测试 H1。只有 H1–H3 有增量价值，才研究 H4。
Goal PR/Interface 实现必须晚于 H5/H6。

## 9.2 Metrics

- transition classification precision/recall；
- benign/authorized change false-positive rate；
- first invalid transition localization error；
- Goal-field continuity preservation；
- authority/lineage completeness；
- review decision accuracy and latency；
- appropriate reliance / calibration error；
- valid-work preservation；
- recovery success、cost、re-drift；
- proposal preparation cost and governance overhead。

禁止把这些提前压缩为 Trust Score。

## 9.3 Research stop conditions

暂停该方向，如果：

- ordinary task history 已能复制 transition record 的全部价值；
- authority ground truth 无法以可接受成本构造；
- versioning 增加误判或 stale-goal protection；
- review 不改善 decision quality；
- recovery 不优于 restart；
- Goal PR 主要产生形式文档；
- research track 持续挤占现行 integration mainline；
- governance wording被用户/Agent稳定误解为执行审批。

# 10. First-Principles Answers

## 10.1 Why Agents need Goal Evolution

智能意味着根据新事实修正路线和目标假设。长期 Agent 若只能坚持初始文本，会在过期条件下继续优化；
若可隐式改写，则又无法解释和恢复。Goal Evolution 提供两者之间的显式变化路径。

## 10.2 Why prohibiting Goal change reduces intelligence

禁止变化会把适应性变成违规：澄清无法吸收，Evidence 无法修正错误假设，环境变化无法反馈，Agent 只能
停止或暗中改变。它保护的是旧文本，不一定保护真实 intent。

## 10.3 Why manage change instead of preventing change

目标是允许变化，同时保留：

- 谁提出；
- 为什么；
- 依据什么；
- 改变什么；
- 谁可接纳；
- 影响多大；
- 如何回到最近可信状态。

管理变化让系统既不僵化，也不失去连续性。

## 10.4 Why Goal Integrity remains necessary

Goal Evolution 回答“变化如何发生”；Goal Integrity 回答“变化后是否仍属于有效 Goal lineage”。二者关系：

```text
Goal Object
    ↓
Goal Evolution / Transition
    ↓
Goal Integrity Assessment
    ↓
State Integrity
    ↓
Recovery
```

没有 Transition，Integrity 容易把合法变化误报；没有 Integrity，Transition record 可能只是形式包装。

# 11. Relationship to Phase 8.0-D3.1 Benchmark

上一阶段 benchmark 仍有效，本模型不覆盖或修改它。Human review 后，可考虑未来 benchmark amendment：

- 将 `Goal Anchor only` 拆为 static vs versioned transition-aware anchor；
- 为 Clarification、Refinement、Expansion、Substitution 增加 balanced ground truth；
- 比较 binary approval 与 transition quality vector；
- 加入 Goal PR overhead 和 threshold experiment；
- 保持 automatic recovery 禁止。

当前：

```text
BENCHMARK_AMENDED=false
EXPERIMENT_EXECUTED=false
EXPERIMENT_RERUN_AUTHORIZED=false
```

# 12. SAEE Candidate Role

若未来研究成立，SAEE 候选角色仍限于：

```text
Goal Transition Assessment
Goal Drift Diagnosis
Goal Recovery Recommendation
```

SAEE 不创建、修改、接受或执行 Goal transition：

```text
SAEE_GOAL_OWNER=false
SAEE_TRANSITION_ACCEPTOR=false
SAEE_GOAL_MODIFIER=false
SAEE_ACTUATOR=false
SAEE_AUTO_APPROVAL_CORE=false
```

当前 `saee.evaluate_agent_run` 仍不是 Goal transition evaluator：

```text
CURRENT_EVALUATION_AS_CHECKPOINT=true
CURRENT_EVALUATION_AS_GOAL_TRANSITION_EVALUATOR=false
CURRENT_EVALUATION_AS_GOAL_DETECTOR=false
```

# 13. Claims and Non-Claims

## Claims

- 已定义 Goal Transition theoretical object 和 lifecycle；
- 已区分 Clarification、Refinement、Expansion、Substitution 与 Drift；
- 已定义五维 transition quality；
- 已定义 source-aware diagnosis、recovery modes 和 Goal PR 研究概念；
- 已提出可证伪 hypotheses 和 stop conditions；
- Codex 仅作为第一观察环境。

## Non-Claims

本模型不代表：

- 已创建 Goal Capability、Schema、Protocol、Plugin 或 Interface；
- SAEE 已能观察、验证或接受真实 Goal transition；
- Codex Goal metadata 天然可信；
- Goal PR 已实现或适用于所有变化；
- Goal transition acceptance 等于 Action/部署/外部执行授权；
- SAEE 能读取模型内部 Goal 或 intent；
- Goal Governance 等于 Agent control、IAM、Policy Engine 或人工审批替代；
- Goal Recovery 已实现或优于 restart；
- Goal Evolution 已成为新的宪法主线；
- research model 已获得 customer/commercial/production validation。

```text
SAEE_RECOMMENDATION_NOT_AUTHORIZATION=true
SAEE_EXECUTION_CONTROL=false
SAEE_AUTO_APPROVAL_CORE=false
SAEE_EXTERNAL_WORLD_EXECUTION=false
COMMERCIAL_VALIDATION=false
PRODUCTION_READY=false
```

# 14. Human Review Questions

1. 是否接受 `Drift` 是无效/未证明变化的诊断，而不是合法 transition type？
2. 是否接受 `approval_state` 仅表示 lineage acceptance，不表示执行授权？
3. 是否接受 substitution 通常需要 superseding version 或新 lineage？
4. 是否接受 Agent 可以提出 transition，但不能自动自授 Goal-change authority？
5. 是否接受 Goal PR 只对 M2+ change 候选触发，避免治理过载？
6. 是否接受该研究继续从属于现行 integration mainline？

# 15. Final Status

```text
GOAL_TRANSITION_GOVERNANCE_MODEL_STATUS=COMPLETE
GOAL_OBJECT_MODEL_DEFINED=true
GOAL_TRANSITION_MODEL_DEFINED=true
GOAL_TRANSITION_QUALITY_MODEL_DEFINED=true
GOAL_DRIFT_MODEL_DEFINED=true
GOAL_RECOVERY_MODEL_DEFINED=true
GOAL_PULL_REQUEST_CONCEPT_DEFINED=true
GOAL_GOVERNANCE_MEANS_EXECUTION_APPROVAL=false
CODEX_AS_FIRST_OBSERVATION_ENVIRONMENT=true
CODEX_PRODUCT_BINDING=false
CURRENT_EVALUATION_AS_GOAL_TRANSITION_EVALUATOR=false
GOAL_PLUGIN_IMPLEMENTED=false
GOAL_INTERFACE_IMPLEMENTED=false
GOAL_SCHEMA_CREATED=false
GOAL_PROTOCOL_CREATED=false
RECOVERY_IMPLEMENTED=false
EXPERIMENT_EXECUTED=false
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CONTAINED_BY_RESEARCH_ONLY_BOUNDARY
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_GOAL_TRANSITION_MODEL
```
