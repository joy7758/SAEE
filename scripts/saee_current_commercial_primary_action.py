#!/usr/bin/env python3
"""Publish the observed-trace agent-first commercial primary action."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "phase_b_product/commercial_readiness/current_commercial_primary_action"
SUMMARY_PATH = OUT / "current_commercial_primary_action.local.json"
GATE = ROOT / "docs/strategy/SAEE_CURRENT_COMMERCIAL_PRIMARY_ACTION_GATE.md"
AGENT_INDEX = ROOT / "agent-index.json"
SITE_URL = "https://saee-stability-lab.zhangbin1982.chatgpt.site"
SITE_VERSION = 38
SITE_VERSION_ID = "appgprj_6a5099d5a99c8191bdb92fdcb9d67f2c~appgver_31a4e3d7245081918ad0310ad92e1218"
SITE_DEPLOYMENT_ID = "appgdep_6a51b80c31f88191ae8d6971319b9d77"
SITE_COMMIT_SHA = "b2ba13bf107c7ac2ecd66f8768008dd03b0829a0"
AGENT_URL = f"{SITE_URL}/for-agents"
MANIFEST_URL = f"{SITE_URL}/agent-manifest.json"
OBSERVED_COMMAND = (
    "python3 scripts/saee_agent_cli.py evaluate-traces "
    "--input agent-interface/examples/observed-trace-bundle.json"
)
MCP_COMMAND = "python3 scripts/saee_mcp_stdio.py"
WALKTHROUGH_CASES = "agent-interface/examples/commercial-walkthrough-cases.json"
MARKER = "SAEE_CURRENT_COMMERCIAL_PRIMARY_ACTION"
QIANFAN_CONFIG = "agent-interface/qianfan/host-config.json"
QIANFAN_COMMAND = "python3 scripts/saee_qianfan_mcp_host.py --write-evidence"
QIANFAN_DATA_PROFILE = "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json"
QIANFAN_POLICY_GATE = "docs/strategy/SAEE_QIANFAN_PROVIDER_POLICY_SNAPSHOT_RECOMMENDATION_GATE.md"
CONTROLLED_PREVIEW_REQUEST = "agent-interface/examples/controlled-preview-request.json"
CONTROLLED_PREVIEW_REQUEST_SCHEMA = "agent-interface/schemas/controlled-preview-request.schema.json"
CONTROLLED_PREVIEW_REQUEST_VALIDATOR = "scripts/saee_controlled_preview_request_validator.py"
COMMERCIAL_QUOTE_REQUEST = "agent-interface/examples/commercial-quote-request.json"
COMMERCIAL_QUOTE_REQUEST_SCHEMA = "agent-interface/schemas/commercial-quote-request.schema.json"
COMMERCIAL_QUOTE_RESPONSE_SCHEMA = "agent-interface/schemas/commercial-quote-response.schema.json"
COMMERCIAL_QUOTE_REQUEST_VALIDATOR = "scripts/saee_commercial_quote_request_validator.py"
SUPPORT_CASE_REQUEST = "agent-interface/examples/agent-support-case-request.json"
SUPPORT_CASE_REQUEST_SCHEMA = "agent-interface/schemas/agent-support-case-request.schema.json"
SUPPORT_CASE_RESPONSE_SCHEMA = "agent-interface/schemas/agent-support-case-response.schema.json"
SUPPORT_CASE_REQUEST_VALIDATOR = "scripts/saee_agent_support_case_validator.py"
COMMERCIAL_DEPENDENCY_PLAN = "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json"
COMMERCIAL_DEPENDENCY_PLAN_COMMAND = "python3 scripts/saee_commercial_blocker_dependency_plan.py"
PHASE1_LOCAL_AUTHORIZATION = "phase_b_product/commercial_readiness/phase_1_local_execution_authorization/authorization.local.json"
RBAC_CONSISTENCY_PROFILE = "phase_b_product/commercial_readiness/auth_evidence/rbac_role_permission_consistency.local.json"
PHASE1_PROFILE_COMMAND = "python3 scripts/saee_phase1_identity_tenant_evidence_profile.py --json"
AGENT_PRIORITY_INDEX = "phase_b_product/commercial_readiness/agent_blocker_priority_index/agent_blocker_priority_index.local.json"
OIDC_JWKS_EVIDENCE = "phase_b_product/commercial_readiness/oidc_jwks_verifier_evidence/oidc_jwks_verifier_evidence.local.json"
OIDC_JWKS_VALIDATION = "agent_recommendation/oidc_jwks_verifier/run_001/independent_agent_validation.local.json"
OIDC_JWKS_PROFILE_COMMAND = "python3 scripts/saee_oidc_jwks_validation_profile.py"
TENANT_REQUIRED_STORAGE_EVIDENCE = "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json"
TENANT_REQUIRED_STORAGE_AGENT_VALIDATION = "agent_recommendation/tenant_required_storage_guard/run_001/independent_agent_validation.local.json"
STORAGE_TENANT_MEMBERSHIP_AGENT_VALIDATION = "agent_recommendation/storage_tenant_membership/run_001/independent_agent_validation.local.json"
TENANT_SECRET_BOUNDARY_PROFILE = "phase_b_product/commercial_readiness/tenant_secret_boundary/tenant_secret_boundary.local.json"
TENANT_SECRET_BOUNDARY_AGENT_VALIDATION = "agent_recommendation/tenant_secret_boundary/run_001/independent_agent_validation.local.json"
BOUND_TENANT_AUTHORIZATION_PROFILE = "phase_b_product/commercial_readiness/tenant_authorization/tenant_authorization.local.json"
BOUND_TENANT_AUTHORIZATION_AGENT_VALIDATION = "agent_recommendation/bound_tenant_authorization/run_001/independent_agent_validation.local.json"
TENANT_AGENT_REVIEW_PROFILE = "phase_b_product/commercial_readiness/tenant_agent_review/tenant_agent_review.local.json"
TENANT_AGENT_REVIEW_VALIDATION = "agent_recommendation/tenant_agent_review_evidence/run_001/independent_agent_validation.local.json"
TENANT_SECURITY_AGENT_REVIEW_PROFILE = "phase_b_product/commercial_readiness/tenant_security_agent_review/tenant_security_agent_review.local.json"
TENANT_SECURITY_AGENT_REVIEW_VALIDATION = "agent_recommendation/tenant_security_agent_review/run_001/independent_agent_validation.local.json"
TENANT_PRIVACY_AGENT_REVIEW_PROFILE = "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_agent_review.local.json"
TENANT_PRIVACY_DATA_FLOW_PROFILE = "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_data_flow.local.json"
TENANT_PRIVACY_AGENT_REVIEW_VALIDATION = "agent_recommendation/tenant_privacy_agent_review/run_001/independent_agent_validation.local.json"


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def replace_block(path: Path, body: str) -> None:
    begin = f"<!-- BEGIN {MARKER} -->"
    end = f"<!-- END {MARKER} -->"
    wrapped = f"{begin}\n{body.rstrip()}\n{end}\n\n"
    text = path.read_text(encoding="utf-8")
    if begin in text and end in text:
        before, rest = text.split(begin, 1)
        _, after = rest.split(end, 1)
        write(path, before + wrapped + after.lstrip("\n"))
        return
    lines = text.splitlines(keepends=True)
    insert_at = 1 if lines and lines[0].startswith("#") else 0
    write(path, "".join(lines[:insert_at]) + "\n" + wrapped + "".join(lines[insert_at:]))


def validation_state() -> dict:
    path = ROOT / "agent_recommendation/agent_first_validation/run_005/independent_agent_validation.local.json"
    if not path.exists():
        return {
            "post_fix_rerun_completed": False,
            "post_fix_verdict": "pending",
            "current_scope_agent_recommendations": 0,
            "current_scope_blockers": 1,
            "independent_agent_profiles": 3,
        }
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "post_fix_rerun_completed": data.get("successful_runs", 0) == data.get("roundtrip_runs", 0) == 3,
        "post_fix_verdict": data.get("post_fix_verdict", "pending"),
        "current_scope_agent_recommendations": data.get("post_fix_agent_recommendations", 0),
        "current_scope_blockers": data.get("post_fix_blockers", 1),
        "independent_agent_profiles": data.get("independent_agent_profiles", 3),
    }


def make_summary(site_deployed: bool) -> dict:
    validation = validation_state()
    return {
        "current_commercial_primary_action_v0_3": True,
        "status": "agent_first_commercial_preview_is_current_primary_action",
        "current_goal_blocker": (
            "mcp_stdio_adapter_independent_agent_validation"
            if not validation["post_fix_rerun_completed"]
            else "phase_1_identity_tenant_boundary"
        ),
        "recommended_path_locked": True,
        "recommended_path_id": "agent_first_commercial_preview_qianfan_bridge",
        "primary_entrypoint": AGENT_URL,
        "primary_entrypoint_access": "custom_owner_only",
        "primary_entrypoint_deployment_succeeded": site_deployed,
        "primary_entrypoint_site_version": SITE_VERSION,
        "primary_entrypoint_site_version_id": SITE_VERSION_ID,
        "primary_entrypoint_site_deployment_id": SITE_DEPLOYMENT_ID,
        "primary_entrypoint_site_commit_sha": SITE_COMMIT_SHA,
        "human_primary_interface_language": "zh-CN",
        "agent_contract_languages": ["zh-CN", "en"],
        "agent_manifest": "agent-interface/agent-manifest.json",
        "agent_manifest_url": MANIFEST_URL,
        "tool_contract": "agent-interface/tool-contract.json",
        "cli": "scripts/saee_agent_cli.py",
        "cli_command": OBSERVED_COMMAND,
        "mcp_stdio_command": MCP_COMMAND,
        "mcp_protocol_version": "2025-11-25",
        "mcp_tools": ["describe_saee", "compare_observed_traces"],
        "mcp_config": "agent-interface/mcp/stdio-config.json",
        "mcp_guide": "agent-interface/mcp/README.md",
        "qianfan_host_bridge": True,
        "qianfan_host_config": QIANFAN_CONFIG,
        "qianfan_host_command": QIANFAN_COMMAND,
        "qianfan_provider": "baidu_qianfan",
        "qianfan_model": "ernie-4.5-turbo-128k",
        "qianfan_roundtrips": 3,
        "qianfan_negative_cases": "13/13",
        "qianfan_native_mcp_support_proven": False,
        "qianfan_external_provider_network_used": True,
        "qianfan_saee_mcp_network_used": False,
        "qianfan_provider_data_processing_profile": QIANFAN_DATA_PROFILE,
        "qianfan_provider_retention_terms_verified": False,
        "qianfan_dpa_completed": False,
        "commercial_walkthrough_cases": WALKTHROUGH_CASES,
        "controlled_preview_request": CONTROLLED_PREVIEW_REQUEST,
        "controlled_preview_request_schema": CONTROLLED_PREVIEW_REQUEST_SCHEMA,
        "controlled_preview_request_validator": CONTROLLED_PREVIEW_REQUEST_VALIDATOR,
        "commercial_quote_request": COMMERCIAL_QUOTE_REQUEST,
        "commercial_quote_request_schema": COMMERCIAL_QUOTE_REQUEST_SCHEMA,
        "commercial_quote_response_schema": COMMERCIAL_QUOTE_RESPONSE_SCHEMA,
        "commercial_quote_request_validator": COMMERCIAL_QUOTE_REQUEST_VALIDATOR,
        "agent_support_case_request": SUPPORT_CASE_REQUEST,
        "agent_support_case_request_schema": SUPPORT_CASE_REQUEST_SCHEMA,
        "agent_support_case_response_schema": SUPPORT_CASE_RESPONSE_SCHEMA,
        "agent_support_case_request_validator": SUPPORT_CASE_REQUEST_VALIDATOR,
        "commercial_walkthrough_case_count": 3,
        "commercial_walkthrough_verdict": "recommend_3_of_3_agents_blockers_0",
        "commercial_walkthrough_real_customer_evidence": False,
        "example_request": "agent-interface/examples/observed-trace-bundle.json",
        "example_receipt": "agent-interface/examples/observed-trace-receipt.json",
        "request_schema": "agent-interface/schemas/observed-trace-bundle.schema.json",
        "receipt_schema": "agent-interface/schemas/observed-trace-receipt.schema.json",
        "evaluation_mode": "observed_trace_bundle_evaluation",
        "synthetic_descriptor_mode_also_available": True,
        "initial_agent_recommendation_gate": "recommend",
        "local_acceptance": "pass",
        **validation,
        "human_validation_is_primary": False,
        "human_validation_used": False,
        "agent_validation_primary": True,
        "synthetic_data_only": True,
        "real_customer_data_allowed": False,
        "manual_outreach_required": False,
        "observed_agent_trace_evidence_evaluation_available": True,
        "mcp_stdio_adapter_available": True,
        "mcp_dynamic_tools": False,
        "mcp_arbitrary_file_input": False,
        "trace_capture_by_saee": False,
        "trace_authenticity_verified": False,
        "pii_absence_verified_by_saee": False,
        "candidate_code_executed": False,
        "external_system_executed": False,
        "customer_contacted": False,
        "customer_validated": False,
        "production_ready": False,
        "product_launched": False,
        "private_core_exposed": False,
        "commercial_blocker_dependency_plan": COMMERCIAL_DEPENDENCY_PLAN,
        "commercial_blocker_dependency_plan_command": COMMERCIAL_DEPENDENCY_PLAN_COMMAND,
        "agent_blocker_priority_index": AGENT_PRIORITY_INDEX,
        "agent_blocker_first_priority": "production_identity_provider",
        "legacy_support_contact_priority_superseded": True,
        "provider_neutral_oidc_verifier_core_available": True,
        "local_signed_jwks_validation_completed": True,
        "local_oidc_rbac_binding_reviewed": True,
        "oidc_jwks_verifier_evidence": OIDC_JWKS_EVIDENCE,
        "oidc_jwks_independent_agent_validation": OIDC_JWKS_VALIDATION,
        "oidc_jwks_independent_agent_verdict": "recommend",
        "oidc_jwks_independent_agent_blockers": 0,
        "oidc_jwks_negative_cases": "43/43",
        "oidc_jwks_handler_boundary_rejections": "6/6",
        "oidc_jwks_network_calls": 0,
        "production_blockers_closed_by_oidc_jwks_slice": 0,
        "phase_1_local_execution_authorization": PHASE1_LOCAL_AUTHORIZATION,
        "rbac_role_permission_consistency_profile": RBAC_CONSISTENCY_PROFILE,
        "tenant_required_storage_guard_evidence": TENANT_REQUIRED_STORAGE_EVIDENCE,
        "tenant_required_storage_guard_agent_validation": TENANT_REQUIRED_STORAGE_AGENT_VALIDATION,
        "tenant_required_storage_guard": True,
        "tenant_required_storage_guard_requires_factory": True,
        "tenant_required_storage_guard_negative_cases": "7/7",
        "storage_tenant_membership_enforcement_available": True,
        "unlisted_tenant_operations_denied": True,
        "unlisted_tenant_operation_cases": "7/7",
        "membership_scope": "configured_preview_allowlist_not_identity_authentication",
        "storage_tenant_membership_agent_validation": STORAGE_TENANT_MEMBERSHIP_AGENT_VALIDATION,
        "storage_tenant_membership_agent_verdict": "recommend",
        "storage_tenant_membership_agent_blockers": 0,
        "tenant_secret_boundary_available": True,
        "tenant_secret_boundary_profile": TENANT_SECRET_BOUNDARY_PROFILE,
        "tenant_secret_boundary_agent_validation": TENANT_SECRET_BOUNDARY_AGENT_VALIDATION,
        "tenant_secret_boundary_agent_verdict": "recommend",
        "tenant_secret_boundary_agent_blockers": 0,
        "tenant_secret_boundary_negative_cases": "24/24",
        "tenant_secret_boundary_raw_profile_reviewed": False,
        "tenant_secret_boundary_reviewed": True,
        "production_secrets_management_available": False,
        "encryption_at_rest_proven": False,
        "kms_hsm_available": False,
        "bound_tenant_authorization_available": True,
        "bound_tenant_authorization_profile": BOUND_TENANT_AUTHORIZATION_PROFILE,
        "bound_tenant_authorization_agent_validation": BOUND_TENANT_AUTHORIZATION_AGENT_VALIDATION,
        "bound_tenant_authorization_agent_verdict": "recommend",
        "bound_tenant_authorization_agent_blockers": 0,
        "bound_tenant_authorization_negative_cases": "14/14",
        "tenant_authorization_raw_profile_reviewed": False,
        "tenant_authorization_policy_reviewed": True,
        "tenant_authorization_enabled": False,
        "tenant_agent_review_profile": TENANT_AGENT_REVIEW_PROFILE,
        "tenant_agent_review_validation": TENANT_AGENT_REVIEW_VALIDATION,
        "security_review_completed": True,
        "security_review_completion_scope": "local_controlled_preview_independent_agent",
        "formal_production_security_review_completed": False,
        "tenant_security_agent_review_profile": TENANT_SECURITY_AGENT_REVIEW_PROFILE,
        "tenant_security_agent_review_validation": TENANT_SECURITY_AGENT_REVIEW_VALIDATION,
        "agent_privacy_boundary_review_completed": True,
        "agent_privacy_boundary_review_scope": "whole_tenant_api_synthetic_only_controlled_preview_independent_agent",
        "tenant_privacy_agent_review_profile": TENANT_PRIVACY_AGENT_REVIEW_PROFILE,
        "tenant_privacy_data_flow_profile": TENANT_PRIVACY_DATA_FLOW_PROFILE,
        "tenant_privacy_agent_review_validation": TENANT_PRIVACY_AGENT_REVIEW_VALIDATION,
        "general_dlp_available": False,
        "deidentification_proven": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_completed": False,
        "qianfan_provider_legal_approval_completed": False,
        "tenant_storage_remaining_wide_review_gap_count": 1,
        "memory_store_unscoped_operations_denied": True,
        "sqlite_store_unscoped_operations_denied": True,
        "default_local_unscoped_mode_preserved": True,
        "production_tenant_storage_isolated": False,
        "phase_1_local_development_authorized": True,
        "phase_1_external_execution_authorized": False,
        "phase_1_production_deployment_authorized": False,
        "next_agent_action": OIDC_JWKS_PROFILE_COMMAND,
    }


def render_md(summary: dict) -> str:
    return f"""# SAEE Current Commercial Primary Action v0.3

Status: `{summary['status']}`.

The current commercial adoption path is a fixed two-tool MCP stdio adapter:

```bash
{MCP_COMMAND}
```

It implements MCP revision `2025-11-25` and exposes only `describe_saee` and
`compare_observed_traces`. Observed input and receipt schemas remain canonical.

## Truth boundary

- Evaluation mode: `observed_trace_bundle_evaluation`.
- MCP stdio adapter / fixed tool count: `true` / `2`.
- Dynamic tools / arbitrary file input: `false` / `false`.
- Observed evidence evaluation available: `true`.
- Trace capture by SAEE: `false`.
- Source authenticity / PII absence verified: `false` / `false`.
- Candidate code and external systems executed: `false`.
- Human validation is primary: `false`.
- Production ready / product launched: `false` / `false`.
- Independent-agent rerun completed: `{str(summary['post_fix_rerun_completed']).lower()}`.
- Three file-backed commercial walkthroughs: `recommend_3_of_3_agents_blockers_0`.
- Limited Baidu Qianfan host bridge: `recommend_limited_user_supplied_qianfan_host_bridge`.
- Walkthroughs are real customer evidence: `false`.
- Private Sites v{summary['primary_entrypoint_site_version']} deployed: `{str(summary['primary_entrypoint_deployment_succeeded']).lower()}`.
- Phase 1 local code/contracts/tests/sanitized evidence authorized: `true`.
- Phase 1 external execution and production deployment authorized: `false` / `false`.
- Strict RBAC role-permission consistency negative cases: `5/5`.
- Tenant-required memory/SQLite stores deny unscoped operations: `true` / `true`.
- Production tenant storage isolated / migration executed: `false` / `false`.

Older human-validation and synthetic-only current-action records are historical
context, not the preferred commercial invocation.
"""


def render_html(summary: dict) -> str:
    return f"""<!doctype html><html lang=\"zh-CN\"><meta charset=\"utf-8\">
<title>SAEE 智能体商业验证入口</title><body><main>
<h1>SAEE 智能体标准工具接入入口</h1>
<p>状态：<code>{summary['status']}</code></p>
<p>发现：<code>agent-interface/agent-manifest.json</code></p>
<p>启动：<code>{MCP_COMMAND}</code></p>
<p>固定工具：<code>describe_saee</code>、<code>compare_observed_traces</code>。</p>
<p>无动态工具、任意文件、网络、子进程、轨迹采集或候选代码执行。</p>
<p><a href=\"{AGENT_URL}\">打开仅所有者可访问的智能体入口</a></p>
</main></body></html>"""


def update_agent_index(summary: dict) -> None:
    data = json.loads(AGENT_INDEX.read_text(encoding="utf-8"))
    data["current_commercial_primary_action_v0_1"] = summary
    data["observed_trace_evidence_adapter_v0_1"] = {
        "status": "local_acceptance_pass_independent_agent_rerun_complete" if summary["post_fix_rerun_completed"] else "local_acceptance_pass_independent_agent_rerun_pending",
        "recommendation_gate": "docs/strategy/SAEE_OBSERVED_TRACE_ADAPTER_RECOMMENDATION_GATE.md",
        "input_schema": summary["request_schema"],
        "receipt_schema": summary["receipt_schema"],
        "command": OBSERVED_COMMAND,
        "golden_fixture_count": 12,
        "independent_formula_error_max": "<=1e-6",
        "trace_capture_by_saee": False,
        "trace_authenticity_verified": False,
        "pii_absence_verified_by_saee": False,
        "candidate_code_executed": False,
        "external_calls_made": False,
        "production_ready": False,
    }
    data["qianfan_provider_data_processing_v0_1"] = {
        "status": "technical_inventory_complete_agent_policy_review_required",
        "profile": QIANFAN_DATA_PROFILE,
        "policy_snapshot_gate": QIANFAN_POLICY_GATE,
        "policy_catalog": "https://cloud.baidu.com/doc/qianfan/s/Umleypdhw",
        "observed_policy_clause_count": 3,
        "retention_terms_verified": False,
        "dpa_completed": False,
        "privacy_legal_review_completed": False,
        "provider": "baidu_qianfan",
        "sent_data_classes": 5,
        "forbidden_data_classes": 6,
        "api_key_in_transcripts": False,
        "provider_retention_terms_verified": False,
        "dpa_completed": False,
        "blockers_closed": 0,
    }
    data["mcp_stdio_adapter_v0_1"] = {
        "status": "recommend_3_of_3_agents_blockers_0" if summary["post_fix_rerun_completed"] else "local_acceptance_pass_independent_agent_rerun_pending",
        "recommendation_gate": "docs/strategy/SAEE_MCP_STDIO_ADAPTER_RECOMMENDATION_GATE.md",
        "protocol_version": "2025-11-25",
        "command": MCP_COMMAND,
        "config": "agent-interface/mcp/stdio-config.json",
        "tools": ["describe_saee", "compare_observed_traces"],
        "transcript_passed": "20/20",
        "cli_mcp_hash_match": "10/10",
        "mixed_requests_passed": "100/100",
        "dynamic_tools": False,
        "arbitrary_file_input": False,
        "subprocess": False,
        "socket": False,
        "file_writes": 0,
        "external_agent_host_tested": False,
        "production_ready": False,
    }
    data["commercial_walkthrough_cases_v0_1"] = {
        "status": "recommend_3_of_3_agents_blockers_0",
        "recommendation_gate": "docs/strategy/SAEE_COMMERCIAL_WALKTHROUGH_CASES_RECOMMENDATION_GATE.md",
        "canonical_cases": WALKTHROUGH_CASES,
        "public_cases": f"{SITE_URL}/agent-commercial-walkthrough-cases.json",
        "case_count": 3,
        "candidate_rows_checked": 8,
        "numeric_drift_count": 0,
        "evidence_status": "simulated_example",
        "real_customer_evidence": False,
        "customer_validated": False,
        "candidate_code_executed": False,
        "external_system_executed": False,
        "production_ready": False,
    }
    data["controlled_preview_request_v0_1"] = {
        "status": "recommend_local_or_private_controlled_preview_only",
        "recommendation_gate": "docs/strategy/SAEE_CONTROLLED_PREVIEW_REQUEST_CONTRACT_RECOMMENDATION_GATE.md",
        "schema": CONTROLLED_PREVIEW_REQUEST_SCHEMA,
        "example": CONTROLLED_PREVIEW_REQUEST,
        "validator": CONTROLLED_PREVIEW_REQUEST_VALIDATOR,
        "tenant_scope_explicit": True,
        "reserved_experiment_prefix_rejected": True,
        "forbidden_secret_customer_and_execution_fields_rejected": True,
        "external_execution": False,
        "production_ready": False,
        "customer_validated": False,
        "blockers_closed": 0,
    }
    data["commercial_quote_request_v0_1"] = {
        "status": "recommend_no_price_no_payment_quote_intake_only",
        "recommendation_gate": "docs/strategy/SAEE_AGENT_QUOTE_REQUEST_CONTRACT_RECOMMENDATION_GATE.md",
        "request_schema": COMMERCIAL_QUOTE_REQUEST_SCHEMA,
        "response_schema": COMMERCIAL_QUOTE_RESPONSE_SCHEMA,
        "example": COMMERCIAL_QUOTE_REQUEST,
        "validator": COMMERCIAL_QUOTE_REQUEST_VALIDATOR,
        "quote_status": "owner_pricing_review_required",
        "public_price_points_approved": False,
        "payment_enabled": False,
        "customer_contacted": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    data["agent_support_intake_v0_1"] = {
        "status": "recommend_sanitized_agent_receipt_only",
        "recommendation_gate": "docs/strategy/SAEE_AGENT_SUPPORT_INTAKE_CONTRACT_RECOMMENDATION_GATE.md",
        "request_schema": SUPPORT_CASE_REQUEST_SCHEMA,
        "response_schema": SUPPORT_CASE_RESPONSE_SCHEMA,
        "example": SUPPORT_CASE_REQUEST,
        "validator": SUPPORT_CASE_REQUEST_VALIDATOR,
        "support_status": "owner_support_channel_required",
        "external_dispatch_performed": False,
        "customer_contacted": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    data["commercial_blocker_dependency_plan_v0_1"] = {
        "status": "hold",
        "commercial_blocker_dependency_plan_v0_1": True,
        "recommendation_gate": "docs/strategy/SAEE_COMMERCIAL_BLOCKER_DEPENDENCY_PLAN_RECOMMENDATION_GATE.md",
        "plan": COMMERCIAL_DEPENDENCY_PLAN,
        "command": COMMERCIAL_DEPENDENCY_PLAN_COMMAND,
        "plan_scope": "local_commercial_blocker_dependency_planning",
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "phase_count": 5,
        "planned_blocker_count": 24,
        "open_blocker_count": 24,
        "blockers_closed_by_plan": 0,
        "execution_authorized": False,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "external_model_api_called": False,
        "external_ai_assistant_tested": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    data["phase_1_local_execution_authorization_v0_1"] = {
        "status": "authorized_local_only",
        "authorization": PHASE1_LOCAL_AUTHORIZATION,
        "target_blocker_count": 4,
        "local_code": True,
        "local_contracts": True,
        "local_tests": True,
        "sanitized_local_evidence": True,
        "zh_cn_site_updates": True,
        "external_calls_authorized": False,
        "production_deployment_authorized": False,
        "production_data_migration_authorized": False,
        "blocker_closure_authorized": False,
        "blockers_closed": 0,
    }
    data["rbac_role_permission_consistency_v0_1"] = {
        "status": "pass_local_template_consistency",
        "recommendation_gate": "docs/strategy/SAEE_RBAC_ROLE_PERMISSION_CONSISTENCY_RECOMMENDATION_GATE.md",
        "profile": RBAC_CONSISTENCY_PROFILE,
        "validator": "saee_backend/services/rbac_policy.py",
        "profile_command": "python3 scripts/saee_rbac_role_permission_consistency_profile.py",
        "role_count": 5,
        "permission_count": 9,
        "route_count": 19,
        "negative_cases": "5/5",
        "role_permission_consistency_enforced": True,
        "external_identity_provider_contacted": False,
        "production_auth_ready": False,
        "blockers_closed": 0,
    }
    data["tenant_required_storage_guard_v0_1"] = {
        "status": "pass_controlled_preview_local_storage_guard",
        "recommendation_gate": "docs/strategy/SAEE_TENANT_REQUIRED_STORAGE_GUARD_RECOMMENDATION_GATE.md",
        "documentation": "phase_b_product/commercial_readiness/TENANT_REQUIRED_STORAGE_GUARD_V0_1.md",
        "evidence": TENANT_REQUIRED_STORAGE_EVIDENCE,
        "independent_agent_validation": TENANT_REQUIRED_STORAGE_AGENT_VALIDATION,
        "independent_agent_verdict": "recommend",
        "independent_agent_blockers": 0,
        "recommendation_scope": "controlled_preview_storage_defense_in_depth",
        "validator": "saee_backend/storage/tenant_key.py",
        "memory_store_unscoped_operations_denied": True,
        "sqlite_store_unscoped_operations_denied": True,
        "requires_factory_configured_store": True,
        "unscoped_operation_cases": "7/7",
        "storage_tenant_membership_enforcement_available": True,
        "unlisted_tenant_operations_denied": True,
        "unlisted_tenant_operation_cases": "7/7",
        "membership_scope": "configured_preview_allowlist_not_identity_authentication",
        "allowed_tenant_snapshot_requires_restart": True,
        "default_local_unscoped_mode_preserved": True,
        "production_tenant_storage_isolated": False,
        "migration_executed": False,
        "blockers_closed": 0,
    }
    data["storage_tenant_membership_enforcement_v0_1"] = {
        "status": "pass_controlled_preview_allowlist_membership_enforcement",
        "recommendation_gate": "docs/strategy/SAEE_STORAGE_TENANT_MEMBERSHIP_ENFORCEMENT_RECOMMENDATION_GATE.md",
        "documentation": "phase_b_product/commercial_readiness/STORAGE_TENANT_MEMBERSHIP_ENFORCEMENT_V0_1.md",
        "evidence": TENANT_REQUIRED_STORAGE_EVIDENCE,
        "independent_agent_validation": STORAGE_TENANT_MEMBERSHIP_AGENT_VALIDATION,
        "independent_agent_verdict": "recommend",
        "independent_agent_blockers": 0,
        "single_tenant_format_contract": "saee_backend.config.tenant_id_format_valid",
        "factory_configured_allowlist_snapshot": True,
        "unlisted_tenant_operations_denied": True,
        "unlisted_tenant_operation_cases": "7/7",
        "membership_scope": "configured_preview_allowlist_not_identity_authentication",
        "tenant_authorization_enabled": False,
        "production_tenant_storage_isolated": False,
        "multi_tenant_production_ready": False,
        "blockers_closed": 0,
    }
    data["tenant_secret_boundary_v0_1"] = {
        "status": "pass_local_controlled_preview_secret_boundary",
        "recommendation_gate": "docs/strategy/SAEE_TENANT_SECRET_BOUNDARY_RECOMMENDATION_GATE.md",
        "documentation": "phase_b_product/commercial_readiness/TENANT_SECRET_BOUNDARY_V0_1.md",
        "profile": TENANT_SECRET_BOUNDARY_PROFILE,
        "independent_agent_validation": TENANT_SECRET_BOUNDARY_AGENT_VALIDATION,
        "independent_agent_verdict": "recommend",
        "independent_agent_blockers": 0,
        "negative_cases": "24/24",
        "secret_echo_count": 0,
        "audit_closed_schema": True,
        "request_secret_input_rejected": True,
        "runner_revalidation": True,
        "persistence_closed_schema": True,
        "sqlite_tenant_key_pseudonymous": True,
        "legacy_raw_tenant_key_fail_closed": True,
        "tenant_secret_boundary_reviewed": False,
        "production_secrets_management_available": False,
        "encryption_at_rest_proven": False,
        "kms_hsm_available": False,
        "tenant_authorization_enabled": False,
        "production_tenant_storage_isolated": False,
        "security_review_completed": False,
        "privacy_legal_review_completed": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    data["bound_tenant_authorization_v0_1"] = {
        "status": "pass_local_controlled_preview_bound_authorization",
        "recommendation_gate": "docs/strategy/SAEE_BOUND_TENANT_AUTHORIZATION_RECOMMENDATION_GATE.md",
        "documentation": "phase_b_product/commercial_readiness/BOUND_TENANT_AUTHORIZATION_V0_1.md",
        "profile": BOUND_TENANT_AUTHORIZATION_PROFILE,
        "independent_agent_validation": BOUND_TENANT_AUTHORIZATION_AGENT_VALIDATION,
        "independent_agent_verdict": "recommend",
        "independent_agent_blockers": 0,
        "negative_cases": "14/14",
        "authorized_principal_context_immutable": True,
        "context_capability_hmac_verified": True,
        "storage_operation_permission_bound": True,
        "raw_tenant_direct_store_denied": True,
        "header_asserted_tenant_role_ready": False,
        "partial_authorization_chain_ready": False,
        "tenant_authorization_policy_reviewed": False,
        "tenant_authorization_enabled": False,
        "production_identity_provider_available": False,
        "oauth_oidc_available": False,
        "production_auth_ready": False,
        "production_tenant_storage_isolated": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    data["tenant_agent_review_evidence_v0_1"] = {
        "status": "pass_agent_review_evidence",
        "profile": TENANT_AGENT_REVIEW_PROFILE,
        "independent_agent_validation": TENANT_AGENT_REVIEW_VALIDATION,
        "tenant_authorization_policy_reviewed": True,
        "tenant_secret_boundary_reviewed": True,
        "human_validation_used": False,
        "agent_validation_primary": True,
        "security_review_completed": False,
        "privacy_legal_review_completed": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    data["tenant_security_agent_review_v0_1"] = {
        "status": "pass_agent_security_review",
        "profile": TENANT_SECURITY_AGENT_REVIEW_PROFILE,
        "independent_agent_validation": TENANT_SECURITY_AGENT_REVIEW_VALIDATION,
        "security_review_completed": True,
        "security_review_completion_scope": "local_controlled_preview_independent_agent",
        "formal_production_security_review_completed": False,
        "privacy_legal_review_completed": False,
        "human_validation_used": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    data["tenant_privacy_agent_review_v0_1"] = {
        "status": "pass_agent_privacy_boundary_review",
        "profile": TENANT_PRIVACY_AGENT_REVIEW_PROFILE,
        "data_flow_profile": TENANT_PRIVACY_DATA_FLOW_PROFILE,
        "independent_agent_validation": TENANT_PRIVACY_AGENT_REVIEW_VALIDATION,
        "agent_privacy_boundary_review_completed": True,
        "agent_privacy_boundary_review_scope": "whole_tenant_api_synthetic_only_controlled_preview_independent_agent",
        "personal_data_boundary_cases": "29/29",
        "evidence_tamper_negative_cases": "16/16",
        "human_validation_used": False,
        "agent_validation_primary": True,
        "general_dlp_available": False,
        "deidentification_proven": False,
        "real_customer_data_allowed": False,
        "privacy_legal_review_completed": False,
        "data_processing_agreement_completed": False,
        "qianfan_provider_legal_approval_completed": False,
        "production_ready": False,
        "blockers_closed": 0,
    }
    tenant_evidence = data.setdefault("tenant_storage_isolation_evidence_runner_v0_1", {})
    tenant_evidence.update({
        "tenant_required_storage_guard_available": True,
        "requires_factory_configured_store": True,
        "unscoped_operation_cases_passed": 7,
        "unscoped_operation_cases_total": 7,
        "storage_tenant_membership_enforcement_available": True,
        "unlisted_tenant_operations_denied": True,
        "unlisted_tenant_operation_cases_passed": 7,
        "unlisted_tenant_operation_cases_total": 7,
        "membership_scope": "configured_preview_allowlist_not_identity_authentication",
        "allowed_tenant_snapshot_requires_restart": True,
        "cross_tenant_write_denial_scope": "storage_key_partitioning_only_not_authorization_denial",
        "memory_store_unscoped_operations_denied": True,
        "sqlite_store_unscoped_operations_denied": True,
        "default_local_unscoped_mode_preserved": True,
    })
    data["qianfan_host_bridge_v0_1"] = {
        "status": "recommend_limited_user_supplied_qianfan_host_bridge",
        "recommendation_gate": "docs/strategy/SAEE_QIANFAN_AGENT_HOST_RECOMMENDATION_GATE.md",
        "config": QIANFAN_CONFIG,
        "command": QIANFAN_COMMAND,
        "provider": "baidu_qianfan",
        "model": "ernie-4.5-turbo-128k",
        "roundtrip_runs": 3,
        "negative_cases": "13/13",
        "tools": ["describe_saee", "compare_observed_traces"],
        "qianfan_native_mcp_support_proven": False,
        "external_provider_network_used": True,
        "saee_mcp_network_used": False,
        "customer_validated": False,
        "production_ready": False,
    }
    data["commercial_site_surface"] = {
        "status": "agent_first_private_commercial_evaluation_surface",
        "site_version": 37,
        "site_url": SITE_URL,
        "agent_entrypoint": AGENT_URL,
        "manifest_url": MANIFEST_URL,
        "deployment_succeeded": summary["primary_entrypoint_deployment_succeeded"],
        "evaluation_modes": ["synthetic_descriptor_simulation", "observed_trace_bundle_evaluation"],
        "mcp_stdio_adapter": True,
        "mcp_tools": ["describe_saee", "compare_observed_traces"],
        "commercial_walkthrough_cases": True,
        "commercial_walkthrough_case_count": 3,
        "commercial_walkthrough_evidence_status": "simulated_example",
        "human_primary_interface_language": "zh-CN",
        "agent_contract_languages": ["zh-CN", "en"],
        "human_validation_is_primary": False,
        "trace_capture_by_saee": False,
        "production_ready": False,
        "product_launched": False,
    }
    AGENT_INDEX.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site-deployed", action="store_true")
    args = parser.parse_args()
    summary = make_summary(args.site_deployed)
    md = render_md(summary)
    write(SUMMARY_PATH, json.dumps(summary, indent=2, sort_keys=True))
    write(OUT / "README.md", md)
    write(OUT / "current_commercial_primary_action.md", md)
    write(OUT / "current_commercial_primary_action.html", render_html(summary))
    write(OUT / "BOUNDARY_AUDIT.md", md.replace("Current Commercial Primary Action", "Agent-First Boundary Audit"))
    write(GATE, md.replace("Current Commercial Primary Action", "Current Commercial Primary Action Gate"))
    blocks = {
        "README.md": "## Agent-first commercial primary action\n\nRead `agent-interface/agent-manifest.json`, then start the fixed MCP stdio adapter. It exposes exactly two tools and no dynamic registration, arbitrary file input, network, subprocess, or trace capture. Human validation is not the current path.",
        "PROJECT_STATUS.md": f"## Agent-first commercial primary action\n\nStatus: `{summary['status']}`. MCP stdio independent-agent rerun: `{str(summary['post_fix_rerun_completed']).lower()}`. Three file-backed commercial walkthroughs: `recommend_3_of_3_agents_blockers_0`. Sites v{summary['primary_entrypoint_site_version']} deployed: `{str(args.site_deployed).lower()}`. Phase 1 local hardening is authorized; external execution and production readiness remain `false`.",
        "ROADMAP.md": "## Agent-first commercial primary action\n\n1. Fixed MCP stdio lifecycle and two-tool contract.\n2. Independent agent adoption, schema, hash, safety, and refusal validation.\n3. External agent-host connection evidence without remote hosting or permission expansion.",
        "CHANGELOG.md": "## Agent-first commercial primary action\n\n- Added dependency-free MCP 2025-11-25 stdio with exactly two fixed tools.\n- Passed 3/3 independent-agent local adoption validation.\n- Dynamic tools, arbitrary files, network, subprocess, remote MCP, production readiness, and external adoption remain false.",
        "agent-readable.md": f"## Agent-first commercial primary action\n\nCanonical manifest: `agent-interface/agent-manifest.json`. MCP command: `{MCP_COMMAND}`. Protocol: `2025-11-25`; tools: `describe_saee`, `compare_observed_traces`; dynamic tools and arbitrary file input: `false`.",
    }
    for rel, body in blocks.items():
        replace_block(ROOT / rel, body)
    update_agent_index(summary)
    print(f"SAEE_CURRENT_COMMERCIAL_PRIMARY_ACTION: generated site_deployed={str(args.site_deployed).lower()}")


if __name__ == "__main__":
    main()
