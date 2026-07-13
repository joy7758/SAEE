#!/usr/bin/env python3
"""Simulate one agent-like local invocation of the SAEE tool prototype."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.local_evidence_tool import evaluate_evidence_tool


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the local offline SAEE evidence adequacy tool prototype.")
    parser.add_argument("--input", required=True, type=Path, help="Path to one local JSON request.")
    args = parser.parse_args()
    try:
        payload = args.input.read_bytes()
    except OSError:
        payload = b""
    result = evaluate_evidence_tool(payload)
    print("SAEE_LOCAL_TOOL_RESULT")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["tool_result"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
