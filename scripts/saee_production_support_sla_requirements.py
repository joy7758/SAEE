#!/usr/bin/env python3
"""Print SAEE Production Support / SLA Requirements v0.1."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS_PATH = (
    ROOT / "phase_b_product/commercial_readiness/PRODUCTION_SUPPORT_SLA_REQUIREMENTS_V0_1.json"
)


def main() -> None:
    print(json.dumps(json.loads(REQUIREMENTS_PATH.read_text(encoding="utf-8")), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
