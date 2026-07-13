#!/usr/bin/env python3
"""Run the single-scenario SAEE Rehearsal MVP with a real Qianfan model."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.rehearsal_runtime import AgentAdapter, load_mvp_scenario, run_rehearsal_mvp
from scripts.saee_qianfan_mcp_host import QianfanClient


def main() -> int:
    parser = argparse.ArgumentParser(description="运行 SAEE 单场景真实模型演练 MVP")
    parser.add_argument("--output-dir", default="output/rehearsal-mvp")
    args = parser.parse_args()
    if not os.environ.get("QIANFAN_API_KEY"):
        print("SAEE_REHEARSAL_DEMO: FAIL missing QIANFAN_API_KEY", file=sys.stderr)
        return 2
    scenario = load_mvp_scenario()
    client = QianfanClient()
    adapter = AgentAdapter(
        client,
        provider_name="baidu_qianfan",
        agent_id="agent:qianfan-coding-release-mvp-v0.1",
        created_at=scenario["created_at"],
    )
    result = run_rehearsal_mvp(adapter)
    output_dir = (ROOT / args.output_dir).resolve()
    try:
        output_dir.relative_to(ROOT.resolve())
    except ValueError:
        print("SAEE_REHEARSAL_DEMO: FAIL output outside repository", file=sys.stderr)
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "SAEE_AGENT_REHEARSAL_REPORT.md"
    result_path = output_dir / "saee-rehearsal-mvp-result.v0.1.json"
    report_path.write_text(result["report_markdown"], encoding="utf-8")
    result_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "SAEE_REHEARSAL_DEMO_RESULT": "PASS",
        "provider": result["run"]["provider"],
        "model": result["run"]["model"],
        "state_transitions": len(result["run"]["state_transitions"]),
        "observations": len(result["run"]["observations"]),
        "recommendation": result["recommendation"],
        "authorization_assessment": result["evidence_case"]["evaluations"][0]["result"],
        "oversight_assessment": result["evidence_case"]["evaluations"][1]["result"],
        "report": str(report_path.relative_to(ROOT)),
        "external_world_actions": False,
        "customer_data": False,
        "production_ready": False,
        "secret_reflected": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

