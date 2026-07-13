#!/usr/bin/env python3
"""CLI for the controlled local SAEE Agent Rehearsal Runtime MVP."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import RehearsalRuntimeError, run_task


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one allowlisted local SAEE Agent rehearsal scenario.")
    parser.add_argument("--scenario", required=True, type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        result = run_task(args.scenario)
    except (RehearsalRuntimeError, json.JSONDecodeError, OSError, ValueError, KeyError) as exc:
        code = getattr(exc, "code", "REHEARSAL_RUNTIME_FAILED")
        print(json.dumps({"status": "FAIL", "reason_code": code, "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps({"status": "PASS", "result_type": "SAEE_AGENT_REHEARSAL_RUN", "run": result}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
