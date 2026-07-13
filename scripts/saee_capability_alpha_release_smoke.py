#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Capability Alpha Preparation v0.1."""

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

from saee_backend.services.capability_release_boundary_validator import validate_release_boundary  # noqa: E402


RELEASE = ROOT / "release/saee-capability-alpha-v0.1"
AGENT_MANIFEST = ROOT / "agent-interface/release/saee-alpha-release-manifest.v0.1.json"
BOUNDARY_SCHEMA = ROOT / "schemas/saee-capability-release-boundary.schema.v0.1.json"
SERVICE = ROOT / "saee_backend/services/capability_release_boundary_validator.py"
DEVELOPER_GUIDE = ROOT / "docs/public/SAEE_DEVELOPER_QUICK_START.md"
AGENT_GUIDE = ROOT / "docs/public/SAEE_AGENT_QUICK_START.md"
VERSION_POLICY = ROOT / "docs/release/SAEE_CAPABILITY_VERSION_POLICY.md"
REVIEW = ROOT / "docs/release/SAEE_CAPABILITY_ALPHA_RELEASE_REVIEW.md"


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def resolve_from(base: Path, ref: str) -> Path:
    path = (base / ref).resolve()
    path.relative_to(ROOT.resolve())
    return path


def main() -> int:
    required_package = {
        "README.md", "capability-card.json", "manifest.json", "operations.json", "protocols.json",
        "limitations.md", "changelog.md", "version.json", "examples/README.md", "examples/example-index.json",
    }
    assert RELEASE.is_dir()
    assert all((RELEASE / ref).is_file() for ref in required_package)
    assert not list(RELEASE.rglob("*.py")), "release package duplicated executable logic"

    schema = load(BOUNDARY_SCHEMA)
    Draft202012Validator.check_schema(schema)
    manifest = load(RELEASE / "manifest.json")
    boundary = manifest["release_boundary"]
    valid = validate_release_boundary(boundary)
    assert valid["valid"] is True and valid["reason_codes"] == []
    assert valid["alpha_preparation"] is True
    assert valid["public_release"] is False and valid["public_service"] is False and valid["production_ready"] is False

    package_files = manifest["package_files"]
    assert set(package_files.values()).issubset(required_package)
    assert all(resolve_from(RELEASE, ref).is_file() for ref in package_files.values())
    assert all(resolve_from(RELEASE, ref).is_file() for ref in manifest["canonical_source_references"].values())
    assert resolve_from(RELEASE, manifest["truth_consistency_validation_reference"]).is_file()
    assert manifest["business_logic_duplicated"] is False

    version = load(RELEASE / "version.json")
    card = load(RELEASE / "capability-card.json")
    operations = load(RELEASE / "operations.json")
    protocols = load(RELEASE / "protocols.json")
    examples = load(RELEASE / "examples/example-index.json")
    assert {version["version"], card["version"], operations["version"], protocols["version"], examples["version"], manifest["version"]} == {"0.1.0"}
    assert version["release_status"] == card["release_status"] == manifest["release_status"] == "ALPHA_PREPARATION"
    assert set(card["capability_identity"]) == {"saee.agent-reliability", "saee.evidence-evaluation"}
    assert card["business_logic_duplicated"] is False and operations["operation_logic_included"] is False and examples["example_payloads_duplicated"] is False
    assert operations["public_endpoint"] is None
    assert {item["operation_id"] for item in operations["operations"]} == {"evaluate_agent_run", "evaluate_evidence", "rehearse_agent"}
    assert next(item for item in operations["operations"] if item["operation_id"] == "rehearse_agent")["status"] == "contract_only"
    assert {item["name"] for item in protocols["protocols"]} == {"MCP", "HTTP Contract"}
    assert all(item["public_endpoint"] is None for item in protocols["protocols"])
    assert all(resolve_from(RELEASE, item["contract_reference"]).is_file() for item in protocols["protocols"])
    assert all(resolve_from(RELEASE / "examples", item["reference"]).is_file() for item in examples["examples"])
    assert resolve_from(RELEASE / "examples", examples["integration_examples_reference"]).is_file()

    agent_manifest = load(AGENT_MANIFEST)
    assert agent_manifest["release_id"] == manifest["release_id"] and agent_manifest["version"] == manifest["version"]
    assert agent_manifest["release_status"] == "ALPHA_PREPARATION"
    assert len(agent_manifest["capabilities"]) == 2 and len(agent_manifest["operations"]) == 3 and len(agent_manifest["protocols"]) == 2
    assert len(agent_manifest["limitations"]) >= 6
    assert all((ROOT / ref).is_file() for ref in agent_manifest["source_references"].values())
    assert all((ROOT / ref).is_file() for ref in agent_manifest["validation_references"].values())
    truth = agent_manifest["truth_boundary"]
    assert truth["alpha_preparation"] is True
    assert all(truth[field] is False for field in ("public_release", "public_api", "public_service", "marketplace_listed", "external_adoption", "customer_validated", "production_ready"))

    invalid: list[dict] = []
    for field in ("public_release", "public_api", "public_service", "marketplace_listed", "external_adoption", "customer_validated", "production_ready", "certified", "approved", "trusted_by_all_agents"):
        mutation = copy.deepcopy(boundary); mutation["truth_boundary"][field] = True; invalid.append(mutation)
    for field in ("limitations_present", "version_present", "capability_identity_present"):
        mutation = copy.deepcopy(boundary); mutation["requirements"][field] = False; invalid.append(mutation)
    mutation = copy.deepcopy(boundary); mutation.pop("version"); invalid.append(mutation)
    mutation = copy.deepcopy(boundary); mutation["unexpected"] = True; invalid.append(mutation)
    mutation = copy.deepcopy(boundary); mutation["version"] = "1.0.0"; invalid.append(mutation)
    assert len(invalid) >= 15
    assert all(validate_release_boundary(item)["valid"] is False for item in invalid)

    developer = DEVELOPER_GUIDE.read_text(encoding="utf-8")
    assert "SAEE Alpha provides capability contracts and local invocation patterns. It does not provide public production services." in developer
    assert "SAEE Alpha 提供能力契约和本地调用方式，不提供公网生产服务。" in developer
    agent = AGENT_GUIDE.read_text(encoding="utf-8")
    for marker in ("SUPPORTED does not mean APPROVED", "SUPPORTED does not mean CERTIFIED", "SUPPORTED does not mean SAFE", "SUPPORTED does not mean DEPLOYED"):
        assert marker in agent
    assert VERSION_POLICY.is_file() and REVIEW.is_file()

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True)
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_release_boundary(copy.deepcopy(boundary)), ensure_ascii=False, sort_keys=True) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"} & imports)

    print("SAEE_CAPABILITY_ALPHA_RELEASE_SMOKE: PASS")
    print("release_package_exists=true")
    print("package_files=10/10")
    print("version_valid=true")
    print("capability_identity_valid=true")
    print("capabilities=2/2")
    print("operations=3/3")
    print("protocols=2/2")
    print("limitations_valid=true")
    print("boundary_valid=true")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("business_logic_duplicated=false")
    print("alpha_preparation=true")
    print("public_release=false")
    print("public_api=false")
    print("public_service=false")
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
