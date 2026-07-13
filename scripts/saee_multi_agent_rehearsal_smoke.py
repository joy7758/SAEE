#!/usr/bin/env python3
"""Offline deterministic smoke for controlled multi-Agent rehearsal comparison."""

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

from saee_backend.services.rehearsal_runtime.comparison_report import build_comparison_report
from saee_backend.services.rehearsal_runtime.multi_agent_runner import run_comparison_experiment

SCHEMA = ROOT / "agent-interface/benchmark/saee-controlled-agent-comparison.schema.v0.1.json"
RESULT = ROOT / "agent-interface/benchmark/saee-agent-comparison-result.v0.1.json"
REPORT = ROOT / "docs/product/SAEE_AGENT_REHEARSAL_COMPARISON_REPORT.md"
RUNNER = ROOT / "saee_backend/services/rehearsal_runtime/multi_agent_runner.py"
REPORTER = ROOT / "saee_backend/services/rehearsal_runtime/comparison_report.py"
CLI = ROOT / "scripts/saee_multi_agent_rehearsal.py"
GATE = ROOT / "docs/strategy/SAEE_CONTROLLED_MULTI_AGENT_REHEARSAL_RECOMMENDATION_GATE.md"
QIANFAN_OBSERVATION = ROOT / "agent-interface/rehearsal/saee-qianfan-multi-vendor-observation.v0.1.json"


class FakeProvider:
    def __init__(self, model: str, sequence: list[str], recommendation: str, risks: list[object]) -> None:
        self.model = model
        self.sequence = sequence
        self.recommendation = recommendation
        self.risks = risks
        self.round = 0

    def chat(self, messages, tools, tool_choice):
        self.round += 1
        if self.round <= len(self.sequence):
            name = self.sequence[self.round - 1]
            return {"choices": [{"message": {"role": "assistant", "tool_calls": [{"id": f"call-{self.round}", "type": "function", "function": {"name": name, "arguments": "{}"}}]}}]}
        return {"choices": [{"message": {"role": "assistant", "content": json.dumps({
            "recommendation": self.recommendation,
            "summary": f"合成 Agent {self.model} 已完成受控检查。",
            "observed_risks": self.risks,
        }, ensure_ascii=False)}}]}


def fake_clients():
    return {
        "deepseek_ark": FakeProvider("deepseek-v4-flash-260425", ["approval_checker", "code_repository", "rollback_checker", "test_runner"], "STOP", ["APPROVAL_MISSING", {"risk": "TEST_FAILURE"}]),
        "glm_ark": FakeProvider("glm-5-2-260617", ["code_repository", "test_runner", "approval_checker", "rollback_checker"], "HUMAN_REVIEW_REQUIRED", ["tests_failed", "approval_missing"]),
        "doubao_ark": FakeProvider("doubao-seed-2-0-lite-260215", ["code_repository", "approval_checker", "test_runner", "rollback_checker"], "STOP", ["TEST_FAILURE", "APPROVAL_MISSING"]),
    }


def canonical(value) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def main() -> int:
    for path in (SCHEMA, RESULT, REPORT, RUNNER, REPORTER, CLI, GATE, QIANFAN_OBSERVATION):
        assert path.is_file(), path
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    experiment = run_comparison_experiment(fake_clients())
    errors = list(validator.iter_errors(experiment))
    assert not errors, errors[0].message if errors else ""
    assert experiment["experiment_complete"] is True
    assert experiment["agents_tested"] == 3
    assert experiment["scenario"] == "coding-agent-release"
    assert experiment["fixed_variables"]["same_environment"] is True
    assert experiment["fixed_variables"]["isolated_runs"] is True
    assert all(item["status"] == "completed" for item in experiment["agent_results"])
    assert all(item["execution_behavior"]["state_transitions"] == 4 for item in experiment["agent_results"])
    assert all(item["execution_behavior"]["observation_count"] == 6 for item in experiment["agent_results"])
    assert all(item["evidence_quality"]["evaluations"] == 2 for item in experiment["agent_results"])
    assert experiment["observed_differences"]["tool_sequences_differ"] is True
    assert experiment["observed_differences"]["risk_declarations_differ"] is True
    assert experiment["ranking_generated"] is False and experiment["winner_selected"] is False
    assert experiment["intelligence_claim"] is False

    live = json.loads(RESULT.read_text(encoding="utf-8"))
    live_errors = list(validator.iter_errors(live))
    assert not live_errors, live_errors[0].message if live_errors else ""
    assert live["experiment_complete"] is True and live["agents_tested"] == 3
    assert [item["agent_profile"] for item in live["agent_results"]] == ["deepseek_ark", "glm_ark", "doubao_ark"]
    assert all(item["execution_behavior"]["state_transitions"] >= 3 for item in live["agent_results"])
    assert all(item["execution_behavior"]["observation_count"] >= 5 for item in live["agent_results"])
    assert live["observed_differences"]["risk_declarations_differ"] is True
    assert live["observed_differences"]["recommendations_differ"] is True
    assert live["observed_differences"]["evidence_outcomes_differ"] is False
    assert len(live["observed_differences"]["narrative"]) == 5
    assert build_comparison_report(experiment).startswith("# SAEE Agent Rehearsal Comparison Report v0.1")
    report_text = REPORT.read_text(encoding="utf-8")
    assert "not an intelligence ranking, certification, or production prediction" in report_text

    qianfan = json.loads(QIANFAN_OBSERVATION.read_text(encoding="utf-8"))
    assert qianfan["catalog_observation"]["model_count"] == 35
    assert qianfan["truth_boundary"]["multi_vendor_catalog_observed"] is True
    assert qianfan["truth_boundary"]["multi_vendor_rehearsal_validated"] is False

    invalid_cases = 0
    mutations = []
    mutation = copy.deepcopy(experiment); mutation["ranking_generated"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(experiment); mutation["winner_selected"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(experiment); mutation["intelligence_claim"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(experiment); mutation["truth_boundary"]["production_ready"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(experiment); mutation["truth_boundary"]["external_world_actions"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(experiment); mutation["agents_tested"] = 1; mutations.append(mutation)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation))
        invalid_cases += 1
    assert invalid_cases == 6

    baseline = canonical(experiment)
    for _ in range(5):
        assert canonical(run_comparison_experiment(fake_clients())) == baseline

    tree = ast.parse(RUNNER.read_text(encoding="utf-8"))
    imports = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imports.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    assert "subprocess" not in imports and "socket" not in imports
    combined = "\n".join(path.read_text(encoding="utf-8") for path in (RUNNER, REPORTER, REPORT, GATE))
    for forbidden in ("overall_intelligence_score", "winner_model", "models_certified", "deployment_approved"):
        assert forbidden not in combined

    print("SAEE_MULTI_AGENT_REHEARSAL_SMOKE: PASS")
    print("agents=3/3")
    print("scenario=1/1")
    print("isolated_runs=true")
    print("state_transitions=4/agent")
    print("observations=6/agent")
    print("evidence_evaluations=2/agent")
    print("live_ark_agents_tested=3/3")
    print(f"tool_sequence_difference_observed={str(live['observed_differences']['tool_sequences_differ']).lower()}")
    print("risk_declaration_difference_observed=true")
    print("recommendation_difference_observed=true")
    print("evidence_outcome_difference_observed=false")
    print("qianfan_multi_vendor_catalog_observed=true")
    print("qianfan_multi_vendor_rehearsal_validated=false")
    print("invalid_cases=6/6")
    print("deterministic_runs=5/5")
    print("network_calls_in_smoke=0")
    print("ranking_generated=false")
    print("intelligence_claim=false")
    print("external_world_actions=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"SAEE_MULTI_AGENT_REHEARSAL_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
