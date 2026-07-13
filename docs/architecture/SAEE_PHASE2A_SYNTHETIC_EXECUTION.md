# SAEE Phase 2A Synthetic Assurance Pipeline Execution

## 1. 目标

Phase 2A 第一次验证冻结的 SAEE Contract Stack 能否约束一条以既有 Evaluation Input 为起点、本地、合成、确定性且无外部副作用的保障流水线。

它不评估真实 Agent 能力，不处理客户数据，也不表示生产部署。它强化 Sandbox Development（沙盒发育）、Pareto Fitness Evaluation（帕累托适应度评估）与 Evolutionary Archive / Rollback Immune System（演化档案 / 回滚免疫系统）的受控连接。

## 2. Runner 职责

入口：

```text
scripts/saee_phase2a_synthetic_runner.py
```

Runner 只做：

1. 重新运行 Phase 2A Readiness Gate；
2. 接受固定允许列表中的 Replay Evaluation Contract；
3. 校验 Replay、Evaluation Input 路径和 SHA-256；
4. 检查人工启动、Stop Authority、合成 Consent/Permission 和无执行边界；
5. 忽略 Mapping Rule 的可执行含义，只使用已绑定的 Evaluation Input；
6. 在 Completed 路径调用现有本地合成 Case Builder；
7. 生成 Evaluation Run Contract 与 Derived Evidence Case，或生成 Termination Contract；
8. 将独立 Execution Report 输出到标准输出，不写回冻结对象。

Runner 不解释自由文本，不修改规则，不动态加载模块，不执行候选代码。

Runner 会验证 Replay Contract 的引用、摘要和边界，但不会根据 Observation Envelope 执行元数据重建，也不会重新生成 Evaluation Input：

```text
synthetic_replay_contract_validated=true
synthetic_metadata_reconstruction_applied=false
synthetic_offline_replay_executed=false
```

## 3. 固定内部转换

```text
Allowlisted Replay Evaluation Contract
        ↓ validate contract, reference and digest
Pre-existing Bound Evaluation Input
        ↓ existing fixed local synthetic Case Builder
Evaluation Run Contract
        ↓
Derived Evidence Case
```

`observation_mapping_rules` 只被验证为：

```text
deterministic=true
executable=false
```

Runner 不把它们转换成 Python、Shell、表达式或插件执行：

```text
declared_mapping_rules_executed_as_code=false
```

因此，本阶段执行的是 Fixed Evaluation Input Pipeline（固定评测输入流水线），不是 Observation → Replay → Evaluation Input 重建：

```text
fixed_evaluation_input_pipeline_executed=true  # 仅 Completed 路径
```

## 4. Completed 路径

成功路径输出：

```text
lifecycle_output.completed=true
lifecycle_output.terminated=false
evaluation_run_contract=<valid v0.1 object>
evidence_case=<derived local synthetic object>
termination_contract=null
```

Result 与 Evidence Case 使用规范化 JSON SHA-256 绑定。Runner 不新增 Decision 算法；Evidence Case 中已有的 Scenario-scoped Decision Support 来自既有 Case Builder，并继续保持：

```text
automatic_decision=false
deployment_authorized=false
risk_probability_measured=false
```

## 5. Terminated 路径

Runner 支持固定合成生命周期：

```text
manual_abort
runtime_failed
input_rejected
```

终止路径输出：

```text
lifecycle_output.completed=false
lifecycle_output.terminated=true
evaluation_run_contract=null
evidence_case=null
termination_contract=<valid v0.1 object>
```

输入拒绝发生在 Case Builder 之前；所有路径都不执行元数据重建：

```text
run_started=false
synthetic_metadata_reconstruction_applied=false
synthetic_offline_replay_executed=false
fixed_evaluation_input_pipeline_executed=false
fixed_internal_transform_applied=false
```

终止路径不会产生 Evidence。

## 6. 严格二选一

每次 Runner 调用必须满足：

```text
completed XOR terminated = true
```

禁止：

- 同一报告同时包含 Completed Run 和 Termination；
- Termination 带 Evidence Case；
- Completed 路径缺少 Run 或 Evidence；
- Partial Result 被提升为 Evidence。

## 7. 执行边界

Phase 2A 允许的“执行”仅包括：

- 本地 JSON 读取；
- SHA-256；
- Schema 和 Gate 校验；
- 固定内部 Python 数据转换；
- 既有本地合成 Case Builder。

严格禁止：

```text
real_agent_executed=true
real_evaluator_runtime_executed=true
external_tool_executed=true
network_accessed=true
external_code_executed=true
dependency_installed=true
customer_data_processed=true
```

Runner 和 Smoke 不导入 `socket`、`subprocess`、`urllib`、`requests`、`httpx` 或 `pip`。

## 8. Execution Report

Runner 输出 `saee_phase2a_synthetic_execution_report_v0_1` JSON，其中明确记录：

```text
execution_mode=synthetic_offline_fixed_evaluation_input_pipeline
gate_result=PHASE2A_GATE_PASS
declared_mapping_rules_executed_as_code=false
synthetic_replay_contract_validated=true
synthetic_metadata_reconstruction_applied=false
synthetic_offline_replay_executed=false
preexisting_evaluation_input_loaded=true
fixed_evaluation_input_pipeline_executed=<true only for Completed path>
fixed_internal_transform_applied=<boolean>
local_synthetic_case_builder_applied=<boolean>
real_agent_executed=false
network_accessed=false
customer_data_processed=false
production_ready=false
```

该报告不修改 Phase 1.x 契约中的历史字段，也不表示 Observation 元数据重建、完整离线 Replay、真实 Agent 或客户验证。

## 9. 使用方法

Completed：

```bash
python3 scripts/saee_phase2a_synthetic_runner.py \
  --input agent-interface/architecture/examples/replay-evaluation/synthetic-replay-evaluation.json \
  --lifecycle completed
```

人工终止：

```bash
python3 scripts/saee_phase2a_synthetic_runner.py \
  --input agent-interface/architecture/examples/replay-evaluation/transformed-replay-evaluation.json \
  --lifecycle manual_abort
```

输入拒绝：

```bash
python3 scripts/saee_phase2a_synthetic_runner.py \
  --input agent-interface/architecture/examples/replay-evaluation/consent-bound-replay-evaluation.json \
  --lifecycle input_rejected
```

验证：

```bash
python3 scripts/saee_phase2a_execution_smoke.py
```

## 10. 当前限制

- 只接受三个固定 Replay Evaluation Contract；
- Replay Contract 仅被校验，不执行 Observation 元数据重建或 Evaluation Input 再生成；
- Lifecycle 选择由显式本地命令参数提供，不是自动风险判断；
- 不执行 Mapping Rule 代码；
- 不接 Adapter、真实 Agent、真实 Tool、网络或客户数据；
- 不验证 Consent、Permission、Provenance 或 Evidence 的外部真实性；
- 不构成外部验证、客户验证、生产就绪或部署许可。

Phase 2B Receive-only Adapter Prototype 仍处于 HOLD；下一步必须先定义 `PHASE2B_ADAPTER_READINESS_GATE`，不得直接实现 Adapter。
