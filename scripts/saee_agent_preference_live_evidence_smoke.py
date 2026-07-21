#!/usr/bin/env python3
"""Validate recorded Qianfan Agent preference evidence without network access."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
STATUS = ROOT / "agent-interface/recommendation/simulation/saee-agent-preference-live-validation.v0.1.json"
RUN_SCHEMA = ROOT / "agent-interface/recommendation/simulation/saee-agent-preference-run.schema.v0.1.json"


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise SystemExit("SAEE_AGENT_PREFERENCE_LIVE_EVIDENCE_SMOKE: FAIL " + detail)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    evidence_paths = [
        *(ROOT / item["aggregate_ref"] for item in status["calibration_iterations"]),
        *(ROOT / item["run_ref"] for item in status["final_runs"]),
    ]
    present_count = sum(path.is_file() for path in evidence_paths)
    if present_count == 0 and os.environ.get("SAEE_PROVIDER_EVIDENCE_MODE") == "optional":
        print("external_provider_evidence_status=NOT_REQUIRED")
        print(
            "SAEE_AGENT_PREFERENCE_LIVE_EVIDENCE_SMOKE: PASS "
            "live_runs=0/6 normal_check_requires_external_provider_evidence=false"
        )
        return
    require(present_count == len(evidence_paths), "partial external evidence")
    schema = json.loads(RUN_SCHEMA.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    require(status["status"] == "controlled_qianfan_agent_preference_validated_in_synthetic_capability_selection", "status")
    iterations = status["calibration_iterations"]
    require([item["matched_profiles"] for item in iterations] == [3, 5, 6], "calibration progression")
    require([item["verdict"] for item in iterations] == ["HOLD", "HOLD", "PASS"], "calibration verdicts")
    for item in iterations:
        path = ROOT / item["aggregate_ref"]
        require(path.is_file() and sha256(path) == item["aggregate_sha256"], "aggregate binding")
    runs = []
    for record in status["final_runs"]:
        path = ROOT / record["run_ref"]
        require(path.is_file() and sha256(path) == record["run_sha256"], "run binding")
        run = json.loads(path.read_text(encoding="utf-8"))
        require(not list(validator.iter_errors(run)), "run schema")
        require(run["provider"]["name"] == "baidu_qianfan", "provider")
        require(run["provider"]["model"] == "ernie-4.5-turbo-128k", "model")
        require(run["provider"]["external_reasoning_model_called"] is True, "real reasoning")
        require(len(run["rounds"]) == 3 and len(run["provider"]["response_digests"]) == 3, "multi-round")
        require(run["grading"]["assessment"] == "MATCHED_PROFILE", "hidden grading")
        require(run["grading"]["profile_hidden_from_agent"] is True, "profile visibility")
        require(all(run["submission"]["boundary_ack"].values()), "boundary ack")
        require(run["submission"]["decision"] == record["decision"], "decision binding")
        require(run["truth_boundary"]["external_world_actions"] == 0, "external action")
        runs.append(run)
    require(len(runs) == 6, "run count")
    require(sum(item["submission"]["decision"] == "COMPOSE_WITH_SAEE" for item in runs) == 3, "compose count")
    require(sum(item["submission"]["decision"] == "DO_NOT_RECOMMEND_SAEE" for item in runs) == 3, "decline count")
    require(status["final_result"]["contextual_agent_preference_validated"] is True, "final result")
    require(status["final_result"]["universal_agent_preference_claimed"] is False, "universal claim")
    truth = status["truth_boundary"]
    require(truth["external_reasoning_model_called"] is True and truth["controlled_synthetic_agent_preference_observed"] is True, "observed preference")
    for field in ("human_participants", "customer_data_used", "customer_validated", "market_fit_achieved", "production_ready"):
        require(truth[field] is False, "truth overclaim " + field)
    require(truth["external_world_actions"] == 0 and truth["secret_leakage"] == 0, "security boundary")
    for path in [STATUS, *(ROOT / item["run_ref"] for item in status["final_runs"])]:
        text = path.read_text(encoding="utf-8")
        for marker in ("bce-v3/", "QIANFAN_API_KEY=", '"api_key"', '"access_token"'):
            require(marker not in text, "secret marker")
    print("SAEE_AGENT_PREFERENCE_LIVE_EVIDENCE_SMOKE: PASS")
    print("calibration_iterations=3/3")
    print("calibration_progression=3/6->5/6->6/6")
    print("synthetic_agents=6/6")
    print("provider_rounds=18/18")
    print("matched_profiles=6/6")
    print("compose_with_saee=3")
    print("do_not_recommend_saee=3")
    print("contextual_agent_preference_validated=true")
    print("universal_agent_preference_claimed=false")
    print("human_participants=false")
    print("external_world_actions=0")
    print("secret_leakage=0")
    print("customer_validated=false")
    print("production_ready=false")


if __name__ == "__main__":
    main()
