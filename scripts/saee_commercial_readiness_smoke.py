#!/usr/bin/env python3
"""Offline consistency smoke for SAEE Commercial Readiness Review v0.1."""

from __future__ import annotations

import ast
import copy
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ASSESSMENT_PATH = ROOT / "agent-interface/commercial/saee-commercial-readiness.v0.1.json"
REPORT_PATH = ROOT / "docs/commercial/SAEE_COMMERCIAL_READINESS_REVIEW.md"
BOUNDARY_PATH = ROOT / "docs/commercial/SAEE_COMMERCIAL_CLAIMS_BOUNDARY.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_READINESS_REVIEW_RECOMMENDATION_GATE.md"
PREVIEW_STATUS_PATH = ROOT / "agent-interface/agent-first-commercial-preview-status.json"

FALSE_CLAIMS = (
    "commercial_ready",
    "pilot_ready",
    "production_ready",
    "enterprise_ready",
    "customer_validated",
    "customer_contacted",
    "revenue_validated",
    "product_launched",
    "regulatory_compliance_claimed",
    "security_certified",
)
SCORE_FIELDS = {"technology", "product", "market", "integration", "trust"}


class CommercialReadinessError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise CommercialReadinessError(code, detail)


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_assessment(document: dict[str, Any]) -> dict[str, Any]:
    require(document.get("saee_commercial_readiness_review_v0_1") is True, "COMMERCIAL_ASSESSMENT_IDENTITY_INVALID", "root marker")
    require(document.get("assessment_version") == "0.1", "COMMERCIAL_ASSESSMENT_VERSION_INVALID", "version")
    require(document.get("assessment_type") == "objective_internal_assessment", "COMMERCIAL_ASSESSMENT_TYPE_INVALID", "assessment type")
    require(document.get("product_stage") == "research_prototype", "COMMERCIAL_PRODUCT_STAGE_INVALID", "product stage")
    for field in FALSE_CLAIMS:
        require(document.get(field) is False, "COMMERCIAL_UNSUPPORTED_READINESS_CLAIM", f"{field} must be false")
    scores = document.get("scores")
    require(isinstance(scores, dict) and set(scores) == SCORE_FIELDS, "COMMERCIAL_SCORE_SET_INVALID", "scores")
    for name, value in scores.items():
        require(type(value) is int and 0 <= value <= 5, "COMMERCIAL_SCORE_INVALID", name)
    report_scores = document.get("report_dimension_scores")
    require(isinstance(report_scores, dict) and len(report_scores) == 6, "COMMERCIAL_SCORE_SET_INVALID", "report scores")
    require(all(type(value) is int and 0 <= value <= 5 for value in report_scores.values()), "COMMERCIAL_SCORE_INVALID", "report scores")
    sellable = document.get("sellable_today")
    require(isinstance(sellable, dict), "COMMERCIAL_SELLABLE_BOUNDARY_INVALID", "sellable_today")
    require(sellable.get("standardized_production_software") is False, "COMMERCIAL_SELLABLE_BOUNDARY_INVALID", "standardized software")
    require(sellable.get("status") == "not_customer_validated_not_commercially_operational", "COMMERCIAL_SELLABLE_BOUNDARY_INVALID", "candidate status")
    require(len(document.get("customer_hypotheses", [])) == 5, "COMMERCIAL_CUSTOMER_HYPOTHESIS_INVALID", "top five")
    require(document.get("current_production_blocker_count") == 24, "COMMERCIAL_BLOCKER_TRUTH_INVALID", "production blocker count")
    require(isinstance(document.get("limitations"), list) and document["limitations"], "COMMERCIAL_LIMITATIONS_REQUIRED", "limitations")
    return document


def validate_documents() -> None:
    for path in (REPORT_PATH, BOUNDARY_PATH, GATE_PATH):
        require(path.is_file(), "COMMERCIAL_DOCUMENT_MISSING", str(path))
    report = REPORT_PATH.read_text(encoding="utf-8")
    for section in range(1, 12):
        require(f"## {section} " in report, "COMMERCIAL_REPORT_SECTION_MISSING", str(section))
    for token in ("Enterprise AI teams", "AI governance/security teams", "Regulated industries", "AI evaluation labs"):
        require(token in report, "COMMERCIAL_CUSTOMER_ANALYSIS_MISSING", token)
    require("SAEE Evidence Adequacy Review Pack" in report, "COMMERCIAL_MVP_MISSING", "minimum viable product")

    boundary = BOUNDARY_PATH.read_text(encoding="utf-8")
    require("SAEE currently represents a research prototype and evaluation framework. It is not a production governance platform or certified compliance solution." in boundary, "COMMERCIAL_BOUNDARY_MISSING", "English")
    require("SAEE 当前代表研究原型和评估框架，不是生产级治理平台，也不是经过认证的合规解决方案." in boundary, "COMMERCIAL_BOUNDARY_MISSING", "Chinese")

    forbidden_assertions = (
        "SAEE 已经生产就绪",
        "SAEE 已获得客户采用",
        "SAEE 已产生收入",
        "SAEE is production ready",
        "SAEE is enterprise ready",
        "SAEE is a certified compliance solution",
    )
    combined = report + "\n" + boundary
    require(not any(token in combined for token in forbidden_assertions), "COMMERCIAL_UNSUPPORTED_COPY", "unsupported affirmative claim")

    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    imports.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    require(not imports.intersection({"socket", "subprocess", "urllib", "requests", "httpx"}), "COMMERCIAL_EXTERNAL_CAPABILITY_IMPORT", "forbidden import")


def validate_existing_truth_surface() -> None:
    preview = read_json(PREVIEW_STATUS_PATH)
    truth = preview["truth_boundary"]
    production = preview["production_readiness"]
    for field in ("customer_validated", "production_ready", "product_launched", "customer_contacted", "revenue_validated"):
        require(truth.get(field) is False, "COMMERCIAL_SOURCE_TRUTH_DRIFT", field)
    require(production.get("verdict") == "hold", "COMMERCIAL_SOURCE_TRUTH_DRIFT", "production verdict")
    require(production.get("production_blocker_count") == 24, "COMMERCIAL_SOURCE_TRUTH_DRIFT", "blocker count")


def main() -> None:
    require(ASSESSMENT_PATH.is_file(), "COMMERCIAL_ASSESSMENT_MISSING", str(ASSESSMENT_PATH))
    source = read_json(ASSESSMENT_PATH)
    result = validate_assessment(copy.deepcopy(source))
    validate_documents()
    validate_existing_truth_surface()

    invalid_cases: list[tuple[dict[str, Any], str]] = []
    production = copy.deepcopy(source); production["product_stage"] = "production_service"; invalid_cases.append((production, "COMMERCIAL_PRODUCT_STAGE_INVALID"))
    ready = copy.deepcopy(source); ready["commercial_ready"] = True; invalid_cases.append((ready, "COMMERCIAL_UNSUPPORTED_READINESS_CLAIM"))
    customer = copy.deepcopy(source); customer["customer_validated"] = True; invalid_cases.append((customer, "COMMERCIAL_UNSUPPORTED_READINESS_CLAIM"))
    score = copy.deepcopy(source); score["scores"]["market"] = 6; invalid_cases.append((score, "COMMERCIAL_SCORE_INVALID"))
    blockers = copy.deepcopy(source); blockers["current_production_blocker_count"] = 0; invalid_cases.append((blockers, "COMMERCIAL_BLOCKER_TRUTH_INVALID"))
    for candidate, expected in invalid_cases:
        try:
            validate_assessment(candidate)
        except CommercialReadinessError as exc:
            require(exc.code == expected, "COMMERCIAL_REASON_CODE_UNSTABLE", f"expected {expected}, got {exc.code}")
        else:
            raise CommercialReadinessError("COMMERCIAL_INVALID_CASE_ACCEPTED", expected)

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = validate_assessment(copy.deepcopy(source))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "COMMERCIAL_NON_DETERMINISTIC", "assessment")

    print("SAEE_COMMERCIAL_READINESS_SMOKE: PASS")
    print("valid_cases=1/1")
    print("invalid_cases=5/5")
    print("deterministic_runs=5/5")
    print("report_sections=11/11")
    print("core_scores=5/5")
    print("customer_hypotheses=5/5")
    print("product_stage=research_prototype")
    print("production_blocker_count=24")
    print("commercial_ready=false")
    print("pilot_ready=false")
    print("production_ready=false")
    print("customer_validated=false")
    print("customer_contacted=false")
    print("revenue_validated=false")
    print("product_launched=false")
    print("regulatory_compliance_claimed=false")
    print("security_certified=false")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")


if __name__ == "__main__":
    main()

