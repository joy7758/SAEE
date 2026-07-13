# SAEE Phase 2A Readiness Gate

## 1. Gate 目标

本 Gate 判断冻结的 SAEE Contract Stack 是否可以进入 Phase 2A Synthetic Assurance Pipeline Execution（合成保障流水线执行）。

它不是 Replay Contract、Execution Contract 或部署许可。Gate 只进行本地只读检查，不执行 Replay、Mapping、Evaluator、Agent 或外部工具。

智能体推荐结论：

```text
recommend
```

推荐范围仅限：

> 使用仓库内合成声明、固定 Schema、允许列表路径和确定性本地代码，准备一次无网络、无真实 Agent、无客户数据的 Phase 2A 实施任务。

## 2. 允许范围

- 读取冻结 Schema 和本地合成 JSON；
- 校验 JSON Schema、SHA-256、对象引用和生命周期互斥；
- 检查合成来源、内容排除、人工控制和无外部副作用边界；
- 输出 `PHASE2A_GATE_PASS` 或 fail-closed 错误；
- 后续 Phase 2A 可使用固定内部实现应用声明式 Mapping，但不得把 Mapping Rule 当作外部代码执行。

## 3. 禁止范围

- 真实 Agent、真实 Evaluator Runtime 或外部工具执行；
- 网络、DNS、API、外部仓库、包管理器或依赖安装；
- 客户数据、个人数据、Raw Prompt、Raw Output、Hidden Reasoning；
- 任意脚本、插件、Mapping Code 或候选代码执行；
- 自动决策、部署授权、权限扩张；
- 修改冻结 Contract 或把 Gate PASS 表述为生产就绪。

## 4. Synthetic-only 判定

Observation 的语义类型可以是：

```text
synthetic_environment
runtime_observation
tool_trace_observation
```

后两个名称不代表真实 Runtime 或真实 Tool 数据。Gate 仅在以下条件同时成立时把来源判为 `synthetic_only`：

```text
authorization.status=synthetic_declared_only
sanitization.status=synthetic_no_raw_content
sanitization.method=synthetic_generation
source.raw_content_included=false
source.external_execution_by_saee=false
producer.adapter_implemented=false
privacy.personal_data_included=false
every_event.payload_included=false
truth_boundary.real_agent_executed_by_saee=false
truth_boundary.network_accessed=false
```

任何外部 Attestation、Raw Content、客户/个人数据或已实现 Adapter 都必须拒绝。

## 5. Gate 规则

### A. Contract Integrity

```text
contract_stack_valid=true
frozen_contracts_unchanged=true
schema_versions_valid=true
reference_digests_valid=true
```

### B. Data Boundary

```text
source_type=synthetic_only
customer_data_present=false
personal_data_present=false
raw_prompt_present=false
raw_output_present=false
hidden_reasoning_present=false
raw_content_present=false
```

这里的内容检查依据结构化 Content Boundary、Sanitization 和 `payload_included=false`，不会因为字段名 `hidden_reasoning_excluded` 本身而误报。

### C. Execution Boundary

```text
network_allowed=false
external_tool_execution_allowed=false
real_agent_execution_allowed=false
external_code_execution_allowed=false
dependency_install_allowed=false
mapping_rule_executable=false
```

Gate 脚本自身只能读取文件、计算摘要和执行 Schema 校验；禁止导入网络、子进程或包安装能力。

### D. Human Control

```text
manual_start_required=true
operator_present=true
stop_authority_present=true
```

### E. Lifecycle Integrity

```text
completed_termination_run_id_intersection=0
exactly_one_lifecycle_output=true
completed_xor_terminated=true
partial_result_is_evidence=false
terminated_path_evidence_case_produced=false
```

### F. Decision Boundary

```text
automatic_decision=false
deployment_authorized=false
production_ready=false
```

## 6. PASS 的含义

`PHASE2A_GATE_PASS` 只表示：

> 当前本地合成 Contract Stack 满足另行实施 Phase 2A 的前置条件。

它不表示：

- Replay 已执行；
- Mapping 已执行；
- Agent 或 Tool 已执行；
- Result 正确或 Evidence 真实；
- 真实数据、客户试点、外部验证或生产部署获得授权。

Phase 2A 实施必须生成独立 Execution Report，不能回写冻结对象中的 `replay_executed=false` 或 `mapping_executed=false`。

## 7. 运行

```bash
python3 scripts/saee_phase2a_readiness_gate.py
```

或：

```bash
make check-saee-phase2a-readiness-gate
```

任何检查失败均返回非零退出状态，并保持 Phase 2A 未授权执行。

## 8. 当前限制

- Gate 只覆盖仓库内现有合成样例；
- 不验证 Consent、Permission、Stop Authority 或 Provenance 的外部真实性；
- 不执行 Mapping 或生成新的 Run/Evidence；
- 不授权 Phase 2B Adapter、真实数据、真实 Agent、客户验证或生产部署。

## Required Design Check

1. 强化子系统：Sandbox Development 与 Evolutionary Archive / Rollback Immune System。
2. 改善能力：执行前选择、失败即关闭、溯源和回滚边界检查。
3. 安全边界：无网络、无外部代码、无权限扩张、无客户数据、无真实 Agent。
4. Audit-first 风险：Gate 服务于 Deployment Assurance 的受控沙盒验证，不改变 SAEE 核心身份。
