#!/usr/bin/env python3
"""Run one local SAEE Agent Readiness public-product operation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.baidu_agent_readiness_service import (
    ReadinessInputError,
    evaluate_agent_run,
    evaluate_evidence,
)


OPERATIONS = {
    "evaluate-agent-run": evaluate_agent_run,
    "evaluate-evidence": evaluate_evidence,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a local SAEE Agent Readiness assessment")
    parser.add_argument("operation", choices=sorted(OPERATIONS))
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        request = json.loads(args.input.read_text(encoding="utf-8"))
        result = OPERATIONS[args.operation](request)
    except (OSError, json.JSONDecodeError, ReadinessInputError) as exc:
        code = exc.code if isinstance(exc, ReadinessInputError) else "READINESS_INPUT_FILE_INVALID"
        print(json.dumps({"status": "REJECTED", "reason_code": code}, sort_keys=True), file=sys.stderr)
        return 2
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
