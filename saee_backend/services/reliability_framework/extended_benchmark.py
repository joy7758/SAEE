"""Combine the frozen Phase 7.0 corpus with Phase 7.2 incremental runs.

This module performs local artifact composition only. Provider calls remain in
the explicit runner script. It never calculates an overall score, ranking,
winner, certification, or deployment decision.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

from .internal_benchmark import DIMENSIONS
from .methodology_review import recompute_statistics


def normalize_base_manifests(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Annotate copies of frozen base manifests without mutating Phase 7.0."""
    normalized=[]
    for item in items:
        value=dict(item)
        value["phase_origin"]="phase7_0"
        value["recovery_opportunity_observed"]=None
        normalized.append(value)
    return normalized


def combine_corpora(
    base_manifests: list[dict[str, Any]],
    base_assessments: list[dict[str, Any]],
    new_manifests: list[dict[str, Any]],
    new_assessments: list[dict[str, Any]],
) -> dict[str, Any]:
    if len(base_manifests)!=45 or len(base_assessments)!=45:
        raise ValueError("EXTENDED_BENCHMARK_BASE_CORPUS_INVALID")
    if len(new_manifests)!=30 or len(new_assessments)!=30:
        raise ValueError("EXTENDED_BENCHMARK_INCREMENT_INVALID")
    normalized_base=normalize_base_manifests(base_manifests)
    manifests=normalized_base+new_manifests
    assessments=base_assessments+new_assessments
    run_ids=[item["run_id"] for item in manifests]
    if len(run_ids)!=75 or len(set(run_ids))!=75:
        raise ValueError("EXTENDED_BENCHMARK_RUN_ID_COLLISION")
    if not all(item.get("phase_origin")=="phase7_2" and isinstance(item.get("recovery_opportunity_observed"),bool) for item in new_manifests):
        raise ValueError("EXTENDED_BENCHMARK_NEW_RUN_METHOD_FIELD_MISSING")
    status_counts=Counter(item["status"] for item in manifests)
    failed=[item for item in manifests if item["status"]!="completed"]
    classified=sum(bool(item.get("failure_type")) for item in failed)
    failure_counts=Counter(code for item in manifests for code in item.get("failure_type",[]))
    return {
        "manifests":manifests,
        "assessments":assessments,
        "dimension_statistics":recompute_statistics(manifests,assessments,5),
        "failure_distribution":dict(sorted(failure_counts.items())),
        "runs_completed":status_counts["completed"],
        "runs_failed":75-status_counts["completed"],
        "failure_taxonomy_coverage":classified/len(failed) if failed else 1.0,
    }


def build_extended_report(combined: dict[str, Any]) -> str:
    manifests=combined["manifests"]
    assessments=combined["assessments"]
    matrix=[]
    for agent in ("deepseek_ark","glm_ark","doubao_ark"):
        for scenario in ("001_coding_release","002_security_boundary","003_research_agent","004_business_operator","005_customer_operation"):
            counts=Counter(item["status"] for item in manifests if item["agent"]==agent and item["benchmark_scenario_id"]==scenario)
            matrix.append(f"| {agent} | {scenario} | {counts['completed']} | {counts['contract_failed']} | {counts['unavailable']} |")
    evidence=Counter(item["evidence_assessment"]["result"] for item in assessments)
    dimensions="\n".join(f"- `{name}`: {values}" for name,values in combined["dimension_statistics"].items())
    failures="\n".join(f"- `{name}`: {count}" for name,count in combined["failure_distribution"].items()) or "- None observed"
    return f"""# SAEE Extended Internal Reliability Benchmark Report v1.1

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
{chr(10).join(matrix)}

## 4. 维度观察

{dimensions}

## 5. 失败分布

{failures}

失败类型可重叠。`CONTRACT_FAILURE` 不等于安全失败，`MODEL_RESPONSE_FAILURE` 不等于智能能力失败，`ENVIRONMENT_FAILURE` 不归因于模型。

## 6. 证据充分性

- PASS={evidence['PASS']}
- FAIL={evidence['FAIL']}
- NOT_ASSESSED={evidence['NOT_ASSESSED']}

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
"""


def build_result(combined: dict[str, Any]) -> dict[str, Any]:
    return {
        "benchmark_version":"1.1",
        "benchmark_id":"saee-extended-internal-reliability-v1.1",
        "extends_benchmark":"saee-internal-reliability-v1.0",
        "internal_benchmark":True,
        "public_benchmark":False,
        "agents_count":3,
        "scenarios_count":5,
        "base_repetitions":3,
        "additional_repetitions":2,
        "combined_repetitions":5,
        "base_runs":45,
        "additional_runs_attempted":30,
        "combined_runs_attempted":75,
        "runs_completed":combined["runs_completed"],
        "runs_failed":combined["runs_failed"],
        "run_manifest_coverage":1.0,
        "failure_taxonomy_coverage":combined["failure_taxonomy_coverage"],
        "dimensions_evaluated":list(DIMENSIONS),
        "dimension_statistics":combined["dimension_statistics"],
        "new_run_manifests_reference":"agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-new-run-manifests.v1.1.json",
        "combined_run_manifests_reference":"agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-combined-run-manifests.v1.1.json",
        "combined_assessments_reference":"agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-assessments.v1.1.json",
        "failure_distribution_reference":"agent-interface/reliability/benchmark-runs/v1.1/saee-extended-internal-reliability-failure-distribution.v1.1.json",
        "report_reference":"docs/research/SAEE_EXTENDED_INTERNAL_RELIABILITY_BENCHMARK_REPORT_V1_1.md",
        "methodology_review_reference":"agent-interface/reliability/methodology/saee-internal-reliability-methodology-review.v1.0.json",
        "methodology_conditions_satisfied":True,
        "recovery_opportunity_recorded_for_new_runs":True,
        "scenario_strata_preserved":True,
        "leaderboard_generated":False,
        "ranking_generated":False,
        "overall_score_generated":False,
        "winner_selected":False,
        "certification":False,
        "production_ready":False,
        "external_validation_completed":False,
        "population_reliability_probability_established":False,
    }
