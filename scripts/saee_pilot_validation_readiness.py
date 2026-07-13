#!/usr/bin/env python3
"""Print SAEE controlled pilot validation readiness."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.pilot_validation_readiness import (
    evaluate_pilot_validation_readiness,
)


def main() -> None:
    print(json.dumps(evaluate_pilot_validation_readiness(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
