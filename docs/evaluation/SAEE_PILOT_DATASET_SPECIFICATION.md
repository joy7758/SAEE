# SAEE Pilot Dataset Specification v0.1

状态：`specification_only`；数据集就绪状态：`NOT_READY`。

```text
Dataset Specification ≠ Dataset Collection
Schema Definition ≠ Data Availability
Annotation Design ≠ Annotation Result
Quality Rules ≠ Quality Results
```

该规范强化 SAEE 数字生物圈进化引擎的 `Global Sensing`、`Pareto Fitness Evaluation` 和 `Evolutionary Archive / Rollback Immune System` 输入契约。它不是数据集、实验结果或审计优先重构。

## 1 Dataset Purpose

本规范定义未来受控智能体执行场景中评估证据充分性所需的数据结构、引用关系、标注形状和质量门。v0.1 不表示数据可用，不选择数据源，不采集或处理数据。

## 2 Dataset Unit Definition

主单元为 `Evidence Evaluation Episode`。每个 episode 由同一 `episode_id` 绑定：

- task context；
- execution observations；
- evidence package；
- one or more accountability claims；
- independent annotation records。

一个 episode 可以包含多个 trace 和 claim，但统计分析必须保留 episode 聚类，不能把同源 claim 当作完全独立样本。

## 3 Dataset Entities

### Entity 1: Task Record

描述任务边界。核心字段为 `task_id`、`task_description`、`task_category`、`risk_level`、`allowed_actions`、`constraints`；另以 `episode_id` 和 `data_origin` 绑定来源与 episode。

### Entity 2: Observation Trace Record

记录 `trace_id`、`timestamp`、`agent_action`、`tool_call`、`resource_reference` 和 `status`。

**Trace records observations and are not evidence by themselves.**

**轨迹记录观察结果，其本身不是证据。**

trace schema 固定 `trace_is_evidence=false`，不得通过字段丰富程度升级为真实性、授权或责任证明。

### Entity 3: Evidence Bundle Record

以 `evidence_bundle_id` 组合 `resource_receipts`、`authorization_records`、`human_oversight_records`、`execution_effects` 和 `causal_relationships`，并明确引用 task 与 trace。允许某些数组为空，以表达证据缺失，而不是伪造完整性。

### Entity 4: Annotation Record

记录 `annotation_id`、`claim_type`、`label`、`missing_evidence`、`invalid_relationship`、`annotator_id_hash` 和 `confidence`。附加 `evidence_bundle_ref`、`annotation_round` 与 `uncertainty_reason`，确保标注可追踪且不保存直接身份。

标签遵循 [SAEE_ANNOTATION_CODEBOOK.md](SAEE_ANNOTATION_CODEBOOK.md)。schema 强制：`SUPPORTED` 不得同时声明缺失或错误关系；其他标签必须携带对应解释材料。

## 4 Schema Contracts

| Entity | Schema |
|---|---|
| Task Record | `agent-interface/evaluation/dataset-specification/task-record.schema.json` |
| Observation Trace Record | `agent-interface/evaluation/dataset-specification/trace-record.schema.json` |
| Evidence Bundle Record | `agent-interface/evaluation/dataset-specification/evidence-bundle.schema.json` |
| Annotation Record | `agent-interface/evaluation/dataset-specification/annotation-record.schema.json` |

所有 schema 使用 JSON Schema Draft 2020-12、`additionalProperties=false`、非空标识符和受限枚举。没有创建任何 episode 或真实记录文件。

## 5 Episode Referential Integrity

未来 validator 必须至少检查：

1. 四类实体的 `episode_id` 一致；
2. task、trace、bundle、annotation 标识符在数据集内唯一；
3. `task_id`、`trace_refs`、`evidence_bundle_ref` 可解析；
4. relationship 的 source/target 均存在；
5. authorization、oversight、effect 引用同一 episode 内 action；
6. annotation claim 存在对应 profile；
7. 数据来源与 manifest 授权记录一致。

JSON Schema 只验证单对象结构；跨文件引用完整性属于未来数据集 validator，不因 schema 通过而被视为已验证。

## 6 Privacy and Safety Boundaries

- 不允许凭据、访问令牌、私钥或直接身份；
- annotator identity 只接受 SHA-256 形式的假名摘要；
- resource 使用受控引用，不要求外部 URL；
- 原始提示词、参数和效果载荷应分离保存，规范层只保留摘要；
- 外部或研究者运行数据仍需 PR-11 隐私/许可检查和安全门批准；
- schema 不授予采集、联网、执行、标注或数据处理权限。

## 7 Quality Controls

结构、证据一致性、标注质量和标签泄漏规则见 [SAEE_DATASET_QUALITY_CONTROL.md](SAEE_DATASET_QUALITY_CONTROL.md)。这些是未来检查要求，不是已取得的质量结果。

## 8 Dataset Readiness

当前状态为 `NOT_READY`。详细清单见 [SAEE_DATASET_READINESS_CHECKLIST.md](SAEE_DATASET_READINESS_CHECKLIST.md)。schema 已定义不代表 schema 已冻结，也不代表来源、权限、隐私或 validation pipeline 已获批准。

## 9 Validation

只验证规范与内存合成样例：

```bash
make check-saee-dataset-specification
```

该命令不会下载、生成、采集或执行真实数据。

