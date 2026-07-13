"""Deterministic access to the canonical SAEE capability inventory.

The checked-in Capability Package manifest is the authority. This module does
not discover capabilities heuristically, invoke a model, start a server or
modify repository files.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "capability-package/manifest.json"
SCHEMA_PATH = ROOT / "schemas/saee-canonical-capability-inventory.schema.v1.json"
CANONICAL_SOURCE = "capability-package/manifest.json#canonical_inventory"


class CanonicalCapabilityInventoryError(ValueError):
    """Fail-closed capability lookup or validation error."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise CanonicalCapabilityInventoryError("INVENTORY_JSON_ROOT_INVALID", str(path))
    return value


def load_canonical_inventory() -> dict[str, Any]:
    """Load the repository authority without consulting a projection."""

    document = _load_json(MANIFEST_PATH)
    inventory = document.get("canonical_inventory")
    if not isinstance(inventory, dict):
        raise CanonicalCapabilityInventoryError(
            "CANONICAL_INVENTORY_MISSING",
            CANONICAL_SOURCE,
        )
    return inventory


def normalize_inventory(inventory: dict[str, Any]) -> dict[str, Any]:
    """Return a stable normalized view; source files are never rewritten."""

    normalized = copy.deepcopy(inventory)
    normalized["capabilities"] = sorted(
        normalized.get("capabilities", []),
        key=lambda item: item.get("capability_id", ""),
    )
    for capability in normalized["capabilities"]:
        capability["interfaces"] = sorted(
            capability.get("interfaces", []),
            key=lambda item: (
                item.get("interface_type", ""),
                item.get("role", ""),
                item.get("path", ""),
                item.get("tool_name") or "",
            ),
        )
        for field in (
            "aliases",
            "implementation_evidence",
            "test_evidence",
            "documentation",
            "supersedes",
            "superseded_by",
            "claims",
            "non_claims",
        ):
            capability[field] = sorted(capability.get(field, []))
    normalized["mcp_surfaces"] = sorted(
        normalized.get("mcp_surfaces", []),
        key=lambda item: item.get("surface_id", ""),
    )
    for surface in normalized["mcp_surfaces"]:
        surface["tools"] = sorted(surface.get("tools", []))
        surface["test_evidence"] = sorted(surface.get("test_evidence", []))
    return normalized


def canonical_inventory_json(inventory: dict[str, Any] | None = None) -> str:
    """Serialize the normalized inventory deterministically."""

    value = normalize_inventory(inventory or load_canonical_inventory())
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _repo_path_error(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return "must be a non-empty repository-relative path"
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        return "must not be absolute or contain '..'"
    return None


def _exists(relative_path: str) -> bool:
    return (ROOT / relative_path.split("#", 1)[0]).exists()


def _append_path_errors(
    errors: list[str],
    capability_id: str,
    field: str,
    paths: list[Any],
) -> None:
    for value in paths:
        problem = _repo_path_error(value)
        if problem:
            errors.append(f"{capability_id}.{field}: {value!r} {problem}")
        elif not _exists(value):
            errors.append(f"{capability_id}.{field}: missing path {value}")


def _cycle_errors(capabilities: list[dict[str, Any]]) -> list[str]:
    ids = {item.get("capability_id") for item in capabilities}
    graph = {
        item["capability_id"]: [
            target for target in item.get("superseded_by", []) if target in ids
        ]
        for item in capabilities
        if isinstance(item.get("capability_id"), str)
    }
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: tuple[str, ...]) -> None:
        if node in visiting:
            errors.append(f"deprecation cycle: {' -> '.join((*trail, node))}")
            return
        if node in visited:
            return
        visiting.add(node)
        for child in graph.get(node, []):
            visit(child, (*trail, node))
        visiting.remove(node)
        visited.add(node)

    for capability_id in sorted(graph):
        visit(capability_id, ())
    return errors


def validate_inventory_document(document: dict[str, Any]) -> list[str]:
    """Validate schema, real paths, routing uniqueness and truth boundaries."""

    errors: list[str] = []
    schema = _load_json(SCHEMA_PATH)
    validator = Draft202012Validator(schema)
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.absolute_path)):
        pointer = "/" + "/".join(str(part) for part in error.absolute_path)
        errors.append(f"capability-package/manifest.json{pointer}: {error.message}")
    inventory = document.get("canonical_inventory")
    if not isinstance(inventory, dict):
        return errors or ["capability-package/manifest.json: canonical_inventory missing"]

    capabilities = inventory.get("capabilities", [])
    capability_ids = [item.get("capability_id") for item in capabilities if isinstance(item, dict)]
    duplicates = sorted({item for item in capability_ids if capability_ids.count(item) > 1})
    for capability_id in duplicates:
        errors.append(f"{capability_id}.capability_id: duplicate capability_id")

    aliases: dict[str, str] = {}
    id_set = set(capability_ids)
    for capability in capabilities:
        if not isinstance(capability, dict):
            continue
        capability_id = str(capability.get("capability_id", "UNKNOWN"))
        for alias in capability.get("aliases", []):
            if alias in id_set and alias != capability_id:
                errors.append(f"{capability_id}.aliases: alias conflicts with capability_id {alias}")
            previous = aliases.get(alias)
            if previous and previous != capability_id:
                errors.append(f"{capability_id}.aliases: alias {alias} already belongs to {previous}")
            aliases[alias] = capability_id

        status = capability.get("implementation_status")
        implementation = capability.get("canonical_implementation")
        entrypoint = capability.get("canonical_entrypoint")
        if status in {"implemented", "partial"}:
            if not isinstance(implementation, str):
                errors.append(f"{capability_id}.canonical_implementation: required for {status}")
            else:
                _append_path_errors(errors, capability_id, "canonical_implementation", [implementation])
            if not isinstance(entrypoint, str) or not entrypoint:
                errors.append(f"{capability_id}.canonical_entrypoint: required for {status}")
            if not capability.get("test_evidence"):
                errors.append(f"{capability_id}.test_evidence: required for {status}")
        if status == "partial" and not isinstance(capability.get("partial_scope"), dict):
            errors.append(f"{capability_id}.partial_scope: implemented and missing scope required")
        if status == "missing" and (implementation is not None or entrypoint is not None):
            errors.append(f"{capability_id}: missing capability cannot have implementation or entrypoint")

        for field in ("implementation_evidence", "test_evidence", "documentation"):
            _append_path_errors(errors, capability_id, field, capability.get(field, []))

        canonical_by_type: dict[str, list[dict[str, Any]]] = {}
        for interface in capability.get("interfaces", []):
            path = interface.get("path")
            _append_path_errors(errors, capability_id, "interfaces.path", [path])
            if interface.get("role") == "canonical":
                canonical_by_type.setdefault(str(interface.get("interface_type")), []).append(interface)
            if interface.get("role") == "deprecated" and not interface.get("replacement"):
                errors.append(f"{capability_id}.interfaces: deprecated entry missing replacement")
        for interface_type, matches in canonical_by_type.items():
            if len(matches) > 1:
                errors.append(f"{capability_id}.interfaces.{interface_type}: multiple canonical entries")

        deprecation = capability.get("deprecation", {})
        if capability.get("lifecycle_status") == "deprecated":
            for field in ("reason", "replacement", "migration_guidance", "removal_criteria"):
                if not deprecation.get(field):
                    errors.append(f"{capability_id}.deprecation.{field}: required")

    errors.extend(_cycle_errors(capabilities))

    surfaces = inventory.get("mcp_surfaces", [])
    surface_ids = [item.get("surface_id") for item in surfaces if isinstance(item, dict)]
    for surface_id in sorted({item for item in surface_ids if surface_ids.count(item) > 1}):
        errors.append(f"{surface_id}.surface_id: duplicate MCP surface")
    canonical_public = [item for item in surfaces if item.get("classification") == "canonical_public"]
    if len(canonical_public) != 1:
        errors.append(f"mcp_surfaces: expected exactly one canonical_public surface, got {len(canonical_public)}")
    elif canonical_public[0].get("public_contract") is not True:
        errors.append(f"{canonical_public[0].get('surface_id')}.public_contract: must be true")

    inventoried_scripts: set[str] = set()
    for surface in surfaces:
        surface_id = str(surface.get("surface_id", "UNKNOWN"))
        implementation_path = surface.get("implementation_path")
        if isinstance(implementation_path, str):
            inventoried_scripts.add(implementation_path)
        _append_path_errors(errors, surface_id, "implementation_path", [implementation_path])
        _append_path_errors(errors, surface_id, "test_evidence", surface.get("test_evidence", []))
        if surface.get("classification") in {"compatibility", "deprecated"} and not surface.get("replacement"):
            errors.append(f"{surface_id}.replacement: required for {surface.get('classification')}")
        if surface.get("classification") != "canonical_public" and surface.get("public_contract") is True:
            errors.append(f"{surface_id}.public_contract: only canonical_public may be public")
        if implementation_path and implementation_path not in str(surface.get("start_command", "")):
            errors.append(f"{surface_id}.start_command: does not route to {implementation_path}")

    executable_mcp_scripts = {
        str(path.relative_to(ROOT))
        for path in (ROOT / "scripts").glob("*mcp*stdio*.py")
        if "smoke" not in path.name
    }
    for missing in sorted(executable_mcp_scripts - inventoried_scripts):
        errors.append(f"mcp_surfaces: unclassified executable surface {missing}")
    for extra in sorted(inventoried_scripts - executable_mcp_scripts):
        errors.append(f"mcp_surfaces: inventoried path is not an executable stdio surface {extra}")

    otel = next(
        (item for item in capabilities if item.get("capability_id") == "saee.otel_style_candidate_mapping"),
        None,
    )
    if not otel:
        errors.append("saee.otel_style_candidate_mapping: capability missing")
    else:
        non_claims = " ".join(otel.get("non_claims", [])).lower()
        for phrase in ("not otlp ingestion", "not opentelemetry collector", "does not verify telemetry authenticity"):
            if phrase not in non_claims:
                errors.append(f"saee.otel_style_candidate_mapping.non_claims: missing boundary {phrase!r}")

    return list(dict.fromkeys(errors))


def _capability_maps(inventory: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    by_id = {item["capability_id"]: item for item in inventory.get("capabilities", [])}
    aliases = {
        alias: capability_id
        for capability_id, item in by_id.items()
        for alias in item.get("aliases", [])
    }
    return by_id, aliases


def get_capability(reference: str, inventory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve an exact capability id or exact alias; never fuzzy-match."""

    source = inventory or load_canonical_inventory()
    by_id, aliases = _capability_maps(source)
    capability_id = reference if reference in by_id else aliases.get(reference)
    if capability_id is None:
        raise CanonicalCapabilityInventoryError("CAPABILITY_UNKNOWN", reference)
    return copy.deepcopy(by_id[capability_id])


def resolve_interface(
    reference: str,
    interface_type: str,
    inventory: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Resolve the unique canonical interface for a capability and type."""

    capability = get_capability(reference, inventory)
    matches = [
        item
        for item in capability.get("interfaces", [])
        if item.get("interface_type") == interface_type and item.get("role") == "canonical"
    ]
    if not matches:
        raise CanonicalCapabilityInventoryError(
            "CANONICAL_INTERFACE_NOT_FOUND",
            f"{capability['capability_id']}:{interface_type}",
        )
    if len(matches) > 1:
        raise CanonicalCapabilityInventoryError(
            "CANONICAL_INTERFACE_CONFLICT",
            f"{capability['capability_id']}:{interface_type}",
        )
    interface = copy.deepcopy(matches[0])
    return {
        "capability_id": capability["capability_id"],
        "implementation_status": capability["implementation_status"],
        "lifecycle_status": capability["lifecycle_status"],
        "interface": interface,
        "replacement": interface.get("replacement"),
        "canonical_source": CANONICAL_SOURCE,
    }


def resolve_mcp_surface(reference: str, inventory: dict[str, Any] | None = None) -> dict[str, Any]:
    """Resolve an MCP surface by exact id or implementation path."""

    source = inventory or load_canonical_inventory()
    matches = [
        item
        for item in source.get("mcp_surfaces", [])
        if reference in {item.get("surface_id"), item.get("implementation_path")}
    ]
    if not matches:
        raise CanonicalCapabilityInventoryError("MCP_SURFACE_UNKNOWN", reference)
    if len(matches) > 1:
        raise CanonicalCapabilityInventoryError("MCP_SURFACE_CONFLICT", reference)
    surface = copy.deepcopy(matches[0])
    return {
        "surface": surface,
        "replacement": surface.get("replacement"),
        "canonical_source": CANONICAL_SOURCE,
    }


def validate_repository_inventory(
    *,
    document: dict[str, Any] | None = None,
    agent_index: dict[str, Any] | None = None,
    public: dict[str, Any] | None = None,
    well_known: dict[str, Any] | None = None,
    documents: dict[str, str] | None = None,
) -> list[str]:
    """Validate the authority and the bounded repository projections."""

    source_document = document if document is not None else _load_json(MANIFEST_PATH)
    errors = validate_inventory_document(source_document)
    inventory = source_document.get("canonical_inventory", {})
    capabilities = inventory.get("capabilities", [])
    status_projection = {
        item["capability_id"]: {
            "implementation_status": item["implementation_status"],
            "lifecycle_status": item["lifecycle_status"],
        }
        for item in capabilities
    }
    public_operations = sorted(
        item["capability_id"]
        for item in capabilities
        if any(
            interface.get("interface_type") == "mcp"
            and interface.get("audience") == "public"
            and interface.get("role") == "canonical"
            for interface in item.get("interfaces", [])
        )
    )

    index_projection = agent_index if agent_index is not None else _load_json(ROOT / "agent-index.json")
    ledger = index_projection.get("capability_progress_ledger_v1", {})
    if ledger.get("canonical_source") != CANONICAL_SOURCE:
        errors.append("agent-index.json.capability_progress_ledger_v1.canonical_source: projection drift")
    if ledger.get("capability_status_projection") != status_projection:
        errors.append("agent-index.json.capability_progress_ledger_v1.capability_status_projection: projection drift")
    roadmap_policy = ledger.get("roadmap_policy", {})
    if roadmap_policy.get("roadmap_authority") is not False:
        errors.append("agent-index.json.capability_progress_ledger_v1.roadmap_policy: roadmap authority must be false")

    public_projection = public if public is not None else _load_json(ROOT / "agent-interface/public/saee-public-capability-surface.v0.1.json")
    projected_public = sorted(item.get("operation_id") for item in public_projection.get("available_operations", []))
    if projected_public != public_operations:
        errors.append("agent-interface/public/saee-public-capability-surface.v0.1.json.available_operations: projection drift")
    well_known_projection = well_known if well_known is not None else _load_json(ROOT / ".well-known/saee-capability-index.json")
    if sorted(well_known_projection.get("public_operations", [])) != public_operations:
        errors.append(".well-known/saee-capability-index.json.public_operations: projection drift")

    expected_doc_tokens = {
        "AGENTS.md": [
            f"canonical_capability_source={CANONICAL_SOURCE}",
            "do_not_rebuild=synthetic OpenTelemetry-style candidate evidence mapping",
        ],
        "llms.txt": [
            f"Canonical capability source: {CANONICAL_SOURCE}",
            "agent-index.json recommended_next_pr fields are deprecated compatibility metadata",
        ],
        "README.md": [
            "python3 scripts/saee_agent_readiness_mcp_stdio.py",
            CANONICAL_SOURCE,
        ],
        "docs/CAPABILITY_INVENTORY.md": [
            CANONICAL_SOURCE,
            "synthetic_opentelemetry_style",
            "scripts/saee_agent_readiness_mcp_stdio.py",
        ],
    }
    for relative_path, tokens in expected_doc_tokens.items():
        if documents is not None and relative_path in documents:
            text = documents[relative_path]
        else:
            path = ROOT / relative_path
            if not path.is_file():
                errors.append(f"{relative_path}: required projection missing")
                continue
            text = path.read_text(encoding="utf-8")
        for token in tokens:
            if token not in text:
                errors.append(f"{relative_path}: missing canonical projection token {token!r}")

    forbidden_active_recommendations = {
        "Add OpenTelemetry-to-SAEE Evidence Adequacy Mapping",
        "Add OpenTelemetry-to-SAEE resource event mapping",
        "Canonical Capability Inventory, Routing and Deprecation Map v1",
    }

    def walk(value: Any, path: str = "agent-index.json") -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                child_path = f"{path}.{key}"
                if key == "recommended_next_pr" and child in forbidden_active_recommendations:
                    errors.append(f"{child_path}: completed work remains an active recommendation")
                walk(child, child_path)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, f"{path}[{index}]")

    walk(index_projection)
    return list(dict.fromkeys(errors))
