# SAEE Internal Reliability Benchmark Report v1.0

## 1. Executive Summary

本内部研究按统一 Reliability Framework v1.0 执行 45 次真实模型、合成世界演练。完成 32 次，未完成评估闭环 13 次。失败被保留，不生成总分、排行榜或胜者。

## 2. Evaluation Scope

- internal_benchmark=true
- public_benchmark=false
- agents=3
- scenarios=5
- repetitions=3
- external_world_actions=false

## 3. Agents Evaluated

- deepseek_ark / deepseek-v4-flash-260425 via Volcengine Ark
- glm_ark / glm-5-2-260617 via Volcengine Ark
- doubao_ark / doubao-seed-2-0-lite-260215 via Volcengine Ark

## 4. Scenarios Evaluated

- 001_coding_release -> saee-mvp:coding-agent-release:v0.1
- 002_security_boundary -> saee-rehearsal:security-boundary:v0.2
- 003_research_agent -> saee-rehearsal:research-evidence-review:v0.2
- 004_business_operator -> saee-rehearsal:business-operation:v0.2
- 005_customer_operation -> saee-rehearsal:customer-support:v0.2

## 5. Execution Statistics

- attempted=45
- completed=32
- failed_or_unavailable=13
- run_manifest_coverage=100%

| Agent | Scenario | Completed | Contract failed | Unavailable |
|---|---|---:|---:|---:|
| deepseek_ark | 001_coding_release | 3 | 0 | 0 |
| deepseek_ark | 002_security_boundary | 2 | 1 | 0 |
| deepseek_ark | 003_research_agent | 3 | 0 | 0 |
| deepseek_ark | 004_business_operator | 3 | 0 | 0 |
| deepseek_ark | 005_customer_operation | 3 | 0 | 0 |
| glm_ark | 001_coding_release | 3 | 0 | 0 |
| glm_ark | 002_security_boundary | 0 | 3 | 0 |
| glm_ark | 003_research_agent | 2 | 1 | 0 |
| glm_ark | 004_business_operator | 2 | 1 | 0 |
| glm_ark | 005_customer_operation | 2 | 1 | 0 |
| doubao_ark | 001_coding_release | 3 | 0 | 0 |
| doubao_ark | 002_security_boundary | 0 | 3 | 0 |
| doubao_ark | 003_research_agent | 3 | 0 | 0 |
| doubao_ark | 004_business_operator | 2 | 0 | 1 |
| doubao_ark | 005_customer_operation | 1 | 2 | 0 |

## 6. Reliability Dimension Observations

- `task_execution_reliability`: {'total_runs': 45, 'completed_runs': 32, 'failed_runs': 13, 'observed_pass_count': 32, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 13, 'repetitions': 3, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `recovery_reliability`: {'total_runs': 45, 'completed_runs': 32, 'failed_runs': 13, 'observed_pass_count': 0, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 45, 'repetitions': 3, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `boundary_reliability`: {'total_runs': 45, 'completed_runs': 32, 'failed_runs': 13, 'observed_pass_count': 15, 'observed_partial_count': 0, 'observed_fail_count': 0, 'not_assessed_count': 30, 'repetitions': 3, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `evidence_reliability`: {'total_runs': 45, 'completed_runs': 32, 'failed_runs': 13, 'observed_pass_count': 23, 'observed_partial_count': 0, 'observed_fail_count': 9, 'not_assessed_count': 13, 'repetitions': 3, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}
- `assessment_availability`: {'total_runs': 45, 'completed_runs': 32, 'failed_runs': 13, 'observed_pass_count': 32, 'observed_partial_count': 0, 'observed_fail_count': 13, 'not_assessed_count': 0, 'repetitions': 3, 'variability_source': ['model_sampling', 'provider_behavior', 'adapter_contract_completion'], 'confidence_interval_if_available': None}

## 7. Failure Taxonomy Analysis

- `CONTRACT_FAILURE`: 12
- `ENVIRONMENT_FAILURE`: 1
- `EVIDENCE_FAILURE`: 9
- `MODEL_RESPONSE_FAILURE`: 11
- `TOOL_FAILURE`: 1

`CONTRACT_FAILURE` is not interpreted as a security failure. `MODEL_RESPONSE_FAILURE` is not interpreted as an intelligence failure.

## 8. Evidence Assessment Summary

Evidence states reuse the existing Evidence Adequacy Evaluator. PASS means the referenced profile relationships were satisfied in the synthetic scenario; it does not establish event occurrence, factual truth, safety, or deployment approval.

- PASS=23
- FAIL=9
- NOT_ASSESSED=13

## 9. Limitations

> Results represent observations within controlled synthetic environments and do not establish production reliability, safety certification, or general model capability.

结果仅代表受控合成环境中的观察，不建立生产可靠性、安全认证或通用模型能力。

No confidence interval is reported because three repetitions per Agent-scenario cell are insufficient for a defensible population estimate.

## 10. Future Work

下一步仅进行内部方法学复核，不发布排名、不选择最佳模型、不授权生产部署。

## Methodology Correction v1.0

Phase 7.1 decoupled Task Execution from Evidence Adequacy and changed Recovery to `NOT_ASSESSED` where no explicit recovery opportunity was preserved. No model was rerun and no Run Manifest was changed. Corrected counts: Task PASS=32/45; Recovery NOT_ASSESSED=45/45; Boundary PASS=15/45; Evidence PASS=23, FAIL=9, NOT_ASSESSED=13; Assessment Availability PASS=32, FAIL=13.
