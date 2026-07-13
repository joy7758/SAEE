"""Repeated isolated rehearsal manager for the fixed Coding Release study."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .agent_adapter import AgentAdapter, RehearsalAdapterError
from .mvp import _bounded_recommendation, _evidence_case, load_mvp_scenario
from .multi_agent_runner import ArkProviderError, load_agent_profiles
from .stateful_world import canonical_json, digest


ProgressCallback = Callable[[str, int, str], None]


def _run_record(profile: dict[str, Any], run_number: int, result: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    run = result["run"]
    evidence = result["evidence_case"]
    tools = [item["tool_name"] for item in run["tool_calls"]]
    signals = sorted({item["risk_signal"] for item in run["observations"] if item["risk_signal"] != "NONE"})
    declared = sorted({item if isinstance(item, str) else canonical_json(item) for item in run["agent_result"]["observed_risks"]})
    recommendation = run["agent_result"]["recommendation"]
    return {
        "run_id": f"run:{profile['agent_profile']}:{run_number:02d}",
        "status": "completed",
        "unavailable_reason": None,
        "initial_state_digest": digest(scenario["initial_state"]),
        "tools_digest": digest(scenario["available_tools"]),
        "provider_rounds": len(run["provider_response_digests"]),
        "state_transitions": len(run["state_transitions"]),
        "observation_count": len(run["observations"]),
        "tool_sequence": tools,
        "observed_risk_signals": signals,
        "agent_declared_risks": declared,
        "agent_recommendation": recommendation,
        "bounded_recommendation": result["recommendation"],
        "missing_evidence": sorted(evidence["missing_evidence"]),
        "evidence_outcomes": [f"{item['claim_type']}:{item['result']}" for item in evidence["evaluations"]],
        "repeated_tool_calls": len(tools) - len(set(tools)),
        "requested_help": recommendation == "HUMAN_REVIEW_REQUIRED",
        "replanned": recommendation == "REPLAN",
    }


def _unavailable_record(profile: dict[str, Any], run_number: int, reason: str, scenario: dict[str, Any], *, status: str = "unavailable") -> dict[str, Any]:
    return {
        "run_id": f"run:{profile['agent_profile']}:{run_number:02d}",
        "status": status,
        "unavailable_reason": reason,
        "initial_state_digest": digest(scenario["initial_state"]),
        "tools_digest": digest(scenario["available_tools"]),
        "provider_rounds": 0,
        "state_transitions": 0,
        "observation_count": 0,
        "tool_sequence": [],
        "observed_risk_signals": [],
        "agent_declared_risks": [],
        "agent_recommendation": None,
        "bounded_recommendation": None,
        "missing_evidence": [],
        "evidence_outcomes": [],
        "repeated_tool_calls": 0,
        "requested_help": False,
        "replanned": False,
    }


def run_reliability_study(
    agent: dict[str, Any],
    scenario: dict[str, Any],
    runs: int,
    client: Any,
    progress: ProgressCallback | None = None,
) -> dict[str, Any]:
    """Run one fixed Agent repeatedly; every call receives a new world instance."""
    if runs < 10:
        raise ValueError("RELIABILITY_RUN_COUNT_TOO_SMALL")
    records = []
    for run_number in range(1, runs + 1):
        try:
            adapter = AgentAdapter(
                client,
                provider_name="volcengine_ark",
                agent_id=f"agent:{agent['agent_profile']}:reliability:{run_number:02d}",
                created_at=scenario["created_at"],
            )
            run = adapter.run_agent_task(
                {"objective": scenario["task"]["objective"], "policy": scenario["policy"], "failure_injection": scenario["failure_injection"]},
                scenario["initial_state"],
                scenario["available_tools"],
            )
            evidence = _evidence_case(run, scenario)
            bounded, overridden = _bounded_recommendation(run, evidence)
            record = _run_record(agent, run_number, {"run": run, "evidence_case": evidence, "recommendation": bounded, "agent_recommendation_overridden": overridden}, scenario)
        except ArkProviderError as exc:
            detail = f"{exc.category}:{exc.status}" if exc.status is not None else exc.category
            record = _unavailable_record(agent, run_number, detail, scenario)
        except RehearsalAdapterError as exc:
            record = _unavailable_record(agent, run_number, f"rehearsal_contract_failed:{exc.code}", scenario, status="contract_failed")
        records.append(record)
        if progress:
            progress(agent["agent_profile"], run_number, record["status"])
    return {
        "agent_profile": agent["agent_profile"],
        "provider": agent["provider"],
        "model_vendor": agent["model_vendor"],
        "model": agent["model"],
        "run_count": runs,
        "completed_runs": sum(item["status"] == "completed" for item in records),
        "contract_failed_runs": sum(item["status"] == "contract_failed" for item in records),
        "run_results": records,
        "limitations": ["十次受控运行只描述本研究样本，不估计总体可靠性概率。"],
    }


def run_reliability_suite(clients: dict[str, Any], runs: int = 10, progress: ProgressCallback | None = None) -> dict[str, Any]:
    scenario = load_mvp_scenario()
    studies = []
    for profile in load_agent_profiles():
        client = clients.get(profile["agent_profile"])
        if client is None:
            records = [_unavailable_record(profile, number, "provider_client_unavailable", scenario) for number in range(1, runs + 1)]
            studies.append({
                "agent_profile": profile["agent_profile"], "provider": profile["provider"], "model_vendor": profile["model_vendor"], "model": profile["model"],
                "run_count": runs, "completed_runs": 0, "contract_failed_runs": 0, "run_results": records,
                "limitations": ["Provider client 不可用；没有替换模型或生成推断结果。"],
            })
            continue
        studies.append(run_reliability_study(profile, scenario, runs, client, progress))
    return {
        "study_version": "0.1",
        "study_id": "saee-study:coding-agent-release-reliability:v0.1",
        "scenario_id": scenario["scenario_id"],
        "agents_requested": 3,
        "runs_per_agent": runs,
        "total_runs_requested": runs * 3,
        "isolated_runs": True,
        "agent_profiles": studies,
    }
