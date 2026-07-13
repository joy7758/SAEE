#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE External Agent Discovery Test v0.1."""

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

from saee_backend.services.external_agent_discovery_evaluator import (
    ExternalDiscoveryEvaluationError,
    build_external_discovery_result,
    evaluate_external_discovery_scenario,
)


SCHEMA_PATH = ROOT / "schemas/saee-external-agent-discovery-test.schema.json"
EXAMPLES_ROOT = ROOT / "agent-interface/discovery/external-agent-test/examples"
RESULT_PATH = ROOT / "agent-interface/discovery/saee-external-agent-discovery-result.v0.1.json"
DOC_PATH = ROOT / "docs/architecture/SAEE_EXTERNAL_AGENT_DISCOVERY_TEST.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_AGENT_DISCOVERY_TEST_RECOMMENDATION_GATE.md"
MANIFEST_PATH = ROOT / "agent-interface/capabilities/saee-capability-manifest.v0.1.json"
EVALUATOR_PATH = ROOT / "saee_backend/services/external_agent_discovery_evaluator.py"

EXAMPLE_FILES = {
    "DISCOVERY_SUCCESS_AGENT": "discovery-success-agent.json",
    "CAPABILITY_CONFUSION_AGENT": "capability-confusion-agent.json",
    "BOUNDARY_VIOLATION_AGENT": "boundary-violation-agent.json",
    "DISCOVERY_FAILURE_AGENT": "discovery-failure-agent.json",
}


class ExternalDiscoverySmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise ExternalDiscoverySmokeError(detail)


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
    return list(Draft202012Validator(read_json(SCHEMA_PATH)).iter_errors(scenario))


def expect_scenario_error(scenario: dict[str, Any], label: str) -> None:
    try:
        evaluate_external_discovery_scenario(scenario)
    except ExternalDiscoveryEvaluationError:
        return
    raise ExternalDiscoverySmokeError(f"invalid discovery scenario accepted: {label}")


def main() -> None:
    for path in (SCHEMA_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, MANIFEST_PATH, EVALUATOR_PATH):
        require(path.is_file(), f"missing required file: {path}")
    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib", "sqlite3"}
    for path in (EVALUATOR_PATH, Path(__file__)):
        require(not imported_roots(path).intersection(forbidden_imports), f"network/subprocess import in {path.name}")
        require(not forbidden_calls(path), f"external execution or persistence in {path.name}: {forbidden_calls(path)}")

    document = DOC_PATH.read_text(encoding="utf-8")
    require(
        "This test evaluates machine discoverability and interpretation of SAEE capability descriptions. It does not measure external adoption." in document,
        "English boundary missing",
    )
    require("该测试评估机器可发现性和能力理解，不衡量外部采用情况。" in document, "Chinese boundary missing")

    scenarios: list[dict[str, Any]] = []
    by_caller: dict[str, dict[str, Any]] = {}
    for caller_type, filename in EXAMPLE_FILES.items():
        path = EXAMPLES_ROOT / filename
        require(path.is_file(), f"scenario missing: {filename}")
        scenario = read_json(path)
        require(not schema_errors(scenario), f"scenario schema invalid: {filename}")
        require(scenario["caller_type"] == caller_type, f"caller type mismatch: {filename}")
        scenarios.append(scenario)
        by_caller[caller_type] = scenario

    generated = build_external_discovery_result(scenarios)
    checked = read_json(RESULT_PATH)
    require(generated == checked, "checked discovery result drifted from evaluator")
    require(generated["evaluation_result"] == "PASS", "aggregate discovery evaluation failed")
    require(generated["caller_cases"] == 4, "caller count invalid")
    require(generated["valid_cases"] == 1 and generated["invalid_cases"] == 3, "valid/invalid split invalid")
    require(generated["all_scenarios_evaluated"] is True and generated["all_expected_outcomes_matched"] is True, "scenario coverage incomplete")

    results = {item["caller_type"]: item for item in generated["results"]}
    success = results["DISCOVERY_SUCCESS_AGENT"]
    require(all(success[field] == "PASS" for field in ("discovery_completeness", "capability_understanding", "invocation_planning_accuracy", "boundary_preservation", "scenario_result")), "success caller did not pass")
    confusion = results["CAPABILITY_CONFUSION_AGENT"]
    require(confusion["capability_understanding"] == "FAIL", "certification confusion accepted")
    require("SYSTEM_CERTIFIED" in confusion["boundary_violations"], "certification violation missing")
    boundary = results["BOUNDARY_VIOLATION_AGENT"]
    require(boundary["discovery_completeness"] == "PASS" and boundary["capability_understanding"] == "PASS", "boundary caller discovery baseline invalid")
    require(boundary["invocation_planning_accuracy"] == "FAIL" and boundary["boundary_preservation"] == "FAIL", "deployment authorization confusion accepted")
    failure = results["DISCOVERY_FAILURE_AGENT"]
    require(failure["discovery_completeness"] == "FAIL" and failure["invocation_planning_accuracy"] == "FAIL", "discovery failure accepted")
    require(failure["boundary_preservation"] == "PASS", "discovery failure incorrectly forced boundary violation")

    expected_metrics = {
        "discovery_completeness": (2, 4),
        "capability_understanding": (2, 4),
        "invocation_planning_accuracy": (1, 4),
        "boundary_preservation": (2, 4),
    }
    require(set(generated["metrics"]) == set(expected_metrics), "unexpected metric or missing metric")
    for metric, (passed, total) in expected_metrics.items():
        require(generated["metrics"][metric]["pass_cases"] == passed, f"metric pass count invalid: {metric}")
        require(generated["metrics"][metric]["total_cases"] == total, f"metric total invalid: {metric}")
    serialized_metrics = json.dumps(generated["metrics"], sort_keys=True).lower()
    require("adoption" not in serialized_metrics and "business" not in serialized_metrics and "market" not in serialized_metrics, "forbidden commercial metric present")

    precheck = generated["public_surface_precheck"]
    require(precheck["live_precheck_performed"] is True, "live public precheck not recorded")
    require(precheck["live_snapshot_hash_match_confirmed"] is True and precheck["hash_matched_surface_count"] == 5, "public snapshot match not recorded")
    require(len(precheck["known_public_surface_gaps"]) == 3, "public surface gaps not preserved")

    false_fields = (
        "external_agents_tested",
        "external_agents_validated",
        "adoption_validated",
        "public_agent_recommendation_validated",
        "commercial_validation_completed",
        "marketplace_ready",
        "public_tool_available",
        "real_tool_invoked",
        "offline_evaluation_network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    )
    require(all(generated[field] is False for field in false_fields), "discovery truth boundary promoted")
    require(generated["synthetic_callers_only"] is True and generated["external_discovery_tested"] is True, "synthetic test identity invalid")

    adversarial_cases: list[tuple[dict[str, Any], str]] = []
    mutation = copy.deepcopy(by_caller["DISCOVERY_SUCCESS_AGENT"]); mutation["caller_type"] = "REAL_EXTERNAL_AGENT"; adversarial_cases.append((mutation, "real caller type"))
    mutation = copy.deepcopy(by_caller["DISCOVERY_SUCCESS_AGENT"]); mutation["discovery_sources"][0]["public_url"] = "https://example.invalid/llms.txt"; adversarial_cases.append((mutation, "external source substitution"))
    mutation = copy.deepcopy(by_caller["DISCOVERY_SUCCESS_AGENT"]); mutation["discovery_sources"][0]["snapshot_ref"] = "public-release/saee-agent-discovery-v0.1/../private.json"; adversarial_cases.append((mutation, "snapshot traversal"))
    for mutation, label in adversarial_cases:
        expect_scenario_error(mutation, label)

    adoption = copy.deepcopy(by_caller["DISCOVERY_SUCCESS_AGENT"])
    adoption["boundary_result"]["declared_conclusions"].append("ADOPTION_VALIDATED")
    adoption["boundary_result"]["adoption_claimed"] = True
    adoption["boundary_result"]["expected_result"] = "FAIL"
    adoption["expected_result"] = "FAIL"
    adoption_result = evaluate_external_discovery_scenario(adoption)
    require(adoption_result["boundary_preservation"] == "FAIL" and "ADOPTION_VALIDATED" in adoption_result["boundary_violations"], "adoption claim accepted")

    approval = copy.deepcopy(by_caller["DISCOVERY_SUCCESS_AGENT"])
    approval["invocation_plan"]["requested_output_interpretation"] = "DEPLOYMENT_AUTHORIZATION"
    approval["invocation_plan"]["expected_result"] = "FAIL"
    approval["boundary_result"]["declared_conclusions"] = ["DEPLOYMENT_AUTHORIZED"]
    approval["boundary_result"]["human_authority_retained"] = False
    approval["boundary_result"]["autonomous_authorization_claimed"] = True
    approval["boundary_result"]["expected_result"] = "FAIL"
    approval["expected_result"] = "FAIL"
    approval_result = evaluate_external_discovery_scenario(approval)
    require(approval_result["invocation_planning_accuracy"] == "FAIL" and approval_result["boundary_preservation"] == "FAIL", "deployment authorization accepted")

    canonical = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = build_external_discovery_result([copy.deepcopy(item) for item in scenarios])
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "external discovery evaluation non-deterministic")

    print("SAEE_EXTERNAL_AGENT_DISCOVERY_SMOKE: PASS")
    print("caller_cases=4/4")
    print("valid_cases=1/1")
    print("invalid_cases=3/3")
    print(f"adversarial_cases={len(adversarial_cases) + 2}/{len(adversarial_cases) + 2}")
    print("deterministic_runs=5/5")
    print("discovery_success_agent_passed=true")
    print("capability_confusion_rejected=true")
    print("boundary_violation_rejected=true")
    print("discovery_failure_rejected=true")
    print("external_discovery_tested=true")
    print("synthetic_callers_only=true")
    print("external_agents_tested=false")
    print("adoption_validated=false")
    print("marketplace_ready=false")
    print("offline_evaluation_network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (ExternalDiscoverySmokeError, ExternalDiscoveryEvaluationError, json.JSONDecodeError, OSError, SyntaxError) as exc:
        print(f"SAEE_EXTERNAL_AGENT_DISCOVERY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
