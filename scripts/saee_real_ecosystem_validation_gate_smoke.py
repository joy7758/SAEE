#!/usr/bin/env python3
"""Offline adversarial smoke for the first real ecosystem validation gate."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.real_ecosystem_validation_entry_gate import evaluate_entry_gate  # noqa: E402
from saee_backend.services.real_ecosystem_validation_gate_validator import (  # noqa: E402
    BLOCKERS_PATH,
    DECISION_PATH,
    FIXTURE_DIR,
    MATRIX_PATH,
    evaluate_fixture,
    validate_gate_artifacts,
    validate_gate_repository,
)


SERVICE_PATHS = [
    ROOT / "saee_backend/services/real_ecosystem_validation_entry_gate.py",
    ROOT / "saee_backend/services/real_ecosystem_validation_gate_validator.py",
]
EXPECTED_FIXTURES = {
    "CURRENT_PREPARED_STATE.json", "MISSING_OPERATION_OWNER.json", "MISSING_DATA_BOUNDARY.json",
    "ALL_REQUIREMENTS_VERIFIED.json", "FAKE_EXTERNAL_APPROVAL.json",
    "FAKE_PARTICIPANT_CONFIRMATION.json", "FAKE_ADOPTION_CLAIM.json",
}


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def assert_no_runtime_escape() -> None:
    forbidden = {"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"}
    for path in SERVICE_PATHS:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".")[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".")[0])
        assert not (imports & forbidden), f"forbidden import in {path.name}: {sorted(imports & forbidden)}"


def main() -> int:
    valid = validate_gate_repository()
    assert valid["valid"] is True, valid
    assert all(valid[key] == "PASS" for key in ("technical_matrix", "candidate_matrix", "risk_matrix", "decision_logic"))
    assert valid["boundary_preserved"] is True

    matrix = load(MATRIX_PATH)
    decision = load(DECISION_PATH)
    blockers = load(BLOCKERS_PATH)
    assert len(matrix["dimensions"]) >= 5
    assert {item["dimension"] for item in matrix["dimensions"]} == {"technical", "candidate", "scope", "risk", "operational"}
    assert decision["decision"] == "HOLD"

    files = {path.name for path in FIXTURE_DIR.glob("*.json")}
    assert files == EXPECTED_FIXTURES
    fixture_results = [evaluate_fixture(path) for path in sorted(FIXTURE_DIR.glob("*.json"))]
    assert all(item["matched_expected"] for item in fixture_results)
    entry_ready = next(item for item in fixture_results if item["fixture_id"] == "ALL_REQUIREMENTS_VERIFIED")
    assert entry_ready["decision"] == "ENTRY_READY"
    assert all(entry_ready[key] is False for key in ("external_validation", "execution_authorized", "validation_started", "participant_contact", "real_candidate", "customer_data", "adoption_validated", "production_ready"))

    conditional = evaluate_entry_gate({
        "fixture_id": "NON_CRITICAL_OPERATIONAL_GAP", "technical_ready": True,
        "candidate_ready": True, "scope_ready": True, "risk_ready": True,
        "operational_ready": False, "all_required_verified": False, "critical_blocker": False,
    })
    assert conditional["decision"] == "CONDITIONAL_READY"

    invalid: list[tuple[dict, dict, dict]] = []
    for field in ("external_validation", "participant_contact", "real_candidate", "customer_data", "adoption_validated", "production_ready", "execution_authorized", "validation_started"):
        d = copy.deepcopy(decision); d["truth_boundary"][field] = True; invalid.append((copy.deepcopy(matrix), d, copy.deepcopy(blockers)))
    for field in ("technical_readiness", "candidate_readiness", "scope_readiness", "risk_readiness", "operational_readiness"):
        d = copy.deepcopy(decision); d[field]["required_checks"] += 1; invalid.append((copy.deepcopy(matrix), d, copy.deepcopy(blockers)))
    for dimension in ("technical", "candidate", "scope", "risk", "operational"):
        m = copy.deepcopy(matrix); next(item for item in m["dimensions"] if item["dimension"] == dimension)["checks"][0]["evidence_ref"] = "missing.json"; invalid.append((m, copy.deepcopy(decision), copy.deepcopy(blockers)))
    d = copy.deepcopy(decision); d["decision"] = "ENTRY_READY"; invalid.append((copy.deepcopy(matrix), d, copy.deepcopy(blockers)))
    d = copy.deepcopy(decision); d["blocking_conditions"] = []; invalid.append((copy.deepcopy(matrix), d, copy.deepcopy(blockers)))
    b = copy.deepcopy(blockers); b["blockers"][0]["severity"] = "URGENT"; invalid.append((copy.deepcopy(matrix), copy.deepcopy(decision), b))
    b = copy.deepcopy(blockers); b["blockers"][0]["status"] = "CLOSED"; invalid.append((copy.deepcopy(matrix), copy.deepcopy(decision), b))
    assert len(invalid) >= 20
    assert all(validate_gate_artifacts(m, d, b)["valid"] is False for m, d, b in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        rerun = validate_gate_repository()
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline
    assert_no_runtime_escape()

    print("SAEE_REAL_ECOSYSTEM_VALIDATION_GATE_SMOKE: PASS")
    print("dimensions=5/5")
    print("fixtures=7/7")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("current_decision=HOLD")
    print("conditional_branch_validated=true")
    print("entry_ready_authorizes_execution=false")
    print("external_validation=false")
    print("participant_contact=false")
    print("real_candidate=false")
    print("customer_data=false")
    print("adoption_validated=false")
    print("production_ready=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
