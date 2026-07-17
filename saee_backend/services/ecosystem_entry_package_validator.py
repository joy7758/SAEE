"""Offline validator for SAEE Ecosystem Entry Package v1.0."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
MCP_ROOT = ROOT / "ecosystem/mcp-entry-package-v1"
ARK_ROOT = ROOT / "ecosystem/volcengine-ark-entry-package-v0.1"
MAPPING_PATH = ROOT / "agent-interface/ecosystem/saee-volcengine-capability-mapping.v0.1.json"
EXPECTED_TOOLS = {
    "evaluate_rehearsal_run": "LOCAL_TESTED",
    "evaluate_evidence": "LOCAL_TESTED",
    "rehearse_agent": "CONTRACT_ONLY",
}
EXPECTED_SURFACES = {"FUNCTION_CALLING", "MCP", "HTTP_CAPABILITY"}
MCP_FILES = {"README.md", "capability-card.json", "mcp-tools.json", "agent-usage-guide.md", "integration-flow.md", "limitations.md"}
ARK_FILES = {"README.md", "integration-model.md", "capability-mapping.json", "mcp-mapping.json", "http-mapping.json", "limitations.md"}
FORBIDDEN = (
    "official support", "official integration", "official ark integration",
    "cloud partner", "partnered with", "marketplace listed",
    "verified marketplace support", "integration completed", "ecosystem adoption",
)
NEGATIONS = ("not ", "no ", "false", "does not", "do not", "不是", "不", "未", "没有")


def _result(valid: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reasons,
        "package_count": 2 if valid else 0,
        "mcp_tool_count": 3 if valid else 0,
        "platform_package_count": 1 if valid else 0,
        "mcp_package": valid,
        "volcengine_package": valid,
        "capability_reference_valid": valid,
        "boundary_valid": valid,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "integration_executed": False,
        "official_support": False,
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


def _has_unsupported_claim(value: Any) -> bool:
    for text in _strings(value):
        normalized = re.sub(r"\s+", " ", text.lower()).strip()
        for phrase in FORBIDDEN:
            if phrase not in normalized:
                continue
            prefix = normalized[: normalized.index(phrase)]
            if not any(marker in prefix[-40:] for marker in NEGATIONS):
                return True
    return False


def _local_file(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or "://" in ref or "\\" in ref:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def validate_entry_data(mcp_card: Any, tools: Any, mapping: Any) -> dict[str, Any]:
    if not all(isinstance(item, dict) for item in (mcp_card, tools, mapping)):
        return _result(False, ["ECOSYSTEM_ENTRY_DATA_INVALID"])
    if mcp_card.get("status") != "ECOSYSTEM_REVIEW_PREPARATION":
        return _result(False, ["ECOSYSTEM_ENTRY_MCP_STATUS_INVALID"])
    tool_items = tools.get("tools")
    if not isinstance(tool_items, list) or {item.get("name"): item.get("status") for item in tool_items if isinstance(item, dict)} != EXPECTED_TOOLS:
        return _result(False, ["ECOSYSTEM_ENTRY_TOOL_SET_INVALID"])
    if any(item.get("side_effects") is not False or item.get("authorization_performed") is not False for item in tool_items):
        return _result(False, ["ECOSYSTEM_ENTRY_TOOL_BOUNDARY_INVALID"])
    mappings = mapping.get("mappings")
    if not isinstance(mappings, list) or {item.get("entry_surface") for item in mappings if isinstance(item, dict)} != EXPECTED_SURFACES:
        return _result(False, ["ECOSYSTEM_ENTRY_ARK_SURFACE_INVALID"])
    if any(item.get("status") != "DESIGN_ONLY" for item in mappings):
        return _result(False, ["ECOSYSTEM_ENTRY_ARK_STATUS_INVALID"])
    for truth in (mcp_card.get("truth_boundary"), mapping.get("truth_boundary")):
        if not isinstance(truth, dict) or any(truth.get(key) is not False for key in (
            "integration_executed", "official_support", "partner_contact", "marketplace_submission", "production_ready"
        )):
            return _result(False, ["ECOSYSTEM_ENTRY_BOUNDARY_INVALID"])
    if mapping["truth_boundary"].get("saee_mapping_local_tested") is not False:
        return _result(False, ["ECOSYSTEM_ENTRY_ARK_TEST_CLAIM_INVALID"])
    refs = [
        mcp_card.get("tools_ref"), mcp_card.get("canonical_mcp_descriptor_ref"),
        mcp_card.get("canonical_adapter_ref"), mcp_card.get("runtime_ref"),
        mcp_card.get("ecosystem_demo_reference"),
        mcp_card.get("first_validation_candidate_reference"),
        mcp_card.get("first_external_validation_simulation_reference"),
        tools.get("canonical_descriptor_ref"),
    ]
    if any(not _local_file(ref) for ref in refs):
        return _result(False, ["ECOSYSTEM_ENTRY_REFERENCE_INVALID"])
    if _has_unsupported_claim({"mcp": mcp_card, "tools": tools, "mapping": mapping}):
        return _result(False, ["ECOSYSTEM_ENTRY_UNSUPPORTED_CLAIM"])
    return _result(True, [])


def validate_entry_packages() -> dict[str, Any]:
    if not MCP_ROOT.is_dir() or any(not (MCP_ROOT / name).is_file() for name in MCP_FILES):
        return _result(False, ["ECOSYSTEM_ENTRY_MCP_PACKAGE_INCOMPLETE"])
    if not ARK_ROOT.is_dir() or any(not (ARK_ROOT / name).is_file() for name in ARK_FILES):
        return _result(False, ["ECOSYSTEM_ENTRY_ARK_PACKAGE_INCOMPLETE"])
    try:
        mcp_card = json.loads((MCP_ROOT / "capability-card.json").read_text(encoding="utf-8"))
        tools = json.loads((MCP_ROOT / "mcp-tools.json").read_text(encoding="utf-8"))
        mapping = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _result(False, ["ECOSYSTEM_ENTRY_PACKAGE_JSON_INVALID"])
    result = validate_entry_data(mcp_card, tools, mapping)
    if not result["valid"]:
        return result
    for name in ("capability-mapping.json", "mcp-mapping.json", "http-mapping.json"):
        try:
            payload = json.loads((ARK_ROOT / name).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            return _result(False, ["ECOSYSTEM_ENTRY_PACKAGE_JSON_INVALID"])
        if payload.get("status") != "DESIGN_ONLY" or payload.get("official_integration") is not False or payload.get("production_ready") is not False:
            return _result(False, ["ECOSYSTEM_ENTRY_ARK_PACKAGE_BOUNDARY_INVALID"])
        refs = [value for key, value in payload.items() if key.endswith("_ref")]
        if any(not _local_file(ref) for ref in refs):
            return _result(False, ["ECOSYSTEM_ENTRY_REFERENCE_INVALID"])
    review = ROOT / "docs/ecosystem/SAEE_ECOSYSTEM_ENTRY_PACKAGE_REVIEW.md"
    audit = ROOT / "docs/ecosystem/SAEE_ECOSYSTEM_ENTRY_ASSET_AUDIT.md"
    if not review.is_file() or not audit.is_file():
        return _result(False, ["ECOSYSTEM_ENTRY_DOCUMENT_MISSING"])
    return result
