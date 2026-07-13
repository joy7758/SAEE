#!/usr/bin/env python3
"""CLI for the local SAEE Agent Readiness Benchmark v0.1."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.readiness_benchmark import ReadinessBenchmarkError, run_benchmark


def main() -> int:
    try:
        result = run_benchmark()
    except (ReadinessBenchmarkError, json.JSONDecodeError, OSError, ValueError, KeyError) as exc:
        code = getattr(exc, "code", "READINESS_BENCHMARK_FAILED")
        print(json.dumps({"status": "FAIL", "reason_code": code, "reason": str(exc)}, ensure_ascii=False, sort_keys=True))
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
