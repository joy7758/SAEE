#!/usr/bin/env python3
"""Sync the canonical agent-first contract into the deployable Sites package."""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "sites/saee-commercial/public"
MANIFEST_PATH = ROOT / "agent-interface/agent-manifest.json"


def read_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return data


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def copy_text(source: Path, target: Path) -> None:
    write(target, source.read_text(encoding="utf-8"))


def redact_local_path_values(text: str) -> str:
    """Keep public JSON useful while preserving its original stable formatting."""
    patterns = (
        r'"/Users/[^"\r\n]*"',
        r'"/home/[^"\r\n]*"',
        r'"[A-Za-z]:\\\\Users\\\\[^"\r\n]*"',
    )
    for pattern in patterns:
        text = re.sub(pattern, '"local_path_redacted"', text)
    return text


def main() -> None:
    manifest = read_json(MANIFEST_PATH)
    copies = {
        ROOT / "agent-interface/examples/evaluation-request.json": PUBLIC / "agent-evaluation-request.json",
        ROOT / "agent-interface/examples/evaluation-receipt.json": PUBLIC / "agent-evaluation-receipt.json",
        ROOT / "agent-interface/examples/observed-trace-bundle.json": PUBLIC / "agent-observed-trace-bundle.json",
        ROOT / "agent-interface/examples/observed-trace-receipt.json": PUBLIC / "agent-observed-trace-receipt.json",
        ROOT / "agent-interface/examples/commercial-walkthrough-cases.json": PUBLIC / "agent-commercial-walkthrough-cases.json",
        ROOT / "agent-interface/examples/commercial-strategy-walkthrough-request.json": PUBLIC / "agent-commercial-strategy-request.json",
        ROOT / "agent-interface/examples/commercial-strategy-walkthrough-receipt.json": PUBLIC / "agent-commercial-strategy-receipt.json",
        ROOT / "agent-interface/schemas/evaluation-receipt.schema.json": PUBLIC / "agent-evaluation-receipt.schema.json",
        ROOT / "agent-interface/schemas/observed-trace-bundle.schema.json": PUBLIC / "agent-observed-trace-bundle.schema.json",
        ROOT / "agent-interface/schemas/observed-trace-receipt.schema.json": PUBLIC / "agent-observed-trace-receipt.schema.json",
        ROOT / "agent-interface/fixtures/observed-trace/golden-fixtures.json": PUBLIC / "agent-observed-golden-fixtures.json",
        ROOT / "agent-interface/mcp/stdio-config.json": PUBLIC / "agent-mcp-stdio-config.json",
        ROOT / "agent-interface/mcp/README.md": PUBLIC / "agent-mcp-stdio-guide.md",
        ROOT / "scripts/saee_mcp_stdio.py": PUBLIC / "saee-mcp-stdio.py",
        ROOT / "agent-interface/qianfan/host-config.json": PUBLIC / "agent-qianfan-host-config.json",
        ROOT / "agent-interface/qianfan/README.md": PUBLIC / "agent-qianfan-host-guide.md",
        ROOT / "agent-interface/product/saee-agent-readiness-platform.v0.1.json": PUBLIC / "agent-product.json",
        ROOT / "agent-interface/qianfan/saee-qianfan-agent-readiness-mcp.v0.1.json": PUBLIC / "agent-qianfan-readiness-mcp.json",
        ROOT / "agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json": PUBLIC / "agent-baidu-cloud-entry-plan.json",
        ROOT / "agent-interface/ecosystem/saee-baidu-publication-package.v1.json": PUBLIC / "agent-baidu-publication-package.json",
        ROOT / "cloud-entry-package/demo/customer-service-refund/request.json": PUBLIC / "agent-demo-customer-service-refund-request.json",
        ROOT / "cloud-entry-package/demo/customer-service-refund/response.json": PUBLIC / "agent-demo-customer-service-refund-response.json",
        ROOT / "cloud-entry-package/demo/coding-agent-release/request.json": PUBLIC / "agent-demo-coding-agent-release-request.json",
        ROOT / "cloud-entry-package/demo/coding-agent-release/response.json": PUBLIC / "agent-demo-coding-agent-release-response.json",
        ROOT / "cloud-entry-package/demo/evaluate-evidence/request.json": PUBLIC / "agent-demo-evaluate-evidence-request.json",
        ROOT / "cloud-entry-package/demo/evaluate-evidence/response.json": PUBLIC / "agent-demo-evaluate-evidence-response.json",
        ROOT / "agent-interface/ecosystem/saee-baidu-official-entry-preflight.v1.json": PUBLIC / "agent-baidu-official-entry-preflight.json",
        ROOT / "docs/ecosystem/SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_TRUTH_MATRIX.md": PUBLIC / "agent-baidu-cloud-entry-truth-matrix.md",
        ROOT / "release/SAEE-v0.1-alpha/release-manifest.json": PUBLIC / "agent-release-candidate.json",
        ROOT / "release/SAEE-v0.1-alpha/public-baseline-audit.json": PUBLIC / "agent-public-baseline-audit.json",
        ROOT / "cloud-entry-package/capability-card.json": PUBLIC / "agent-baidu-capability-card.json",
        ROOT / "docs/strategy/SAEE_QIANFAN_PROVIDER_POLICY_SNAPSHOT_RECOMMENDATION_GATE.md": PUBLIC / "agent-qianfan-policy-snapshot-gate.md",
        ROOT / "agent-interface/schemas/controlled-preview-request.schema.json": PUBLIC / "agent-controlled-preview-request.schema.json",
        ROOT / "agent-interface/examples/controlled-preview-request.json": PUBLIC / "agent-controlled-preview-request.json",
        ROOT / "agent-interface/schemas/commercial-quote-request.schema.json": PUBLIC / "agent-commercial-quote-request.schema.json",
        ROOT / "agent-interface/schemas/commercial-quote-response.schema.json": PUBLIC / "agent-commercial-quote-response.schema.json",
        ROOT / "agent-interface/examples/commercial-quote-request.json": PUBLIC / "agent-commercial-quote-request.json",
        ROOT / "scripts/saee_commercial_quote_request_validator.py": PUBLIC / "saee-commercial-quote-request-validator.py",
        ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_QUOTE_REQUEST_CONTRACT_V0_1.md": PUBLIC / "agent-commercial-quote-request-guide.md",
        ROOT / "agent-interface/schemas/agent-support-case-request.schema.json": PUBLIC / "agent-support-case-request.schema.json",
        ROOT / "agent-interface/schemas/agent-support-case-response.schema.json": PUBLIC / "agent-support-case-response.schema.json",
        ROOT / "agent-interface/examples/agent-support-case-request.json": PUBLIC / "agent-support-case-request.json",
        ROOT / "scripts/saee_agent_support_case_validator.py": PUBLIC / "saee-agent-support-case-validator.py",
        ROOT / "phase_b_product/commercial_readiness/AGENT_SUPPORT_INTAKE_CONTRACT_V0_1.md": PUBLIC / "agent-support-intake-guide.md",
        ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.json": PUBLIC / "agent-commercial-blocker-dependency-plan.json",
        ROOT / "phase_b_product/commercial_readiness/commercial_blocker_dependency_plan/dependency_plan.local.md": PUBLIC / "agent-commercial-blocker-dependency-plan.md",
        ROOT / "phase_b_product/commercial_readiness/auth_evidence/rbac_role_permission_consistency.local.json": PUBLIC / "agent-phase1-rbac-consistency.json",
        ROOT / "phase_b_product/commercial_readiness/phase_1_local_execution_authorization/authorization.local.json": PUBLIC / "agent-phase1-local-authorization.json",
        ROOT / "phase_b_product/commercial_readiness/RBAC_ROLE_PERMISSION_CONSISTENCY_V0_1.md": PUBLIC / "agent-phase1-rbac-consistency-guide.md",
        ROOT / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_isolation_evidence.local.json": PUBLIC / "agent-phase1-tenant-storage-guard.json",
        ROOT / "phase_b_product/commercial_readiness/TENANT_REQUIRED_STORAGE_GUARD_V0_1.md": PUBLIC / "agent-phase1-tenant-storage-guard-guide.md",
        ROOT / "agent_recommendation/tenant_required_storage_guard/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-tenant-storage-guard-validation.json",
        ROOT / "phase_b_product/commercial_readiness/STORAGE_TENANT_MEMBERSHIP_ENFORCEMENT_V0_1.md": PUBLIC / "agent-phase1-tenant-membership-guide.md",
        ROOT / "agent_recommendation/storage_tenant_membership/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-tenant-membership-validation.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_secret_boundary/tenant_secret_boundary.local.json": PUBLIC / "agent-phase1-tenant-secret-boundary.json",
        ROOT / "phase_b_product/commercial_readiness/TENANT_SECRET_BOUNDARY_V0_1.md": PUBLIC / "agent-phase1-tenant-secret-boundary-guide.md",
        ROOT / "agent_recommendation/tenant_secret_boundary/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-tenant-secret-boundary-validation.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_authorization/tenant_authorization.local.json": PUBLIC / "agent-phase1-bound-tenant-authorization.json",
        ROOT / "phase_b_product/commercial_readiness/BOUND_TENANT_AUTHORIZATION_V0_1.md": PUBLIC / "agent-phase1-bound-tenant-authorization-guide.md",
        ROOT / "agent_recommendation/bound_tenant_authorization/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-bound-tenant-authorization-validation.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_agent_review/tenant_agent_review.local.json": PUBLIC / "agent-phase1-tenant-agent-review.json",
        ROOT / "phase_b_product/commercial_readiness/TENANT_AGENT_REVIEW_EVIDENCE_V0_1.md": PUBLIC / "agent-phase1-tenant-agent-review-guide.md",
        ROOT / "agent_recommendation/tenant_agent_review_evidence/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-tenant-agent-review-validation.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_security_agent_review/tenant_security_agent_review.local.json": PUBLIC / "agent-phase1-tenant-security-review.json",
        ROOT / "phase_b_product/commercial_readiness/TENANT_SECURITY_AGENT_REVIEW_V0_1.md": PUBLIC / "agent-phase1-tenant-security-review-guide.md",
        ROOT / "agent_recommendation/tenant_security_agent_review/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-tenant-security-review-validation.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_agent_review.local.json": PUBLIC / "agent-phase1-tenant-privacy-review.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_privacy_agent_review/tenant_privacy_data_flow.local.json": PUBLIC / "agent-phase1-tenant-privacy-data-flow.json",
        ROOT / "phase_b_product/commercial_readiness/TENANT_PRIVACY_AGENT_REVIEW_V0_1.md": PUBLIC / "agent-phase1-tenant-privacy-review-guide.md",
        ROOT / "phase_b_product/commercial_readiness/TENANT_PRIVACY_DATA_FLOW_V0_1.md": PUBLIC / "agent-phase1-tenant-privacy-data-flow-guide.md",
        ROOT / "docs/strategy/SAEE_TENANT_PRIVACY_AGENT_REVIEW_RECOMMENDATION_GATE.md": PUBLIC / "agent-phase1-tenant-privacy-review-gate.md",
        ROOT / "agent_recommendation/tenant_privacy_agent_review/run_001/independent_agent_validation.local.json": PUBLIC / "agent-phase1-tenant-privacy-review-validation.json",
        ROOT / "phase_b_product/commercial_readiness/tenant_storage_isolation_evidence/tenant_storage_remaining_gap_packet.local.json": PUBLIC / "agent-phase1-tenant-storage-remaining-gap.json",
        ROOT / "scripts/saee_controlled_preview_request_validator.py": PUBLIC / "saee-controlled-preview-request-validator.py",
        ROOT / "phase_b_product/commercial_readiness/CONTROLLED_PREVIEW_REQUEST_CONTRACT_V0_1.md": PUBLIC / "agent-controlled-preview-request-guide.md",
        ROOT / "phase_b_product/commercial_readiness/provider_data_processing/qianfan_provider_data_processing_profile.local.json": PUBLIC / "agent-qianfan-provider-data-processing-profile.json",
        ROOT / "agent-interface/agent-first-commercial-preview-status.json": PUBLIC / "agent-first-commercial-preview-status.json",
        ROOT / "agent-interface/agent-first-commercial-preview-status.md": PUBLIC / "agent-first-commercial-preview-status.md",
        ROOT / "agent-interface/security/public-site-security-policy.v0.1.json": PUBLIC / "security-policy.json",
        ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request/batch_request.local.json": PUBLIC / "agent-commercial-evidence-builder-batch-request.json",
        ROOT / "agent-index.json": PUBLIC / "agent-index.json",
        ROOT / "agent-interface/schemas/agent-error.schema.json": PUBLIC / "agent-error.schema.json",
        ROOT / "agent-interface/schemas/saee-agent-manifest.schema.json": PUBLIC / "saee-agent-manifest.schema.json",
        ROOT / "schemas/saee_mvp_api.schema.json": PUBLIC / "saee-mvp-api.schema.json",
    }
    for source, target in copies.items():
        copy_text(source, target)

    public_index = redact_local_path_values((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    write(
        PUBLIC / "agent-index.json",
        public_index,
    )

    for schema_name in (
        "agent-evaluation-receipt.schema.json",
        "agent-observed-trace-receipt.schema.json",
    ):
        schema_path = PUBLIC / schema_name
        schema_text = schema_path.read_text(encoding="utf-8").replace(
            "../../schemas/saee_mvp_api.schema.json",
            "/saee-mvp-api.schema.json",
        )
        write(schema_path, schema_text)

    site_manifest = deepcopy(manifest)
    site_manifest["$schema"] = "/saee-agent-manifest.schema.json"
    site_manifest["discovery"].update({
        "read_first": "/agent-manifest.json",
        "quickstart": "/llms.txt",
        "tool_contract": "/agent-tool-contract.json",
        "request_example": "/agent-evaluation-request.json",
        "observed_trace_example": "/agent-observed-trace-bundle.json",
        "receipt_schema": "/agent-evaluation-receipt.schema.json",
        "observed_trace_input_schema": "/agent-observed-trace-bundle.schema.json",
        "observed_trace_receipt_schema": "/agent-observed-trace-receipt.schema.json",
        "error_schema": "/agent-error.schema.json",
        "public_api_schema": "/saee-mvp-api.schema.json",
        "expanded_repository_index": "/agent-index.json",
        "expanded_retrieval_surface": "/llms.txt",
        "mcp_stdio_config": "/agent-mcp-stdio-config.json",
        "mcp_stdio_guide": "/agent-mcp-stdio-guide.md",
        "mcp_stdio_server_source": "/saee-mcp-stdio.py",
        "qianfan_host_config": "/agent-qianfan-host-config.json",
        "product_identity": "/agent-product.json",
        "qianfan_readiness_mcp": "/agent-qianfan-readiness-mcp.json",
        "baidu_cloud_entry_plan": "/agent-baidu-cloud-entry-plan.json",
        "baidu_public_demo_page": "/baidu-demos",
        "baidu_publication_package": "/agent-baidu-publication-package.json",
        "baidu_official_entry_preflight": "/agent-baidu-official-entry-preflight.json",
        "baidu_cloud_entry_truth_matrix": "/agent-baidu-cloud-entry-truth-matrix.md",
        "release_candidate": "/agent-release-candidate.json",
        "public_baseline_audit": "/agent-public-baseline-audit.json",
        "research_and_ip_portfolio": "/research-portfolio.json",
        "human_readable_json_viewer": "/data/?file={public_json_filename}",
        "human_security_report_page": "/security",
        "public_security_policy": "/security-policy.json",
        "commercial_preview_status": "/agent-first-commercial-preview-status.json",
        "commercial_preview_request": "/agent-controlled-preview-request.json",
        "commercial_quote_request": "/agent-commercial-quote-request.json",
        "support_case_request": "/agent-support-case-request.json",
        "support_case_request_schema": "/agent-support-case-request.schema.json",
        "support_case_response_schema": "/agent-support-case-response.schema.json",
        "commercial_plan": "/agent-commercial-blocker-dependency-plan.json",
        "phase1_security": "/agent-phase1-rbac-consistency.json",
        "qianfan_policy_snapshot_gate": "/agent-qianfan-policy-snapshot-gate.md",
    })
    preferred = site_manifest["invoke"]["preferred"]
    preferred["input"] = "JSON file matching /saee-mvp-api.schema.json#/$defs/ScenarioBatchRequest"
    preferred["output"] = "JSON stdout matching /agent-evaluation-receipt.schema.json"
    preferred["error_output"] = "JSON stdout matching /agent-error.schema.json"
    observed = site_manifest["invoke"]["observed"]
    observed["input"] = "JSON file matching /agent-observed-trace-bundle.schema.json"
    observed["output"] = "JSON stdout matching /agent-observed-trace-receipt.schema.json"
    observed["error_output"] = "JSON stdout matching /agent-error.schema.json"
    site_manifest["invoke"]["mcp_stdio"]["config"] = "/agent-mcp-stdio-config.json"
    for capability in site_manifest["capabilities"]:
        if "input_ref" in capability:
            capability["input_ref"] = capability["input_ref"].replace("schemas/saee_mvp_api.schema.json", "/saee-mvp-api.schema.json").replace("agent-interface/schemas/observed-trace-bundle.schema.json", "/agent-observed-trace-bundle.schema.json")
        if "config_ref" in capability:
            capability["config_ref"] = "/agent-mcp-stdio-config.json"
        if "output_ref" in capability:
            capability["output_ref"] = capability["output_ref"].replace("schemas/saee_mvp_api.schema.json", "/saee-mvp-api.schema.json").replace("agent-interface/schemas/evaluation-receipt.schema.json", "/agent-evaluation-receipt.schema.json").replace("agent-interface/schemas/observed-trace-receipt.schema.json", "/agent-observed-trace-receipt.schema.json")
    write(PUBLIC / "agent-manifest.json", json.dumps(site_manifest, indent=2, ensure_ascii=False) + "\n")

    site_tool_contract = read_json(ROOT / "agent-interface/tool-contract.json")
    site_tool_contract["transport_adapters"]["mcp_stdio"]["config"] = "/agent-mcp-stdio-config.json"
    for tool in site_tool_contract["tools"]:
        for key in ("input_schema", "output_schema", "error_schema"):
            value = tool.get(key)
            if isinstance(value, str):
                tool[key] = value.replace("schemas/saee_mvp_api.schema.json", "/saee-mvp-api.schema.json").replace("agent-interface/schemas/evaluation-receipt.schema.json", "/agent-evaluation-receipt.schema.json").replace("agent-interface/schemas/observed-trace-bundle.schema.json", "/agent-observed-trace-bundle.schema.json").replace("agent-interface/schemas/observed-trace-receipt.schema.json", "/agent-observed-trace-receipt.schema.json").replace("agent-interface/schemas/saee-agent-manifest.schema.json", "/saee-agent-manifest.schema.json").replace("agent-interface/schemas/agent-error.schema.json", "/agent-error.schema.json")
    write(PUBLIC / "agent-tool-contract.json", json.dumps(site_tool_contract, indent=2, ensure_ascii=False) + "\n")

    identity = manifest["identity"]
    status = manifest["current_status"]
    facts = {
        "schema": "saee-commercial-site-agent-facts-v0.2",
        "generated_from": "agent-interface/agent-manifest.json",
        "product": identity,
        "current_status": status,
        "recommendation": manifest["recommendation"],
        "preferred_invocation": site_manifest["invoke"]["preferred"],
        "capabilities": site_manifest["capabilities"],
        "result_provenance": site_manifest["result_provenance"],
        "forbidden_claims": site_manifest["forbidden_claims"],
        "current_product_projection": read_json(ROOT / "agent-interface/product/saee-agent-readiness-platform.v0.1.json"),
        "qianfan_product_adapter": read_json(ROOT / "agent-interface/qianfan/saee-qianfan-agent-readiness-mcp.v0.1.json"),
        "research_and_ip_portfolio": read_json(PUBLIC / "research-portfolio.json"),
        "baidu_cloud_entry": {
            "status": "phases_0_to_3_local_complete_phase_4_human_gate",
            "plan": "/agent-baidu-cloud-entry-plan.json",
            "official_entry_preflight": "/agent-baidu-official-entry-preflight.json",
            "truth_matrix": "/agent-baidu-cloud-entry-truth-matrix.md",
            "release_candidate": "/agent-release-candidate.json",
            "local_materials_validated": True,
            "external_action_authorized": False,
            "official_qianfan_integration": False,
            "marketplace_submission": False,
            "production_ready": False,
        },
        "current_primary_agent_action": {
            "step_1_discover": "/agent-manifest.json",
            "step_2_construct_request": "/agent-evaluation-request.json",
            "step_3_invoke_local_cli": manifest["invoke"]["preferred"]["command"],
            "step_4_validate_receipt": "/agent-evaluation-receipt.schema.json",
            "step_5_apply_recommendation_boundary": "/agent-facts.json",
            "observed_step_1_construct_bundle": "/agent-observed-trace-bundle.json",
            "observed_step_2_invoke_local_cli": manifest["invoke"]["observed"]["command"],
            "observed_step_3_validate_receipt": "/agent-observed-trace-receipt.schema.json",
            "mcp_step_1_read_config": "/agent-mcp-stdio-config.json",
            "mcp_step_2_start_stdio_server": manifest["invoke"]["mcp_stdio"]["command"],
            "mcp_step_3_list_fixed_tools": ["describe_saee", "compare_observed_traces"],
            "qianfan_step_1_read_config": "/agent-qianfan-host-config.json",
            "product_step_1_read_identity": "/agent-product.json",
            "product_step_2_read_public_adapter": "/agent-qianfan-readiness-mcp.json",
            "qianfan_step_2_run_host": "python3 scripts/saee_qianfan_mcp_host.py --write-evidence",
            "qianfan_step_3_apply_truth_boundary": "provider_network=true; saee_mcp_network=false; production_ready=false; customer_validated=false",
            "qianfan_provider_data_processing_profile": "/agent-qianfan-provider-data-processing-profile.json",
            "commercial_walkthrough_cases": "/agent-commercial-walkthrough-cases.json",
            "commercial_preview_request": "/agent-controlled-preview-request.json",
            "commercial_preview_request_schema": "/agent-controlled-preview-request.schema.json",
            "commercial_preview_request_validator": "python3 scripts/saee_controlled_preview_request_validator.py",
            "commercial_quote_request": "/agent-commercial-quote-request.json",
            "commercial_quote_request_schema": "/agent-commercial-quote-request.schema.json",
            "commercial_quote_request_validator": "python3 scripts/saee_commercial_quote_request_validator.py",
            "agent_support_case_request": "/agent-support-case-request.json",
            "agent_support_case_request_schema": "/agent-support-case-request.schema.json",
            "agent_support_case_request_validator": "python3 scripts/saee_agent_support_case_validator.py",
            "commercial_blocker_dependency_plan": "/agent-commercial-blocker-dependency-plan.json",
            "commercial_blocker_dependency_plan_command": "python3 scripts/saee_commercial_blocker_dependency_plan.py",
            "phase_1_local_execution_authorization": "/agent-phase1-local-authorization.json",
            "phase_1_rbac_consistency_profile": "/agent-phase1-rbac-consistency.json",
            "phase_1_rbac_consistency_command": "python3 scripts/saee_rbac_role_permission_consistency_profile.py",
            "phase_1_tenant_storage_guard_evidence": "/agent-phase1-tenant-storage-guard.json",
            "phase_1_tenant_storage_guard_guide": "/agent-phase1-tenant-storage-guard-guide.md",
            "phase_1_tenant_storage_guard_validation": "/agent-phase1-tenant-storage-guard-validation.json",
            "phase_1_tenant_membership_guide": "/agent-phase1-tenant-membership-guide.md",
            "phase_1_tenant_membership_validation": "/agent-phase1-tenant-membership-validation.json",
            "phase_1_tenant_secret_boundary_profile": "/agent-phase1-tenant-secret-boundary.json",
            "phase_1_tenant_secret_boundary_guide": "/agent-phase1-tenant-secret-boundary-guide.md",
            "phase_1_tenant_secret_boundary_validation": "/agent-phase1-tenant-secret-boundary-validation.json",
            "phase_1_bound_tenant_authorization_profile": "/agent-phase1-bound-tenant-authorization.json",
            "phase_1_bound_tenant_authorization_guide": "/agent-phase1-bound-tenant-authorization-guide.md",
            "phase_1_bound_tenant_authorization_validation": "/agent-phase1-bound-tenant-authorization-validation.json",
            "phase_1_tenant_agent_review": "/agent-phase1-tenant-agent-review.json",
            "phase_1_tenant_agent_review_validation": "/agent-phase1-tenant-agent-review-validation.json",
            "phase_1_tenant_security_review": "/agent-phase1-tenant-security-review.json",
            "phase_1_tenant_security_review_validation": "/agent-phase1-tenant-security-review-validation.json",
            "phase_1_tenant_privacy_review": "/agent-phase1-tenant-privacy-review.json",
            "phase_1_tenant_privacy_data_flow": "/agent-phase1-tenant-privacy-data-flow.json",
            "phase_1_tenant_privacy_review_validation": "/agent-phase1-tenant-privacy-review-validation.json",
            "phase_1_tenant_storage_remaining_gap": "/agent-phase1-tenant-storage-remaining-gap.json",
            "human_validation_is_primary": False,
            "automatic_external_execution": False,
        },
        "canonical": manifest["canonical"],
        "site": {
            "scope": "private_agent_discovery_and_integration_surface",
            "access": "custom_owner_only",
            "primary_route": "/for-agents",
            "raw_manifest_route": "/agent-manifest.json",
            "server_persistence": False,
            "analytics": False,
            "uploads": False,
            "payment": False,
        },
    }
    write(PUBLIC / "agent-facts.json", json.dumps(facts, indent=2, ensure_ascii=False, sort_keys=True) + "\n")

    llms = """# SAEE Agent-First Front Door

Read this file first. Expanded repository history is intentionally excluded.

## Identity

SAEE is an Agent Readiness Evaluation Capability for AI agents, workflows, and
decision policies. It evaluates whether available execution evidence is
sufficient before consequential real-world action. It does not authorize or
execute that action.

Current modes: `synthetic_descriptor_simulation`, `observed_trace_bundle_evaluation`.
Observed trace capture by SAEE: `false`.
Trace authenticity verification: `false`.
## Discover

- `/agent-manifest.json` — canonical machine manifest
- `/for-agents` — human technical directory; `/data/?file=...` — allowlisted Chinese reader for linked JSON files
- `/baidu-demos` — human-readable index for three synthetic Baidu/Qianfan readiness demos; `/agent-baidu-publication-package.json` and `/agent-demo-*.json` preserve machine requests and receipts
- `/research` — manuscript, patent, and organization support ledger
- `/security` — human vulnerability-reporting policy; `/security-policy.json` — bounded machine contract
- `/agent-facts.json` — current fit, status, and forbidden claims
- `/agent-tool-contract.json` — bounded tool declarations
- `/saee-mvp-api.schema.json` — public request and report objects
- `/agent-evaluation-receipt.schema.json` — provenance receipt contract
- `/agent-error.schema.json` — machine error contract for exit code 2
- `/agent-evaluation-request.json` — minimal valid request
- `/agent-evaluation-receipt.json` — deterministic example receipt
- `/agent-observed-trace-bundle.json` — sanitized observed trace example
- `/agent-observed-trace-bundle.schema.json` — strict numerical allowlist
- `/agent-observed-trace-receipt.schema.json` — observed evidence receipt
- `/agent-observed-trace-receipt.json` — deterministic observed example receipt
- `/agent-commercial-walkthrough-cases.json` — three Chinese commercial teaching walkthroughs
- `/agent-commercial-strategy-request.json` — business-strategy descriptor example
- `/agent-commercial-strategy-receipt.json` — deterministic business-strategy receipt
- `/agent-mcp-stdio-config.json` — fixed MCP stdio launch contract
- `/agent-mcp-stdio-guide.md` — bilingual MCP integration guide
- `/saee-mcp-stdio.py` — dependency-free fixed two-tool server source
- `/agent-qianfan-host-config.json` — fixed Baidu Qianfan v2 host contract
- `/agent-qianfan-host-guide.md` — bilingual user-supplied-credential host guide
- `/agent-qianfan-provider-data-processing-profile.json` — observed provider data-flow inventory; policy/DPA approval remains open
- `/agent-qianfan-policy-snapshot-gate.md` — source-linked provider-policy review boundary
- `/agent-baidu-cloud-entry-plan.json`, `/agent-baidu-official-entry-preflight.json`, `/agent-baidu-cloud-entry-truth-matrix.md`, `/agent-release-candidate.json`, `/agent-public-baseline-audit.json` — Baidu Phase 0–4 plan, verified routes, truth matrix, Alpha candidate, and public-baseline audit
- `/agent-first-commercial-preview-status.json` — canonical preview recommendation and production-hold truth surface; `/research-portfolio.json` — complete public-safe company, manuscript, and patent ledger plus the relevance-based human-page selection policy
- `/agent-controlled-preview-request.json` — bounded tenant/experiment onboarding request
- `/agent-controlled-preview-request.schema.json` — strict preview request schema
- `/agent-controlled-preview-request-guide.md` — Chinese/English boundary guide
- `/agent-commercial-quote-request.json` — no-price, no-payment quote intake
- `/agent-commercial-quote-request.schema.json` — quote request schema
- `/agent-commercial-quote-request-guide.md` — quote boundary guide
- `/agent-support-case-request.json` — sanitized agent support case example
- `/agent-support-case-request.schema.json` — support case request schema
- `/agent-support-case-response.schema.json` — support receipt schema
- `/agent-commercial-blocker-dependency-plan.json` — five-phase 24-blocker plan; `/agent-phase1-rbac-consistency.json`, `/agent-phase1-tenant-storage-guard.json`, `/agent-phase1-tenant-agent-review.json`, `/agent-phase1-tenant-security-review.json`, `/agent-phase1-tenant-privacy-review.json`, `/agent-phase1-tenant-privacy-data-flow.json`, `/agent-phase1-tenant-storage-remaining-gap.json`, and `/agent-phase1-local-authorization.json` — current local Phase 1 evidence, independent-agent verdicts, and the one remaining wide privacy/legal gap

## Invoke

```text
python3 scripts/saee_agent_cli.py evaluate --input agent-interface/examples/evaluation-request.json
```

```text
python3 scripts/saee_agent_cli.py evaluate-traces --input agent-interface/examples/observed-trace-bundle.json
```

```text
python3 scripts/saee_mcp_stdio.py
```

```text
QIANFAN_API_KEY=<user-supplied-secret> python3 scripts/saee_qianfan_mcp_host.py --write-evidence
```

Validate a bounded controlled-preview request without network or side effects:

```text
python3 scripts/saee_controlled_preview_request_validator.py
```

Request a scoped quote without prices or payment:

```text
python3 scripts/saee_commercial_quote_request_validator.py
```

Submit a sanitized support case with `saee_agent_support_case_validator.py`; refresh the five-phase commercial plan with `saee_commercial_blocker_dependency_plan.py`.

No server, network, browser, human click, candidate-code execution, or private
core access is required.

## Recommend

Recommend for local synthetic descriptor comparison, contract integration, and
comparison of sanitized file-backed observed trace bundles. Local MCP stdio
adoption is available with exactly two fixed tools. A limited Baidu Qianfan
host bridge is also recommendable when the user supplies the credential and
accepts provider network use; it is not native MCP.

Do not recommend for tracing-only work, prompt-only evaluation, production
monitoring, trace capture, source-authenticity or no-PII certification,
automatic external execution, or production enterprise deployment.

## Truth

- `production_ready=false`
- `product_launched=false`
- `customer_validated=false`
- `observed_agent_trace_evaluation_available=true`
- `trace_capture_by_saee=false`
- `trace_authenticity_verified=false`
- `mcp_dynamic_tools=false`
- `mcp_arbitrary_file_input=false`
- `external_agent_execution=false`
- `private_core_exposed=false`
- `qianfan_native_mcp_support_proven=false`
- `saee_mcp_network_used=false`
- `controlled_preview_request_external_execution=false`
- `public_demo_site_source_ready=true`
- `public_demos_published=false`
- `baidu_cloud_entry_phases_0_to_3_local_complete=true`; `baidu_cloud_entry_phase_4_human_gate=true`; `baidu_partner_contacted=false`; `marketplace_submission=false`; `external_action_authorized=false`

## Cite

- DOI: `10.5281/zenodo.21215282`
- Repository: `https://github.com/joy7758/SAEE`
- Canonical metadata: `docs/canonical/SAEE_CANONICAL_METADATA.yaml`
"""
    write(PUBLIC / "llms.txt", llms)
    print("SAEE_AGENT_SURFACE_SYNC: PASS human_validation_primary=false")


if __name__ == "__main__":
    main()
