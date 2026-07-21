#!/usr/bin/env python3
"""Offline adversarial smoke for the first candidate validation simulation."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.first_external_validation_simulation import (  # noqa: E402
    CANDIDATE_PATH,
    FEEDBACK_PATH,
    run_first_external_validation_simulation,
)
from saee_backend.services.first_external_validation_simulation_validator import validate_simulation_data  # noqa: E402


RESULT_PATH = ROOT / "agent-interface/ecosystem/saee-first-external-validation-simulation-result.v0.1.json"
WORKFLOW = ROOT / "saee_backend/services/first_external_validation_simulation.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_historical_internal_name(value: dict) -> dict:
    """Project the one registered historical narrative field onto the current name."""

    old_name = "evaluate_agent_run"
    new_name = "evaluate_rehearsal_run"
    expected = "evaluate_agent_run delegated through CapabilityMCPAdapter and Capability Runtime."
    serialized = json.dumps(value, ensure_ascii=False, sort_keys=True)
    assert serialized.count(old_name) == 1, "unregistered historical internal-name occurrence"
    observations = value.get("integration_observations")
    assert isinstance(observations, list) and len(observations) > 1, "historical observation pointer missing"
    assert observations[1] == expected, "registered historical observation changed"
    normalized = copy.deepcopy(value)
    normalized["integration_observations"][1] = expected.replace(old_name, new_name, 1)
    return normalized


def main() -> int:
    candidate = load(CANDIDATE_PATH)
    feedback = load(FEEDBACK_PATH)
    checked_in = normalize_historical_internal_name(load(RESULT_PATH))
    generated = run_first_external_validation_simulation()
    assert generated == checked_in
    valid = validate_simulation_data(candidate, feedback, generated)
    assert valid["valid"] is True and valid["candidate_valid"] is True
    assert valid["candidate_type"] == "mcp_agent_developer"
    assert valid["scenario_count"] >= 7 and valid["feedback_record_count"] >= 1
    assert valid["scope_valid"] is True and valid["feedback_valid"] is True
    assert valid["evidence_boundary"] is True and valid["synthetic_only"] is True

    invalid = []
    for field in ("real_identity", "real_company", "real_contact", "external_account"):
        c = copy.deepcopy(candidate); c[field] = "forbidden"; invalid.append((c, copy.deepcopy(feedback), copy.deepcopy(generated)))
    for mutate in (
        lambda c: c.update({"simulation_only": False}),
        lambda c: c.update({"candidate_type": "cloud_platform"}),
        lambda c: c.update({"integration_scope": ["capability_discovery"]}),
    ):
        c = copy.deepcopy(candidate); mutate(c); invalid.append((c, copy.deepcopy(feedback), copy.deepcopy(generated)))
    for field in ("customer_data", "private_prompt", "credentials", "chain_of_thought", "business_confidential_data"):
        f = copy.deepcopy(feedback); f[field] = "forbidden"; invalid.append((copy.deepcopy(candidate), f, copy.deepcopy(generated)))
    f = copy.deepcopy(feedback); f["simulation_only"] = False; invalid.append((copy.deepcopy(candidate), f, copy.deepcopy(generated)))
    for field in ("external_validation", "participant_contact", "real_external_agent", "customer_data", "adoption_validated", "production_ready", "network_accessed", "external_execution"):
        r = copy.deepcopy(generated); r["evidence_boundary"][field] = True; invalid.append((copy.deepcopy(candidate), copy.deepcopy(feedback), r))
    for field in ("real_candidate", "adoption_claim", "customer_claim", "customer_success", "adoption_proof", "market_validation", "production_validation"):
        r = copy.deepcopy(generated); r[field] = True; invalid.append((copy.deepcopy(candidate), copy.deepcopy(feedback), r))
    r = copy.deepcopy(generated); r["scenario_results"][0]["matched_expected"] = False; invalid.append((copy.deepcopy(candidate), copy.deepcopy(feedback), r))
    r = copy.deepcopy(generated); r["scenario_results"].pop(); invalid.append((copy.deepcopy(candidate), copy.deepcopy(feedback), r))
    r = copy.deepcopy(generated); r["feedback_records"] = []; invalid.append((copy.deepcopy(candidate), copy.deepcopy(feedback), r))
    assert len(invalid) >= 20
    assert all(validate_simulation_data(c, f, r)["valid"] is False for c, f, r in invalid)

    baseline = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(run_first_external_validation_simulation(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(WORKFLOW.read_text(encoding="utf-8"))
    imports = set()
    forbidden_direct = {"saee_backend.services.agent_run_capability", "saee_backend.services.evidence_adequacy", "saee_backend.services.capability_runtime.capability_router"}
    direct_evaluator_imports = 0
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
            direct_evaluator_imports += sum(alias.name in forbidden_direct for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
            direct_evaluator_imports += node.module in forbidden_direct
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"} & imports)
    assert direct_evaluator_imports == 0
    assert all(valid[key] is False for key in ("external_validation", "participant_contact", "customer_data", "adoption_validated", "production_ready"))

    print("SAEE_FIRST_EXTERNAL_VALIDATION_SIMULATION_SMOKE: PASS")
    print("candidate_type=mcp_agent_developer")
    print(f"scenario_cases={valid['scenario_count']}/7")
    print(f"feedback_records={valid['feedback_record_count']}/1")
    print("scope_valid=true")
    print("evidence_boundary=true")
    print("synthetic_only=true")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print(f"direct_evaluator_imports={direct_evaluator_imports}")
    print("external_validation=false")
    print("participant_contact=false")
    print("real_external_agent=false")
    print("customer_data=false")
    print("adoption_validated=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
