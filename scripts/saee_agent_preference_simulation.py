#!/usr/bin/env python3
"""运行 SAEE 智能体偏好多轮合成模拟。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_preference_simulation import (  # noqa: E402
    AgentPreferenceError,
    CORPUS_PATH,
    aggregate_agent_preferences,
    load_json,
    run_agent_preference_simulation,
)
from scripts.saee_qianfan_mcp_host import ProviderError, QianfanClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="使用百度千帆真实推理模型运行六个 SAEE 智能体偏好场景。")
    parser.add_argument("--write-dir", type=Path, help="写入脱敏运行证据的 allowlist 目录")
    args = parser.parse_args()
    try:
        provider = QianfanClient()
        scenarios = load_json(CORPUS_PATH)["scenarios"]
        runs = [run_agent_preference_simulation(item["scenario_id"], provider, external_reasoning_model_called=True) for item in scenarios]
        aggregate = aggregate_agent_preferences(runs)
        if args.write_dir:
            target = args.write_dir.resolve()
            allowed = (ROOT / "output/agent-preference-simulation").resolve()
            if target != allowed:
                raise AgentPreferenceError("AGENT_PREFERENCE_OUTPUT_OUTSIDE_ALLOWLIST", str(args.write_dir))
            target.mkdir(parents=True, exist_ok=True)
            for run in runs:
                slug = run["scenario_id"].split(":")[1]
                (target / f"qianfan-{slug}.v0.1.run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            (target / "qianfan-agent-preference-aggregate.v0.1.json").write_text(json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (AgentPreferenceError, ProviderError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        code = getattr(exc, "code", getattr(exc, "category", "AGENT_PREFERENCE_SIMULATION_FAILED"))
        print(json.dumps({"status": "FAIL", "reason_code": code, "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS" if aggregate["contextual_agent_preference_validated"] else "HOLD", "aggregate": aggregate}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if aggregate["contextual_agent_preference_validated"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
