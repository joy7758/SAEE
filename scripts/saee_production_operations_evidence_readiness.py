#!/usr/bin/env python3
"""Run SAEE production operations evidence readiness checks."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS
from saee_backend.services.production_operations_evidence import (
    evaluate_production_operations_evidence,
)


def main() -> None:
    print(
        json.dumps(
            evaluate_production_operations_evidence(SETTINGS),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
