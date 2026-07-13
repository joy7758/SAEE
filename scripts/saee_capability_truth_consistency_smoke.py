#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Capability Truth Consistency v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.capability_truth_consistency_validator import (  # noqa: E402
    load_truth_sources,
    validate_current_capability_truth,
    validate_truth_sources,
)


SCHEMA = ROOT / "schemas/saee-capability-truth-consistency.schema.v0.1.json"
RESULT = ROOT / "agent-interface/validation/saee-capability-truth-consistency-result.v0.1.json"
FIXTURES = ROOT / "agent-interface/validation/truth-consistency-fixtures"
SERVICE = ROOT / "saee_backend/services/capability_truth_consistency_validator.py"
DOC = ROOT / "docs/release/SAEE_CAPABILITY_TRUTH_CONSISTENCY_VALIDATION.md"
GATE = ROOT / "docs/strategy/SAEE_CAPABILITY_TRUTH_CONSISTENCY_RECOMMENDATION_GATE.md"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def apply_fixture(sources: dict, fixture: dict) -> dict:
    mutated = copy.deepcopy(sources)
    mutation = fixture["mutation"]
    target = mutated[mutation["target"]]
    path = mutation["path"]
    parent = target
    for part in path[:-1]:
        parent = parent[part]
    operation = mutation["operation"]
    if operation == "set":
        parent[path[-1]] = mutation["value"]
    elif operation == "remove_list_item":
        values = parent[path[-1]]
        parent[path[-1]] = [item for item in values if item[mutation["match_key"]] != mutation["match_value"]]
    elif operation == "set_list_item":
        values = parent[path[-1]]
        item = next(item for item in values if item[mutation["match_key"]] == mutation["match_value"])
        item[mutation["field"]] = mutation["value"]
    else:
        raise AssertionError(f"unsupported fixture operation: {operation}")
    return mutated


def main() -> int:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    generated = validate_current_capability_truth()
    checked = load(RESULT)
    assert generated == checked
    assert not list(Draft202012Validator(schema).iter_errors(checked))
    assert len(checked["checked_sources"]) >= 8
    assert all(checked[field] is True for field in ("identity_match", "operation_match", "status_match", "lifecycle_match", "protocol_match", "boundary_match"))
    assert checked["conflicts_detected"] is False and checked["conflicts"] == []

    fixture_files = sorted(FIXTURES.glob("*.json"))
    assert len(fixture_files) >= 10
    sources = load_truth_sources()
    invalid_results = []
    for path in fixture_files:
        fixture = load(path)
        result = validate_truth_sources(apply_fixture(sources, fixture))
        assert result["conflicts_detected"] is True, path.name
        assert fixture["expected_reason_code"] in result["conflicts"], (path.name, result["conflicts"])
        invalid_results.append(result)
    serialized = json.dumps(invalid_results, ensure_ascii=False)
    for required in (
        "TRUTH_BOUNDARY_PRODUCTION_ESCALATION",
        "TRUTH_BOUNDARY_PUBLIC_SERVICE_CLAIM",
        "TRUTH_BOUNDARY_EXTERNAL_ADOPTION_CLAIM",
        "TRUTH_BOUNDARY_MARKETPLACE_CLAIM",
        "TRUTH_BOUNDARY_CERTIFICATION_CLAIM",
    ):
        assert required in serialized

    document = DOC.read_text(encoding="utf-8")
    assert "SAEE validates consistency among capability descriptions. It does not establish external trust, adoption, certification, or production readiness." in document
    assert "SAEE 验证能力描述之间的一致性，不建立外部信任、采用、认证或生产就绪结论。" in document
    assert "`recommend`" in GATE.read_text(encoding="utf-8")

    baseline = json.dumps(generated, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        repeated = validate_current_capability_truth()
        assert json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"} & imports)

    print("SAEE_CAPABILITY_TRUTH_CONSISTENCY_SMOKE: PASS")
    print("sources_checked=8/8")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(fixture_files)}/{len(fixture_files)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("identity_match=true")
    print("operation_match=true")
    print("status_match=true")
    print("lifecycle_match=true")
    print("protocol_match=true")
    print("boundary_match=true")
    print("conflicts_detected=false")
    print("validation_only=true")
    print("alpha_release=true")
    print("public_release=false")
    print("marketplace_listed=false")
    print("external_adoption=false")
    print("customer_validated=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
