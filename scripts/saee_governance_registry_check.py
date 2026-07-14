#!/usr/bin/env python3
"""Validate the SAEE Phase 0 governance registries without changing state."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_DIR = ROOT / "governance" / "registry"
SCHEMA_DIR = ROOT / "governance" / "schemas"

REGISTRY_FILES = {
    "assets": "asset-registry.json",
    "repositories": "repository-registry.json",
    "capabilities": "capability-crosswalk.json",
    "mcp": "mcp-registry.json",
    "products": "product-registry.json",
    "external_systems": "external-system-registry.json",
}

SCHEMA_FILES = {
    "assets": "asset-registry.schema.json",
    "capabilities": "capability.schema.json",
    "mcp": "mcp-entry.schema.json",
    "products": "product.schema.json",
}

REQUIRED_ASSET_IDS = {
    "saee",
    "agent-evidence-layer",
    "agent-evidence",
    "agent-receipt-validator",
    "pop",
    "aop",
    "aro-audit",
    "digital-biosphere",
    "saee-website",
    "aliyun-product-68657",
    "aliyun-product-68658",
    "redcrag-cn",
}

REQUIRED_CAPABILITIES = {
    "saee.evaluate_agent_run",
    "saee.evaluate_evidence",
    "evidence.receipt",
    "evidence.validation",
    "capability.registry",
    "mcp.discovery",
    "saee.otel_sdk_or_otlp_ingestion",
    "saee.external_identity_binding",
    "saee.delegation_binding",
}


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_documents(root: Path = ROOT) -> tuple[dict[str, Any], dict[str, Any]]:
    registry_dir = root / "governance" / "registry"
    schema_dir = root / "governance" / "schemas"
    documents = {
        name: _read_json(registry_dir / filename)
        for name, filename in REGISTRY_FILES.items()
    }
    schemas = {
        name: _read_json(schema_dir / filename)
        for name, filename in SCHEMA_FILES.items()
    }
    return documents, schemas


def validate_schema_documents(
    documents: dict[str, Any], schemas: dict[str, Any]
) -> list[str]:
    errors: list[str] = []
    checker = FormatChecker()
    for name, schema in schemas.items():
        validator = Draft202012Validator(schema, format_checker=checker)
        for error in sorted(validator.iter_errors(documents[name]), key=str):
            location = ".".join(str(item) for item in error.absolute_path) or "root"
            errors.append(f"{name} schema error at {location}: {error.message}")
    return errors


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _true_production_paths(value: Any, path: str = "root") -> list[str]:
    results: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            if key == "production_ready" and child is True:
                results.append(child_path)
            results.extend(_true_production_paths(child, child_path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            results.extend(_true_production_paths(child, f"{path}[{index}]"))
    return results


def validate_documents(
    documents: dict[str, Any], schemas: dict[str, Any]
) -> list[str]:
    errors = validate_schema_documents(documents, schemas)

    assets = documents["assets"].get("assets", [])
    asset_ids = [item.get("id") for item in assets if isinstance(item, dict)]
    duplicate_assets = _duplicates([value for value in asset_ids if isinstance(value, str)])
    if duplicate_assets:
        errors.append(f"duplicate asset id: {sorted(duplicate_assets)}")
    missing_assets = REQUIRED_ASSET_IDS - set(asset_ids)
    if missing_assets:
        errors.append(f"missing required asset ids: {sorted(missing_assets)}")

    repositories = documents["repositories"].get("repositories", [])
    required_repository_fields = {
        "name",
        "path",
        "git_head",
        "branch",
        "remote",
        "role",
        "canonicality",
        "migration_status",
        "notes",
    }
    repository_names: list[str] = []
    for index, repository in enumerate(repositories):
        if not isinstance(repository, dict):
            errors.append(f"repositories[{index}] must be an object")
            continue
        missing = required_repository_fields - set(repository)
        if missing:
            errors.append(f"repositories[{index}] missing fields: {sorted(missing)}")
        name = repository.get("name")
        if isinstance(name, str):
            repository_names.append(name)
        if repository.get("canonicality") not in {"canonical", "reference", "external", "unknown"}:
            errors.append(f"repositories[{index}].canonicality is invalid")
        if repository.get("migration_status") not in {"KEEP", "MIGRATE", "MERGE", "DEPRECATE", "UNKNOWN"}:
            errors.append(f"repositories[{index}].migration_status is invalid")
    duplicate_repositories = _duplicates(repository_names)
    if duplicate_repositories:
        errors.append(f"duplicate repository name: {sorted(duplicate_repositories)}")

    canonical_repositories = [
        item for item in repositories if item.get("canonicality") == "canonical"
    ]
    if len(canonical_repositories) != 1:
        errors.append("exactly one canonical local repository must be recorded")
    else:
        canonical_repository = canonical_repositories[0]
        if canonical_repository.get("name") != "saee":
            errors.append("SAEE must be the canonical local repository")
        if canonical_repository.get("remote") is not None:
            errors.append("Phase 0 canonical SAEE remote must remain NOT_ESTABLISHED")
        if "Canonical local only" not in canonical_repository.get("notes", ""):
            errors.append("SAEE repository record must state Canonical local only")

    agent_evidence_repository = next(
        (item for item in repositories if item.get("name") == "agent-evidence-layer"),
        None,
    )
    if not agent_evidence_repository:
        errors.append("agent-evidence-layer repository record is missing")
    elif agent_evidence_repository.get("canonicality") != "external":
        errors.append("agent-evidence-layer must remain an external subsystem repository")
    elif "Not merged" not in agent_evidence_repository.get("notes", ""):
        errors.append("agent-evidence-layer must not be marked merged")

    capability_document = documents["capabilities"]
    if capability_document.get("canonical_capability_source") != "capability-package/manifest.json#canonical_inventory":
        errors.append("canonical capability source must remain capability-package/manifest.json#canonical_inventory")
    if capability_document.get("crosswalk_is_capability_source") is not False:
        errors.append("capability crosswalk must not become a second capability source")
    capabilities = capability_document.get("capabilities", [])
    capability_ids = [item.get("capability") for item in capabilities]
    duplicate_capabilities = _duplicates(
        [value for value in capability_ids if isinstance(value, str)]
    )
    if duplicate_capabilities:
        errors.append(f"duplicate canonical capability mapping: {sorted(duplicate_capabilities)}")
    missing_capabilities = REQUIRED_CAPABILITIES - set(capability_ids)
    if missing_capabilities:
        errors.append(f"missing required capability mappings: {sorted(missing_capabilities)}")
    capability_by_id = {
        item.get("capability"): item for item in capabilities if isinstance(item, dict)
    }
    for missing_id in (
        "saee.otel_sdk_or_otlp_ingestion",
        "saee.external_identity_binding",
        "saee.delegation_binding",
    ):
        if capability_by_id.get(missing_id, {}).get("status") != "missing":
            errors.append(f"{missing_id} must remain status=missing")

    mcp_entries = documents["mcp"].get("entries", [])
    mcp_names = [item.get("name") for item in mcp_entries]
    duplicate_mcp_names = _duplicates(
        [value for value in mcp_names if isinstance(value, str)]
    )
    if duplicate_mcp_names:
        errors.append(f"duplicate MCP entry name: {sorted(duplicate_mcp_names)}")
    canonical_by_scope: dict[tuple[str, str], list[str]] = {}
    for entry in mcp_entries:
        if entry.get("canonical") is True:
            scope = (entry.get("owner", ""), entry.get("namespace", ""))
            canonical_by_scope.setdefault(scope, []).append(entry.get("name", ""))
    for scope, names in canonical_by_scope.items():
        if len(names) > 1:
            errors.append(f"multiple canonical MCP entries for owner/namespace {scope}: {names}")
    canonical_saee = [
        entry
        for entry in mcp_entries
        if entry.get("owner") == "SAEE" and entry.get("canonical") is True
    ]
    if len(canonical_saee) != 1:
        errors.append("exactly one canonical SAEE MCP surface must exist")
    else:
        expected_tools = {"saee.evaluate_agent_run", "saee.evaluate_evidence"}
        if set(canonical_saee[0].get("tools", [])) != expected_tools:
            errors.append("canonical SAEE MCP must expose exactly the two namespaced tools")
        if canonical_saee[0].get("namespace") != "saee.*":
            errors.append("canonical SAEE MCP namespace must be saee.*")
    receipt_mcp = next(
        (entry for entry in mcp_entries if entry.get("name") == "agent-evidence-receipt-mcp"),
        None,
    )
    if not receipt_mcp:
        errors.append("Agent Evidence Receipt MCP record is missing")
    else:
        if receipt_mcp.get("type") != "external-product":
            errors.append("Agent Evidence Receipt MCP must remain external-product")
        if receipt_mcp.get("namespace") != "receipt.*":
            errors.append("Agent Evidence Receipt logical namespace must be receipt.*")
        if "never SAEE canonical" not in receipt_mcp.get("canonical_scope", ""):
            errors.append("Agent Evidence Receipt MCP must not be marked SAEE canonical")

    products = documents["products"].get("products", [])
    product_ids = [item.get("id") for item in products]
    duplicate_products = _duplicates(
        [value for value in product_ids if isinstance(value, str)]
    )
    if duplicate_products:
        errors.append(f"duplicate product id: {sorted(duplicate_products)}")
    required_product_ids = {"saee", "saee-evidence", "agent-evidence-receipt", "saee-evaluation"}
    if set(product_ids) != required_product_ids:
        errors.append("product registry must contain exactly SAEE, SAEE Evidence, Agent Evidence Receipt and SAEE Evaluation")
    forbidden_product_names = {"SAEE Governance", "SAEE Autonomous"}
    actual_product_names = {item.get("name") for item in products}
    if actual_product_names & forbidden_product_names:
        errors.append("future concepts SAEE Governance and SAEE Autonomous must not be registered as products")
    receipt_product = next(
        (item for item in products if item.get("id") == "agent-evidence-receipt"),
        None,
    )
    if not receipt_product:
        errors.append("Agent Evidence Receipt product record is missing")
    else:
        if receipt_product.get("relationship") != "saee_subproject":
            errors.append("Agent Evidence Receipt relationship must be saee_subproject")
        if receipt_product.get("runtime_owner") == "SAEE":
            errors.append("Agent Evidence Receipt must not be marked as an SAEE-owned runtime")
        if receipt_product.get("source_code_migrated") is not False:
            errors.append("Agent Evidence Receipt source_code_migrated must remain false")
        if receipt_product.get("runtime_integrated") is not False:
            errors.append("Agent Evidence Receipt runtime_integrated must remain false")

    systems = documents["external_systems"].get("systems", [])
    required_system_fields = {
        "id",
        "name",
        "type",
        "location",
        "owner",
        "relationship",
        "status",
        "private_access_performed",
        "production_ready",
    }
    system_ids: list[str] = []
    for index, system in enumerate(systems):
        if not isinstance(system, dict):
            errors.append(f"external_systems[{index}] must be an object")
            continue
        missing = required_system_fields - set(system)
        if missing:
            errors.append(f"external_systems[{index}] missing fields: {sorted(missing)}")
        system_id = system.get("id")
        if isinstance(system_id, str):
            system_ids.append(system_id)
        if system.get("private_access_performed") is not False:
            errors.append(f"external_systems[{index}] must not claim private access")
    duplicate_systems = _duplicates(system_ids)
    if duplicate_systems:
        errors.append(f"duplicate external system id: {sorted(duplicate_systems)}")

    for document_name, document in documents.items():
        for path in _true_production_paths(document, document_name):
            errors.append(f"forbidden production_ready=true at {path}")

    return errors


def main() -> int:
    try:
        documents, schemas = load_documents()
    except (OSError, json.JSONDecodeError) as exc:
        print("SAEE_GOVERNANCE_REGISTRY_CHECK: FAIL")
        print(f"- unable to load registry or schema: {exc}")
        return 1

    errors = validate_documents(documents, schemas)
    if errors:
        print("SAEE_GOVERNANCE_REGISTRY_CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SAEE_GOVERNANCE_REGISTRY_CHECK: PASS")
    print(f"registries={len(documents)}/{len(REGISTRY_FILES)}")
    print(f"schemas={len(schemas)}/{len(SCHEMA_FILES)}")
    print(f"assets={len(documents['assets']['assets'])}")
    print(f"repositories={len(documents['repositories']['repositories'])}")
    print(f"capabilities={len(documents['capabilities']['capabilities'])}")
    print(f"mcp_entries={len(documents['mcp']['entries'])}")
    print(f"products={len(documents['products']['products'])}")
    print("canonical_source=LOCAL_ONLY")
    print("canonical_git_remote=NOT_ESTABLISHED")
    print("canonical_saee_mcp=saee.agent_readiness_mcp_stdio")
    print("agent_evidence_runtime_integrated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    sys.exit(main())
