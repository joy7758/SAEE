#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Agent-Native Invocation Evaluation v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_invocation_evaluator import (
    InvocationEvaluationError,
    build_invocation_evaluation_result,
    evaluate_invocation_scenario,
)


SCHEMA_PATH = ROOT / "schemas/saee-agent-invocation-evaluation.schema.json"
EXAMPLES_ROOT = ROOT / "agent-interface/capabilities/invocation-evaluation/examples"
RESULT_PATH = ROOT / "agent-interface/capabilities/saee-agent-invocation-evaluation-result.v0.1.json"
DOC_PATH = ROOT / "docs/architecture/SAEE_AGENT_INVOCATION_EVALUATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_AGENT_INVOCATION_EVALUATION_RECOMMENDATION_GATE.md"
MANIFEST_PATH = ROOT / "agent-interface/capabilities/saee-capability-manifest.v0.1.json"
EVALUATOR_PATH = ROOT / "saee_backend/services/agent_invocation_evaluator.py"

EXAMPLE_FILES = {
    "CORRECT_AGENT": "correct-agent.json",
    "OVERREACHING_AGENT": "overreaching-agent.json",
    "INVALID_TOOL_AGENT": "invalid-tool-agent.json",
    "APPROVAL_CONFUSION_AGENT": "approval-confusion-agent.json",
}


class InvocationSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise InvocationSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__", "open"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "system",
            "popen",
            "run",
            "Popen",
            "write_text",
            "write_bytes",
            "open",
        }:
            found.add(node.func.attr)
    return found


def schema_errors(scenario: dict[str, Any]) -> list[Any]:
    schema = read_json(SCHEMA_PATH)
    return list(Draft202012Validator(schema).iter_errors(scenario))


def expect_scenario_error(scenario: dict[str, Any], label: str) -> None:
    try:
        evaluate_invocation_scenario(scenario)
    except InvocationEvaluationError:
        return
    raise InvocationSmokeError(f"invalid scenario accepted: {label}")


def main() -> None:
    for path in (SCHEMA_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, MANIFEST_PATH, EVALUATOR_PATH):
        require(path.is_file(), f"missing required file: {path}")
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib", "sqlite3"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        require(not imported_roots(path).intersection(forbidden_imports), f"network/subprocess import in {path.name}")
        require(not forbidden_calls(path), f"external execution or persistence in {path.name}: {forbidden_calls(path)}")

    document = DOC_PATH.read_text(encoding="utf-8")
    require(
        "This evaluation tests capability usage correctness. It does not measure agent intelligence or deployment readiness." in document,
        "English limitation missing",
    )
    require("该评估测试能力使用正确性，不衡量智能体智能水平或部署就绪性。" in document, "Chinese limitation missing")

    scenarios: list[dict[str, Any]] = []
    by_caller: dict[str, dict[str, Any]] = {}
    for caller_type, filename in EXAMPLE_FILES.items():
        path = EXAMPLES_ROOT / filename
        require(path.is_file(), f"caller fixture missing: {filename}")
        scenario = read_json(path)
        require(not schema_errors(scenario), f"scenario schema invalid: {filename}")
        require(scenario["caller_type"] == caller_type, f"caller type mismatch: {filename}")
        scenarios.append(scenario)
        by_caller[caller_type] = scenario

    generated = build_invocation_evaluation_result(scenarios)
    checked = read_json(RESULT_PATH)
    require(generated == checked, "checked invocation result drifted from evaluator")
    require(generated["evaluation_result"] == "PASS", "aggregate evaluation failed")
    require(generated["caller_cases"] == 4, "caller count invalid")
    require(generated["valid_cases"] == 1 and generated["invalid_cases"] == 3, "valid/invalid split invalid")
    require(generated["all_callers_evaluated"] is True, "caller coverage incomplete")
    require(generated["all_expected_outcomes_matched"] is True, "expected outcome mismatch")

    results = {item["caller_type"]: item for item in generated["results"]}
    correct = results["CORRECT_AGENT"]
    require(all(correct[field] == "PASS" for field in ("discovery_result", "contract_result", "interpretation_result", "boundary_result", "scenario_result")), "correct caller did not pass")
    overreach = results["OVERREACHING_AGENT"]
    require(overreach["contract_result"] == "PASS", "overreaching request contract should pass")
    require(overreach["interpretation_result"] == "FAIL" and overreach["boundary_result"] == "FAIL", "overreach not rejected")
    require({"SYSTEM_UNSAFE", "ACTION_BLOCKED"}.issubset(overreach["boundary_violations"]), "overreach reasons missing")
    invalid = results["INVALID_TOOL_AGENT"]
    require(invalid["actual_tool_result"] == "REJECTED_INPUT" and invalid["contract_result"] == "FAIL", "invalid caller not rejected")
    require(len(invalid["additional_probe_results"]) == 2, "invalid caller probes missing")
    require(all(item["expected_rejection_matched"] for item in invalid["additional_probe_results"]), "invalid probe behavior mismatch")
    approval = results["APPROVAL_CONFUSION_AGENT"]
    require(approval["actual_claim_assessment"] == "SUPPORTED", "approval scenario baseline invalid")
    require(approval["interpretation_result"] == "FAIL" and "DEPLOYMENT_APPROVED" in approval["boundary_violations"], "approval confusion not rejected")

    false_fields = (
        "external_agents_tested",
        "agent_intelligence_measured",
        "adoption_validated",
        "commercial_success_validated",
        "public_tool_available",
        "mcp_used",
        "api_used",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    )
    require(all(generated[field] is False for field in false_fields), "aggregate truth boundary promoted")
    require(generated["synthetic_callers_only"] is True, "synthetic boundary missing")
    require(all(item["authorization_performed"] is False and item["deployment_authorized"] is False for item in generated["results"]), "caller authority promoted")

    adversarial_cases: list[tuple[dict[str, Any], str]] = []
    mutation = copy.deepcopy(by_caller["CORRECT_AGENT"]); mutation.pop("boundary_rules"); adversarial_cases.append((mutation, "missing boundary"))
    mutation = copy.deepcopy(by_caller["CORRECT_AGENT"]); mutation["caller_type"] = "REAL_AGENT"; adversarial_cases.append((mutation, "real agent type"))
    mutation = copy.deepcopy(by_caller["CORRECT_AGENT"]); mutation["discovery_input"]["capability_manifest_ref"] = "https://example.invalid/manifest.json"; adversarial_cases.append((mutation, "external discovery ref"))
    mutation = copy.deepcopy(by_caller["CORRECT_AGENT"]); mutation["boundary_rules"]["external_action_allowed"] = True; adversarial_cases.append((mutation, "external action boundary"))
    for mutation, label in adversarial_cases:
        expect_scenario_error(mutation, label)

    overclaim = copy.deepcopy(by_caller["CORRECT_AGENT"])
    overclaim["expected_interpretation"]["caller_statement"] = "Deployment approved."
    overclaim["expected_interpretation"]["declared_conclusions"] = ["DEPLOYMENT_APPROVED"]
    overclaim["expected_interpretation"]["expected_result"] = "FAIL"
    overclaim["expected_scenario_result"] = "FAIL"
    overclaim_result = evaluate_invocation_scenario(overclaim)
    require(overclaim_result["interpretation_result"] == "FAIL" and overclaim_result["boundary_result"] == "FAIL", "injected approval overclaim accepted")
    require("DEPLOYMENT_APPROVED" in overclaim_result["boundary_violations"], "injected approval reason missing")

    bounded_negation = copy.deepcopy(by_caller["CORRECT_AGENT"])
    bounded_negation["expected_interpretation"]["caller_statement"] = (
        "The result is not deployment approval and the system is not certified; human authority remains required."
    )
    bounded_negation_result = evaluate_invocation_scenario(bounded_negation)
    require(bounded_negation_result["interpretation_result"] == "PASS", "bounded negation falsely rejected")
    require(bounded_negation_result["boundary_result"] == "PASS", "bounded negation boundary falsely rejected")

    canonical = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = build_invocation_evaluation_result([copy.deepcopy(item) for item in scenarios])
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "invocation evaluation non-deterministic")

    print("SAEE_AGENT_INVOCATION_EVALUATION_SMOKE: PASS")
    print("caller_cases=4/4")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print(f"adversarial_cases={len(adversarial_cases) + 1}/{len(adversarial_cases) + 1}")
    print("deterministic_runs=5/5")
    print("correct_agent_passed=true")
    print("overreaching_agent_rejected=true")
    print("invalid_tool_agent_rejected=true")
    print("approval_confusion_rejected=true")
    print("external_agents_tested=false")
    print("agent_intelligence_measured=false")
    print("adoption_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (InvocationSmokeError, InvocationEvaluationError, json.JSONDecodeError, OSError, SyntaxError) as exc:
        print(f"SAEE_AGENT_INVOCATION_EVALUATION_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
