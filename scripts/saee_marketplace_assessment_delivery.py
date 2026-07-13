#!/usr/bin/env python3
"""CLI for the bounded Alibaba Cloud Marketplace assessment delivery bridge."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.marketplace_assessment_delivery import (
    MarketplaceDeliveryError,
    finalize_delivery,
    prepare_delivery,
)


def parser() -> argparse.ArgumentParser:
    value = argparse.ArgumentParser(description=__doc__)
    commands = value.add_subparsers(dest="command", required=True)
    prepare = commands.add_parser("prepare", help="Generate bundle, report, and prepared receipt.")
    prepare.add_argument("--input", type=Path, required=True)
    prepare.add_argument("--output-dir", type=Path, required=True)
    finalize = commands.add_parser("finalize", help="Confirm review and delete the local intake source.")
    finalize.add_argument("--prepared-receipt", type=Path, required=True)
    finalize.add_argument("--input", type=Path, required=True)
    finalize.add_argument("--intake-root", type=Path, required=True)
    finalize.add_argument("--reviewer-role-token", required=True)
    return value


def main() -> int:
    args = parser().parse_args()
    try:
        if args.command == "prepare":
            result = prepare_delivery(args.input, args.output_dir)
        else:
            result = finalize_delivery(
                args.prepared_receipt,
                args.input,
                args.intake_root,
                args.reviewer_role_token,
            )
    except MarketplaceDeliveryError as exc:
        print(json.dumps({"ok": False, "error": exc.code, "detail": exc.detail}, ensure_ascii=False), file=sys.stderr)
        return 2
    print(json.dumps({"ok": True, "receipt": result}, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

