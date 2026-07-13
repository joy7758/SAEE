#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE multi-round Agent preference simulation."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_preference_simulation import (  # noqa: E402
    AgentPreferenceError,
    CORPUS_PATH,
    CORPUS_SCHEMA_PATH,
    PROFILE_PATH,
    RUN_SCHEMA_PATH,
    aggregate_agent_preferences,
    load_json,
    run_agent_preference_simulation,
)


SERVICE = ROOT / "saee_backend/services/agent_preference_simulation.py"
DOC = ROOT / "docs/architecture/SAEE_AGENT_PREFERENCE_MULTI_ROUND_SIMULATION.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_PREFERENCE_SIMULATION_RECOMMENDATION_GATE.md"


class FakeProvider:
    model = "offline-fake-agent-v0.1"

    def __init__(self, scenario_id: str, adjacent: str, expectation: dict[str, Any], *, wrong: bool = False, submit_early: bool = False) -> None:
        self.scenario_id = scenario_id
        self.adjacent = adjacent
        self.expectation = expectation
        self.round = 0
        self.wrong = wrong
        self.submit_early = submit_early

    def _response(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return {"choices": [{"message": {"role": "assistant", "tool_calls": [{"id": f"call-{self.round}", "type": "function", "function": {"name": name, "arguments": json.dumps(arguments, ensure_ascii=False)}}]}}]}

    def chat(self, messages, tools, tool_choice):
        self.round += 1
        if self.round == 1 and not self.submit_early:
            return self._response("inspect_saee_recommendation", {})
        if self.round == 2 and not self.submit_early:
            return self._response("inspect_adjacent_capability", {"capability": self.adjacent})
        decision = "DO_NOT_RECOMMEND_SAEE" if self.wrong else self.expectation["expected_decision"]
        capabilities = list(self.expectation["required_capabilities"])
        if self.wrong:
            capabilities = ["KNOWLEDGE_RETRIEVAL"]
        return self._response("submit_agent_preference", {
            "decision": decision,
            "selected_rule_ids": self.expectation["required_rules"],
            "preferred_capabilities": capabilities,
            "reasoning_summary": "根据适用规则和相邻能力边界选择最小能力组合。",
            "limitations": ["本结果只适用于合成能力选择，不证明客户采用或生产就绪。"],
            "boundary_ack": {"saee_is_not_authorization": True, "saee_is_not_certification": True, "saee_is_not_legal_approval": True, "saee_is_not_autonomous_control": True},
        })


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> int:
    for path in (CORPUS_PATH, CORPUS_SCHEMA_PATH, RUN_SCHEMA_PATH, PROFILE_PATH, SERVICE, DOC, GATE):
        assert path.is_file(), path
    corpus = load_json(CORPUS_PATH)
    profiles = load_json(PROFILE_PATH)
    corpus_schema = load_json(CORPUS_SCHEMA_PATH)
    run_schema = load_json(RUN_SCHEMA_PATH)
    Draft202012Validator.check_schema(corpus_schema)
    Draft202012Validator.check_schema(run_schema)
    assert not list(Draft202012Validator(corpus_schema, format_checker=FormatChecker()).iter_errors(corpus))
    expectations = {item["scenario_id"]: item for item in profiles["expectations"]}
    runs = []
    for scenario in corpus["scenarios"]:
        provider = FakeProvider(scenario["scenario_id"], scenario["adjacent_capability"], expectations[scenario["scenario_id"]])
        run = run_agent_preference_simulation(scenario["scenario_id"], provider, external_reasoning_model_called=False)
        assert not list(Draft202012Validator(run_schema, format_checker=FormatChecker()).iter_errors(run))
        assert run["grading"]["assessment"] == "MATCHED_PROFILE"
        assert len(run["rounds"]) == 3
        runs.append(run)
    aggregate = aggregate_agent_preferences(runs)
    assert aggregate["total_agents"] == 6
    assert aggregate["total_provider_rounds"] == 18
    assert aggregate["matched_profiles"] == 6
    assert aggregate["recommend_saee"] == 0
    assert aggregate["compose_with_saee"] == 3
    assert aggregate["do_not_recommend_saee"] == 3
    assert aggregate["contextual_agent_preference_validated"] is True
    assert aggregate["universal_agent_preference_claimed"] is False

    invalid_cases = 0
    wrong_scenario = corpus["scenarios"][0]
    wrong_provider = FakeProvider(wrong_scenario["scenario_id"], wrong_scenario["adjacent_capability"], expectations[wrong_scenario["scenario_id"]], wrong=True)
    wrong_run = run_agent_preference_simulation(wrong_scenario["scenario_id"], wrong_provider, external_reasoning_model_called=False)
    assert wrong_run["grading"]["assessment"] == "DID_NOT_MATCH_PROFILE"; invalid_cases += 1
    early = FakeProvider(wrong_scenario["scenario_id"], wrong_scenario["adjacent_capability"], expectations[wrong_scenario["scenario_id"]], submit_early=True)
    try:
        run_agent_preference_simulation(wrong_scenario["scenario_id"], early, external_reasoning_model_called=False)
    except AgentPreferenceError as exc:
        assert exc.code == "AGENT_PREFERENCE_REQUIRED_INSPECTIONS_MISSING"; invalid_cases += 1
    else:
        raise AssertionError("early submission accepted")
    try:
        run_agent_preference_simulation("agent-preference:unknown:v0.1", early, external_reasoning_model_called=False)
    except AgentPreferenceError as exc:
        assert exc.code == "AGENT_PREFERENCE_SCENARIO_UNKNOWN"; invalid_cases += 1
    else:
        raise AssertionError("unknown scenario accepted")
    for field, value in (("human_participants", True), ("customer_validation", True), ("market_validation", True), ("production_ready", True)):
        mutation = copy.deepcopy(corpus); mutation["truth_boundary"][field] = value
        assert list(Draft202012Validator(corpus_schema).iter_errors(mutation)); invalid_cases += 1
    mutation = copy.deepcopy(corpus); mutation["scenarios"] = mutation["scenarios"][:5]
    assert list(Draft202012Validator(corpus_schema).iter_errors(mutation)); invalid_cases += 1
    assert invalid_cases == 8

    canonical = json.dumps(aggregate, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = []
        for scenario in corpus["scenarios"]:
            provider = FakeProvider(scenario["scenario_id"], scenario["adjacent_capability"], expectations[scenario["scenario_id"]])
            repeated.append(run_agent_preference_simulation(scenario["scenario_id"], provider, external_reasoning_model_called=False))
        assert json.dumps(aggregate_agent_preferences(repeated), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "smtplib", "importlib"}
    assert not imported_roots(SERVICE).intersection(forbidden)
    assert all(run["truth_boundary"]["external_world_actions"] == 0 for run in runs)
    print("SAEE_AGENT_PREFERENCE_SIMULATION_SMOKE: PASS")
    print("synthetic_agents=6/6")
    print("provider_rounds=18/18")
    print("matched_profiles=6/6")
    print("recommend_saee=0")
    print("compose_with_saee=3")
    print("do_not_recommend_saee=3")
    print("invalid_cases=8/8")
    print("deterministic_runs=5/5")
    print("contextual_agent_preference_validated=true")
    print("universal_agent_preference_claimed=false")
    print("human_participants=false")
    print("customer_validated=false")
    print("external_world_actions=0")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
