# SAEE Phase 1 本地合成垂直切片

状态：`implemented_local_synthetic_only`。

## 1. 目的

Phase 1 把 SAEE v3 已接受的 L3 `Deployment Assurance Projection` 压缩成一条可离线重复的最小链：

```text
Synthetic Task Contract
        ↓
Synthetic Environment Scenarios
        ↓
Declared Observations
        ↓
Evaluation Result
Score + Reason + Failure Class + Evidence Reference
        ↓
Existing Evidence Adequacy Evaluator
        ↓
Scenario Risk Estimate
        ↓
Scenario-scoped Decision Support
```

该链不运行真实 Agent，不接触客户数据，不调用工具，不访问网络，也不签发部署权限。

## 2. SAEE Evidence Case Object

Case Object 是 Phase 1 的机器可读主对象，包含九类关系：

```text
identity
task_contract
environment
agent_reference
observation
evaluation
evidence
risk
decision
```

具体文件：

- schema：`agent-interface/architecture/saee-evidence-case.v0.1.schema.json`；
- 合成输入：`agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json`；
- 实现：`saee_backend/services/saee_evidence_case.py`；
- CLI：`scripts/saee_agent_cli.py run-assurance-case`。

输入 schema 严格拒绝未声明字段。语义检查还要求 candidate 与 evidence 一一对应、scenario 权重之和为 1、每个 candidate/scenario 恰好有一条 observation、evidence reference 完整绑定、低风险阈值严格小于复测阈值。

## 3. Evaluation Output Contract

每条合成 observation 产生：

- `score`：`1 - declared synthetic failure estimate`；
- `reason`：为什么产生该分数；
- `failure_class`：可检索的失败类型；
- `evidence_ref`：对应 Evidence Contract 引用。

Observation 明确保持 `observation_is_evidence=false`。Score 不能脱离 reason、failure class 和 evidence reference 单独用于 Decision Support。

## 4. Evidence Adequacy Gate

Phase 1 不复制 Evidence Adequacy 逻辑，而是直接调用现有：

```python
evaluate_evidence_adequacy(claim_type, package)
```

Evidence Adequacy PASS 仅表示合成 evidence package 满足选定 profile 的字段和关系要求，不证明事件真实发生、身份已独立验证或授权真实有效。任一 candidate 的 Adequacy FAIL 时，其 Decision Support 强制为 `RETEST`。

## 5. Risk Estimate

场景风险估计：

```text
R_s = P_s × I_s × X_s × (1 - C_s) + U_s
R_total = Σ_s w_s × R_s
```

- `P_s`：输入文件声明的合成 failure estimate；
- `I_s`：业务影响；
- `X_s`：暴露；
- `C_s`：控制有效性；
- `U_s`：不确定性惩罚；
- `w_s`：场景权重。

输出始终包含 `risk_estimate_not_measurement=true` 和 `risk_probability_measured=false`。这些数值未经客户、真实分布或外部研究校准。

## 6. Decision Support

本切片只输出：

- `DEPLOY_LIMITED`：在本地合成阈值下估计较低；
- `RETEST`：估计位于中间区间，或 Evidence Adequacy FAIL；
- `HOLD`：估计高于复测阈值。

它不输出自动决策。`customer_execution_authorized=false`、`automatic_decision=false`、`deployment_authorized=false` 始终保持。

## 7. 合成对比结果

内置样例包含两个候选与两个场景：普通多轮对话、长上下文漂移。

| Candidate | Aggregate risk estimate | Decision Support |
|---|---:|---|
| `candidate:synthetic-a` | `0.1734` | `RETEST` |
| `candidate:synthetic-b` | `0.131` | `DEPLOY_LIMITED` |

因此 `candidate:synthetic-b` 是该合成 Case 中的最低估计风险候选。这不是对任何真实 Agent 的推荐，也不能推广到其他任务、阈值或业务环境。

## 8. 调用

```bash
python3 scripts/saee_agent_cli.py run-assurance-case \
  --input agent-interface/architecture/examples/saee-evidence-case-synthetic-001.json
```

聚焦验证：

```bash
make check-saee-phase1-synthetic-vertical-slice
```

## 9. 明确限制

- 没有真实 Agent execution；
- 没有 Runtime、Memory 或 Tool Trace Adapter；
- 没有真实工具、网络、子进程或外部仓库；
- 没有生产 trace 或客户数据；
- 没有测得的 failure probability；
- 没有外部 validation 或 customer validation；
- 没有 production readiness、持续保障或自动反馈变异；
- 不构成法律结论、安全认证或部署授权。

## 10. 下一阶段边界

下一步应先对 Phase 1 Case Object 做第二轮架构与结果审查。未经新的推荐门和明确授权，不实现真实 receive-only adapter，不启动外部 pilot，也不修改商业网站。

