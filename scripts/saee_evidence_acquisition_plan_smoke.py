#!/usr/bin/env python3
"""Offline smoke for SAEE Pilot Evidence Acquisition Planning v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.pilot_evidence_acquisition import (  # noqa: E402
    CLOSURE_FIELDS,
    EXPECTED_GAP_IDS,
    PilotEvidenceAcquisitionError,
    evaluate_evidence_acquisition_plan,
)


PLAN_PATH = ROOT / "agent-interface/evaluation/saee-pilot-evidence-acquisition-plan.v0.1.json"
GAP_PLAN_PATH = ROOT / "agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json"
DOC_PATH = ROOT / "docs/evaluation/SAEE_PILOT_EVIDENCE_ACQUISITION_PLAN.md"
BOUNDARY_PATH = ROOT / "docs/evaluation/SAEE_EVIDENCE_ACQUISITION_BOUNDARIES.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_EVIDENCE_ACQUISITION_PLAN_RECOMMENDATION_GATE.md"
SERVICE_PATH = ROOT / "saee_backend/services/pilot_evidence_acquisition.py"
CLI_PATH = ROOT / "scripts/saee_agent_cli.py"


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> None:
    require(PLAN_PATH.is_file(), "acquisition plan missing")
    require(GAP_PLAN_PATH.is_file(), "source gap plan missing")
    source = read_json(PLAN_PATH)
    gap_plan = read_json(GAP_PLAN_PATH)
    result = evaluate_evidence_acquisition_plan(copy.deepcopy(source))
    require(result["result_type"] == "SAEE_EVIDENCE_ACQUISITION_PLAN_RESULT", "result type")
    require(result["current_readiness"] == "NO_GO", "current readiness")
    require(result["pilot_status"] == "not_authorized", "pilot status")
    require(result["missing_evidence_count"] == 12, "missing count")
    require(result["open_artifact_requirement_count"] == 12, "open artifact count")
    require(result["gaps_addressed"] == 0, "gaps addressed")

    mapped = tuple(item["gap_id"] for item in source["artifact_requirements"])
    source_gaps = tuple(item["id"] for item in gap_plan["gaps"])
    require(mapped == EXPECTED_GAP_IDS, "canonical gap coverage")
    require(mapped == source_gaps, "gap plan coverage drift")
    require(all(item["artifact_status"] == "MISSING" for item in source["artifact_requirements"]), "artifact status boundary")
    require(all(all(item[field] is None for field in CLOSURE_FIELDS) for item in source["artifact_requirements"]), "artifact evidence unexpectedly present")

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    started = copy.deepcopy(source); started["evidence_acquisition_started"] = True; invalid_cases.append((started, "EVIDENCE_ACQUISITION_STARTED_FORBIDDEN"))
    closed = copy.deepcopy(source); closed["artifact_requirements"][0]["artifact_status"] = "CLOSED"; invalid_cases.append((closed, "EVIDENCE_ACQUISITION_CLOSED_WITHOUT_REFERENCE"))
    authorized = copy.deepcopy(source); authorized["pilot_authorized"] = True; invalid_cases.append((authorized, "EVIDENCE_ACQUISITION_PILOT_AUTHORIZATION_FORBIDDEN"))
    ready = copy.deepcopy(source); ready["current_readiness"] = "GO"; invalid_cases.append((ready, "EVIDENCE_ACQUISITION_READINESS_CHANGED"))
    records = copy.deepcopy(source); records["evidence_records_created"] = True; invalid_cases.append((records, "EVIDENCE_RECORD_CREATION_FORBIDDEN"))
    addressed = copy.deepcopy(source); addressed["gaps_addressed"] = 1; invalid_cases.append((addressed, "EVIDENCE_ACQUISITION_GAP_COUNT_MISMATCH"))
    for candidate, expected in invalid_cases:
        try:
            evaluate_evidence_acquisition_plan(candidate)
        except PilotEvidenceAcquisitionError as exc:
            require(exc.code == expected, f"reason code expected {expected}, got {exc.code}")
        else:
            raise AssertionError(f"invalid acquisition plan accepted: {expected}")

    for path in (DOC_PATH, BOUNDARY_PATH, GATE_PATH):
        require(path.is_file(), f"document missing: {path}")
    doc = DOC_PATH.read_text(encoding="utf-8")
    for section in range(1, 7):
        require(f"## {section} " in doc, f"missing section {section}")
    for artifact in ("Dataset Source Declaration", "Ownership Statement", "Usage Authorization Record", "Privacy Assessment Record", "Retention and Deletion Policy Record", "Access Control Record", "Schema Version Freeze Record", "Annotation Protocol Approval Record", "Pilot Environment Manifest", "Execution Safety Approval Record"):
        require(artifact in doc, f"artifact mapping {artifact}")
    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    require("This plan specifies future evidence requirements. It does not represent collected evidence, approval, or pilot authorization." in boundary, "English boundary")
    require("该计划定义未来证据需求，不代表已收集证据、已获得批准或已授权试点执行。" in boundary, "Chinese boundary")
    require("review-evidence-acquisition-plan" in CLI_PATH.read_text(encoding="utf-8"), "CLI command")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    for path in (Path(__file__), SERVICE_PATH):
        require(not imported_roots(path).intersection(forbidden), f"external capability import: {path}")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = evaluate_evidence_acquisition_plan(copy.deepcopy(source))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic acquisition plan")

    print("SAEE_EVIDENCE_ACQUISITION_PLAN_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=6/6")
    print("gap_mappings=12/12")
    print("artifact_status_missing=12/12")
    print("artifact_evidence_fields_null=60/60")
    print("deterministic_runs=5/5")
    print("current_readiness=NO_GO")
    print("missing_artifacts=12")
    print("gaps_addressed=0")
    print("evidence_acquisition_started=false")
    print("evidence_records_created=false")
    print("pilot_authorized=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("data_collected=false")
    print("external_parties_contacted=false")
    print("privacy_decisions_created=false")
    print("approvals_created=false")
    print("external_validation_completed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()

