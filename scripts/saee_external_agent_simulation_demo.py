#!/usr/bin/env python3
"""Run one local synthetic external-Agent simulation scenario."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.external_agent_simulator import evaluate_external_agent_simulation  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one local synthetic SAEE external-Agent scenario")
    parser.add_argument("--input", required=True, help="Repository-local synthetic scenario JSON")
    args = parser.parse_args()
    scenario = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = evaluate_external_agent_simulation(scenario)
    print("SAEE_EXTERNAL_AGENT_SIMULATION_RESULT")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["expected_outcome_matched"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
