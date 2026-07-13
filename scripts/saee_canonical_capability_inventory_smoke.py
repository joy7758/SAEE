#!/usr/bin/env python3
"""Adversarial smoke for canonical SAEE capability facts and routing."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.capability_runtime.canonical_capability_inventory import (  # noqa: E402
    CANONICAL_SOURCE,
    CanonicalCapabilityInventoryError,
    canonical_inventory_json,
    get_capability,
    load_canonical_inventory,
    normalize_inventory,
    resolve_interface,
    resolve_mcp_surface,
    validate_inventory_document,
    validate_repository_inventory,
)


MANIFEST = ROOT / "capability-package/manifest.json"
INDEX = ROOT / "agent-index.json"
CLI = ROOT / "scripts/saee_agent_cli.py"


class InventorySmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise InventorySmokeError(detail)


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"JSON root must be object: {path}")
    return value


def rejected(document: dict[str, Any], marker: str) -> bool:
    return any(marker in error for error in validate_inventory_document(document))


def cli(*args: str, expected_code: int = 0) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, str(CLI), *args],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    require(completed.returncode == expected_code, f"CLI {' '.join(args)} exit={completed.returncode}: {completed.stdout} {completed.stderr}")
    require(completed.stderr == "", f"CLI {' '.join(args)} wrote stderr")
    value = json.loads(completed.stdout)
    require(isinstance(value, dict), f"CLI {' '.join(args)} output root")
    return value


def main() -> int:
    document = load(MANIFEST)
    inventory = load_canonical_inventory()
    errors = validate_repository_inventory()
    require(not errors, f"canonical repository validation failed: {errors}")

    capability_ids = [item["capability_id"] for item in inventory["capabilities"]]
    surfaces = inventory["mcp_surfaces"]
    require(len(capability_ids) == 9 and len(set(capability_ids)) == 9, "capability ids 9/9 unique")
    require(len(surfaces) == 4, "four MCP surfaces not inventoried")
    require(sum(item["classification"] == "canonical_public" for item in surfaces) == 1, "canonical public MCP uniqueness")
    require(all(item["classification"] != "UNKNOWN" for item in surfaces), "MCP surface remains UNKNOWN")
    require(all(item["usage_evidence"] == "UNKNOWN" for item in surfaces), "unsupported usage evidence claim")

    alias = get_capability("synthetic_opentelemetry_style")
    require(alias["capability_id"] == "saee.otel_style_candidate_mapping", "exact alias resolution")
    canonical_mcp = resolve_interface("saee.evaluate_agent_run", "mcp")
    require(canonical_mcp["interface"]["path"] == "scripts/saee_agent_readiness_mcp_stdio.py", "canonical MCP route")
    qianfan = resolve_mcp_surface("scripts/saee_qianfan_readiness_mcp_stdio.py")
    require(qianfan["surface"]["classification"] == "compatibility", "Qianfan surface role")
    require(qianfan["replacement"] == "saee.agent_readiness_mcp_stdio", "Qianfan replacement")
    internal_surfaces = [item for item in surfaces if item["classification"] == "internal"]
    require(len(internal_surfaces) == 2 and all(item["public_contract"] is False for item in internal_surfaces), "internal MCP public leak")

    otel = get_capability("saee.otel_style_candidate_mapping")
    otel_non_claims = " ".join(otel["non_claims"]).lower()
    require("not otlp ingestion" in otel_non_claims, "OTLP boundary")
    require("not opentelemetry collector" in otel_non_claims, "Collector boundary")
    require(get_capability("saee.otel_sdk_or_otlp_ingestion")["implementation_status"] == "missing", "real OTLP falsely implemented")

    normalized = normalize_inventory(inventory)
    require([item["capability_id"] for item in normalized["capabilities"]] == sorted(capability_ids), "normalized capability order")
    baseline = canonical_inventory_json(inventory)
    for _ in range(5):
        require(canonical_inventory_json(copy.deepcopy(inventory)) == baseline, "inventory normalization not deterministic")

    negative_results: list[tuple[str, bool]] = []

    mutation = copy.deepcopy(document)
    mutation["canonical_inventory"]["capabilities"].append(copy.deepcopy(mutation["canonical_inventory"]["capabilities"][0]))
    negative_results.append(("duplicate capability_id", rejected(mutation, "duplicate capability_id")))

    mutation = copy.deepcopy(document)
    mutation["canonical_inventory"]["capabilities"][1]["aliases"].append("evaluate_agent_run")
    negative_results.append(("alias conflict", rejected(mutation, "already belongs")))

    mutation = copy.deepcopy(document)
    run = next(item for item in mutation["canonical_inventory"]["capabilities"] if item["capability_id"] == "saee.evaluate_agent_run")
    run["interfaces"].append(copy.deepcopy(run["interfaces"][0]))
    run["interfaces"][-1]["path"] = "scripts/saee_qianfan_readiness_mcp_stdio.py"
    negative_results.append(("multiple canonical interfaces", rejected(mutation, "multiple canonical entries")))

    mutation = copy.deepcopy(document)
    run = next(item for item in mutation["canonical_inventory"]["capabilities"] if item["capability_id"] == "saee.evaluate_agent_run")
    run["canonical_implementation"] = "/tmp/private.py"
    negative_results.append(("absolute implementation path", rejected(mutation, "must not be absolute")))

    mutation = copy.deepcopy(document)
    run = next(item for item in mutation["canonical_inventory"]["capabilities"] if item["capability_id"] == "saee.evaluate_agent_run")
    run["canonical_implementation"] = "saee_backend/services/missing.py"
    negative_results.append(("missing implementation path", rejected(mutation, "missing path")))

    mutation = copy.deepcopy(document)
    run = next(item for item in mutation["canonical_inventory"]["capabilities"] if item["capability_id"] == "saee.evaluate_agent_run")
    run["test_evidence"] = []
    negative_results.append(("implemented without test", rejected(mutation, "test_evidence")))

    mutation = copy.deepcopy(document)
    run = next(item for item in mutation["canonical_inventory"]["capabilities"] if item["capability_id"] == "saee.evaluate_agent_run")
    run["lifecycle_status"] = "deprecated"
    negative_results.append(("deprecated without migration", rejected(mutation, "deprecation.reason")))

    mutation = copy.deepcopy(document)
    first, second = mutation["canonical_inventory"]["capabilities"][:2]
    first["superseded_by"] = [second["capability_id"]]
    second["superseded_by"] = [first["capability_id"]]
    negative_results.append(("deprecation cycle", rejected(mutation, "deprecation cycle")))

    mutation = copy.deepcopy(document)
    mutation["canonical_inventory"]["mcp_surfaces"].pop()
    negative_results.append(("unclassified MCP surface", rejected(mutation, "unclassified executable surface")))

    mutation = copy.deepcopy(document)
    canonical = next(item for item in mutation["canonical_inventory"]["mcp_surfaces"] if item["classification"] == "canonical_public")
    canonical["classification"] = "test_only"
    negative_results.append(("test-only surface recommended", rejected(mutation, "exactly one canonical_public")))

    mutation = copy.deepcopy(document)
    mutation["canonical_inventory"]["recommended_next_pr"] = "Build OTLP"
    negative_results.append(("roadmap field mixed into facts", rejected(mutation, "Additional properties")))

    mutated_index = load(INDEX)
    mutated_index["capability_progress_ledger_v1"]["capability_status_projection"]["saee.otel_sdk_or_otlp_ingestion"]["implementation_status"] = "implemented"
    negative_results.append(("agent-index projection drift", any("capability_status_projection" in item for item in validate_repository_inventory(agent_index=mutated_index))))

    mutated_index = load(INDEX)
    mutated_index["otel_candidate_evidence_mapping_v0_1"]["recommended_next_pr"] = "Add OpenTelemetry-to-SAEE Evidence Adequacy Mapping"
    negative_results.append(("completed OTEL work recommended", any("completed work remains" in item for item in validate_repository_inventory(agent_index=mutated_index))))

    duplicate_interface_inventory = copy.deepcopy(inventory)
    run = get_capability("saee.evaluate_agent_run", duplicate_interface_inventory)
    run["interfaces"].append(copy.deepcopy(run["interfaces"][0]))
    for index, item in enumerate(duplicate_interface_inventory["capabilities"]):
        if item["capability_id"] == run["capability_id"]:
            duplicate_interface_inventory["capabilities"][index] = run
    try:
        resolve_interface("saee.evaluate_agent_run", "mcp", duplicate_interface_inventory)
    except CanonicalCapabilityInventoryError as exc:
        negative_results.append(("resolver canonical conflict", exc.code == "CANONICAL_INTERFACE_CONFLICT"))
    else:
        negative_results.append(("resolver canonical conflict", False))

    try:
        get_capability("saee.unknown")
    except CanonicalCapabilityInventoryError as exc:
        negative_results.append(("unknown capability", exc.code == "CAPABILITY_UNKNOWN"))
    else:
        negative_results.append(("unknown capability", False))

    deprecated_inventory = copy.deepcopy(inventory)
    deprecated_surface = next(item for item in deprecated_inventory["mcp_surfaces"] if item["surface_id"] == "saee.qianfan_readiness_mcp_stdio")
    deprecated_surface["classification"] = "deprecated"
    resolved_deprecated = resolve_mcp_surface("saee.qianfan_readiness_mcp_stdio", deprecated_inventory)
    negative_results.append(("deprecated surface replacement", resolved_deprecated["replacement"] == "saee.agent_readiness_mcp_stdio"))

    require(all(result for _, result in negative_results), f"negative coverage failed: {[name for name, result in negative_results if not result]}")
    negative = dict(negative_results)
    required_coverage = {
        "01_capability_id_unique": len(capability_ids) == len(set(capability_ids)),
        "02_alias_unique": negative["alias conflict"],
        "03_canonical_entry_unique": negative["multiple canonical interfaces"],
        "04_paths_repository_relative": negative["absolute implementation path"],
        "05_implemented_path_exists": negative["missing implementation path"],
        "06_implemented_test_exists": negative["implemented without test"],
        "07_deprecated_migration_required": negative["deprecated without migration"],
        "08_deprecation_cycle_rejected": negative["deprecation cycle"],
        "09_four_mcp_surfaces_classified": len(surfaces) == 4,
        "10_no_unclassified_public_mcp": negative["unclassified MCP surface"],
        "11_completed_otel_not_recommended": negative["completed OTEL work recommended"],
        "12_facts_roadmap_separated": negative["roadmap field mixed into facts"],
        "13_repeated_generation_equal": canonical_inventory_json(copy.deepcopy(inventory)) == baseline,
        "14_normalized_sort_stable": [item["capability_id"] for item in normalized["capabilities"]] == sorted(capability_ids),
        "15_unknown_capability_fails": negative["unknown capability"],
        "16_multiple_canonical_resolver_fails": negative["resolver canonical conflict"],
        "17_deprecated_entry_returns_replacement": negative["deprecated surface replacement"],
        "18_test_only_not_recommended": negative["test-only surface recommended"],
        "19_internal_not_public": len(internal_surfaces) == 2 and all(item["public_contract"] is False for item in internal_surfaces),
        "20_synthetic_otel_not_real_otlp": "not otlp ingestion" in otel_non_claims,
        "21_agent_index_mutation_fails": negative["agent-index projection drift"],
        "22_duplicate_capability_id_fails": negative["duplicate capability_id"],
        "23_deprecation_cycle_mutation_fails": negative["deprecation cycle"],
        "24_deleted_implementation_fails": negative["missing implementation path"],
    }
    require(len(required_coverage) == 24 and all(required_coverage.values()), f"required coverage failed: {[key for key, value in required_coverage.items() if not value]}")

    listed = cli("capability-list")
    require(len(listed["capabilities"]) == 9 and listed["canonical_source"] == CANONICAL_SOURCE, "CLI list")
    shown = cli("capability-show", "synthetic_opentelemetry_style")
    require(shown["capability"]["capability_id"] == "saee.otel_style_candidate_mapping", "CLI alias show")
    resolved = cli("capability-resolve", "saee.evaluate_agent_run", "--interface", "mcp")
    require(resolved["interface"]["role"] == "canonical", "CLI resolve")
    validated = cli("capability-validate")
    require(validated["valid"] is True and validated["errors"] == [], "CLI validate")
    unknown = cli("capability-show", "saee.unknown", expected_code=2)
    require(unknown["error_type"] == "evaluation_error" and "CAPABILITY_UNKNOWN" in unknown["message"], "CLI unknown failure")

    print("SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: PASS")
    print("canonical_source=capability-package/manifest.json#canonical_inventory")
    print("capabilities=9/9")
    print("mcp_surfaces=4/4")
    print("canonical_public_mcp_surfaces=1/1")
    print("aliases_unique=true")
    print("active_completed_otel_recommendations=0")
    print(f"negative_cases={len(negative_results)}/{len(negative_results)}")
    print(f"required_coverage={len(required_coverage)}/{len(required_coverage)}")
    print("deterministic_runs=5/5")
    print("public_mcp_endpoint_available=false")
    print("external_mcp_interoperability_validated=false")
    print("customer_validated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (InventorySmokeError, OSError, json.JSONDecodeError) as exc:
        print(f"SAEE_CANONICAL_CAPABILITY_INVENTORY_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
