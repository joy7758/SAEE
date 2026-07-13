"""Load the checked-in Capability Package without remote resolution."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
PACKAGE = ROOT / "capability-package"
CAPABILITY_ID = "saee.agent-reliability"
EXPECTED_OPERATIONS = {
    "evaluate_agent_run": "implemented_local_offline_alpha",
    "evaluate_evidence": "implemented_local_offline_prototype",
    "rehearse_agent": "contract_only",
}


class CapabilityPackageError(ValueError):
    """The checked-in Package and local Runtime are incompatible."""


def _load(name: str) -> dict[str, Any]:
    value = json.loads((PACKAGE / name).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CapabilityPackageError(f"CAPABILITY_PACKAGE_INVALID: {name}")
    return value


def load_capability_registry() -> dict[str, Any]:
    """Return the fixed operation registry after Package compatibility checks."""

    manifest = _load("manifest.json")
    card = _load("capability-card.json")
    mcp = _load("mcp-tool.json")
    if manifest.get("package_id") != CAPABILITY_ID or card.get("id") != CAPABILITY_ID:
        raise CapabilityPackageError("CAPABILITY_PACKAGE_ID_MISMATCH")
    manifest_operations = {
        item.get("operation_id"): item.get("status") for item in manifest.get("operations", [])
    }
    card_operations = {
        item.get("operation_id"): item.get("implementation_status") for item in card.get("capabilities", [])
    }
    mcp_operations = {item.get("name") for item in mcp.get("tools", [])}
    if manifest_operations != EXPECTED_OPERATIONS:
        raise CapabilityPackageError("CAPABILITY_PACKAGE_OPERATION_DRIFT")
    expected_card = dict(EXPECTED_OPERATIONS)
    expected_card["rehearse_agent"] = "contract_only"
    if card_operations != expected_card or mcp_operations != set(EXPECTED_OPERATIONS):
        raise CapabilityPackageError("CAPABILITY_PACKAGE_SURFACE_DRIFT")
    return {
        "capability_id": CAPABILITY_ID,
        "runtime_stage": "local_alpha",
        "operations": dict(EXPECTED_OPERATIONS),
        "package_operations_verified": True,
        "hidden_operations": [],
        "network_api_available": False,
        "public_service": False,
        "standard_mcp_transport": False,
        "production_ready": False,
    }

