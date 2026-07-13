#!/usr/bin/env python3
"""Run SAEE public-shell data retention evaluation."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS
from saee_backend.services.data_retention import evaluate_data_retention


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate SAEE public-shell data retention.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply retention only when SAEE_RETENTION_DRY_RUN=false.",
    )
    args = parser.parse_args()
    print(json.dumps(evaluate_data_retention(SETTINGS, apply=args.apply), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
