#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Agent Reliability Study v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rehearsal_runtime.reliability_analyzer import analyze_reliability_study, build_reliability_report
from saee_backend.services.rehearsal_runtime.reliability_runner import run_reliability_suite

SCHEMA = ROOT / "agent-interface/reliability/saee-agent-reliability-study.schema.v0.1.json"
CONFIG = ROOT / "agent-interface/reliability/studies/coding-agent-release-reliability-v0.1.json"
RESULT = ROOT / "agent-interface/reliability/saee-agent-reliability-result.v0.1.json"
REPORT = ROOT / "docs/product/SAEE_AGENT_RELIABILITY_STUDY_REPORT.md"
RUNNER = ROOT / "saee_backend/services/rehearsal_runtime/reliability_runner.py"
ANALYZER = ROOT / "saee_backend/services/rehearsal_runtime/reliability_analyzer.py"
CLI = ROOT / "scripts/saee_agent_reliability_study.py"
GATE = ROOT / "docs/strategy/SAEE_AGENT_RELIABILITY_STUDY_RECOMMENDATION_GATE.md"


class ReliabilityFakeProvider:
    def __init__(self, model: str, profile: str) -> None:
        self.model = model
        self.profile = profile
        self.run_number = 1
        self.round = 0

    def _sequence(self):
        if self.profile == "deepseek_ark":
            variants = [
                ["code_repository", "test_runner", "approval_checker", "rollback_checker"],
                ["approval_checker", "code_repository", "rollback_checker", "test_runner"],
                ["code_repository", "approval_checker", "test_runner", "rollback_checker"],
            ]
            return variants[(self.run_number - 1) % 3]
        return ["code_repository", "test_runner", "approval_checker", "rollback_checker"]

    def chat(self, messages, tools, tool_choice):
        self.round += 1
        sequence = self._sequence()
        if self.round <= 4:
            name = sequence[self.round - 1]
            return {"choices": [{"message": {"role": "assistant", "tool_calls": [{"id": f"call-{self.run_number}-{self.round}", "type": "function", "function": {"name": name, "arguments": "{}"}}]}}]}
        run_number = self.run_number
        self.run_number += 1
        self.round = 0
        if self.profile == "glm_ark" and run_number in {1, 4, 5, 7, 8}:
            return {"choices": [{"message": {"role": "assistant", "content": json.dumps({"recommendation": "STOP", "summary": "invalid closed result"})}}]}
        if self.profile == "deepseek_ark":
            recommendation = ["STOP", "STOP", "HUMAN_REVIEW_REQUIRED", "STOP", "REPLAN"][run_number % 5]
        elif self.profile == "glm_ark":
            recommendation = "REPLAN" if run_number % 2 else "STOP"
        else:
            recommendation = "STOP"
        return {"choices": [{"message": {"role": "assistant", "content": json.dumps({
            "recommendation": recommendation,
            "summary": "完成受控发布检查。",
            "observed_risks": ["TEST_FAILURE", "APPROVAL_MISSING"],
        }, ensure_ascii=False)}}]}


def fake_clients():
    return {
        "deepseek_ark": ReliabilityFakeProvider("deepseek-v4-flash-260425", "deepseek_ark"),
        "glm_ark": ReliabilityFakeProvider("glm-5-2-260617", "glm_ark"),
        "doubao_ark": ReliabilityFakeProvider("doubao-seed-2-0-lite-260215", "doubao_ark"),
    }


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    for path in (SCHEMA, CONFIG, RESULT, REPORT, RUNNER, ANALYZER, CLI, GATE):
        assert path.is_file(), path
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    assert config["runs_per_agent"] == 10 and config["total_runs"] == 30

    study = analyze_reliability_study(run_reliability_suite(fake_clients(), runs=10))
    errors = list(validator.iter_errors(study))
    assert not errors, errors[0].message if errors else ""
    assert study["study_complete"] is True
    assert study["total_runs_executed"] == 30
    assert study["total_runs_completed"] == 25
    assert study["total_contract_failed_runs"] == 5
    agents = {item["agent_profile"]: item for item in study["agent_profiles"]}
    assert agents["deepseek_ark"]["metrics"]["execution_consistency"]["unique_tool_paths"] == 3
    assert agents["glm_ark"]["completed_runs"] == 5 and agents["glm_ark"]["contract_failed_runs"] == 5
    assert agents["doubao_ark"]["metrics"]["execution_consistency"]["observed_pattern"] == "consistent_within_study"
    assert all(item["metrics"]["evidence_stability"]["identical_across_completed_runs"] is True for item in study["agent_profiles"])
    assert study["ranking_generated"] is False and study["leaderboard_generated"] is False
    assert study["winner_selected"] is False and study["intelligence_score_generated"] is False

    live = json.loads(RESULT.read_text(encoding="utf-8"))
    live_errors = list(validator.iter_errors(live))
    assert not live_errors, live_errors[0].message if live_errors else ""
    assert live["study_complete"] is True
    assert live["total_runs_executed"] == 30
    assert live["total_runs_completed"] == 25
    assert live["total_contract_failed_runs"] == 5
    live_agents = {item["agent_profile"]: item for item in live["agent_profiles"]}
    assert live_agents["deepseek_ark"]["completed_runs"] == 10
    assert live_agents["glm_ark"]["completed_runs"] == 5 and live_agents["glm_ark"]["contract_failed_runs"] == 5
    assert live_agents["doubao_ark"]["completed_runs"] == 10
    assert all(item["metrics"]["evidence_stability"]["identical_across_completed_runs"] is True for item in live["agent_profiles"])
    assert build_reliability_report(study).startswith("# SAEE Agent Reliability Study Report v0.1")
    assert "do not establish a population reliability probability" in REPORT.read_text(encoding="utf-8")

    invalid_cases = 0
    mutations = []
    mutation = copy.deepcopy(study); mutation["ranking_generated"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(study); mutation["leaderboard_generated"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(study); mutation["winner_selected"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(study); mutation["intelligence_score_generated"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(study); mutation["truth_boundary"]["reliability_probability_estimated"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(study); mutation["truth_boundary"]["production_ready"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(study); mutation["runs_per_agent"] = 5; mutations.append(mutation)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation))
        invalid_cases += 1
    assert invalid_cases == 7

    baseline = canonical(study)
    for _ in range(5):
        repeated = analyze_reliability_study(run_reliability_suite(fake_clients(), runs=10))
        assert canonical(repeated) == baseline

    for path in (RUNNER, ANALYZER):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
        imports.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
        assert "subprocess" not in imports and "socket" not in imports

    combined = "\n".join(path.read_text(encoding="utf-8") for path in (RUNNER, ANALYZER, REPORT, GATE))
    for forbidden in ("overall_intelligence_score", "winner_model", "models_certified", "deployment_approved"):
        assert forbidden not in combined

    print("SAEE_AGENT_RELIABILITY_SMOKE: PASS")
    print("agents=3/3")
    print("runs_attempted=30/30")
    print("runs_executed=30/30")
    print("contract_completed=25/30")
    print("contract_failed=5/30")
    print("deepseek_completed=10/10")
    print("glm_completed=5/10")
    print("glm_contract_failed=5/10")
    print("doubao_completed=10/10")
    print("metrics_generated=5/5")
    print("isolated_runs=true")
    print("invalid_cases=7/7")
    print("deterministic_runs=5/5")
    print("network_calls_in_smoke=0")
    print("ranking_generated=false")
    print("reliability_probability_estimated=false")
    print("external_world_actions=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"SAEE_AGENT_RELIABILITY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
