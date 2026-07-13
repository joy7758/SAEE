#!/usr/bin/env python3
"""Offline smoke for SAEE Controlled Pilot Simulation v0.1."""

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

from saee_backend.services.pilot_simulation_evaluator import (  # noqa: E402
    evaluate_pilot_simulation,
    validate_simulation_truth_claims,
)
from saee_backend.services.pilot_simulator import simulate_transition  # noqa: E402


SCHEMA_PATH = ROOT / "agent-interface/integration/saee-pilot-state-machine.schema.v0.1.json"
GATE_MODEL_PATH = ROOT / "agent-interface/integration/pilot-gates.v0.1.json"
SCENARIO_DIR = ROOT / "agent-interface/integration/pilot-simulation"
RESULT_PATH = ROOT / "agent-interface/integration/saee-controlled-pilot-simulation-result.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_CONTROLLED_PILOT_SIMULATION.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CONTROLLED_PILOT_SIMULATION_RECOMMENDATION_GATE.md"
DESIGN_PATH = ROOT / "docs/commercial/SAEE_CONTROLLED_EXTERNAL_AGENT_PILOT_DESIGN.md"
SIMULATOR_PATH = ROOT / "saee_backend/services/pilot_simulator.py"
EVALUATOR_PATH = ROOT / "saee_backend/services/pilot_simulation_evaluator.py"

EXPECTED_SCENARIOS = {
    "COMPLETE_APPROVAL_PATH": ("PASS", "PILOT_ACTIVE", "NONE", "NOT_REQUIRED"),
    "MISSING_SECURITY_GATE": ("BLOCK", "TECHNICAL_READY", "MISSING_SECURITY_GATE", "NOT_REQUIRED"),
    "DATA_BOUNDARY_VIOLATION": ("STOP", "PILOT_TERMINATED", "DATA_BOUNDARY_VIOLATION", "COMPLETED"),
    "SECRET_EXPOSURE_DURING_PILOT": ("IMMEDIATE_TERMINATION", "PILOT_TERMINATED", "SECRET_EXPOSURE", "COMPLETED"),
    "NORMAL_TERMINATION": ("PASS", "PILOT_TERMINATED", "NORMAL_TERMINATION", "COMPLETED"),
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


def main() -> int:
    for path in (SCHEMA_PATH, GATE_MODEL_PATH, RESULT_PATH, DOC_PATH, GATE_PATH, DESIGN_PATH, SIMULATOR_PATH, EVALUATOR_PATH):
        assert path.is_file(), path

    schema = _load(SCHEMA_PATH)
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema)
    scenario_paths = sorted(SCENARIO_DIR.glob("*.json"))
    assert len(scenario_paths) == 5

    scenarios = [_load(path) for path in scenario_paths]
    results: list[dict] = []
    for scenario in scenarios:
        errors = list(validator.iter_errors(scenario))
        assert not errors, [error.message for error in errors]
        result = evaluate_pilot_simulation(scenario)
        expected = EXPECTED_SCENARIOS[scenario["scenario_type"]]
        actual = (
            result["simulation_result"],
            result["current_state"],
            result["stop_reason"],
            result["cleanup_result"],
        )
        assert actual == expected, (scenario["scenario_type"], actual, expected)
        assert validate_simulation_truth_claims(result)["valid"] is True
        results.append(result)

    valid_cases = sum(result["simulation_result"] == "PASS" for result in results)
    invalid_cases = len(results) - valid_cases
    assert valid_cases == 2
    assert invalid_cases == 3

    complete = next(item for item in scenarios if item["scenario_type"] == "COMPLETE_APPROVAL_PATH")
    skip = copy.deepcopy(complete)
    skip["requested_transitions"].remove("SECURITY_READY")
    skip_result = evaluate_pilot_simulation(skip)
    assert skip_result["simulation_result"] == "BLOCK"
    assert skip_result["reason_codes"] == ["SIMULATION_MANDATORY_GATE_SKIP_REJECTED"]

    fake_reference = copy.deepcopy(complete)
    fake_reference["gate_states"]["TECHNICAL_READINESS"]["approval_reference"] = "real:approval:unsupported"
    fake_reference_result = evaluate_pilot_simulation(fake_reference)
    assert fake_reference_result["simulation_result"] == "BLOCK"

    normal = next(item for item in scenarios if item["scenario_type"] == "NORMAL_TERMINATION")
    incomplete_cleanup = copy.deepcopy(normal)
    incomplete_cleanup["closure_actions"]["revoke_access"] = False
    incomplete_cleanup_result = evaluate_pilot_simulation(incomplete_cleanup)
    assert incomplete_cleanup_result["simulation_result"] == "STOP"
    assert incomplete_cleanup_result["cleanup_result"] == "PENDING"

    result_document = _load(RESULT_PATH)
    truth = validate_simulation_truth_claims(result_document)
    assert truth["valid"] is True, truth
    assert result_document["scenario_cases"] == 5
    assert result_document["valid_cases"] == 2
    assert result_document["invalid_cases"] == 3
    assert result_document["recommended_next_pr"] == "SAEE External Agent Pilot Readiness Review v0.1"

    invalid_claim_fields = (
        "external_pilot_executed",
        "approval_granted",
        "customer_validated",
        "data_collected",
        "external_agent_connected",
        "production_ready",
    )
    for field in invalid_claim_fields:
        candidate = copy.deepcopy(result_document)
        candidate[field] = True
        invalid = validate_simulation_truth_claims(candidate)
        assert invalid["valid"] is False
        assert invalid["reason_codes"] == [f"SIMULATION_REAL_WORLD_CLAIM_FORBIDDEN:{field}"]

    gate_model = _load(GATE_MODEL_PATH)
    assert gate_model["simulation_only"] is True
    assert gate_model["all_gates_approved"] is False
    assert gate_model["approval_granted"] is False
    assert gate_model["pilot_start_authorized"] is False
    assert len(gate_model["gates"]) == 5
    assert all(gate["status"] == "NOT_READY" for gate in gate_model["gates"])
    assert all(gate["evidence_reference"] is None and gate["approval_reference"] is None for gate in gate_model["gates"])

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (SIMULATOR_PATH, EVALUATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This simulation validates pilot governance logic. It does not execute an external pilot." in document
    assert "该模拟验证 Pilot 治理逻辑，不执行真实外部 Pilot。" in document
    assert "Controlled Pilot Simulation Reference" in DESIGN_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = [json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for result in results]
    for _ in range(5):
        repeated = [
            json.dumps(evaluate_pilot_simulation(copy.deepcopy(scenario)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            for scenario in scenarios
        ]
        assert repeated == canonical

    direct_skip = simulate_transition("DESIGN_ONLY", "SECURITY_READY", complete["gate_states"])
    assert direct_skip["transition_allowed"] is False
    assert direct_skip["reason_code"] == "SIMULATION_MANDATORY_GATE_SKIP_REJECTED"

    print("SAEE_CONTROLLED_PILOT_SIMULATION_SMOKE: PASS")
    print("scenario_cases=5/5")
    print("valid_cases=2/2")
    print("invalid_cases=3/3")
    print("adversarial_cases=3/3")
    print("invalid_claim_cases=6/6")
    print("deterministic_runs=5/5")
    print("mandatory_gate_skipping_rejected=true")
    print("fail_closed_validated=true")
    print("normal_termination_closure_complete=true")
    print("external_pilot_executed=false")
    print("external_agent_connected=false")
    print("customer_data_used=false")
    print("data_collected=false")
    print("approval_granted=false")
    print("customer_validated=false")
    print("external_validation_completed=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
