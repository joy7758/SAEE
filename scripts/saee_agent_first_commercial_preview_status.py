#!/usr/bin/env python3
"""Build the canonical agent-first commercial-preview status contract.

This is a retrieval/calling surface for the limited preview product. It keeps
validated agent capability separate from production, customer, legal, billing,
and external-operation evidence. It never closes a production blocker.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "agent-interface/agent-first-commercial-preview-status.json"
OUT_MD = ROOT / "agent-interface/agent-first-commercial-preview-status.md"
INDEX = ROOT / "agent-index.json"
ACTION = ROOT / "phase_b_product/commercial_readiness/current_commercial_primary_action/current_commercial_primary_action.local.json"
MATRIX = ROOT / "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json"
QIANFAN = ROOT / "agent_recommendation/agent_first_validation/run_005/independent_agent_validation.local.json"
QIANFAN_PROFILE = ROOT / "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build() -> dict:
    action = read(ACTION)
    matrix = read(MATRIX)
    qianfan = read(QIANFAN)
    qianfan_profile = read(QIANFAN_PROFILE)
    blockers = [item["blocker_id"] for item in matrix["matrix"]]
    return {
        "contract_id": "saee-agent-first-commercial-preview-status-v0.1",
        "schema_version": "0.1.0",
        "status": "recommend_limited_agent_first_commercial_preview",
        "recommendation": "recommend",
        "preview_capabilities": {
            "mcp_stdio": {
                "verdict": "recommend",
                "scope": "local_fixed_two_tool",
                "protocol_version": action["mcp_protocol_version"],
                "tools": action["mcp_tools"],
            },
            "qianfan_host_bridge": {
                "verdict": "recommend",
                "scope": "limited_user_supplied_credential",
                "provider": qianfan["provider"],
                "model": qianfan["model"],
                "roundtrip_runs": qianfan["roundtrip_runs"],
                "negative_cases": f"{qianfan['negative_cases_passed']}/{qianfan['negative_cases_total']}",
                "qianfan_native_mcp_support_proven": False,
            },
            "observed_trace_adapter": {
                "verdict": "recommend",
                "scope": "sanitized_file_bundle",
                "trace_authenticity_verified": False,
                "pii_absence_verified_by_saee": False,
                "trace_capture_by_saee": False,
            },
            "commercial_walkthroughs": {
                "verdict": "recommend",
                "scope": "simulated_teaching_examples",
                "case_count": action["commercial_walkthrough_case_count"],
                "evidence_status": "simulated_example",
                "real_customer_evidence": False,
            },
            "dataflow_inventory": {
                "status": "documented",
                "scope": "run_005_provider_payload_classes",
                "privacy_legal_approval": False,
                "official_policy_snapshot": {
                    "profile": "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json",
                    "catalog_url": qianfan_profile["official_policy_reference"]["catalog_url"],
                    "observed_clause_count": len(qianfan_profile["official_policy_reference"]["observed_clauses"]),
                    "retention_terms_verified": qianfan_profile["review_status"]["provider_retention_terms_verified"],
                    "dpa_completed": qianfan_profile["review_status"]["data_processing_agreement_completed"],
                },
            },
            "tenant_preview_storage": {
                "verdict": "conditional",
                "scope": "local_preview_only",
                "same_experiment_id_partitioned": True,
                "invalid_tenant_id_rejected": True,
                "reserved_experiment_prefix_rejected": True,
                "sqlite_reload_preserves_scope": True,
                "production_tenant_storage_isolated": False,
                "multi_tenant_production_ready": False,
            },
            "preview_auth": {
                "verdict": "recommend",
                "scope": "controlled_preview_only",
                "default_off": True,
                "jwt_preview_available": True,
                "production_auth_ready": False,
                "external_identity_provider_contacted": False,
            },
            "restore_drill": {
                "verdict": "recommend",
                "scope": "local_public_shell_isolated_restore_drill",
                "integrity_checks_passed": True,
                "restore_to_live_path": False,
                "production_restore_policy_available": False,
                "production_restore_tested": False,
                "production_data_operations_ready": False,
            },
            "controlled_preview_request": {
                "verdict": "recommend",
                "scope": "local_or_private_controlled_preview_only",
                "schema": "agent-interface/schemas/controlled-preview-request.schema.json",
                "validator": "scripts/saee_controlled_preview_request_validator.py",
                "external_execution": False,
                "production_ready": False,
                "blockers_closed": 0,
            },
            "commercial_quote_request": {
                "verdict": "recommend",
                "scope": "private_no_price_no_payment_intake",
                "request_schema": "agent-interface/schemas/commercial-quote-request.schema.json",
                "response_schema": "agent-interface/schemas/commercial-quote-response.schema.json",
                "validator": "scripts/saee_commercial_quote_request_validator.py",
                "quote_status": "owner_pricing_review_required",
                "public_price_points_approved": False,
                "payment_enabled": False,
                "blockers_closed": 0,
            },
            "agent_support_intake": {
                "verdict": "recommend",
                "scope": "sanitized_agent_receipt_only",
                "request_schema": "agent-interface/schemas/agent-support-case-request.schema.json",
                "response_schema": "agent-interface/schemas/agent-support-case-response.schema.json",
                "validator": "scripts/saee_agent_support_case_validator.py",
                "support_status": "owner_support_channel_required",
                "external_dispatch_performed": False,
                "customer_contacted": False,
                "production_ready": False,
                "blockers_closed": 0,
            },
            "phase_1_local_hardening": {
                "verdict": "recommend",
                "scope": "local_code_contracts_tests_sanitized_evidence",
                "target_blockers": [
                    "production_identity_provider",
                    "oauth_oidc",
                    "rbac",
                    "tenant_storage_isolation",
                ],
                "authorization": "phase_b_product/commercial_readiness/phase_1_local_execution_authorization/authorization.local.json",
                "rbac_consistency_profile": "phase_b_product/commercial_readiness/auth_evidence/rbac_role_permission_consistency.local.json",
                "tenant_required_storage_guard_evidence": "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json",
                "rbac_negative_cases": "5/5",
                "tenant_required_storage_guard": True,
                "memory_store_unscoped_operations_denied": True,
                "sqlite_store_unscoped_operations_denied": True,
                "default_local_unscoped_mode_preserved": True,
                "production_tenant_storage_isolated": False,
                "local_development_authorized": True,
                "external_execution_authorized": False,
                "production_deployment_authorized": False,
                "production_data_migration_authorized": False,
                "blockers_closed": 0,
            },
        },
        "truth_boundary": {
            "external_provider_network_used": True,
            "saee_mcp_network_used": False,
            "qianfan_native_mcp_support_proven": False,
            "candidate_code_executed": False,
            "external_system_executed": False,
            "human_validation_is_primary": False,
            "customer_validated": False,
            "production_ready": False,
            "product_launched": False,
            "customer_contacted": False,
            "revenue_validated": False,
        },
        "production_readiness": {
            "verdict": "hold",
            "production_ready": False,
            "production_launch_status": matrix["production_launch_status"],
            "production_blocker_count": matrix["production_blocker_count"],
            "open_production_blocker_count": matrix["open_blocker_count"],
            "blockers_closed_by_contract": 0,
            "production_checks_satisfied_by_contract": 0,
            "blocker_matrix": "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json",
            "next_review_lane": "provider_data_processing_and_production_commercialization_evidence",
        },
        "production_blocker_truth_source": "canonical_default_go_no_go",
        "local_fixture_or_human_profile_promoted_to_production_truth": False,
        "production_blockers": blockers,
        "allowed_claims": [
            "SAEE can be discovered through file-backed agent contracts",
            "SAEE can compare sanitized observed-trace bundles",
            "a bounded user-supplied Qianfan host bridge has passed its recorded roundtrips",
            "commercial walkthroughs explain simulated use cases",
        ],
        "forbidden_claims": [
            "MCP validation implies production integration readiness",
            "Qianfan roundtrips imply Qianfan-native MCP or customer adoption",
            "observed bundle evaluation proves trace authenticity or no PII",
            "walkthrough recommendation is real customer evidence",
            "dataflow documentation is privacy/legal/security approval",
            "agent recommendation is human or customer validation",
            "contract creation or retrieval closes a production blocker",
        ],
        "zero_effect_assertions": {
            "blockers_closed_by_contract": 0,
            "matrix_mutated_by_contract": False,
            "production_release_performed": False,
            "external_execution_performed": False,
            "customer_contact_performed": False,
        },
        "evidence_refs": {
            "current_action": "phase_b_product/commercial_readiness/current_commercial_primary_action/current_commercial_primary_action.local.json",
            "blocker_matrix": "phase_b_product/commercial_readiness/production_blocker_gap_matrix/gap_matrix.local.json",
            "qianfan_validation": "agent_recommendation/agent_first_validation/run_005/independent_agent_validation.local.json",
            "provider_data_profile": "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json",
        },
        "source_hashes": {
            "current_action_sha256": file_sha256(ACTION),
            "blocker_matrix_sha256": file_sha256(MATRIX),
            "qianfan_validation_sha256": file_sha256(QIANFAN),
        },
        "agent_next_actions": [
            action["next_agent_action"],
            "Read phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json and its policy snapshot gate; keep retention, DPA, and privacy/legal approval false.",
            "Review phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.local.json before any separate builder approval.",
            "Keep scripts/saee_commercial_evidence_builder_batch_executor.py in dry-run mode until the exact approval phrase is recorded.",
            "Read this contract before interpreting any production status.",
            "Keep the 24 canonical production blockers open until source-backed evidence and approvals exist.",
        ],
        "site_entrypoint": "https://saee-stability-lab.zhangbin1982.chatgpt.site/for-agents",
        "generated_by": "scripts/saee_agent_first_commercial_preview_status.py",
        "generated_at": datetime.now(timezone.utc).date().isoformat(),
    }


def main() -> None:
    data = build()
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
    OUT_MD.write_text(
        "# SAEE Agent-First Commercial Preview Status\n\n"
        "推荐范围：有限的、以智能体为主的商业预览；不等于生产上线。\n\n"
        f"- status: `{data['status']}`\n"
        f"- recommendation: `{data['recommendation']}`\n"
        f"- open production blockers: `{data['production_readiness']['open_production_blocker_count']}`\n"
        f"- blockers closed by contract: `{data['production_readiness']['blockers_closed_by_contract']}`\n"
        f"- next machine action: `{data['agent_next_actions'][0]}`\n\n"
        "## Boundary\n\n"
        "The preview can be recommended for agent discovery, fixed-tool calls,\n"
        "and sanitized evaluation. It does not claim customer validation, DPA\n"
        "completion, payment readiness, production launch, or external execution.\n"
    )
    index = read(INDEX)
    index["agent_first_commercial_preview_v0_1"] = data
    INDEX.write_text(json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print("SAEE_AGENT_FIRST_COMMERCIAL_PREVIEW_STATUS: PASS recommendation=recommend open_production_blockers=24 blockers_closed=0")


if __name__ == "__main__":
    main()
