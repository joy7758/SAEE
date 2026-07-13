#!/usr/bin/env python3
"""Offline adversarial smoke for first ecosystem candidate preparation."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.ecosystem_candidate_preparation_validator import (  # noqa: E402
    MATRIX_PATH,
    PACKAGE_ROOT,
    SUCCESS_PATH,
    validate_candidate_preparation,
    validate_preparation_data,
)


SERVICE = ROOT / "saee_backend/services/ecosystem_candidate_preparation_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    matrix = load(MATRIX_PATH)
    success = load(SUCCESS_PATH)
    feedback = load(PACKAGE_ROOT / "feedback-template.json")
    valid = validate_candidate_preparation()
    assert valid["valid"] is True
    assert valid["candidate_model"] is True and valid["candidate_type_count"] >= 3
    assert all(valid[key] is True for key in ("scope_defined", "success_defined", "feedback_defined", "boundary_defined"))
    assert matrix["candidates"][0]["priority"] == "P0"
    assert matrix["candidates"][0]["candidate"]["candidate_type"] == "mcp_agent_developer"

    invalid = []
    m = copy.deepcopy(matrix); m["candidates"].pop(); invalid.append((m, copy.deepcopy(success), copy.deepcopy(feedback)))
    for index, priority in ((0, "P2"), (1, "P0"), (2, "P1")):
        m = copy.deepcopy(matrix); m["candidates"][index]["priority"] = priority; invalid.append((m, copy.deepcopy(success), copy.deepcopy(feedback)))
    for key in ("candidate_selected", "real_participant_identified", "participant_contact", "external_validation", "customer_validated", "adoption_validated", "production_ready"):
        m = copy.deepcopy(matrix); m["truth_boundary"][key] = True; invalid.append((m, copy.deepcopy(success), copy.deepcopy(feedback)))
    for key in ("external_side_effects", "customer_data_allowed", "private_system_access_allowed", "production_execution_allowed"):
        m = copy.deepcopy(matrix); m["validation_scope_model"][key] = True; invalid.append((m, copy.deepcopy(success), copy.deepcopy(feedback)))
    for forbidden in ("real_participant", "company_name", "contact_completed", "external_validation_completed", "adoption_claim"):
        m = copy.deepcopy(matrix); m[forbidden] = True; invalid.append((m, copy.deepcopy(success), copy.deepcopy(feedback)))
    for forbidden in ("customer_data", "private_prompt", "credentials", "chain_of_thought", "business_confidential_data"):
        f = copy.deepcopy(feedback); f[forbidden] = "forbidden"; invalid.append((copy.deepcopy(matrix), copy.deepcopy(success), f))
    s = copy.deepcopy(success); s["excluded_outcomes"].remove("revenue"); invalid.append((copy.deepcopy(matrix), s, copy.deepcopy(feedback)))
    s = copy.deepcopy(success); s["truth_boundary"]["success_observed"] = True; invalid.append((copy.deepcopy(matrix), s, copy.deepcopy(feedback)))
    f = copy.deepcopy(feedback); f["discovery_feedback"] = "CLEAR"; invalid.append((copy.deepcopy(matrix), copy.deepcopy(success), f))
    assert len(invalid) >= 15
    assert all(validate_preparation_data(m, s, f)["valid"] is False for m, s, f in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_candidate_preparation(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"} & imports)
    assert all(valid[key] is False for key in ("candidate_selected", "external_validation", "participant_contact", "customer_validated", "adoption_validated", "production_ready"))

    print("SAEE_FIRST_ECOSYSTEM_CANDIDATE_PREPARATION_SMOKE: PASS")
    print(f"candidate_types={valid['candidate_type_count']}/3")
    print("highest_priority=mcp_agent_developer")
    print("scope_defined=true")
    print("success_criteria=true")
    print("feedback_schema=true")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("candidate_selected=false")
    print("external_validation=false")
    print("participant_contact=false")
    print("customer_validated=false")
    print("adoption_validated=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
