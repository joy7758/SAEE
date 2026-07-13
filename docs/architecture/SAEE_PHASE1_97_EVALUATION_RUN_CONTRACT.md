# SAEE Phase 1.97 Evaluation Run Contract v0.1

## 1. 定位

Evaluation Run Contract（评测运行契约）是一个严格的本地合成生命周期记录，用来回答：

> 哪个 Evaluation Input，在什么声明版本的 Evaluator、Grader、Criteria 和环境下，对应哪个结果与 Derived Evidence Case？

它强化 Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）的运行溯源，不实现 Evaluation Engine，不执行 Agent，也不改变 Digital Biosphere Evolution Engine（数字生物圈进化引擎）的项目核心。

## 2. Evaluation Input、Evaluation Run 与 Evidence Case

三个对象职责不同：

| 对象 | 回答的问题 | 不负责 |
|---|---|---|
| Evaluation Input | 测什么任务、环境、候选与合成观察？ | 不说明是哪一次运行 |
| Evaluation Run Contract | 哪次运行生命周期绑定了什么输入、版本、结果与 Evidence Case？ | 不实现真实 Evaluator Runtime |
| Evidence Case | 最终形成什么证据支撑的评测结果？ | 不自动携带完整运行历史，也不授权部署 |

Phase 1.97 补齐：

```text
Evaluation Input
        ↓ consumed_by
Evaluation Run Contract
        ↓ produces
Evaluation Result
        ↓ binds_to
Derived Evidence Case
```

`reverse_lookup_anchor` 允许通过独立 Run Contract 索引从 Evidence Case 的稳定 `case_id` 反查 Run 和 Input。Evidence Case v0.1 保持冻结，不加入新顶层字段。

## 3. Input Lineage

每份 Run Contract 同时绑定：

- Evaluation Input 文件路径与 SHA-256；
- Replay Evaluation Contract 文件路径与 SHA-256；
- Replay Evaluation Contract 内声明的同一 Evaluation Input；
- Result 的规范化 SHA-256；
- Derived Evidence Case 的稳定 `case_id` 与规范化 SHA-256。

当前 `result_ref` 和 `evidence_case_ref` 是逻辑标识。Smoke 使用现有本地合成 Case Builder 重新计算规范化输出并验证摘要，而不是访问外部 Artifact Store。

## 4. Evaluator 版本管理

一个 Run 只能绑定一个：

```text
evaluator_ref
evaluator_version
```

多 Evaluator 比较必须由多个 Run 表达，而不是把多个 Evaluator 塞入同一个 Run。v0.1 验证引用和版本字段存在且在重复运行中保持一致，但不独立验证 Evaluator 发布者、代码真实性或外部来源，因此：

```text
evaluator_provenance_independently_verified=false
```

## 5. Grader 与 Criteria 版本管理

每个 Run 必须明确：

```text
grader_ref
grader_version
criteria_ref
criteria_version
```

Grader 表示评判机制的声明身份；Criteria 表示适用规则集。相同 Input 在不同版本下必须创建不同 Run。v0.1 只验证声明绑定，不证明这些引用的外部真实性。

## 6. Run Status

v0.1 只接受三类本地合成记录：

- `synthetic_recorded_completed`：合成运行记录完成；
- `synthetic_recorded_completed_with_evaluation_failure`：运行记录完成，但评测内容包含失败情形；
- `synthetic_recorded_repeat_completed`：使用相同 Input、Evaluator、Grader、Criteria 再次记录确定性结果。

`failed-evaluation-run.json` 不是 Runtime 崩溃记录，也不表示真实 Agent 执行失败。

重复运行必须带 `repeat_of_run_ref`，并保持 Input、Replay Evaluation、Evaluator、Grader、Criteria、Result 和 Evidence 摘要一致。

## 7. 不执行 Agent 的边界

Phase 1.97 不提供真实 Evaluator Runtime，不执行 Agent、不调用工具、不访问网络、不读取客户数据。Smoke 仅调用仓库已有的本地合成 Case Builder，验证声明的规范化 Result 和 Evidence Case 摘要。

所有对象强制：

```text
real_evaluator_runtime_executed=false
real_agent_executed=false
external_tool_executed=false
network_accessed=false
customer_data_processed=false
```

## 8. Risk 与 Decision 边界

Evaluation Run Contract 不能把合成结果升级为真实风险概率，也不能做自动决策或部署授权：

```text
risk_probability_measured=false
automatic_decision=false
deployment_authorized=false
risk_model_implemented=false
production_ready=false
```

它记录运行溯源，不是 Risk Model，也不是 Decision Authority。

## 9. 验证

```bash
python3 scripts/saee_evaluation_run_contract_smoke.py
```

或运行包含 Phase 1.95、1.9、1.75、1.5 与 v3 回归的入口：

```bash
make check-saee-evaluation-run-contract
```

验证覆盖：

- 严格 Schema 与负例；
- Input 和 Replay Evaluation 文件摘要；
- 声明的 Evaluator、Grader、Criteria 版本绑定；
- Result 与 Evidence Case 规范化摘要；
- Run 正向溯源与 Evidence 反查；
- 重复运行绑定；
- 冻结文件 SHA-256；
- 无真实 Runtime、Risk 概率、自动 Decision 或部署权限。

## 10. 当前限制

- 仅三份本地合成 Run Contract；
- Evaluator、Grader、Criteria Provenance 只是声明，没有独立验证；
- Result 和 Evidence Case 通过本地确定性重算验证，没有外部 Artifact Store；
- 不记录真实失败 Runtime 的异常、重试或恢复过程；
- 不实现真实 Replay、Evaluator Runtime、Agent、工具或网络；
- 不构成外部验证、客户验证、生产就绪、标准兼容或合规声明。

Phase 2 Consent-First Offline Replay 继续保持 `HOLD`，直到 Phase 1.97 通过独立只读架构审查。
