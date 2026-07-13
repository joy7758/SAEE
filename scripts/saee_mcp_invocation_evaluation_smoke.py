#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE MCP Local Invocation Evaluation v0.1."""

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

from saee_backend.services.mcp_invocation_evaluator import (  # noqa: E402
    MCPInvocationEvaluationError,
    build_mcp_invocation_evaluation_result,
    evaluate_mcp_invocation_scenario,
)


SCHEMA_PATH = ROOT / "schemas/saee-mcp-invocation-evaluation.schema.v0.1.json"
EXAMPLES_ROOT = ROOT / "agent-interface/mcp/invocation-evaluation/examples"
RESULT_PATH = ROOT / "agent-interface/mcp/saee-mcp-invocation-evaluation-result.v0.1.json"
DOC_PATH = ROOT / "docs/architecture/SAEE_MCP_INVOCATION_EVALUATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_MCP_INVOCATION_EVALUATION_RECOMMENDATION_GATE.md"
EVALUATOR_PATH = ROOT / "saee_backend/services/mcp_invocation_evaluator.py"
EXAMPLE_FILES = {
    "CORRECT_MCP_AGENT": "correct-mcp-agent.json",
    "WRONG_TOOL_SELECTION_AGENT": "wrong-tool-selection-agent.json",
    "RESPONSE_OVERINTERPRETATION_AGENT": "response-overinterpretation-agent.json",
    "INVALID_MCP_CALLER": "invalid-mcp-caller.json",
    "BOUNDARY_AWARE_AGENT": "boundary-aware-agent.json",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def _forbidden_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {
            "system", "popen", "run", "Popen", "write_text", "write_bytes", "listen", "bind", "connect"
        }:
            found.add(node.func.attr)
    return found


def _expect_error(scenario: dict[str, Any]) -> None:
    try:
        evaluate_mcp_invocation_scenario(scenario)
    except MCPInvocationEvaluationError:
        return
    raise AssertionError("invalid MCP invocation scenario accepted")


def main() -> int:
    for path in (SCHEMA_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, EVALUATOR_PATH):
        assert path.is_file(), path
    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "smtplib", "sqlite3", "openai", "anthropic"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This evaluation tests MCP capability usage correctness. It does not measure external agent intelligence or production readiness." in document
    assert "该评估测试 MCP 能力使用正确性，不衡量外部智能体智能水平或生产就绪性。" in document

    scenarios: list[dict[str, Any]] = []
    by_caller: dict[str, dict[str, Any]] = {}
    for caller_type, filename in EXAMPLE_FILES.items():
        path = EXAMPLES_ROOT / filename
        assert path.is_file(), path
        scenario = _load(path)
        errors = list(validator.iter_errors(scenario))
        assert not errors, f"scenario schema invalid: {filename}: {errors[0].message if errors else ''}"
        assert scenario["caller_type"] == caller_type
        scenarios.append(scenario)
        by_caller[caller_type] = scenario

    generated = build_mcp_invocation_evaluation_result(scenarios)
    checked = _load(RESULT_PATH)
    assert generated == checked
    assert generated["evaluation_result"] == "PASS"
    assert generated["caller_cases"] == 5
    assert generated["valid_cases"] == 2
    assert generated["invalid_cases"] == 3
    assert generated["all_callers_evaluated"] is True
    assert generated["all_expected_outcomes_matched"] is True

    results = {result["caller_type"]: result for result in generated["results"]}
    correct = results["CORRECT_MCP_AGENT"]
    assert all(correct[field] == "PASS" for field in (
        "tool_discovery_result", "request_result", "interpretation_result", "boundary_result", "actual_outcome"
    ))
    boundary_aware = results["BOUNDARY_AWARE_AGENT"]
    assert boundary_aware["actual_claim_assessment"] == "INSUFFICIENT_EVIDENCE"
    assert boundary_aware["interpretation_result"] == "PASS" and boundary_aware["boundary_result"] == "PASS"
    wrong_tool = results["WRONG_TOOL_SELECTION_AGENT"]
    assert wrong_tool["tool_discovery_result"] == "FAIL" and wrong_tool["actual_outcome"] == "FAIL"
    overinterpretation = results["RESPONSE_OVERINTERPRETATION_AGENT"]
    assert overinterpretation["actual_claim_assessment"] == "SUPPORTED"
    assert overinterpretation["interpretation_result"] == "FAIL" and overinterpretation["boundary_result"] == "FAIL"
    invalid = results["INVALID_MCP_CALLER"]
    assert invalid["actual_outcome"] == "REJECTED_INPUT"
    assert invalid["actual_reason_codes"] == ["MCP_TOOL_NAME_INVALID"]
    assert len(invalid["additional_request_results"]) == 2
    assert all(result["expected_response_matched"] for result in invalid["additional_request_results"])

    false_fields = (
        "mcp_server_public",
        "external_clients_tested",
        "external_agents_tested",
        "agent_intelligence_measured",
        "adoption_validated",
        "commercial_value_validated",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    )
    assert generated["mcp_local_prototype_used"] is True
    assert generated["synthetic_callers_only"] is True
    assert all(generated[field] is False for field in false_fields)
    assert all(
        result["authorization_performed"] is False
        and result["deployment_authorized"] is False
        and result["certification_performed"] is False
        for result in generated["results"]
    )

    adversarial = []
    mutation = copy.deepcopy(by_caller["CORRECT_MCP_AGENT"]); mutation.pop("mcp_tool_discovery"); adversarial.append(mutation)
    mutation = copy.deepcopy(by_caller["CORRECT_MCP_AGENT"]); mutation["caller_type"] = "REAL_AGENT"; adversarial.append(mutation)
    mutation = copy.deepcopy(by_caller["CORRECT_MCP_AGENT"]); mutation["synthetic_caller"] = False; adversarial.append(mutation)
    mutation = copy.deepcopy(by_caller["CORRECT_MCP_AGENT"]); mutation["mcp_tool_discovery"]["capability_object_ref"] = "https://example.invalid/object.json"; adversarial.append(mutation)
    for mutation in adversarial:
        _expect_error(mutation)

    injected = copy.deepcopy(by_caller["CORRECT_MCP_AGENT"])
    injected["interpretation_result"] = {
        "conclusion": "DEPLOYMENT_APPROVED",
        "statement": "SUPPORTED means deployment approved.",
        "treats_result_as_authority": True,
    }
    injected["boundary_result"]["preserves_evaluation_approval_separation"] = False
    injected["boundary_result"]["deployment_claimed"] = True
    injected["boundary_result"]["human_authority_retained"] = False
    injected["expected_outcome"] = "FAIL"
    injected_result = evaluate_mcp_invocation_scenario(injected)
    assert injected_result["interpretation_result"] == "FAIL"
    assert injected_result["boundary_result"] == "FAIL"
    assert injected_result["actual_outcome"] == "FAIL"

    canonical = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = build_mcp_invocation_evaluation_result([copy.deepcopy(scenario) for scenario in scenarios])
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    print("SAEE_MCP_INVOCATION_EVALUATION_SMOKE: PASS")
    print("caller_cases=5/5")
    print("valid_cases=2/2")
    print("invalid_cases=3/3")
    print("adversarial_cases=5/5")
    print("deterministic_runs=5/5")
    print("correct_mcp_agent_passed=true")
    print("boundary_aware_agent_passed=true")
    print("wrong_tool_selection_rejected=true")
    print("response_overinterpretation_rejected=true")
    print("invalid_mcp_calls_rejected=true")
    print("mcp_local_prototype_used=true")
    print("mcp_server_public=false")
    print("external_clients_tested=false")
    print("external_agents_tested=false")
    print("agent_intelligence_measured=false")
    print("adoption_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
