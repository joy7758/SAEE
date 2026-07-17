"""Offline validator for the first SAEE ecosystem demonstration package."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DEMO_ROOT = ROOT / "examples/ecosystem-demo-v1"
SCENARIO_PATH = DEMO_ROOT / "scenario/coding-agent-preflight.json"
RESULT_PATH = DEMO_ROOT / "result-example.json"
REQUIRED_DOCUMENTS = {
    "README.md",
    "agent-flow.md",
    "mcp-demo.md",
    "interpretation.md",
    "limitations.md",
}
ALLOWED_RECOMMENDATIONS = {"CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"}
REQUIRED_FINDINGS = {"missing_test_evidence", "insufficient_recovery_plan"}
REQUIRED_LIMITATIONS = {
    "not_authorization",
    "not_certification",
    "not_security_guarantee",
    "not_deployment_approval",
    "not_external_compatibility_evidence",
}
FORBIDDEN_KEYS = {
    "production_claim",
    "adoption_claim",
    "certification_claim",
    "security_guarantee_claim",
    "approval_claim",
}
FORBIDDEN_AFFIRMATIVE = (
    re.compile(r"\bproduction\s+ready\b", re.I),
    re.compile(r"\bmarketplace\s+listed\b", re.I),
    re.compile(r"\bexternally\s+adopted\b", re.I),
    re.compile(r"\bcertified\s+safe\b", re.I),
    re.compile(r"\bguaranteed\s+secure\b", re.I),
    re.compile(r"\bexternal\s+mcp\s+compatible\b", re.I),
)
NEGATIONS = ("not ", "no ", "does not ", "do not ", "isn't ", "不是", "不", "未", "没有")


def _result(valid: bool, reason_codes: list[str], documents: int = 0) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reason_codes,
        "demo_package": valid,
        "scenario_exists": valid,
        "flow_exists": valid,
        "result_example": valid,
        "limitations": valid,
        "scenario_count": 1 if valid else 0,
        "document_count": documents,
        "local_demo_only": True,
        "external_agent": False,
        "external_execution": False,
        "customer_validated": False,
        "marketplace_listed": False,
        "production_ready": False,
        "network_accessed": False,
        "subprocess_started": False,
    }


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        return any(key in FORBIDDEN_KEYS or _contains_forbidden_key(child) for key, child in value.items())
    if isinstance(value, list):
        return any(_contains_forbidden_key(child) for child in value)
    return False


def _has_affirmative_claim(text: str) -> bool:
    normalized = re.sub(r"\s+", " ", text).strip()
    for pattern in FORBIDDEN_AFFIRMATIVE:
        match = pattern.search(normalized)
        if match is None:
            continue
        prefix = normalized[max(0, match.start() - 48):match.start()].lower()
        if not any(marker in prefix for marker in NEGATIONS):
            return True
    return False


def validate_demo_data(scenario: Any, result: Any, documents: Any) -> dict[str, Any]:
    """Validate one fully local, synthetic ecosystem-demo representation."""

    document_count = len(documents) if isinstance(documents, dict) else 0
    if not isinstance(scenario, dict) or not isinstance(result, dict) or not isinstance(documents, dict):
        return _result(False, ["ECOSYSTEM_DEMO_DATA_INVALID"], document_count)
    if set(documents) != REQUIRED_DOCUMENTS or any(not isinstance(text, str) or not text.strip() for text in documents.values()):
        return _result(False, ["ECOSYSTEM_DEMO_DOCUMENT_SET_INVALID"], document_count)
    if scenario.get("scenario_id") != "coding-agent-preflight" or scenario.get("scenario_type") != "LOCAL_SYNTHETIC_PREFLIGHT":
        return _result(False, ["ECOSYSTEM_DEMO_SCENARIO_INVALID"], document_count)
    if scenario.get("required_capabilities") != ["evaluate_rehearsal_run", "evaluate_evidence"]:
        return _result(False, ["ECOSYSTEM_DEMO_CAPABILITY_FLOW_INVALID"], document_count)
    expected_flow = [
        "TASK_INSPECTION", "CAPABILITY_DISCOVERY", "CONTROLLED_REHEARSAL_CONTEXT",
        "RELIABILITY_ASSESSMENT", "EVIDENCE_EVALUATION", "BOUNDED_DECISION_CONTEXT",
        "AGENT_BEHAVIOR_ADJUSTMENT",
    ]
    if scenario.get("flow") != expected_flow:
        return _result(False, ["ECOSYSTEM_DEMO_CAPABILITY_FLOW_INVALID"], document_count)
    if scenario.get("expected_recommendation") != "REPLAN" or set(scenario.get("expected_findings", [])) != REQUIRED_FINDINGS:
        return _result(False, ["ECOSYSTEM_DEMO_EXPECTATION_INVALID"], document_count)
    scenario_false = ("customer_data", "external_agent", "external_execution", "deployment_authorized", "production_ready")
    if scenario.get("synthetic") is not True or any(scenario.get(key) is not False for key in scenario_false):
        return _result(False, ["ECOSYSTEM_DEMO_SCENARIO_BOUNDARY_INVALID"], document_count)
    if result.get("result_kind") != "SYNTHETIC_EXAMPLE_NOT_EXECUTION_RECORD" or result.get("scenario_ref") != "examples/ecosystem-demo-v1/scenario/coding-agent-preflight.json":
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_IDENTITY_INVALID"], document_count)
    if result.get("first_validation_candidate_reference") != "agent-interface/ecosystem/saee-first-validation-candidate-matrix.v0.1.json":
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_IDENTITY_INVALID"], document_count)
    if result.get("recommendation") not in ALLOWED_RECOMMENDATIONS or result.get("recommendation") != scenario["expected_recommendation"]:
        return _result(False, ["ECOSYSTEM_DEMO_RECOMMENDATION_INVALID"], document_count)
    if set(result.get("findings", [])) != REQUIRED_FINDINGS or set(result.get("limitations", [])) != REQUIRED_LIMITATIONS:
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_CONTENT_INVALID"], document_count)
    capability_results = result.get("capability_results")
    if not isinstance(capability_results, list) or {item.get("operation") for item in capability_results if isinstance(item, dict)} != {"evaluate_rehearsal_run", "evaluate_evidence"}:
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_CONTENT_INVALID"], document_count)
    if any(item.get("assessment") != "INSUFFICIENT_EVIDENCE" for item in capability_results):
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_CONTENT_INVALID"], document_count)
    if "Local MCP demonstration only" not in documents["mcp-demo.md"] or "SUPPORTED" not in documents["interpretation.md"] or "REPLAN" not in documents["agent-flow.md"]:
        return _result(False, ["ECOSYSTEM_DEMO_INTERPRETATION_MISSING"], document_count)
    boundary = result.get("truth_boundary")
    if not isinstance(boundary, dict) or boundary.get("ecosystem_demo") is not True or boundary.get("local_demo_only") is not True or boundary.get("synthetic_example") is not True:
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_BOUNDARY_INVALID"], document_count)
    if any(boundary.get(key) is not False for key in ("external_agent", "external_execution", "customer_validated", "marketplace_listed", "production_ready")):
        return _result(False, ["ECOSYSTEM_DEMO_RESULT_BOUNDARY_INVALID"], document_count)
    structured_text = json.dumps({"scenario": scenario, "result": result}, ensure_ascii=False, sort_keys=True)
    if _contains_forbidden_key({"scenario": scenario, "result": result}) or _has_affirmative_claim(structured_text) or any(
        _has_affirmative_claim(text) for text in documents.values()
    ):
        return _result(False, ["ECOSYSTEM_DEMO_UNSUPPORTED_CLAIM"], document_count)
    return _result(True, [], document_count)


def validate_demo_package() -> dict[str, Any]:
    if not DEMO_ROOT.is_dir() or not SCENARIO_PATH.is_file() or not RESULT_PATH.is_file():
        return _result(False, ["ECOSYSTEM_DEMO_PACKAGE_INCOMPLETE"])
    if any(not (DEMO_ROOT / name).is_file() for name in REQUIRED_DOCUMENTS):
        return _result(False, ["ECOSYSTEM_DEMO_PACKAGE_INCOMPLETE"])
    try:
        scenario = json.loads(SCENARIO_PATH.read_text(encoding="utf-8"))
        result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
        documents = {name: (DEMO_ROOT / name).read_text(encoding="utf-8") for name in REQUIRED_DOCUMENTS}
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _result(False, ["ECOSYSTEM_DEMO_PACKAGE_INVALID"])
    return validate_demo_data(scenario, result, documents)
