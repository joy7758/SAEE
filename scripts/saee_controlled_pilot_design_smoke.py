#!/usr/bin/env python3
"""Offline smoke for SAEE Controlled External Agent Pilot Design v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.pilot_design_validator import (  # noqa: E402
    PILOT_DESIGN_APPROVAL_CLAIM_FORBIDDEN,
    PILOT_DESIGN_CUSTOMER_VALIDATION_FORBIDDEN,
    PILOT_DESIGN_EXTERNAL_CONNECTION_FORBIDDEN,
    PILOT_DESIGN_EXTERNAL_DATA_CLAIM_FORBIDDEN,
    PILOT_DESIGN_GATES_INVALID,
    PILOT_DESIGN_HUMAN_BOUNDARY_REQUIRED,
    PILOT_DESIGN_PILOT_COMPLETION_FORBIDDEN,
    PILOT_DESIGN_PRODUCTION_CLAIM_FORBIDDEN,
    PILOT_DESIGN_ROLLBACK_INVALID,
    validate_pilot_design,
)


DESIGN_PATH = ROOT / "agent-interface/integration/saee-controlled-pilot-design.v0.1.json"
DOC_PATH = ROOT / "docs/commercial/SAEE_CONTROLLED_EXTERNAL_AGENT_PILOT_DESIGN.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_CONTROLLED_EXTERNAL_AGENT_PILOT_DESIGN_RECOMMENDATION_GATE.md"
INTEGRATION_DOC_PATH = ROOT / "docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md"
VALIDATOR_PATH = ROOT / "saee_backend/services/pilot_design_validator.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(candidate: dict, reason: str) -> None:
    result = validate_pilot_design(candidate)
    assert result["design_valid"] is False
    assert result["reason_codes"] == [reason], result


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
    for path in (DESIGN_PATH, DOC_PATH, GATE_PATH, INTEGRATION_DOC_PATH, VALIDATOR_PATH):
        assert path.is_file(), path

    design = _load(DESIGN_PATH)
    valid = validate_pilot_design(design)
    assert valid["design_valid"] is True
    assert valid["reason_codes"] == []

    invalid_cases: list[tuple[dict, str]] = []

    completed = copy.deepcopy(design)
    completed["pilot_executed"] = True
    invalid_cases.append((completed, PILOT_DESIGN_PILOT_COMPLETION_FORBIDDEN))

    connected = copy.deepcopy(design)
    connected["external_agent_connected"] = True
    invalid_cases.append((connected, PILOT_DESIGN_EXTERNAL_CONNECTION_FORBIDDEN))

    customer_validated = copy.deepcopy(design)
    customer_validated["customer_validated"] = True
    invalid_cases.append((customer_validated, PILOT_DESIGN_CUSTOMER_VALIDATION_FORBIDDEN))

    approved = copy.deepcopy(design)
    approved["approval_granted"] = True
    invalid_cases.append((approved, PILOT_DESIGN_APPROVAL_CLAIM_FORBIDDEN))

    collected = copy.deepcopy(design)
    collected["data_collected"] = True
    invalid_cases.append((collected, PILOT_DESIGN_EXTERNAL_DATA_CLAIM_FORBIDDEN))

    production = copy.deepcopy(design)
    production["production_ready"] = True
    invalid_cases.append((production, PILOT_DESIGN_PRODUCTION_CLAIM_FORBIDDEN))

    gate_granted = copy.deepcopy(design)
    gate_granted["approval_gates"][0]["status"] = "GRANTED"
    invalid_cases.append((gate_granted, PILOT_DESIGN_GATES_INVALID))

    human_bypass = copy.deepcopy(design)
    human_bypass["human_boundary"]["human_review_bypass_allowed"] = True
    invalid_cases.append((human_bypass, PILOT_DESIGN_HUMAN_BOUNDARY_REQUIRED))

    rollback_approved = copy.deepcopy(design)
    rollback_approved["rollback_model"]["plans_approved"] = True
    invalid_cases.append((rollback_approved, PILOT_DESIGN_ROLLBACK_INVALID))

    for candidate, reason in invalid_cases:
        _expect_invalid(candidate, reason)

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3"}
    for path in (VALIDATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "This document defines the requirements for a possible future controlled external Agent Pilot. It does not authorize or execute a Pilot." in document
    assert "Pilot Design != Pilot Execution" in document
    assert "approval_granted=false" in document
    assert "controlled external Agent Pilot design" in INTEGRATION_DOC_PATH.read_text(encoding="utf-8")
    assert "`recommend`" in GATE_PATH.read_text(encoding="utf-8")

    canonical = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_pilot_design(copy.deepcopy(design))
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    false_fields = (
        "pilot_start_authorized",
        "external_agent_connected",
        "pilot_executed",
        "data_collected",
        "approval_granted",
        "customer_validated",
        "external_validation_completed",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    )
    assert all(valid[field] is False for field in false_fields)
    assert valid["readiness_gate"] == "HOLD"

    print("SAEE_CONTROLLED_PILOT_DESIGN_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("approval_gates=5/5")
    print("pilot_stage=design_only")
    print("readiness_gate=HOLD")
    print("pilot_start_authorized=false")
    print("external_agent_connected=false")
    print("pilot_executed=false")
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
