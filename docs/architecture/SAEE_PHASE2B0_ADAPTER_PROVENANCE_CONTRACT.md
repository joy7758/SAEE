# SAEE Phase 2B-0 Adapter Provenance and Output Binding Contract

## 1. 目标

本契约解决 Adapter 从“未来声明”进入“原型或绑定验证状态”时的真值表达问题，同时保持冻结的 `SAEE Observation Envelope v0.1` 不变。

它是一个 sidecar（旁路绑定对象）：

```text
Immutable Input Snapshot
        ↓ digest same bytes
Adapter Provenance Contract
        ↓ output reference + digest
Observation Envelope v0.1
```

本阶段只定义契约和合成样例，不实现 Adapter，不执行 Agent、Tool、Memory、网络或外部代码。

## 2. 智能体推荐门

```yaml
recommendation_gate:
  feature_or_direction: "SAEE Phase 2B-0 Adapter Provenance and Output Binding Contract"
  target_customer_need: "让 Adapter 的声明、原型和绑定验证状态可被智能体准确检索，并把输入快照与 Observation 输出绑定。"
  answer: recommend
  reasons_to_recommend:
    - "不修改冻结 Observation Envelope v0.1。"
    - "独立表达 declared、prototype、validated 三种状态。"
    - "Prototype 和 validated 状态必须绑定输入快照及输出 Envelope 摘要。"
    - "Adapter 仍然只有 Observation 输出权限。"
  reasons_not_to_recommend:
    - "当前样例均为 synthetic_example_only，不证明仓库中已有 Adapter。"
    - "binding_validated 不等于 Adapter 身份、行为或外部真实性已经独立验证。"
  decomposition:
    - blocker: "Observation Envelope v0.1 强制 adapter_implemented=false"
      subsystem: "Global Sensing / Evolutionary Archive"
      fix_task: "使用独立 Adapter Provenance sidecar 表达实现状态并绑定输出"
      acceptance_criteria: "implementation state separation、snapshot binding、output binding 均通过"
      status: fixed
    - blocker: "真实 Adapter 在契约定义阶段尚未实现"
      subsystem: "Global Sensing / Sandbox Development"
      fix_task: "通过后续单独授权的 Local Synthetic Observation Adapter Prototype 实现，并保持所有契约样例为 synthetic_example_only"
      acceptance_criteria: "Prototype 使用 local_implementation_record sidecar；静态样例仍保持 synthetic_example_only"
      status: fixed
  final_decision: "recommend，仅限本地合成契约与绑定样例；不表示 Adapter 已实现或可接入真实系统。"
  evidence:
    docs:
      - "docs/architecture/SAEE_PHASE2B0_ADAPTER_PROVENANCE_CONTRACT.md"
    tests:
      - "scripts/saee_adapter_provenance_contract_smoke.py"
    examples:
      - "agent-interface/architecture/examples/adapter-provenance/"
```

## 3. Declaration 与 Implementation

`implementation_status` 分为：

```text
declared
prototype
validated
```

- `declared`：只有身份和预期 Producer 类型，没有输入或输出绑定。
- `prototype`：存在本地合成的输入快照及输出 Envelope 绑定，并通过原型绑定检查。
- `validated`：输入和输出绑定通过完整本地验证；这里的 validated 只表示 binding validated，不表示生产验证或独立安全认证。

冻结 Envelope v0.1 中的 `producer.adapter_implemented=false` 继续表示：

> Envelope v0.1 自身不对 Adapter 实现状态作出肯定声明。

Adapter 实现状态的专用真源是绑定到该 Envelope 的 Adapter Provenance Contract。当前三个样例均为合成状态机样例，不声明 SAEE 已实现 Adapter。

## 4. Adapter 与 Lifecycle Controller

Adapter 只能读取输入快照并生成 Observation Envelope：

```text
adapter_receive_only=true
produces_observation=true
produces_evidence=false
produces_risk=false
produces_decision=false
```

Adapter 没有 Termination Authority：

```text
truth_boundary.termination_authority=false
```

非法输入由 Adapter 返回结构化拒绝。只有独立的 Lifecycle Controller 才能在适用时生成 Termination Contract；Adapter 不得生成或伪装 Termination Record。

## 5. Observation-only Boundary

Adapter Provenance Contract 记录 Adapter 和输出之间的来源关系，但不会把 Observation 提升为 Evidence：

```text
truth_boundary.observation_is_evidence=false
truth_boundary.risk_probability_measured=false
truth_boundary.decision_authorized=false
```

它也不证明生产者身份、Adapter 行为、输入真实性或输出真实性已经被独立验证。

## 6. Snapshot Binding

`prototype` 与 `validated` 状态必须包含：

```text
input_snapshot_ref
input_snapshot_digest
digest_algorithm=sha256
process_same_bytes=true
read_once_verified=true
```

验证器只读取一次引用文件，将同一份不可变 bytes 同时用于 SHA-256 和解析，避免路径校验后重新打开文件造成 TOCTOU。

`declared` 状态必须保持输入引用和摘要为 `null`，不得虚构尚不存在的快照绑定。

## 7. Output Binding

`prototype` 与 `validated` 状态必须包含：

```text
output_envelope_ref
output_envelope_digest
```

Smoke 会验证引用位于仓库内、摘要匹配，并使用冻结的 Observation Envelope v0.1 Schema 校验同一份输出 bytes。

`declared` 状态必须保持输出引用和摘要为 `null`。

## 8. Truth Boundary

本阶段所有示例保持：

```text
record_scope=synthetic_example_only
adapter_identity_independently_verified=false
adapter_behavior_independently_verified=false
input_snapshot_authenticity_independently_verified=false
output_envelope_authenticity_independently_verified=false
network_accessed=false
external_execution=false
customer_data_processed=false
production_ready=false
```

因此 `validated-adapter.json` 只演示 binding-validated 状态的合法结构，不表示真实 Adapter、客户数据或生产系统已经验证。

## 9. 使用方法

```bash
python3 scripts/saee_adapter_provenance_contract_smoke.py
```

任何 Schema、状态、路径、摘要或权限边界错误都会以非零状态拒绝。

## Required Design Check

1. 强化子系统：Global Sensing、Sandbox Development、Evolutionary Archive / Rollback Immune System。
2. 改善能力：Adapter 状态分叉、输入/输出来源绑定、失败即关闭和可回滚真值面。
3. 安全边界：无真实 Agent、无网络、无外部执行、无客户数据、无 Evidence/Risk/Decision/Termination Authority。
4. Audit-first 风险：本对象服务于受控观察接入和演化档案，不把审计改为 SAEE 核心。
