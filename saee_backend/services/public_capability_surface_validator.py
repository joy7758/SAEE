"""Offline validator for the SAEE Agent-Native Public Capability Surface v0.1."""

from __future__ import annotations

import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas/saee-public-capability-surface.schema.v0.1.json"
EXPECTED_CAPABILITIES = {"saee.agent-reliability", "saee.evidence-evaluation"}
EXPECTED_OPERATIONS = {"saee.evaluate_agent_run", "saee.evaluate_evidence"}
EXPECTED_PROTOCOLS = {"MCP", "HTTP Contract"}
FORBIDDEN_AFFIRMATIVE_CLAIMS = (
    re.compile(r"\b(?:certified|approved|safe)\b", re.I),
    re.compile(r"\bindustry\s+standard\b", re.I),
    re.compile(r"\btrusted\s+by\s+all\s+agents\b", re.I),
    re.compile(r"\bmarketplace\s+listed\b", re.I),
)
SECRET_VALUE_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bbce-v\d+/[A-Za-z0-9/_-]{20,}\b"),
)
PRIVATE_PARTS = {"saee_backend", "scripts", ".git", ".env", "private", "secrets"}


def _result(valid: bool, reason_codes: list[str], surface: Any = None) -> dict[str, Any]:
    capabilities = surface.get("capabilities", []) if isinstance(surface, dict) else []
    protocols = surface.get("protocols", []) if isinstance(surface, dict) else []
    return {
        "valid": valid,
        "reason_codes": reason_codes,
        "capability_count": len(capabilities) if isinstance(capabilities, list) else 0,
        "protocol_count": len(protocols) if isinstance(protocols, list) else 0,
        "public_surface": valid,
        "public_api": False,
        "public_service": False,
        "production_ready": False,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
    }


def _safe_public_ref(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or "://" in ref or "\\" in ref:
        return False
    clean = ref.split("#", 1)[0]
    path = PurePosixPath(clean)
    if path.is_absolute() or ".." in path.parts or any(part.lower() in PRIVATE_PARTS for part in path.parts):
        return False
    resolved = (ROOT / clean).resolve()
    try:
        resolved.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return resolved.is_file()


def _has_secret_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower().replace("-", "_")
            if normalized in {"api_key", "apikey", "credential", "credentials", "secret", "token"}:
                return True
            if _has_secret_key(child):
                return True
    elif isinstance(value, list):
        return any(_has_secret_key(child) for child in value)
    return False


def validate_public_capability_surface(surface: Any, index: Any) -> dict[str, Any]:
    """Validate checked-in public-safe metadata without resolving any network resource."""

    if not isinstance(surface, dict) or not isinstance(index, dict):
        return _result(False, ["PUBLIC_SURFACE_INVALID"], surface)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    if list(Draft202012Validator(schema).iter_errors(surface)):
        return _result(False, ["PUBLIC_SURFACE_SCHEMA_INVALID"], surface)
    if {item.get("id") for item in surface["capabilities"]} != EXPECTED_CAPABILITIES:
        return _result(False, ["PUBLIC_SURFACE_CAPABILITY_SET_INVALID"], surface)
    if {item.get("operation_id") for item in surface["available_operations"]} != EXPECTED_OPERATIONS:
        return _result(False, ["PUBLIC_SURFACE_OPERATION_SET_INVALID"], surface)
    if set(surface["protocols"]) != EXPECTED_PROTOCOLS:
        return _result(False, ["PUBLIC_SURFACE_PROTOCOL_SET_INVALID"], surface)
    if any(not _safe_public_ref(ref) for ref in surface["references"].values()):
        return _result(False, ["PUBLIC_SURFACE_REFERENCE_INVALID"], surface)
    required_index = {"capability_reference", "limitations_reference", "quick_understanding_reference", "discovery_validation_reference", "alpha_release_reference", "ecosystem_validation_preparation_reference"}
    if not required_index.issubset(index) or any(not _safe_public_ref(index[key]) for key in required_index):
        return _result(False, ["PUBLIC_SURFACE_INDEX_REFERENCE_INVALID"], surface)
    index_refs = [item.get("reference") for item in index.get("capabilities", [])]
    if len(index_refs) < 2 or any(not _safe_public_ref(ref) for ref in index_refs):
        return _result(False, ["PUBLIC_SURFACE_INDEX_CAPABILITY_INVALID"], surface)
    truth = surface["truth_boundary"]
    if truth.get("public_product_operation_count") != len(EXPECTED_OPERATIONS):
        return _result(False, ["PUBLIC_SURFACE_OPERATION_COUNT_INVALID"], surface)
    index_truth = {key: index.get(key) for key in ("publicly_deployed", "public_api", "public_service", "production_ready")}
    if any(value is not False for value in index_truth.values()) or any(
        truth[field] is not False
        for field in ("publicly_deployed", "public_api", "public_service", "marketplace_listed", "external_agents_connected", "customer_data", "industry_standard_claimed", "certification_claimed", "production_ready")
    ):
        return _result(False, ["PUBLIC_SURFACE_BOUNDARY_OVERCLAIM"], surface)
    combined = json.dumps({"surface": surface, "index": index}, ensure_ascii=False, sort_keys=True)
    if any(pattern.search(combined) for pattern in FORBIDDEN_AFFIRMATIVE_CLAIMS):
        return _result(False, ["PUBLIC_SURFACE_FORBIDDEN_CLAIM"], surface)
    if _has_secret_key(surface) or _has_secret_key(index) or any(pattern.search(combined) for pattern in SECRET_VALUE_PATTERNS):
        return _result(False, ["PUBLIC_SURFACE_SECRET_DETECTED"], surface)
    if any(operation.get("public_endpoint") is not None for operation in surface["available_operations"]):
        return _result(False, ["PUBLIC_SURFACE_ENDPOINT_FORBIDDEN"], surface)
    return _result(True, [], surface)
