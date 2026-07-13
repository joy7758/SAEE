#!/usr/bin/env python3
"""Requirement-by-requirement completion audit for ecosystem occupancy v2."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "output/SAEE_ECOSYSTEM_OCCUPANCY_V2_COMPLETION_AUDIT.json"
OUTPUT_MD = ROOT / "output/SAEE_ECOSYSTEM_OCCUPANCY_V2_COMPLETION_AUDIT.md"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def command_ok(args: list[str]) -> bool:
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def requirement(req_id: str, title: str, complete: bool, evidence: list[str], note: str) -> dict:
    return {
        "requirement_id": req_id,
        "title": title,
        "status": "proven_complete" if complete else "incomplete",
        "evidence": evidence,
        "note": note,
    }


def main() -> None:
    plan = load("agent-interface/ecosystem/saee-ecosystem-occupancy-execution-plan.v2.json")
    package = load("agent-interface/ecosystem/saee-ecosystem-capability-package.v2.json")
    technical = plan["kpis"]["technical"]
    ecosystem = plan["kpis"]["ecosystem"]
    commercial = plan["kpis"]["commercial"]
    local_smoke = command_ok(["python3", "scripts/saee_ecosystem_occupancy_v2_smoke.py"])

    requirements = [
        requirement("R01", "Freeze SAEE Agent Readiness Capability identity", local_smoke, ["README.md", "docs/product/SAEE_AGENT_READINESS_CAPABILITY_V2.md"], "Human and machine names agree."),
        requirement("R02", "Expose exactly evaluate_agent_run and evaluate_evidence", local_smoke, ["saee-capability-card.json", "agent-interface/product/saee-agent-readiness-capability.v2.json"], "Two public operations; three internal operations excluded."),
        requirement("R03", "Create the SAEE Capability Card", local_smoke, ["saee-capability-card.json"], "Discovery, use/do-not-use, schemas and boundaries are file-backed."),
        requirement("R04", "Create Qoder-first adapter configuration", technical["qoder_configuration_and_local_protocol_validated"], [".mcp.json", "adapters/qoder/qoder-project.mcp.json"], "Official-format project config and local protocol compatibility pass."),
        requirement("R05", "Validate a Qoder process invoking SAEE", technical["qoder_process_invocation_validated"], ["adapters/qoder/README.md"], "Qoder CLI is absent; no Qoder process receipt exists."),
        requirement("R06", "Complete Qoder coding-release Demo", local_smoke, ["examples/qoder-saee-readiness-demo/request.json", "examples/qoder-saee-readiness-demo/response.json"], "REPLAN with rollback and approval missing; no deployment."),
        requirement("R07", "Retain Qianfan adapter evidence", technical["qianfan_bounded_provider_roundtrip_validated"], ["adapters/qianfan/README.md", "agent-interface/qianfan/live-validation/"], "Bounded synthetic provider receipts pass; official integration false."),
        requirement("R08", "Prepare LangChain, CrewAI, and Claude Code branches", local_smoke, ["adapters/langchain/", "adapters/crewai/", "adapters/claude-code/"], "Configuration templates only; framework processes not run."),
        requirement("R09", "Prepare one-page technical positioning", local_smoke, ["docs/ecosystem/SAEE_AGENT_READINESS_CAPABILITY_LAYER_ONE_PAGER.md"], "Platform-neutral position and boundaries present."),
        requirement("R10", "Prepare ten-page technical solution", local_smoke, ["docs/ecosystem/SAEE_AGENT_READINESS_CAPABILITY_TECHNICAL_SOLUTION_V2.md", "output/pdf/SAEE_Agent_Readiness_Capability_Technical_Solution_v2.0.pdf"], "Exactly ten rendered pages."),
        requirement("R11", "Prepare self-explanatory three-minute Demo video", local_smoke, ["output/video/SAEE_Ecosystem_Capability_Demo_v2.0.mp4", "output/video/SAEE_Ecosystem_Capability_Demo_v2.0.manifest.json"], "Nine scenes, 180 seconds, Chinese narration and subtitles."),
        requirement("R12", "Adjust GitHub discovery structure and first sentence", local_smoke, ["README.md", "agent-index.json", "llms.txt", "adapters/", "examples/"], "Frozen first sentence and Agent-readable entrypoints present."),
        requirement("R13", "Validate MCP Capability locally", technical["mcp_capability_local_validated"], [".mcp.json", "scripts/saee_qoder_adapter_smoke.py"], "Two-tool stdio discovery and calls pass."),
        requirement("R14", "Keep OpenAPI stable", technical["openapi_local_contract_validated"], ["capability-package/openapi.yaml", "scripts/saee_cloud_entry_package_smoke.py"], "Local package validation passes; no public service inferred."),
        requirement("R15", "Complete two cloud-vendor technical conversations", ecosystem["cloud_vendor_technical_conversation_completed"] >= ecosystem["cloud_vendor_technical_conversation_target"], ["agent-interface/ecosystem/saee-qoder-technical-conversation-request-email-receipt.v1.json", "agent-interface/ecosystem/saee-alibaba-qoder-technical-consultation-ticket-receipt.v1.json", "agent-interface/ecosystem/saee-alibaba-qoder-official-support-ticket-submission-receipt.v1.json", "agent-interface/ecosystem/saee-baidu-qianfan-technical-conversation-request-email-receipt.v1.json"], f"completed={ecosystem['cloud_vendor_technical_conversation_completed']}/{ecosystem['cloud_vendor_technical_conversation_target']}; in_progress={ecosystem['cloud_vendor_technical_conversation_in_progress']}; business_handoff_pending={ecosystem['cloud_vendor_business_handoff_pending']}; Qoder CN support declared the request outside support scope and forwarded it to business, so no active or completed technical conversation is inferred."),
        requirement("R16", "Complete one external ecosystem presentation", ecosystem["external_ecosystem_presentation_completed"] >= ecosystem["external_ecosystem_presentation_target"], ["agent-interface/ecosystem/saee-ecosystem-occupancy-execution-plan.v2.json"], f"completed={ecosystem['external_ecosystem_presentation_completed']}/{ecosystem['external_ecosystem_presentation_target']}; owned public demo is tracked separately."),
        requirement("R17", "Complete three consented external developer tests", ecosystem["consented_external_developer_test_completed"] >= ecosystem["consented_external_developer_test_target"], ["docs/ecosystem/SAEE_EXTERNAL_DEVELOPER_TEST_PROTOCOL_V1.md", "agent-interface/ecosystem/saee-external-developer-test-intake.template.v1.json"], f"completed={ecosystem['consented_external_developer_test_completed']}/{ecosystem['consented_external_developer_test_target']}; protocol and intake are ready but no external observation is counted."),
        requirement("R18", "Confirm one Design Partner", commercial["design_partner_completed"] >= commercial["design_partner_target"], ["agent-interface/ecosystem/saee-ecosystem-occupancy-execution-plan.v2.json"], f"completed={commercial['design_partner_completed']}/{commercial['design_partner_target']}."),
        requirement("R19", "Prepare one joint-solution draft", commercial["unilateral_joint_solution_draft_completed"] >= commercial["joint_solution_draft_target"], ["docs/ecosystem/SAEE_QODER_JOINT_SOLUTION_DRAFT_V0_1.md"], "Unilateral bounded draft complete; Alibaba review and confirmation remain false."),
        requirement("R20", "Stop new protocol, Runtime, governance modules, and architecture papers", plan["stopped_work"] == ["NEW_PROTOCOL", "NEW_RUNTIME", "NEW_GOVERNANCE_MODULE", "ADDITIONAL_ARCHITECTURE_PAPER"], ["agent-interface/ecosystem/saee-ecosystem-occupancy-execution-plan.v2.json"], "This package reuses the existing two-tool Runtime."),
        requirement("R21", "Obtain Qoder Plugin or Qianfan Capability entry", package["truth_boundary"]["official_qoder_plugin"] or plan["truth_boundary"]["official_cloud_integration"], ["agent-interface/ecosystem/saee-ecosystem-capability-package.v2.json", "agent-interface/ecosystem/saee-qoder-global-partner-application-submission-receipt.v1.json"], "The Qoder partner application is submitted; no approved plugin or official capability entry exists."),
        requirement("R22", "Enter an approved cloud marketplace route", plan["truth_boundary"]["approved_cloud_marketplace_route_available"], ["agent-interface/ecosystem/saee-alibaba-product-ecosystem-partner-activation-receipt.v1.json"], "Alibaba Product Ecosystem Partner and AI Partner Basic Lv.1 workbench access exposes a cloud-marketplace self-service route; no SAEE product submission or listing is inferred."),
        requirement("R23", "Preserve non-audit, non-execution, and authorization boundaries", local_smoke and not package["truth_boundary"]["production_ready"], ["docs/strategy/SAEE_ECOSYSTEM_OCCUPANCY_V2_RECOMMENDATION_GATE.md", "saee-capability-card.json"], "Evaluation remains a read-only capability projection."),
    ]
    complete_count = sum(item["status"] == "proven_complete" for item in requirements)
    incomplete = [item["requirement_id"] for item in requirements if item["status"] != "proven_complete"]
    result = {
        "audit_id": "saee.ecosystem-occupancy-v2.completion-audit",
        "requirement_count": len(requirements),
        "proven_complete_count": complete_count,
        "incomplete_requirement_ids": incomplete,
        "goal_complete": not incomplete,
        "requirements": requirements,
        "truth_boundary": {
            "local_package_ready": local_smoke,
            "qoder_process_executed": plan["truth_boundary"]["qoder_process_executed"],
            "official_qoder_integration": plan["truth_boundary"]["official_qoder_integration"],
            "external_kpis_complete": not any(item in incomplete for item in ["R15", "R16", "R17", "R18"]),
            "marketplace_listed": package["truth_boundary"]["marketplace_listed"],
            "production_ready": False,
        },
    }
    OUTPUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_JSON.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["| ID | Requirement | Status | Note |", "|---|---|---|---|"]
    rows.extend(f"| {item['requirement_id']} | {item['title']} | `{item['status']}` | {item['note']} |" for item in requirements)
    OUTPUT_MD.write_text("\n".join([
        "# SAEE Ecosystem Occupancy v2 Completion Audit",
        "",
        f"Overall: `goal_complete={str(not incomplete).lower()}`; proven complete: `{complete_count}/{len(requirements)}`.",
        "",
        *rows,
        "",
        "Incomplete requirements require a real platform process, independently verifiable external participation, or provider approval. Local configuration, applications, templates, and owned demos do not close those gates.",
        "",
    ]), encoding="utf-8")
    print(f"SAEE_ECOSYSTEM_OCCUPANCY_V2_COMPLETION_AUDIT: PASS audited={len(requirements)} proven_complete={complete_count} incomplete={len(incomplete)} goal_complete={str(not incomplete).lower()}")


if __name__ == "__main__":
    main()
