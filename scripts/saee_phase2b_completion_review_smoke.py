#!/usr/bin/env python3
"""Offline consistency checks for the Phase 2B completion architecture review."""

from __future__ import annotations

import ast
import copy
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REVIEW_PATH = ROOT / "docs/architecture/SAEE_PHASE2B_COMPLETION_ARCHITECTURE_REVIEW.md"
CHECKLIST_PATH = ROOT / "docs/architecture/SAEE_PHASE2B_COMPLETION_CHECKLIST.md"
RESULT_PATH = ROOT / "agent-interface/architecture/saee-phase2b-completion-review.v0.1.json"

REQUIRED_PHASE2B_PATHS = (
    ROOT / "agent-interface/architecture/saee-synthetic-external-observation.v0.1.schema.json",
    ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json",
    ROOT / "agent-interface/architecture/saee-adapter-provenance-contract.v0.1.schema.json",
    ROOT / "saee_backend/services/synthetic_observation_adapter.py",
    ROOT / "scripts/saee_phase2b_adapter_readiness_gate.py",
    ROOT / "scripts/saee_adapter_provenance_contract_smoke.py",
    ROOT / "scripts/saee_synthetic_observation_adapter_smoke.py",
    ROOT / "docs/architecture/SAEE_PHASE2B_SYNTHETIC_OBSERVATION_ADAPTER.md",
)

FROZEN_HASHES = {
    ROOT / "docs/architecture/FINAL_ARCHITECTURE_SPEC.md": "60f1e8c71172f8f8c214a57bdf2ac2162483e5eccd14b838c226cc89ede649a3",
    ROOT / "agent-interface/architecture/saee-evidence-case.v0.1.schema.json": "e99ece1b5e37291775e344d871d6223089c84bd11065e7ef0f0fcfab353b121e",
    ROOT / "agent-interface/architecture/saee-observation-envelope.v0.1.schema.json": "5e46e58163c14e6e9d7013c227cbc177cade5ec76c67d667fccdbafb9790cdd2",
    ROOT / "agent-interface/architecture/saee-observation-replay-contract.v0.1.schema.json": "aa7fcdcf7908a1f6f2bcd530ba7a8edfab1aa41d32fa964c422680dd36f61db1",
    ROOT / "agent-interface/architecture/saee-replay-evaluation-contract.v0.1.schema.json": "4c2e9c483a26b477163a14296bd5d505b8176cf5c4c242c4c9e2aa46d8aeb30d",
    ROOT / "agent-interface/architecture/saee-evaluation-run-contract.v0.1.schema.json": "80847a94737a88f84a2f4f4c0b266b7b230c177ec01950375aa628bafe4b4a6d",
    ROOT / "agent-interface/architecture/saee-evaluation-run-termination-contract.v0.1.schema.json": "daa79bed6c130a554512890d6039b92337e17b000985d108ce33768434d0d362",
}


class Phase2BCompletionReviewSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise Phase2BCompletionReviewSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_bytes())


def validate_result(result: dict[str, Any]) -> dict[str, Any]:
    require(result.get("saee_phase2b_completion_review_v0_1") is True, "review marker missing")
    require(result.get("review_version") == "0.1" and result.get("phase") == "2B", "review identity invalid")
    require(result.get("status") == "completed_prototype", "completion status invalid")
    require(result.get("architecture_review_status") == "PASS_AND_FREEZE", "architecture status invalid")
    require(result.get("review_scope") == "local_synthetic_observation_ingestion_only", "review scope invalid")
    for field in ("production_ready", "customer_ready", "external_validation_completed", "deployment_authorized", "security_certification_claimed"):
        require(result.get(field) is False, f"unsupported claim: {field}")
    expected_capabilities = {
        "observation_schema",
        "synthetic_adapter",
        "adapter_provenance_binding",
        "snapshot_integrity",
        "fail_closed_handling",
        "boundary_enforcement",
        "reproducibility",
        "documentation",
    }
    capabilities = result.get("capability_status", {})
    require(set(capabilities) == expected_capabilities, "capability set invalid")
    require(all(value == "PASS" for value in capabilities.values()), "capability not PASS")
    boundaries = result.get("boundary_status", {})
    require(boundaries.get("observation_to_evidence") == "NOT_AUTOMATIC", "Observation promoted to Evidence")
    require(boundaries.get("adapter_to_trust") == "NOT_ESTABLISHED", "Adapter trust overclaimed")
    require(boundaries.get("synthetic_to_production") == "NOT_SUPPORTED", "production support overclaimed")
    require(boundaries.get("input_to_decision") == "NOT_CONNECTED", "input connected to decision")
    require(boundaries.get("adapter_to_termination") == "NOT_AUTHORIZED", "termination authority overclaimed")
    require(bool(result.get("limitations")) and len(result["limitations"]) >= 6, "limitations missing")
    require(result.get("next_phase_recommended") == "commercial_review_prototype", "unsafe or unexpected next phase")
    truth = result.get("truth_boundary", {})
    require(truth and all(value is False for value in truth.values()), "truth boundary promoted")
    return copy.deepcopy(result)


def expect_invalid(result: dict[str, Any], label: str) -> None:
    try:
        validate_result(result)
    except Phase2BCompletionReviewSmokeError:
        return
    raise Phase2BCompletionReviewSmokeError(f"invalid case accepted: {label}")


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_execution_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen"}:
            found.add(node.func.attr)
    return found


def main() -> None:
    for path in (REVIEW_PATH, CHECKLIST_PATH, RESULT_PATH, *REQUIRED_PHASE2B_PATHS):
        require(path.is_file(), f"missing required file: {path}")
    for path, expected in FROZEN_HASHES.items():
        require(path.is_file(), f"missing frozen file: {path}")
        require(hashlib.sha256(path.read_bytes()).hexdigest() == expected, f"frozen file changed: {path}")

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "pip", "importlib"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "network or subprocess capability imported")
    require(not forbidden_execution_calls(Path(__file__)), "dynamic or shell execution present")

    review_text = REVIEW_PATH.read_text(encoding="utf-8")
    checklist_text = CHECKLIST_PATH.read_text(encoding="utf-8")
    for marker in (
        "Architecture Review != Production Approval",
        "Prototype Validation != Deployment Readiness",
        "Boundary Definition != External Trust",
        "Observation Input != Evidence",
        "next_phase_recommended=commercial_review_prototype",
        "production_ready=false",
        "customer_ready=false",
    ):
        require(marker in review_text, f"review marker missing: {marker}")
    for marker in ("Observation Schema", "Adapter Provenance", "Snapshot Integrity", "Fail Closed", "Reproducibility", "Production Readiness"):
        require(marker in checklist_text, f"checklist item missing: {marker}")
    for forbidden in ("production_ready=true", "customer_ready=true", "external_validation_completed=true", "deployment_authorized=true"):
        require(forbidden not in review_text and forbidden not in checklist_text, f"unsupported documentation claim: {forbidden}")

    result = read_json(RESULT_PATH)
    canonical = validate_result(result)

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    for field in ("production_ready", "customer_ready", "external_validation_completed", "deployment_authorized"):
        mutation = copy.deepcopy(result)
        mutation[field] = True
        invalid_cases.append((mutation, field))
    mutation = copy.deepcopy(result); mutation["limitations"] = []; invalid_cases.append((mutation, "limitations"))
    mutation = copy.deepcopy(result); mutation["next_phase_recommended"] = "real_adapter_integration"; invalid_cases.append((mutation, "unsafe next phase"))
    for mutation, label in invalid_cases:
        expect_invalid(mutation, label)

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_result(read_json(RESULT_PATH))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "review result non-deterministic")

    print("SAEE_PHASE2B_COMPLETION_REVIEW_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("phase2b_completion_status=completed_prototype")
    print("architecture_review_status=PASS_AND_FREEZE")
    print("next_phase_recommended=commercial_review_prototype")
    print("limitations_present=true")
    print("frozen_files_unchanged=true")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    print("customer_ready=false")
    print("external_validation_completed=false")


if __name__ == "__main__":
    try:
        main()
    except (Phase2BCompletionReviewSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_PHASE2B_COMPLETION_REVIEW_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
