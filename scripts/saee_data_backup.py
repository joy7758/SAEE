#!/usr/bin/env python3
"""Create a local public-shell backup for the SAEE MVP API shell."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS
from saee_backend.services.data_backup import create_public_shell_backup


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", default="manual", help="Optional filesystem-safe backup label.")
    args = parser.parse_args()
    print(json.dumps(create_public_shell_backup(SETTINGS, label=args.label), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
