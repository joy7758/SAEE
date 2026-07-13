#!/usr/bin/env python3
"""Print SAEE production tenant storage evidence readiness."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS
from saee_backend.services.production_tenant_storage_evidence import (
    evaluate_production_tenant_storage_evidence,
)


def main() -> None:
    print(
        json.dumps(
            evaluate_production_tenant_storage_evidence(SETTINGS),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
