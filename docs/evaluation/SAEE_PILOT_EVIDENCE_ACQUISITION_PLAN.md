# SAEE Pilot Evidence Acquisition Planning v0.1

当前 readiness：`NO_GO`；artifact 状态：`MISSING 12/12`。

```text
Evidence Acquisition Plan ≠ Evidence Acquisition
Evidence Template ≠ Evidence Record
Required Artifact ≠ Existing Artifact
Future Approval ≠ Current Approval
```

本计划服务于 SAEE 数字生物圈进化引擎的 `Global Sensing`、`Sandbox Development`、`Pareto Fitness Evaluation` 和档案/回滚免疫系统。它只定义未来证据对象，不生成真实性或批准。

## 1 Purpose

本文定义未来 Pilot Readiness Reassessment 所需的 evidence artifact 类型、角色所有权和验证规则。它不创建、收集、验证或批准这些 artifact，也不选择数据源或联系任何外部主体。

## 2 Evidence Acquisition Principle

每个 readiness gap 必须由一个显式、可引用的 evidence artifact 支撑。声明某项 gap 已关闭，至少需要：

- artifact identifier；
- known source；
- timestamp；
- verification method；
- evidence reference。

artifact type 名称只是未来契约。没有实际 reference 时，状态必须为 `MISSING`。

## 3 Evidence Artifact Mapping

| Readiness Gap | Required Future Evidence Artifact | Purpose | Verification Rule | Current Status |
|---|---|---|---|---|
| Dataset Source | Dataset Source Declaration | 界定来源、所有者与用途范围 | source identity、ownership、scope 可验证 | MISSING |
| Data Ownership | Ownership Statement | 记录 owner/controller/processor 关系 | ownership relationship 有来源和引用 | MISSING |
| Data Permissions | Usage Authorization Record | 定义采集、转换、标注、使用与撤销范围 | permission scope、issuer、duration 明确 | MISSING |
| Privacy Review | Privacy Assessment Record | 记录数据清单、敏感性、最小化和审查结果 | 由负责流程完成并接受 | MISSING |
| Retention Policy | Retention and Deletion Policy Record | 定义数据生命周期和到期动作 | 所有数据类别均有批准规则 | MISSING |
| Deletion Process | Deletion Procedure Test Record | 记录删除与撤回测试 | 覆盖主存储、备份和派生产物 | MISSING |
| Access Control | Access Control Record | 定义最小权限、复核和撤销 | 授权路径及拒绝/撤销测试可引用 | MISSING |
| Schema Freeze | Schema Version Freeze Record | 固定版本、hash、迁移和变更权限 | exact version 与 change policy 固定 | MISSING |
| Approved Sample | Approved Sample Manifest | 绑定非主评估 sample 的来源、权限和分割 | 通过 source、permission、leakage 检查 | MISSING |
| Annotation Approval | Annotation Protocol Approval Record | 固定 codebook、说明、裁决和 agreement | 版本冻结并由负责流程接受 | MISSING |
| Pilot Environment | Pilot Environment Manifest | 固定隔离环境、依赖、资产和复现步骤 | environment digest 与复现测试可检查 | MISSING |
| Safety Approval | Execution Safety Approval Record | 绑定 sandbox、network denial、stop、rollback 和执行批准 | 控制测试通过且批准范围明确 | MISSING |

当前 `artifact_identifier`、`artifact_source`、`artifact_timestamp`、`verification_method`、`evidence_reference` 全部为 `null`。

## 4 Ownership Model

每类 artifact 只分配角色，不指派真人：

- `creator_role`：准备候选 artifact；
- `reviewer_role`：检查内容、范围和缺口；
- `approver_role`：通过负责流程决定是否接受；
- `verifier_role`：独立核对 identifier、source、timestamp、method 和 reference。

角色名称不证明角色已有人承担，也不产生审批。creator 不能仅凭创建动作把状态升级为已批准。

## 5 Evidence Verification Rules

artifact 只有在以下条件同时满足时，才可能支持 gap closure：

1. identifier 非空且在相应命名空间唯一；
2. source 已知并能说明来源权威性；
3. timestamp 存在且适用于被审查版本；
4. verification method 明确且结果可复核；
5. evidence reference 记录在 gap plan 与 readiness matrix 可访问范围；
6. required artifact 被负责流程接受，而不是由 validator 自动批准。

`PRESENT_UNVERIFIED` 不等于 verified；`VERIFIED` 不自动等于 approved；`CLOSED` 必须保留完整引用并在新的 readiness review 中重新计算。

## 6 Reassessment Flow

```text
OPEN GAP
    ↓
Artifact Created by future responsible process
    ↓
Artifact Verified
    ↓
Evidence Reference Added
    ↓
Gap plan permits re-review
    ↓
Readiness Review re-run
    ↓
New GO / CONDITIONAL_GO / NO_GO decision
```

本计划当前停在第一步之前。`gaps_addressed=0`，不能进入 readiness re-review。

本地验证：

```bash
python3 scripts/saee_agent_cli.py review-evidence-acquisition-plan \
  --input agent-interface/evaluation/saee-pilot-evidence-acquisition-plan.v0.1.json
```

