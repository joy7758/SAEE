#!/usr/bin/env python3
"""Print SAEE billing and pricing readiness."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.billing_pricing_readiness import (
    evaluate_billing_pricing_readiness,
)


def main() -> None:
    print(json.dumps(evaluate_billing_pricing_readiness(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
