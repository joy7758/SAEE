#!/usr/bin/env python3
"""Offline deterministic checks for the SAEE Design Partner protocol-only plan."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = ROOT / "agent-interface/commercial/saee-design-partner-validation-plan.v0.1.json"
PROTOCOL_PATH = ROOT / "docs/commercial/SAEE_DESIGN_PARTNER_VALIDATION_PROTOCOL.md"
DEMO_PATH = ROOT / "docs/commercial/SAEE_DESIGN_PARTNER_DEMO_SCRIPT.md"
FEEDBACK_PATH = ROOT / "docs/commercial/SAEE_DESIGN_PARTNER_FEEDBACK_TEMPLATE.md"
BOUNDARIES_PATH = ROOT / "docs/commercial/SAEE_EXTERNAL_ENGAGEMENT_BOUNDARIES.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_DESIGN_PARTNER_VALIDATION_PROTOCOL_RECOMMENDATION_GATE.md"
REPORT_PATH = ROOT / "docs/commercial/SAEE_SYNTHETIC_EVIDENCE_REVIEW_REPORT_EXAMPLE.md"

ROOT_KEYS = {
    "saee_design_partner_validation_plan_v0_1",
    "plan_version",
    "validation_stage",
    "objective",
    "source_artifacts",
    "profiles",
    "interview",
    "demo",
    "feedback_template",
    "metrics",
    "boundaries",
    "customer_contacted",
    "feedback_collected",
    "customer_data_received",
    "personal_data_stored",
    "pilot_started",
    "customer_validated",
    "market_fit_achieved",
    "revenue_opportunity_confirmed",
    "customer_adoption_confirmed",
    "commercial_success_claimed",
    "production_ready",
    "next_step",
}

FALSE_STATUS_FIELDS = (
    "customer_contacted",
    "feedback_collected",
    "customer_data_received",
    "personal_data_stored",
    "pilot_started",
    "customer_validated",
    "market_fit_achieved",
    "revenue_opportunity_confirmed",
    "customer_adoption_confirmed",
    "commercial_success_claimed",
    "production_ready",
)

REQUIRED_PROFILES = {
    "AI_EVALUATION_RED_TEAM_LAB",
    "AI_GOVERNANCE_CONSULTANCY",
    "AI_AGENT_PLATFORM_TEAM",
}

REQUIRED_METRICS = {
    "PROBLEM_RECOGNITION",
    "WORKFLOW_FIT",
    "VALUE_PERCEPTION",
    "ADOPTION_BARRIER",
    "FOLLOW_UP_INTEREST",
}


class DesignPartnerValidationSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise DesignPartnerValidationSmokeError(detail)


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), "plan root must be object")
    return value


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def forbidden_execution_calls(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "compile", "__import__"}:
            found.add(node.func.id)
        elif isinstance(node.func, ast.Attribute) and node.func.attr in {"system", "popen", "run", "Popen"}:
            found.add(node.func.attr)
    return found


def all_keys(value: Any) -> set[str]:
    if isinstance(value, dict):
        return set(value).union(*(all_keys(child) for child in value.values())) if value else set()
    if isinstance(value, list):
        result: set[str] = set()
        for child in value:
            result.update(all_keys(child))
        return result
    return set()


def validate_plan(plan: dict[str, Any]) -> dict[str, Any]:
    require(set(plan) == ROOT_KEYS, "unexpected or missing root field")
    require(plan["saee_design_partner_validation_plan_v0_1"] is True, "plan marker missing")
    require(plan["plan_version"] == "0.1.0", "plan version invalid")
    require(plan["validation_stage"] == "protocol_only", "validation stage promoted")
    for field in FALSE_STATUS_FIELDS:
        require(plan[field] is False, f"unsupported status claim: {field}")
    require(
        plan["next_step"]
        == "Complete Agent Discoverability, Tool Capability, and External Agent Recommendation gates before considering protocol review",
        "next step invalid",
    )

    for ref in plan["source_artifacts"]:
        require(isinstance(ref, str) and (ROOT / ref).is_file(), f"source artifact missing: {ref}")

    profiles = plan["profiles"]
    require(isinstance(profiles, list) and len(profiles) == 3, "partner profile count invalid")
    require({item["profile_id"] for item in profiles} == REQUIRED_PROFILES, "partner profile coverage invalid")
    for item in profiles:
        require(
            set(item) == {"profile_id", "problem_hypothesis", "expected_feedback", "adoption_barrier"}
            and all(isinstance(value, str) and value.strip() for value in item.values()),
            f"partner profile invalid: {item}",
        )

    interview = plan["interview"]
    require(interview["duration_minutes"] == {"minimum": 20, "maximum": 30}, "interview duration invalid")
    require(interview["synthetic_material_only"] is True, "non-synthetic interview material allowed")
    require(interview["recording_allowed"] is False, "recording allowed")
    require(len(interview["sections"]) == 4, "interview section coverage invalid")
    questions = [question for section in interview["sections"] for question in section["questions"]]
    require(12 <= len(questions) <= 20, "interview question count invalid")
    leading_terms = ("will you buy", "what is your budget", "purchase date", "when will you purchase")
    require(not any(term in question.lower() for question in questions for term in leading_terms), "leading sales question present")

    demo = plan["demo"]
    require((ROOT / demo["script_ref"]).is_file() and (ROOT / demo["report_ref"]).is_file(), "demo reference missing")
    require(
        demo["steps"] == ["SHOW_AGENT_TRACE", "SHOW_EVIDENCE_GAP", "SHOW_SAEE_REVIEW_REPORT", "EXPLAIN_BOUNDARIES"],
        "demo flow invalid",
    )
    require(demo["safety_or_compliance_certification_claimed"] is False, "certification claim promoted")
    require(demo["deployment_authority_claimed"] is False, "deployment authority promoted")

    feedback = plan["feedback_template"]
    require((ROOT / feedback["template_ref"]).is_file(), "feedback template missing")
    require(feedback["feedback_records"] == [], "feedback record present")
    forbidden_fields = {
        "person_name",
        "email_address",
        "organization_name",
        "contact_details",
        "private_logs",
        "production_traces",
        "customer_data",
    }
    require(set(feedback["forbidden_collection_fields"]) == forbidden_fields, "forbidden collection coverage invalid")
    plan_keys = all_keys(plan)
    require(not plan_keys.intersection(forbidden_fields), "personal or customer data field instantiated")

    metrics = plan["metrics"]
    require({item["metric_id"] for item in metrics} == REQUIRED_METRICS, "validation metric coverage invalid")
    require(all(set(item) == {"metric_id", "allowed_values", "does_not_establish"} for item in metrics), "metric shape invalid")

    boundaries = plan["boundaries"]
    require(boundaries["protocol_review_required_before_interview"] is True, "protocol review gate missing")
    require(boundaries["per_session_consent_required"] is True, "session consent missing")
    require(boundaries["synthetic_examples_only"] is True, "synthetic-only boundary missing")
    for field in (
        "personal_information_collection_allowed",
        "customer_data_collection_allowed",
        "private_log_collection_allowed",
        "production_trace_collection_allowed",
        "customer_outreach_authorized",
        "sales_activity_authorized",
        "pilot_authorized",
        "pricing_discussion_in_scope",
        "contract_creation_in_scope",
        "crm_creation_in_scope",
    ):
        require(boundaries[field] is False, f"engagement boundary promoted: {field}")
    return copy.deepcopy(plan)


def expect_invalid(plan: dict[str, Any], label: str) -> None:
    try:
        validate_plan(plan)
    except DesignPartnerValidationSmokeError:
        return
    raise DesignPartnerValidationSmokeError(f"invalid plan accepted: {label}")


def main() -> None:
    required_paths = (PLAN_PATH, PROTOCOL_PATH, DEMO_PATH, FEEDBACK_PATH, BOUNDARIES_PATH, GATE_PATH, REPORT_PATH)
    for path in required_paths:
        require(path.is_file(), f"missing required file: {path}")

    forbidden_imports = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(Path(__file__)).intersection(forbidden_imports), "network or subprocess capability imported")
    require(not forbidden_execution_calls(Path(__file__)), "dynamic or external execution present")

    protocol_text = PROTOCOL_PATH.read_text(encoding="utf-8")
    boundaries_text = BOUNDARIES_PATH.read_text(encoding="utf-8")
    for marker in (
        "Design Partner Validation != Customer Acquisition",
        "Interview != Customer Commitment",
        "Feedback != Market Validation",
        "Interest != Willingness To Pay",
        "20–30",
        "Current Practice",
        "Pain Discovery",
        "SAEE Concept Review",
        "Adoption Barrier",
        "protocol_review_deferred_until_agent_native_gates",
    ):
        require(marker in protocol_text, f"protocol marker missing: {marker}")
    for marker in ("Before Consent", "During Validation", "After Validation", "customer_contacted=false", "pilot_started=false"):
        require(marker in boundaries_text, f"boundary marker missing: {marker}")
    for claim in (
        "customer_validated=true",
        "market_fit_achieved=true",
        "revenue_opportunity_confirmed=true",
        "customer_adoption_confirmed=true",
        "pilot_started=true",
    ):
        require(claim not in protocol_text and claim not in boundaries_text, f"unsupported documentation claim: {claim}")

    plan = read_json(PLAN_PATH)
    canonical = validate_plan(plan)

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    for field in ("customer_contacted", "feedback_collected", "customer_data_received", "pilot_started"):
        mutation = copy.deepcopy(plan)
        mutation[field] = True
        invalid_cases.append((mutation, field))
    mutation = copy.deepcopy(plan)
    mutation["feedback_template"]["feedback_records"] = [{"role_category": "agent_platform"}]
    invalid_cases.append((mutation, "feedback record"))
    mutation = copy.deepcopy(plan)
    mutation["boundaries"]["customer_outreach_authorized"] = True
    invalid_cases.append((mutation, "outreach authorization"))
    mutation = copy.deepcopy(plan)
    mutation["feedback_template"]["email_address"] = "not-allowed@example.invalid"
    invalid_cases.append((mutation, "personal data field"))
    for mutation, label in invalid_cases:
        expect_invalid(mutation, label)

    encoded = json.dumps(canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_plan(read_json(PLAN_PATH))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "plan validation non-deterministic")

    print("SAEE_DESIGN_PARTNER_VALIDATION_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid_cases)}/{len(invalid_cases)}")
    print("deterministic_runs=5/5")
    print("partner_profiles=3/3")
    print("interview_sections=4/4")
    print("validation_metrics=5/5")
    print("feedback_records=0")
    print("personal_data_fields_present=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("customer_contacted=false")
    print("feedback_collected=false")
    print("customer_data_received=false")
    print("pilot_started=false")
    print("customer_validated=false")
    print("market_fit_achieved=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (DesignPartnerValidationSmokeError, json.JSONDecodeError) as exc:
        print(f"SAEE_DESIGN_PARTNER_VALIDATION_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
