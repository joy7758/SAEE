# SAEE Agent Readiness Architecture v1.0

状态：`phase6_5_controlled_qianfan_agent_preference_validated`。

```yaml
artifact: SAEE_AGENT_READINESS_ARCHITECTURE_V1
architecture_version: 1.0
scope: l3_commercial_product_projection
canonical_architecture_replaced: false
runtime_added: false
agent_rehearsal_runtime_implemented: true
evaluate_agent_run_available: true
production_ready: false
customer_validated: false
```

## 1. 本次重统一解决什么

SAEE 曾沿着 Evidence、Capability Registry、MCP Prototype 和 Pilot Gate
持续深化，却没有先完成商业入口所依赖的 Agent Rehearsal Runtime。Phase
6.0 不删除这些资产，也不把不存在的 Runtime 写成已实现；它将已有资产归位，
恢复正确依赖顺序。

本规范明确区分五个身份：

| 角色 | 统一定义 |
|---|---|
| 工程核心 | `Digital Biosphere Evolution Engine` |
| 商业方向 | `Agent Readiness Infrastructure`（智能体就绪基础设施） |
| 面向人的产品 | `SAEE Agent Readiness Platform`（SAEE 智能体上线准备平台） |
| 第一产品入口 | `Agent Rehearsal Engine`（智能体演练引擎） |
| 技术护城河 | `Evidence Intelligence`（证据智能） |
| 面向智能体的未来入口 | `SAEE Agent-Native Capability Interface` |

Evidence 是免疫与证明子系统，不是 SAEE 的工程核心。本规范不把项目重构为
audit SDK、通用 Agent framework 或生产治理平台。

## 2. 与 canonical 三层架构的关系

权威架构仍然是：

```text
L1 Frozen Scientific Object (LCR-REDS)
 ↓
L2 Meta-Protocol System (SAEE-MP)
 ↓
L3 Engineering / Runtime / Experiment Projection
```

本文件的四层结构是 L3 内部的商业产品投影，不创建新的理论权威，也不替换
`FINAL_ARCHITECTURE_SPEC.md`。依赖只能从 canonical 定义流向产品投影，产品
运行、商业材料或局部实验不得反向修改 L1/L2。

## 3. 四层 Agent Readiness 产品投影

### Layer 1 — Agent World Layer

回答 Agent 是谁、想做什么、声明了什么能力。它把 Digital Biosphere、POP、
Agent Object、Intent Protocol、Token Governor 等现有概念投影为演练输入边界。

当前状态：`partial_existing_assets`。这些资产存在，但尚未形成统一的 Rehearsal
输入适配协议。

### Layer 2 — Agent Rehearsal Layer

回答 Agent 在受控世界中如何接受测试。目标组件是：

- `Agent Adapter`：统一的 `run_task()` 边界；
- `Scenario Runner`：加载固定、版本化、本地场景；
- `Controlled Environment`：合成 Repo、模拟 API、临时数据库与受控工具；
- `Trace Collector`：记录动作、工具结果、状态变化、失败与恢复；
- `Evidence Export`：将演练产物交给现有 Observation/Evidence 管线。

当前状态：`local_controlled_synthetic_agent_runtime_implemented`。Phase 6.1
已经新增固定内部策略 Agent、Scenario Runner、内存受控工具、Trace Collector
和 Evidence Candidate Export。仓库中的旧合成 Case、Replay、Pilot Simulation
和 MCP Invocation Evaluation 仍不能单独作为 Runtime 实现证据；实现证据是
`agent_rehearsal_runtime.py` 及其 Runtime smoke。

“真实演练”指 Agent 在本地或另行批准的隔离沙箱中真实执行受控场景，不指
直接操作生产世界。不得自动安装未知依赖、执行未知仓库、扩大权限或访问未批准
网络。

### Layer 3 — Evidence Intelligence Layer

回答 Trace 能否形成证据，以及这些证据是否足以支持限定责任声明：

```text
Execution Trace
 ↓
Observation
 ↓
Evidence Object
 ↓
Claim-specific Adequacy Evaluation
 ↓
Bounded Readiness Assessment
```

当前状态：`implemented_local_synthetic_and_declared_scope`。资源解析收据、
Observation Contract、Replay/Evaluation Contracts、Evidence Adequacy、Case
Corpus、Review Report 和可复现性资产均归入本层。

Phase 4/5 的 External Integration Design、Pilot Gate、Gap Plan 和 Re-readiness
Simulation 统一冻结为 `SAEE Governance and Evidence Control Plane v0.1`。
它们负责边界与证据治理，但不构成 Rehearsal Runtime，也不证明客户验证或生产
就绪。

### Layer 4 — Agent-Native Interface Layer

回答外部 Agent 如何发现、理解和调用 SAEE。Capability Manifest、Capability
Object、Registry、本地 Tool 和本地 MCP Prototype 均归入本层。

当前状态：`local_prototype_only`。这些表面证明本地机器契约与调用路径可以被
验证，不证明公开 MCP、真实外部 Agent 兼容、市场采用或生产服务可用。

## 4. 唯一产品数据流

```text
Agent
 ↓
Rehearsal
 ↓
Trace
 ↓
Evidence
 ↓
SAEE Evaluation
 ↓
Capability Service
 ↓
Agent Economy
```

禁止的捷径：

- Agent 不能绕过 Rehearsal/Trace 直接获得 readiness 结论；
- Trace 不能绕过 Evidence 直接变成证明；
- Evidence `SUPPORTED` 不能升级为安全、合规或部署批准；
- Capability Interface 不能在 Runtime 缺失时声称完整产品已经可调用；
- Pilot Simulation 不能升级为真实客户或生产验证。

## 5. 当前资产归位

| 当前资产 | 新位置 | 可证明范围 | 不能证明 |
|---|---|---|---|
| Digital Biosphere、POP、Intent | Agent World | 身份、意图与演化输入概念 | 统一 Adapter 已实现 |
| Synthetic Case、Evaluation Prototype | Rehearsal 前置材料 | 场景和评测契约可本地复现 | Agent 已真实参加演练 |
| Observation/Replay/Evaluation Contracts | Evidence Intelligence | 结构化转换链与边界 | 外部运行真实性 |
| Evidence Objects、Adequacy、Reports | Evidence Intelligence | profile 范围内证据充分性 | 安全、合规或部署批准 |
| Manifest、Registry、Local Tool/MCP | Agent-Native Interface | 本地发现与固定调用契约 | 公开服务和外部兼容 |
| Phase 5 Pilot Gates | Governance and Evidence Control Plane | fail-closed 规则与缺口台账 | Pilot 已执行或获批 |

## 6. Phase 6.1 Runtime MVP 契约边界

Phase 6.1 才允许新增行为。最小闭环必须同时具备：

```text
fixed synthetic scenario
  + approved local Agent adapter
  + isolated execution workspace
  + allowlisted tools
  + deterministic lifecycle controller
  + trace collection
  + evidence export
  + existing adequacy evaluation
```

`run_task()` 的未来概念输入必须包含 scenario、Agent reference、sandbox policy、
tool allowlist 和 stop conditions；输出必须分离 run status、trace reference、
evidence export reference、termination reason 和 limitations。

Phase 6.1 v0.1 固定规则管线完成后的精确状态：

```text
agent_rehearsal_runtime_implemented=true
agent_adapter_implemented=true
scenario_runner_implemented=true
trace_collector_implemented=true
evidence_export_from_rehearsal_implemented=true
real_external_agent_executed=false
```

Phase 6.1 v0.2 已在此基础上增加百度千帆真实推理模型，但仍只进入完全合成世界：

```text
controlled_external_reasoning_model_rehearsal_validated=true
controlled_reasoning_live_runs=3
grading_profiles_hidden_from_agent=true
external_world_actions=0
real_customer_agent_tested=false
production_ready=false
```

Phase 6.1 v0.3 进一步增加有状态、多步骤的 SaaS 发布世界：

```text
stateful_business_rehearsal_validated=true
stateful_business_live_runs=1
state_transition_count=3
customer_controlled_adapter_contract_available=true
customer_controlled_adapter_enabled=false
external_world_actions=0
```

## 7. Phase 6.2 Agent Capability Alpha 边界

`evaluate_agent_run` 已在 Phase 6.1 产生 run/trace/evidence 链后实现为本地
离线 Alpha。它评估证据充分程度和缺口，不输出 `SAFE`、`COMPLIANT`、
`CERTIFIED` 或自动部署许可。

当前状态：

```text
evaluate_agent_run_available=true
agent_callable_runtime=true
public_api_available=false
public_mcp_available=false
```

## 8. 冻结路线

| 阶段 | 目标 | 当前状态 |
|---|---|---|
| 6.0 | Architecture Reunification | `completed_documentation_and_truth_alignment` |
| 6.1 | Agent Rehearsal Runtime MVP | `stateful_multi_step_qianfan_business_rehearsal_validated_customer_agent_pending` |
| 6.2 | Agent Capability Alpha: `evaluate_agent_run` | `completed_local_offline_alpha` |
| 6.3 | 20-scenario Readiness Benchmark | `completed_local_20_case_synthetic_benchmark` |
| 6.4 | MCP Capability Release | `completed_local_in_memory_capability_no_standard_transport` |
| 6.5 | Agent Preference Validation | `controlled_qianfan_multi_agent_preference_validated_human_participants_excluded` |

商业顺序保持：先用 Agent Rehearsal Assessment 形成面向人的价值，再发展持续
测试，最后才考虑 Agent 自主调用经济。不得把未来 Agent 付费市场作为当前收入
成立的证据。

## 9. Truth Boundary

Phase 6.0/6.1 证明架构已重新统一，固定规则 Runtime 已执行，百度千帆真实推理模型
已完成三个单步受控场景和一个有状态多步骤 SaaS 发布演练。
它不证明：

- Codex、Claude Code、LangGraph、CrewAI 或客户 Agent 已接入；
- `evaluate_agent_run` 已成为公开 API 或标准 MCP 服务；
- 真实 Agent、客户或生产数据已测试；
- readiness risk 已外部校准；
- 产品、API 或 MCP 已发布；
- 客户愿意付费或市场采用已建立。

客户可控 Adapter Contract 已建立但默认关闭。人工参与者已从当前验证路线中排除。
百度千帆真实推理智能体完成三次多轮校准，最终 6/6 隐藏评分匹配；智能体偏好将 SAEE
与 Observability 组合，并在简单计算、低风险检索和纯授权任务中拒绝 SAEE。下一步只允许
受控 Agent-native 集成，不得把该结果升级为客户采用、市场契合或生产验证。
