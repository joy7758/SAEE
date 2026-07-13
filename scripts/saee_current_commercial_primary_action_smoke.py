#!/usr/bin/env python3
"""Validate the observed-trace current commercial primary action."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SUMMARY = ROOT / "phase_b_product/commercial_readiness/current_commercial_primary_action/current_commercial_primary_action.local.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_CURRENT_COMMERCIAL_PRIMARY_ACTION_SMOKE: FAIL {message}")


def main() -> None:
    data = json.loads(SUMMARY.read_text(encoding="utf-8"))
    require(data["status"] == "agent_first_commercial_preview_is_current_primary_action", "status")
    require(data["recommended_path_id"] == "agent_first_commercial_preview_qianfan_bridge", "path")
    require(data["primary_entrypoint"].endswith("/for-agents"), "agent route")
    require(data["primary_entrypoint_site_version"] == 38, "site version")
    require(data["provider_neutral_oidc_verifier_core_available"] is True, "offline OIDC core")
    require(data["local_signed_jwks_validation_completed"] is True, "signed JWKS validation")
    require(data["local_oidc_rbac_binding_reviewed"] is True, "OIDC RBAC review")
    require(data["oidc_jwks_independent_agent_verdict"] == "recommend", "OIDC agent verdict")
    require(data["oidc_jwks_independent_agent_blockers"] == 0, "OIDC agent blockers")
    require(data["production_blockers_closed_by_oidc_jwks_slice"] == 0, "OIDC production boundary")
    require(data["qianfan_host_bridge"] is True, "Qianfan bridge")
    require(data["qianfan_roundtrips"] == 3 and data["qianfan_negative_cases"] == "13/13", "Qianfan evidence")
    require(data["qianfan_native_mcp_support_proven"] is False, "native MCP boundary")
    require(data["qianfan_provider_retention_terms_verified"] is False and data["qianfan_dpa_completed"] is False, "provider policy boundary")
    require(data["human_primary_interface_language"] == "zh-CN", "Chinese primary UI")
    require(data["agent_contract_languages"] == ["zh-CN", "en"], "bilingual contracts")
    require(data["human_validation_used"] is False and data["agent_validation_primary"] is True, "agent validation policy")
    require(data["synthetic_data_only"] is True and data["real_customer_data_allowed"] is False, "synthetic data boundary")
    require(data["tenant_authorization_policy_reviewed"] is True, "agent authorization review")
    require(data["tenant_secret_boundary_reviewed"] is True, "agent secret review")
    require(data["security_review_completed"] is True, "agent security review")
    require(data["formal_production_security_review_completed"] is False, "formal security boundary")
    require(data["agent_privacy_boundary_review_completed"] is True, "agent privacy boundary")
    require(data["privacy_legal_review_completed"] is False, "privacy legal boundary")
    require(data["evaluation_mode"] == "observed_trace_bundle_evaluation", "mode")
    require(data["observed_agent_trace_evidence_evaluation_available"] is True, "observed adapter")
    require(data["mcp_stdio_adapter_available"] is True, "MCP adapter")
    require(data["mcp_protocol_version"] == "2025-11-25", "MCP protocol")
    require(data["mcp_tools"] == ["describe_saee", "compare_observed_traces"], "MCP tools")
    require(data["commercial_walkthrough_case_count"] == 3, "walkthrough count")
    require(data["commercial_walkthrough_verdict"] == "recommend_3_of_3_agents_blockers_0", "walkthrough verdict")
    require(data["commercial_walkthrough_real_customer_evidence"] is False, "walkthrough customer evidence")
    for key in (
        "human_validation_is_primary", "manual_outreach_required", "trace_capture_by_saee",
        "mcp_dynamic_tools", "mcp_arbitrary_file_input",
        "trace_authenticity_verified", "pii_absence_verified_by_saee",
        "candidate_code_executed", "external_system_executed", "customer_contacted",
        "customer_validated", "production_ready", "product_launched", "private_core_exposed",
    ):
        require(data[key] is False, f"{key} must be false")
    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    require(index["current_commercial_primary_action_v0_1"] == data, "index sync")
    require(index["observed_trace_evidence_adapter_v0_1"]["golden_fixture_count"] == 12, "fixtures")
    require(index["mcp_stdio_adapter_v0_1"]["tools"] == ["describe_saee", "compare_observed_traces"], "index MCP")
    require(index["commercial_walkthrough_cases_v0_1"]["candidate_rows_checked"] == 8, "walkthrough rows")
    require(index["commercial_walkthrough_cases_v0_1"]["numeric_drift_count"] == 0, "walkthrough drift")
    require(index["qianfan_host_bridge_v0_1"]["status"] == "recommend_limited_user_supplied_qianfan_host_bridge", "Qianfan index")
    require(index["qianfan_provider_data_processing_v0_1"]["blockers_closed"] == 0, "Qianfan data profile")
    qianfan_policy = index["qianfan_provider_data_processing_v0_1"]
    require(qianfan_policy["observed_policy_clause_count"] == 3, "Qianfan policy clauses")
    require(qianfan_policy["retention_terms_verified"] is False and qianfan_policy["dpa_completed"] is False, "Qianfan policy hold")
    preview_request = index["controlled_preview_request_v0_1"]
    require(preview_request["tenant_scope_explicit"] is True, "preview request tenant scope")
    require(preview_request["reserved_experiment_prefix_rejected"] is True, "preview request reserved prefix")
    require(preview_request["external_execution"] is False and preview_request["blockers_closed"] == 0, "preview request boundary")
    quote_request = index["commercial_quote_request_v0_1"]
    require(quote_request["quote_status"] == "owner_pricing_review_required", "quote status")
    require(quote_request["public_price_points_approved"] is False and quote_request["payment_enabled"] is False, "quote pricing/payment boundary")
    require(quote_request["blockers_closed"] == 0, "quote blocker boundary")
    support_request = index["agent_support_intake_v0_1"]
    require(support_request["support_status"] == "owner_support_channel_required", "support status")
    require(support_request["external_dispatch_performed"] is False and support_request["customer_contacted"] is False, "support dispatch/contact boundary")
    require(support_request["blockers_closed"] == 0, "support blocker boundary")
    plan = index["commercial_blocker_dependency_plan_v0_1"]
    require(plan["phase_count"] == 5 and plan["planned_blocker_count"] == 24, "dependency plan counts")
    require(plan["open_blocker_count"] == 24 and plan["blockers_closed_by_plan"] == 0, "dependency plan hold")
    require(plan["execution_authorized"] is False and plan["production_ready"] is False, "dependency plan boundary")
    authorization = index["phase_1_local_execution_authorization_v0_1"]
    require(authorization["target_blocker_count"] == 4, "Phase 1 authorization targets")
    require(authorization["local_code"] is True and authorization["sanitized_local_evidence"] is True, "Phase 1 local authorization")
    require(authorization["external_calls_authorized"] is False and authorization["production_deployment_authorized"] is False, "Phase 1 external boundary")
    require(authorization["blockers_closed"] == 0, "Phase 1 authorization closure boundary")
    rbac_consistency = index["rbac_role_permission_consistency_v0_1"]
    require(rbac_consistency["negative_cases"] == "5/5", "RBAC consistency negative cases")
    require(rbac_consistency["role_permission_consistency_enforced"] is True, "RBAC role-permission consistency")
    require(rbac_consistency["production_auth_ready"] is False and rbac_consistency["blockers_closed"] == 0, "RBAC production boundary")
    tenant_guard = index["tenant_required_storage_guard_v0_1"]
    require(tenant_guard["memory_store_unscoped_operations_denied"] is True, "tenant guard memory")
    require(tenant_guard["sqlite_store_unscoped_operations_denied"] is True, "tenant guard sqlite")
    require(tenant_guard["requires_factory_configured_store"] is True, "tenant guard factory")
    require(tenant_guard["unscoped_operation_cases"] == "7/7", "tenant guard negative cases")
    require(tenant_guard["storage_tenant_membership_enforcement_available"] is True, "tenant membership guard")
    require(tenant_guard["unlisted_tenant_operations_denied"] is True, "tenant membership denial")
    require(tenant_guard["unlisted_tenant_operation_cases"] == "7/7", "tenant membership negative cases")
    require(tenant_guard["membership_scope"] == "configured_preview_allowlist_not_identity_authentication", "tenant membership scope")
    require(tenant_guard["independent_agent_verdict"] == "recommend", "tenant guard agent verdict")
    require(tenant_guard["independent_agent_blockers"] == 0, "tenant guard agent blockers")
    membership = index["storage_tenant_membership_enforcement_v0_1"]
    require(membership["independent_agent_verdict"] == "recommend", "membership agent verdict")
    require(membership["independent_agent_blockers"] == 0, "membership agent blockers")
    require(membership["unlisted_tenant_operation_cases"] == "7/7", "membership cases")
    require(membership["tenant_authorization_enabled"] is False, "membership authorization boundary")
    require(membership["production_tenant_storage_isolated"] is False and membership["blockers_closed"] == 0, "membership production boundary")
    secret_boundary = index["tenant_secret_boundary_v0_1"]
    require(secret_boundary["independent_agent_verdict"] == "recommend", "secret boundary agent verdict")
    require(secret_boundary["independent_agent_blockers"] == 0, "secret boundary agent blockers")
    require(secret_boundary["negative_cases"] == "24/24", "secret boundary cases")
    require(secret_boundary["secret_echo_count"] == 0, "secret boundary echo")
    require(secret_boundary["tenant_secret_boundary_reviewed"] is False, "secret boundary production review")
    require(secret_boundary["production_ready"] is False and secret_boundary["blockers_closed"] == 0, "secret boundary production hold")
    bound_auth = index["bound_tenant_authorization_v0_1"]
    require(bound_auth["independent_agent_verdict"] == "recommend", "bound auth agent verdict")
    require(bound_auth["independent_agent_blockers"] == 0, "bound auth agent blockers")
    require(bound_auth["negative_cases"] == "14/14", "bound auth cases")
    require(bound_auth["context_capability_hmac_verified"] is True, "bound auth capability")
    require(bound_auth["storage_operation_permission_bound"] is True, "bound auth permission")
    require(bound_auth["tenant_authorization_policy_reviewed"] is False, "bound auth production review")
    require(bound_auth["production_ready"] is False and bound_auth["blockers_closed"] == 0, "bound auth production hold")
    tenant_agent_review = index["tenant_agent_review_evidence_v0_1"]
    require(tenant_agent_review["tenant_authorization_policy_reviewed"] is True, "tenant agent authorization review")
    require(tenant_agent_review["tenant_secret_boundary_reviewed"] is True, "tenant agent secret review")
    security_review = index["tenant_security_agent_review_v0_1"]
    require(security_review["security_review_completed"] is True, "tenant security review")
    require(security_review["formal_production_security_review_completed"] is False, "formal security review boundary")
    privacy_review = index["tenant_privacy_agent_review_v0_1"]
    require(privacy_review["agent_privacy_boundary_review_completed"] is True, "tenant privacy review")
    require(privacy_review["personal_data_boundary_cases"] == "29/29", "privacy cases")
    require(privacy_review["evidence_tamper_negative_cases"] == "16/16", "privacy evidence cases")
    require(privacy_review["privacy_legal_review_completed"] is False, "privacy legal hold")
    require(privacy_review["production_ready"] is False and privacy_review["blockers_closed"] == 0, "privacy production hold")
    require(tenant_guard["default_local_unscoped_mode_preserved"] is True, "tenant guard local compatibility")
    require(tenant_guard["production_tenant_storage_isolated"] is False and tenant_guard["migration_executed"] is False, "tenant guard production boundary")
    require(tenant_guard["blockers_closed"] == 0, "tenant guard blocker boundary")
    require(index["commercial_site_surface"]["human_primary_interface_language"] == "zh-CN", "site language")
    print(
        "SAEE_CURRENT_COMMERCIAL_PRIMARY_ACTION_SMOKE: PASS "
        f"site_deployed={str(data['primary_entrypoint_deployment_succeeded']).lower()} "
        "mode=observed_trace_bundle_evaluation mcp_tools=2 "
        "human_validation_primary=false trace_capture=false production_ready=false"
    )


if __name__ == "__main__":
    main()
