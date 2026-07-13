# SAEE Pilot Readiness Gap Resolution Plan v0.1

当前 readiness：`NO_GO`；当前 gap resolution：`0/12`。

```text
Gap Resolution Plan ≠ Gap Resolution
Action Plan ≠ Completed Action
Future Requirement ≠ Approved Evidence
```

本计划强化 SAEE 数字生物圈进化引擎的 `Global Sensing`、`Sandbox Development`、`Pareto Fitness Evaluation` 和档案/回滚免疫系统。它只定义未来重新审查路径，不授权执行。

## 1 Purpose

本文描述未来再次进行 Pilot Execution Readiness Review 前必须完成的动作、产物和验收条件。它不创建这些产物，不接受任何审批，不改变当前 matrix，也不授权采集、标注或执行。

## 2 Current Readiness State

当前固定状态：

```text
current_readiness=NO_GO
pilot_authorized=false
execution_started=false
future_reassessment_allowed=false
```

主要原因：

- dataset source unavailable；
- ownership and permissions incomplete；
- privacy review incomplete；
- retention、deletion 与 access control 未批准或测试；
- dataset schema 和 annotation codebook 未冻结；
- 没有批准的 validation sample；
- 没有 pilot-specific environment freeze；
- safety gate 仍为 STOP，execution approval unavailable。

PR-13 的 Technical/Safety `READY` 仅说明本地合成控制面和安全规则已定义。本计划要求的 pilot-specific environment、控制测试和执行批准尚不存在，因此没有篡改或降级 PR-13 matrix。

## 3 Gap Matrix

| Gap | Current State | Required Future Evidence | Blocking Level | Status |
|---|---|---|---|---|
| Dataset Source | 未选择或批准 | approved source record | CRITICAL | OPEN |
| Data Ownership | 责任角色未明确 | approved ownership record | CRITICAL | OPEN |
| Permissions | 采集与研究使用未批准 | approved permission record | CRITICAL | OPEN |
| Privacy Review | 隐私和敏感数据审查未完成 | approved privacy review | CRITICAL | OPEN |
| Retention Policy | 无批准保留计划 | approved retention schedule | CRITICAL | OPEN |
| Deletion Process | 删除/撤回未测试 | tested deletion record | CRITICAL | OPEN |
| Access Control | pilot 访问角色未批准 | approved access-control record | CRITICAL | OPEN |
| Schema Freeze | schema 是草案 | schema hashes and freeze record | HIGH | OPEN |
| Approved Sample | 无非主评估 sample | approved sample manifest | HIGH | OPEN |
| Annotation Approval | codebook 未批准 | approved annotation protocol | HIGH | OPEN |
| Environment | 本地检查通过但 pilot 环境未冻结 | pilot environment freeze record | HIGH | OPEN |
| Safety Controls / Execution Approval | 规则存在但 safety gate 为 STOP | safety tests and explicit approval | CRITICAL | OPEN |

机器可读细节见 `agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json`。

## 4 Remediation Actions

每个 gap 必须依序保留四类信息：

1. **Action**：由负责流程执行的未来动作；
2. **Required artifact**：必须形成并可引用的文件化产物；
3. **Completion criteria**：负责流程接受该产物的明确条件；
4. **Evidence refs**：实际产物引用。

没有 required artifact 与 evidence ref，不能把状态升级为 `EVIDENCE_READY` 或 `CLOSED`。

关键动作顺序：

1. 先解决 source、ownership、permissions；
2. 再完成 privacy、retention、deletion、access control；
3. 之后才能冻结 schema、准备批准 sample、冻结 annotation protocol；
4. 使用已批准 sample 冻结并测试 pilot-specific environment；
5. 最后验证 sandbox、network denial、stop authority 和 rollback；
6. 只有 critical gap 均有证据后，才能请求单独的 execution approval。

例如 `Privacy Review` 只有在 `approved_privacy_review_record` 存在，并被负责审查流程接受后，才可声明证据已准备；本计划本身不是该 record。

## 5 Re-Review Criteria

只有以下条件全部成立，`future_reassessment_allowed` 才能变为 `true`：

- 所有 gap 状态为 `EVIDENCE_READY` 或 `CLOSED`；
- 每个 gap 至少有一个实际 evidence reference；
- required artifacts 已由负责流程接受，而不是由 validator 推断；
- readiness matrix 在单独变更中更新；
- safety stop conditions 始终保持有效；
- 新审查重新计算 decision，不继承本计划的任何批准。

允许重新审查不等于 `GO`。只有新的 PR-13 readiness review 计算得到 `GO`，并另有明确执行授权，才可讨论 controlled pilot。

## 6 Explicit Non-Goals

本计划不：

- approve pilot；
- create dataset or sample；
- collect or process data；
- authorize execution；
- create privacy、permission 或 safety approval；
- prove compliance；
- claim validation or experimental success；
- change current `NO_GO`。

验证计划一致性：

```bash
python3 scripts/saee_agent_cli.py review-pilot-gaps \
  --input agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json
```

