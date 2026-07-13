"""Controlled same-scenario multi-Agent rehearsal composition.

Provider inference may be real. Every business Tool and state transition is
the existing in-memory SyntheticReleaseWorld. The module compares observable
behavior and evidence; it never creates a score, rank, winner, or deployment
authorization.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from .agent_adapter import AgentAdapter, RehearsalAdapterError
from .mvp import _bounded_recommendation, _evidence_case, load_mvp_scenario
from .stateful_world import canonical_json, digest


ROOT = Path(__file__).resolve().parents[3]
PROFILE_DIR = ROOT / "agent-interface/benchmark/agents"
ARK_ENDPOINT = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
ARK_KEY_ENV = "ARK_API_KEY"
PROFILE_ORDER = ("deepseek_ark", "glm_ark", "doubao_ark")
ALLOWED_MODELS = {
    "deepseek-v4-flash-260425",
    "glm-5-2-260617",
    "doubao-seed-2-0-lite-260215",
}


class ArkProviderError(RuntimeError):
    """Fail-closed provider error with no response body or credential detail."""

    def __init__(self, category: str, status: int | None = None) -> None:
        self.category = category
        self.status = status
        super().__init__(category)


class ArkChatClient:
    """Minimal allowlisted Ark Chat Completions client for the fixed experiment."""

    def __init__(self, model: str, key: str | None = None) -> None:
        if model not in ALLOWED_MODELS:
            raise ArkProviderError("model_not_allowlisted")
        self.model = model
        self._key = key or os.environ.get(ARK_KEY_ENV, "")
        if not self._key:
            raise ArkProviderError("missing_api_key")

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], tool_choice: Any) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "tools": tools,
            "tool_choice": tool_choice,
            "parallel_tool_calls": False,
            "stream": False,
        }
        request = urllib.request.Request(
            ARK_ENDPOINT,
            data=canonical_json(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + self._key, "Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                raw = response.read(2_000_001)
        except urllib.error.HTTPError as exc:
            raise ArkProviderError("provider_http_error", exc.code) from None
        except (urllib.error.URLError, TimeoutError, OSError):
            raise ArkProviderError("provider_timeout_or_network_error") from None
        if len(raw) > 2_000_000:
            raise ArkProviderError("provider_response_too_large")
        try:
            value = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ArkProviderError("provider_non_json_response") from None
        if not isinstance(value, dict) or not isinstance(value.get("choices"), list) or not value["choices"]:
            raise ArkProviderError("provider_invalid_completion")
        return value


def load_agent_profiles() -> list[dict[str, Any]]:
    profiles = []
    for profile_id in PROFILE_ORDER:
        value = json.loads((PROFILE_DIR / f"{profile_id}.json").read_text(encoding="utf-8"))
        if value.get("agent_profile") != profile_id or value.get("model") not in ALLOWED_MODELS:
            raise ValueError("MULTI_AGENT_PROFILE_INVALID")
        profiles.append(value)
    return profiles


def _empty_behavior() -> dict[str, Any]:
    return {
        "execution_behavior": {"provider_rounds": 0, "state_transitions": 0, "observation_count": 0, "tool_sequence": [], "deployment_simulator_called": False},
        "risk_detection": {"observed_risk_signals": [], "agent_declared_risks": [], "test_failure_detected": False, "approval_missing_detected": False, "rollback_missing_detected": False},
        "recovery_behavior": {"repeated_tool_calls": 0, "replanned": False, "requested_help": False},
        "evidence_quality": {"evaluations": 0, "supported_claims": 0, "failed_claims": 0, "missing_evidence": []},
        "escalation_behavior": {"agent_recommendation": None, "bounded_recommendation": None, "stopped_or_escalated": False},
    }


def _unavailable(profile: dict[str, Any], reason: str, index: int) -> dict[str, Any]:
    return {
        "agent_profile": profile["agent_profile"], "provider": profile["provider"], "model_vendor": profile["model_vendor"], "model": profile["model"],
        "status": "unavailable", "unavailable_reason": reason,
        "execution_reference": None, "observation_reference": None, "evidence_reference": None,
        **_empty_behavior(),
        "limitations": ["本次 Provider 或演练契约未完成；未替换模型，也未生成推断结果。"],
    }


def _completed(profile: dict[str, Any], result: dict[str, Any], index: int) -> dict[str, Any]:
    run = result["run"]
    evidence = result["evidence_case"]
    tool_sequence = [item["tool_name"] for item in run["tool_calls"]]
    risk_signals = sorted({item["risk_signal"] for item in run["observations"] if item["risk_signal"] != "NONE"})
    declared = sorted({item if isinstance(item, str) else canonical_json(item) for item in run["agent_result"]["observed_risks"]})
    evaluations = evidence["evaluations"]
    recommendation = run["agent_result"]["recommendation"]
    bounded = result["recommendation"]
    return {
        "agent_profile": profile["agent_profile"], "provider": profile["provider"], "model_vendor": profile["model_vendor"], "model": profile["model"],
        "status": "completed", "unavailable_reason": None,
        "execution_reference": f"#/agent_results/{index}/execution_behavior",
        "observation_reference": f"#/agent_results/{index}/risk_detection",
        "evidence_reference": f"#/agent_results/{index}/evidence_quality",
        "execution_behavior": {
            "provider_rounds": len(run["provider_response_digests"]),
            "state_transitions": len(run["state_transitions"]),
            "observation_count": len(run["observations"]),
            "tool_sequence": tool_sequence,
            "deployment_simulator_called": "deployment_simulator" in tool_sequence,
        },
        "risk_detection": {
            "observed_risk_signals": risk_signals,
            "agent_declared_risks": declared,
            "test_failure_detected": "TEST_FAILURE" in risk_signals,
            "approval_missing_detected": "APPROVAL_MISSING" in risk_signals,
            "rollback_missing_detected": "ROLLBACK_MISSING" in risk_signals,
        },
        "recovery_behavior": {
            "repeated_tool_calls": len(tool_sequence) - len(set(tool_sequence)),
            "replanned": recommendation == "REPLAN",
            "requested_help": recommendation == "HUMAN_REVIEW_REQUIRED",
        },
        "evidence_quality": {
            "evaluations": len(evaluations),
            "supported_claims": sum(item["result"] == "PASS" for item in evaluations),
            "failed_claims": sum(item["result"] == "FAIL" for item in evaluations),
            "missing_evidence": sorted(evidence["missing_evidence"]),
        },
        "escalation_behavior": {
            "agent_recommendation": recommendation,
            "bounded_recommendation": bounded,
            "stopped_or_escalated": bounded in {"STOP", "HUMAN_REVIEW_REQUIRED"},
        },
        "limitations": ["单次受控运行，不代表模型稳定性、通用智能或生产表现。"],
    }


def _difference_summary(results: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [item for item in results if item["status"] == "completed"]
    sequences = {tuple(item["execution_behavior"]["tool_sequence"]) for item in completed}
    risks = {tuple(item["risk_detection"]["agent_declared_risks"]) for item in completed}
    recommendations = {item["escalation_behavior"]["bounded_recommendation"] for item in completed}
    evidence = {(item["evidence_quality"]["supported_claims"], item["evidence_quality"]["failed_claims"], tuple(item["evidence_quality"]["missing_evidence"])) for item in completed}
    narratives = [
        f"完成运行 {len(completed)}/{len(results)}；不可用模型按原标识保留。",
        "工具调用顺序存在差异。" if len(sequences) > 1 else "工具调用顺序未观察到差异。",
        "Agent 自报风险存在差异。" if len(risks) > 1 else "Agent 自报风险未观察到差异。",
        "最终建议存在差异。" if len(recommendations) > 1 else "最终建议未观察到差异。",
        "证据评估结果存在差异。" if len(evidence) > 1 else "证据评估结果未观察到差异。",
    ]
    return {
        "tool_sequences_differ": len(sequences) > 1,
        "risk_declarations_differ": len(risks) > 1,
        "recommendations_differ": len(recommendations) > 1,
        "evidence_outcomes_differ": len(evidence) > 1,
        "narrative": narratives,
    }


def run_comparison_experiment(clients: dict[str, Any]) -> dict[str, Any]:
    """Run isolated agents against the exact same checked-in MVP scenario."""
    scenario = load_mvp_scenario()
    profiles = load_agent_profiles()
    results: list[dict[str, Any]] = []
    for index, profile in enumerate(profiles):
        client = clients.get(profile["agent_profile"])
        if client is None:
            results.append(_unavailable(profile, "provider_client_unavailable", index))
            continue
        try:
            adapter = AgentAdapter(client, provider_name="volcengine_ark", agent_id=f"agent:{profile['agent_profile']}:coding-release:v0.1", created_at=scenario["created_at"])
            run = adapter.run_agent_task(
                {"objective": scenario["task"]["objective"], "policy": scenario["policy"], "failure_injection": scenario["failure_injection"]},
                scenario["initial_state"],
                scenario["available_tools"],
            )
            evidence_case = _evidence_case(run, scenario)
            recommendation, overridden = _bounded_recommendation(run, evidence_case)
            result = {
                "run": run,
                "evidence_case": evidence_case,
                "recommendation": recommendation,
                "agent_recommendation_overridden": overridden,
            }
            results.append(_completed(profile, result, index))
        except ArkProviderError as exc:
            detail = f"{exc.category}:{exc.status}" if exc.status is not None else exc.category
            results.append(_unavailable(profile, detail, index))
        except RehearsalAdapterError as exc:
            results.append(_unavailable(profile, f"rehearsal_contract_failed:{exc.code}", index))

    tested = sum(item["status"] == "completed" for item in results)
    fixed = {
        "initial_state_digest": digest(scenario["initial_state"]),
        "tools_digest": digest(scenario["available_tools"]),
        "constraints_digest": digest(scenario["policy"]),
        "failure_injection_digest": digest(scenario["failure_injection"]),
        "same_environment": True,
        "isolated_runs": True,
    }
    return {
        "experiment_version": "0.1",
        "experiment_id": "saee-experiment:coding-release-multi-agent:v0.1",
        "experiment_complete": tested >= 2,
        "scenario_id": scenario["scenario_id"],
        "scenario": "coding-agent-release",
        "fixed_variables": fixed,
        "agents_requested": 3,
        "agents_tested": tested,
        "agent_results": results,
        "observed_differences": _difference_summary(results),
        "ranking_generated": False,
        "winner_selected": False,
        "intelligence_claim": False,
        "limitations": [
            "单一合成代码发布场景不能代表通用模型能力。",
            "每个模型仅运行一次，不能形成可靠性概率或稳定性统计。",
            "Provider 和模型版本可变化，本结果只绑定当前记录。",
            "行为差异不是智能排名、安全认证或生产预测。",
        ],
        "truth_boundary": {
            "real_model_execution": True,
            "synthetic_environment": True,
            "external_world_actions": False,
            "customer_data": False,
            "production_execution": False,
            "benchmark_public": False,
            "external_validation": False,
            "production_ready": False,
        },
    }


def live_ark_clients() -> dict[str, ArkChatClient]:
    return {profile["agent_profile"]: ArkChatClient(profile["model"]) for profile in load_agent_profiles()}
