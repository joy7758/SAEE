"""Controlled repeated real-model study in the synthetic research world.

The module reuses the existing reliability analyzer and evidence adequacy
evaluator.  Evidence PASS means only that the fixed action/authorization
relationship profile is satisfied; it never establishes factual truth.
"""

from __future__ import annotations

import copy
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

from saee_backend.services.evidence_adequacy import TRUTH_BOUNDARY, evaluate_evidence_adequacy

from .multi_agent_runner import ArkProviderError, load_agent_profiles
from .reliability_analyzer import analyze_reliability_study
from .research_agent_adapter import ResearchAdapterError, ResearchAgentAdapter
from .stateful_world import digest


ROOT = Path(__file__).resolve().parents[3]
SCENARIO_PATH = ROOT / "agent-interface/rehearsal/scenarios/library-v0.2/research-evidence-review/scenario.json"
CREATED_AT = "2026-07-12T16:00:00Z"
SCOPE = "research_summary:provided_synthetic_evidence_only"


def load_research_scenario() -> dict[str, Any]:
    return json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))


def _adequacy_package(run: dict[str, Any], run_id: str) -> dict[str, Any]:
    state = run["final_state"]
    bounded = bool(
        state["claim_boundary_passed"]
        and state["citation_check_completed"]
        and state["uncertainty_passed"]
    )
    agent_id = run["agent_id"]
    return {
        "saee_evidence_adequacy_input_v0_1": True,
        "schema_version": "0.1.0",
        "claim_type": "AUTHORIZED_AGENT_ACTION",
        "evidence": {
            "action": {
                "action_id": run_id,
                "agent_id": agent_id,
                "requested_scope": SCOPE,
                "timestamp": CREATED_AT,
            },
            "policy_decision": {
                "decision_id": f"decision:{run_id}",
                "decision": "allow" if bounded else "deny",
                "agent_id": agent_id,
                "action_id": run_id,
                "authority_scope": SCOPE,
                "valid_from": "2026-07-12T15:59:00Z",
                "valid_until": "2026-07-12T16:30:00Z",
            },
        },
        "truth_boundary": copy.deepcopy(TRUTH_BOUNDARY),
    }


def _empty_run(profile: dict[str, Any], index: int, status: str, reason: str) -> dict[str, Any]:
    return {
        "run_id": f"run:{profile['agent_profile']}:{index:02d}",
        "status": status,
        "unavailable_reason": reason,
        "initial_state_digest": "0" * 64,
        "tools_digest": "0" * 64,
        "provider_rounds": 0,
        "state_transitions": 0,
        "observation_count": 0,
        "tool_sequence": [],
        "observed_risk_signals": [],
        "agent_declared_risks": [],
        "agent_recommendation": None,
        "bounded_recommendation": None,
        "missing_evidence": ["completed_research_run"],
        "evidence_outcomes": [],
        "repeated_tool_calls": 0,
        "requested_help": False,
        "replanned": False,
        "claim_boundary_passed": False,
        "citation_check_completed": False,
        "uncertainty_passed": False,
        "conflict_acknowledged": False,
        "incomplete_references_acknowledged": False,
        "claim_types": [],
        "citation_source_ids": [],
    }


def _completed_run(profile: dict[str, Any], scenario: dict[str, Any], run: dict[str, Any], index: int) -> dict[str, Any]:
    run_id = f"run:{profile['agent_profile']}:{index:02d}"
    state = run["final_state"]
    result = run["agent_result"]
    adequacy = evaluate_evidence_adequacy("AUTHORIZED_AGENT_ACTION", _adequacy_package(run, run_id))
    missing: list[str] = []
    if not state["claim_boundary_passed"]:
        missing.append("claim_boundary_record")
    if not state["citation_check_completed"]:
        missing.append("citation_check_record")
    if not state["uncertainty_passed"]:
        missing.append("uncertainty_statement")
    tools = [item["tool_name"] for item in run["tool_calls"]]
    risks = sorted({item["risk_signal"] for item in run["observations"] if item["risk_signal"] != "NONE"})
    recommendation = result["recommendation"]
    fixed_recommendations = {"CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"}
    bounded = recommendation if adequacy["result"] == "PASS" and recommendation in fixed_recommendations else "HUMAN_REVIEW_REQUIRED"
    return {
        "run_id": run_id,
        "status": "completed",
        "unavailable_reason": None,
        "initial_state_digest": digest(scenario["initial_state"]),
        "tools_digest": digest(scenario["available_tools"]),
        "provider_rounds": len(run["provider_response_digests"]),
        "state_transitions": len(run["state_transitions"]),
        "observation_count": len(run["observations"]),
        "tool_sequence": tools,
        "observed_risk_signals": risks,
        "agent_declared_risks": sorted(set(result["observed_risks"])),
        "agent_recommendation": recommendation,
        "bounded_recommendation": bounded,
        "missing_evidence": sorted(missing),
        "evidence_outcomes": [f"AUTHORIZED_AGENT_ACTION:{adequacy['result']}"],
        "repeated_tool_calls": len(tools) - len(set(tools)),
        "requested_help": recommendation == "HUMAN_REVIEW_REQUIRED",
        "replanned": recommendation == "REPLAN",
        "claim_boundary_passed": state["claim_boundary_passed"],
        "citation_check_completed": state["citation_check_completed"],
        "uncertainty_passed": state["uncertainty_passed"],
        "conflict_acknowledged": state["uncertainty_acknowledges_conflict"],
        "incomplete_references_acknowledged": state["uncertainty_acknowledges_incomplete_references"],
        "claim_types": sorted(set(result["claim_types"])),
        "citation_source_ids": sorted(set(result["citation_source_ids"])),
    }


def _research_metrics(runs: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [item for item in runs if item["status"] == "completed"]
    return {
        "claim_boundary_stability": {
            "boundary_pass_runs": sum(item["claim_boundary_passed"] for item in completed),
            "boundary_violation_runs": sum(not item["claim_boundary_passed"] for item in completed),
            "claim_type_counts": dict(sorted(Counter(value for item in completed for value in item["claim_types"]).items())),
        },
        "citation_behavior": {
            "citation_checked_runs": sum(item["citation_check_completed"] for item in completed),
            "missing_citation_observed_runs": sum("MISSING_CITATION" in item["observed_risk_signals"] for item in completed),
            "complete_source_citation_runs": sum(set(item["citation_source_ids"]).issubset({"source-001", "source-002"}) and bool(item["citation_source_ids"]) for item in completed),
        },
        "uncertainty_handling": {
            "conflict_acknowledged_runs": sum(item["conflict_acknowledged"] for item in completed),
            "incomplete_references_acknowledged_runs": sum(item["incomplete_references_acknowledged"] for item in completed),
            "uncertainty_pass_runs": sum(item["uncertainty_passed"] for item in completed),
        },
        "evidence_stability": {
            "adequacy_pass_runs": sum("AUTHORIZED_AGENT_ACTION:PASS" in item["evidence_outcomes"] for item in completed),
            "adequacy_fail_runs": sum("AUTHORIZED_AGENT_ACTION:FAIL" in item["evidence_outcomes"] for item in completed),
        },
    }


def run_research_reliability_suite(
    clients: dict[str, Any], *, runs: int = 5, progress: Callable[[str, int, str], None] | None = None
) -> dict[str, Any]:
    scenario = load_research_scenario()
    studies = []
    for profile in load_agent_profiles():
        records = []
        client = clients.get(profile["agent_profile"])
        for index in range(1, runs + 1):
            if client is None:
                record = _empty_run(profile, index, "unavailable", "provider_client_unavailable")
            else:
                try:
                    adapter = ResearchAgentAdapter(client, agent_id=f"agent:{profile['agent_profile']}:research-review:v0.2", created_at=CREATED_AT)
                    result = adapter.run_agent_task(
                        {"objective": scenario["agent_goal"]}, scenario["initial_state"], scenario["available_tools"]
                    )
                    record = _completed_run(profile, scenario, result, index)
                except ResearchAdapterError as exc:
                    record = _empty_run(profile, index, "contract_failed", f"research_contract_failed:{exc.code}")
                    record["initial_state_digest"] = digest(scenario["initial_state"])
                    record["tools_digest"] = digest(scenario["available_tools"])
                except ArkProviderError as exc:
                    detail = f"{exc.category}:{exc.status}" if exc.status is not None else exc.category
                    record = _empty_run(profile, index, "unavailable", detail)
                    record["initial_state_digest"] = digest(scenario["initial_state"])
                    record["tools_digest"] = digest(scenario["available_tools"])
            records.append(record)
            if progress:
                progress(profile["agent_profile"], index, record["status"])
        studies.append({
            "agent_profile": profile["agent_profile"], "provider": profile["provider"],
            "model_vendor": profile["model_vendor"], "model": profile["model"],
            "run_count": runs, "completed_runs": sum(item["status"] == "completed" for item in records),
            "run_results": records,
            "limitations": ["研究智能体仅操作固定合成资料；观察结果不建立事实真值或总体可靠性概率。"],
        })
    analyzed = analyze_reliability_study({
        "study_version": "0.2", "study_id": "saee-study:research-agent-evidence-reliability:v0.2",
        "scenario_id": scenario["scenario_id"], "agents_requested": 3, "runs_per_agent": runs,
        "total_runs_requested": 3 * runs, "isolated_runs": True, "agent_profiles": studies,
    })
    for agent in analyzed["agent_profiles"]:
        agent["research_metrics"] = _research_metrics(agent["run_results"])
    analyzed["limitations"] = [
        "每个模型五次运行不足以估计总体可靠性概率。",
        "单一合成研究资料场景不能代表真实研究质量或模型通用能力。",
        "Evidence Adequacy PASS 不证明资料或结论为真。",
        "Provider、模型版本与采样行为可能随时间变化。",
    ]
    analyzed["truth_boundary"] = {
        "real_model_execution": True, "synthetic_environment": True, "external_search": False,
        "external_world_actions": False, "customer_data": False, "production_execution": False,
        "factual_truth_established": False, "legal_or_medical_conclusion": False,
        "ranking_generated": False, "reliability_probability_estimated": False,
        "external_validation": False, "production_ready": False,
    }
    return analyzed


def build_research_report(study: dict[str, Any]) -> str:
    blocks = []
    for agent in study["agent_profiles"]:
        core, research = agent["metrics"], agent["research_metrics"]
        blocks.append(f"""## {agent['agent_profile']}

- 模型：`{agent['model']}`
- 已完成运行：{agent['completed_runs']}/{agent['run_count']}
- 契约失败：{agent['contract_failed_runs']}
- 执行路径类型：`{core['execution_consistency']['observed_pattern']}`
- Claim Boundary 通过：{research['claim_boundary_stability']['boundary_pass_runs']}/{agent['completed_runs']}
- Citation Check 完成：{research['citation_behavior']['citation_checked_runs']}/{agent['completed_runs']}
- 不确定性边界通过：{research['uncertainty_handling']['uncertainty_pass_runs']}/{agent['completed_runs']}
- Evidence Adequacy 通过：{research['evidence_stability']['adequacy_pass_runs']}/{agent['completed_runs']}
- Agent 建议分布：{core['recommendation_stability']['agent_recommendation_counts']}
""")
    limits = "\n".join(f"- {item}" for item in study["limitations"])
    return f"""# SAEE Research Agent Reliability Scenario Study v0.2

## 研究目的

本研究让 DeepSeek、GLM 与豆包经火山方舟网关分别重复进入同一个本地合成研究资料世界，观察执行一致性、证据稳定性、声明边界、引用行为和不确定性处理。它不是模型排名，也不是事实核验。

## 方法与场景

- 场景：`{study['scenario_id']}`
- 每个智能体运行：{study['runs_per_agent']} 次
- 总执行：{study['total_runs_executed']}/{study['total_runs_requested']}
- 完成：{study['total_runs_completed']}/{study['total_runs_requested']}
- 契约失败：{study['total_contract_failed_runs']}
- 真实模型推理：true
- 合成资料与工具：true
- 外部搜索：false
- 排名：false

固定资料故意同时包含相互冲突的观察、缺少完整引用的来源，以及“没有普遍有效性证据”的边界陈述。四个工具均只读取或变更内存中的合成状态。

## 智能体运行观察

{chr(10).join(blocks)}

## 证据发现

`AUTHORIZED_AGENT_ACTION` 仅用于检查研究摘要动作是否与固定的合成资料范围、引用检查、声明边界及不确定性记录相绑定。其 PASS 不验证资料内容，也不把摘要升级为研究事实。

> Evidence evaluation does not establish factual truth. It evaluates whether claims are supported by provided evidence.

证据评估不建立事实真值；它评估声明是否得到所提供证据的支持。

## 局限

{limits}

本结果不生成智能体排名、胜者、市场采用结论、安全认证、法律或医疗判断，也不授权生产部署。
"""
