#!/usr/bin/env python3
"""Simulate one local agent-like call to the SAEE MCP prototype."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.local_mcp_server import create_local_mcp_server  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one local synthetic SAEE MCP request")
    parser.add_argument("--input", required=True, help="Repository-local JSON request file")
    args = parser.parse_args()
    request = json.loads(Path(args.input).read_text(encoding="utf-8"))
    result = create_local_mcp_server().call_tool(request)
    print("SAEE_LOCAL_MCP_RESPONSE")
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    return 0 if result["tool_result"] == "SUCCESS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
