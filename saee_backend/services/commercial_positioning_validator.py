"""Offline validator for SAEE Agent Readiness Assessment product packaging."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "commercial/agent-readiness-assessment-package-v1"
REQUIRED_FILES = {
    "README.md",
    "product.json",
    "assessment-scope.md",
    "scenario-template.md",
    "report-template.md",
    "limitations.md",
    "delivery-checklist.md",
}
EXPECTED_RECOMMENDATIONS = ["CONTINUE", "REPLAN", "HUMAN_REVIEW_REQUIRED", "STOP"]
EXPECTED_TRUTH = {
    "commercial_product_design": True,
    "assessment_package": True,
    "production_service": False,
    "public_service": False,
    "commercial_delivery_completed": False,
    "customer_validated": False,
    "market_validation": False,
    "revenue_confirmed": False,
    "deployment_authorized": False,
}
FORBIDDEN = (
    "certification",
    "guaranteed safety",
    "production approval",
    "best agent ranking",
    "customer success",
)
NEGATIONS = ("not ", "not a ", "does not", "do not", "false", "reject", "不是", "不提供", "不得", "没有", "未")


def _result(valid: bool, reasons: list[str]) -> dict[str, Any]:
    return {
        "valid": valid,
        "reason_codes": reasons,
        "product_definition": valid,
        "assessment_package": valid,
        "report_template": valid,
        "demo_flow": valid,
        "limitations": valid,
        "network_accessed": False,
        "subprocess_started": False,
        "external_execution": False,
        "commercial_delivery_completed": False,
        "production_service": False,
    }


def _local_file(ref: Any) -> bool:
    if not isinstance(ref, str) or not ref or "://" in ref or "\\" in ref:
        return False
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError:
        return False
    return path.is_file()


def find_unsupported_claims(text: str) -> list[str]:
    found: set[str] = set()
    for line in text.splitlines():
        normalized = re.sub(r"\s+", " ", line.strip().lower())
        for phrase in FORBIDDEN:
            if phrase not in normalized:
                continue
            prefix = normalized[: normalized.index(phrase)]
            if any(marker in prefix[-40:] for marker in NEGATIONS):
                continue
            found.add(phrase)
    return sorted(found)


def validate_product(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        return _result(False, ["PRODUCT_CONTRACT_INVALID"])
    if value.get("product_id") != "saee.agent-readiness-assessment":
        return _result(False, ["PRODUCT_ID_INVALID"])
    if value.get("language") != "zh-CN":
        return _result(False, ["PRODUCT_LANGUAGE_INVALID"])
    if value.get("allowed_recommendations") != EXPECTED_RECOMMENDATIONS:
        return _result(False, ["PRODUCT_RECOMMENDATION_SET_INVALID"])
    if value.get("truth_boundary") != EXPECTED_TRUTH:
        return _result(False, ["PRODUCT_TRUTH_BOUNDARY_INVALID"])
    refs = [value.get(name) for name in (
        "canonical_service_ref", "request_schema_ref", "response_schema_ref",
        "product_definition_ref", "report_template_ref", "demo_ref",
    )]
    if not all(_local_file(ref) for ref in refs):
        return _result(False, ["PRODUCT_REFERENCE_INVALID"])
    if find_unsupported_claims(json.dumps(value, ensure_ascii=False, sort_keys=True)):
        return _result(False, ["PRODUCT_UNSUPPORTED_CLAIM"])
    return _result(True, [])


def validate_package() -> dict[str, Any]:
    if not PACKAGE_ROOT.is_dir() or any(not (PACKAGE_ROOT / name).is_file() for name in REQUIRED_FILES):
        return _result(False, ["PRODUCT_PACKAGE_INCOMPLETE"])
    try:
        value = json.loads((PACKAGE_ROOT / "product.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return _result(False, ["PRODUCT_CONTRACT_INVALID"])
    result = validate_product(value)
    if not result["valid"]:
        return result
    surfaces = (
        ROOT / "docs/commercial/SAEE_AGENT_READINESS_ASSESSMENT_PRODUCT.md",
        ROOT / "docs/commercial/SAEE_AGENT_READINESS_REPORT_TEMPLATE.md",
        ROOT / "docs/commercial/SAEE_AGENT_READINESS_PRODUCTIZATION_ASSET_AUDIT.md",
        ROOT / "examples/commercial-demo/README.md",
    )
    if not all(path.is_file() for path in surfaces):
        return _result(False, ["PRODUCT_SURFACE_MISSING"])
    text = "\n".join((PACKAGE_ROOT / name).read_text(encoding="utf-8") for name in REQUIRED_FILES if name.endswith(".md"))
    text += "\n" + "\n".join(path.read_text(encoding="utf-8") for path in surfaces)
    if find_unsupported_claims(text):
        return _result(False, ["PRODUCT_UNSUPPORTED_CLAIM"])
    if "CONTINUE" not in (ROOT / "docs/commercial/SAEE_AGENT_READINESS_REPORT_TEMPLATE.md").read_text(encoding="utf-8"):
        return _result(False, ["PRODUCT_REPORT_TEMPLATE_INVALID"])
    return _result(True, [])

