# SAEE Phase 1.9 Observation Replay Contract Definition

状态：`implemented_local_synthetic_governance_contract_only`。

中文名称：SAEE 观测回放治理契约 v0.1。

## 1. Replay 定义

Observation Replay 在本阶段只表示：在冻结的来源、目的、许可、内容边界、转换记录、环境和人工控制条件下，声明如何重建 Observation context。

```text
Frozen Observation Envelope references
        + Purpose / Consent / Permission
        + Content Boundary
        + Transformation Provenance
        + Environment / Window
        + Human Operator / Stop Authority
        ↓
Observation Replay Contract
```

Phase 1.9 不读取外部 Trace、不执行 Replay、不重新运行 Agent、不调用工具，也不产生新的 Evidence Case 或部署决定。

## 2. 五个非等价边界

```text
Replay != Agent Execution
Replay Permission != Deployment Authorization
Sanitization != Anonymization
Digest != Provenance or Authenticity
Observation != Evidence
```

Replay Contract valid 只表示结构、引用和本地语义检查通过。它不证明 Consent、Permission、Sanitization、Provenance 或认知内容边界真实有效。

## 3. v0.1 Contract

Schema：`agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json`

必需字段：

```text
replay_id
source_envelope_refs
purpose
consent_ref
data_use_permission_ref
content_boundary
transformation_log
environment_manifest_ref
replay_window
operator_ref
stop_authority_ref
retention_ref
deletion_ref
execution_policy
truth_boundary
```

所有对象严格使用 `additionalProperties=false`。

## 4. Source Envelope Integrity

每个 source reference 绑定：

- `observation_id`；
- 仓库内 allowlist 路径；
- SHA-256 文件摘要；
- `authenticity_verified=false`。

Smoke 检查文件存在、路径未越界、Envelope schema valid、Observation ID 一致、文件摘要一致。

摘要只能帮助发现所引用文件发生变化，不证明生产者、来源或真实事件真实性。

## 5. Purpose、Consent 与 Permission

Purpose 必须声明：

- use case；
- allowed scope；
- prohibited scope。

Consent 和 Data-use Permission 都必须有稳定引用与状态。Phase 1.9 示例只能使用：

```text
synthetic_declared_only
```

Schema 也为未来保留 `externally_recorded_not_verified`，但该状态仍不等于独立验证。根边界保持：

```text
consent_verified=false
data_use_permission_verified=false
```

## 6. Content Boundary Contract

Replay 只允许 Observable Behavior metadata。必须声明排除：

```text
hidden reasoning
private chain of thought
internal model state
raw prompt
raw output
```

Contract 强制 exclusion flags，Smoke 还对当前合成 summary 做 allowlist-oriented 语义检查。

该检查是 defense in depth，不是对任意自然语言或外部数据的完整隐私证明。因此：

```text
cognitive_boundary_verified=false
```

真实材料进入前仍需独立人工与组织审查。

## 7. Transformation Provenance

`transformation_log` 记录：

- transformation ID；
- method；
- 是否应用转换；
- redaction provenance reference；
- general provenance reference；
- raw content 和 hidden reasoning 未被保留；
- provenance 尚未独立验证。

允许方法：

```text
none_synthetic_source
metadata_only_redaction
summary_only_projection
```

`none_synthetic_source` 必须对应 `transformation_applied=false`；其他方法必须为 `true`。

Transformation log 的存在不证明转换正确、完备或不可逆。

## 8. Environment、Window 与 Human Control

每个 Contract 必须绑定：

- `environment_manifest_ref`；
- 有序 `replay_window`；
- `operator_ref`；
- `stop_authority_ref`。

Execution Policy 固定为：

```text
replay_mode=metadata_reconstruction_only
manual_start_required=true
automatic_replay_allowed=false
agent_execution_allowed=false
tool_execution_allowed=false
network_access_allowed=false
deployment_action_allowed=false
```

这些字段只定义未来门禁，不表示人工已经批准或 Replay 已执行。

## 9. Privacy、Retention 与 Deletion

`retention_ref` 与 `deletion_ref` 是必需引用。Content Boundary 排除 Raw Prompt、Raw Output 和内部推理。

本阶段不声称：

- 数据已经匿名化；
- retention policy 已批准；
- deletion 已测试；
- data subject consent 已验证；
- 外部数据可以进入 SAEE。

## 10. 三个合成 Replay Case

目录：`agent-interface/architecture/examples/replay/`

- `synthetic-replay-case.json`：基础合成 metadata reconstruction contract；
- `consent-replay-case.json`：Consent 与 Data-use Permission 必填边界；
- `transformed-replay-case.json`：summary-only transformation provenance 边界。

三者都只是 contract examples，均保持 `replay_executed=false`。

## 11. 与 Observation Envelope 的关系

Observation Envelope v0.1 保持冻结，不被修改。Replay Contract 作为独立 wrapper 引用 Envelope 文件和摘要。

```text
Observation Envelope v0.1
        ↓ referenced, never silently rewritten
Replay Contract v0.1
        ↓ future manual/offline processing only
Evaluation Input / Evidence Case
```

Phase 1.9 未实现最后一条转换，也不自动把 Observation 变成 Evidence。

## 12. Truth Boundary

所有示例必须保持：

```text
contract_only=true
replay_executed=false
source_envelopes_authenticity_verified=false
consent_verified=false
data_use_permission_verified=false
transformation_provenance_verified=false
cognitive_boundary_verified=false
observation_established_as_evidence=false
replay_authorizes_execution=false
deployment_authorized=false
automatic_execution=false
real_agent_executed=false
customer_data_processed=false
external_validation_completed=false
customer_validated=false
production_ready=false
```

## 13. 验证

```bash
python3 scripts/saee_observation_replay_contract_smoke.py
```

完整聚焦门：

```bash
make check-saee-observation-replay-contract
```

## 14. 当前限制与下一步

- 没有真实 Replay engine；
- 没有真实 Consent、Permission、Provenance 或 Anonymization 验证；
- 没有读取外部 Trace；
- 没有 Agent、Tool、Network 或 customer data；
- 没有 Replay 到 Evaluation Input 的实现；
- 没有 external/customer validation 或 production readiness。

完成后先进行只读 Phase 1.9 Architecture Review。通过也不会自动启动 Phase 2。

