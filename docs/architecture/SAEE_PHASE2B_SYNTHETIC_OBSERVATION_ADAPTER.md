# SAEE Phase 2B Local Synthetic Observation Adapter Prototype

## 1. 定位

本 Prototype 是 SAEE 第一个本地合成、receive-only（只接收）的 Observation Adapter。它只强化 Global Sensing（全球感知）的受控输入面，不是 Agent Platform、Replay Engine、Evidence Generator 或 Lifecycle Controller。

```text
Synthetic External Observation
        ↓ read once + expected digest
Immutable Input Snapshot
        ↓ process the same bytes
Local Synthetic Observation Adapter
        ↓
Observation Envelope v0.1
        +
Adapter Provenance Contract v0.1
```

不接入 LangChain、CrewAI、OpenAI Agent SDK、MCP、真实 Agent、网络或客户数据。

## 2. 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Phase 2B Local Synthetic Observation Adapter Prototype"
  target_customer_need: "把本地合成的可观察行为摘要转换为严格 Observation Envelope，并提供可验证的输入/输出来源绑定。"
  answer: recommend
  reasons_to_recommend:
    - "只读取仓库内本地合成输入，不接真实 Agent 或网络。"
    - "对预期摘要、同一份 bytes 处理、Observation 输出和 Provenance sidecar 做确定性验证。"
    - "Content Boundary、Snapshot mismatch 和权限越界均 fail closed。"
  reasons_not_to_recommend:
    - "不适用于真实 Runtime、真实客户数据或生产环境。"
    - "Adapter 身份和行为未经过独立外部验证。"
  decomposition:
    - blocker: "冻结 Envelope v0.1 不表达实现状态"
      subsystem: "Global Sensing / Evolutionary Archive"
      fix_task: "使用 Phase 2B-0 Adapter Provenance sidecar 作为实现状态真源"
      acceptance_criteria: "adapter_provenance_binding=true"
      status: fixed
    - blocker: "输入可能在摘要校验与处理之间变化"
      subsystem: "Sandbox Development / Rollback Immune System"
      fix_task: "read once、digest、process same bytes，并测试 mismatch fail closed"
      acceptance_criteria: "snapshot_integrity=true 且 snapshot_mismatch_rejected=true"
      status: fixed
    - blocker: "真实生态和客户数据尚未授权"
      subsystem: "Global Sensing"
      fix_task: "保持所有非合成 Adapter 与真实数据工作为 HOLD"
      acceptance_criteria: "real_agent_executed=false、network_accessed=false、customer_data_processed=false"
      status: deferred
  final_decision: "recommend，仅限仓库内本地合成 Prototype；不推荐解释为真实 Adapter 或生产能力。"
  evidence:
    docs:
      - "docs/architecture/SAEE_PHASE2B_SYNTHETIC_OBSERVATION_ADAPTER.md"
    tests:
      - "scripts/saee_synthetic_observation_adapter_smoke.py"
    examples:
      - "agent-interface/architecture/examples/adapter-provenance/synthetic-adapter-input.json"
```

## 3. Receive-only 原则

Adapter 只能读取显式提供的仓库内本地合成 JSON 文件：

```text
adapter_receive_only=true
agent_execution_allowed=false
external_tool_executed=false
memory_modification_allowed=false
network_accessed=false
```

它不向 Runtime、Agent、Tool 或 Memory 发送任何命令，也不扩大权限。

## 4. 输入契约与 Content Boundary

输入 Schema：

```text
agent-interface/architecture/saee-synthetic-external-observation.v0.1.schema.json
```

只允许 observable behavior summary（可观察行为摘要）。以下字段无论出现在对象哪一层都会被 fail closed 拒绝：

```text
raw_prompt
raw_output
hidden_reasoning
private_chain_of_thought
internal_model_state
customer_data
```

输入 `content_boundary` 还必须显式声明这些内容不存在。

## 5. Snapshot 策略

Adapter 的 `run_adapter_file` 采用：

```text
resolve bounded local path
        ↓
read_snapshot_once
        ↓
calculate SHA-256 over snapshot.payload
        ↓
compare expected digest
        ↓
parse and transform snapshot.payload
```

路径不会在校验摘要后重新打开进行处理。传入文件与预期摘要不一致时返回：

```text
adapter_result=reject
reason_code=ADAPTER_SNAPSHOT_DIGEST_MISMATCH
```

且不写 Observation 或 Provenance 输出。

## 6. Observation-only 输出

唯一业务输出是符合冻结 Schema 的 Observation Envelope v0.1：

```text
truth_boundary.observation_only=true
truth_boundary.evidence_established=false
truth_boundary.automatic_decision=false
truth_boundary.deployment_authorized=false
```

Adapter Result 的以下槽位始终为 `null`：

```text
evidence
risk
decision
termination_contract
```

Adapter 不生成 Termination Contract。下游 Lifecycle Controller 是否生成 Termination Record 不属于 Adapter 权限。

## 7. Provenance 绑定

成功转换同时生成一个 `implementation_status=prototype` 的 Adapter Provenance sidecar：

```text
adapter_id=adapter:saee-local-synthetic-observation-v0.1
adapter_version=0.1.0-prototype
process_same_bytes=true
read_once_verified=true
validation_status=prototype_binding_validated
```

Sidecar 绑定：

- 输入快照相对路径及 SHA-256；
- 输出 Envelope 相对路径及 SHA-256；
- receive-only 和 Observation-only 权限；
- 无 Evidence、Risk、Decision、Network、External Execution 和 Termination Authority。

Envelope v0.1 中冻结的 `producer.adapter_implemented=false` 表示 Envelope 本身不证明实现状态。Prototype 的实现状态真源是绑定 sidecar；两者用途不同，不修改冻结 Schema。

## 8. 失败路径

所有 Adapter 拒绝结果都保持：

```text
adapter_result=reject
observation_envelope=null
adapter_provenance=null
evidence=null
risk=null
decision=null
termination_contract=null
```

覆盖：

- JSON 或 Schema 非法；
- Raw Prompt、Raw Output、Hidden Reasoning、Private Chain of Thought、Internal Model State、Customer Data；
- Snapshot digest mismatch；
- 输入或输出路径越过仓库边界；
- 输出或 Provenance Schema 失败。

Adapter 不猜测、不修复、不降级接受。

## 9. 当前真值边界

```text
adapter_implemented=true
implementation_scope=local_synthetic_prototype_only
adapter_behavior_independently_verified=false
real_agent_executed=false
external_tool_executed=false
network_accessed=false
customer_data_processed=false
automatic_decision=false
deployment_authorized=false
production_ready=false
```

这里的 `adapter_implemented=true` 只表示仓库内存在通过本地 smoke 的合成 Prototype，不表示真实生态 Adapter、客户验证、外部验证或生产能力。

## 10. 验证

```bash
python3 scripts/saee_phase2b_adapter_readiness_gate.py
python3 scripts/saee_adapter_provenance_contract_smoke.py
python3 scripts/saee_synthetic_observation_adapter_smoke.py
python3 scripts/mainline_guard.py
```

## Required Design Check

1. 强化子系统：Global Sensing、Sandbox Development、Evolutionary Archive / Rollback Immune System。
2. 改善能力：合成感知接入、状态分叉、输入/输出摘要绑定和失败即关闭。
3. 安全边界：无真实 Agent、无网络、无外部工具、无动态代码、无依赖安装、无客户数据。
4. Audit-first 风险：Provenance 只作为感知输入的来源 sidecar，不把 Evidence/Audit 提升为 SAEE 核心。
