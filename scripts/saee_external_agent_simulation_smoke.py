#!/usr/bin/env python3
"""Offline smoke test for SAEE External Agent Simulation Prototype v0.1."""

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

from saee_backend.services.external_agent_simulator import (  # noqa: E402
    build_external_agent_simulation_result,
    evaluate_external_agent_simulation,
)


AGENT_SCHEMA_PATH = ROOT / "agent-interface/integration/synthetic-agent.schema.v0.1.json"
TENANT_SCHEMA_PATH = ROOT / "agent-interface/integration/tenant-context.schema.v0.1.json"
SCENARIO_ROOT = ROOT / "agent-interface/integration/simulation"
RESULT_PATH = ROOT / "agent-interface/integration/saee-external-agent-simulation-result.v0.1.json"
DOC_PATH = ROOT / "docs/architecture/SAEE_EXTERNAL_AGENT_SIMULATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_AGENT_SIMULATION_RECOMMENDATION_GATE.md"
SIMULATOR_PATH = ROOT / "saee_backend/services/external_agent_simulator.py"
DEMO_PATH = ROOT / "scripts/saee_external_agent_simulation_demo.py"
SCENARIO_FILES = {
    "TRUST_CONFUSION_AGENT": "trust-confusion-agent.json",
    "PURPOSE_ESCALATION_AGENT": "purpose-escalation-agent.json",
    "TENANT_BOUNDARY_AGENT": "tenant-boundary-agent.json",
    "SECRET_EXPOSURE_AGENT": "secret-exposure-agent.json",
    "CORRECT_EXTERNAL_AGENT": "correct-external-agent.json",
}


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_valid(value: Any, schema_path: Path) -> bool:
    return not list(Draft202012Validator(_load(schema_path)).iter_errors(value))


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


def main() -> int:
    for path in (AGENT_SCHEMA_PATH, TENANT_SCHEMA_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, SIMULATOR_PATH, DEMO_PATH):
        assert path.is_file(), path
    Draft202012Validator.check_schema(_load(AGENT_SCHEMA_PATH))
    Draft202012Validator.check_schema(_load(TENANT_SCHEMA_PATH))

    scenarios: list[dict[str, Any]] = []
    by_type: dict[str, dict[str, Any]] = {}
    for scenario_type, filename in SCENARIO_FILES.items():
        path = SCENARIO_ROOT / filename
        assert path.is_file(), path
        scenario = _load(path)
        assert scenario["scenario_type"] == scenario_type
        assert scenario["synthetic_scenario"] is True
        scenarios.append(scenario)
        by_type[scenario_type] = scenario

    correct = by_type["CORRECT_EXTERNAL_AGENT"]
    assert _schema_valid(correct["agent_identity"], AGENT_SCHEMA_PATH)
    assert _schema_valid(correct["tenant_context"], TENANT_SCHEMA_PATH)
    assert not _schema_valid(by_type["TRUST_CONFUSION_AGENT"]["agent_identity"], AGENT_SCHEMA_PATH)
    assert not _schema_valid(by_type["TENANT_BOUNDARY_AGENT"]["tenant_context"], TENANT_SCHEMA_PATH)

    generated = build_external_agent_simulation_result(scenarios)
    checked = _load(RESULT_PATH)
    assert generated == checked
    assert generated["simulation_result"] == "PASS"
    assert generated["scenario_cases"] == 5
    assert generated["valid_cases"] == 1
    assert generated["invalid_cases"] == 4
    assert generated["all_scenarios_evaluated"] is True
    assert generated["all_expected_outcomes_matched"] is True

    results = {result["scenario_type"]: result for result in generated["results"]}
    assert results["CORRECT_EXTERNAL_AGENT"]["mcp_result"] == "PASS"
    assert results["CORRECT_EXTERNAL_AGENT"]["mcp_claim_assessment"] == "SUPPORTED"
    assert results["TRUST_CONFUSION_AGENT"]["identity_result"] == "FAIL"
    assert "SIMULATION_IDENTITY_TRUST_CONFUSION" in results["TRUST_CONFUSION_AGENT"]["reason_codes"]
    assert results["PURPOSE_ESCALATION_AGENT"]["purpose_result"] == "FAIL"
    assert results["TENANT_BOUNDARY_AGENT"]["tenant_result"] == "FAIL"
    secret = results["SECRET_EXPOSURE_AGENT"]
    assert secret["secret_result"] == "REJECT" and secret["mcp_result"] == "NOT_CALLED"
    assert secret["reason_codes"] == ["SIMULATION_SECRET_EXPOSURE_REJECTED"]

    serialized = json.dumps(generated, ensure_ascii=False, sort_keys=True)
    assert "synthetic-api-key-placeholder" not in serialized
    assert "synthetic-private-key-placeholder" not in serialized
    assert "synthetic-access-token-placeholder" not in serialized

    fake_authentication = copy.deepcopy(correct)
    fake_authentication["agent_identity"]["identity_as_authentication"] = True
    fake_authentication["expected_outcome"] = "FAIL"
    auth_result = evaluate_external_agent_simulation(fake_authentication)
    assert auth_result["actual_outcome"] == "FAIL"
    assert auth_result["identity_result"] == "FAIL"
    assert "SIMULATION_IDENTITY_AUTHENTICATION_CONFUSION" in auth_result["reason_codes"]

    autonomous = copy.deepcopy(correct)
    autonomous["request_intent"]["autonomous_authorization_requested"] = True
    autonomous["expected_outcome"] = "FAIL"
    autonomous_result = evaluate_external_agent_simulation(autonomous)
    assert autonomous_result["actual_outcome"] == "FAIL"
    assert autonomous_result["boundary_result"] == "FAIL"
    assert autonomous_result["mcp_result"] == "NOT_CALLED"

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3", "smtplib"}
    for path in (SIMULATOR_PATH, DEMO_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This simulation evaluates architecture boundaries using synthetic agents. It does not validate external agents." in document
    assert "该模拟使用合成智能体评估架构边界，不验证真实外部智能体。" in document

    canonical = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = build_external_agent_simulation_result([copy.deepcopy(scenario) for scenario in scenarios])
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    false_fields = (
        "external_agents_connected",
        "authentication_available",
        "tenant_runtime_implemented",
        "credentials_stored",
        "external_validation_completed",
        "adoption_validated",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    )
    assert generated["synthetic_agents_only"] is True
    assert all(generated[field] is False for field in false_fields)
    assert all(
        result["identity_authenticated"] is False
        and result["agent_trusted"] is False
        and result["tenant_runtime_used"] is False
        and result["authorization_performed"] is False
        and result["external_action_performed"] is False
        for result in generated["results"]
    )

    print("SAEE_EXTERNAL_AGENT_SIMULATION_SMOKE: PASS")
    print("scenario_cases=5/5")
    print("valid_cases=1/1")
    print("invalid_cases=4/4")
    print("adversarial_cases=2/2")
    print("deterministic_runs=5/5")
    print("correct_external_agent_passed=true")
    print("trust_confusion_rejected=true")
    print("purpose_escalation_rejected=true")
    print("cross_tenant_access_rejected=true")
    print("secret_exposure_rejected=true")
    print("human_gate_bypass_rejected=true")
    print("synthetic_agents_only=true")
    print("external_agents_connected=false")
    print("authentication_available=false")
    print("tenant_runtime_implemented=false")
    print("credentials_stored=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
