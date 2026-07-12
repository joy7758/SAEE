#!/usr/bin/env python3
"""Offline deterministic validation for the public SAEE product center."""

from __future__ import annotations

import copy
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAP = ROOT / "docs/product/saee-product-ecosystem-map.v1.0.json"
README = ROOT / "README.md"
AGENT_INDEX = ROOT / "agent-index.json"
REQUIRED_DOCS = (
    ROOT / "docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md",
    ROOT / "docs/product/SAEE_MODULE_REGISTRY.md",
    ROOT / "docs/product/SAEE_GITHUB_ASSET_CONSOLIDATION_MAP.md",
    ROOT / "docs/product/SAEE_PUBLIC_POSITIONING.md",
    ROOT / "docs/ecosystem/SAEE_CLOUD_ECOSYSTEM_POSITIONING.md",
)
SECTIONS = ("为什么需要 SAEE", "核心能力", "产品架构", "快速开始", "MCP 支持", "云生态路线", "研究基础", "限制声明")


def validate(value: object, readme: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["MAP_NOT_OBJECT"]
    identity = value.get("canonical_identity", {})
    if identity.get("theory_name") != "Silicon-Amplified Evolutionary Ecology": errors.append("THEORY_IDENTITY_DRIFT")
    if identity.get("engineering_core") != "Digital Biosphere Evolution Engine": errors.append("ENGINEERING_CORE_DRIFT")
    if identity.get("product_surface") != "Agent Reliability Evaluation Capability Layer": errors.append("PRODUCT_SURFACE_DRIFT")
    if identity.get("primary_language") != "zh-CN": errors.append("PRIMARY_LANGUAGE_INVALID")
    modules = value.get("modules", [])
    ids = [item.get("module_id") for item in modules if isinstance(item, dict)]
    if len(modules) < 10: errors.append("MODULE_COUNT_INSUFFICIENT")
    if len(ids) != len(set(ids)): errors.append("MODULE_ID_DUPLICATE")
    if any(str(item.get("source", "")).startswith(("/Users/", "/home/")) for item in modules if isinstance(item, dict)): errors.append("LOCAL_PATH_EXPOSED")
    if any(item.get("core") and item.get("module_id") in {"audit_evidence", "evidence_engine_reference", "mcp_interface"} for item in modules if isinstance(item, dict)): errors.append("AUDIT_FIRST_DRIFT")
    truth = value.get("truth_boundary", {})
    if not truth or any(truth.values()): errors.append("TRUTH_BOUNDARY_INVALID")
    if not all(section in readme for section in SECTIONS): errors.append("README_SECTION_MISSING")
    if not readme.startswith("# SAEE 智能体可靠性评估基础设施"): errors.append("README_CHINESE_FIRST_INVALID")
    if "Smart Agent Execution & Evidence" in readme: errors.append("CANONICAL_RENAME_FORBIDDEN")
    return errors


def main() -> int:
    value = json.loads(MAP.read_text(encoding="utf-8"))
    readme = README.read_text(encoding="utf-8")
    assert not validate(value, readme)
    assert all(path.is_file() and path.read_text(encoding="utf-8").strip() for path in REQUIRED_DOCS)
    index = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    assert index["language"] == {"primary": "zh-CN", "secondary": "en"}
    assert json.loads((ROOT / "docs/agent-index.json").read_text(encoding="utf-8")) == index
    assert (ROOT / "docs/llms.txt").read_text(encoding="utf-8") == (ROOT / "llms.txt").read_text(encoding="utf-8")

    invalid: list[tuple[dict, str]] = []
    for field, bad in (("theory_name", "Other"), ("engineering_core", "Audit Engine"), ("product_surface", "Generic Agent OS"), ("primary_language", "en")):
        item = copy.deepcopy(value); item["canonical_identity"][field] = bad; invalid.append((item, readme))
    item = copy.deepcopy(value); item["modules"] = item["modules"][:2]; invalid.append((item, readme))
    item = copy.deepcopy(value); item["modules"][0]["module_id"] = item["modules"][1]["module_id"]; invalid.append((item, readme))
    item = copy.deepcopy(value); item["modules"][0]["source"] = "/Users/example/private"; invalid.append((item, readme))
    for module_id in ("audit_evidence", "evidence_engine_reference", "mcp_interface"):
        item = copy.deepcopy(value); next(row for row in item["modules"] if row["module_id"] == module_id)["core"] = True; invalid.append((item, readme))
    for key in value["truth_boundary"]:
        item = copy.deepcopy(value); item["truth_boundary"][key] = True; invalid.append((item, readme))
    invalid.append((copy.deepcopy(value), readme.replace("为什么需要 SAEE", "缺失章节")))
    invalid.append((copy.deepcopy(value), "# SAEE Smart Agent Execution & Evidence\n" + readme))
    assert len(invalid) >= 15
    assert all(validate(item, text) for item, text in invalid)
    baseline = json.dumps(validate(value, readme), sort_keys=True)
    for _ in range(5): assert json.dumps(validate(value, readme), sort_keys=True) == baseline

    print("SAEE_PRODUCT_CONSOLIDATION_SMOKE: PASS")
    print("product_identity=true")
    print(f"module_mapping={len(value['modules'])}/11")
    print("README_complete=true")
    print("language_policy=zh-CN_primary_en_secondary")
    print("boundary_statements=true")
    print(f"invalid_cases={len(invalid)}")
    print("deterministic_runs=5/5")
    print("private_core_exported=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
