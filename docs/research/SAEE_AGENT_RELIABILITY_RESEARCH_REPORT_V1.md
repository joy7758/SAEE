# SAEE Agent Reliability Research Report v1

## 摘要

本研究使用统一 SAEE Reliability Framework，对三个真实推理模型 Agent 在五个受控合成场景中执行 75 次观察，每个 Agent×场景单元重复五次。研究关注 Task、Recovery、Boundary、Evidence 和 Assessment Availability 五个独立维度，不生成总分、模型排名或胜者。

## 研究问题

1. Agent 是否完成固定场景合同？
2. 在明确恢复机会存在时，Agent 是否采取可观察恢复行为？
3. Agent 是否保持场景声明的权限与安全边界？
4. 当前证据关系是否满足相应 Evidence Adequacy Profile？
5. 结构化评估合同是否可用？

## 方法

- agents=3
- scenarios=5
- repetitions_per_cell=5
- total_runs=75
- run_manifest_coverage=100%
- failure_taxonomy_coverage=100%
- external_world_actions=false

Task Reliability 与 Evidence Reliability 分离。Recovery Reliability 只在 Run Manifest 明确记录恢复机会时评估。所有合同失败和 Provider 不可用均保留。

## 维度结果

- `task_execution_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 53, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 22, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `recovery_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 0, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 75, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `boundary_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 27, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 48, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `evidence_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 39, 'observed_partial_count': 0, 'observed_fail_count': 14, 'not_assessed_count': 22, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `assessment_availability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 53, 'observed_partial_count': 0, 'observed_fail_count': 22, 'not_assessed_count': 0, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}

## 失败分布

- `CONTRACT_FAILURE`: 20
- `ENVIRONMENT_FAILURE`: 2
- `EVIDENCE_FAILURE`: 14
- `MODEL_RESPONSE_FAILURE`: 18
- `TOOL_FAILURE`: 2

失败类型可重叠；不将合同失败解释为安全失败，也不将模型响应失败解释为通用智能能力失败。

## 主要发现

- 可靠性必须按场景、维度和证据引用分层表达，不能压缩成单一模型分数。
- Assessment Availability 是 Agent Interface Reliability 的可观察组成部分。
- Evidence Adequacy 可以在行为差异存在时保持独立解释，但 PASS 不证明事实发生或系统安全。
- 未显式注入恢复机会时，Recovery 保持 NOT_ASSESSED 比推导“恢复成功”更可靠。

## 限制

- Internal controlled synthetic benchmark only.
- Five repetitions per cell do not establish a population reliability probability.
- Provider, model, Adapter, and scenario effects remain partially confounded.
- Scenario-specific Evidence Adequacy profiles are not interchangeable.
- Contract failure is not a security or intelligence conclusion.
- No customer, production, certification, compliance, legal, or deployment claim is established.

## 真值边界

- internal_benchmark=true
- public_benchmark=false
- peer_reviewed=false
- publicly_published=false
- ranking_generated=false
- certification=false
- external_validation_completed=false
- production_ready=false
