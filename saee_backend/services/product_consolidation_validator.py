"""Offline validator for the bounded SAEE product consolidation surface."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
MAP_PATH = ROOT / "agent-interface/product/saee-product-ecosystem-map.v1.0.json"
SCHEMA_PATH = ROOT / "schemas/saee-product-ecosystem-map.schema.v1.0.json"
README_PATH = ROOT / "README.md"
DOCS = {
    "asset_map": ROOT / "docs/product/SAEE_GITHUB_ASSET_CONSOLIDATION_MAP.md",
    "architecture": ROOT / "docs/product/SAEE_PRODUCT_ARCHITECTURE_V1.md",
    "module_registry": ROOT / "docs/product/SAEE_MODULE_REGISTRY.md",
    "positioning": ROOT / "docs/product/SAEE_PUBLIC_POSITIONING.md",
    "cloud": ROOT / "docs/ecosystem/SAEE_CLOUD_ECOSYSTEM_POSITIONING.md",
    "proposal": ROOT / "docs/product/SAEE_GITHUB_PRODUCT_CONSOLIDATION_EVOLUTION_PROPOSAL.md",
}
FORBIDDEN_IDENTITY = "Smart Agent Execution & Evidence"
REQUIRED_README_SECTIONS = {
    "为什么需要 SAEE", "核心能力", "产品架构", "快速开始", "MCP 支持", "云生态路线", "研究基础", "限制声明",
}


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_product_consolidation(value: Any, *, readme: str | None = None, documents: dict[str, str] | None = None) -> dict[str, Any]:
    reasons: list[str] = []
    if not isinstance(value, dict) or list(Draft202012Validator(_load(SCHEMA_PATH)).iter_errors(value)):
        reasons.append("PRODUCT_CONSOLIDATION_MAP_INVALID")
    else:
        identity = value["canonical_identity"]
        if identity["theory_name"] != "Silicon-Amplified Evolutionary Ecology" or identity["engineering_core"] != "Digital Biosphere Evolution Engine":
            reasons.append("PRODUCT_CONSOLIDATION_CANONICAL_IDENTITY_DRIFT")
        ids = [item["module_id"] for item in value["modules"]]
        if len(ids) != len(set(ids)):
            reasons.append("PRODUCT_CONSOLIDATION_MODULE_ID_DUPLICATE")
        if any(item["source"].startswith(("/Users/", "/home/", "C:\\")) for item in value["modules"]):
            reasons.append("PRODUCT_CONSOLIDATION_LOCAL_PATH_EXPOSED")
        if any(item["core"] and item["module_id"] in {"audit_evidence", "evidence_engine_reference", "mcp_interface"} for item in value["modules"]):
            reasons.append("PRODUCT_CONSOLIDATION_AUDIT_FIRST_DRIFT")
    text = README_PATH.read_text(encoding="utf-8") if readme is None else readme
    if not all(section in text for section in REQUIRED_README_SECTIONS):
        reasons.append("PRODUCT_CONSOLIDATION_README_INCOMPLETE")
    if "# SAEE 数字生物圈进化引擎" not in text or "Agent Reliability Evaluation Capability Layer" not in text:
        reasons.append("PRODUCT_CONSOLIDATION_LANGUAGE_OR_POSITIONING_INVALID")
    source_docs = {key: path.read_text(encoding="utf-8") for key, path in DOCS.items()} if documents is None else documents
    if set(source_docs) != set(DOCS) or any(not content.strip() for content in source_docs.values()):
        reasons.append("PRODUCT_CONSOLIDATION_DOCUMENT_SET_INVALID")
    # Discussion documents may quote a rejected identity while explaining why it
    # is incompatible. Reject only an actual README identity heading.
    if f"# SAEE {FORBIDDEN_IDENTITY}" in text:
        reasons.append("PRODUCT_CONSOLIDATION_FORBIDDEN_IDENTITY_REFRAME")
    if "historical_repository_notice_written=false" not in source_docs.get("asset_map", ""):
        reasons.append("PRODUCT_CONSOLIDATION_NOTICE_BOUNDARY_MISSING")
    return {
        "valid": not reasons,
        "reason_codes": list(dict.fromkeys(reasons)),
        "product_identity": not any("IDENTITY" in code for code in reasons),
        "module_mapping": not any(code in reasons for code in ("PRODUCT_CONSOLIDATION_MAP_INVALID", "PRODUCT_CONSOLIDATION_LOCAL_PATH_EXPOSED")),
        "README_complete": "PRODUCT_CONSOLIDATION_README_INCOMPLETE" not in reasons,
        "language_policy": "PRODUCT_CONSOLIDATION_LANGUAGE_OR_POSITIONING_INVALID" not in reasons,
        "boundary_statements": "PRODUCT_CONSOLIDATION_NOTICE_BOUNDARY_MISSING" not in reasons,
        "canonical_identity_changed": False,
        "historical_repository_notice_written": False,
        "repository_renamed": False,
        "history_rewritten": False,
        "public_release": False,
        "external_announcement": False,
        "production_ready": False,
    }


def validate_product_consolidation_repository() -> dict[str, Any]:
    Draft202012Validator.check_schema(_load(SCHEMA_PATH))
    return validate_product_consolidation(_load(MAP_PATH))
