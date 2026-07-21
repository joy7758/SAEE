#!/usr/bin/env python3
"""Validate SAEE Development Constitution v1.1 and its truth boundaries."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "agent-interface/governance/saee-development-constitution.v1.1.json"
SCHEMA_PATH = ROOT / "schemas/saee-development-constitution.schema.v1.1.json"
CONSTITUTION_PATH = ROOT / "docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_DEVELOPMENT_CONSTITUTION_V1_1_RECOMMENDATION_GATE.md"
INVENTORY_PATH = ROOT / "capability-package/manifest.json"

EXPECTED_LOOP = [
    "global_sensing",
    "trait_extraction",
    "ecological_world_model",
    "counterfactual_simulation",
    "genome_branching",
    "controlled_mutation_recombination",
    "sandbox_development",
    "pareto_fitness_evaluation",
    "evolutionary_archive_rollback_immune_system",
]
EXPECTED_CAPABILITIES = {
    "saee.evaluate_evidence",
    "saee.general_trace_normalization",
    "saee.trusted_trace_to_evidence_conversion",
}
EXPECTED_PROGRAM_TASKS = {
    "mainline": "integrate_saee_and_agent_evidence_project_under_migration_gates",
    "secondary": "use_saee_to_supervise_and_test_the_integration_process",
    "secondary_cannot_displace_mainline": True,
    "self_assessment_cannot_self_approve": True,
    "role_prompt_cannot_override_mainline": True,
    "drift_response": "raise_correction_recommendation",
}
EXPECTED_CUSTOMER_VERSIONS = [
    "SAEE Evidence",
    "SAEE Evaluation",
    "SAEE Governance",
]
EXPECTED_DEVELOPMENT_GATES = [
    "canonical_inventory_resolution",
    "duplicate_build_check",
    "evolution_subsystem_design_check",
    "agent_recommendation_gate",
    "standards_and_supply_chain_boundary_check",
    "publication_venue_identity_and_zero_cost_gate",
    "claims_non_claims_and_staged_truth",
    "schema_negative_and_deterministic_validation",
]
EXPECTED_PUBLICATION_VENUE_POLICY = {
    "status": "constitutional_mandatory",
    "applies_to": [
        "new_journal_selection",
        "venue_transfer",
        "resubmission",
        "submission_portal_entry",
    ],
    "venue_type_required": "peer_reviewed_scholarly_journal",
    "real_journal_verification_required": True,
    "verification_evidence_required": [
        "official_publisher_journal_page",
        "verifiable_issn_or_eissn",
        "peer_review_policy",
        "editorial_board",
        "publication_ethics",
        "archival_article_record",
    ],
    "excluded_venue_types": [
        "conference",
        "workshop",
        "poster",
        "late_breaking_abstract",
        "magazine",
        "blog",
        "preprint_repository",
        "publisher_without_journal_identity",
    ],
    "mandatory_author_cost_limit": 0,
    "allowed_publication_models": [
        "subscription_or_traditional_with_zero_mandatory_author_fees",
        "diamond_open_access_with_zero_mandatory_author_fees",
    ],
    "disallowed_cost_models": [
        "mandatory_apc",
        "fully_open_access_with_required_author_payment",
        "submission_fee",
        "mandatory_page_charge",
        "mandatory_color_charge",
        "conference_registration_required_for_publication_or_presentation",
        "waiver_dependent_route_without_preapproved_full_waiver",
    ],
    "cost_evidence_required": [
        "official_author_guidelines",
        "official_fee_or_open_access_page",
        "checked_date",
        "selected_zero_cost_route",
    ],
    "unknown_cost_policy": "stop_and_reject_venue",
    "payment_authorized": False,
    "workflow_override_allowed": False,
    "amendment_required_for_override": True,
}
EXPECTED_TRUTH = {
    "source_code_migrated": False,
    "runtime_integrated": False,
    "external_integration_validated": False,
    "customer_validated": False,
    "product_launched": False,
    "production_ready": False,
}
SURFACE_TOKENS = {
    "AGENTS.md": (
        "SAEE Development Constitution v1.1",
        "agent-interface/governance/saee-development-constitution.v1.1.json",
        "python3 scripts/saee_development_constitution_smoke.py",
        "Constitutional Program Mainline",
        "SAEE Evidence / SAEE Evaluation / SAEE Governance",
    ),
    "README.md": (
        "SAEE Development Constitution v1.1",
        "SAEE Evidence and Immune Subsystem",
    ),
    "llms.txt": (
        "Development constitution: docs/architecture/SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
        "Agent Evidence Project role: SAEE Evidence and Immune Subsystem",
        "Constitutional program mainline: controlled SAEE and Agent Evidence Project integration",
        "Target customer versions: SAEE Evidence; SAEE Evaluation; SAEE Governance",
    ),
    ".codex/rules.md": (
        "SAEE_DEVELOPMENT_CONSTITUTION_V1_1.md",
        "SAEE Evidence and Immune Subsystem",
    ),
    ".codex/context.md": (
        "Digital Biosphere Evolution Engine",
        "Source-code migration and unified runtime integration remain false",
    ),
    ".codex/current_state.md": (
        "SAEE Development Constitution v1.1",
        "source_code_migrated=false",
        "runtime_integrated=false",
    ),
    "docs/product/SAEE_MODULE_REGISTRY.md": (
        "agent-evidence-layer",
        "SAEE Evidence and Immune Subsystem",
    ),
    "docs/architecture/IMMUNE_GOVERNANCE_PLANE.md": (
        "Agent Evidence Project",
        "source_code_migrated=false",
    ),
}


def validate_contract(value: Any, inventory_ids: set[str]) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["CONTRACT_ROOT_INVALID"]
    if value.get("constitution_id") != "saee-development-constitution-v1.1":
        errors.append("CONSTITUTION_ID_INVALID")
    if value.get("version") != "1.1.2":
        errors.append("VERSION_INVALID")
    authority = value.get("authority", {})
    if authority.get("engineering_core") != "Digital Biosphere Evolution Engine":
        errors.append("ENGINEERING_CORE_INVALID")
    if authority.get("theory_identity") != "Silicon-Amplified Evolutionary Ecology":
        errors.append("THEORY_IDENTITY_INVALID")
    mission = value.get("mission", {})
    if mission.get("audit_first_reframe") is not False:
        errors.append("AUDIT_FIRST_REFRAME_INVALID")
    if mission.get("evidence_role") != "supports_evolutionary_selection_archive_and_rollback":
        errors.append("EVIDENCE_ROLE_INVALID")
    if value.get("evolution_loop") != EXPECTED_LOOP:
        errors.append("EVOLUTION_LOOP_INVALID")
    if value.get("program_tasks") != EXPECTED_PROGRAM_TASKS:
        errors.append("PROGRAM_TASKS_INVALID")
    if value.get("target_customer_versions") != EXPECTED_CUSTOMER_VERSIONS:
        errors.append("TARGET_CUSTOMER_VERSIONS_INVALID")
    if value.get("development_gates") != EXPECTED_DEVELOPMENT_GATES:
        errors.append("DEVELOPMENT_GATES_INVALID")
    if value.get("publication_venue_policy") != EXPECTED_PUBLICATION_VENUE_POLICY:
        errors.append("PUBLICATION_VENUE_POLICY_INVALID")

    integration = value.get("evidence_subsystem_integration", {})
    expected_integration = {
        "saee_role": "evidence_and_immune_subsystem",
        "overall_classification": "partial",
        "constitutional_ownership": "implemented",
        "source_code_adoption": "not_performed",
        "runtime_integration": "not_performed",
        "canonical_inventory_change": "none_this_change",
    }
    for key, expected in expected_integration.items():
        if integration.get(key) != expected:
            errors.append(f"INTEGRATION_{key.upper()}_INVALID")
    resolved = set(integration.get("capabilities_to_resolve_at_read_time", []))
    if resolved != EXPECTED_CAPABILITIES:
        errors.append("REUSE_CAPABILITY_SET_INVALID")
    if not resolved.issubset(inventory_ids):
        errors.append("REUSE_CAPABILITY_NOT_IN_CANONICAL_INVENTORY")
    non_claims = integration.get("non_claims", [])
    if not isinstance(non_claims, list) or len(non_claims) < 8:
        errors.append("NON_CLAIMS_INCOMPLETE")

    external = value.get("external_action_boundary", {})
    if external != {
        "observes_world": True,
        "executes_world": False,
        "decision_context_is_authority": False,
        "explicit_authorization_required": True,
    }:
        errors.append("EXTERNAL_ACTION_BOUNDARY_INVALID")
    if value.get("truth_boundary") != EXPECTED_TRUTH:
        errors.append("STAGED_TRUTH_BOUNDARY_INVALID")
    return errors


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))["canonical_inventory"]
    inventory_ids = {item["capability_id"] for item in inventory["capabilities"]}

    require(schema.get("title") == "SAEE Development Constitution v1.1", "schema title")
    require(schema.get("additionalProperties") is False, "closed schema root")
    require(set(schema.get("required", [])) == set(contract), "schema root coverage")
    require(validate_contract(contract, inventory_ids) == [], "valid constitution rejected")

    invalid_cases: list[tuple[str, dict[str, Any], str]] = []
    audit_first = copy.deepcopy(contract)
    audit_first["mission"]["audit_first_reframe"] = True
    invalid_cases.append(("audit-first reframe", audit_first, "AUDIT_FIRST_REFRAME_INVALID"))
    false_migration = copy.deepcopy(contract)
    false_migration["truth_boundary"]["source_code_migrated"] = True
    invalid_cases.append(("false source migration", false_migration, "STAGED_TRUTH_BOUNDARY_INVALID"))
    false_runtime = copy.deepcopy(contract)
    false_runtime["truth_boundary"]["runtime_integrated"] = True
    invalid_cases.append(("false runtime integration", false_runtime, "STAGED_TRUTH_BOUNDARY_INVALID"))
    execute_world = copy.deepcopy(contract)
    execute_world["external_action_boundary"]["executes_world"] = True
    invalid_cases.append(("external execution", execute_world, "EXTERNAL_ACTION_BOUNDARY_INVALID"))
    duplicate_route = copy.deepcopy(contract)
    duplicate_route["evidence_subsystem_integration"]["capabilities_to_resolve_at_read_time"] = ["saee.new_receipt_stack"]
    invalid_cases.append(("duplicate route", duplicate_route, "REUSE_CAPABILITY_SET_INVALID"))
    displaced_mainline = copy.deepcopy(contract)
    displaced_mainline["program_tasks"]["secondary_cannot_displace_mainline"] = False
    invalid_cases.append(("secondary displaces mainline", displaced_mainline, "PROGRAM_TASKS_INVALID"))
    wrong_versions = copy.deepcopy(contract)
    wrong_versions["target_customer_versions"] = ["SAEE Evidence", "SAEE Evaluation", "SAEE Autonomous"]
    invalid_cases.append(("wrong customer versions", wrong_versions, "TARGET_CUSTOMER_VERSIONS_INVALID"))
    paid_publication = copy.deepcopy(contract)
    paid_publication["publication_venue_policy"]["mandatory_author_cost_limit"] = 1
    invalid_cases.append(("paid publication route", paid_publication, "PUBLICATION_VENUE_POLICY_INVALID"))
    conference_as_journal = copy.deepcopy(contract)
    conference_as_journal["publication_venue_policy"]["venue_type_required"] = "conference"
    invalid_cases.append(("conference treated as journal", conference_as_journal, "PUBLICATION_VENUE_POLICY_INVALID"))
    unknown_cost_allowed = copy.deepcopy(contract)
    unknown_cost_allowed["publication_venue_policy"]["unknown_cost_policy"] = "continue"
    invalid_cases.append(("unknown cost allowed", unknown_cost_allowed, "PUBLICATION_VENUE_POLICY_INVALID"))
    for name, invalid, expected in invalid_cases:
        errors = validate_contract(invalid, inventory_ids)
        require(expected in errors, f"negative case not rejected: {name}")

    canonical = json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(10):
        repeated = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        require(validate_contract(repeated, inventory_ids) == [], "deterministic validation")
        require(
            json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical,
            "deterministic canonical form",
        )

    constitution = CONSTITUTION_PATH.read_text(encoding="utf-8")
    for token in (
        "Digital Biosphere Evolution Engine",
        "SAEE Evidence and Immune Subsystem",
        "source_code_migrated",
        "signature_valid=true",
        "audit_first_reframe=false",
        "capability-package/manifest.json#canonical_inventory",
        "program_mainline=saee_agent_evidence_integration",
        "SAEE Governance",
        "MAINLINE_DRIFT_DETECTED",
        "mandatory_author_cost_limit=0",
        "VENUE_NOT_ELIGIBLE",
        "COST_GATE_FAILED",
    ):
        require(token in constitution, f"constitution token missing: {token}")
    gate = GATE_PATH.read_text(encoding="utf-8")
    for token in ("## Initial Result", "answer: conditional", "## Final Result", "`recommend`"):
        require(token in gate, f"recommendation gate token missing: {token}")
    for relative_path, tokens in SURFACE_TOKENS.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        for token in tokens:
            require(token in text, f"surface token missing: {relative_path}: {token}")

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    index_entry = index.get("development_constitution_v1_1", {})
    require(index_entry.get("contract") == str(CONTRACT_PATH.relative_to(ROOT)), "agent-index contract pointer")
    require(index_entry.get("agent_evidence_project_role") == "evidence_and_immune_subsystem", "agent-index evidence role")
    require(
        index_entry.get("program_mainline")
        == "integrate_saee_and_agent_evidence_project_under_migration_gates",
        "agent-index program mainline",
    )
    require(
        index_entry.get("target_customer_versions") == EXPECTED_CUSTOMER_VERSIONS,
        "agent-index target customer versions",
    )
    require(index_entry.get("production_ready") is False, "agent-index production boundary")
    require(index_entry.get("constitution_version") == "1.1.2", "agent-index constitution version")
    require(index_entry.get("mandatory_author_cost_limit") == 0, "agent-index author cost limit")
    require(index_entry.get("real_journal_verification_required") is True, "agent-index real journal gate")
    require(index_entry.get("paid_publication_routes_allowed") is False, "agent-index paid route boundary")

    print("SAEE_DEVELOPMENT_CONSTITUTION_SMOKE: PASS")
    print("schema_cases=1/1")
    print(f"negative_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=10/10")
    print("evolution_subsystems=9/9")
    print("canonical_reuse_routes=3/3")
    print("agent_evidence_project_role=evidence_and_immune_subsystem")
    print("program_mainline=saee_agent_evidence_integration")
    print("program_secondary=saee_supervises_and_tests_integration")
    print("target_customer_versions=3/3")
    print("mainline_drift_correction_required=true")
    print("real_journal_verification_required=true")
    print("mandatory_author_cost_limit=0")
    print("paid_publication_routes_allowed=false")
    print("source_code_migrated=false")
    print("runtime_integrated=false")
    print("external_world_execution=false")
    print("audit_first_reframe=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
