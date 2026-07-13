#!/usr/bin/env python3
"""Print a local SAEE operations telemetry snapshot."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.operations_telemetry import build_operations_telemetry_snapshot


def main() -> None:
    print(json.dumps(build_operations_telemetry_snapshot(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
