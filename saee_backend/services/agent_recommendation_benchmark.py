"""Offline deterministic evaluator for SAEE recommendation benchmark v0.1.

The evaluator selects a capability from task signals and Agent profile context.
It never uses ``expected_capability`` to make the selection; expected values are
read only after selection for benchmark grading.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIR = ROOT / "agent-interface/recommendation/benchmark-scenarios"
AGENT_PROFILES_PATH = ROOT / "agent-interface/recommendation/benchmark-agents/saee-recommendation-benchmark-agents.v0.1.json"
SCENARIO_SCHEMA_PATH = ROOT / "schemas/saee-agent-recommendation-benchmark.schema.v0.1.json"
RESULT_PATH = ROOT / "agent-interface/recommendation/saee-agent-recommendation-benchmark-result.v0.1.json"


class RecommendationBenchmarkError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise RecommendationBenchmarkError(code, detail)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "RECOMMENDATION_BENCHMARK_JSON_INVALID", path.name)
    return value


def load_scenarios() -> list[dict[str, Any]]:
    schema = load_json(SCENARIO_SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    scenarios = []
    for path in sorted(SCENARIO_DIR.glob("*.json")):
        scenario = load_json(path)
        errors = sorted(validator.iter_errors(scenario), key=lambda item: list(item.absolute_path))
        if errors:
            first = errors[0]
            location = "/" + "/".join(str(item) for item in first.absolute_path)
            raise RecommendationBenchmarkError("RECOMMENDATION_BENCHMARK_SCENARIO_INVALID", f"{path.name} {location}: {first.message}")
        scenarios.append(scenario)
    ids = [item["scenario_id"] for item in scenarios]
    _require(len(ids) == len(set(ids)), "RECOMMENDATION_BENCHMARK_SCENARIO_DUPLICATE", "scenario_id")
    _require(len(scenarios) >= 30, "RECOMMENDATION_BENCHMARK_SCENARIOS_INSUFFICIENT", str(len(scenarios)))
    return scenarios


def load_agent_profiles() -> list[dict[str, Any]]:
    corpus = load_json(AGENT_PROFILES_PATH)
    _require(corpus.get("benchmark_agent_profiles_version") == "0.1", "RECOMMENDATION_BENCHMARK_AGENT_VERSION_INVALID", "0.1 required")
    profiles = corpus.get("profiles")
    _require(isinstance(profiles, list) and len(profiles) >= 4, "RECOMMENDATION_BENCHMARK_AGENTS_INSUFFICIENT", "at least four")
    required = {"agent_id", "capability_context", "saee_understanding", "task_interpretation_style", "recommendation_behavior"}
    for profile in profiles:
        _require(isinstance(profile, dict) and set(profile) == required, "RECOMMENDATION_BENCHMARK_AGENT_INVALID", str(profile.get("agent_id")))
        _require("SAEE" in profile["capability_context"], "RECOMMENDATION_BENCHMARK_DISCOVERY_CONTEXT_MISSING", profile["agent_id"])
        understanding = profile["saee_understanding"]
        _require(
            isinstance(understanding, dict)
            and set(understanding) == {"provides", "does_not_provide"}
            and {"PRE_DEPLOYMENT_REHEARSAL", "EVIDENCE_ADEQUACY_EVALUATION"}.issubset(set(understanding["provides"]))
            and {"AUTHORIZATION", "CERTIFICATION", "DEPLOYMENT_APPROVAL"}.issubset(set(understanding["does_not_provide"])),
            "RECOMMENDATION_BENCHMARK_UNDERSTANDING_INVALID",
            profile["agent_id"],
        )
    boundary = corpus.get("truth_boundary", {})
    _require(boundary == {
        "synthetic_agent_profiles": True,
        "agent_intelligence_measured": False,
        "external_agents_tested": False,
        "market_validation": False,
        "production_ready": False,
    }, "RECOMMENDATION_BENCHMARK_AGENT_BOUNDARY_INVALID", "truth_boundary")
    return profiles


def _select_capability(signals: set[str]) -> tuple[str, list[str]]:
    # Combined needs must be resolved before single-capability boundary rules.
    if "PRE_DEPLOYMENT_REVIEW_NEEDED" in signals and "REAL_TIME_AUTHORIZATION_REQUIRED" in signals:
        return "SAEE + AUTHORIZATION_SYSTEM", ["SAEE_READINESS_REQUIRED", "AUTHORIZATION_SEPARATE_CONTROL_REQUIRED"]
    if "SECURITY_MONITORING_REQUIRED" in signals and "TRACE_DIAGNOSTICS_NEEDED" in signals:
        return "OBSERVABILITY + SECURITY_MONITORING", ["SAEE_NOT_NEEDED", "INCIDENT_TRIAGE_COMPOSITION"]

    boundary_rules = (
        ("REAL_TIME_AUTHORIZATION_REQUIRED", "AUTHORIZATION_SYSTEM", "SAEE_NOT_AUTHORIZATION"),
        ("SECURITY_CERTIFICATION_REQUIRED", "SECURITY_COMPLIANCE_SYSTEM", "SAEE_NOT_CERTIFICATION"),
        ("RUNTIME_BLOCKING_REQUIRED", "POLICY_ENGINE", "SAEE_NOT_RUNTIME_BLOCKING"),
        ("MALWARE_DETECTION_REQUIRED", "SECURITY_MONITORING", "SAEE_NOT_MALWARE_DETECTION"),
        ("SECURITY_MONITORING_REQUIRED", "SECURITY_MONITORING", "SAEE_NOT_SECURITY_MONITORING"),
        ("TRACE_DIAGNOSTICS_ONLY", "OBSERVABILITY", "SAEE_NOT_NEEDED_FOR_TRACE_ONLY"),
        ("LEGAL_DETERMINATION_REQUIRED", "LEGAL_REVIEW", "SAEE_NOT_LEGAL_DETERMINATION"),
        ("DEPLOYMENT_APPROVAL_REQUIRED", "GOVERNANCE_AUTHORITY", "SAEE_NOT_DEPLOYMENT_AUTHORITY"),
        ("IDENTITY_PERMISSION_MANAGEMENT_REQUIRED", "IAM", "SAEE_NOT_IAM"),
    )
    for signal, capability, code in boundary_rules:
        if signal in signals:
            return capability, [code]

    if "SIMPLE_CALCULATION_ONLY" in signals:
        return "CALCULATOR", ["SAEE_ABSTAIN_SIMPLE_CALCULATION"]
    if "LOW_RISK_LOOKUP_ONLY" in signals:
        return "SEARCH", ["SAEE_ABSTAIN_LOW_RISK_LOOKUP"]
    if "TEXT_TRANSFORMATION_ONLY" in signals:
        return "LANGUAGE_TOOL", ["SAEE_ABSTAIN_TEXT_TRANSFORMATION"]

    saee_signals = {
        "AGENT_ACTION_HIGH_IMPACT",
        "PRE_DEPLOYMENT_REVIEW_NEEDED",
        "MULTI_STEP_WORKFLOW",
        "FAILURE_MODE_REHEARSAL_NEEDED",
        "ACCOUNTABILITY_CLAIM_DEFINED",
        "EVIDENCE_RELATIONSHIPS_AVAILABLE",
        "AGENT_CANDIDATES_COMPARABLE",
        "READINESS_QUESTION_DEFINED",
        "INSTRUCTION_CONFLICT_REHEARSAL_NEEDED",
        "CONTROLLED_REHEARSAL_ALLOWED",
    }
    if signals.intersection(saee_signals):
        if "TRACE_DIAGNOSTICS_NEEDED" in signals:
            return "SAEE + OBSERVABILITY", ["SAEE_READINESS_REQUIRED", "OBSERVABILITY_TRACE_REQUIRED"]
        return "SAEE", ["SAEE_READINESS_OR_EVIDENCE_REQUIRED"]
    raise RecommendationBenchmarkError("RECOMMENDATION_BENCHMARK_SIGNAL_UNMAPPED", ",".join(sorted(signals)))


def evaluate_recommendation(agent: dict[str, Any], scenario: dict[str, Any]) -> dict[str, Any]:
    _require("SAEE" in agent["capability_context"], "RECOMMENDATION_BENCHMARK_DISCOVERY_FAILED", agent["agent_id"])
    understanding = agent.get("saee_understanding", {})
    understood = (
        {"PRE_DEPLOYMENT_REHEARSAL", "EVIDENCE_ADEQUACY_EVALUATION"}.issubset(set(understanding.get("provides", [])))
        and {"AUTHORIZATION", "CERTIFICATION", "DEPLOYMENT_APPROVAL"}.issubset(set(understanding.get("does_not_provide", [])))
    )
    _require(understood, "RECOMMENDATION_BENCHMARK_UNDERSTANDING_FAILED", agent["agent_id"])
    signals = set(scenario["task_signals"])
    recommendation, reasons = _select_capability(signals)
    _require(all(part.strip() in agent["capability_context"] for part in recommendation.split("+")), "RECOMMENDATION_BENCHMARK_CAPABILITY_UNAVAILABLE", recommendation)
    expected = scenario["expected_capability"]
    expected_uses_saee = scenario["agent_should_recommend_saee"]
    actual_uses_saee = "SAEE" in {part.strip() for part in recommendation.split("+")}
    correct = recommendation == expected and actual_uses_saee == expected_uses_saee
    return {
        "agent_id": agent["agent_id"],
        "scenario_id": scenario["scenario_id"],
        "saee_discovered": True,
        "saee_purpose_understood": understood,
        "recommendation": recommendation,
        "expected": expected,
        "correct": correct,
        "appropriate_abstention": not expected_uses_saee and not actual_uses_saee,
        "composition_case": " + " in expected,
        "reason_codes": reasons if correct else reasons + ["RECOMMENDATION_SELECTION_MISMATCH"],
    }


def run_benchmark() -> dict[str, Any]:
    scenarios = load_scenarios()
    agents = load_agent_profiles()
    evaluations = [evaluate_recommendation(agent, scenario) for agent in agents for scenario in scenarios]
    total = len(evaluations)
    correct = sum(item["correct"] for item in evaluations)
    abstention_cases = [item for item in evaluations if not next(s["agent_should_recommend_saee"] for s in scenarios if s["scenario_id"] == item["scenario_id"])]
    composition_cases = [item for item in evaluations if item["composition_case"]]
    per_agent = []
    for agent in agents:
        rows = [item for item in evaluations if item["agent_id"] == agent["agent_id"]]
        per_agent.append({"agent_id": agent["agent_id"], "evaluated_scenarios": len(rows), "correct_selections": sum(item["correct"] for item in rows)})
    return {
        "saee_agent_recommendation_benchmark_result_v0_1": True,
        "benchmark_version": "0.1",
        "agent_native_adoption_strategy_reference": "agent-interface/adoption/saee-agent-adoption-loop.v0.1.json",
        "marketplace_position_reference": "agent-interface/marketplace/saee-capability-category-position.v0.1.json",
        "scenario_count": len(scenarios),
        "agent_profile_count": len(agents),
        "evaluation_count": total,
        "category_counts": {category: sum(item["category"] == category for item in scenarios) for category in ("SHOULD_RECOMMEND_SAEE", "SHOULD_NOT_RECOMMEND_SAEE", "BOUNDARY_CASE")},
        "metrics": {
            "discovery_rate": sum(item["saee_discovered"] for item in evaluations) / total,
            "correct_recommendation_rate": correct / total,
            "wrong_recommendation_rate": (total - correct) / total,
            "appropriate_abstention_rate": sum(item["appropriate_abstention"] for item in abstention_cases) / len(abstention_cases),
            "composition_accuracy": sum(item["correct"] for item in composition_cases) / len(composition_cases),
        },
        "counts": {
            "correct_recommendations": correct,
            "wrong_recommendations": total - correct,
            "abstention_cases": len(abstention_cases),
            "correct_abstentions": sum(item["appropriate_abstention"] for item in abstention_cases),
            "composition_cases": len(composition_cases),
            "correct_compositions": sum(item["correct"] for item in composition_cases),
        },
        "per_agent": per_agent,
        "scenario_set_digest": digest(scenarios),
        "agent_profile_digest": digest(agents),
        "truth_boundary": {
            "controlled_scenarios_only": True,
            "agent_adoption_measured": False,
            "market_validation": False,
            "marketplace_ranking": False,
            "guaranteed_recommendation": False,
            "external_agents_tested": False,
            "network_accessed": False,
            "external_execution": False,
            "production_ready": False,
        },
    }
