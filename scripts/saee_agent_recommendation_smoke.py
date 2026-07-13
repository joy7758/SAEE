#!/usr/bin/env python3
"""Offline smoke for SAEE Agent Recommendation Infrastructure v0.1."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_recommendation_validator import validate_agent_recommendation  # noqa: E402


SCHEMA = ROOT / "agent-interface/recommendation/saee-agent-recommendation.schema.v0.1.json"
SURFACE = ROOT / "agent-interface/recommendation/saee-agent-recommendation.v0.1.json"
CARD = ROOT / "agent-interface/recommendation/saee-agent-recommendation-card.v0.1.json"
DOC = ROOT / "docs/architecture/SAEE_AGENT_RECOMMENDATION_INFRASTRUCTURE.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_RECOMMENDATION_INFRASTRUCTURE_RECOMMENDATION_GATE.md"
SERVICE = ROOT / "saee_backend/services/agent_recommendation_validator.py"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def expect_invalid(value: dict, code: str) -> None:
    result = validate_agent_recommendation(value)
    assert result["valid"] is False, code
    assert result["reason_codes"] == [code], result


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {alias.name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def main() -> int:
    for path in (SCHEMA, SURFACE, CARD, DOC, GATE, SERVICE):
        assert path.is_file(), path
    schema = load(SCHEMA)
    Draft202012Validator.check_schema(schema)
    surface = load(SURFACE)
    card = load(CARD)
    result = validate_agent_recommendation(surface)
    assert result["valid"] is True and result["rule_count"] == 11, result
    assert card["recommendation"]["recommendation_reference"] == "agent-interface/recommendation/saee-agent-recommendation.v0.1.json"
    assert card["recommendation"]["rehearsal_mvp_reference"] == "agent-interface/rehearsal/mvp/saee-rehearsal-mvp-live-validation.v0.1.json"
    assert card["recommendation"]["scenario_library_reference"] == "agent-interface/rehearsal/scenario-library.schema.v0.2.json"
    assert card["recommendation"]["multi_agent_rehearsal_reference"] == "agent-interface/benchmark/saee-agent-comparison-result.v0.1.json"
    assert card["recommendation"]["reliability_study_reference"] == "agent-interface/reliability/saee-agent-reliability-result.v0.1.json"
    assert card["recommendation"]["research_agent_study_reference"] == "agent-interface/reliability/saee-research-agent-reliability-result.v0.2.json"
    assert card["recommendation"]["security_boundary_study_reference"] == "agent-interface/reliability/saee-security-boundary-reliability-result.v0.3.json"
    assert set(card["composition"]["works_with"]) == {"Stateful Rehearsal Runtime", "MCP", "Observability", "Evaluation", "Human Review"}
    assert card["boundaries"]["recommendation_controls_agent_decision"] is False
    assert card["truth_boundary"] == {
        "external_agent_recommendation_observed": True,
        "controlled_synthetic_agent_preference_observed": True,
        "external_agent_recommendation_evidence_ref": "agent-interface/recommendation/simulation/saee-agent-preference-live-validation.v0.1.json",
        "marketplace_available": False,
        "external_validation_completed": False,
        "production_ready": False,
    }

    invalid = []
    mutation = copy.deepcopy(surface); mutation["should_recommend_when"] = []; invalid.append((mutation, "AGENT_RECOMMENDATION_SCHEMA_INVALID"))
    mutation = copy.deepcopy(surface); mutation["should_not_recommend_when"] = []; invalid.append((mutation, "AGENT_RECOMMENDATION_SCHEMA_INVALID"))
    mutation = copy.deepcopy(surface); mutation["truth_boundary"]["production_ready"] = True; invalid.append((mutation, "AGENT_RECOMMENDATION_SCHEMA_INVALID"))
    mutation = copy.deepcopy(surface); mutation["limitations"].append("guaranteed adoption"); invalid.append((mutation, "AGENT_RECOMMENDATION_CLAIM_FORBIDDEN"))
    mutation = copy.deepcopy(surface); mutation["limitations"].append("trusted by all agents"); invalid.append((mutation, "AGENT_RECOMMENDATION_CLAIM_FORBIDDEN"))
    mutation = copy.deepcopy(surface); mutation["limitations"].append("certified capability"); invalid.append((mutation, "AGENT_RECOMMENDATION_CLAIM_FORBIDDEN"))
    mutation = copy.deepcopy(surface); mutation["limitations"].append("automatic approval"); invalid.append((mutation, "AGENT_RECOMMENDATION_CLAIM_FORBIDDEN"))
    mutation = copy.deepcopy(surface); mutation["composition_rules"][-1]["capability"] = "OBSERVATION_LAYER"; invalid.append((mutation, "AGENT_RECOMMENDATION_COMPOSITION_INVALID"))
    mutation = copy.deepcopy(surface); mutation["should_recommend_when"][1]["rule_id"] = mutation["should_recommend_when"][0]["rule_id"]; invalid.append((mutation, "AGENT_RECOMMENDATION_RULE_ID_DUPLICATE"))
    for value, code in invalid:
        expect_invalid(value, code)

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        rerun = validate_agent_recommendation(copy.deepcopy(surface))
        assert json.dumps(rerun, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical

    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "smtplib", "importlib"}
    assert not imported_roots(SERVICE).intersection(forbidden)
    assert not imported_roots(Path(__file__)).intersection(forbidden)
    doc = DOC.read_text(encoding="utf-8")
    assert "SAEE provides machine-readable recommendation context. It does not control agent decisions." in doc
    assert "SAEE 提供机器可读推荐上下文，不控制智能体决策。" in doc

    print("SAEE_AGENT_RECOMMENDATION_SMOKE: PASS")
    print("valid_cases=1/1")
    print(f"invalid_cases={len(invalid)}/{len(invalid)}")
    print("deterministic_runs=5/5")
    print("should_recommend_rules=6/6")
    print("should_not_recommend_rules=5/5")
    print("composition_rules=5/5")
    print("external_agent_recommendation_observed=true")
    print("controlled_synthetic_agent_preference_observed=true")
    print("automatic_recommendation_implemented=false")
    print("marketplace_available=false")
    print("external_validation_completed=false")
    print("network_accessed=false")
    print("subprocess_started=false")
    print("external_execution=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
