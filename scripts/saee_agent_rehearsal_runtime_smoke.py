#!/usr/bin/env python3
"""Offline deterministic smoke for the SAEE Agent Rehearsal Runtime MVP."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import (
    RehearsalRuntimeError,
    _validate_scenario,
    run_task,
)


SCENARIO_DIR = ROOT / "agent-interface/rehearsal/scenarios"
SCENARIO_SCHEMA = ROOT / "agent-interface/rehearsal/saee-agent-rehearsal-scenario.v0.1.schema.json"
RUN_SCHEMA = ROOT / "agent-interface/rehearsal/saee-agent-rehearsal-run.v0.1.schema.json"
SERVICE = ROOT / "saee_backend/services/agent_rehearsal_runtime.py"
CLI = ROOT / "scripts/saee_agent_rehearsal.py"
DOC = ROOT / "docs/architecture/SAEE_AGENT_REHEARSAL_RUNTIME_MVP.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_REHEARSAL_RUNTIME_RECOMMENDATION_GATE.md"

EXPECTED = {
    "baseline-metadata-inspection.json": ("completed", "allow"),
    "tool-timeout-abstention.json": ("abstained", "allow"),
    "instruction-conflict-refusal.json": ("refused", "deny"),
}


class RehearsalSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise RehearsalSmokeError(detail)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root invalid: {path}")
    return value


def digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


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
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        if isinstance(node.func, ast.Attribute) and node.func.attr in {"run", "Popen", "system", "popen", "urlopen", "connect"}:
            found.add(node.func.attr)
    return found


def expect_invalid(scenario: dict[str, Any], label: str) -> None:
    try:
        _validate_scenario(scenario)
    except (RehearsalRuntimeError, ValueError):
        return
    raise RehearsalSmokeError(f"invalid scenario accepted: {label}")


def main() -> None:
    for path in (SCENARIO_SCHEMA, RUN_SCHEMA, SERVICE, CLI, DOC, GATE):
        require(path.is_file(), f"required file missing: {path}")

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(SERVICE).intersection(forbidden_imports), "service imports external execution or network module")
    require(not forbidden_calls(SERVICE), "service contains dynamic or external execution call")

    scenario_validator = Draft202012Validator(load(SCENARIO_SCHEMA), format_checker=FormatChecker())
    run_validator = Draft202012Validator(load(RUN_SCHEMA), format_checker=FormatChecker())
    results: dict[str, dict[str, Any]] = {}
    for filename, (disposition, decision) in EXPECTED.items():
        path = SCENARIO_DIR / filename
        scenario_validator.validate(load(path))
        result = run_task(path)
        run_validator.validate(result)
        require(result["agent_disposition"] == disposition, f"disposition mismatch: {filename}")
        require(result["policy_decision"] == decision, f"policy mismatch: {filename}")
        require(result["trace"]["trace_digest"] == digest(result["trace"]["events"]), f"trace digest mismatch: {filename}")
        require(result["evidence_export"]["trace_digest"] == result["trace"]["trace_digest"], f"evidence export unbound: {filename}")
        truth = result["truth_boundary"]
        require(truth["local_rehearsal_runtime_executed"] is True, "local Runtime execution missing")
        require(truth["fixed_internal_agent_executed"] is True, "internal Agent execution missing")
        for field in ("real_external_agent_executed", "external_tool_executed", "network_accessed", "subprocess_started", "customer_data_used", "evidence_established", "readiness_decision_made", "deployment_authorized", "production_ready"):
            require(truth[field] is False, f"truth boundary promoted: {filename}:{field}")
        results[filename] = result

    base = load(SCENARIO_DIR / "baseline-metadata-inspection.json")
    invalid: list[tuple[dict[str, Any], str]] = []
    item = copy.deepcopy(base); item["sandbox"]["network_allowed"] = True; invalid.append((item, "network enabled"))
    item = copy.deepcopy(base); item["sandbox"]["subprocess_allowed"] = True; invalid.append((item, "subprocess enabled"))
    item = copy.deepcopy(base); item["sandbox"]["filesystem_write_allowed"] = True; invalid.append((item, "filesystem write enabled"))
    item = copy.deepcopy(base); item["agent_adapter"]["synthetic"] = False; invalid.append((item, "external adapter"))
    item = copy.deepcopy(base); item["expected_outcome"]["external_effect_expected"] = True; invalid.append((item, "external effect"))
    item = copy.deepcopy(base); item["truth_boundary"]["production_ready"] = True; invalid.append((item, "production overclaim"))
    item = copy.deepcopy(base); item["agent_adapter"]["adapter_type"] = "dynamic_plugin"; invalid.append((item, "dynamic adapter"))
    for item, label in invalid:
        expect_invalid(item, label)

    try:
        run_task(ROOT / "README.md")
    except RehearsalRuntimeError as exc:
        require(exc.code == "REHEARSAL_SCENARIO_OUTSIDE_ALLOWLIST", "outside path reason code unstable")
    else:
        raise RehearsalSmokeError("outside-allowlist path accepted")

    canonical = {name: json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")) for name, result in results.items()}
    for _ in range(5):
        for filename in EXPECTED:
            repeated = run_task(SCENARIO_DIR / filename)
            require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical[filename], f"non-deterministic run: {filename}")

    doc = DOC.read_text(encoding="utf-8")
    for marker in ("run_task()", "real_external_agent_executed=false", "evaluate_agent_run_available=false", "Evidence Export"):
        require(marker in doc, f"documentation marker missing: {marker}")

    print("SAEE_AGENT_REHEARSAL_RUNTIME_SMOKE: PASS")
    print("scenario_cases=3/3")
    print("runtime_runs=3/3")
    print(f"invalid_cases={len(invalid) + 1}/{len(invalid) + 1}")
    print("deterministic_runs=5/5")
    print("trace_digest_bindings=3/3")
    print("evidence_export_bindings=3/3")
    print("local_rehearsal_runtime_executed=true")
    print("fixed_internal_agent_executed=true")
    print("real_external_agent_executed=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("evaluate_agent_run_available=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (RehearsalSmokeError, RehearsalRuntimeError, json.JSONDecodeError, ValueError, KeyError) as exc:
        print(f"SAEE_AGENT_REHEARSAL_RUNTIME_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
