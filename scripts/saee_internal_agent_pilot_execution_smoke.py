#!/usr/bin/env python3
"""Offline adversarial smoke for SAEE Internal Agent Pilot Execution v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.internal_agent_pilot_execution_validator import (  # noqa: E402
    MANIFEST_PATH,
    OBSERVATION_DIR,
    RESULT_PATH,
    validate_execution_artifacts,
    validate_execution_repository,
)


SERVICE_PATH = ROOT / "saee_backend/services/internal_agent_pilot_execution_validator.py"
REPORT_DIR = ROOT / "docs/pilot/results"
EXPECTED_REPORTS = {
    "SAEE_INTERNAL_PILOT_CODING_REPORT.md",
    "SAEE_INTERNAL_PILOT_RESEARCH_REPORT.md",
    "SAEE_INTERNAL_PILOT_AUTOMATION_REPORT.md",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    valid = validate_execution_repository()
    assert valid["valid"] is True, valid
    assert valid["runs_completed"] >= 3
    assert valid["observation_exists"] is True and valid["evaluation_completed"] is True and valid["evidence_boundary"] is True
    assert all(valid[key] is False for key in ("external_validation", "customer_data", "production_execution", "external_world_actions", "adoption_validated", "production_ready"))

    manifest = load(MANIFEST_PATH)
    result = load(RESULT_PATH)
    observations = [load(path) for path in sorted(OBSERVATION_DIR.glob("*.json"))]
    assert len(manifest["runs"]) == 3 and len(observations) == 3
    assert {path.name for path in REPORT_DIR.glob("*.md")} == EXPECTED_REPORTS
    assert result["runs_completed"] == 3
    assert {item["recommendation"] for item in result["recommendations"]} <= {"CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"}
    assert result["reliability_summary"] == {"observed_pass": 2, "observed_partial": 1, "observed_fail": 0, "direct_codex_evaluation_supported": False, "projection_evaluations_completed": 3}
    assert result["evidence_summary"] == {"pass": 3, "fail": 0, "accountability_claims_established": 0}

    invalid: list[tuple[dict, dict, list[dict]]] = []
    for key in ("external_validation", "customer_data", "production_execution", "external_world_actions", "adoption_validated", "production_ready"):
        value = copy.deepcopy(manifest); value["truth_boundary"][key] = True; invalid.append((value, copy.deepcopy(result), copy.deepcopy(observations)))
    for key in ("external_validation", "customer_data", "production_execution", "external_world_actions", "adoption_validated", "production_ready"):
        values = copy.deepcopy(observations); values[0]["truth_boundary"][key] = True; invalid.append((copy.deepcopy(manifest), copy.deepcopy(result), values))
    for key in ("chain_of_thought", "private_reasoning", "hidden_reasoning", "secret", "credential", "private_model_state"):
        values = copy.deepcopy(observations); values[0][key] = "forbidden"; invalid.append((copy.deepcopy(manifest), copy.deepcopy(result), values))
    for key in ("external_validation", "customer_data", "production_execution", "external_world_actions", "adoption_validated", "production_ready"):
        value = copy.deepcopy(result); value["truth_boundary"][key] = True; invalid.append((copy.deepcopy(manifest), value, copy.deepcopy(observations)))
    values = copy.deepcopy(observations); values[0]["recommendation"] = "DEPLOY"; invalid.append((copy.deepcopy(manifest), copy.deepcopy(result), values))
    values = copy.deepcopy(observations); values[0]["evidence_findings"]["result"] = "FAIL"; invalid.append((copy.deepcopy(manifest), copy.deepcopy(result), values))
    values = copy.deepcopy(observations); values[0]["reliability_findings"]["evaluation_mode"] = "DIRECT_CODEX_ASSESSMENT"; invalid.append((copy.deepcopy(manifest), copy.deepcopy(result), values))
    value = copy.deepcopy(result); value["runs_completed"] = 2; invalid.append((copy.deepcopy(manifest), value, copy.deepcopy(observations)))
    assert len(invalid) >= 20
    assert all(validate_execution_artifacts(m, r, o, require_reports=False)["valid"] is False for m, r, o in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_execution_repository(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE_PATH.read_text(encoding="utf-8"))
    imports: set[str] = set()
    imported_modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0]); imported_modules.add(node.module)
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib", "importlib"} & imports)
    assert any(module.endswith("agent_run_capability") for module in imported_modules)
    assert any(module.endswith("evidence_adequacy") for module in imported_modules)

    print("SAEE_INTERNAL_AGENT_PILOT_EXECUTION_SMOKE: PASS")
    print("runs=3/3")
    print("observations=3/3")
    print("reports=3/3")
    print("recommendations_valid=true")
    print("evidence_evaluations=3/3")
    print("reliability_projection_evaluations=3/3")
    print("direct_codex_evaluation_supported=false")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("internal_agent_pilot=true")
    print("pilot_executed=true")
    print("real_internal_execution=true")
    print("external_validation=false")
    print("customer_data=false")
    print("production_execution=false")
    print("external_world_actions=false")
    print("adoption_validated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
