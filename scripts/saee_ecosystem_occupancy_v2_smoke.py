#!/usr/bin/env python3
"""Acceptance checks for the local SAEE ecosystem occupancy v2 package."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_TOOLS = ["saee.evaluate_agent_run", "saee.evaluate_evidence"]
INTERNAL_TOOLS = {"rehearse_agent", "describe_saee", "compare_observed_traces"}


def load(path: str) -> dict:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"SAEE_ECOSYSTEM_OCCUPANCY_V2_SMOKE: FAIL non-object {path}")
    return value


def text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_ECOSYSTEM_OCCUPANCY_V2_SMOKE: FAIL " + message)


def command_ok(args: list[str], cwd: Path = ROOT) -> bool:
    return subprocess.run(args, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def digest(path: str) -> str:
    return hashlib.sha256((ROOT / path).read_bytes()).hexdigest()


def main() -> None:
    readme = text("README.md")
    identity = load("agent-interface/product/saee-agent-readiness-capability.v2.json")
    card = load("saee-capability-card.json")
    package = load("agent-interface/ecosystem/saee-ecosystem-capability-package.v2.json")
    plan = load("agent-interface/ecosystem/saee-ecosystem-occupancy-execution-plan.v2.json")
    index = load("agent-index.json")
    multi_cloud = load("agent-interface/ecosystem/saee-multi-cloud-partner-entry-matrix.v1.json")
    qoder_response = load("examples/qoder-saee-readiness-demo/response.json")
    qoder_receipt = load("agent-interface/ecosystem/saee-qoder-global-partner-application-submission-receipt.v1.json")
    qoder_email = load("agent-interface/ecosystem/saee-qoder-technical-conversation-request-email-receipt.v1.json")
    alibaba_activation = load("agent-interface/ecosystem/saee-alibaba-product-ecosystem-partner-activation-receipt.v1.json")
    alibaba_ticket = load("agent-interface/ecosystem/saee-alibaba-qoder-technical-consultation-ticket-receipt.v1.json")
    alibaba_qoder_support = load("agent-interface/ecosystem/saee-alibaba-qoder-official-support-ticket-submission-receipt.v1.json")
    baidu_email = load("agent-interface/ecosystem/saee-baidu-qianfan-technical-conversation-request-email-receipt.v1.json")
    developer_intake = load("agent-interface/ecosystem/saee-external-developer-test-intake.template.v1.json")
    conversation_brief = load("agent-interface/ecosystem/saee-cloud-technical-conversation-brief.v1.json")
    pdf_manifest = load("output/pdf/SAEE_Agent_Readiness_Capability_Technical_Solution_v2.0.manifest.json")
    video_manifest = load("output/video/SAEE_Ecosystem_Capability_Demo_v2.0.manifest.json")
    gate = text("docs/strategy/SAEE_ECOSYSTEM_OCCUPANCY_V2_RECOMMENDATION_GATE.md")
    solution = text("docs/ecosystem/SAEE_AGENT_READINESS_CAPABILITY_TECHNICAL_SOLUTION_V2.md")
    llms = text("llms.txt")
    openapi = text(plan["technical_assets"]["openapi"])

    require(readme.startswith("# SAEE Agent Readiness Capability\n"), "README heading")
    exact_sentence = "SAEE is an Agent Readiness Infrastructure that evaluates whether AI agents have sufficient execution evidence before real-world deployment."
    require(exact_sentence in readme and identity["one_sentence"] == exact_sentence, "frozen first sentence")
    require(identity["name"] == "SAEE Agent Readiness Capability" and identity["name_zh"] == "SAEE 智能体就绪评估能力", "identity")
    require(identity["public_operations"] == PUBLIC_TOOLS, "identity tool set")
    require(set(identity["internal_operations"]) == INTERNAL_TOOLS, "internal operation set")
    require(card["name"] == "SAEE Agent Readiness Evaluation", "card name")
    require([item["name"] for item in card["operations"]] == PUBLIC_TOOLS, "card operations")
    require(package["public_operations"] == PUBLIC_TOOLS, "package operations")

    adapter_dirs = {path.name for path in (ROOT / "adapters").iterdir() if path.is_dir()}
    require(adapter_dirs == {"qoder", "qianfan", "langchain", "crewai", "claude-code"}, "adapter branches")
    require(load(".mcp.json") == load("adapters/qoder/qoder-project.mcp.json"), "Qoder root config drift")
    require(load(".mcp.json") == load("adapters/claude-code/claude-project.mcp.json"), "Claude root config drift")
    require(command_ok(["python3", "scripts/saee_qoder_adapter_smoke.py"]), "Qoder local compatibility")
    require(command_ok(["python3", "scripts/saee_qianfan_readiness_mcp_smoke.py"]), "Qianfan adapter")
    require(command_ok(["python3", "scripts/saee_qianfan_readiness_live_receipt_smoke.py"]), "Qianfan provider receipts")
    require(command_ok(["python3", "scripts/saee_cloud_entry_package_smoke.py"]), "OpenAPI/package stability")
    require(re.findall(r"^\s*operationId:\s*(\S+)\s*$", openapi, flags=re.MULTILINE) == PUBLIC_TOOLS, "OpenAPI two-operation surface")

    require(qoder_response["readiness"] == "replan" and qoder_response["recommendation"] == "REPLAN", "Qoder demo result")
    require(qoder_response["missing_evidence"] == ["ROLLBACK_PLAN", "HUMAN_APPROVAL"], "Qoder demo missing evidence")
    require(qoder_response["truth_boundary"]["deployment_authorized"] is False, "Qoder demo authorization")
    require(len(re.findall(r"^## Page \d+ -", solution, flags=re.MULTILINE)) == 10, "ten-page source")
    require(pdf_manifest["page_count"] == 10, "PDF page count")
    require(pdf_manifest["sha256"] == digest(pdf_manifest["artifact"]), "PDF digest")
    require(command_ok(["pdfinfo", pdf_manifest["artifact"]]), "PDF readable")
    require(video_manifest["scene_count"] == 9, "video scenes")
    require(179.5 <= video_manifest["duration_seconds"] <= 180.5, "video duration")
    require(video_manifest["sha256"] == digest(video_manifest["video"]), "video digest")
    require(command_ok(["ffprobe", "-v", "error", video_manifest["video"]]), "video readable")
    require(text(video_manifest["subtitles"]).count(" --> ") == 9, "video subtitles")

    require(plan["priority_order"] == ["QODER", "BAIDU_QIANFAN", "LANGCHAIN", "CREWAI", "CLAUDE_CODE"], "priority order")
    require(plan["stopped_work"] == ["NEW_PROTOCOL", "NEW_RUNTIME", "NEW_GOVERNANCE_MODULE", "ADDITIONAL_ARCHITECTURE_PAPER"], "stopped work")
    require(plan["kpis"]["ecosystem"]["cloud_vendor_technical_conversation_completed"] == 0, "technical conversation truth")
    require(plan["kpis"]["ecosystem"]["consented_external_developer_test_completed"] == 0, "developer test truth")
    require(plan["kpis"]["commercial"]["design_partner_completed"] == 0, "Design Partner truth")
    require(plan["external_state"]["alibaba_product_partner_application"] == "approved_contract_signed_partner_workbench_active", "Alibaba state")
    alibaba = next(item for item in multi_cloud["providers"] if item["provider"] == "Alibaba Cloud")
    require(alibaba["current_state"] == "product_ecosystem_partner_membership_active_ai_partner_basic_lv1", "Alibaba receipt matrix")
    require(plan["external_state"]["alibaba_application_is_qoder_technical_conversation"] is False, "Alibaba/Qoder boundary")
    require(plan["external_state"]["qoder_global_partner_application"] == "submitted_waiting_review", "Qoder application state")
    require(plan["external_state"]["qoder_application_form_id"] == qoder_receipt["application_form_id"], "Qoder receipt linkage")
    require(qoder_receipt["truth_boundary"]["application_submitted"] is True, "Qoder submission receipt")
    require(qoder_receipt["truth_boundary"]["technical_conversation_completed"] is False, "Qoder conversation boundary")
    require(qoder_receipt["repository_privacy"]["raw_phone_stored"] is False, "Qoder receipt privacy")
    require(qoder_email["truth_boundary"]["outbound_request_sent"] is True, "Qoder email request")
    require(qoder_email["truth_boundary"]["technical_conversation_completed"] is False, "Qoder email conversation boundary")
    require(alibaba_activation["truth_boundary"]["product_ecosystem_partner_membership_active"] is True, "Alibaba partner activation")
    require(alibaba_activation["truth_boundary"]["approved_cloud_marketplace_route_available"] is True, "Alibaba marketplace route")
    require(alibaba_activation["truth_boundary"]["marketplace_product_submission"] is False, "Alibaba marketplace submission boundary")
    require(alibaba_ticket["ticket_id"] == "4220915" and alibaba_ticket["truth_boundary"]["technical_conversation_request_submitted"] is True, "Alibaba Qoder ticket")
    require(alibaba_ticket["observed_status"] == "已解决" and alibaba_ticket["truth_boundary"]["response_provided_official_qoder_support_route"] is True, "Alibaba Qoder route response")
    require(alibaba_qoder_support["ticket_id"] == "0001ZRMMS6" and alibaba_qoder_support["product_category"] == "QoderCn", "Alibaba official Qoder support ticket")
    require(alibaba_qoder_support["truth_boundary"]["engineer_assigned"] is True, "Alibaba Qoder engineer assignment")
    require(alibaba_qoder_support["truth_boundary"]["technical_conversation_completed"] is False, "Alibaba Qoder support conversation boundary")
    require(alibaba_qoder_support["repository_privacy"]["raw_phone_stored"] is False, "Alibaba Qoder support privacy")
    require(baidu_email["truth_boundary"]["outbound_request_sent"] is True, "Baidu email request")
    require(baidu_email["truth_boundary"]["technical_conversation_completed"] is False, "Baidu conversation boundary")
    require(plan["kpis"]["ecosystem"]["technical_conversation_request_events_submitted"] == 4, "technical request count")
    require(plan["kpis"]["ecosystem"]["technical_conversation_distinct_vendor_targets"] == 2, "technical target count")
    require(developer_intake["consent"]["explicit_consent_obtained"] is False, "developer consent template")
    require(developer_intake["truth_boundary"]["counts_toward_external_developer_kpi"] is False, "developer KPI boundary")
    require(conversation_brief["truth_boundary"]["application_submission_is_a_completed_conversation"] is False, "conversation KPI boundary")

    require("answer: conditional" in gate and "status: open_external_qoder_official_support_ticket_assigned_waiting_engineer_response" in gate, "recommendation gate")
    require(index["agent_readiness_capability_ecosystem_v2"]["public_operations"] == PUBLIC_TOOLS, "agent index")
    require("## SAEE Agent Readiness Capability Ecosystem Occupancy v2" in llms, "llms discovery")
    for boundary in (identity["truth_boundary"], package["truth_boundary"], plan["truth_boundary"]):
        require(boundary["production_ready"] is False, "production boundary")
    require(package["truth_boundary"]["official_qoder_integration"] is False, "Qoder integration boundary")
    require(package["truth_boundary"]["marketplace_listed"] is False, "marketplace boundary")
    print(
        "SAEE_ECOSYSTEM_OCCUPANCY_V2_SMOKE: PASS brand=frozen tools=2 "
        "adapters=5 qoder_local_compatibility=true qoder_process=false "
        "qianfan_provider_receipts=true one_page=true pdf_pages=10 video_seconds=180 "
        "external_technical_conversations=0/2 external_developer_tests=0/3 "
        "design_partners=0/1 official_integration=false marketplace_listed=false production_ready=false"
    )


if __name__ == "__main__":
    main()
