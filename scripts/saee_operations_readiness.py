#!/usr/bin/env python3
"""Print SAEE Operations Readiness v0.1 for the public API shell."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS
from saee_backend.services.operations_readiness import evaluate_operations_readiness


def main() -> None:
    print(json.dumps(evaluate_operations_readiness(SETTINGS), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
