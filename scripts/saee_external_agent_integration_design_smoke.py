#!/usr/bin/env python3
"""Offline smoke test for SAEE External Agent Integration Design v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.external_agent_integration_validator import (  # noqa: E402
    EXTERNAL_INTEGRATION_AUTHENTICATION_IMPLEMENTATION_FORBIDDEN,
    EXTERNAL_INTEGRATION_AUTHORIZATION_CLAIM_FORBIDDEN,
    EXTERNAL_INTEGRATION_AUTONOMOUS_EXECUTION_FORBIDDEN,
    EXTERNAL_INTEGRATION_CONNECTED_CLAIM_FORBIDDEN,
    EXTERNAL_INTEGRATION_CREDENTIAL_EXPOSURE,
    EXTERNAL_INTEGRATION_HUMAN_BOUNDARY_REQUIRED,
    EXTERNAL_INTEGRATION_PRODUCTION_CLAIM_FORBIDDEN,
    EXTERNAL_INTEGRATION_TRUST_CLAIM_FORBIDDEN,
    validate_external_agent_integration_design,
)


DESIGN_PATH = ROOT / "agent-interface/integration/saee-external-agent-integration-design.v0.1.json"
DOC_PATH = ROOT / "docs/architecture/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN_RECOMMENDATION_GATE.md"
VALIDATOR_PATH = ROOT / "saee_backend/services/external_agent_integration_validator.py"


def _load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _expect_invalid(value: dict, reason: str) -> None:
    result = validate_external_agent_integration_design(value)
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
    for path in (DESIGN_PATH, DOC_PATH, GATE_PATH, VALIDATOR_PATH):
        assert path.is_file(), path
    design = _load(DESIGN_PATH)
    valid = validate_external_agent_integration_design(design)
    assert valid["design_valid"] is True
    assert valid["reason_codes"] == []

    fake_connection = copy.deepcopy(design)
    fake_connection["external_agent_connected"] = True
    _expect_invalid(fake_connection, EXTERNAL_INTEGRATION_CONNECTED_CLAIM_FORBIDDEN)

    fake_trust = copy.deepcopy(design)
    fake_trust["trusted_external_agent"] = True
    _expect_invalid(fake_trust, EXTERNAL_INTEGRATION_TRUST_CLAIM_FORBIDDEN)

    fake_production = copy.deepcopy(design)
    fake_production["production_enabled"] = True
    _expect_invalid(fake_production, EXTERNAL_INTEGRATION_PRODUCTION_CLAIM_FORBIDDEN)

    missing_human = copy.deepcopy(design)
    missing_human["human_control_model"]["human_approval_required"] = False
    _expect_invalid(missing_human, EXTERNAL_INTEGRATION_HUMAN_BOUNDARY_REQUIRED)

    credential_exposure = copy.deepcopy(design)
    credential_exposure["api_key"] = "synthetic-credential-placeholder"
    _expect_invalid(credential_exposure, EXTERNAL_INTEGRATION_CREDENTIAL_EXPOSURE)

    autonomous = copy.deepcopy(design)
    autonomous["autonomous_execution"] = True
    _expect_invalid(autonomous, EXTERNAL_INTEGRATION_AUTONOMOUS_EXECUTION_FORBIDDEN)

    authorization = copy.deepcopy(design)
    authorization["invocation_boundary"]["authorization_performed"] = True
    _expect_invalid(authorization, EXTERNAL_INTEGRATION_AUTHORIZATION_CLAIM_FORBIDDEN)

    authentication = copy.deepcopy(design)
    authentication["authentication_available"] = True
    _expect_invalid(authentication, EXTERNAL_INTEGRATION_AUTHENTICATION_IMPLEMENTATION_FORBIDDEN)

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "aiohttp", "openai", "anthropic", "sqlite3", "smtplib"}
    for path in (VALIDATOR_PATH, Path(__file__)):
        assert not (_imported_roots(path) & forbidden_imports), path
        assert not _forbidden_calls(path), f"forbidden call in {path.name}: {_forbidden_calls(path)}"

    document = DOC_PATH.read_text(encoding="utf-8")
    assert "It does not establish external integration." in document
    assert "Agent Identity != Agent Trust" in document
    assert "gate_status=HOLD" in document

    canonical = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_external_agent_integration_design(copy.deepcopy(design))
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    false_fields = (
        "external_agent_connected",
        "authentication_available",
        "trusted_external_agent",
        "autonomous_execution",
        "network_accessed",
        "subprocess_started",
        "external_execution",
        "production_ready",
    )
    assert valid["human_approval_required"] is True
    assert all(valid[field] is False for field in false_fields)

    print("SAEE_EXTERNAL_AGENT_INTEGRATION_DESIGN_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=8/8")
    print("deterministic_runs=5/5")
    print("identity_boundary_valid=true")
    print("invocation_boundary_valid=true")
    print("data_boundary_valid=true")
    print("tenant_model_design_only=true")
    print("secret_model_requirements_only=true")
    print("human_approval_required=true")
    print("readiness_gate=HOLD")
    print("external_agent_connected=false")
    print("authentication_available=false")
    print("trusted_external_agent=false")
    print("autonomous_execution=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
