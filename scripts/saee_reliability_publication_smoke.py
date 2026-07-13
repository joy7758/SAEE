#!/usr/bin/env python3
"""Offline deterministic validation for the SAEE Reliability publication draft."""

from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "agent-interface/research/reliability-study-v0.1"
MANIFEST = PACKAGE / "manifest.v0.1.json"
README = PACKAGE / "README.md"
REPORT = ROOT / "docs/research/SAEE_AGENT_RELIABILITY_STUDY_V0_1.md"
SUMMARY = ROOT / "docs/research/SAEE_AGENT_RELIABILITY_SUMMARY_V0_1.md"
RESULT = ROOT / "agent-interface/reliability/saee-agent-reliability-result.v0.1.json"
RESULT_SCHEMA = ROOT / "agent-interface/reliability/saee-agent-reliability-study.schema.v0.1.json"
GATE = ROOT / "docs/strategy/SAEE_AGENT_RELIABILITY_PUBLICATION_DRAFT_RECOMMENDATION_GATE.md"

SECRET_PATTERNS = (
    re.compile(r"bce-v3/", re.I),
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"AKLT[A-Za-z0-9]{12,}"),
    re.compile(r"BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY", re.I),
)
FORBIDDEN_CLAIMS = (
    re.compile(r"best model", re.I),
    re.compile(r"winner is", re.I),
    re.compile(r"industry standard", re.I),
    re.compile(r"certified by", re.I),
    re.compile(r"production_ready=true", re.I),
    re.compile(r"external_validation=true", re.I),
    re.compile(r"doi_assigned=true", re.I),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_manifest(value: Any, *, check_files: bool = True) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict) or value.get("artifact_id") != "saee-research:agent-reliability-study:v0.1":
        return ["PUBLICATION_MANIFEST_IDENTITY_INVALID"]
    if value.get("status") != "local_publication_draft_not_published":
        errors.append("PUBLICATION_STATUS_INVALID")
    refs = value.get("references")
    if not isinstance(refs, list) or len(refs) < 10:
        errors.append("PUBLICATION_REFERENCES_REQUIRED")
        refs = []
    paths = [item.get("path") for item in refs if isinstance(item, dict)]
    if len(paths) != len(set(paths)):
        errors.append("PUBLICATION_REFERENCE_DUPLICATE")
    if check_files:
        for item in refs:
            if not isinstance(item, dict) or not isinstance(item.get("path"), str):
                errors.append("PUBLICATION_REFERENCE_INVALID")
                continue
            path = (ROOT / item["path"]).resolve()
            try:
                path.relative_to(ROOT.resolve())
            except ValueError:
                errors.append("PUBLICATION_REFERENCE_OUTSIDE_ROOT")
                continue
            if not path.is_file():
                errors.append("PUBLICATION_REFERENCE_MISSING")
                continue
            expected = item.get("sha256")
            if expected is not None and expected != sha256(path):
                errors.append("PUBLICATION_REFERENCE_DIGEST_MISMATCH")
        result_digest = value.get("study_result_digest")
        if result_digest != "sha256:" + sha256(RESULT):
            errors.append("PUBLICATION_RESULT_DIGEST_MISMATCH")
    boundary = value.get("truth_boundary")
    expected_boundary = {
        "experiments_rerun_for_publication": False,
        "external_validation": False,
        "peer_reviewed": False,
        "doi_assigned": False,
        "publicly_published": False,
        "ranking_generated": False,
        "certification_claimed": False,
        "production_ready": False,
    }
    if boundary != expected_boundary:
        errors.append("PUBLICATION_BOUNDARY_INVALID")
    return sorted(set(errors))


def main() -> int:
    for path in (MANIFEST, README, REPORT, SUMMARY, RESULT, RESULT_SCHEMA, GATE):
        assert path.is_file(), path
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert validate_manifest(manifest) == []

    schema = json.loads(RESULT_SCHEMA.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    result_errors = list(Draft202012Validator(schema).iter_errors(result))
    assert not result_errors, result_errors[0].message if result_errors else ""
    assert result["study_complete"] is True
    assert result["total_runs_executed"] == 30
    assert result["total_runs_completed"] == 25
    assert result["total_contract_failed_runs"] == 5
    assert result["ranking_generated"] is False
    assert result["truth_boundary"]["reliability_probability_estimated"] is False

    report = REPORT.read_text(encoding="utf-8")
    summary = SUMMARY.read_text(encoding="utf-8")
    required_sections = (
        "## Abstract", "## 1. Motivation", "## 2. System Architecture", "## 3. Experimental Methodology",
        "## 4. Agent Configuration", "## 5. Scenario Description", "## 6. Observable Metrics",
        "## 7. Results", "## 8. Findings", "## 9. Threats to Validity and Limitations",
        "## 10. Reproducibility", "## 11. Artifact and Publication Boundary",
    )
    assert all(section in report for section in required_sections)
    for finding in (
        "Finding 1: Agent behavior may vary under identical environments",
        "Finding 2: Evidence assessment may remain stable despite behavioral differences",
        "Finding 3: Interface contract reliability is part of agent reliability",
    ):
        assert finding in report and finding.split(": ", 1)[1] + "." in summary
    for marker in ("30", "25", "MVP_FINAL_RESULT_INVALID", "reliability_probability_estimated=false"):
        assert marker in report or marker in summary or marker in json.dumps(manifest)

    combined = "\n".join((report, summary, README.read_text(encoding="utf-8"), GATE.read_text(encoding="utf-8"), json.dumps(manifest, ensure_ascii=False)))
    assert not any(pattern.search(combined) for pattern in SECRET_PATTERNS)
    assert not any(pattern.search(combined) for pattern in FORBIDDEN_CLAIMS)
    assert '"provider_response"' not in combined and '"raw_provider_payload"' not in combined

    invalid_cases = 0
    mutations = []
    mutation = copy.deepcopy(manifest); mutation["status"] = "published"; mutations.append((mutation, "PUBLICATION_STATUS_INVALID"))
    mutation = copy.deepcopy(manifest); mutation["truth_boundary"]["peer_reviewed"] = True; mutations.append((mutation, "PUBLICATION_BOUNDARY_INVALID"))
    mutation = copy.deepcopy(manifest); mutation["truth_boundary"]["ranking_generated"] = True; mutations.append((mutation, "PUBLICATION_BOUNDARY_INVALID"))
    mutation = copy.deepcopy(manifest); mutation["references"][0]["path"] = "../../secret"; mutations.append((mutation, "PUBLICATION_REFERENCE_OUTSIDE_ROOT"))
    mutation = copy.deepcopy(manifest); mutation["references"][0]["sha256"] = "0" * 64; mutations.append((mutation, "PUBLICATION_REFERENCE_DIGEST_MISMATCH"))
    mutation = copy.deepcopy(manifest); mutation["references"].append(copy.deepcopy(mutation["references"][0])); mutations.append((mutation, "PUBLICATION_REFERENCE_DUPLICATE"))
    for mutation, code in mutations:
        assert code in validate_manifest(mutation)
        invalid_cases += 1
    assert invalid_cases == 6

    baseline = json.dumps(validate_manifest(manifest), sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        assert json.dumps(validate_manifest(manifest), sort_keys=True, separators=(",", ":")) == baseline

    print("SAEE_RELIABILITY_PUBLICATION_SMOKE: PASS")
    print("publication_report=1/1")
    print("external_summary=1/1")
    print("reproducibility_manifest=1/1")
    print("references_resolved=13/13")
    print("frozen_result_digest_valid=true")
    print("required_findings=3/3")
    print("invalid_cases=6/6")
    print("deterministic_runs=5/5")
    print("experiments_rerun_for_publication=false")
    print("ranking_generated=false")
    print("external_validation=false")
    print("publicly_published=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, json.JSONDecodeError, OSError, ValueError) as exc:
        print(f"SAEE_RELIABILITY_PUBLICATION_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
