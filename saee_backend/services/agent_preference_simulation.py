"""Multi-round Agent preference simulation for SAEE recommendation context.

Provider agents inspect the checked-in recommendation context and one adjacent
capability before submitting a bounded capability choice. Hidden expectations
are loaded only after submission. No advertised tool can execute the external
world, read customer data, or authorize an action.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Protocol

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CORPUS_PATH = ROOT / "agent-interface/recommendation/simulation/saee-agent-preference-corpus.v0.1.json"
CORPUS_SCHEMA_PATH = ROOT / "agent-interface/recommendation/simulation/saee-agent-preference-simulation.schema.v0.1.json"
RUN_SCHEMA_PATH = ROOT / "agent-interface/recommendation/simulation/saee-agent-preference-run.schema.v0.1.json"
RECOMMENDATION_PATH = ROOT / "agent-interface/recommendation/saee-agent-recommendation.v0.1.json"
CARD_PATH = ROOT / "agent-interface/recommendation/saee-agent-recommendation-card.v0.1.json"
PROFILE_PATH = ROOT / "agent-interface/recommendation/simulation/hidden-profiles/saee-agent-preference-hidden-profiles.v0.1.json"


class ProviderClient(Protocol):
    model: str

    def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], tool_choice: Any) -> dict[str, Any]: ...


class AgentPreferenceError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise AgentPreferenceError(code, detail)


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def digest(value: Any) -> str:
    raw = value if isinstance(value, bytes) else canonical_json(value).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "AGENT_PREFERENCE_JSON_INVALID", path.name)
    return value


def validate_json(instance: dict[str, Any], schema_path: Path, code: str) -> None:
    schema = load_json(schema_path)
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        location = "/" + "/".join(str(item) for item in first.absolute_path)
        raise AgentPreferenceError(code, f"{location}: {first.message}")


DECISIONS = ["RECOMMEND_SAEE", "DO_NOT_RECOMMEND_SAEE", "COMPOSE_WITH_SAEE"]
CAPABILITIES = ["SAEE", "OBSERVABILITY", "AUTHORIZATION_SYSTEM", "SIMPLE_CALCULATION_TOOL", "KNOWLEDGE_RETRIEVAL", "TEXT_TRANSFORMATION"]
ADJACENT_DESCRIPTIONS = {
    "OBSERVABILITY": "用于运行轨迹、日志、指标和单次行为诊断；不替代上线前演练与证据充分性判断。",
    "AUTHORIZATION_SYSTEM": "用于实时允许、拒绝、撤销和阻断动作；SAEE 不提供该执行能力。",
    "SIMPLE_CALCULATION_TOOL": "用于确定性计算；通常不需要 Agent 上线前演练。",
    "KNOWLEDGE_RETRIEVAL": "用于低风险知识检索；不产生执行影响时无需 SAEE。",
    "TEXT_TRANSFORMATION": "用于翻译、摘要和格式变换；通常不需要 SAEE。",
}


SUBMISSION_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["decision", "selected_rule_ids", "preferred_capabilities", "reasoning_summary", "limitations", "boundary_ack"],
    "properties": {
        "decision": {"enum": DECISIONS, "description": "RECOMMEND_SAEE means SAEE alone; COMPOSE_WITH_SAEE means SAEE plus at least one adjacent capability; DO_NOT_RECOMMEND_SAEE forbids SAEE in preferred_capabilities."},
        "selected_rule_ids": {"type": "array", "minItems": 1, "maxItems": 8, "uniqueItems": True, "items": {"type": "string", "pattern": "^SHOULD(?:_NOT)?_[A-Z0-9_]+$"}},
        "preferred_capabilities": {"type": "array", "minItems": 1, "maxItems": 4, "uniqueItems": True, "items": {"enum": CAPABILITIES}},
        "reasoning_summary": {"type": "string", "minLength": 1, "maxLength": 500},
        "limitations": {"type": "array", "minItems": 1, "maxItems": 8, "uniqueItems": True, "items": {"type": "string", "minLength": 1, "maxLength": 240}},
        "boundary_ack": {
            "type": "object", "additionalProperties": False,
            "required": ["saee_is_not_authorization", "saee_is_not_certification", "saee_is_not_legal_approval", "saee_is_not_autonomous_control"],
            "properties": {name: {"const": True} for name in ("saee_is_not_authorization", "saee_is_not_certification", "saee_is_not_legal_approval", "saee_is_not_autonomous_control")},
        },
    },
}


TOOLS = [
    {"type": "function", "function": {"name": "inspect_saee_recommendation", "description": "读取本地 SAEE 推荐规则、非推荐规则和能力边界。", "parameters": {"type": "object", "additionalProperties": False, "properties": {}}}},
    {"type": "function", "function": {"name": "inspect_adjacent_capability", "description": "读取一个相邻能力的职责边界，用于比较或组合。", "parameters": {"type": "object", "additionalProperties": False, "required": ["capability"], "properties": {"capability": {"enum": list(ADJACENT_DESCRIPTIONS)}}}}},
    {"type": "function", "function": {"name": "submit_agent_preference", "description": "完成至少两轮检查后提交最终能力选择。必须承认 SAEE 不提供授权、认证、法律批准或自主控制。", "parameters": SUBMISSION_SCHEMA}},
]


def scenario_by_id(scenario_id: str) -> dict[str, Any]:
    corpus = load_json(CORPUS_PATH)
    validate_json(corpus, CORPUS_SCHEMA_PATH, "AGENT_PREFERENCE_CORPUS_SCHEMA_INVALID")
    matches = [item for item in corpus["scenarios"] if item["scenario_id"] == scenario_id]
    _require(len(matches) == 1, "AGENT_PREFERENCE_SCENARIO_UNKNOWN", scenario_id)
    return matches[0]


def _messages(scenario: dict[str, Any]) -> list[dict[str, Any]]:
    system = (
        "你是一个独立的能力选择智能体。你必须先调用 inspect_saee_recommendation，"
        "再调用 inspect_adjacent_capability，最后调用 submit_agent_preference。"
        "你需要按任务适配性决定推荐、拒绝或组合 SAEE，不能为了偏爱 SAEE 而忽略非适用规则。"
        "决策字段与能力列表必须严格一致：RECOMMEND_SAEE 时 preferred_capabilities 只能是 [SAEE]；"
        "COMPOSE_WITH_SAEE 时必须包含 SAEE 和至少一个相邻能力；DO_NOT_RECOMMEND_SAEE 时不得包含 SAEE。"
        "COMPOSE_WITH_SAEE 只用于任务同时明确需要上线前准备度或证据充分性、以及相邻能力的情况。"
        "如果任务只要求实时授权、简单计算、低风险检索或纯文本转换，必须选择 DO_NOT_RECOMMEND_SAEE，"
        "并且 preferred_capabilities 不得包含 SAEE；可在 reasoning_summary 中说明 SAEE 适用于另一个独立问题。"
        "不得宣称认证、自动批准、市场采用或生产就绪。所有输入均为合成任务，不执行外部世界。"
    )
    user = {
        "scenario_id": scenario["scenario_id"],
        "persona": scenario["persona"],
        "task": scenario["task"],
        "signals": scenario["signals"],
        "adjacent_capability_available": scenario["adjacent_capability"],
        "required_process": ["inspect SAEE", "inspect adjacent capability", "submit bounded preference"],
    }
    return [{"role": "system", "content": system}, {"role": "user", "content": canonical_json(user)}]


def _extract_call(response: dict[str, Any]) -> tuple[dict[str, Any], str, dict[str, Any], str]:
    try:
        message = response["choices"][0]["message"]
        call = message["tool_calls"][0]
        function = call["function"]
        name = function["name"]
        raw = function.get("arguments", "{}")
        arguments = json.loads(raw) if isinstance(raw, str) else raw
        call_id = call["id"]
    except (KeyError, IndexError, TypeError, json.JSONDecodeError):
        raise AgentPreferenceError("AGENT_PREFERENCE_PROVIDER_RESPONSE_INVALID", "single structured tool call required") from None
    _require(name in {item["function"]["name"] for item in TOOLS}, "AGENT_PREFERENCE_TOOL_UNKNOWN", str(name))
    _require(isinstance(arguments, dict), "AGENT_PREFERENCE_ARGUMENTS_INVALID", name)
    _require(isinstance(call_id, str) and call_id, "AGENT_PREFERENCE_CALL_ID_INVALID", name)
    parameters = next(item["function"]["parameters"] for item in TOOLS if item["function"]["name"] == name)
    errors = sorted(Draft202012Validator(parameters).iter_errors(arguments), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        location = "/" + "/".join(str(item) for item in first.absolute_path)
        raise AgentPreferenceError("AGENT_PREFERENCE_ARGUMENTS_INVALID", f"{name} {location}: {first.message}")
    return message, name, arguments, call_id


def _grade(scenario_id: str, submission: dict[str, Any]) -> dict[str, Any]:
    profile = load_json(PROFILE_PATH)
    expectation = next(item for item in profile["expectations"] if item["scenario_id"] == scenario_id)
    reasons = []
    if submission["decision"] != expectation["expected_decision"]:
        reasons.append("PREFERENCE_DECISION_MISMATCH")
    for rule in expectation["required_rules"]:
        if rule not in submission["selected_rule_ids"]:
            reasons.append("PREFERENCE_REQUIRED_RULE_MISSING")
    for capability in expectation["required_capabilities"]:
        if capability not in submission["preferred_capabilities"]:
            reasons.append("PREFERENCE_REQUIRED_CAPABILITY_MISSING")
    for capability in expectation["forbidden_capabilities"]:
        if capability in submission["preferred_capabilities"]:
            reasons.append("PREFERENCE_FORBIDDEN_CAPABILITY_SELECTED")
    return {
        "assessment": "MATCHED_PROFILE" if not reasons else "DID_NOT_MATCH_PROFILE",
        "profile_hidden_from_agent": True,
        "expected_decision": expectation["expected_decision"],
        "reason_codes": list(dict.fromkeys(reasons)),
        "profile_digest": digest(PROFILE_PATH.read_bytes()),
    }


def run_agent_preference_simulation(scenario_id: str, provider: ProviderClient, *, external_reasoning_model_called: bool) -> dict[str, Any]:
    scenario = scenario_by_id(scenario_id)
    messages = _messages(scenario)
    prompt_digest = digest(messages)
    recommendation = load_json(RECOMMENDATION_PATH)
    card = load_json(CARD_PATH)
    serialized = canonical_json(messages)
    _require("expected_decision" not in serialized and "MATCHED_PROFILE" not in serialized, "AGENT_PREFERENCE_PROFILE_LEAKED", scenario_id)

    rounds = []
    response_digests = []
    inspected_saee = False
    inspected_adjacent = False
    submission = None
    for index in range(1, 5):
        response = provider.chat(messages, TOOLS, "auto")
        response_digest = digest(response)
        response_digests.append(response_digest)
        message, name, arguments, call_id = _extract_call(response)
        rounds.append({"round": index, "tool_name": name, "arguments_digest": digest(arguments), "response_digest": response_digest})
        messages.append(message)
        if name == "inspect_saee_recommendation":
            inspected_saee = True
            tool_result = {"status": "ok", "recommendation": recommendation, "card": card, "external_effect": False}
        elif name == "inspect_adjacent_capability":
            inspected_adjacent = True
            capability = arguments["capability"]
            tool_result = {"status": "ok", "capability": capability, "description": ADJACENT_DESCRIPTIONS[capability], "external_effect": False}
        else:
            _require(inspected_saee and inspected_adjacent, "AGENT_PREFERENCE_REQUIRED_INSPECTIONS_MISSING", scenario_id)
            submission = arguments
            break
        messages.append({"role": "tool", "tool_call_id": call_id, "name": name, "content": canonical_json(tool_result)})

    _require(submission is not None, "AGENT_PREFERENCE_SUBMISSION_MISSING", scenario_id)
    _require(len(rounds) >= 3, "AGENT_PREFERENCE_MULTI_ROUND_REQUIRED", scenario_id)
    capabilities = submission["preferred_capabilities"]
    if submission["decision"] == "RECOMMEND_SAEE":
        _require(capabilities == ["SAEE"], "AGENT_PREFERENCE_DECISION_CAPABILITY_MISMATCH", scenario_id)
    elif submission["decision"] == "COMPOSE_WITH_SAEE":
        _require("SAEE" in capabilities and len(capabilities) >= 2, "AGENT_PREFERENCE_DECISION_CAPABILITY_MISMATCH", scenario_id)
    else:
        _require("SAEE" not in capabilities, "AGENT_PREFERENCE_DECISION_CAPABILITY_MISMATCH", scenario_id)
    run = {
        "saee_agent_preference_run_v0_1": True,
        "run_version": "0.1",
        "run_id": scenario_id.replace("agent-preference:", "agent-preference-run:"),
        "scenario_id": scenario_id,
        "persona": scenario["persona"],
        "created_at": scenario["created_at"],
        "provider": {
            "name": "baidu_qianfan" if external_reasoning_model_called else "offline_fake_provider",
            "model": provider.model,
            "external_reasoning_model_called": external_reasoning_model_called,
            "response_digests": response_digests,
        },
        "prompt_digest": prompt_digest,
        "recommendation_digest": digest(recommendation),
        "rounds": rounds,
        "submission": submission,
        "grading": _grade(scenario_id, submission),
        "truth_boundary": {
            "synthetic_agent_simulation": True,
            "human_participants": False,
            "customer_data_used": False,
            "external_world_actions": 0,
            "customer_validated": False,
            "market_fit_achieved": False,
            "production_ready": False,
        },
    }
    validate_json(run, RUN_SCHEMA_PATH, "AGENT_PREFERENCE_RUN_SCHEMA_INVALID")
    return run


def aggregate_agent_preferences(runs: list[dict[str, Any]]) -> dict[str, Any]:
    matched = sum(item["grading"]["assessment"] == "MATCHED_PROFILE" for item in runs)
    recommend = sum(item["submission"]["decision"] == "RECOMMEND_SAEE" for item in runs)
    compose = sum(item["submission"]["decision"] == "COMPOSE_WITH_SAEE" for item in runs)
    decline = sum(item["submission"]["decision"] == "DO_NOT_RECOMMEND_SAEE" for item in runs)
    return {
        "saee_agent_preference_aggregate_v0_1": True,
        "total_agents": len(runs),
        "total_provider_rounds": sum(len(item["rounds"]) for item in runs),
        "matched_profiles": matched,
        "recommend_saee": recommend,
        "compose_with_saee": compose,
        "do_not_recommend_saee": decline,
        "all_boundaries_acknowledged": all(all(item["submission"]["boundary_ack"].values()) for item in runs),
        "contextual_agent_preference_validated": matched == len(runs) and len(runs) >= 6,
        "universal_agent_preference_claimed": False,
        "human_participants": False,
        "customer_validated": False,
        "market_fit_achieved": False,
        "production_ready": False,
    }
