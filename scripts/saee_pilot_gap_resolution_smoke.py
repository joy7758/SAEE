#!/usr/bin/env python3
"""Offline smoke for SAEE Pilot Readiness Gap Resolution Plan v0.1."""

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

from saee_backend.services.pilot_gap_tracking import (  # noqa: E402
    PilotGapTrackingError,
    evaluate_pilot_gap_plan,
)


PLAN_PATH = ROOT / "agent-interface/evaluation/saee-pilot-readiness-gap-plan.v0.1.json"
DOC_PATH = ROOT / "docs/evaluation/SAEE_PILOT_READINESS_GAP_RESOLUTION_PLAN.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_PILOT_READINESS_GAP_RESOLUTION_PLAN_RECOMMENDATION_GATE.md"
SERVICE_PATH = ROOT / "saee_backend/services/pilot_gap_tracking.py"
CLI_PATH = ROOT / "scripts/saee_agent_cli.py"


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise AssertionError(detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def make_reassessment_ready(document: dict[str, Any]) -> dict[str, Any]:
    candidate = copy.deepcopy(document)
    for gap in candidate["gaps"]:
        gap["status"] = "EVIDENCE_READY"
        gap["evidence_refs"] = [f"synthetic:future-{gap['id'].lower()}"]
    candidate["future_reassessment_allowed"] = True
    return candidate


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> None:
    require(PLAN_PATH.is_file(), "gap plan missing")
    source = read_json(PLAN_PATH)
    result = evaluate_pilot_gap_plan(copy.deepcopy(source))
    require(result["result_type"] == "SAEE_PILOT_GAP_REVIEW_RESULT", "result type")
    require(result["current_readiness"] == "NO_GO", "current readiness")
    require(result["open_gap_count"] == 12, "open gap count")
    require(result["critical_open_gap_count"] == 8, "critical open gap count")
    require(result["blocking_level"] == "CRITICAL", "blocking level")
    require(result["reassessment_allowed"] is False, "current reassessment boundary")
    require(result["pilot_authorized"] is False, "authorization boundary")
    require(result["gap_resolution_claimed"] is False, "resolution boundary")

    future = evaluate_pilot_gap_plan(make_reassessment_ready(source))
    require(future["current_readiness"] == "NO_GO", "future fixture must not change readiness")
    require(future["open_gap_count"] == 0, "future fixture open gaps")
    require(future["reassessment_allowed"] is True, "reassessment path")
    require(len(future["evidence_ready_pending_rereview"]) == 12, "future evidence-ready count")
    require(future["pilot_authorized"] is False, "future fixture cannot authorize pilot")

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    go = copy.deepcopy(source); go["current_readiness"] = "GO"; invalid_cases.append((go, "PILOT_GAP_CRITICAL_READINESS_MISMATCH"))
    authorized = copy.deepcopy(source); authorized["pilot_authorized"] = True; invalid_cases.append((authorized, "PILOT_GAP_AUTHORIZATION_FORBIDDEN"))
    executed = copy.deepcopy(source); executed["execution_started"] = True; invalid_cases.append((executed, "PILOT_GAP_EXECUTION_FORBIDDEN"))
    completed = copy.deepcopy(source); completed["gaps"][0]["status"] = "CLOSED"; invalid_cases.append((completed, "PILOT_GAP_COMPLETED_WITHOUT_EVIDENCE"))
    reassessment = copy.deepcopy(source); reassessment["future_reassessment_allowed"] = True; invalid_cases.append((reassessment, "PILOT_GAP_REASSESSMENT_MISMATCH"))
    for candidate, expected in invalid_cases:
        try:
            evaluate_pilot_gap_plan(candidate)
        except PilotGapTrackingError as exc:
            require(exc.code == expected, f"reason code expected {expected}, got {exc.code}")
        else:
            raise AssertionError(f"invalid gap plan accepted: {expected}")

    require(DOC_PATH.is_file(), "gap plan document missing")
    require(GATE_PATH.is_file(), "recommendation gate missing")
    doc = DOC_PATH.read_text(encoding="utf-8")
    for section in range(1, 7):
        require(f"## {section} " in doc, f"missing section {section}")
    for title in ("Dataset Source", "Data Ownership", "Permissions", "Privacy Review", "Retention Policy", "Deletion Process", "Schema Freeze", "Annotation Approval", "Environment", "Safety Controls"):
        require(title in doc, f"gap matrix item {title}")
    require("review-pilot-gaps" in CLI_PATH.read_text(encoding="utf-8"), "CLI command")

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx"}
    for path in (Path(__file__), SERVICE_PATH):
        require(not imported_roots(path).intersection(forbidden), f"external capability import: {path}")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = evaluate_pilot_gap_plan(copy.deepcopy(source))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "non-deterministic gap review")

    print("SAEE_PILOT_GAP_RESOLUTION_SMOKE: PASS")
    print("valid_cases=2/2")
    print("invalid_cases=5/5")
    print("gap_cases=12/12")
    print("critical_open_gaps=8/8")
    print("reassessment_paths=2/2")
    print("deterministic_runs=5/5")
    print("current_readiness=NO_GO")
    print("open_gaps=12")
    print("future_reassessment_allowed=false")
    print("pilot_authorized=false")
    print("execution_started=false")
    print("gap_resolution_claimed=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("data_created=false")
    print("approvals_created=false")
    print("external_validation_completed=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()

