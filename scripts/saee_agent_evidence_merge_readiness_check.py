#!/usr/bin/env python3
"""Validate the read-only Agent Evidence source freeze and migration crosswalk."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FREEZE_PATH = ROOT / "governance/migration/agent-evidence-source-provenance.v1.json"
CROSSWALK_PATH = ROOT / "governance/migration/agent-evidence-migration-crosswalk.v1.json"
COMPATIBILITY_PATH = ROOT / "governance/migration/agent-evidence-schema-compatibility.v1.json"
INTEGRATION_PLAN_PATH = ROOT / "governance/migration/saee-three-version-integration-plan.v1.json"
OWNER_DECISION_PATH = ROOT / "governance/migration/agent-evidence-m03-owner-decision.v1.json"
EXPECTED_VERSIONS = ["SAEE Evidence", "SAEE Evaluation", "SAEE Governance"]
ALLOWED_DISPOSITIONS = {
    "REUSE_SAEE",
    "ADAPT_CONTRACT_AFTER_LICENSE_GATE",
    "ADAPT_SPEC_NOT_CODE",
    "MIGRATE_AFTER_LICENSE_AND_TRUST_GATE",
    "ADAPT_AFTER_COMPATIBILITY_GATE",
    "KEEP_EXTERNAL_UNTIL_RUNTIME_DECISION",
    "KEEP_EXTERNAL",
    "REVIEW_AND_ADAPT_AFTER_LICENSE_GATE",
}


def load_documents(
    root: Path = ROOT,
) -> tuple[
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
    dict[str, Any],
]:
    migration = root / "governance" / "migration"
    freeze = json.loads(
        (migration / "agent-evidence-source-provenance.v1.json").read_text(encoding="utf-8")
    )
    crosswalk = json.loads(
        (migration / "agent-evidence-migration-crosswalk.v1.json").read_text(encoding="utf-8")
    )
    compatibility = json.loads(
        (migration / "agent-evidence-schema-compatibility.v1.json").read_text(encoding="utf-8")
    )
    integration_plan = json.loads(
        (migration / "saee-three-version-integration-plan.v1.json").read_text(encoding="utf-8")
    )
    owner_decision = json.loads(
        (migration / "agent-evidence-m03-owner-decision.v1.json").read_text(encoding="utf-8")
    )
    return freeze, crosswalk, compatibility, integration_plan, owner_decision


def validate_documents(
    freeze: dict[str, Any],
    crosswalk: dict[str, Any],
    compatibility: dict[str, Any],
    integration_plan: dict[str, Any],
    owner_decision: dict[str, Any],
) -> list[str]:
    errors: list[str] = []
    source = freeze.get("source_repository", {})
    license_record = freeze.get("license", {})

    if freeze.get("freeze_scope") != "TRACKED_HEAD_ONLY":
        errors.append("freeze_scope must be TRACKED_HEAD_ONLY")
    for field in ("commit_oid", "tree_oid", "git_ls_tree_sha256", "tracked_file_count"):
        if not source.get(field):
            errors.append(f"source_repository.{field} is required")
    if license_record.get("classification") != "ALL_RIGHTS_RESERVED":
        errors.append("license classification must preserve ALL_RIGHTS_RESERVED")
    if license_record.get("open_source") is not False:
        errors.append("license.open_source must remain false")
    if license_record.get("migration_grant_recorded") is not True:
        errors.append("bounded clean-room migration grant must be recorded")
    for field in (
        "source_copy_performed",
        "runtime_integration_performed",
        "mcp_change_performed",
        "marketplace_transfer_performed",
    ):
        if freeze.get(field) is not False:
            errors.append(f"{field} must remain false at the provenance-freeze gate")
    if freeze.get("migration_execution_authorized") is not True:
        errors.append("bounded clean-room migration execution must be authorized")

    if crosswalk.get("canonical_capability_source") != "capability-package/manifest.json#canonical_inventory":
        errors.append("crosswalk must route capability facts to the canonical inventory")
    if crosswalk.get("crosswalk_is_capability_source") is not False:
        errors.append("crosswalk must not become a capability fact source")
    if crosswalk.get("target_customer_versions") != EXPECTED_VERSIONS:
        errors.append("target customer versions must be the constitutional three-version set")

    mappings = crosswalk.get("mappings")
    if not isinstance(mappings, list) or not mappings:
        errors.append("crosswalk mappings must be a non-empty list")
        mappings = []
    mapping_ids: set[str] = set()
    for index, mapping in enumerate(mappings):
        if not isinstance(mapping, dict):
            errors.append(f"mappings[{index}] must be an object")
            continue
        mapping_id = mapping.get("mapping_id")
        if not isinstance(mapping_id, str) or not mapping_id:
            errors.append(f"mappings[{index}].mapping_id is required")
        elif mapping_id in mapping_ids:
            errors.append(f"duplicate mapping_id: {mapping_id}")
        else:
            mapping_ids.add(mapping_id)
        if mapping.get("disposition") not in ALLOWED_DISPOSITIONS:
            errors.append(f"{mapping_id or index} has invalid disposition")
        if mapping.get("target_version") not in EXPECTED_VERSIONS:
            errors.append(f"{mapping_id or index} has invalid target_version")
        if not mapping.get("source_assets") or not mapping.get("saee_existing"):
            errors.append(f"{mapping_id or index} must record source_assets and saee_existing")
        if not mapping.get("non_claim"):
            errors.append(f"{mapping_id or index} must record a non_claim")

    gate = crosswalk.get("gate", {})
    expected_gate = {
        "source_provenance_freeze": "PASS_TRACKED_HEAD_ONLY",
        "duplicate_build_prevention": "PASS_PLAN_USES_REUSE_FIRST",
        "license_gate": "PASS_BOUNDED_CLEAN_ROOM_SCOPE",
        "source_migration": "AUTHORIZED_CLEAN_ROOM_TRAITS_ONLY",
        "runtime_integration": "NOT_AUTHORIZED",
        "marketplace_transfer": "NOT_AUTHORIZED",
    }
    for key, expected in expected_gate.items():
        if gate.get(key) != expected:
            errors.append(f"gate.{key} must be {expected}")

    if gate.get("schema_compatibility_gate") != "PASS_BOUNDED_ADAPTER_AND_EVALUATION_BRIDGE_LOCAL":
        errors.append(
            "schema compatibility gate must record the bounded local adapter and evaluation bridge"
        )
    if compatibility.get("analysis_mode") != "READ_ONLY_TRAIT_AND_FIELD_MAPPING":
        errors.append("schema compatibility analysis must remain read-only")
    if compatibility.get("source_code_copied") is not False:
        errors.append("schema compatibility analysis must not claim source code copied")
    comparisons = compatibility.get("comparisons")
    if not isinstance(comparisons, list) or len(comparisons) != 3:
        errors.append("schema compatibility must contain exactly three contract comparisons")
        comparisons = []
    comparison_ids: set[str] = set()
    for index, comparison in enumerate(comparisons):
        comparison_id = comparison.get("comparison_id") if isinstance(comparison, dict) else None
        if not isinstance(comparison_id, str) or comparison_id in comparison_ids:
            errors.append(f"comparisons[{index}] has missing or duplicate comparison_id")
            continue
        comparison_ids.add(comparison_id)
        if not comparison.get("field_map") or not comparison.get("required_adapter_guards"):
            errors.append(f"{comparison_id} must record field_map and required_adapter_guards")
        if comparison.get("compatibility") not in {
            "ADAPTER_REQUIRED_LOSSY",
            "CONTRACT_ADAPTATION_REQUIRED",
            "RESULT_ENVELOPE_ADAPTER_REQUIRED",
        }:
            errors.append(f"{comparison_id} has invalid compatibility classification")
    compatibility_gate = compatibility.get("gate", {})
    for key, expected in {
        "direct_schema_compatibility": False,
        "adapter_required": True,
        "adapter_implemented": True,
        "license_gate": "PASS_BOUNDED_CLEAN_ROOM_SCOPE",
        "migration_execution": "AUTHORIZED_FIXTURES_AND_ADAPTERS_ONLY",
    }.items():
        if compatibility_gate.get(key) != expected:
            errors.append(f"compatibility gate.{key} must be {expected}")

    if integration_plan.get("canonical_capability_source") != "capability-package/manifest.json#canonical_inventory":
        errors.append("integration plan must route capability facts to the canonical inventory")
    if integration_plan.get("plan_is_capability_source") is not False:
        errors.append("integration plan must not become a capability fact source")
    if integration_plan.get("target_customer_versions") != EXPECTED_VERSIONS:
        errors.append("integration plan must preserve the exact three-version target")
    truth = integration_plan.get("current_truth", {})
    required_false_truth = {
        "legacy_runtime_integrated",
        "legacy_mcp_transferred",
        "marketplace_transferred",
        "merge_completed",
        "three_versions_implemented",
        "three_versions_customer_validated",
        "three_versions_launched",
        "production_ready",
    }
    for field in required_false_truth:
        if truth.get(field) is not False:
            errors.append(f"integration current_truth.{field} must remain false")
    if truth.get("selected_source_traits_integrated") is not True:
        errors.append(
            "integration current_truth.selected_source_traits_integrated must record the bounded local subset"
        )
    if truth.get("license_scope_approved") is not True:
        errors.append("integration current_truth.license_scope_approved must be true")
    for field in ("compatibility_fixtures_implemented", "adapter_contracts_implemented"):
        if truth.get(field) is not True:
            errors.append(f"integration current_truth.{field} must be true")
    slices = integration_plan.get("migration_slices")
    expected_slice_ids = {f"M-{number:02d}" for number in range(11)}
    actual_slice_ids = {
        item.get("slice_id") for item in slices if isinstance(item, dict)
    } if isinstance(slices, list) else set()
    if actual_slice_ids != expected_slice_ids:
        errors.append("integration plan must contain migration slices M-00 through M-10")
    if isinstance(slices, list):
        license_slice = next((item for item in slices if item.get("slice_id") == "M-03"), {})
        if license_slice.get("status") != "completed_owner_approved_bounded_clean_room":
            errors.append("M-03 must record completed bounded clean-room owner approval")
        governance_slice = next((item for item in slices if item.get("slice_id") == "M-07"), {})
        if governance_slice.get("status") != "target_not_implemented":
            errors.append("M-07 must preserve SAEE Governance target_not_implemented")
        fixture_slice = next((item for item in slices if item.get("slice_id") == "M-04"), {})
        if fixture_slice.get("status") != "completed_local_synthetic":
            errors.append("M-04 must record completed_local_synthetic")
        adapter_slice = next((item for item in slices if item.get("slice_id") == "M-05"), {})
        if adapter_slice.get("status") != "completed_local_bounded_integrity_adapter":
            errors.append("M-05 must record the bounded local integrity adapter")
        bridge_slice = next((item for item in slices if item.get("slice_id") == "M-06"), {})
        if bridge_slice.get("status") != "completed_local_evaluation_bridge":
            errors.append("M-06 must record the bounded local Evaluation bridge")
    version_contracts = integration_plan.get("version_completion_contracts", [])
    if {item.get("version") for item in version_contracts} != set(EXPECTED_VERSIONS):
        errors.append("integration plan must contain one completion contract per target version")
    for contract in version_contracts:
        if contract.get("implementation_complete") is not False:
            errors.append(f"{contract.get('version')} implementation_complete must remain false")
        if not contract.get("missing_before_implemented"):
            errors.append(f"{contract.get('version')} must record missing implementation evidence")

    if owner_decision.get("source_commit") != source.get("commit_oid"):
        errors.append("M-03 owner decision must bind the frozen source commit")
    if owner_decision.get("decision_status") != "APPROVED_BOUNDED_CLEAN_ROOM":
        errors.append("M-03 decision_status must record bounded clean-room approval")
    if owner_decision.get("selected_option") != "APPROVE_CLEAN_ROOM_TRAIT_MIGRATION":
        errors.append("M-03 selected_option must be APPROVE_CLEAN_ROOM_TRAIT_MIGRATION")
    if owner_decision.get("authorization_effective") is not True:
        errors.append("M-03 bounded authorization must be effective")
    for field in ("owner_identity", "owner_statement", "decided_at"):
        if not owner_decision.get(field):
            errors.append(f"M-03 {field} is required for effective authorization")
    if owner_decision.get("proposed_method") != "CLEAN_ROOM_TRAIT_AND_CONTRACT_REIMPLEMENTATION":
        errors.append("M-03 proposed method must remain clean-room trait reimplementation")
    required_exclusions = {
        "direct copying of source implementation text",
        "Git history merge",
        "packages/agent_evidence/api runtime migration",
        "packages/agent_evidence/mcp endpoint or namespace transfer",
        "deploy/aliyun-mcp transfer",
        "Aliyun product 68658 transfer",
    }
    if not required_exclusions.issubset(set(owner_decision.get("excluded_scope", []))):
        errors.append("M-03 owner decision is missing required excluded scope")
    return errors


def _git(source_root: Path, *args: str) -> bytes:
    result = subprocess.run(
        ["git", *args], cwd=source_root, check=False, capture_output=True
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def validate_live_source(
    freeze: dict[str, Any], compatibility: dict[str, Any], source_root: Path
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    observations: dict[str, Any] = {"source_available": source_root.is_dir()}
    if not source_root.is_dir():
        return [f"source repository is unavailable: {source_root}"], observations

    expected = freeze["source_repository"]
    try:
        head = _git(source_root, "rev-parse", "HEAD").decode().strip()
        tree = _git(source_root, "rev-parse", "HEAD^{tree}").decode().strip()
        ls_tree = _git(source_root, "ls-tree", "-r", "--full-tree", "HEAD")
        file_count = len(_git(source_root, "ls-tree", "-r", "--name-only", "HEAD").splitlines())
        license_bytes = _git(source_root, "show", "HEAD:LICENSE")
        status = _git(source_root, "status", "--porcelain=v1", "-z")
    except RuntimeError as exc:
        return [f"unable to inspect source repository: {exc}"], observations

    observations.update(
        {
            "head": head,
            "tree": tree,
            "tracked_file_count": file_count,
            "git_ls_tree_sha256": hashlib.sha256(ls_tree).hexdigest(),
            "license_sha256": hashlib.sha256(license_bytes).hexdigest(),
            "worktree_status_sha256": hashlib.sha256(status).hexdigest(),
            "worktree_snapshot_match": hashlib.sha256(status).hexdigest()
            == freeze["worktree_observation"]["status_porcelain_v1_z_sha256"],
        }
    )
    comparisons = {
        "HEAD": (head, expected["commit_oid"]),
        "tree": (tree, expected["tree_oid"]),
        "tracked file count": (file_count, expected["tracked_file_count"]),
        "ls-tree digest": (observations["git_ls_tree_sha256"], expected["git_ls_tree_sha256"]),
        "license digest": (observations["license_sha256"], freeze["license"]["sha256"]),
    }
    for label, (actual, wanted) in comparisons.items():
        if actual != wanted:
            errors.append(f"source {label} mismatch: expected {wanted}, found {actual}")
    for schema_record in compatibility["source_schemas"]:
        path = schema_record["path"]
        try:
            tree_line = _git(source_root, "ls-tree", "HEAD", "--", path).decode().strip()
        except RuntimeError as exc:
            errors.append(f"unable to inspect source schema {path}: {exc}")
            continue
        fields = tree_line.split()
        actual_blob = fields[2] if len(fields) >= 4 else None
        if actual_blob != schema_record["blob_oid"]:
            errors.append(
                f"source schema blob mismatch for {path}: expected {schema_record['blob_oid']}, found {actual_blob}"
            )
    return errors, observations


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    try:
        (
            freeze,
            crosswalk,
            compatibility,
            integration_plan,
            owner_decision,
        ) = load_documents(ROOT)
    except (OSError, json.JSONDecodeError) as exc:
        print("SAEE_AGENT_EVIDENCE_MERGE_READINESS_CHECK: FAIL")
        print(f"- unable to load migration documents: {exc}")
        return 1

    errors = validate_documents(
        freeze, crosswalk, compatibility, integration_plan, owner_decision
    )
    observations: dict[str, Any] = {"source_available": False}
    if not args.offline:
        source_root = args.source_root or Path(freeze["source_repository"]["path"])
        live_errors, observations = validate_live_source(freeze, compatibility, source_root)
        errors.extend(live_errors)

    if errors:
        print("SAEE_AGENT_EVIDENCE_MERGE_READINESS_CHECK: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("SAEE_AGENT_EVIDENCE_MERGE_READINESS_CHECK: PASS")
    print("SOURCE_PROVENANCE_FREEZE=PASS_TRACKED_HEAD_ONLY")
    print("LICENSE_GATE=PASS_BOUNDED_CLEAN_ROOM_SCOPE")
    print("SOURCE_MIGRATION=AUTHORIZED_CLEAN_ROOM_TRAITS_ONLY")
    print("RUNTIME_INTEGRATION=NOT_AUTHORIZED")
    print(f"MAPPINGS={len(crosswalk['mappings'])}")
    print(f"SCHEMA_COMPARISONS={len(compatibility['comparisons'])}")
    print("SCHEMA_COMPATIBILITY=ADAPTER_REQUIRED")
    print("M04_COMPATIBILITY_FIXTURES=COMPLETED_LOCAL_SYNTHETIC")
    print("M05_INTEGRITY_ADAPTER=COMPLETED_LOCAL_BOUNDED")
    print("M06_EVALUATION_BRIDGE=COMPLETED_LOCAL_BOUNDED")
    print(f"MIGRATION_SLICES={len(integration_plan['migration_slices'])}")
    print("MERGE_COMPLETED=false")
    print("M03_OWNER_DECISION=APPROVED_BOUNDED_CLEAN_ROOM")
    if not args.offline:
        print(f"SOURCE_HEAD={observations['head']}")
        print(f"SOURCE_TREE={observations['tree']}")
        print(
            "WORKTREE_OBSERVATION_MATCH="
            + ("YES" if observations["worktree_snapshot_match"] else "NO_INFORMATIONAL_ONLY")
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
