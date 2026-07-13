#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Alpha Positioning Release v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.alpha_release_positioning_validator import (  # noqa: E402
    EXPECTED_TITLE,
    RELEASE_ROOT,
    validate_capabilities,
    validate_release_package,
)


CAPABILITIES = RELEASE_ROOT / "capabilities.json"
SERVICE = ROOT / "saee_backend/services/alpha_release_positioning_validator.py"


def main() -> int:
    value = json.loads(CAPABILITIES.read_text(encoding="utf-8"))
    valid = validate_release_package()
    assert valid["valid"] is True, valid
    assert valid["title_consistent"] is True
    assert valid["limitations_present"] is True
    assert valid["research_claims_bounded"] is True
    assert valid["commercial_claims_absent"] is True
    assert valid["document_count"] >= 5
    assert value["title"] == EXPECTED_TITLE

    invalid: list[dict] = []
    for phrase in (
        "industry standard", "certified", "production ready",
        "trusted by all agents", "market leader", "official standard",
    ):
        bad = copy.deepcopy(value)
        bad["subtitle"] = phrase
        invalid.append(bad)
    for key in (
        "public_release_executed", "production_ready", "commercial_service",
        "marketplace_listed", "customer_validated", "adoption_validated", "external_validation",
    ):
        bad = copy.deepcopy(value)
        bad["truth_boundary"][key] = True
        invalid.append(bad)
    for mutation in (
        lambda v: v.pop("title"),
        lambda v: v.update({"title": "SAEE Reliability Platform"}),
        lambda v: v.pop("capabilities"),
        lambda v: v.update({"capabilities": v["capabilities"][:2]}),
        lambda v: v["capabilities"][0].update({"canonical_ref": "missing.md"}),
        lambda v: v["capabilities"][0].update({"canonical_ref": "https://example.invalid/x"}),
        lambda v: v["entrypoints"].update({"asset_map": "../outside.md"}),
        lambda v: v.pop("truth_boundary"),
        lambda v: v.update({"truth_boundary": {}}),
    ):
        bad = copy.deepcopy(value)
        mutation(bad)
        invalid.append(bad)
    assert len(invalid) >= 20
    assert all(validate_capabilities(case)["valid"] is False for case in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        rerun = validate_release_package()
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"} & imported)

    assert (ROOT / "docs/release/SAEE_ALPHA_ASSET_MAP.md").is_file()
    assert (ROOT / "examples/public-demo/README.md").is_file()
    assert (ROOT / "docs/research/SAEE_RESEARCH_ARTIFACT_INDEX.md").is_file()
    assert all(valid[field] is False for field in (
        "network_accessed", "subprocess_started", "external_execution",
        "public_release_executed", "production_ready",
    ))

    print("SAEE_ALPHA_POSITIONING_RELEASE_SMOKE: PASS")
    print("release_package=true")
    print(f"documents={valid['document_count']}")
    print("asset_map=true")
    print("demo_index=true")
    print("research_index=true")
    print(f"invalid_cases={len(invalid)}")
    print("deterministic_runs=5/5")
    print("alpha_release_preparation=true")
    print("public_release_package=true")
    print("public_release_executed=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

