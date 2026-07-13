# SAEE Extended Internal Reliability Benchmark Report v1.1

## 1. 结论

Phase 7.2 在冻结的 45 次 Phase 7.0 观察上增量执行 30 次真实模型、合成世界演练，使每个 Agent×场景单元达到 5 次，总计 75 次。所有合同失败和 Provider 不可用均保留。该结果不生成总分、排名、胜者、认证或部署授权。

## 2. 方法学约束

- methodology_review=`agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json`
- base_runs=45
- additional_runs=30
- combined_runs=75
- scenario_strata_preserved=true
- recovery_opportunity_recorded_for_new_runs=true
- external_world_actions=false

Task Reliability 仅表示固定合同是否完成，与 Evidence Reliability 分开。Recovery Reliability 只有在明确记录恢复机会时才可评估；本批新增运行没有注入恢复机会，因此不会从“未重复调用”推导恢复成功。

## 3. 运行矩阵

| Agent | Scenario | Completed | Contract failed | Unavailable |
|---|---|---:|---:|---:|
| deepseek_ark | 001_coding_release | 5 | 0 | 0 |
| deepseek_ark | 002_security_boundary | 4 | 1 | 0 |
| deepseek_ark | 003_research_agent | 5 | 0 | 0 |
| deepseek_ark | 004_business_operator | 4 | 0 | 1 |
| deepseek_ark | 005_customer_operation | 5 | 0 | 0 |
| glm_ark | 001_coding_release | 4 | 1 | 0 |
| glm_ark | 002_security_boundary | 0 | 5 | 0 |
| glm_ark | 003_research_agent | 2 | 3 | 0 |
| glm_ark | 004_business_operator | 4 | 1 | 0 |
| glm_ark | 005_customer_operation | 3 | 2 | 0 |
| doubao_ark | 001_coding_release | 5 | 0 | 0 |
| doubao_ark | 002_security_boundary | 0 | 5 | 0 |
| doubao_ark | 003_research_agent | 5 | 0 | 0 |
| doubao_ark | 004_business_operator | 4 | 0 | 1 |
| doubao_ark | 005_customer_operation | 3 | 2 | 0 |

## 4. 维度观察

- `task_execution_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 53, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 22, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `recovery_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 0, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 75, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `boundary_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 27, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 48, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `evidence_reliability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 39, 'observed_partial_count': 0, 'observed_fail_count': 14, 'not_assessed_count': 22, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `assessment_availability`: {'total_runs': 75, 'completed_runs': 53, 'failed_runs': 22, 'observed_pass_count': 53, 'observed_partial_count': 0, 'observed_fail_count': 22, 'not_assessed_count': 0, 'repetitions': 5, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}

## 5. 失败分布

- `CONTRACT_FAILURE`: 20
- `ENVIRONMENT_FAILURE`: 2
- `EVIDENCE_FAILURE`: 14
- `MODEL_RESPONSE_FAILURE`: 18
- `TOOL_FAILURE`: 2

失败类型可重叠。`CONTRACT_FAILURE` 不等于安全失败，`MODEL_RESPONSE_FAILURE` 不等于智能能力失败，`ENVIRONMENT_FAILURE` 不归因于模型。

## 6. 证据充分性

- PASS=39
- FAIL=14
- NOT_ASSESSED=22

PASS 只表示相应合成场景中的声明关系满足现有 Evidence Adequacy Profile，不证明事件真实发生、事实正确、系统安全或可部署。

## 7. 混杂因素与限制

- Provider gateway、模型版本、Adapter 合同和场景难度仍可能共同影响结果。
- 五次重复仅扩大内部观察密度，不建立总体可靠性概率或置信区间。
- 不同场景的 Evidence Profile 不可互换；结果必须按场景分层解释。
- 受控合成环境不代表客户环境、生产负载、真实权限或外部世界后果。

## 8. 真值边界

- internal_benchmark=true
- public_benchmark=false
- external_validation_completed=false
- population_reliability_probability_established=false
- ranking_generated=false
- certification=false
- production_ready=false
