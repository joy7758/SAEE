"""Generate a bounded human-readable SAEE evidence review report from synthetic adequacy results."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
REPORT_SCHEMA_PATH = ROOT / "agent-interface/commercial/saee-evidence-review-report.schema.json"
REPORT_VERSION = "0.1.0"

CASE_KEYS = {
    "saee_synthetic_review_case_v0_1",
    "case_id",
    "report_id",
    "case_reference",
    "review_scope",
    "observation_references",
    "evidence_package_references",
    "adequacy_results",
    "limitations",
    "truth_boundary",
}

CASE_TRUTH_BOUNDARY = {
    "synthetic_only": True,
    "customer_data_used": False,
    "external_validation_completed": False,
    "compliance_certification": False,
    "legal_judgment": False,
    "automated_decision": False,
    "deployment_authorized": False,
    "commercial_service_delivered": False,
    "production_ready": False,
}

ASSESSMENT_MAP = {
    "PASS": "SUPPORTED",
    "FAIL": "INSUFFICIENT_EVIDENCE",
    "UNKNOWN": "UNKNOWN",
}

STATEMENTS = {
    "SUPPORTED": (
        "Current evidence supports the defined accountability claim within the stated synthetic review scope.",
        "现有证据在本次合成审查范围内支持该责任声明。",
    ),
    "INSUFFICIENT_EVIDENCE": (
        "Current evidence is insufficient to support the defined accountability claim.",
        "现有证据不足以支持该责任声明。证据不足不等于系统不安全。",
    ),
    "UNKNOWN": (
        "The available evaluation output does not establish whether the defined accountability claim is supported.",
        "现有评估输出无法确定该责任声明是否得到支持。",
    ),
}

DEFAULT_LIMITATIONS = (
    "This is a local synthetic report prototype, not a customer deliverable or commercial service.",
    "Evidence adequacy assessment is not compliance certification, legal judgment, or security certification.",
    "An evidence finding does not determine overall system safety or authorize deployment.",
    "The report does not independently verify evidence authenticity, identity, authorization, or event occurrence.",
)

FORBIDDEN_AFFIRMATIVE_PATTERNS = (
    re.compile(r"\b(?:the\s+)?system\s+(?:is|has\s+been)\s+(?:safe|unsafe|compliant|approved|certified)\b", re.IGNORECASE),
    re.compile(r"\b(?:certification|approval)\s+(?:granted|confirmed|passed)\b", re.IGNORECASE),
    re.compile(r"系统(?:是|已被|已经)(?:安全|不安全|合规|批准|认证)", re.IGNORECASE),
    re.compile(r"(?:认证|批准)(?:已经)?通过", re.IGNORECASE),
)


class ReviewReportError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise ReviewReportError(code, detail)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_bytes())
    require(isinstance(value, dict), "REVIEW_INPUT_INVALID", "root must be object")
    return value


def resolve_local_ref(ref: str) -> Path:
    path = (ROOT / ref).resolve()
    try:
        path.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise ReviewReportError("REVIEW_REFERENCE_OUTSIDE_ROOT", ref) from exc
    require(path.is_file(), "REVIEW_REFERENCE_MISSING", ref)
    return path


def iter_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from iter_text(child)
    elif isinstance(value, list):
        for child in value:
            yield from iter_text(child)


def validate_no_forbidden_claims(value: Any) -> None:
    for text in iter_text(value):
        for pattern in FORBIDDEN_AFFIRMATIVE_PATTERNS:
            require(pattern.search(text) is None, "REVIEW_FORBIDDEN_CLAIM", text)


def validate_case(case: dict[str, Any]) -> None:
    require(set(case) == CASE_KEYS, "REVIEW_CASE_SHAPE_INVALID", "unexpected or missing root field")
    require(case["saee_synthetic_review_case_v0_1"] is True, "REVIEW_CASE_MARKER_INVALID", "marker")
    require(case["truth_boundary"] == CASE_TRUTH_BOUNDARY, "REVIEW_CASE_BOUNDARY_INVALID", "truth_boundary")
    scope = case["review_scope"]
    require(
        isinstance(scope, dict)
        and scope.get("synthetic") is True
        and scope.get("customer_data_used") is False
        and scope.get("compliance_review") is False
        and scope.get("production_assessment") is False,
        "REVIEW_SCOPE_INVALID",
        "review_scope",
    )
    resolve_local_ref(case["case_reference"])
    observation_refs = case["observation_references"]
    evidence_refs = case["evidence_package_references"]
    require(isinstance(observation_refs, list) and observation_refs, "REVIEW_OBSERVATION_REFERENCE_MISSING", "observation_references")
    require(isinstance(evidence_refs, list) and evidence_refs, "REVIEW_EVIDENCE_REFERENCE_MISSING", "evidence_package_references")
    for ref in [*observation_refs, *evidence_refs]:
        resolve_local_ref(ref)
    evidence_set = set(evidence_refs)
    results = case["adequacy_results"]
    require(isinstance(results, list) and results, "REVIEW_ADEQUACY_RESULTS_MISSING", "adequacy_results")
    for result in results:
        require(
            isinstance(result, dict)
            and set(result)
            == {
                "claim_type",
                "result",
                "adequacy_profile_ref",
                "supporting_evidence_refs",
                "missing_requirements",
                "reason_codes",
            },
            "REVIEW_ADEQUACY_RESULT_SHAPE_INVALID",
            str(result),
        )
        require(result["result"] in ASSESSMENT_MAP, "REVIEW_ADEQUACY_RESULT_UNKNOWN", result["result"])
        resolve_local_ref(result["adequacy_profile_ref"])
        require(set(result["supporting_evidence_refs"]).issubset(evidence_set), "REVIEW_EVIDENCE_REFERENCE_UNDECLARED", result["claim_type"])
        if result["result"] == "PASS":
            require(not result["missing_requirements"], "REVIEW_PASS_HAS_MISSING_EVIDENCE", result["claim_type"])
        if result["result"] == "FAIL":
            require(bool(result["missing_requirements"]), "REVIEW_FAIL_WITHOUT_MISSING_EVIDENCE", result["claim_type"])
    require(isinstance(case["limitations"], list) and len(case["limitations"]) >= 4, "REVIEW_LIMITATIONS_MISSING", "limitations")
    validate_no_forbidden_claims(case["limitations"])


def validate_report(report: dict[str, Any]) -> None:
    schema = load_json(REPORT_SCHEMA_PATH)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(report), key=lambda item: list(item.path))
    if errors:
        path = ".".join(str(part) for part in errors[0].path) or "root"
        raise ReviewReportError("REVIEW_REPORT_SCHEMA_INVALID", f"{path}: {errors[0].message}")
    text_surface = {
        "review_scope": report["review_scope"],
        "claim_assessments": report["claim_assessments"],
        "limitations": report["limitations"],
    }
    validate_no_forbidden_claims(text_surface)


def generate_review_report(case: dict[str, Any]) -> dict[str, Any]:
    validate_case(case)
    assessments: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    supporting_refs: set[str] = set()

    for result in case["adequacy_results"]:
        assessment = ASSESSMENT_MAP[result["result"]]
        statement_en, statement_zh = STATEMENTS[assessment]
        supporting = sorted(set(result["supporting_evidence_refs"]))
        supporting_refs.update(supporting)
        reasons = sorted(set(result["reason_codes"]))
        missing_requirements = sorted(set(result["missing_requirements"]))
        assessments.append(
            {
                "claim_type": result["claim_type"],
                "assessment": assessment,
                "assessment_statement": statement_en,
                "assessment_statement_zh": statement_zh,
                "adequacy_profile_ref": result["adequacy_profile_ref"],
                "supporting_evidence": supporting,
                "missing_requirements": missing_requirements,
                "reason_codes": reasons,
            }
        )
        for requirement in missing_requirements:
            missing.append(
                {
                    "claim_type": result["claim_type"],
                    "requirement": requirement,
                    "reason_codes": reasons,
                }
            )

    limitations = list(dict.fromkeys([*case["limitations"], *DEFAULT_LIMITATIONS]))
    report = {
        "saee_evidence_review_report_v0_1": True,
        "report_id": case["report_id"],
        "report_version": REPORT_VERSION,
        "case_reference": case["case_reference"],
        "review_scope": case["review_scope"],
        "claim_assessments": assessments,
        "evidence_summary": {
            "observation_references": sorted(set(case["observation_references"])),
            "evidence_package_references": sorted(set(case["evidence_package_references"])),
            "supporting_evidence_count": len(supporting_refs),
            "synthetic_only": True,
        },
        "missing_evidence": sorted(missing, key=lambda item: (item["claim_type"], item["requirement"])),
        "boundary_statement": {
            "english": "This synthetic evidence assessment is not compliance certification, a safety determination, legal judgment, production approval, or customer deliverable.",
            "chinese": "本合成证据评估不是合规认证、安全结论、法律判断、生产批准或客户交付物。",
            "evidence_assessment_is_compliance_certification": False,
            "evidence_insufficient_means_system_unsafe": False,
            "finding_is_automated_decision": False,
            "synthetic_report_is_customer_deliverable": False,
            "production_approval": False,
        },
        "limitations": limitations,
        "truth_boundary": {
            "synthetic_report": True,
            "customer_data_used": False,
            "external_validation_completed": False,
            "security_certification_claimed": False,
            "regulatory_compliance_claimed": False,
            "legal_judgment_made": False,
            "automated_decision_made": False,
            "deployment_authorized": False,
            "customer_accepted": False,
            "commercial_service_delivered": False,
            "production_ready": False,
        },
    }
    validate_report(report)
    return report


def generate_review_report_path(path: Path) -> dict[str, Any]:
    return generate_review_report(load_json(path))


def _markdown_cell(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def render_review_report_markdown(report: dict[str, Any]) -> str:
    validate_report(report)
    lines = [
        "# SAEE Evidence Adequacy Review Report",
        "",
        "> 本报告是本地合成的证据充分性审查原型，不是客户报告、认证结论或部署决定。",
        "",
        "## Review Scope",
        "",
        f"- 场景：{report['review_scope']['scenario']}",
        f"- 范围：{report['review_scope']['scope_description']}",
        "- 数据：仅使用仓库内合成资料；未使用客户数据。",
        "",
        "## Evaluated Claims",
        "",
        "| 责任声明 | 评估 | 客户可读说明 |",
        "|---|---|---|",
    ]
    for item in report["claim_assessments"]:
        lines.append(
            f"| `{_markdown_cell(item['claim_type'])}` | `{item['assessment']}` | {_markdown_cell(item['assessment_statement_zh'])} |"
        )

    lines.extend(["", "## Evidence Supporting Assessment", ""])
    for item in report["claim_assessments"]:
        lines.append(f"### `{item['claim_type']}`")
        lines.append("")
        lines.append(f"- Evidence Adequacy Profile：`{item['adequacy_profile_ref']}`")
        if item["supporting_evidence"]:
            for ref in item["supporting_evidence"]:
                lines.append(f"- 证据引用：`{ref}`")
        else:
            lines.append("- 证据引用：无。")
        lines.append("")

    lines.extend(["## Missing Evidence", ""])
    if report["missing_evidence"]:
        for item in report["missing_evidence"]:
            codes = ", ".join(f"`{code}`" for code in item["reason_codes"]) or "无原因码"
            lines.append(f"- `{item['claim_type']}` 缺少 `{item['requirement']}`；原因码：{codes}。")
    else:
        lines.append("- 本次定义的责任声明没有记录缺失证据。")
    lines.extend(
        [
            "",
            "> Current evidence is insufficient to support the defined accountability claim.",
            "",
            "这句话只表示证据不足，不能解释为系统不安全。",
            "",
            "## Boundary Statement",
            "",
            f"> {report['boundary_statement']['english']}",
            "",
            f"> {report['boundary_statement']['chinese']}",
            "",
            "Review Finding 不会自动生成 Risk Decision、部署批准或合规结论。",
            "",
            "## Limitations",
            "",
        ]
    )
    for limitation in report["limitations"]:
        lines.append(f"- {limitation}")
    lines.append("")
    return "\n".join(lines)
