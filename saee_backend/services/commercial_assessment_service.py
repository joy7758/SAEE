"""Local Agent-callable projection of SAEE reliability observations.

The service is Chinese-first and deterministic. It reads checked-in artifacts,
preserves categorical observations, and never issues a score, ranking,
certification, safety/compliance finding, legal judgment, or deployment action.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


ROOT=Path(__file__).resolve().parents[2]
REQUEST_SCHEMA=ROOT/"agent-interface/commercial/saee-commercial-assessment-service-request.schema.v1.0.json"
RESPONSE_SCHEMA=ROOT/"agent-interface/commercial/saee-commercial-assessment-service-response.schema.v1.0.json"
DIMENSIONS=("task_execution_reliability","recovery_reliability","boundary_reliability","evidence_reliability","assessment_availability")
FORBIDDEN=(
    re.compile(r"最佳模型|排名第一|已批准部署|安全认证通过|符合所有法规|法律结论"),
    re.compile(r"\b(?:best model|ranked first|deployment approved|security certified|legally compliant)\b",re.I),
)


class CommercialAssessmentError(ValueError):
    def __init__(self,code: str,detail: str) -> None:
        self.code=code; self.detail=detail
        super().__init__(f"{code}: {detail}")


def _load(path: Path) -> dict[str,Any]:
    try: value=json.loads(path.read_text(encoding="utf-8"))
    except (OSError,json.JSONDecodeError) as exc: raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_INPUT_INVALID",str(path)) from exc
    if not isinstance(value,dict): raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_INPUT_INVALID",str(path))
    return value


def _validate(schema_path: Path,value: dict[str,Any],code: str) -> None:
    errors=sorted(Draft202012Validator(_load(schema_path)).iter_errors(value),key=lambda item:list(item.path))
    if errors:
        path=".".join(str(x) for x in errors[0].path) or "root"
        raise CommercialAssessmentError(code,f"{path}: {errors[0].message}")


def _resolve(ref: str) -> Path:
    path=(ROOT/ref).resolve()
    try: path.relative_to(ROOT.resolve())
    except ValueError as exc: raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_REF_OUTSIDE_ROOT",ref) from exc
    if not path.is_file(): raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_REF_MISSING",ref)
    return path


def _digest(path: Path) -> str: return hashlib.sha256(path.read_bytes()).hexdigest()


def _iter_text(value: Any) -> Iterable[str]:
    if isinstance(value,str): yield value
    elif isinstance(value,dict):
        for item in value.values(): yield from _iter_text(item)
    elif isinstance(value,list):
        for item in value: yield from _iter_text(item)


def _reject_forbidden(value: Any) -> None:
    for text in _iter_text(value):
        if any(pattern.search(text) for pattern in FORBIDDEN):
            raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_FORBIDDEN_CLAIM",text)


def _dimension_finding(name: str,items: list[dict[str,Any]]) -> dict[str,Any]:
    counts=Counter(item["dimensions"][name]["status"] for item in items)
    observed=sum(counts[key] for key in ("OBSERVED_PASS","OBSERVED_PARTIAL","OBSERVED_FAIL"))
    if observed==0:
        assessment="INSUFFICIENT_OBSERVATION"; statement="当前范围没有足够观察支持该维度判断。"
    elif counts["OBSERVED_FAIL"] or counts["OBSERVED_PARTIAL"] or counts["NOT_ASSESSED"]:
        assessment="MIXED_OBSERVATIONS"; statement="当前范围包含通过、部分、失败或未评估状态，必须按场景与证据引用分别审查。"
    else:
        assessment="OBSERVED_WITHIN_SCOPE"; statement="当前受控合成范围内仅观察到合同定义的通过状态；这不是生产可靠性证明。"
    return {"dimension":name,"assessment":assessment,"observed_pass":counts["OBSERVED_PASS"],"observed_partial":counts["OBSERVED_PARTIAL"],"observed_fail":counts["OBSERVED_FAIL"],"not_assessed":counts["NOT_ASSESSED"],"statement_zh":statement}


def generate_commercial_assessment(request: dict[str,Any]) -> dict[str,Any]:
    _validate(REQUEST_SCHEMA,request,"COMMERCIAL_ASSESSMENT_REQUEST_SCHEMA_INVALID")
    refs=[request["benchmark_result_ref"],request["run_manifests_ref"],request["assessments_ref"]]
    paths=[_resolve(ref) for ref in refs]
    benchmark,manifest_payload,assessment_payload=(_load(path) for path in paths)
    manifests=manifest_payload.get("run_manifests"); assessments=assessment_payload.get("assessments")
    if not isinstance(manifests,list) or not isinstance(assessments,list): raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_CORPUS_INVALID","missing lists")
    expected=benchmark.get("combined_runs_attempted",benchmark.get("runs_attempted"))
    if expected!=len(manifests) or len(manifests)!=len(assessments): raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_CORPUS_MISMATCH",str(expected))
    if benchmark.get("ranking_generated") is not False or benchmark.get("production_ready") is not False: raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_SOURCE_BOUNDARY_INVALID","benchmark truth boundary")
    scope=request["scope"]; wanted_agents=set(scope["agent_profiles"]); wanted_scenarios=set(scope["scenario_ids"])
    selected_manifests=[item for item in manifests if item.get("agent") in wanted_agents and item.get("scenario") in wanted_scenarios]
    selected_ids={item["run_id"] for item in selected_manifests}
    selected_assessments=[item for item in assessments if item.get("run_id") in selected_ids]
    if not selected_manifests or len(selected_manifests)!=len(selected_assessments): raise CommercialAssessmentError("COMMERCIAL_ASSESSMENT_SCOPE_EMPTY_OR_UNBOUND","scope")
    failure_counts=Counter(code for item in selected_manifests for code in item.get("failure_type",[]))
    boundaries={"CONTRACT_FAILURE":"合同失败不等于安全失败。","MODEL_RESPONSE_FAILURE":"模型响应失败不等于通用智能能力失败。","TOOL_FAILURE":"合成工具失败只适用于当前场景。","ENVIRONMENT_FAILURE":"环境失败不得归因于模型。","EVIDENCE_FAILURE":"证据不足不等于系统不安全。","AUTHORIZATION_FAILURE":"授权关系失败不自动证明恶意行为。"}
    failure_observations=[{"failure_type":code,"count":count,"interpretation_boundary":boundaries.get(code,"该失败只在当前受控范围内解释。") } for code,count in sorted(failure_counts.items())]
    evidence=Counter(item["evidence_assessment"]["result"] for item in selected_assessments)
    actions=[]
    if failure_counts.get("CONTRACT_FAILURE") or failure_counts.get("MODEL_RESPONSE_FAILURE"): actions.append("检查模型输出、Adapter 与结构化合同之间的兼容性，并保留失败样本。")
    if evidence["FAIL"]: actions.append("针对证据充分性失败项补齐缺失关系；不得把证据不足解释为系统不安全。")
    if evidence["NOT_ASSESSED"]: actions.append("为未评估运行补充可绑定观察和证据对象，或明确维持 NOT_ASSESSED。")
    if any(item["dimensions"]["boundary_reliability"]["status"]=="OBSERVED_FAIL" for item in selected_assessments): actions.append("在隔离环境复核边界失败，并禁止把该响应转成外部动作。")
    actions.append("由独立治理能力决定是否继续测试；本响应不提供部署授权。")
    response={
        "response_version":"1.0",
        "response_id":f"saee:commercial-assessment:{request['request_id']}",
        "request_id":request["request_id"],
        "service_stage":"local_agent_callable_validated_service",
        "scope_summary":{"available_runs":len(manifests),"selected_runs":len(selected_manifests),"agent_profiles":sorted(wanted_agents),"scenario_ids":sorted(wanted_scenarios),"language":"zh-CN"},
        "dimension_findings":[_dimension_finding(name,selected_assessments) for name in DIMENSIONS],
        "failure_observations":failure_observations,
        "evidence_summary":{"supported":evidence["PASS"],"insufficient":evidence["FAIL"],"not_assessed":evidence["NOT_ASSESSED"],"accountability_claim_established":False},
        "review_actions":actions,
        "input_bindings":[{"reference":ref,"sha256":_digest(path)} for ref,path in zip(refs,paths)],
        "limitations":["本服务只读取仓库内受控合成结果。","维度状态是场景约束下的观察，不是总体可靠性概率。","不同场景的 Evidence Adequacy Profile 不可互换。","Provider、模型、Adapter 与场景因素仍可能混杂。","输出不是安全或合规认证、法律判断、模型排名或部署批准。","当前未使用客户数据，也未完成外部 Agent Design Partner 验证。"],
        "truth_boundary":{"customer_data_used":False,"commercial_delivery_completed":False,"customer_validated":False,"external_validation_completed":False,"overall_score_generated":False,"ranking_generated":False,"winner_selected":False,"security_certification":False,"compliance_determination":False,"legal_judgment":False,"deployment_authorized":False,"production_ready":False},
    }
    _validate(RESPONSE_SCHEMA,response,"COMMERCIAL_ASSESSMENT_RESPONSE_SCHEMA_INVALID")
    _reject_forbidden(response)
    return response


def generate_commercial_assessment_path(path: Path) -> dict[str,Any]: return generate_commercial_assessment(_load(path))
