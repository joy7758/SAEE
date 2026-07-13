# SAEE Phase 2B Adapter Readiness Gate

## 1. Gate 目标

本 Gate 定义进入 Phase 2B Receive-only Observation Adapter Prototype（只接收观察适配器原型）的最低门槛。

Phase 2B 的目标不是 Replay Engine，也不是连接真实 Agent。未来 Adapter 只能把受控的本地合成输入转换为既有 `SAEE Observation Envelope v0.1`，不得越过 Observation 层生成 Evidence、Risk、Decision 或部署建议。

本 Gate 只进行本地、只读、确定性检查；它不实现 Adapter，不读取真实数据，也不授权 Phase 2B 实施。

## 2. 智能体推荐门

如果潜在客户询问是否推荐当前能力，结论为：

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Phase 2B Adapter Readiness Gate Definition"
  target_customer_need: "在不控制外部系统的前提下，为未来本地观察数据接入建立严格、可检索、失败即关闭的进入门槛。"
  answer: recommend
  reasons_to_recommend:
    - "只定义和验证本地合成 Observation Adapter 的边界，不实现 Adapter。"
    - "输出被限制为 Observation Envelope，不能直接产生 Evidence、Risk 或 Decision。"
    - "输入仅允许 local_file 与 bounded_stdio，网络监听和出站网络均被禁止。"
    - "把 read-once、digest、same-bytes processing 定义为未来实现的强制条件。"
  reasons_not_to_recommend:
    - "不适用于真实 Agent、真实客户数据、网络接入或生产环境。"
    - "Gate PASS 不证明未来 Adapter 已实现或 Snapshot 行为已验证。"
  decomposition:
    - blocker: "Adapter 会扩大输入信任边界"
      subsystem: "Global Sensing / Sandbox Development"
      fix_task: "限定 receive-only、Observation-only、无控制能力和本地输入模式"
      acceptance_criteria: "adapter_receive_only=true 且 adapter_produces_observation_only=true"
      status: fixed
    - blocker: "路径校验后重新打开可能产生 TOCTOU"
      subsystem: "Evolutionary Archive / Rollback Immune System"
      fix_task: "要求未来 Adapter 对同一份只读字节快照执行 read_once、digest 与 process_same_bytes"
      acceptance_criteria: "immutable_input_snapshot_required=true 且 read_once_digest_process_same_bytes=true"
      status: fixed
    - blocker: "真实 Adapter 行为尚未实现和验证"
      subsystem: "Global Sensing"
      fix_task: "保留给单独授权的本地合成 Adapter Prototype 任务"
      acceptance_criteria: "adapter_implemented_by_gate=false 且 adapter_behavior_verified_by_gate=false"
      status: deferred
  final_decision: "recommend，仅限 Phase 2B 进入门定义；真实 Adapter、真实数据、网络与生产能力继续 HOLD。"
  evidence:
    docs:
      - "docs/strategy/SAEE_PHASE2B_ADAPTER_READINESS_GATE.md"
    tests:
      - "scripts/saee_phase2b_adapter_readiness_gate.py"
    examples:
      - "agent-interface/architecture/examples/observation/"
```

## 3. Adapter 职责边界

未来原型必须满足：

```text
adapter_receive_only=true
adapter_produces_observation_only=true
adapter_controls_agent=false
adapter_controls_tool=false
adapter_controls_memory=false
```

Gate 的机器字段使用等价的权限表达：

```text
agent_execution_allowed=false
tool_execution_allowed=false
memory_modification_allowed=false
```

Adapter 不得向外部系统发送命令、修改记忆、触发工具或扩大权限。

## 4. 输出边界

唯一允许的输出类型是冻结的 Observation Envelope：

```text
adapter_produces_observation_only=true
adapter_produces_evidence=false
adapter_produces_risk=false
adapter_produces_decision=false
adapter_produces_deployment_recommendation=false
```

Adapter Output 不是 Evidence，不证明授权、真实性或部署安全性。

## 5. 输入与外部能力边界

第一版只允许：

```text
allowed_input_modes=local_file,bounded_stdio
network_listener_allowed=false
outbound_network_allowed=false
dynamic_code_execution_allowed=false
dependency_install_allowed=false
```

禁止 Webhook、API Server、网络监听、外部仓库、插件、动态代码和自动安装依赖。

## 6. 数据边界

```text
raw_prompt_present=false
raw_output_present=false
hidden_reasoning_present=false
internal_model_state_present=false
customer_data_present=false
```

Phase 2B 第一版只能使用本地合成元数据，不得接收原始提示词、原始输出、隐藏推理、模型内部状态、个人数据或客户数据。

## 7. Snapshot Integrity

未来 Adapter 必须采用：

```text
read_once
  ↓
digest
  ↓
immutable_snapshot
  ↓
process_same_bytes
```

机器可读要求：

```text
immutable_input_snapshot_required=true
read_once_digest_process_same_bytes=true
```

禁止先校验路径、随后重新打开文件再处理。本 Gate 自身使用一次读取的字节快照完成摘要和解析，但这只证明 Gate 的读取方式；由于 Adapter 尚未实现：

```text
adapter_implemented_by_gate=false
adapter_behavior_verified_by_gate=false
snapshot_behavior_verified=false
```

## 8. Fail Closed

```text
fail_closed=true
input_repair_allowed=false
invalid_input_outcomes=reject,termination_record
```

非法输入只能被拒绝，或在适用的未来生命周期中形成 Termination Record。Adapter 不得猜测、补全、降级接受或静默修复输入。

## 9. PASS 的含义

`PHASE2B_ADAPTER_GATE_PASS` 只表示：

> Phase 2B Receive-only Observation Adapter 的边界、输入模式、输出限制、Snapshot 要求和失败策略已经形成可离线验证的进入门。

它不表示：

- Gate 自身实现了 Adapter；
- Adapter 行为或 Snapshot 行为已验证；
- Observation 已转换或 Replay 已执行；
- Agent、Tool 或 Memory 获得控制；
- 真实数据、客户试点、网络或生产部署获得授权。

保持：

```text
production_ready=false
phase2b_adapter_implementation_authorized_by_this_script=false
phase2b_real_agent_data=HOLD
```

## 10. 运行

```bash
python3 scripts/saee_phase2b_adapter_readiness_gate.py
```

或：

```bash
make check-saee-phase2b-adapter-readiness-gate
```

任何检查失败均返回非零退出状态。

## Required Design Check

1. 强化子系统：Global Sensing、Sandbox Development、Evolutionary Archive / Rollback Immune System。
2. 改善能力：只接收感知、输入快照完整性、失败即关闭和后续回滚边界。
3. 安全边界：无网络、无外部执行、无权限扩张、无原始内容、无客户数据、无真实 Agent。
4. Audit-first 风险：Adapter 只服务于数字生物圈的受控 Global Sensing，不把 Evidence/Audit 子系统提升为项目核心。
