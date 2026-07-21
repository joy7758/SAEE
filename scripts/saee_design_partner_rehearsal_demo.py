#!/usr/bin/env python3
"""Generate the Chinese Design Partner demo from recorded controlled live runs."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.local_mcp_server import create_local_mcp_server
from saee_backend.services.readiness_benchmark import run_benchmark


LIVE_STATUS = ROOT / "agent-interface/rehearsal/saee-controlled-reasoning-live-validation.v0.2.json"
STATEFUL_STATUS = ROOT / "agent-interface/rehearsal/saee-stateful-business-live-validation.v0.3.json"


def live_evidence_available() -> bool:
    status = json.loads(LIVE_STATUS.read_text(encoding="utf-8"))
    stateful_status = json.loads(STATEFUL_STATUS.read_text(encoding="utf-8"))
    paths = [
        *(ROOT / record["run_ref"] for record in status["live_runs"]),
        ROOT / stateful_status["run_ref"],
    ]
    return all(path.is_file() for path in paths)


def build_demo() -> dict:
    if not live_evidence_available():
        if os.environ.get("SAEE_PROVIDER_EVIDENCE_MODE") == "optional":
            raise RuntimeError("EXTERNAL_EVIDENCE_NOT_AVAILABLE")
        raise FileNotFoundError("recorded Qianfan evidence is not available")
    server = create_local_mcp_server()
    cases = []
    status = json.loads(LIVE_STATUS.read_text(encoding="utf-8"))
    for record in status["live_runs"]:
        run = json.loads((ROOT / record["run_ref"]).read_text(encoding="utf-8"))
        cases.append({
            "scenario_category": record["scenario_category"],
            "scenario": run["scenario_ref"],
            "provider": run["provider"]["provider"],
            "model": run["provider"]["model"],
            "provider_rounds": run["provider"]["provider_rounds"],
            "agent_disposition": run["agent_submission"]["disposition"],
            "observed_tool_calls": run["grading"]["observed_tool_calls"],
            "trace_event_count": len(run["trace"]["events"]),
            "trace_digest": run["trace"]["trace_digest"],
            "grading_assessment": run["grading"]["assessment"],
            "grading_profile_hidden_from_agent": run["grading"]["grading_profile_hidden_from_agent"],
            "evidence_established": run["evidence_export"]["evidence_established"],
            "readiness_established": run["evidence_export"]["readiness_established"],
        })
    stateful_status = json.loads(STATEFUL_STATUS.read_text(encoding="utf-8"))
    stateful = json.loads((ROOT / stateful_status["run_ref"]).read_text(encoding="utf-8"))
    cases.append({
        "scenario_category": "stateful_saas_release_readiness",
        "scenario": stateful["scenario_ref"],
        "provider": stateful["provider"]["provider"],
        "model": stateful["provider"]["model"],
        "provider_rounds": stateful["provider"]["provider_rounds"],
        "agent_disposition": stateful["agent_submission"]["disposition"],
        "observed_tool_calls": stateful["grading"]["observed_tool_calls"],
        "state_transition_count": len(stateful["state_transitions"]),
        "initial_revision": stateful["initial_state"]["revision"],
        "final_revision": stateful["final_state"]["revision"],
        "trace_event_count": len(stateful["trace"]["events"]),
        "trace_digest": stateful["trace"]["trace_digest"],
        "grading_assessment": stateful["grading"]["assessment"],
        "grading_profile_hidden_from_agent": stateful["grading"]["grading_profile_hidden_from_agent"],
        "deployment_tool_called": "request_synthetic_deployment" in stateful["grading"]["observed_tool_calls"],
        "evidence_established": stateful["evidence_export"]["evidence_established"],
        "readiness_established": stateful["evidence_export"]["readiness_established"],
    })
    benchmark = run_benchmark()
    return {
        "saee_design_partner_rehearsal_demo_v0_1": True,
        "language": "zh-CN",
        "demo_scope": "recorded_qianfan_reasoning_runs_in_single_step_and_stateful_synthetic_worlds_no_customer_data",
        "tool_names": [tool["name"] for tool in server.list_tools()],
        "cases": cases,
        "benchmark_metrics": benchmark["metrics"],
        "boundary_statement": "本演示展示百度千帆真实推理模型在完全合成世界中的受控演练，不证明客户 Agent 安全、合规、生产可靠或获准上线。",
        "truth_boundary": {
            "customer_contacted": False,
            "feedback_collected": False,
            "customer_data_used": False,
            "controlled_qianfan_reasoning_model_validated": True,
            "real_customer_agent_validated": False,
            "synthetic_world_only": True,
            "external_world_actions": 0,
            "stateful_business_rehearsal_validated": True,
            "customer_adapter_contract_enabled": False,
            "standard_mcp_transport_available": False,
            "deployment_authorized": False,
            "production_ready": False,
        },
    }


def main() -> int:
    print(json.dumps(build_demo(), ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
