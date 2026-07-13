"""Offline consistency validator for SAEE Capability Alpha truth surfaces."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from saee_backend.services.capability_runtime.capability_registry_loader import load_capability_registry


ROOT = Path(__file__).resolve().parents[2]
SOURCE_REFERENCES = {
    "CAPABILITY_OBJECT": "agent-interface/registry/objects/saee-evidence-adequacy-capability-object.v0.1.json",
    "CAPABILITY_REGISTRY": "agent-interface/registry/saee-capability-card.v0.1.json",
    "CAPABILITY_PACKAGE": "capability-package/manifest.json",
    "ALPHA_RELEASE_MANIFEST": "agent-interface/release/saee-alpha-release-manifest.v0.1.json",
    "PUBLIC_CAPABILITY_SURFACE": "agent-interface/public/saee-public-capability-surface.v0.1.json",
    "MCP_METADATA": "agent-interface/mcp/saee-capability-mcp-adapter.v0.1.json",
    "HTTP_METADATA": "agent-interface/http/saee-capability-http-adapter.v0.1.json",
    "CAPABILITY_RUNTIME": "saee_backend/services/capability_runtime/capability_registry_loader.py",
}
PRIMARY_CAPABILITY = "saee.agent-reliability"
CANONICAL_CAPABILITIES = {PRIMARY_CAPABILITY, "saee.evidence-evaluation"}
CAPABILITY_ALIASES = {"saee.evidence-adequacy": "saee.evidence-evaluation"}
EXPECTED_OPERATIONS = {"evaluate_agent_run", "evaluate_evidence", "rehearse_agent"}
EXPECTED_PUBLIC_OPERATIONS = {"saee.evaluate_agent_run", "saee.evaluate_evidence"}
EXPECTED_STATUS = {
    "evaluate_agent_run": "IMPLEMENTED",
    "evaluate_evidence": "IMPLEMENTED",
    "rehearse_agent": "CONTRACT_ONLY",
}
EXPECTED_PROTOCOLS = {"MCP", "HTTP Contract"}


def _load(ref: str) -> dict[str, Any]:
    value = json.loads((ROOT / ref).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"TRUTH_SOURCE_INVALID:{ref}")
    return value


def load_truth_sources() -> dict[str, dict[str, Any]]:
    """Load eight checked-in truth sources; do not invoke any capability."""

    return {
        "object": _load(SOURCE_REFERENCES["CAPABILITY_OBJECT"]),
        "registry": _load(SOURCE_REFERENCES["CAPABILITY_REGISTRY"]),
        "package": _load(SOURCE_REFERENCES["CAPABILITY_PACKAGE"]),
        "release": _load(SOURCE_REFERENCES["ALPHA_RELEASE_MANIFEST"]),
        "public": _load(SOURCE_REFERENCES["PUBLIC_CAPABILITY_SURFACE"]),
        "mcp": _load(SOURCE_REFERENCES["MCP_METADATA"]),
        "http": _load(SOURCE_REFERENCES["HTTP_METADATA"]),
        "runtime": load_capability_registry(),
    }


def _operation_map(items: Any, id_field: str = "operation_id") -> dict[str, str]:
    if not isinstance(items, list):
        return {}
    result: dict[str, str] = {}
    for item in items:
        if isinstance(item, dict) and isinstance(item.get(id_field), str):
            result[item[id_field]] = str(item.get("status", ""))
    return result


def _normalize_status(value: str) -> str:
    if value in {"implemented_local_offline_alpha", "implemented_local_offline_prototype"}:
        return "IMPLEMENTED"
    if value == "contract_only":
        return "CONTRACT_ONLY"
    return f"UNKNOWN:{value}"


def validate_truth_sources(sources: Any) -> dict[str, Any]:
    """Validate identity, operations, lifecycle, protocols and boundaries."""

    if not isinstance(sources, dict) or set(sources) != {"object", "registry", "package", "release", "public", "mcp", "http", "runtime"}:
        raise ValueError("TRUTH_SOURCE_SET_INVALID")
    obj, registry, package = sources["object"], sources["registry"], sources["package"]
    release, public, mcp = sources["release"], sources["public"], sources["mcp"]
    http, runtime = sources["http"], sources["runtime"]
    conflicts: list[str] = []

    object_id = obj.get("identity", {}).get("capability_id")
    registry_id = registry.get("capability_id")
    release_ids = {item.get("capability_id") for item in release.get("capabilities", []) if isinstance(item, dict)}
    public_ids = {item.get("id") for item in public.get("capabilities", []) if isinstance(item, dict)}
    identity_match = (
        package.get("package_id") == PRIMARY_CAPABILITY
        and mcp.get("capability_id") == PRIMARY_CAPABILITY
        and runtime.get("capability_id") == PRIMARY_CAPABILITY
        and release_ids == CANONICAL_CAPABILITIES
        and public_ids == CANONICAL_CAPABILITIES
        and object_id == registry_id == "saee.evidence-adequacy"
        and CAPABILITY_ALIASES.get(str(object_id)) == "saee.evidence-evaluation"
        and http.get("runtime_reference") == mcp.get("runtime_reference")
    )
    if not identity_match:
        conflicts.append("TRUTH_IDENTITY_MISMATCH")

    version_match = (
        obj.get("identity", {}).get("version") == registry.get("version") == "0.1"
        and package.get("manifest_version") == "1.0.0"
        and release.get("version") == "0.1.0"
        and mcp.get("adapter_version") == http.get("adapter_version") == "0.1.0"
    )
    if not version_match:
        conflicts.append("TRUTH_VERSION_NAMESPACE_MISMATCH")

    operation_maps = {
        "package": _operation_map(package.get("operations")),
        "release": _operation_map(release.get("operations")),
        "runtime": dict(runtime.get("operations", {})),
    }
    operation_sets = [set(mapping) for mapping in operation_maps.values()]
    operation_sets.extend([set(mcp.get("tools", [])), set(http.get("endpoints", {}).values())])
    public_operation_map = _operation_map(public.get("available_operations"))
    operation_match = (
        all(operation_set == EXPECTED_OPERATIONS for operation_set in operation_sets)
        and set(public_operation_map) == EXPECTED_PUBLIC_OPERATIONS
        and public.get("truth_boundary", {}).get("public_product_operation_count") == 2
    )
    if not operation_match:
        conflicts.append("TRUTH_OPERATION_SET_MISMATCH")

    normalized = {
        source: {operation: _normalize_status(status) for operation, status in mapping.items()}
        for source, mapping in operation_maps.items()
    }
    normalized_public = {
        operation.removeprefix("saee."): _normalize_status(status)
        for operation, status in public_operation_map.items()
    }
    expected_public_status = {
        "evaluate_agent_run": "IMPLEMENTED",
        "evaluate_evidence": "IMPLEMENTED",
    }
    status_match = (
        all(mapping == EXPECTED_STATUS for mapping in normalized.values())
        and normalized_public == expected_public_status
    )
    if not status_match:
        conflicts.append("TRUTH_OPERATION_STATUS_MISMATCH")

    lifecycle_match = (
        obj.get("lifecycle", {}).get("state") == registry.get("lifecycle_state") == "LOCAL_PROTOTYPE"
        and package.get("package_stage") == "local_contract_alpha"
        and release.get("release_status") == "ALPHA_PREPARATION"
        and {item.get("status") for item in public.get("capabilities", [])} == {"local_alpha", "local_prototype"}
        and mcp.get("stage") == "local_stdio_alpha"
        and http.get("stage") == "localhost_alpha"
        and runtime.get("runtime_stage") == "local_alpha"
    )
    if not lifecycle_match:
        conflicts.append("TRUTH_LIFECYCLE_MISMATCH")

    protocol_match = (
        set(release.get("protocols", [])) == EXPECTED_PROTOCOLS
        and set(public.get("protocols", [])) == EXPECTED_PROTOCOLS
        and mcp.get("transport") == "stdio"
        and mcp.get("truth_boundary", {}).get("external_mcp_interoperability_validated") is False
        and http.get("bind_address") == "127.0.0.1"
        and http.get("truth_boundary", {}).get("localhost_binding") is True
        and http.get("truth_boundary", {}).get("network_public_access") is False
    )
    if not protocol_match:
        if mcp.get("truth_boundary", {}).get("external_mcp_interoperability_validated") is True:
            conflicts.append("TRUTH_PROTOCOL_MCP_EXAGGERATION")
        elif http.get("bind_address") != "127.0.0.1" or http.get("truth_boundary", {}).get("network_public_access") is not False:
            conflicts.append("TRUTH_PROTOCOL_HTTP_PUBLIC_BINDING")
        else:
            conflicts.append("TRUTH_PROTOCOL_MISMATCH")

    package_truth, release_truth = package.get("truth_boundary", {}), release.get("truth_boundary", {})
    public_truth, mcp_truth = public.get("truth_boundary", {}), mcp.get("truth_boundary", {})
    http_truth, object_truth = http.get("truth_boundary", {}), obj.get("truth_boundary", {})
    registry_validation = registry.get("validation_state", {})

    if release_truth.get("production_ready") is not False or package_truth.get("production_ready") is not False or public_truth.get("production_ready") is not False or mcp_truth.get("production_ready") is not False or http_truth.get("production_ready") is not False or runtime.get("production_ready") is not False or object_truth.get("production_ready") is not False:
        conflicts.append("TRUTH_BOUNDARY_PRODUCTION_ESCALATION")
    if release_truth.get("marketplace_listed") is not False or package_truth.get("marketplace_listed") is not False or public_truth.get("marketplace_listed") is not False:
        conflicts.append("TRUTH_BOUNDARY_MARKETPLACE_CLAIM")
    if release_truth.get("public_api") is not False or release_truth.get("public_service") is not False or public_truth.get("public_api") is not False or public_truth.get("public_service") is not False or mcp_truth.get("public_service") is not False or http_truth.get("public_service") is not False or runtime.get("public_service") is not False:
        conflicts.append("TRUTH_BOUNDARY_PUBLIC_SERVICE_CLAIM")
    if release_truth.get("external_adoption") is not False or object_truth.get("adoption_validated") is not False or registry_validation.get("adoption_validated") is not False:
        conflicts.append("TRUTH_BOUNDARY_EXTERNAL_ADOPTION_CLAIM")
    if public_truth.get("certification_claimed") is not False:
        conflicts.append("TRUTH_BOUNDARY_CERTIFICATION_CLAIM")
    if release_truth.get("customer_validated") is not False:
        conflicts.append("TRUTH_BOUNDARY_CUSTOMER_VALIDATION_CLAIM")
    if release_truth.get("public_release") is not False or package_truth.get("public_release") is not False:
        conflicts.append("TRUTH_BOUNDARY_PUBLIC_RELEASE_CLAIM")

    boundary_codes = [code for code in conflicts if code.startswith("TRUTH_BOUNDARY_")]
    boundary_match = not boundary_codes
    conflicts = list(dict.fromkeys(conflicts))
    valid = not conflicts
    return {
        "validation_version": "0.1",
        "capability_id": PRIMARY_CAPABILITY,
        "version": "0.1.0",
        "checked_sources": list(SOURCE_REFERENCES),
        "capability_aliases": dict(CAPABILITY_ALIASES),
        "version_namespaces": {
            "capability_object": "0.1",
            "package_contract": "1.0.0",
            "alpha_release": "0.1.0",
            "adapter": "0.1.0",
        },
        "identity_match": identity_match and version_match,
        "operation_match": operation_match,
        "status_match": status_match,
        "lifecycle_match": lifecycle_match,
        "protocol_match": protocol_match,
        "boundary_match": boundary_match,
        "source_references": dict(SOURCE_REFERENCES),
        "conflicts_detected": not valid,
        "conflicts": conflicts,
        "limitations": [
            "Historical saee.evidence-adequacy is explicitly mapped to saee.evidence-evaluation.",
            "Artifact versions are validated within namespaces rather than treated as one universal version.",
            "MCP and HTTP metadata expose local transports only; no public interoperability is established.",
            "Consistency confirms descriptions agree but does not prove runtime correctness or external trust.",
            "No external agent, customer data, marketplace, adoption, or production environment is evaluated.",
            "A passing result does not authorize publication, deployment, certification, or lifecycle promotion."
        ],
        "truth_boundary": {
            "validation_only": True,
            "alpha_release": True,
            "public_release": False,
            "production_ready": False,
            "marketplace_listed": False,
            "external_adoption": False,
            "customer_validated": False,
            "external_trust_established": False,
            "certification_established": False,
        },
    }


def validate_current_capability_truth() -> dict[str, Any]:
    """Validate the current checked-in Alpha truth surfaces."""

    return validate_truth_sources(load_truth_sources())
