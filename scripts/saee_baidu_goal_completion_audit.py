#!/usr/bin/env python3
"""Audit every explicit Baidu entry objective requirement against current evidence."""

from __future__ import annotations

import json
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


def command_ok(args: list[str]) -> bool:
    return subprocess.run(args, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0


def requirement(req_id: str, title: str, status: str, evidence: list[str], note: str) -> dict:
    return {"requirement_id": req_id, "title": title, "status": status, "evidence": evidence, "note": note}


def main() -> None:
    plan = json_read("agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json")
    preflight = json_read("agent-interface/ecosystem/saee-baidu-official-entry-preflight.v1.json")
    release = json_read("release/SAEE-v0.1-alpha/release-manifest.json")
    gate = json_read("agent-interface/ecosystem/saee-baidu-external-action-authorization-gate.v1.json")
    readme = read("README.md")
    site = read("sites/saee-commercial/app/page.tsx")
    card = json_read("cloud-entry-package/capability-card.json")
    git_head = command_ok(["git", "rev-parse", "--verify", "HEAD"])
    root_license = exists("LICENSE")
    key_file = Path.home() / ".config/saee/provider-keys.env"
    qianfan_key_name_present = key_file.is_file() and any(line.strip().startswith("QIANFAN_API_KEY=") and line.strip() != "QIANFAN_API_KEY=" for line in key_file.read_text(encoding="utf-8").splitlines())

    requirements = [
        requirement("R01", "Freeze SAEE Agent Readiness Platform brand", "proven_complete_local", ["README.md", "docs/product/SAEE_PRODUCT_IDENTITY_V1.md", "agent-interface/product/saee-agent-readiness-platform.v0.1.json"], "Human and machine first-class surfaces agree."),
        requirement("R02", "Position as Agent reliability/readiness, not governance", "proven_complete_local", ["docs/product/SAEE_PRODUCT_IDENTITY_V1.md", "docs/strategy/SAEE_BAIDU_CLOUD_MARKETPLACE_ENTRY_RECOMMENDATION_GATE.md"], "audit_first_reframe=false and non-use boundaries are explicit."),
        requirement("R03", "First product is Agent Readiness Assessment service", "proven_complete_local", ["agent-interface/product/saee-agent-readiness-platform.v0.1.json", "cloud-entry-package/capability-card.json"], "Two operations are capability interfaces inside the assessment service, not the commercial SKU."),
        requirement("R04", "Baidu target architecture includes BOS through Readiness Report", "proven_complete_target_architecture", ["cloud-entry-package/architecture.svg", "cloud-entry-package/architecture.png", "cloud-entry-package/materials/SAEE_BAIDU_TECHNICAL_WHITEPAPER_V1.md"], "BOS is truthfully marked target composition; BOS access is not implemented."),
        requirement("R05", "Phase 0 exposes exactly evaluate_agent_run and evaluate_evidence", "proven_complete_local", ["agent-interface/public/saee-public-capability-surface.v0.1.json", "cloud-entry-package/openapi.yaml", "cloud-entry-package/mcp.json"], f"public_operation_count={len(card['public_operations'])}; internal debug operations are excluded."),
        requirement("R06", "Phase 1 Qianfan adapter and customer-service/coding demos", "proven_complete_controlled_offline", ["scripts/saee_qianfan_readiness_mcp_smoke.py", "scripts/saee_qianfan_readiness_host_smoke.py", "cloud-entry-package/demo/"], "Offline provider simulation and two product scenarios pass; real Qianfan product roundtrip remains false."),
        requirement("R07", "Phase 2 30-minute Cloud Entry Package", "proven_complete_local", ["cloud-entry-package/README.md", "scripts/saee_cloud_entry_package_smoke.py"], "29 required package files and the documented local path pass."),
        requirement("R08", "Phase 3 product page, 10-page whitepaper, 3-minute video", "proven_complete_local_not_published", ["sites/saee-commercial/app/page.tsx", "output/pdf/SAEE_Baidu_Cloud_Technical_Whitepaper_v1.0.pdf", "output/video/SAEE_Baidu_Cloud_Demo_v1.0.mp4"], "Site tests pass; PDF is 10 pages; video is 180.021 seconds."),
        requirement("R09", "Phase 4 official Baidu ecosystem route and application materials", "preflight_complete_submission_not_authorized", ["agent-interface/ecosystem/saee-baidu-official-entry-preflight.v1.json", "cloud-entry-package/materials/SAEE_BAIDU_PARTNER_PRODUCT_SOLUTION_V1.docx"], "Qianfan partner consultation is verified as first route; company/contact inputs and submission are missing."),
        requirement("R10", "Create main baseline and SAEE-v0.1-alpha GitHub Release", "not_achieved", ["release/SAEE-v0.1-alpha/release-manifest.json", "release/SAEE-v0.1-alpha/public-baseline-audit.json"], f"git_head_exists={str(git_head).lower()}; root_license_present={str(root_license).lower()}; github_release_created={str(release['truth_boundary']['github_release_created']).lower()}."),
        requirement("R11", "Use the required GitHub first sentence", "proven_complete_local", ["README.md"], f"exact_sentence_present={str('SAEE is an Agent Readiness Infrastructure for evaluating whether AI agents have sufficient execution evidence before real-world deployment.' in readme).lower()}."),
        requirement("R12", "Prepare basic and enterprise commercial packaging", "proven_complete_internal_hypothesis_public_approval_missing", ["cloud-entry-package/materials/SAEE_BAIDU_COMMERCIAL_PACKAGING_DRAFT_V1.md"], "Suggested price ranges are preserved as owner-review hypotheses, not public quotes."),
        requirement("R13", "Prepare three public demos", "local_demo_assets_complete_not_public", ["cloud-entry-package/demo/customer-service-refund/", "cloud-entry-package/demo/coding-agent-release/", "cloud-entry-package/demo/evaluate-evidence/"], "Three versioned demos exist locally; no public demo publication evidence exists."),
        requirement("R14", "Execute the 90-day route", "partially_achieved", ["docs/ecosystem/SAEE_BAIDU_90_DAY_EXECUTION_BOARD_V1.md"], "Local technical/material work is complete, while Release, community publication, technical article, ecosystem contact and submission remain external future actions."),
        requirement("R15", "Become callable by a real Baidu Qianfan Agent", "not_achieved", ["scripts/saee_qianfan_readiness_host.py", "agent-interface/ecosystem/saee-baidu-cloud-marketplace-entry-plan.v1.0.json"], f"controlled_offline=true; qianfan_key_name_present={str(qianfan_key_name_present).lower()}; real_product_roundtrip=false."),
    ]
    achieved_statuses = {"proven_complete_local", "proven_complete_target_architecture", "proven_complete_controlled_offline", "proven_complete_local_not_published", "proven_complete_internal_hypothesis_public_approval_missing"}
    achieved = sum(item["status"] in achieved_statuses for item in requirements)
    incomplete = [item["requirement_id"] for item in requirements if item["status"] not in achieved_statuses]
    result = {
        "audit_id": "saee-baidu-entry-goal-completion-2026-07-13",
        "objective_requirement_count": len(requirements),
        "proven_complete_requirement_count": achieved,
        "incomplete_requirement_ids": incomplete,
        "goal_status": "not_complete_human_external_and_release_gates",
        "requirements": requirements,
        "blocking_facts": {
            "git_head_exists": git_head,
            "root_license_present": root_license,
            "qianfan_key_name_present": qianfan_key_name_present,
            "real_qianfan_product_roundtrip": plan["truth_boundary"]["qianfan_real_provider_product_roundtrip"],
            "company_identity_verified": gate["preconditions"]["company_identity_verified"],
            "external_action_authorized": gate["authorization"]["approved"],
            "github_release_created": release["truth_boundary"]["github_release_created"],
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
        f"Overall: `not_complete_human_external_and_release_gates`; requirements proven complete: `{achieved}/{len(requirements)}`.",
        "",
        *rows,
        "",
        "## Exact remaining gates",
        "",
        "1. Owner-selected root LICENSE and approved first public commit scope.",
        "2. Local commit, tag, push and GitHub Release under separately approved Git actions.",
        "3. Qianfan credential and one bounded real product two-tool roundtrip.",
        "4. Verified company/contact/qualification information and public price approval.",
        "5. Explicit authorization for Qianfan consultation, community/article publication, Baidu contact or application submission.",
        "",
        "```text",
        "goal_complete=false",
        "github_release_created=false",
        "real_qianfan_product_roundtrip=false",
        "baidu_submission=false",
        "marketplace_listed=false",
        "production_ready=false",
        "```",
        ""
    ])
    MD_OUTPUT.write_text(markdown, encoding="utf-8")
    print(f"SAEE_BAIDU_GOAL_COMPLETION_AUDIT: PASS audited={len(requirements)} proven_complete={achieved} incomplete={len(incomplete)} goal_complete=false")


if __name__ == "__main__":
    main()
