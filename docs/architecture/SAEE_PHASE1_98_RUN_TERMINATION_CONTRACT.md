# SAEE Phase 1.98 Evaluation Run Termination Contract v0.1

## 1. 定位

Evaluation Run Termination Contract（评测运行终止契约）记录一次没有完成正常 Result→Evidence 路径的本地合成生命周期。它回答：

> 为什么这次预留或已启动的 Run 没有产生 Evidence Case？

它强化 Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统），但不实现真实 Runtime、不执行 Agent，也不改变 Digital Biosphere Evolution Engine 的核心定位。

## 2. Termination 与 Completed Run 的区别

```text
Evaluation Run Contract v0.1
    = 已完成的本地合成运行记录

Evaluation Run Termination Contract v0.1
    = 被人工停止、策略停止、输入拒绝或 Runtime 中断的记录
```

完成路径：

```text
Evaluation Input → Evaluation Run → Result → Evidence Case
```

终止路径：

```text
Evaluation Input → reserved/started Run ID → Termination Record
```

终止路径强制 `evidence_case_produced=false`，不会为了满足 Schema 而伪造 Evidence 引用。

## 3. Failed Outcome 与 Runtime Failure

两者不能混用：

- Evaluation Outcome Failure：Run 已完成，评测发现工具失败、漂移或其他问题；应使用 Evaluation Run Contract。
- Runtime Failure：Run 没有完成，没有形成完整 Result 或 Evidence Case；应使用 Termination Contract，状态为 `runtime_failed`。

因此 `failed-evaluation-run.json` 属于完成路径，而 `runtime-failure-termination.json` 属于终止路径。

## 4. Termination Status 与 Reason Code

状态：

- `manual_abort`：人工 Stop Authority 主动停止；
- `runtime_failed`：本地合成 Runtime 生命周期异常终止；
- `input_rejected`：在 Run 启动前被输入或边界策略拒绝；
- `policy_stopped`：运行开始后因边界策略停止。

可聚合原因码：

```text
MANUAL_ABORT
RUNTIME_ERROR
INPUT_POLICY_REJECTED
BOUNDARY_VIOLATION
RESOURCE_LIMIT
```

Schema 约束状态与原因码组合，避免自由文本成为唯一分类依据。

## 5. Partial Result 边界

Partial Result（部分结果）不是 Evidence：

```text
partial_result_present=true
partial_result_ref=<synthetic logical reference>
partial_result_digest=<declared sha256>
partial_result_is_evidence=false
evidence_case_produced=false
```

v0.1 的 Partial Result 引用与摘要是本地合成声明，没有对应外部 Artifact，也没有独立真实性验证。它不能进入 Risk Interpretation 或 Decision Support。

没有 Partial Result 时，`partial_result_ref` 与 `partial_result_digest` 必须显式为 `null`。

## 6. Stop Authority

每份 Termination Contract 都必须保存：

```text
operator_ref
stop_authority_ref
```

人工停止是治理动作，不等于 Runtime Failure。输入拒绝使用预留 `evaluation_run_id` 并强制 `run_started=false`，不会冒充一个已经启动的 Run。

## 7. No Fake Evidence

终止路径必须：

```text
run_completed=false
evidence_case_produced=false
evidence_case_ref=null
evidence_case_digest=null
```

Partial Result、错误文本、终止原因和 Termination Record 本身都不会自动成为 Evidence Case。

## 8. Execution、Risk 与 Decision 边界

所有样例强制：

```text
real_evaluator_runtime_executed=false
real_agent_executed=false
external_tool_executed=false
network_accessed=false
customer_data_processed=false
risk_probability_measured=false
automatic_decision=false
deployment_authorized=false
architecture_implemented=false
risk_model_implemented=false
production_ready=false
```

Termination 只记录为什么没有产生结论，不生成 Risk、Decision 或 Deployment Authority。

## 9. 验证

```bash
python3 scripts/saee_run_termination_contract_smoke.py
```

或运行包含此前契约回归的入口：

```bash
make check-saee-run-termination-contract
```

验证覆盖严格 Schema、状态与原因码、Input/Replay Evaluation 摘要、Termination Lineage、Stop Authority、Partial Result 边界、No Fake Evidence、确定性及冻结文件哈希。

## 10. 当前限制

- 仅三份本地合成终止记录；
- 不执行真实停止、Runtime、Agent、工具或网络；
- Partial Result 没有外部 Artifact 或真实性材料；
- Stop Authority、Consent、Permission、Retention 和 Deletion 仍是声明引用；
- 不构成外部验证、客户验证、生产就绪或合规声明。

Phase 2 Consent-First Offline Replay 继续保持 `HOLD`，直到 Phase 1.98 通过只读架构审查。
