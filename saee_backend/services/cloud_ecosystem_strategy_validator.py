"""Offline validator for SAEE Cloud Ecosystem Integration Strategy v1.0."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MATRIX_PATH = ROOT / "agent-interface/ecosystem/saee-cloud-ecosystem-priority-matrix.v0.1.json"
PACKAGE_ROOT = ROOT / "ecosystem/cloud-integration-package-v0.1"
EXPECTED_ECOSYSTEMS = {
    "VOLCENGINE_ARK", "BAIDU_QIANFAN", "ALIBABA_BAILIAN", "MCP_ECOSYSTEM", "GLOBAL_AGENT_PLATFORMS"
}
EXPECTED_TRUTH = {
    "cloud_ecosystem_strategy": True,
    "cloud_integration_executed": False,
    "official_support": False,
    "partner_contact": False,
    "marketplace_submission": False,
    "marketplace_listed": False,
    "external_agents_connected": False,
    "customer_validated": False,
    "production_ready": False,
}
REQUIRED_DOCS = (
    "docs/ecosystem/SAEE_CLOUD_ECOSYSTEM_ASSET_AUDIT.md",
    "docs/ecosystem/SAEE_CLOUD_ECOSYSTEM_INTEGRATION_STRATEGY.md",
    "docs/ecosystem/SAEE_VOLCENGINE_ARK_INTEGRATION_STRATEGY.md",
    "docs/ecosystem/SAEE_BAIDU_QIANFAN_INTEGRATION_STRATEGY.md",
    "docs/ecosystem/SAEE_ALIBABA_BAILIAN_INTEGRATION_STRATEGY.md",
    "docs/ecosystem/SAEE_MCP_ECOSYSTEM_POSITIONING.md",
)
REQUIRED_PACKAGE_FILES = {
    "README.md", "capability-card.json", "integration-model.md",
    "mcp-definition.json", "http-definition.json", "limitations.md",
}
FORBIDDEN_CLAIMS = (
    "official support", "official integration", "cloud partner", "partnered with",
    "marketplace listed", "marketplace submission completed", "integration completed",
)
NEGATIONS = ("not ", "no ", "false", "without ", "does not", "do not", "不是", "不", "未", "没有")


def _result(valid: bool, reasons: list[str], platform_count: int = 0) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reasons,
        "strategy_defined": valid,
        "priority_matrix": valid,
        "integration_package": valid,
        "boundary_defined": valid,
        "platform_count": platform_count,
        "document_count": len(REQUIRED_DOCS) if valid else 0,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "cloud_integration_executed": False,
        "partner_contact": False,
        "marketplace_submission": False,
        "production_ready": False,
    }


def _strings(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [text for item in value for text in _strings(item)]
    if isinstance(value, dict):
        return [text for item in value.values() for text in _strings(item)]
    return []


def _unsupported_claims(value: Any) -> list[str]:
    found: set[str] = set()
    for text in _strings(value):
        normalized = re.sub(r"\s+", " ", text.lower()).strip()
        for phrase in FORBIDDEN_CLAIMS:
            if phrase not in normalized:
                continue
            prefix = normalized[: normalized.index(phrase)]
            if any(marker in prefix[-40:] for marker in NEGATIONS):
                continue
            found.add(phrase)
    return sorted(found)


def _local_file(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or "://" in ref or "\\" in ref:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def validate_priority_matrix(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _result(False, ["CLOUD_ECOSYSTEM_MATRIX_INVALID"])
    platforms = value.get("platforms")
    if not isinstance(platforms, list) or len(platforms) < 5:
        return _result(False, ["CLOUD_ECOSYSTEM_PLATFORM_COUNT_INVALID"])
    if {item.get("ecosystem") for item in platforms if isinstance(item, dict)} != EXPECTED_ECOSYSTEMS:
        return _result(False, ["CLOUD_ECOSYSTEM_SET_INVALID"])
    required = {"ecosystem", "integration_surface", "strategic_fit", "technical_readiness", "commercial_readiness", "priority", "limitations"}
    if any(not isinstance(item, dict) or not required.issubset(item) for item in platforms):
        return _result(False, ["CLOUD_ECOSYSTEM_ENTRY_INVALID"])
    if any(item["commercial_readiness"] != "STRATEGY_ONLY" for item in platforms):
        return _result(False, ["CLOUD_ECOSYSTEM_COMMERCIAL_OVERCLAIM"])
    if value.get("truth_boundary") != EXPECTED_TRUTH:
        return _result(False, ["CLOUD_ECOSYSTEM_TRUTH_BOUNDARY_INVALID"])
    if not _local_file(value.get("ecosystem_entry_package_reference")):
        return _result(False, ["CLOUD_ECOSYSTEM_ENTRY_PACKAGE_REFERENCE_INVALID"])
    if _unsupported_claims(value):
        return _result(False, ["CLOUD_ECOSYSTEM_UNSUPPORTED_CLAIM"])
    return _result(True, [], len(platforms))


def validate_strategy_package() -> dict[str, Any]:
    try:
        matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _result(False, ["CLOUD_ECOSYSTEM_MATRIX_INVALID"])
    result = validate_priority_matrix(matrix)
    if not result["valid"]:
        return result
    if not all((ROOT / ref).is_file() for ref in REQUIRED_DOCS):
        return _result(False, ["CLOUD_ECOSYSTEM_DOCUMENT_MISSING"])
    if not PACKAGE_ROOT.is_dir() or any(not (PACKAGE_ROOT / name).is_file() for name in REQUIRED_PACKAGE_FILES):
        return _result(False, ["CLOUD_ECOSYSTEM_PACKAGE_INCOMPLETE"])
    for name in ("capability-card.json", "mcp-definition.json", "http-definition.json"):
        try:
            payload = json.loads((PACKAGE_ROOT / name).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return _result(False, ["CLOUD_ECOSYSTEM_PACKAGE_JSON_INVALID"])
        refs = [value for key, value in payload.items() if key.endswith("_ref")]
        if any(not _local_file(ref) for ref in refs):
            return _result(False, ["CLOUD_ECOSYSTEM_PACKAGE_REFERENCE_INVALID"])
        if payload.get("production_ready") is True or payload.get("official_platform_integration") is True:
            return _result(False, ["CLOUD_ECOSYSTEM_PACKAGE_BOUNDARY_INVALID"])
    card = json.loads((PACKAGE_ROOT / "capability-card.json").read_text(encoding="utf-8"))
    if card.get("status") != "PREPARATION_ONLY" or card.get("truth_boundary", {}).get("cloud_integration_executed") is not False:
        return _result(False, ["CLOUD_ECOSYSTEM_PACKAGE_BOUNDARY_INVALID"])
    return result
