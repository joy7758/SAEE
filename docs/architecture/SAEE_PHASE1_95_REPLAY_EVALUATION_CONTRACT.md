# SAEE Phase 1.95 Replay Evaluation Contract v0.1

## 1. 定位

Replay Evaluation Contract（回放评测契约）定义一个**本地合成、不可执行的确定性映射契约**：它把已获准用于特定目的的 Replay Contract（回放契约）绑定到一个既有 Evaluation Input（评测输入），并保存转换规则与来源链。

它强化 SAEE 的 Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）：评测输入可以反查其 Observation、Replay 治理上下文、Consent、数据使用权限和转换来源。它不改变 Digital Biosphere Evolution Engine（数字生物圈进化引擎）的核心定位，也不把 SAEE 重构为审计 SDK。

## 2. Replay Contract 与 Replay Evaluation Contract 的区别

| 对象 | 回答的问题 | 不负责 |
|---|---|---|
| Observation Envelope | 看到了什么可观察元数据？ | 不证明事件、授权或真实性 |
| Replay Contract | 哪些 Observation 可在什么治理边界下重建上下文？ | 不执行 Replay，不生成 Evaluation Input |
| Replay Evaluation Contract | 允许使用的 Observation 如何声明性地绑定到 Evaluation Input？ | 不执行映射，不评测，不生成 Risk 或 Decision |
| Evaluation Input | 评测任务、环境、候选与合成观察是什么？ | 不自动成为 Evidence |
| Evidence Case / Decision Support | 得出了什么受边界约束的结果和建议？ | 不自动授权部署 |

核心链路：

```text
Observation Envelope
        ↓ governed_by
Replay Contract
        ↓ mapped_by
Replay Evaluation Contract
        ↓ binds_to
Evaluation Input
        ↓ derives_to
Derived Evidence Case
```

`reverse_lookup_anchor` 允许验证器从 Derived Evidence Case 的稳定 `case_id` 反查 Evaluation Input，再通过本契约回到 Replay Contract 与 Observation Envelope。v0.1 不修改冻结的 Evidence Case Schema，因此该反查依赖独立契约索引，而不是在 Evidence Case 顶层加入新字段。

## 3. Replay 不是 Execution

Phase 1.95 不运行真实 Agent、不调用工具、不访问网络、不读取客户数据，也不执行 Replay。`replay_contract_ref` 和 `source_observation_refs` 仅解析仓库内允许目录的本地 JSON 文件并校验 SHA-256 摘要。

`observation_mapping_rules` 是声明性规则：

- `deterministic=true` 表示相同契约应产生相同验证结果；
- `executable=false` 表示规则不是代码，不授予执行权限；
- `mapping_executed=false` 与 `evaluation_input_generated=false` 表示本阶段只定义并验证绑定。

## 4. 转换不是 Decision

Replay Evaluation Contract 的唯一输出边界是对**既有 Evaluation Input 的绑定**。它不能直接产生 Risk，也不能产生或授权 Decision。

禁止链路：

```text
Replay → Risk
Replay → Deployment Decision
```

允许的概念顺序：

```text
Replay Evaluation Contract
        ↓
Evaluation Input
        ↓
Evaluation
        ↓
Evidence
        ↓
Risk Interpretation
        ↓
Decision Support
```

## 5. Evaluation Input 来源链

每份契约必须绑定：

- Replay Contract 文件路径与 SHA-256；
- Observation Envelope 的 `observation_id`、文件路径与 SHA-256；
- Replay 中的 `consent_ref` 与 `data_use_permission_ref`；
- Replay 转换日志中的 `provenance_ref`；
- Evaluation Input 文件路径与 SHA-256；
- Evaluation Input 内的 `task_contract_id` 和 `environment_contract_id`；
- Observation → Replay → Replay Evaluation → Evaluation Input → Derived Evidence Case 的显式边。

验证成功仅证明：本地文件、声明字段、摘要和引用在当前仓库快照中一致。它不独立证明 Consent 有效、Permission 合法、Observation 真实或转换来源可信。

## 6. Failure Estimate 与 Risk 边界

`failure_estimate_source` 是来源说明，不是风险概率证明。v0.1 只允许：

```text
source_type=synthetic_rule_reference
generated_from_trace=false
generated_by_replay=false
risk_probability_measured=false
```

因此 Trace 摘要不能自动生成 failure estimate；Replay 也不能直接生成 Risk。实际风险模型、校准概率和生产测量均未实现。

## 7. 人类控制与真值边界

每份契约必须保存 `operator_ref` 与 `stop_authority_ref`。所有样例均保持：

```text
automatic_decision=false
deployment_authorized=false
architecture_implemented=false
risk_model_implemented=false
real_agent_executed=false
customer_data_processed=false
customer_validated=false
production_ready=false
```

SAEE 输出仍是 Decision Support（决策支持），不是 Decision Authority（决策权限）。

## 8. 离线验证

```bash
python3 scripts/saee_replay_evaluation_contract_smoke.py
```

或运行包含回归检查的入口：

```bash
make check-saee-replay-evaluation-contract
```

检查覆盖严格 Schema、负例、文件摘要、Consent/Permission/Transformation 传播、五层溯源、既有 Case Builder 反查、确定性和冻结文件哈希。

## 9. 当前限制

- 仅有三份本地合成契约；
- 不执行映射或 Replay；
- 不验证外部身份、Consent、Permission、Provenance 或内容真实性；
- 不接入真实 Agent、Runtime Adapter、Memory Adapter 或 Tool Trace Adapter；
- 不产生真实失败概率、Risk Model、自动 Decision 或部署授权；
- 不构成外部验证、客户验证、生产就绪、标准兼容或合规声明。

Phase 2 仍保持 `HOLD`，直到另行授权并通过 Consent-First Offline Replay 的实现审查。
