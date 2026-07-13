#!/usr/bin/env python3
"""Offline deterministic smoke for SAEE Ecosystem Entry Package v1.0."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.ecosystem_entry_package_validator import (  # noqa: E402
    ARK_ROOT,
    MCP_ROOT,
    MAPPING_PATH,
    validate_entry_data,
    validate_entry_packages,
)


SERVICE = ROOT / "saee_backend/services/ecosystem_entry_package_validator.py"


def main() -> int:
    mcp_card = json.loads((MCP_ROOT / "capability-card.json").read_text(encoding="utf-8"))
    tools = json.loads((MCP_ROOT / "mcp-tools.json").read_text(encoding="utf-8"))
    mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    valid = validate_entry_packages()
    assert valid["valid"] is True, valid
    assert valid["package_count"] >= 2
    assert valid["mcp_tool_count"] >= 3
    assert valid["platform_package_count"] >= 1

    invalid: list[tuple[dict, dict, dict]] = []
    for phrase in (
        "official support", "official integration", "official Ark integration",
        "cloud partner", "partnered with", "marketplace listed",
        "verified marketplace support", "integration completed", "ecosystem adoption",
    ):
        bad_card = copy.deepcopy(mcp_card)
        bad_card["purpose"] = phrase
        invalid.append((bad_card, copy.deepcopy(tools), copy.deepcopy(mapping)))
    for key in ("integration_executed", "official_support", "partner_contact", "marketplace_submission", "production_ready"):
        bad_card = copy.deepcopy(mcp_card)
        bad_card["truth_boundary"][key] = True
        invalid.append((bad_card, copy.deepcopy(tools), copy.deepcopy(mapping)))
        bad_mapping = copy.deepcopy(mapping)
        bad_mapping["truth_boundary"][key] = True
        invalid.append((copy.deepcopy(mcp_card), copy.deepcopy(tools), bad_mapping))
    for mutate in (
        lambda c, t, m: c.update({"status": "INTEGRATED"}),
        lambda c, t, m: t.update({"tools": t["tools"][:2]}),
        lambda c, t, m: t["tools"][2].update({"status": "LOCAL_TESTED"}),
        lambda c, t, m: t["tools"][0].update({"authorization_performed": True}),
        lambda c, t, m: m["mappings"][0].update({"status": "LOCAL_TESTED"}),
        lambda c, t, m: m["mappings"].pop(),
        lambda c, t, m: m["truth_boundary"].update({"saee_mapping_local_tested": True}),
        lambda c, t, m: c.update({"runtime_ref": "missing.py"}),
    ):
        c, t, m = copy.deepcopy(mcp_card), copy.deepcopy(tools), copy.deepcopy(mapping)
        mutate(c, t, m)
        invalid.append((c, t, m))
    assert len(invalid) >= 20
    assert all(validate_entry_data(c, t, m)["valid"] is False for c, t, m in invalid)

    baseline = json.dumps(valid, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        assert json.dumps(validate_entry_packages(), ensure_ascii=False, sort_keys=True, separators=(",", ":")) == baseline

    tree = ast.parse(SERVICE.read_text(encoding="utf-8"))
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
    assert not ({"socket", "subprocess", "requests", "urllib", "httpx", "aiohttp", "smtplib"} & imports)
    assert all(valid[key] is False for key in (
        "network_accessed", "subprocess_started", "external_execution", "integration_executed",
        "official_support", "partner_contact", "marketplace_submission", "production_ready",
    ))

    print("SAEE_ECOSYSTEM_ENTRY_PACKAGE_SMOKE: PASS")
    print(f"packages={valid['package_count']}/2")
    print(f"mcp_tools={valid['mcp_tool_count']}/3")
    print(f"platform_packages={valid['platform_package_count']}/1")
    print(f"invalid_cases={len(invalid)}")
    print("deterministic_runs=5/5")
    print("mcp_package=true")
    print("volcengine_package=true")
    print("capability_reference_valid=true")
    print("boundary_valid=true")
    print("rehearse_agent=CONTRACT_ONLY")
    print("integration_executed=false")
    print("official_support=false")
    print("partner_contact=false")
    print("marketplace_submission=false")
    print("production_ready=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

