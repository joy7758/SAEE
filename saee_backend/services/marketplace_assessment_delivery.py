"""Prepare and finalize a bounded Alibaba Cloud Marketplace assessment delivery.

The bridge accepts normalized, authorized, sanitized metadata for exactly one
workflow and one scenario. It delegates assessment to the existing
``saee.evaluate_agent_run`` capability, generates deterministic JSON and
Chinese Markdown artifacts, and records human-review and local-source-deletion
states. It never executes an Agent, opens a URL, contacts a Marketplace, or
authorizes deployment.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator

from saee_backend.services.baidu_agent_readiness_service import evaluate_agent_run


ROOT = Path(__file__).resolve().parents[2]
INTAKE_SCHEMA = ROOT / "agent-interface/commercial/saee-marketplace-assessment-intake.schema.v0.1.json"
BUNDLE_SCHEMA = ROOT / "agent-interface/commercial/saee-marketplace-assessment-bundle.schema.v0.1.json"
RECEIPT_SCHEMA = ROOT / "agent-interface/commercial/saee-marketplace-delivery-receipt.schema.v0.1.json"

BUNDLE_FILENAME = "assessment-bundle.json"
REPORT_FILENAME = "assessment-report.zh-CN.md"
PREPARED_RECEIPT_FILENAME = "delivery-receipt.prepared.json"
FINAL_RECEIPT_FILENAME = "delivery-receipt.final.json"

READINESS_ZH = {
    "continue": "当前必需证据覆盖完整；仍需由负责人决定是否继续。",
    "conditional": "当前证据基本覆盖，但存在必须人工复核的缺口。",
    "replan": "当前证据缺口明显，建议补齐材料或调整方案后再评估。",
    "stop": "当前证据不足，建议停止高影响动作并先补齐关键证据。",
}
EVIDENCE_ZH = {
    "TEST_RESULT": "测试结果",
    "ROLLBACK_PLAN": "回滚方案",
    "PERMISSION_BOUNDARY": "权限边界",
    "HUMAN_APPROVAL": "人工批准记录",
}
RISK_ZH = {
    "insufficient_test_evidence": "测试证据不足",
    "missing_recovery_plan": "缺少恢复或回滚方案",
    "unbounded_external_api_permission": "外部接口权限边界不完整",
    "missing_human_approval_checkpoint": "缺少人工批准检查点",
}
REPORT_LIMITATIONS = [
    "覆盖率只表示必需证据是否存在，不是可靠性或安全概率。",
    "SAEE 不验证所提交摘要、轨迹或证据引用的真实性。",
    "本结果不是安全认证、合规结论或法律意见。",
    "本结果不授权部署、权限扩大、付款或其他外部动作。",
    "本流程只处理经提交方授权并脱敏的规范化摘要，不处理原始客户内容。",
    "交付前必须完成人工边界复核，并删除本地接入源文件。",
]

_SOURCE_REF = re.compile(r"^ref:[A-Za-z0-9._:-]{1,120}$")
_UNSAFE_TEXT = (
    re.compile(r"(?:https?|file|ssh|git)://", re.I),
    re.compile(r"(?:^|\s)(?:\.\./|/Users/|/home/|[A-Za-z]:\\)"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"\b(?:sk|ak)-[A-Za-z0-9_-]{12,}\b", re.I),
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
)
_FORBIDDEN_AFFIRMATIVE = (
    re.compile(r"已通过安全认证"),
    re.compile(r"已批准部署"),
    re.compile(r"符合所有法规"),
    re.compile(r"绝对安全"),
    re.compile(r"\bproduction[-_ ]ready\b", re.I),
)


class MarketplaceDeliveryError(ValueError):
    """Typed fail-closed error for Marketplace delivery preparation."""

    def __init__(self, code: str, detail: str) -> None:
        self.code = code
        self.detail = detail
        super().__init__(f"{code}: {detail}")


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_json(value: Any) -> str:
    return sha256_bytes(canonical_json(value).encode("utf-8"))


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MarketplaceDeliveryError("MARKETPLACE_INPUT_INVALID", str(path)) from exc
    if not isinstance(value, dict):
        raise MarketplaceDeliveryError("MARKETPLACE_INPUT_INVALID", "root must be an object")
    return value


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _schema_without_external_ref(path: Path, field: str) -> dict[str, Any]:
    schema = _load_schema(path)
    schema["properties"][field] = {"type": "object"}
    return schema


def _validate(schema: dict[str, Any], value: dict[str, Any], code: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(value), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        pointer = "/" + "/".join(str(part) for part in first.absolute_path)
        raise MarketplaceDeliveryError(code, f"{pointer}: {first.message}")


def _iter_text(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _iter_text(child)
    elif isinstance(value, list):
        for child in value:
            yield from _iter_text(child)


def _screen_normalized_content(readiness_request: dict[str, Any]) -> None:
    for value in [readiness_request["task"], *[item["summary"] for item in readiness_request["trace"]["events"]]]:
        if any(pattern.search(value) for pattern in _UNSAFE_TEXT):
            raise MarketplaceDeliveryError("MARKETPLACE_CONTENT_SCREEN_REJECTED", "task or event summary")
    for item in readiness_request["evidence"]:
        source_ref = item["source_ref"]
        if source_ref is not None and not _SOURCE_REF.fullmatch(source_ref):
            raise MarketplaceDeliveryError("MARKETPLACE_EVIDENCE_REF_REJECTED", item["evidence_id"])


def _reject_forbidden_claims(value: Any) -> None:
    for text in _iter_text(value):
        if any(pattern.search(text) for pattern in _FORBIDDEN_AFFIRMATIVE):
            raise MarketplaceDeliveryError("MARKETPLACE_FORBIDDEN_CLAIM", text)


def validate_intake(intake: dict[str, Any]) -> None:
    _validate(
        _schema_without_external_ref(INTAKE_SCHEMA, "readiness_request"),
        intake,
        "MARKETPLACE_INTAKE_SCHEMA_INVALID",
    )
    request = intake["readiness_request"]
    try:
        evaluate_agent_run(request)
    except ValueError as exc:
        raise MarketplaceDeliveryError("MARKETPLACE_READINESS_REQUEST_INVALID", str(exc)) from exc
    _screen_normalized_content(request)


def generate_assessment_bundle(intake: dict[str, Any]) -> dict[str, Any]:
    """Generate a deterministic assessment bundle without writing files."""

    validate_intake(intake)
    result = evaluate_agent_run(intake["readiness_request"])
    scope = intake["scope"]
    bundle = {
        "saee_marketplace_assessment_bundle_v0_1": True,
        "bundle_version": "0.1.0",
        "assessment_id": intake["assessment_id"],
        "order_ref": intake["order_ref"],
        "scope": {
            "workflow_id": scope["workflow_id"],
            "scenario_id": scope["scenario_id"],
            "language": scope["language"],
        },
        "operation": "saee.evaluate_agent_run",
        "assessment_result": result,
        "customer_summary": {
            "readiness_zh": READINESS_ZH[result["readiness"]],
            "recommendation": result["recommendation"],
            "coverage_score": result["score"],
            "score_semantics_zh": "必需证据覆盖百分比，不是可靠性或安全概率",
            "missing_evidence": list(result["missing_evidence"]),
            "risk_signals": list(result["risks"]),
        },
        "input_bindings": {
            "intake_sha256": sha256_json(intake),
            "readiness_request_sha256": sha256_json(intake["readiness_request"]),
        },
        "limitations": list(REPORT_LIMITATIONS),
        "truth_boundary": {
            "normalized_customer_metadata_used": True,
            "raw_customer_data_used": False,
            "source_authorization_attested": True,
            "sanitization_attested": True,
            "content_screen_passed": True,
            "pii_absence_verified_by_saee": False,
            "trace_authenticity_verified": False,
            "human_delivery_required": True,
            "customer_accepted": False,
            "commercial_service_delivered": False,
            "customer_validated": False,
            "deployment_authorized": False,
            "production_ready": False,
        },
    }
    _validate(
        _schema_without_external_ref(BUNDLE_SCHEMA, "assessment_result"),
        bundle,
        "MARKETPLACE_BUNDLE_SCHEMA_INVALID",
    )
    _reject_forbidden_claims(bundle)
    return bundle


def render_assessment_report(bundle: dict[str, Any]) -> str:
    """Render the customer-readable Chinese report from a validated bundle."""

    _validate(
        _schema_without_external_ref(BUNDLE_SCHEMA, "assessment_result"),
        bundle,
        "MARKETPLACE_BUNDLE_SCHEMA_INVALID",
    )
    result = bundle["assessment_result"]
    scope = bundle["scope"]
    lines = [
        "# SAEE AI 智能体上线前可靠性评估报告",
        "",
        f"- 评估编号：`{bundle['assessment_id']}`",
        f"- 订单引用：`{bundle['order_ref']}`",
        f"- 工作流：`{scope['workflow_id']}`",
        f"- 场景：`{scope['scenario_id']}`",
        f"- 评估操作：`{bundle['operation']}`",
        "",
        "## 结论摘要",
        "",
        f"- 当前状态：{bundle['customer_summary']['readiness_zh']}",
        f"- 建议标签：`{result['recommendation']}`",
        f"- 必需证据覆盖率：`{result['score']}%`",
        "- 分数含义：必需证据覆盖百分比，不是可靠性或安全概率。",
        "",
        "## 证据检查",
        "",
        "| 必需证据 | 状态 |",
        "|---|---|",
    ]
    present = set(result["present_evidence"])
    for item in result["required_evidence"]:
        lines.append(f"| {EVIDENCE_ZH.get(item, item)} (`{item}`) | {'已提供' if item in present else '缺失'} |")
    lines.extend(["", "## 缺口与风险", ""])
    if result["missing_evidence"]:
        for item in result["missing_evidence"]:
            lines.append(f"- 缺失证据：{EVIDENCE_ZH.get(item, item)} (`{item}`)。")
    else:
        lines.append("- 当前规则要求的证据类型均已声明提供。")
    if result["risks"]:
        for item in result["risks"]:
            lines.append(f"- 风险信号：{RISK_ZH.get(item, item)} (`{item}`)。")
    else:
        lines.append("- 当前规则未生成额外风险信号；这不表示系统安全性已经得到证明。")
    lines.extend(["", "## 适用范围与限制", ""])
    for limitation in bundle["limitations"]:
        lines.append(f"- {limitation}")
    lines.extend(
        [
            "",
            "## 输入绑定",
            "",
            f"- 接入请求 SHA-256：`{bundle['input_bindings']['intake_sha256']}`",
            f"- 评估请求 SHA-256：`{bundle['input_bindings']['readiness_request_sha256']}`",
            "",
            "> 本报告是上线前证据准备的辅助材料，不是安全认证、合规结论、法律意见或部署批准。",
            "",
        ]
    )
    report = "\n".join(lines)
    _reject_forbidden_claims(report)
    return report


def _write_new(path: Path, value: str) -> None:
    if path.exists():
        raise MarketplaceDeliveryError("MARKETPLACE_OUTPUT_EXISTS", path.name)
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


def _receipt_id(source_sha256: str) -> str:
    return f"saee-marketplace-delivery-{source_sha256[:16]}"


def _validate_receipt(receipt: dict[str, Any]) -> None:
    _validate(_load_schema(RECEIPT_SCHEMA), receipt, "MARKETPLACE_RECEIPT_SCHEMA_INVALID")


def prepare_delivery(source_path: Path, output_dir: Path) -> dict[str, Any]:
    """Prepare artifacts for human review; no source deletion or delivery occurs."""

    if source_path.is_symlink() or not source_path.is_file():
        raise MarketplaceDeliveryError("MARKETPLACE_SOURCE_FILE_INVALID", source_path.name)
    source_bytes = source_path.read_bytes()
    source_sha256 = sha256_bytes(source_bytes)
    intake = load_json(source_path)
    bundle = generate_assessment_bundle(intake)
    bundle_text = json.dumps(bundle, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    report_text = render_assessment_report(bundle)
    output_dir.mkdir(parents=True, exist_ok=True)
    bundle_path = output_dir / BUNDLE_FILENAME
    report_path = output_dir / REPORT_FILENAME
    receipt_path = output_dir / PREPARED_RECEIPT_FILENAME
    receipt = {
        "saee_marketplace_delivery_receipt_v0_1": True,
        "receipt_version": "0.1.0",
        "receipt_id": _receipt_id(source_sha256),
        "stage": "prepared_for_human_review",
        "assessment_id": intake["assessment_id"],
        "order_ref": intake["order_ref"],
        "artifacts": {
            "intake_sha256": source_sha256,
            "bundle_filename": BUNDLE_FILENAME,
            "bundle_sha256": sha256_bytes(bundle_text.encode("utf-8")),
            "report_filename": REPORT_FILENAME,
            "report_sha256": sha256_bytes(report_text.encode("utf-8")),
        },
        "human_boundary_review": {"required": True, "completed": False, "reviewer_role_token": None},
        "local_source_deletion": {"required": True, "completed": False, "deleted_input_sha256": None, "source_path_recorded": False},
        "marketplace_delivery": {"ready": False, "completed": False, "customer_accepted": False},
        "truth_boundary": {
            "commercial_service_delivered": False,
            "customer_validated": False,
            "marketplace_product_listed": False,
            "production_ready": False,
        },
    }
    _validate_receipt(receipt)
    _write_new(bundle_path, bundle_text)
    _write_new(report_path, report_text)
    _write_new(receipt_path, json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return receipt


def _digest_file(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise MarketplaceDeliveryError("MARKETPLACE_ARTIFACT_INVALID", path.name)
    return sha256_bytes(path.read_bytes())


def _within_intake_root(source_path: Path, intake_root: Path) -> Path:
    if source_path.is_symlink() or not source_path.is_file():
        raise MarketplaceDeliveryError("MARKETPLACE_SOURCE_FILE_INVALID", source_path.name)
    root = intake_root.resolve(strict=True)
    source = source_path.resolve(strict=True)
    try:
        source.relative_to(root)
    except ValueError as exc:
        raise MarketplaceDeliveryError("MARKETPLACE_SOURCE_OUTSIDE_INTAKE_ROOT", source_path.name) from exc
    return source


def finalize_delivery(
    prepared_receipt_path: Path,
    source_path: Path,
    intake_root: Path,
    reviewer_role_token: str,
) -> dict[str, Any]:
    """Validate artifacts, record human review, and delete the local intake file."""

    if not re.fullmatch(r"[A-Za-z0-9._-]{1,80}", reviewer_role_token):
        raise MarketplaceDeliveryError("MARKETPLACE_REVIEWER_ROLE_INVALID", reviewer_role_token)
    prepared = load_json(prepared_receipt_path)
    _validate_receipt(prepared)
    if prepared["stage"] != "prepared_for_human_review":
        raise MarketplaceDeliveryError("MARKETPLACE_RECEIPT_STAGE_INVALID", prepared["stage"])
    output_dir = prepared_receipt_path.parent.resolve()
    artifacts = prepared["artifacts"]
    bundle_path = output_dir / artifacts["bundle_filename"]
    report_path = output_dir / artifacts["report_filename"]
    if _digest_file(bundle_path) != artifacts["bundle_sha256"]:
        raise MarketplaceDeliveryError("MARKETPLACE_BUNDLE_DIGEST_DRIFT", bundle_path.name)
    if _digest_file(report_path) != artifacts["report_sha256"]:
        raise MarketplaceDeliveryError("MARKETPLACE_REPORT_DIGEST_DRIFT", report_path.name)
    source = _within_intake_root(source_path, intake_root)
    source_sha256 = _digest_file(source)
    if source_sha256 != artifacts["intake_sha256"]:
        raise MarketplaceDeliveryError("MARKETPLACE_SOURCE_DIGEST_DRIFT", source.name)
    final_path = output_dir / FINAL_RECEIPT_FILENAME
    if final_path.exists():
        raise MarketplaceDeliveryError("MARKETPLACE_OUTPUT_EXISTS", final_path.name)
    source.unlink()
    if source.exists():
        raise MarketplaceDeliveryError("MARKETPLACE_SOURCE_DELETION_FAILED", source.name)
    final = {
        **prepared,
        "stage": "reviewed_ready_for_marketplace_delivery",
        "human_boundary_review": {"required": True, "completed": True, "reviewer_role_token": reviewer_role_token},
        "local_source_deletion": {"required": True, "completed": True, "deleted_input_sha256": source_sha256, "source_path_recorded": False},
        "marketplace_delivery": {"ready": True, "completed": False, "customer_accepted": False},
    }
    _validate_receipt(final)
    _write_new(final_path, json.dumps(final, ensure_ascii=False, sort_keys=True, indent=2) + "\n")
    return final
