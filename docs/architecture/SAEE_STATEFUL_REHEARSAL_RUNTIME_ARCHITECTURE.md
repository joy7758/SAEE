# SAEE Stateful Agent Rehearsal Runtime Architecture v0.1

状态：`architecture_design_reusing_existing_single_provider_runtime`。

## 1. 目的与非重复建设原则

本规范定义“真实模型智能体 + 受控合成世界”的多供应商演练架构。它不创建第二套 Runtime，也不创建第二个 Evidence Evaluator；已有千帆有状态演练、Observation Envelope、Evidence Adequacy 和 `evaluate_agent_run` 是必须复用的基线。

```text
Real Model Agent
  ↓
Provider-neutral Agent Adapter
  ↓
Stateful Synthetic Business World
  ↓
Simulated Tools
  ↓
Execution Observation
  ↓
Existing Evidence Pipeline
  ↓
Existing SAEE Evaluation
  ↓
Bounded Agent Readiness Report
```

本规范强化 `Ecological World Model`、`Counterfactual Simulation`、`Sandbox Development`、`Pareto Fitness Evaluation` 与 `Evolutionary Archive`。Evidence 仍是免疫/证明子系统，不取代 Digital Biosphere Evolution Engine 的工程核心。

## 2. 现有资产映射

| 层 | 复用资产 | 当前证明范围 |
|---|---|---|
| Agent Layer | POP、Agent Object、Intent、Token Governor 的现有概念投影；Qianfan controlled/stateful adapter | 身份、目标、预算、provider 与模型边界 |
| Environment Layer | `saee-stateful-business-scenario.v0.3`、`stateful_business_rehearsal.py` | 单一 SaaS 合成世界、三次状态迁移 |
| Observation Layer | `saee-observation-envelope.v0.1.schema.json`、现有 Trace | 观察摘要与状态事件，不自动成为 Evidence |
| Evidence Layer | Rehearsal Evidence Export、Resource Receipt、Evidence Case | 摘要绑定与候选证据关系 |
| Evaluation Layer | `evidence_adequacy.py`、`agent_run_capability.py` | 固定 profile 范围内的充分性判断 |

`verifiable-agent-demo`、ARO Audit、agent-evidence 等相邻概念只能通过文件化契约进入 Evidence Layer；本架构不假定未映射仓库已经成为运行依赖。

## 3. Agent Adapter Layer

统一接口：

```python
run_agent_task(
    agent_profile,
    task,
    environment_state,
    available_tools,
) -> AgentExecutionResult
```

`AgentExecutionResult` 只保存 provider、`model_vendor`、model、可观察消息摘要、工具调用、输出摘要、时间戳、状态变化引用和执行状态。它不得保存隐藏推理、私有模型状态或原始 provider payload。

### Provider Gateway 与 Model Vendor

两者必须分开：

- `provider_gateway` 决定鉴权、API、成本与网络 allowlist；
- `model_vendor` 表示实际模型来源；
- 同一个 `volcengine_ark` Adapter 可以承载豆包、DeepSeek、智谱或月之暗面模型；
- 千帆目录同样可承载百度以外的模型标识；不能把 `baidu_qianfan` Gateway 等同于 Baidu Model Vendor；
- 目录可见不等于当前项目可调用。

当前状态：

| Gateway | Model vendor | 状态 |
|---|---|---|
| Baidu Qianfan | Baidu | 已有 ERNIE 受控有状态 Adapter 与本地证据 |
| Baidu Qianfan | DeepSeek / Zhipu / Moonshot / Qwen 等目录标识 | 已观察多厂商模型目录；本次未执行跨厂商演练或 Function Calling |
| OpenAI-compatible | OpenAI | 本规范中的设计目标，未形成仓库 Runtime Adapter |
| Volcengine Ark | ByteDance | 已观察基础推理与 Function Calling；本规范未实现 Adapter |
| Volcengine Ark | DeepSeek | 已完成 Coding Release 受控多轮 Function Calling 演练；不是通用 Adapter 验证 |
| Volcengine Ark | Zhipu | 已完成 Coding Release 受控多轮 Function Calling 演练；不是通用 Adapter 验证 |
| Volcengine Ark | Moonshot | 模型目录可见，但当前所列 Kimi 版本为 Shutdown/Retiring，调用未通过 |
| Anthropic-compatible | Anthropic | `design_only_not_configured_not_tested` |

详细观察：

- `agent-interface/rehearsal/saee-volcengine-multi-vendor-observation.v0.1.json`
- `agent-interface/rehearsal/saee-qianfan-multi-vendor-observation.v0.1.json`
- `agent-interface/benchmark/saee-agent-comparison-result.v0.1.json`

## 4. Stateful Rehearsal Environment

每个世界状态固定拆分为：

```text
World State
Task State
Resource State
Policy State
Risk State
```

每次工具结果产生一个显式 revision：

```text
revision_0
  ↓ observable agent action
revision_1
  ↓ simulated tool result
revision_2
```

历史必须包含 revision、前后状态摘要、工具名、风险信号和 `external_effect=false`。风险状态是场景内参考，不是现实失败概率。

## 5. Scenario Framework

新场景位于 `agent-interface/rehearsal/scenarios/stateful-runtime-v0.1/`，使用独立 schema，避免污染现有固定内部 Agent Runtime 的根目录 allowlist。

首批五类：

1. `001_coding_release`；
2. `002_customer_operation`；
3. `003_research_agent`；
4. `004_business_operator`；
5. `005_security_boundary`。

它们当前均为 `DESIGN_ONLY_NOT_EXECUTED`。场景规定真实模型执行是未来 Runtime 的必要条件，但场景文件本身不是执行证据。

## 6. Tool Simulator

固定工具：`code_repository`、`test_runner`、`deployment_simulator`、`database_simulator`、`customer_ticket_system`。

所有工具只修改内存合成状态。不存在 shell、真实仓库、真实数据库、真实客户系统、真实部署或生产基础设施访问。

## 7. Observation Contract

每个 Observation 包含：

```text
event_id
agent_id
timestamp
action
tool_call
input_summary
output_summary
state_transition
risk_signal
```

明确排除：隐藏推理、chain-of-thought、私有模型状态和原始 provider payload。Observation 记录可观察动作，不记录模型内部思考过程。

## 8. Evidence Pipeline

唯一允许的数据流：

```text
Execution Trace
  ↓
Observation Envelope
  ↓
Evidence Case
  ↓
existing evidence_adequacy evaluator
  ↓
evaluate_agent_run / bounded report
```

不得创建第二个 evaluator。Observation 不能直接升级为 Evidence；`SUPPORTED` 也不等于成功、安全、合规或获准部署。

## 9. Multi-Agent Evaluation

同一 scenario 可以交给多个 Provider/Model Adapter，按以下维度分别比较：

- task completion；
- evidence quality；
- boundary behavior；
- recovery behavior；
- state consistency。

输出必须保留 provider、model vendor、model version 和场景 revision。不得合成为“绝对智能排名”，不得把不同 provider 的可用性或响应风格解释为通用能力高低。

## 10. 运行边界

未来有效运行必须同时满足：

```text
real_model_execution=true
external_world_actions=false
customer_data_used=false
production_execution=false
```

本架构设计自身的当前真值：

```text
architecture_only=true
multi_provider_runtime_implemented=false
new_provider_adapter_implemented=false
second_evaluator_created=false
production_ready=false
```
