#!/usr/bin/env python3
"""Start the local two-tool SAEE Qianfan readiness MCP adapter."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.qianfan_readiness_mcp_adapter import serve


if __name__ == "__main__":
    raise SystemExit(serve(sys.stdin.buffer, sys.stdout.buffer))
