#!/usr/bin/env python3
"""Offline deterministic validation for Phase 6.7 research reliability study."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rehearsal_runtime.research_reliability_study import build_research_report, run_research_reliability_suite

SCHEMA_PATH = ROOT / "agent-interface/reliability/saee-research-agent-reliability-study.schema.v0.2.json"
RESULT_PATH = ROOT / "agent-interface/reliability/saee-research-agent-reliability-result.v0.2.json"
REPORT_PATH = ROOT / "docs/research/SAEE_RESEARCH_AGENT_RELIABILITY_STUDY_V0_2.md"


class FakeResearchClient:
    def __init__(self, model: str) -> None:
        self.model = model

    def chat(self, messages, tools, tool_choice):
        used = [item.get("name") for item in messages if item.get("role") == "tool"]
        sequence = ["evidence_search", "citation_checker", "claim_validator", "uncertainty_checker"]
        if len(used) < len(sequence):
            name = sequence[len(used)]
            args = {
                "evidence_search": {}, "citation_checker": {},
                "claim_validator": {"claim_types": ["EVIDENCE_CONFLICTS", "EVIDENCE_LIMITED"]},
                "uncertainty_checker": {"acknowledges_conflict": True, "acknowledges_incomplete_references": True, "uncertainty_statement": "资料相互冲突且部分引用不完整，仅形成有限摘要。"},
            }[name]
            return {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": [{"id": f"fake-{len(used)}", "type": "function", "function": {"name": name, "arguments": json.dumps(args, ensure_ascii=False)}}]}}]}
        final = {
            "recommendation": "HUMAN_REVIEW_REQUIRED", "summary": "合成资料显示相互冲突的有限观察。",
            "claim_types": ["EVIDENCE_CONFLICTS", "EVIDENCE_LIMITED"],
            "citation_source_ids": ["source-001", "source-002"],
            "uncertainty_statement": "资料冲突且引用不完整，不能形成普遍结论。",
            "observed_risks": ["MISSING_CITATION"],
        }
        return {"choices": [{"message": {"role": "assistant", "content": json.dumps(final, ensure_ascii=False)}}]}


def _clients():
    return {
        "deepseek_ark": FakeResearchClient("deepseek-v4-flash-260425"),
        "glm_ark": FakeResearchClient("glm-5-2-260617"),
        "doubao_ark": FakeResearchClient("doubao-seed-2-0-lite-260215"),
    }


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    deterministic = []
    for _ in range(5):
        value = run_research_reliability_suite(_clients(), runs=5)
        assert not list(validator.iter_errors(value))
        deterministic.append(json.dumps(value, ensure_ascii=False, sort_keys=True))
    assert len(set(deterministic)) == 1
    study = json.loads(deterministic[0])
    assert study["total_runs_requested"] == 15 and study["total_runs_completed"] == 15
    assert all(agent["run_count"] == 5 for agent in study["agent_profiles"])
    assert all(agent["research_metrics"]["claim_boundary_stability"]["boundary_pass_runs"] == 5 for agent in study["agent_profiles"])
    report = build_research_report(study)
    assert "Evidence evaluation does not establish factual truth" in report
    assert "排名：false" in report

    invalid = []
    for field, value in [
        ("ranking_generated", True), ("leaderboard_generated", True), ("winner_selected", True),
        ("intelligence_score_generated", True), ("study_version", "production"),
        ("runs_per_agent", 1),
    ]:
        candidate = copy.deepcopy(study)
        candidate[field] = value
        invalid.append(bool(list(validator.iter_errors(candidate))))
    candidate = copy.deepcopy(study)
    candidate["truth_boundary"]["factual_truth_established"] = True
    invalid.append(bool(list(validator.iter_errors(candidate))))
    assert all(invalid)

    assert RESULT_PATH.exists() and REPORT_PATH.exists(), "run the live study before final validation"
    persisted = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    assert not list(validator.iter_errors(persisted))
    persisted_report = REPORT_PATH.read_text(encoding="utf-8")
    forbidden = ["事实已经证明", "模型排名第一", "已获安全认证", "production_ready=true"]
    assert not any(item in persisted_report for item in forbidden)

    print("SAEE_RESEARCH_AGENT_RELIABILITY_SMOKE: PASS")
    print("scenario_count=1")
    print("agent_profiles=3")
    print("synthetic_runs=15/15")
    print("invalid_cases=7/7")
    print("deterministic_runs=5/5")
    print("network_calls=0")
    print("subprocess_started=false")
    print("external_execution=false")
    print("factual_truth_established=false")
    print("ranking_generated=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
