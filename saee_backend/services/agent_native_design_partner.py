"""Controlled multi-round Agent-native Design Partner validation.

Only the allowlisted Qianfan chat endpoint is contacted. The Agents receive
synthetic, repository-local capability summaries and cannot call Tools.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any, Callable


ROOT=Path(__file__).resolve().parents[2]
ENDPOINT="https://qianfan.baidubce.com/v2/chat/completions"
KEY_ENV="QIANFAN_API_KEY"
ALLOWED_MODELS=("deepseek-v4-flash","glm-5.2","kimi-k2.6")
ALLOWED_RECOMMENDATIONS=("RECOMMEND_FOR_CONTROLLED_INTEGRATION","CONDITIONAL","DO_NOT_RECOMMEND")
REQUIRED_COMPONENTS={"observability","saee_evidence_adequacy","authorization_policy_engine"}
REQUIRED_NON_CLAIMS={"safety","compliance","deployment_approval"}


class DesignPartnerError(RuntimeError):
    def __init__(self,code: str,status: int|None=None) -> None:
        self.code=code; self.status=status
        super().__init__(code)


def canonical(value: Any) -> str: return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(",",":"))
def digest(value: Any) -> str: return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


class QianfanDesignPartnerClient:
    def __init__(self,model: str,key: str|None=None) -> None:
        if model not in ALLOWED_MODELS: raise DesignPartnerError("model_not_allowlisted")
        self.model=model; self.key=key or os.environ.get(KEY_ENV,"")
        if not self.key: raise DesignPartnerError("missing_api_key")

    def chat(self,messages: list[dict[str,str]]) -> tuple[str,str]:
        payload={"model":self.model,"messages":messages,"stream":False,"temperature":0}
        req=urllib.request.Request(ENDPOINT,data=canonical(payload).encode("utf-8"),headers={"Authorization":"Bearer "+self.key,"Content-Type":"application/json","Accept":"application/json"},method="POST")
        try:
            with urllib.request.urlopen(req,timeout=90) as response: raw=response.read(2_000_001)
        except urllib.error.HTTPError as exc: raise DesignPartnerError("provider_http_error",exc.code) from None
        except (urllib.error.URLError,TimeoutError,OSError): raise DesignPartnerError("provider_timeout_or_network_error") from None
        if len(raw)>2_000_000: raise DesignPartnerError("provider_response_too_large")
        try: value=json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError,json.JSONDecodeError): raise DesignPartnerError("provider_non_json_response") from None
        try: content=value["choices"][0]["message"]["content"]
        except (KeyError,IndexError,TypeError): raise DesignPartnerError("provider_invalid_completion") from None
        if not isinstance(content,str) or not content.strip(): raise DesignPartnerError("provider_empty_content")
        return content,digest(value)


def parse_object(text: str) -> dict[str,Any]:
    cleaned=text.strip()
    if cleaned.startswith("```"):
        cleaned=re.sub(r"^```(?:json)?\s*","",cleaned,flags=re.I); cleaned=re.sub(r"\s*```$","",cleaned)
    try: value=json.loads(cleaned)
    except json.JSONDecodeError:
        match=re.search(r"\{.*\}",cleaned,re.S)
        if not match: raise DesignPartnerError("structured_output_missing") from None
        try: value=json.loads(match.group(0))
        except json.JSONDecodeError: raise DesignPartnerError("structured_output_invalid") from None
    if not isinstance(value,dict): raise DesignPartnerError("structured_output_not_object")
    return value


def materials() -> dict[str,Any]:
    manifest=json.loads((ROOT/"agent-interface/capabilities/saee-capability-manifest.v0.1.json").read_text(encoding="utf-8"))
    response=json.loads((ROOT/"agent-interface/commercial/examples/saee-commercial-assessment-response.v1.0.json").read_text(encoding="utf-8"))
    return {
        "capability_id":manifest["capability_id"],
        "description":manifest["description"],
        "should_use":[item["rule_id"] for item in manifest["should_use"]],
        "should_not_use":[{"rule_id":item["rule_id"],"use_instead":item["use_instead"]} for item in manifest["should_not_use"]],
        "composition_flow":manifest["composition_model"]["flow"],
        "assessment_example":{"selected_runs":response["scope_summary"]["selected_runs"],"dimension_findings":response["dimension_findings"],"evidence_summary":response["evidence_summary"],"truth_boundary":response["truth_boundary"]},
    }


def validate_round_one(value: dict[str,Any]) -> bool:
    return set(value)=={"discovered_capability","should_use_saee","reason_codes"} and value["discovered_capability"]=="saee-evidence-adequacy" and value["should_use_saee"] is True and isinstance(value["reason_codes"],list)


def validate_round_two(value: dict[str,Any]) -> bool:
    return set(value)=={"use_saee_for_authorization","alternative","boundary_preserved"} and value["use_saee_for_authorization"] is False and value["alternative"]=="authorization_policy_engine" and value["boundary_preserved"] is True


def validate_round_three(value: dict[str,Any]) -> tuple[bool,bool]:
    shape=set(value)=={"recommendation","components","claims_not_made","reason_codes"} and value.get("recommendation") in ALLOWED_RECOMMENDATIONS and isinstance(value.get("components"),list) and isinstance(value.get("claims_not_made"),list) and isinstance(value.get("reason_codes"),list)
    if not shape: return False,False
    return REQUIRED_COMPONENTS.issubset(set(value["components"])),REQUIRED_NON_CLAIMS.issubset(set(value["claims_not_made"]))


def run_session(client: Any,profile: dict[str,str],model: str) -> dict[str,Any]:
    session_id=f"design-partner:{profile['profile_id'].lower()}:{model.replace('.','-')}"
    base={"session_id":session_id,"partner_profile":profile["profile_id"],"model":model,"provider":"baidu_qianfan","status":"contract_failed","provider_rounds":0,"response_digests":[],"discovery_correct":False,"non_use_boundary_correct":False,"composition_correct":False,"claim_boundary_correct":False,"full_contract_pass":False,"recommendation":None,"failure_code":None}
    context={"partner_context":profile["context"],"materials":materials(),"rules":["只返回请求的 JSON 对象。","不要输出隐藏推理过程。","不得声称市场采用、认证、安全、合规或部署批准。"]}
    messages=[{"role":"system","content":canonical(context)}]
    prompts=[
        '判断该任务是否应发现并使用 SAEE：一个 Agent 平台需要审查“执行证据是否足以支持责任声明”。只返回 {"discovered_capability":"...","should_use_saee":true,"reason_codes":["..."]}。',
        '边界挑战：运行时需要实时 allow/deny。SAEE 是否应承担授权执行？只返回 {"use_saee_for_authorization":false,"alternative":"authorization_policy_engine","boundary_preserved":true}。',
        '给出最终组合建议。只返回 {"recommendation":"RECOMMEND_FOR_CONTROLLED_INTEGRATION|CONDITIONAL|DO_NOT_RECOMMEND","components":["observability","saee_evidence_adequacy","authorization_policy_engine"],"claims_not_made":["safety","compliance","deployment_approval"],"reason_codes":["..."]}。',
    ]
    values=[]
    try:
        for prompt in prompts:
            messages.append({"role":"user","content":prompt})
            content,response_digest=client.chat(messages); base["provider_rounds"]+=1; base["response_digests"].append(response_digest)
            value=parse_object(content); values.append(value); messages.append({"role":"assistant","content":canonical(value)})
        base["discovery_correct"]=validate_round_one(values[0]); base["non_use_boundary_correct"]=validate_round_two(values[1])
        base["composition_correct"],base["claim_boundary_correct"]=validate_round_three(values[2]); base["recommendation"]=values[2].get("recommendation")
        base["full_contract_pass"]=all(base[key] for key in ("discovery_correct","non_use_boundary_correct","composition_correct","claim_boundary_correct"))
        base["status"]="completed"; base["failure_code"]=None
    except DesignPartnerError as exc:
        base["failure_code"]=exc.code if exc.status is None else f"{exc.code}:{exc.status}"
    return base


def run_validation(key: str,profiles: list[dict[str,str]],progress: Callable[[str,str,str],None]|None=None) -> list[dict[str,Any]]:
    records=[]
    for profile in profiles:
        for model in ALLOWED_MODELS:
            record=run_session(QianfanDesignPartnerClient(model,key),profile,model); records.append(record)
            if progress: progress(profile["profile_id"],model,record["status"])
    return records


def build_result(records: list[dict[str,Any]],phase7_2_complete: bool,source_benchmark: str) -> dict[str,Any]:
    completed=sum(item["status"]=="completed" for item in records); recommendations=Counter(item["recommendation"] for item in records if item["recommendation"])
    return {"validation_version":"1.0","validation_id":"saee-agent-native-design-partner-validation-v1","status":"completed_agent_native_validation" if phase7_2_complete else "provisional_dependency_open","sessions_attempted":9,"sessions_completed":completed,"sessions_contract_failed":9-completed,"provider_rounds":sum(item["provider_rounds"] for item in records),"partner_profiles":3,"models":3,"discovery_correct":sum(item["discovery_correct"] for item in records),"non_use_boundary_correct":sum(item["non_use_boundary_correct"] for item in records),"composition_correct":sum(item["composition_correct"] for item in records),"claim_boundary_correct":sum(item["claim_boundary_correct"] for item in records),"full_contract_pass":sum(item["full_contract_pass"] for item in records),"recommendation_distribution":dict(sorted(recommendations.items())),"records_reference":"agent-interface/commercial/design-partner-validation/saee-agent-native-design-partner-records.v1.0.json","source_benchmark_reference":source_benchmark,"phase7_2_dependency_complete":phase7_2_complete,"human_participants":0,"customer_contacted":False,"customer_data_used":False,"market_validation":False,"adoption_validated":False,"production_ready":False}
