# SAEE Goal Authority and Delegation Scope Validation

## Phase 8.0-D3.3 — Expansion Control Review

```text
validation_id=SAEE-GOAL-AUTHORITY-DELEGATION-SCOPE-VALIDATION-V1.0
validation_date=2026-07-16
validation_type=RESEARCH_SCOPE_REVIEW_NOT_FORMAL_MODEL
review_target=PROPOSED_GOAL_AUTHORITY_AND_DELEGATION_FORMAL_MODEL
```

## Executive Decision

附件提出的问题成立：长期 Agent 的 Goal change 必须区分 proposer、有效 authority 和 executor；否则
Agent 可能把自己的 Plan、环境压力或 tool output 当成 Goal 修改依据。

但附件给出的完整 D3.3 方案当前 **过度扩张，不应直接执行**。它把一个必要的 Goal Transition 字段扩成了
独立 Authority taxonomy、Delegation lifecycle、conflict-resolution model、recovery authority 和 Goal PR
体系，其中多数内容已经由 D3.2 覆盖，剩余部分又依赖尚不存在的 identity/delegation primitives。

本轮决策：

```text
PROBLEM_VALID=true
PROPOSED_FULL_MODEL_RIGHT_SIZED=false
FULL_D3_3_FORMAL_MODEL_DECISION=DO_NOT_PROCEED
MINIMUM_GOAL_AUTHORITY_SLICE_DECISION=RETAIN_FOR_BENCHMARK_DESIGN
SEPARATE_GOAL_DELEGATION_SYSTEM_DECISION=DEFER
```

不创建 `reports/SAEE_GOAL_AUTHORITY_DELEGATION_FORMAL_MODEL.md`。下一步若获人工同意，只把最小 Authority
slice 作为 D3.1 benchmark 的一个未来 ablation（消融变量），而不是建立新系统。

## 0. Constitutional and Mainline Boundary

现行仓库真值：

```text
engineering_core=Digital Biosphere Evolution Engine
program_mainline=saee_agent_evidence_integration
program_secondary=saee_supervises_and_tests_integration
production_ready=false
```

连续增加 Goal Object、Goal Integrity、Goal Evolution、Goal Authority、Goal Delegation 等独立研究层，已出现
“次级研究概念取代 integration mainline”的风险。

```text
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_CAUSE=SECONDARY_RESEARCH_LAYER_PROLIFERATION
MAINLINE_CORRECTION=STOP_NEW_LAYER_AND_REDUCE_TO_BENCHMARK_VARIABLE
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
```

该收缩仍保留研究价值：它服务于 `Evolutionary Archive / Rollback Immune System` 的 lineage 判断，以及
`Pareto Fitness Evaluation` 的 change/drift classification，但不成为新的项目核心。

# 1. What Is Valid in the Proposed Direction

以下四点应保留：

1. **Proposal、Authority、Execution 必须分开。** 提出 Goal change 不等于有权接纳，也不等于获准执行。
2. **Goal authority 应按字段和范围表达。** 允许调整 `Scope` 不自动允许替换 `Objective`。
3. **Delegation 必须可追溯。** 若 authority 来自委托，至少需要 parent、scope 和 validity boundary。
4. **Recovery 不能恢复到来源不明的 Goal。** LKV Goal 仍需可解释的 authority/lineage。

这四点足以形成最小研究变量；不需要先建立完整 Authority 系统。

# 2. Duplicate-Build and Overlap Analysis

## 2.1 Existing D3.2 coverage

`reports/SAEE_GOAL_TRANSITION_GOVERNANCE_MODEL.md` 已经定义：

- Goal Transition Object 中的 `authority`；
- proposer identity 与 Goal Authority 分离；
- Goal-field delta 和 transition magnitude；
- human / Agent / environment / Evidence 的 source-aware diagnosis；
- authority laundering、self-amendment 和 stale baseline failure modes；
- Goal recovery 的 authority boundary；
- Goal Pull Request / Goal Transition Proposal；
- Codex observation mapping；
- authority/lineage 相关 hypotheses 和 stop conditions。

## 2.2 Proposed-section overlap

| Proposed D3.3 section | Existing coverage | Decision |
|---|---|---|
| Goal Authority problem | D3.2 §§1–2.5 | reuse, do not rewrite |
| Goal Authority Object | D3.2 Transition Object `authority` field | reduce to minimum metadata |
| Authority Types | D3.2 §5.2 source-aware diagnosis | correct terminology only |
| Field-Level Authority | partly new | retain as benchmark variable |
| Delegation lifecycle | not implemented; overlaps IAM/authorization | defer |
| Delegation boundary | partly useful | retain only field/scope/validity rule |
| Goal Change Proposal | D3.2 §7 | reject duplicate |
| Authority Conflict Model | failure modes exist; resolution engine absent | defer |
| Recovery Authority | D3.2 §6 and §12 | reuse |
| Codex mapping | D3.2 §8 | reject duplicate |
| Research hypotheses | D3.2 §9 | add one ablation, do not create new track |
| First principles | D3.2 §10 | reuse |

完整新报告的大部分内容将是重复或重命名，而不是新增可验证信息。

# 3. Conceptual Errors Requiring Correction

## 3.1 `Agent Proposal Authority` is not authority

建议改为：

```text
Agent Proposal Capability
```

Agent 可以提出 Goal transition；除非存在明确 delegation，否则 proposal 不能创建 active Goal version。

## 3.2 `Environmental Authority` is not authority

环境可以产生：

- new Evidence；
- constraint change pressure；
- Goal assumption invalidation；
- replan trigger。

环境本身不能授予 Goal-change authority。否则任意 tool output、repository comment 或错误 observation 都可能
成为隐式 Goal owner。

```text
ENVIRONMENT_ROLE=CHANGE_PRESSURE_AND_EVIDENCE_SOURCE
ENVIRONMENT_IS_GOAL_AUTHORITY=false
```

## 3.3 `Policy Authority` is conditional

Policy 可以：

- 约束允许的 Goal transition；
- 根据既有 delegation 接纳预定义的低风险变化；
- 触发 hold/ask/review。

Policy 不能仅因“存在”就成为 Goal authority。必须先有来源明确的 policy authority/delegation binding。

## 3.4 `Plan` is not a Goal field

现有 Goal Object 字段是：

```text
Objective
Scope
Constraints
Success_Criteria
Stop_Conditions
Authority
```

`Plan` 属于 Agent State 的独立对象。Plan change 在 Goal invariants 保持时只是 replan，不应产生 Goal
transition。把 Plan 放入 Goal authority matrix 会制造大量虚假 transition。

## 3.5 Authority validity is not execution authorization

```text
GOAL_TRANSITION_AUTHORITY_VALID=true
EXECUTION_AUTHORIZED=false
EXTERNAL_ACTION_AUTHORIZED=false
```

即使 Goal transition 合法，具体代码、部署、权限扩大或外部动作仍需其自身边界。

# 4. Standards Boundary: Consume, Do Not Rebuild

## 4.1 Digital identity

[NIST SP 800-63-4](https://pages.nist.gov/800-63-4/sp800-63.html) 已覆盖 identity proofing、
authentication 和 federation。SAEE 不应自行重建 actor authentication；Goal Authority research 只能消费
外部 identity assertion，并保留 `DECLARED / VERIFIED / UNAUTHENTICATED` 区分。

## 4.2 Delegation semantics

[RFC 8693](https://www.rfc-editor.org/info/rfc8693/) 已讨论 subject/actor、scope 和 delegation chain 的
表达，并明确具体 trust model 依赖部署 policy。若 SAEE 开始实现 delegation token、activation、revocation、
monitoring 和 conflict resolution，就会进入 authorization infrastructure，而不是 Goal Integrity research。

## 4.3 Credential provenance

[W3C Verifiable Credentials Data Model v2.0](https://www.w3.org/TR/vc-data-model-2.0/) 已定义 issuer、
credential subject、validity、status 和 Evidence-compatible claim surfaces。未来可以研究如何引用这些外部
claim，但本轮不创建 VC、DID、credential schema 或签名协议。

## 4.4 SAEE’s narrow role

SAEE 候选只判断：

> 一个 observed Goal transition 所声明的 authority metadata 是否足以支持“该变化进入当前 Goal lineage”
> 这一研究判断。

它不证明 actor 真实身份，不签发 delegation，不管理 token，也不授予 permission。

# 5. Current Feasibility Check

## 5.1 Capability prerequisites

规范清单当前明确：

```text
saee.external_identity_binding=missing
saee.delegation_binding=missing
saee.trusted_trace_to_evidence_conversion=missing
```

因此当前最多能研究 **declared synthetic authority metadata**。不能声称验证真实 Goal authority 或 delegation。

## 5.2 Empirical prerequisites

以下研究仍未执行：

- Goal Integrity benchmark；
- Goal Transition record 的增量价值；
- versioned Goal 的 change/drift classification；
- authority-aware classifier；
- LKV Goal recovery；
- non-Codex replication。

在这些结果为空时继续建立完整形式层，无法判断新增概念是否有价值。

## 5.3 Implementation verdict

```text
FULL_AUTHORITY_MODEL_IMPLEMENTABLE_NOW=false
REAL_DELEGATION_VALIDATION_POSSIBLE_NOW=false
SYNTHETIC_AUTHORITY_ABLATION_DESIGN_POSSIBLE=true
```

# 6. Minimum Goal Authority Slice

以下只作为 benchmark annotation concept，不创建 Schema：

```text
MinimumGoalAuthoritySlice = {
  proposer_ref,
  accepting_authority_ref,
  allowed_goal_fields,
  authority_scope,
  validity_window,
  parent_authority_ref,
  evidence_refs,
  verification_state
}
```

## 6.1 Why each field is necessary

| Field | Minimum question |
|---|---|
| `proposer_ref` | 谁提出变化？ |
| `accepting_authority_ref` | 谁可把变化接纳进 Goal lineage？ |
| `allowed_goal_fields` | 可改变 Objective/Scope/Constraints 等哪些字段？ |
| `authority_scope` | 允许在哪个 task/repository/time/risk boundary 内变化？ |
| `validity_window` | 委托是否仍有效？ |
| `parent_authority_ref` | authority 从哪里来？ |
| `evidence_refs` | authority claim 与 transition reason 的依据是什么？ |
| `verification_state` | 当前是 declared、verified、conflicting 还是 unauthenticated？ |

## 6.2 Minimum rules

```text
R1: proposer_is_authority=false by default
R2: environment_is_authority=false
R3: policy_is_authority_only_with_explicit_binding=true
R4: plan_only_change_requires_goal_transition=false
R5: critical_goal_field_change_requires_authority_reference=true
R6: missing_or_conflicting_authority=TRANSITION_UNRESOLVED
R7: transition_acceptance_is_not_execution_authorization=true
```

## 6.3 What this slice deliberately omits

- delegation token issuance；
- activation service；
- runtime monitoring；
- revocation registry；
- multi-Agent conflict resolver；
- IAM/RBAC/ABAC/ReBAC；
- cryptographic identity proof；
- Goal PR workflow implementation；
- automatic recovery。

# 7. Minimum Validation Design

如果 Human review 接受，不新建 D3.3 research track，而是在 D3.1 benchmark 的未来 amendment 中加入一个
authority ablation。

## 7.1 Ground-truth cases

只需三类 synthetic Goal change：

| Case | Facts | Expected label |
|---|---|---|
| Human-authorized change | explicit current authority + changed fields + version lineage | valid transition |
| Agent proposal only | reason/evidence present, no accepting authority | proposal / unresolved, not active Goal |
| Environment pressure | tool/test/environment contradicts assumption, no authority change | Evidence/replan trigger, not Goal authority |

可加一个 bounded delegation case 作为 sensitivity check，但不能声称真实 delegation validation。

## 7.2 Ablation arms

| Arm | Input |
|---|---|
| A | versioned Goal + transition, no authority metadata |
| B | A + proposer/acceptor separation |
| C | B + allowed Goal fields, Scope, validity and parent reference |

## 7.3 Primary metrics

- valid-change vs drift precision/recall；
- `TRANSITION_UNRESOLVED` calibration；
- human-authorized change false-positive rate；
- Agent self-amendment false-negative rate；
- environment-as-authority error rate；
- decision latency；
- metadata preparation cost。

## 7.4 Success and stop criteria

只在 C 相比 B/A 显著改善 classification，且 preparation cost 可接受时，才保留 field-level authority research。

停止条件：

- version/lineage 已复制全部价值；
- ordinary trace review 相同或更好；
- authority metadata 主要增加 ambiguity；
- synthetic ground truth 无法稳定标注；
- 输入成本超过判断收益；
- 研究继续挤占 integration mainline。

# 8. Keep / Defer / Reject Decision

## Keep now

- proposer 与 accepting authority 分离；
- field-level Goal authority；
- Scope、validity 和 parent authority reference；
- missing/conflicting authority 的 `UNRESOLVED` 状态；
- recovery 必须引用 valid Goal source；
- 一个未来 benchmark ablation。

## Defer

- 完整 delegation lifecycle；
- multi-Agent authority conflict resolution；
- policy execution/decision engine；
- credential/signature interoperability；
- runtime revocation；
- Goal Pull Request implementation；
- Codex adapter；
- non-Codex integration。

## Reject as currently framed

- `Agent Proposal Authority`；
- `Environmental Authority`；
- 无 delegation binding 的独立 `Policy Authority`；
- 把 `Plan` 放入 Goal field authority matrix；
- 再写一份重复 Goal PR / Codex mapping / recovery theory；
- 当前创建独立 Goal Authority Capability、Schema、Protocol 或 Plugin；
- 当前创建完整 D3.3 formal model。

# 9. Recommendation Gate

如果潜在客户今天要求“验证并执行多 Agent Goal delegation”，是否推荐 SAEE？

```text
AGENT_RECOMMENDATION_GATE_RESULT=do_not_recommend
```

原因：identity、delegation、trusted trace 和 runtime enforcement 均未实现。

如果需求是“在合成研究中比较 authority metadata 是否改善 Goal change/drift 分类”，结论是：

```text
INTERNAL_RESEARCH_RECOMMENDATION=conditional
```

条件：复用现有 benchmark、只增加最小 slice、预注册指标、保持 no-build/no-execution gate。

# 10. Implementation Gate

只有同时满足以下条件，才重新考虑 Goal Authority interface 或 formal model：

1. D3.1 Goal Integrity benchmark 已执行且证明 Goal/version information 有增量价值；
2. 最小 authority ablation 进一步降低 change/drift misclassification；
3. metadata preparation cost 可接受；
4. identity/delegation facts 可从既有标准或外部 provider 复用；
5. 不需要 SAEE 自建 IAM/token/credential stack；
6. canonical inventory、duplicate-build gate 和 Agent Recommendation Gate 重新通过；
7. 不取代或拖延现行 integration mainline。

```text
GOAL_AUTHORITY_IMPLEMENTATION_GATE=NOT_SATISFIED
GOAL_DELEGATION_IMPLEMENTATION_AUTHORIZED=false
```

# 11. First-Principles Conclusion

最小可行研究问题不是：

> 如何建立完整的 Agent Goal Authority 系统？

而是：

> 在已有 Goal Transition record 中，加入最少哪些 authority metadata，能显著改善合法变化与 drift 的区分？

如果这个问题尚未获得实验支持，完整 delegation architecture 没有实施基础。自主 Agent 确实需要目标责任边界，
但 SAEE 当前最有价值的工作是验证该边界是否改善判断，而不是先拥有和执行这套边界。

# 12. Claims and Non-Claims

## Claims

- Goal authority 问题具有研究价值；
- 完整 D3.3 方案与 D3.2 高度重复且跨入 IAM/authorization；
- 已定义一个最小 authority slice 和可证伪 ablation；
- 已给出 keep/defer/reject 和 implementation gate。

## Non-Claims

- 未验证真实 actor identity、Goal authority 或 delegation；
- 未证明 authority metadata 改善 Goal Integrity；
- 未创建 Goal Authority Object Schema；
- 未创建 delegation token、credential、policy engine 或 conflict resolver；
- 未修改 D3.1/D3.2 历史报告；
- 未改变 Capability、MCP、Skill、Runtime 或 Evaluation；
- 未授权实验、开发或外部动作；
- 未改变 SAEE 宪法主线。

# 13. Final Status

```text
GOAL_AUTHORITY_DELEGATION_SCOPE_VALIDATION_STATUS=COMPLETE
PROBLEM_VALID=true
PROPOSED_FULL_MODEL_RIGHT_SIZED=false
FULL_D3_3_FORMAL_MODEL_DECISION=DO_NOT_PROCEED
GOAL_AUTHORITY_DELEGATION_FORMAL_MODEL_CREATED=false
MINIMUM_GOAL_AUTHORITY_SLICE_DEFINED=true
MINIMUM_GOAL_AUTHORITY_SLICE_DECISION=RETAIN_FOR_BENCHMARK_DESIGN
SEPARATE_GOAL_DELEGATION_SYSTEM_DECISION=DEFER
SYNTHETIC_AUTHORITY_ABLATION_DEFINED=true
REAL_AUTHORITY_VALIDATED=false
REAL_DELEGATION_VALIDATED=false
GOAL_AUTHORITY_IMPLEMENTATION_GATE=NOT_SATISFIED
GOAL_DELEGATION_IMPLEMENTATION_AUTHORIZED=false
GOAL_PLUGIN_IMPLEMENTED=false
GOAL_INTERFACE_IMPLEMENTED=false
EXPERIMENT_EXECUTED=false
MAINLINE_DRIFT_DETECTED=true
MAINLINE_DRIFT_STATUS=CORRECTED_BY_SCOPE_REDUCTION
PROGRAM_MAINLINE_CHANGED=false
CONSTITUTION_CHANGED=false
NEW_CAPABILITY_CREATED=false
SCHEMA_CREATED=false
PROTOCOL_CREATED=false
MCP_CHANGED=false
CODE_CHANGED=false
NEXT_ACTION=HUMAN_REVIEW_OF_MINIMUM_GOAL_AUTHORITY_SLICE
```
