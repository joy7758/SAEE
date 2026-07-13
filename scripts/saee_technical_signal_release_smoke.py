#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Technical Signal Release Package v1.0."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "agent-interface/ecosystem/saee-technical-signal-release.v1.0.json"
SCHEMA = ROOT / "schemas/saee-technical-signal-release.schema.v1.0.json"
ARTICLE = ROOT / "docs/public/WHY_AGENTS_NEED_READINESS_EVALUATION.md"
GATE = ROOT / "docs/strategy/SAEE_TECHNICAL_SIGNAL_RELEASE_RECOMMENDATION_GATE.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def errors(value: dict) -> list[str]:
    schema = load(SCHEMA)
    result = ["SCHEMA_INVALID"] if list(Draft202012Validator(schema).iter_errors(value)) else []
    operations = value.get("developer_signal", {}).get("public_operations", [])
    if operations != ["saee.evaluate_agent_run", "saee.evaluate_evidence"]:
        result.append("PUBLIC_OPERATION_SET_INVALID")
    truth = value.get("truth_boundary", {})
    allowed_true = {"technical_signal_package_ready"}
    if any(flag for key, flag in truth.items() if key not in allowed_true):
        result.append("EXTERNAL_CLAIM_FORBIDDEN")
    return list(dict.fromkeys(result))


def main() -> int:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    package = load(PACKAGE)
    assert not errors(package), errors(package)

    article = ARTICLE.read_text(encoding="utf-8")
    for phrase in (
        "为什么自主智能体需要执行前可靠性评估",
        "Why Agents Need Readiness Evaluation Before Autonomous Execution",
        "saee.evaluate_agent_run",
        "saee.evaluate_evidence",
        "article_published=false",
        "production_ready=false",
    ):
        assert phrase in article
    assert "answer: recommend" in GATE.read_text(encoding="utf-8")
    for reference in package["references"].values():
        assert (ROOT / reference).is_file(), reference

    invalid: list[dict] = []
    for path, bad in (
        (("signal_version",), "2.0"),
        (("signal_id",), "other"),
        (("stage_id",), "ECOSYSTEM_ATTENTION"),
        (("recommendation",), "adopted"),
        (("article", "status"), "published"),
        (("github_signal", "status"), "public_release"),
        (("developer_signal", "public_operations"), ["rehearse_agent"]),
        (("developer_signal", "protocols"), ["Public API"]),
        (("truth_boundary", "article_published"), True),
        (("truth_boundary", "github_release_created"), True),
        (("truth_boundary", "developer_activity_presented"), True),
        (("truth_boundary", "ecosystem_technical_conversation_verified"), True),
        (("truth_boundary", "partner_relationship_established"), True),
        (("truth_boundary", "official_cloud_integration"), True),
        (("truth_boundary", "marketplace_listed"), True),
        (("truth_boundary", "external_agent_adoption_validated"), True),
        (("truth_boundary", "production_ready"), True),
    ):
        item = copy.deepcopy(package)
        target = item
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = bad
        invalid.append(item)
    assert len(invalid) >= 12 and all(errors(item) for item in invalid)

    baseline = json.dumps(errors(package), ensure_ascii=False, sort_keys=True)
    for _ in range(5):
        assert json.dumps(errors(copy.deepcopy(package)), ensure_ascii=False, sort_keys=True) == baseline

    print("SAEE_TECHNICAL_SIGNAL_RELEASE_SMOKE: PASS")
    print("current_stage=TECHNICAL_SIGNAL_RELEASE")
    print("public_operations=2/2")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("technical_signal_package_ready=true")
    print("article_published=false")
    print("developer_activity_presented=false")
    print("official_cloud_integration=false")
    print("external_agent_adoption_validated=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
