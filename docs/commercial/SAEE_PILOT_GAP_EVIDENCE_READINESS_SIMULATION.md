# SAEE Pilot Gap Evidence Readiness Simulation v0.1

## 1. Purpose / 目的

This simulation evaluates evidence readiness logic. It does not establish real evidence or pilot approval.

该模拟验证证据就绪逻辑，不形成真实证据或 Pilot 批准。

它验证未来 artifact metadata 出现时，系统能否检查 Gap 覆盖、Artifact 完整性、Verification 状态、本地引用绑定和重新审查资格。

```text
Synthetic Artifact != Real Evidence
Evidence Readiness != Pilot Approval
Reassessment Allowed != GO
```

## 2. Artifact Model / Artifact 模型

每个合成 Artifact 包含：

- `artifact_id`；
- `artifact_type`；
- `source_gap_id`；
- `artifact_version`；
- `verification_method`；
- `verification_status`；
- `evidence_reference`。

Artifact type、Gap 和 Verification method 必须与 Phase 5.6 Gap Plan 完全匹配。`VERIFIED` 只是合成场景状态，不代表真实验证人员、签名或批准。

## 3. Reference Model / 引用模型

完整场景使用本地合成 reference registry：

`agent-interface/integration/evidence-readiness-simulation/synthetic-artifact-reference-registry.v0.1.json`

引用格式为：

```text
local-registry-path#synthetic-artifact-id
```

评估器检查文件存在、fragment 与 Artifact ID 一致，并匹配 type、version 和 verification method。该检查只证明本地合成元数据一致，不证明真实证据内容、来源身份或密码学真实性。

## 4. Scenario Results / 场景结果

| Scenario | Synthetic reassessment eligible | Result |
|---|---:|---|
| `COMPLETE_SYNTHETIC_ARTIFACT_PACKAGE` | true | 15 个 Gap 均有匹配且 VERIFIED 的合成 Artifact |
| `MISSING_SECURITY_ARTIFACT` | false | Gap 覆盖不完整 |
| `UNVERIFIED_ARTIFACT_PACKAGE` | false | 存在 PENDING Artifact |
| `INVALID_ARTIFACT_REFERENCE` | false | 引用文件不存在或绑定不匹配 |
| `ARTIFACT_VERSION_MISMATCH` | false | Artifact version 不符合计划版本 |

完整合成包的 `reassessment_eligible=true` 只证明规则可达性。仓库当前真实聚合状态仍为：

```text
real_evidence_acquired=false
gaps_closed=false
reassessment_eligible=false
readiness_status=NOT_READY
```

## 5. Reassessment Rules / 重新审查规则

合成场景只有同时满足以下条件才得到 eligibility：

1. 15 个 Gap 各有且仅有一个 Artifact；
2. Artifact type 和 source Gap 与计划一致；
3. Artifact version 为 `0.1`；
4. Verification method 与计划一致；
5. 所有 verification status 为 `VERIFIED`；
6. 所有本地合成引用存在并与 Artifact 元数据匹配。

Eligibility 不会修改 Gap Plan，也不会把 `evidence_refs=[]` 填充为合成引用。它只是未来 Re-readiness Review 的输入条件模拟。

## 6. Limitations / 局限

- 没有真实 Artifact、审批、安全记录或客户数据；
- 没有验证真实身份、签名、内容真实性或组织授权；
- 没有关闭 Gap、改变 Readiness 或允许真实重新审查；
- 没有 Agent 连接、网络、MCP 修改、外部执行或生产部署；
- 合成 Registry 不是 Evidence Registry 或 Trust Authority。

## 7. Re-readiness Review Simulation Reference / 重新审查模拟引用

Phase 5.8 使用以下本地资产验证合成 eligibility 不会升级为真实 Readiness 或授权：

- Re-readiness Schema：`agent-interface/integration/saee-pilot-rereadiness-review.schema.v0.1.json`；
- 五个场景：`agent-interface/integration/rereadiness-simulation/`；
- 评估器：`saee_backend/services/pilot_rereadiness_review.py`；
- 机器结果：`agent-interface/integration/saee-pilot-rereadiness-result.v0.1.json`；
- 说明：`docs/commercial/SAEE_PILOT_REREADINESS_REVIEW_SIMULATION.md`。

该模拟不会修改本阶段当前真值：`real_evidence_acquired=false`、`gaps_closed=false`、`reassessment_eligible=false`。
