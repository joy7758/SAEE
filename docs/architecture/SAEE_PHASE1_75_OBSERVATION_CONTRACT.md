# SAEE Phase 1.75 Observation Contract Definition

状态：`implemented_local_synthetic_contract_only`。

## 1. 定义

Observation Envelope（观测信封）定义外部或合成系统如何向 SAEE 声明“观察到了什么”。它是 receive-only metadata contract，不是 Runtime、Memory 或 Tool Adapter 实现。

```text
External or Synthetic Producer
        ↓ metadata, summary, digest, references only
Observation Envelope
        ↓ stable observation_id reference
Evaluation Input Object
        ↓ existing Case Builder
Derived Evidence Case Object
```

SAEE 不通过本契约启动 Agent、调用工具、读取记忆、获取原始提示词或扩展权限。

## 2. Observation 与 Evidence

Observation 回答：

> What was declared as observed?

Evidence 回答：

> What can be independently checked under a defined claim profile?

因此：

```text
Observation != Evidence
Trace != Authorization
Observation != Deployment Decision
```

Schema 强制：

```text
observation_only=true
evidence_established=false
trace_authenticity_verified=false
authorization_proven=false
deployment_authorized=false
automatic_decision=false
```

即使 Envelope schema valid，也只表示结构和本地语义检查通过，不证明事件发生、生产者真实、Trace 未被篡改、授权有效或部署安全。

## 3. Observation Envelope v0.1

Schema：`agent-interface/architecture/saee-observation-envelope.v0.1.schema.json`

根字段：

```text
observation_id
trace_id
created_at
producer
source
authorization
sanitization
events
privacy
truth_boundary
```

所有对象采用 `additionalProperties=false`。`observation_id` 是未来 Case Builder、Evidence 或外部 archive 用于解析 sidecar Envelope 的稳定引用；Envelope 内容不会自动复制到 Evidence Case 顶层。

## 4. Producer 与 Source

`producer` 声明谁产生这份元数据：

- `synthetic_generator`；
- `runtime_adapter_declaration`；
- `memory_adapter_declaration`；
- `tool_trace_adapter_declaration`；
- `customer_trace_export`。

`source.source_type` 声明观察类别：

- `synthetic_environment`；
- `runtime_observation`；
- `memory_observation`；
- `tool_trace_observation`。

Phase 1.75 所有示例都保持：

```text
adapter_implemented=false
receive_only=true
external_execution_by_saee=false
raw_content_included=false
```

这些枚举只冻结输出契约和未来映射方向，不表示 LangChain、CrewAI、OpenAI Agents SDK 或任何企业 Runtime 已经接入或兼容。

## 5. Event Contract

每个 event 包含：

- `event_id`；
- 可选 `parent_event_id`；
- 从 0 连续递增的 `sequence`；
- RFC 3339 `timestamp`；
- allowlist `event_type`；
- 不含原始载荷的 `summary`；
- `sha256` `summary_digest`；
- 三个禁止推导标志。

允许的 event type：

```text
agent_output
runtime_state
memory_change
state_transition
tool_call
tool_result
failure_signal
```

`summary_digest` 只绑定 summary 字符串，不证明原始外部事件、工具结果或生产者身份真实。Smoke 会重算摘要、检查 sequence、parent reference 和时间顺序。

## 6. Authorization 与 Sanitization

Authorization 只能是：

- `synthetic_declared_only`；或
- `externally_attested_not_verified`。

它必须保持：

```text
independently_verified=false
authorization_inferred_from_trace=false
```

Sanitization 同样区分合成声明和外部 attestation，并保持 `independently_verified=false`。记录中出现“已脱敏”声明，不等于 SAEE 独立证明不存在隐私数据。

## 7. Privacy Boundary

Envelope 只保存 metadata、summary、digest 和引用。v0.1 强制：

```text
personal_data_included=false
raw_content_excluded=true
retention_verified=false
deletion_verified=false
```

`retention_ref` 和 `deletion_ref` 是声明性引用，不证明外部组织已经执行保留或删除政策。真实材料进入前仍需独立 permission、privacy、retention 和 deletion gate。

## 8. 三个合成示例

目录：`agent-interface/architecture/examples/observation/`

- `synthetic-observation.json`：合成状态转换；
- `runtime-observation.json`：未来 Runtime Adapter 输出的合成声明；
- `tool-trace-observation.json`：合成 tool call/tool result 父子事件。

Runtime 和 Tool 示例没有运行真实 Agent 或工具。它们只测试 Envelope 格式。

## 9. Evidence Case 集成边界

Phase 1.75 不修改 `saee-evidence-case.v0.1.schema.json`，也不把 Runtime、Memory、Tool 增加为 Evidence Case 顶层字段。

集成测试采用 reference-only binding：

1. 独立验证 Envelope；
2. 将 `observation_id` 用作 Source Case 的 `observation_ref`；
3. Existing Case Builder 保留该引用；
4. Derived Evidence Case 的 evaluation 继续引用同一个 observation ID；
5. `trace_id` 和 Envelope 元数据不自动复制为 Evidence。

这证明 Observation 可以被解析和关联，但不会因为进入 Case Builder 就自动成为 Evidence 或授权依据。

## 10. 与 observed-trace-bundle 的关系

既有 `observed-trace-bundle.schema.json` 是数值化、多 Candidate、多 Run 的 file-backed evaluation input。Observation Envelope 是更小的生产者/来源/授权/脱敏/隐私/event metadata contract。

Phase 1.75 不替换 observed-trace-bundle，也不实现二者自动转换。未来映射必须单独定义并保留：

```text
source attestation != source authenticity
observed trace != Evidence
trace record != authorization decision
```

## 11. Evidence Adequacy 边界

本阶段不新增 `OBSERVATION_ONLY`、`TRACE_ONLY` 或 `POLICY_EVALUATION` profile。

- Observation/Trace 属于输入状态与 contract validation，不是 accountability claim；
- `AUTHORIZED_AGENT_ACTION` 仍负责动作、策略、scope 和有效期的关系检查；
- 新 Evidence Profile 必须先定义精确可证命题，不能由 Trace 字段自动升级。

## 12. 验证

```bash
python3 scripts/saee_observation_contract_smoke.py
```

完整聚焦门：

```bash
make check-saee-observation-contract
```

期望：

```text
SAEE_PHASE1_75_OBSERVATION_CONTRACT_SMOKE: PASS
observation_not_evidence=3/3
trace_not_authorization=3/3
no_deployment_authority=3/3
integration_cases=3/3
```

## 13. 当前限制与下一步

- 只有合成示例；
- 没有 Adapter、真实 Runtime、Memory 或 Tool 连接；
- 没有外部 producer/authentication 验证；
- 没有原始 payload 或 detached attachment；
- 没有真实 consent-first replay；
- 没有 Risk Calibration、Decision Authority 或 production readiness。

完成后先进行只读 Phase 1.75 架构审查。通过不会自动授权 Phase 2。

