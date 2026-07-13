#!/usr/bin/env python3
"""Audit every explicit Baidu entry objective requirement against current evidence."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
JSON_OUTPUT = ROOT / "output/SAEE_BAIDU_ENTRY_GOAL_COMPLETION_AUDIT_2026-07-13.json"
MD_OUTPUT = ROOT / "output/SAEE_BAIDU_ENTRY_GOAL_COMPLETION_AUDIT_2026-07-13.md"


def exists(path: str) -> bool:
    return (ROOT / path).is_file()


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def json_read(path: str) -> dict:
    return json.loads(read(path))


def command_ok(args: list[str], cwd: Path = ROOT) -> bool:
    return subprocess.run(args, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def git_head_short(cwd: Path = ROOT) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "--short=9", "HEAD"],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
    return completed.stdout.strip() if completed.returncode == 0 else ""


def requirement(req_id: str, title: str, status: str, evidence: list[str], note: str) -> dict:
    return {"requirement_id": req_id, "title": title, "status": status, "evidence": evidence, "note": note}


def main() -> None:
    plan = json_read("agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json")
    preflight = json_read("agent-interface/ecosystem/saee-baidu-official-entry-preflight.v1.json")
    release = json_read("release/SAEE-v0.1-alpha/release-manifest.json")
    gate = json_read("agent-interface/ecosystem/saee-baidu-external-action-authorization-gate.v1.json")
    identity = json_read("agent-interface/product/saee-agent-readiness-platform.v0.1.json")
    publication = json_read("agent-interface/ecosystem/saee-baidu-publication-package.v1.json")
    qualification = json_read("agent-interface/ecosystem/saee-baidu-marketplace-qualification-matrix.v1.json")
    response_tracker = json_read("agent-interface/ecosystem/saee-baidu-partner-response-tracker.v1.json")
    readme = read("README.md")
    site = read("sites/saee-commercial/app/page.tsx")
    card = json_read("cloud-entry-package/capability-card.json")
    head_short = git_head_short()
    site_root = ROOT / "sites/saee-commercial"
    site_head_short = git_head_short(site_root)
    git_head = bool(head_short)
    root_license = exists("LICENSE")
    key_file = Path.home() / ".config/saee/provider-keys.env"
    qianfan_key_name_present = key_file.is_file() and any(
        re.match(r"^(?:export\s+)?QIANFAN_API_KEY=.+$", line.strip()) is not None
        for line in key_file.read_text(encoding="utf-8").splitlines()
    )

    checks = {
        "entry_plan": command_ok(["python3", "scripts/saee_baidu_cloud_marketplace_entry_plan_smoke.py"]),
        "qianfan_offline": command_ok(["python3", "scripts/saee_qianfan_readiness_mcp_smoke.py"]),
        "qianfan_live_receipts": command_ok(["python3", "scripts/saee_qianfan_readiness_live_receipt_smoke.py"]),
        "cloud_entry_package": command_ok(["python3", "scripts/saee_cloud_entry_package_smoke.py"]),
        "partner_submission": command_ok(["python3", "scripts/saee_baidu_partner_consultation_application_smoke.py"]),
        "publication_package": command_ok(["python3", "scripts/saee_baidu_publication_package_smoke.py"]),
        "response_tracker": command_ok(["python3", "scripts/saee_baidu_partner_response_tracker_smoke.py"]),
        "product_page": command_ok(["npm", "test"], site_root),
        "marketplace_qualification": command_ok(["python3", "scripts/saee_baidu_marketplace_qualification_smoke.py"]),
        "marketplace_qualification_evidence_intake": command_ok(["python3", "scripts/saee_baidu_marketplace_qualification_evidence_intake_smoke.py"]),
    }
    public_operations = [item["name"] for item in card["public_operations"]]
    expected_sentence = "SAEE is an Agent Readiness Infrastructure for evaluating whether AI agents have sufficient execution evidence before real-world deployment."
    brand_complete = (
        "SAEE Agent Readiness Platform" in readme
        and identity["external_brand"] == "SAEE Agent Readiness Platform"
        and identity["external_brand_zh"] == "SAEE 智能体上线准备平台"
    )
    positioning_complete = "audit_first_reframe=false" in read("docs/strategy/SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_RECOMMENDATION_GATE.md")
    product_complete = card["first_product"] == "SAEE Agent Readiness Assessment"
    architecture_complete = all(exists(path) for path in (
        "cloud-entry-package/architecture.svg",
        "cloud-entry-package/architecture.png",
        "cloud-entry-package/materials/SAEE_BAIDU_TECHNICAL_WHITEPAPER_V1.md",
    ))
    two_tool_surface_complete = public_operations == ["saee.evaluate_agent_run", "saee.evaluate_evidence"]
    phase_3_complete = (
        checks["cloud_entry_package"]
        and checks["product_page"]
        and "智能体上线前可靠性评估" in site
        and "它只做评估" in site
    )
    public_demos_published = publication["truth_boundary"]["public_demos_published"]
    technical_article_published = publication["truth_boundary"]["technical_article_published"]
    github_release_created = release["truth_boundary"]["github_release_created"]
    public_release_complete = root_license and github_release_created
    response_received = response_tracker["truth_boundary"]["baidu_response_received"]
    day_61_90_complete = public_release_complete and public_demos_published and technical_article_published and response_received

    requirements = [
        requirement("R01", "Freeze SAEE Agent Readiness Platform brand", "proven_complete_local" if brand_complete else "evidence_failed", ["README.md", "docs/product/SAEE_PRODUCT_IDENTITY_V1.md", "agent-interface/product/saee-agent-readiness-platform.v0.1.json"], f"human_and_machine_brand_complete={str(brand_complete).lower()}."),
        requirement("R02", "Position as Agent reliability/readiness, not governance", "proven_complete_local" if positioning_complete else "evidence_failed", ["docs/product/SAEE_PRODUCT_IDENTITY_V1.md", "docs/strategy/SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_RECOMMENDATION_GATE.md"], f"audit_first_reframe_boundary_present={str(positioning_complete).lower()}."),
        requirement("R03", "First product is Agent Readiness Assessment service", "proven_complete_local" if product_complete else "evidence_failed", ["agent-interface/product/saee-agent-readiness-platform.v0.1.json", "cloud-entry-package/capability-card.json"], f"assessment_product_identity={str(product_complete).lower()}."),
        requirement("R04", "Baidu target architecture includes BOS through Readiness Report", "proven_complete_target_architecture" if architecture_complete else "evidence_failed", ["cloud-entry-package/architecture.svg", "cloud-entry-package/architecture.png", "cloud-entry-package/materials/SAEE_BAIDU_TECHNICAL_WHITEPAPER_V1.md"], f"target_architecture_artifacts_complete={str(architecture_complete).lower()}; BOS access is not implemented."),
        requirement("R05", "Phase 0 exposes exactly evaluate_agent_run and evaluate_evidence", "proven_complete_local" if two_tool_surface_complete else "evidence_failed", ["agent-interface/public/saee-public-capability-surface.v0.1.json", "cloud-entry-package/openapi.yaml", "cloud-entry-package/mcp.json"], f"public_operations={public_operations}; internal debug operations are excluded."),
        requirement("R06", "Phase 1 Qianfan adapter and customer-service/coding demos", "proven_complete_real_provider_synthetic" if checks["qianfan_offline"] and checks["qianfan_live_receipts"] else "evidence_failed", ["scripts/saee_qianfan_readiness_mcp_smoke.py", "scripts/saee_qianfan_readiness_live_receipt_smoke.py", "agent-interface/qianfan/live-validation/"], f"offline_smoke={str(checks['qianfan_offline']).lower()}; live_receipt_smoke={str(checks['qianfan_live_receipts']).lower()}; bounded synthetic provider evidence only."),
        requirement("R07", "Phase 2 30-minute Cloud Entry Package", "proven_complete_local" if checks["cloud_entry_package"] else "evidence_failed", ["cloud-entry-package/README.md", "scripts/saee_cloud_entry_package_smoke.py"], f"cloud_entry_package_smoke={str(checks['cloud_entry_package']).lower()}."),
        requirement("R08", "Phase 3 product page, 10-page whitepaper, 3-minute video", "proven_complete_local_not_published" if phase_3_complete else "evidence_failed", ["sites/saee-commercial/app/page.tsx", "output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf", "output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4"], f"phase_3_local_artifacts_valid={str(phase_3_complete).lower()}; site_tests={str(checks['product_page']).lower()}; site_head={site_head_short or 'missing'}; publication not inferred."),
        requirement("R09", "Phase 4 official Baidu ecosystem route and application materials", "proven_complete_partner_consultation_submitted" if checks["partner_submission"] else "evidence_failed", ["agent-interface/ecosystem/saee-baidu-partner-consultation-submission-receipt.v1.json", "cloud-entry-package/materials/SAEE_BAIDU_PARTNER_PRODUCT_SOLUTION_V1.docx"], f"partner_submission_smoke={str(checks['partner_submission']).lower()}; this is not a Marketplace submission."),
        requirement("R10", "Create main baseline and SAEE-v0.1-alpha GitHub Release", "proven_complete_public_release" if public_release_complete else "partially_achieved_local_commit_only", ["release/SAEE-v0.1-alpha/release-manifest.json", "release/SAEE-v0.1-alpha/public-baseline-audit.json"], f"git_head_exists={str(git_head).lower()}; local_head={head_short or 'missing'}; root_license_present={str(root_license).lower()}; github_release_created={str(github_release_created).lower()}."),
        requirement("R11", "Use the required GitHub first sentence", "proven_complete_local" if expected_sentence in readme else "evidence_failed", ["README.md"], f"exact_sentence_present={str(expected_sentence in readme).lower()}."),
        requirement("R12", "Prepare basic and enterprise commercial packaging", "proven_complete_internal_hypothesis_public_approval_missing", ["cloud-entry-package/materials/SAEE_BAIDU_COMMERCIAL_PACKAGING_DRAFT_V1.md"], "Suggested price ranges are preserved as owner-review hypotheses, not public quotes."),
        requirement("R13", "Prepare three public demos", "proven_complete_publication" if checks["publication_package"] and public_demos_published else "local_publication_package_ready_not_public", ["cloud-entry-package/public-demos/README.md", "agent-interface/ecosystem/saee-baidu-publication-package.v1.json"], f"publication_package_smoke={str(checks['publication_package']).lower()}; public_demos_published={str(public_demos_published).lower()}."),
        requirement("R14", "Execute the 90-day route", "proven_complete_external_route" if day_61_90_complete else "partially_achieved_waiting_baidu_response_and_publication_authorization", ["docs/ecosystem/SAEE_BAIDU_90_DAY_EXECUTION_BOARD_V1.md", "agent-interface/ecosystem/saee-baidu-partner-response-tracker.v1.json"], f"response_tracker_smoke={str(checks['response_tracker']).lower()}; baidu_response_received={str(response_received).lower()}; technical_article_published={str(technical_article_published).lower()}; public_release_complete={str(public_release_complete).lower()}."),
        requirement("R15", "Become callable by a real Baidu Qianfan Agent", "proven_complete_real_provider_synthetic" if checks["qianfan_live_receipts"] else "evidence_failed", ["scripts/saee_qianfan_readiness_host.py", "scripts/saee_qianfan_readiness_live_receipt_smoke.py", "agent-interface/qianfan/live-validation/"], f"qianfan_key_name_present={str(qianfan_key_name_present).lower()}; live_receipt_smoke={str(checks['qianfan_live_receipts']).lower()}; official_qianfan_integration=false."),
        requirement("R16", "Close direct Baidu Marketplace provider qualifications", "proven_complete_marketplace_qualification" if checks["marketplace_qualification"] and checks["marketplace_qualification_evidence_intake"] and qualification["aggregate"]["qualification_complete"] else "qualification_packet_prepared_provider_criteria_unmet", ["agent-interface/ecosystem/saee-baidu-marketplace-qualification-matrix.v1.json", "agent-interface/ecosystem/saee-baidu-marketplace-qualification-evidence-intake.template.v1.json", "docs/strategy/SAEE_BAIDU_MARKETPLACE_QUALIFICATION_RECOMMENDATION_GATE.md"], f"qualification_smoke={str(checks['marketplace_qualification']).lower()}; sanitized_evidence_intake_smoke={str(checks['marketplace_qualification_evidence_intake']).lower()}; verified={qualification['aggregate']['verified_count']}/7; partial={qualification['aggregate']['partial_count']}/7; direct_application_recommended=false."),
    ]
    achieved_statuses = {"proven_complete_local", "proven_complete_target_architecture", "proven_complete_controlled_offline", "proven_complete_real_provider_synthetic", "proven_complete_local_not_published", "proven_complete_internal_hypothesis_public_approval_missing", "proven_complete_partner_consultation_submitted", "proven_complete_public_release", "proven_complete_publication", "proven_complete_external_route", "proven_complete_marketplace_qualification"}
    achieved = sum(item["status"] in achieved_statuses for item in requirements)
    incomplete = [item["requirement_id"] for item in requirements if item["status"] not in achieved_statuses]
    result = {
        "audit_id": "saee-baidu-entry-goal-completion-2026-07-13",
        "objective_requirement_count": len(requirements),
        "proven_complete_requirement_count": achieved,
        "incomplete_requirement_ids": incomplete,
        "goal_status": "complete" if not incomplete else "not_complete_public_release_demo_publication_90_day_and_marketplace_qualification_gates",
        "validator_results": checks,
        "requirements": requirements,
        "blocking_facts": {
            "git_head_exists": git_head,
            "root_license_present": root_license,
            "qianfan_key_name_present": qianfan_key_name_present,
            "real_qianfan_product_roundtrip": plan["truth_boundary"]["qianfan_real_provider_product_roundtrip"],
            "company_identity_verified": gate["preconditions"]["company_identity_verified"],
            "external_action_authorized": gate["authorization"]["approved"],
            "local_head": head_short,
            "site_head": site_head_short,
            "public_demos_published": public_demos_published,
            "technical_article_published": technical_article_published,
            "baidu_response_received": response_received,
            "github_release_created": github_release_created,
            "marketplace_qualification_verified_count": qualification["aggregate"]["verified_count"],
            "marketplace_qualification_complete": qualification["aggregate"]["qualification_complete"],
            "baidu_submission": preflight["truth_boundary"]["submission"]
        }
    }
    JSON_OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = ["| ID | Requirement | Status | Evidence note |", "|---|---|---|---|"]
    for item in requirements:
        rows.append(f"| {item['requirement_id']} | {item['title']} | `{item['status']}` | {item['note']} |")
    markdown = "\n".join([
        "# SAEE Baidu Entry Goal Completion Audit — 2026-07-13",
        "",
        "This is a requirement-by-requirement completion audit, not a launch or submission receipt.",
        "",
        f"Overall: `{result['goal_status']}`; requirements proven complete: `{achieved}/{len(requirements)}`.",
        "",
        *rows,
        "",
        "## Exact remaining gates",
        "",
        "1. Public license, tag, push and GitHub Release remain withheld or unauthorized.",
        "2. Public price approval and later direct-marketplace qualification evidence.",
        "3. Baidu response is pending; the remaining 90-day public demo, community and technical-article publication actions are not authorized.",
        "4. Direct Marketplace qualification remains `verified=0/7`; team, service history, staffed 5x8 support, software copyright, dedicated account, and agreement evidence are not closed.",
        "",
        "```text",
        "goal_complete=false",
        "github_release_created=false",
        "real_qianfan_product_roundtrip=true",
        "baidu_submission=true",
        "marketplace_listed=false",
        "production_ready=false",
        "```",
        ""
    ])
    MD_OUTPUT.write_text(markdown, encoding="utf-8")
    print(f"SAEE_BAIDU_GOAL_COMPLETION_AUDIT: PASS audited={len(requirements)} proven_complete={achieved} incomplete={len(incomplete)} goal_complete=false")


if __name__ == "__main__":
    main()
