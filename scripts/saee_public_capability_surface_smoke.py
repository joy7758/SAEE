#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Public Capability Surface v0.1."""

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

from saee_backend.services.public_capability_surface_validator import validate_public_capability_surface  # noqa: E402


SURFACE = ROOT / "agent-interface/public/saee-public-capability-surface.v0.1.json"
INDEX = ROOT / ".well-known/saee-capability-index.json"
SCHEMA = ROOT / "schemas/saee-public-capability-surface.schema.v0.1.json"
SERVICE = ROOT / "saee_backend/services/public_capability_surface_validator.py"
PUBLIC_DOC = ROOT / "docs/public/SAEE_AGENT_NATIVE_CAPABILITY_SURFACE.md"
QUICK_DOC = ROOT / "docs/public/SAEE_AGENT_QUICK_UNDERSTANDING.md"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    surface = load(SURFACE)
    index = load(INDEX)
    valid = validate_public_capability_surface(surface, index)
    assert valid["valid"] is True and valid["reason_codes"] == []
    assert valid["capability_count"] >= 2 and valid["protocol_count"] >= 2
    assert {item["operation_id"] for item in surface["available_operations"]} == {"saee.evaluate_agent_run", "saee.evaluate_evidence"}
    assert surface["truth_boundary"]["public_product_operation_count"] == 2
    assert valid["public_surface"] is True and valid["public_api"] is False and valid["production_ready"] is False

    surface_files = [SURFACE, INDEX, PUBLIC_DOC, QUICK_DOC]
    assert len(surface_files) >= 3 and all(path.is_file() for path in surface_files)
    doc = PUBLIC_DOC.read_text(encoding="utf-8")
    assert "SAEE provides machine-readable capability descriptions and bounded evaluation capabilities. It does not provide authorization, certification, or deployment approval." in doc
    assert "SAEE 提供机器可读能力描述和有边界评估能力，不提供授权、认证或部署批准。" in doc

    invalid: list[tuple[dict, dict]] = []
    for mutate in (
        lambda s, i: s.pop("capability_id"),
        lambda s, i: s.update({"unexpected": True}),
        lambda s, i: s.update({"capabilities": s["capabilities"][:1]}),
        lambda s, i: s.update({"protocols": ["MCP"]}),
        lambda s, i: s["truth_boundary"].update({"public_api": True}),
        lambda s, i: s["truth_boundary"].update({"publicly_deployed": True}),
        lambda s, i: s["truth_boundary"].update({"production_ready": True}),
        lambda s, i: s["truth_boundary"].update({"marketplace_listed": True}),
        lambda s, i: s["truth_boundary"].update({"industry_standard_claimed": True}),
        lambda s, i: i.update({"capability_reference": "/Users/private/capability.json"}),
        lambda s, i: i.update({"capability_reference": "https://example.invalid/capability.json"}),
        lambda s, i: i.pop("limitations_reference"),
        lambda s, i: s["description"].update({"en": "SAEE is certified and approved for production use."}),
        lambda s, i: i.update({"api_key": "sk-synthetic-not-a-real-secret"}),
        lambda s, i: s["available_operations"][0].update({"public_endpoint": "https://example.invalid/api"}),
        lambda s, i: s["available_operations"].append({"operation_id": "rehearse_agent", "status": "contract_only", "public_endpoint": None}),
        lambda s, i: s["available_operations"][0].update({"operation_id": "evaluate_agent_run"}),
        lambda s, i: s["truth_boundary"].update({"public_product_operation_count": 3}),
    ):
        bad_surface, bad_index = copy.deepcopy(surface), copy.deepcopy(index)
        mutate(bad_surface, bad_index)
        invalid.append((bad_surface, bad_index))
    assert len(invalid) >= 12
    assert all(validate_public_capability_surface(s, i)["valid"] is False for s, i in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True)
    deterministic_runs = 5
    for _ in range(deterministic_runs):
        assert json.dumps(validate_public_capability_surface(copy.deepcopy(surface), copy.deepcopy(index)), ensure_ascii=False, sort_keys=True) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp"} & imported)

    print("SAEE_PUBLIC_CAPABILITY_SURFACE_SMOKE: PASS")
    print(f"surface_files={len(surface_files)}")
    print(f"capabilities={valid['capability_count']}")
    print(f"protocols={valid['protocol_count']}")
    print(f"invalid_cases={len(invalid)}")
    print(f"deterministic_runs={deterministic_runs}/{deterministic_runs}")
    print("public_surface=true")
    print("repository_public_surface_prepared=true")
    print("publicly_deployed=false")
    print("public_api=false")
    print("public_service=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
