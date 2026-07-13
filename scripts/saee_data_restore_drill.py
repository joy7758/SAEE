#!/usr/bin/env python3
"""Run an isolated local restore drill for a SAEE public-shell backup."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import SETTINGS
from saee_backend.services.data_restore_drill import run_public_shell_restore_drill


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backup-manifest", help="Path to BACKUP_MANIFEST.json.")
    group.add_argument("--backup-dir", help="Path to a backup directory containing BACKUP_MANIFEST.json.")
    parser.add_argument("--label", default="manual", help="Optional filesystem-safe drill label.")
    args = parser.parse_args()

    manifest_path = (
        Path(args.backup_manifest)
        if args.backup_manifest
        else Path(args.backup_dir) / "BACKUP_MANIFEST.json"
    )
    print(
        json.dumps(
            run_public_shell_restore_drill(manifest_path, SETTINGS, label=args.label),
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
