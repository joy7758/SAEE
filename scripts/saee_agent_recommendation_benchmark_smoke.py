#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Agent Recommendation Benchmark v0.1."""

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

from saee_backend.services.agent_recommendation_benchmark import (  # noqa: E402
    AGENT_PROFILES_PATH,
    RESULT_PATH,
    SCENARIO_SCHEMA_PATH,
    RecommendationBenchmarkError,
    evaluate_recommendation,
    load_agent_profiles,
    load_json,
    load_scenarios,
    run_benchmark,
)


SERVICE = ROOT / "saee_backend/services/agent_recommendation_benchmark.py"
DOC = ROOT / "docs/research/SAEE_AGENT_RECOMMENDATION_BENCHMARK.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_RECOMMENDATION_BENCHMARK_RECOMMENDATION_GATE.md"


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen", "run", "Popen", "write_text", "write_bytes"}:
            found.add(node.func.attr)
    return found


def main() -> int:
    for path in (SCENARIO_SCHEMA_PATH, AGENT_PROFILES_PATH, RESULT_PATH, SERVICE, DOC, GATE):
        assert path.is_file(), path
    schema = load_json(SCENARIO_SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    scenarios = load_scenarios()
    agents = load_agent_profiles()
    assert len(scenarios) == 30
    assert len(agents) == 4
    categories = {name: sum(item["category"] == name for item in scenarios) for name in ("SHOULD_RECOMMEND_SAEE", "SHOULD_NOT_RECOMMEND_SAEE", "BOUNDARY_CASE")}
    assert categories == {"SHOULD_RECOMMEND_SAEE": 10, "SHOULD_NOT_RECOMMEND_SAEE": 10, "BOUNDARY_CASE": 10}

    generated = run_benchmark()
    recorded = load_json(RESULT_PATH)
    assert generated == recorded
    assert generated["evaluation_count"] == 120
    assert generated["metrics"] == {
        "discovery_rate": 1.0,
        "correct_recommendation_rate": 1.0,
        "wrong_recommendation_rate": 0.0,
        "appropriate_abstention_rate": 1.0,
        "composition_accuracy": 1.0,
    }
    assert generated["counts"]["abstention_cases"] == 80
    assert generated["counts"]["composition_cases"] == 24
    assert all(item["correct_selections"] == 30 for item in generated["per_agent"])

    invalid_cases = 0
    base = scenarios[0]
    mutations = []
    mutation = copy.deepcopy(base); mutation.pop("expected_capability"); mutations.append(mutation)
    mutation = copy.deepcopy(base); mutation["truth_boundary"]["external_adoption"] = True; mutations.append(mutation)
    mutation = copy.deepcopy(base); mutation["agent_should_recommend_saee"] = False; mutations.append(mutation)
    mutation = copy.deepcopy(base); mutation["marketplace_rank"] = 1; mutations.append(mutation)
    mutation = copy.deepcopy(base); mutation["expected_capability"] = "POPULAR_MARKETPLACE_TOOL"; mutations.append(mutation)
    mutation = copy.deepcopy(base); mutation["risk_level"] = "GUARANTEED_SAFE"; mutations.append(mutation)
    for mutation in mutations:
        assert list(validator.iter_errors(mutation)); invalid_cases += 1

    bad_signal = copy.deepcopy(base); bad_signal["task_signals"] = ["UNMAPPED_SIGNAL"]
    try:
        evaluate_recommendation(agents[0], bad_signal)
    except RecommendationBenchmarkError as exc:
        assert exc.code == "RECOMMENDATION_BENCHMARK_SIGNAL_UNMAPPED"; invalid_cases += 1
    else:
        raise AssertionError("unmapped signal accepted")
    bad_agent = copy.deepcopy(agents[0]); bad_agent["capability_context"].remove("SAEE")
    try:
        evaluate_recommendation(bad_agent, base)
    except RecommendationBenchmarkError as exc:
        assert exc.code == "RECOMMENDATION_BENCHMARK_DISCOVERY_FAILED"; invalid_cases += 1
    else:
        raise AssertionError("undiscoverable SAEE accepted")
    misunderstood_agent = copy.deepcopy(agents[0]); misunderstood_agent["saee_understanding"]["does_not_provide"].remove("AUTHORIZATION")
    try:
        evaluate_recommendation(misunderstood_agent, base)
    except RecommendationBenchmarkError as exc:
        assert exc.code == "RECOMMENDATION_BENCHMARK_UNDERSTANDING_FAILED"; invalid_cases += 1
    else:
        raise AssertionError("misunderstood SAEE boundary accepted")
    assert invalid_cases == 9

    canonical = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        assert json.dumps(run_benchmark(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "smtplib", "importlib"}
    assert not imported_roots(SERVICE).intersection(forbidden_imports)
    assert not forbidden_calls(SERVICE)
    report = DOC.read_text(encoding="utf-8")
    for forbidden_claim in ("市场采用已验证", "marketplace ranking achieved", "guaranteed recommendation", "production recommendation validated"):
        assert forbidden_claim not in report
    assert "This benchmark evaluates recommendation behavior in controlled scenarios. It does not measure real-world agent adoption." in report
    assert "该基准测试受控场景下的智能体推荐行为，不衡量真实世界智能体采用。" in report

    print("SAEE_AGENT_RECOMMENDATION_BENCHMARK_SMOKE: PASS")
    print("scenario_count=30/30")
    print("scenario_categories=3/3")
    print("agent_profiles=4/4")
    print("evaluation_count=120/120")
    print("valid_cases=1/1")
    print("invalid_cases=9/9")
    print("deterministic_runs=5/5")
    print("discovery_rate=1.0")
    print("correct_recommendation_rate=1.0")
    print("wrong_recommendation_rate=0.0")
    print("appropriate_abstention_rate=1.0")
    print("composition_accuracy=1.0")
    print("agent_adoption_measured=false")
    print("market_validation=false")
    print("external_agents_tested=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
