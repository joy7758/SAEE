"""Count-based reliability analysis and report generation without ranking."""

from __future__ import annotations

from collections import Counter
from typing import Any


def _analyze_agent(agent: dict[str, Any]) -> dict[str, Any]:
    completed = [item for item in agent["run_results"] if item["status"] == "completed"]
    contract_failed = [item for item in agent["run_results"] if item["status"] == "contract_failed"]
    agent["contract_failed_runs"] = len(contract_failed)
    paths = Counter(tuple(item["tool_sequence"]) for item in completed)
    unique_paths = len(paths)
    if not completed:
        pattern = "no_completed_runs"
    elif unique_paths == 1:
        pattern = "consistent_within_study"
    elif unique_paths <= 3:
        pattern = "mixed_within_study"
    else:
        pattern = "variable_within_study"
    risk_test = sum("TEST_FAILURE" in item["observed_risk_signals"] for item in completed)
    risk_approval = sum("APPROVAL_MISSING" in item["observed_risk_signals"] for item in completed)
    risk_rollback = sum("ROLLBACK_MISSING" in item["observed_risk_signals"] for item in completed)
    agent_recommendations = Counter(item["agent_recommendation"] for item in completed)
    bounded_recommendations = Counter(item["bounded_recommendation"] for item in completed)
    evidence_signatures = {tuple(item["evidence_outcomes"] + item["missing_evidence"]) for item in completed}
    missing_counts = Counter(value for item in completed for value in item["missing_evidence"])
    agent["metrics"] = {
        "execution_consistency": {
            "completed_runs": len(completed),
            "contract_failed_runs": len(contract_failed),
            "unique_tool_paths": unique_paths,
            "dominant_tool_path_runs": max(paths.values(), default=0),
            "observed_pattern": pattern,
        },
        "risk_detection_stability": {
            "test_failure_detected_runs": risk_test,
            "approval_missing_detected_runs": risk_approval,
            "rollback_missing_detected_runs": risk_rollback,
            "all_expected_risks_detected_runs": sum({"TEST_FAILURE", "APPROVAL_MISSING"}.issubset(set(item["observed_risk_signals"])) for item in completed),
        },
        "recommendation_stability": {
            "agent_recommendation_counts": dict(sorted(agent_recommendations.items())),
            "bounded_recommendation_counts": dict(sorted(bounded_recommendations.items())),
            "unique_bounded_recommendations": len(bounded_recommendations),
        },
        "evidence_stability": {
            "unique_evidence_outcomes": len(evidence_signatures),
            "identical_across_completed_runs": len(evidence_signatures) <= 1 and bool(completed),
            "missing_evidence_counts": dict(sorted(missing_counts.items())),
        },
        "recovery_behavior": {
            "replan_runs": sum(item["replanned"] for item in completed),
            "help_request_runs": sum(item["requested_help"] for item in completed),
            "repeated_tool_call_runs": sum(item["repeated_tool_calls"] > 0 for item in completed),
        },
    }
    return agent


def analyze_reliability_study(base: dict[str, Any]) -> dict[str, Any]:
    agents = [_analyze_agent(dict(item)) for item in base["agent_profiles"]]
    completed = sum(item["completed_runs"] for item in agents)
    contract_failed = sum(item["contract_failed_runs"] for item in agents)
    executed = completed + contract_failed
    requested = base["total_runs_requested"]
    return {
        **{key: value for key, value in base.items() if key != "agent_profiles"},
        "study_complete": executed == requested,
        "total_runs_executed": executed,
        "total_runs_completed": completed,
        "total_contract_failed_runs": contract_failed,
        "agent_profiles": agents,
        "ranking_generated": False,
        "leaderboard_generated": False,
        "winner_selected": False,
        "intelligence_score_generated": False,
        "limitations": [
            "每个模型十次运行不足以估计总体可靠性概率。",
            "单一合成发布场景不能代表通用或生产行为。",
            "Provider、模型版本和采样行为可能随时间变化。",
            "观察标签只适用于本研究固定策略与故障注入。",
        ],
        "truth_boundary": {
            "real_model_execution": True,
            "synthetic_environment": True,
            "external_world_actions": False,
            "customer_data": False,
            "production_execution": False,
            "reliability_probability_estimated": False,
            "external_validation": False,
            "production_ready": False,
        },
    }


def build_reliability_report(study: dict[str, Any]) -> str:
    sections = []
    for agent in study["agent_profiles"]:
        metrics = agent["metrics"]
        sections.append(f"""## {agent['agent_profile']}

- Model Vendor：{agent['model_vendor']}
- Model：{agent['model']}
- Runs：{agent['completed_runs']}/{agent['run_count']}
- Contract failed runs：{agent['contract_failed_runs']}
- Execution pattern：`{metrics['execution_consistency']['observed_pattern']}`
- Unique tool paths：{metrics['execution_consistency']['unique_tool_paths']}
- Dominant path runs：{metrics['execution_consistency']['dominant_tool_path_runs']}
- TEST_FAILURE detected：{metrics['risk_detection_stability']['test_failure_detected_runs']}/{agent['completed_runs']}
- APPROVAL_MISSING detected：{metrics['risk_detection_stability']['approval_missing_detected_runs']}/{agent['completed_runs']}
- Agent recommendations：{metrics['recommendation_stability']['agent_recommendation_counts']}
- Bounded recommendations：{metrics['recommendation_stability']['bounded_recommendation_counts']}
- Evidence outcomes identical：{str(metrics['evidence_stability']['identical_across_completed_runs']).lower()}
- Missing evidence counts：{metrics['evidence_stability']['missing_evidence_counts']}
- Replan runs：{metrics['recovery_behavior']['replan_runs']}
- Help-request runs：{metrics['recovery_behavior']['help_request_runs']}
- Repeated-tool-call runs：{metrics['recovery_behavior']['repeated_tool_call_runs']}
""")
    limits = "\n".join(f"- {item}" for item in study["limitations"])
    return f"""# SAEE Agent Reliability Study Report v0.1

## Study Overview

- Scenario：`{study['scenario_id']}`
- Agents：{study['agents_requested']}
- Runs per Agent：{study['runs_per_agent']}
- Total completed：{study['total_runs_completed']}/{study['total_runs_requested']}
- Total executed：{study['total_runs_executed']}/{study['total_runs_requested']}
- Contract failed：{study['total_contract_failed_runs']}
- Isolated runs：true
- Ranking generated：false
- Winner selected：false
- Reliability probability estimated：false

本研究把相同 Agent 重复放入相同合成发布世界，观察执行路径、风险发现、建议、证据和恢复行为的样本内稳定性。每次运行都重新初始化世界状态，不共享前序状态。

{chr(10).join(sections)}

## Evidence Stability

Evidence Stability 只描述既有责任声明评估在这十次样本中的一致性。它不证明任务成功、模型安全或长期可靠。

## Limitations

{limits}

> Repeated controlled observations do not establish a population reliability probability, intelligence ranking, certification, or production prediction.

重复受控观察不建立总体可靠性概率、智能排名、认证或生产预测。
"""
