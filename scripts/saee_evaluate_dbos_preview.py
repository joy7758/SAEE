#!/usr/bin/env python3
"""Evaluate a DBOS Developer Preview JSON envelope without side effects."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.dbos_developer_preview_adapter import (  # noqa: E402
    DBOSDeveloperPreviewInputError,
    evaluate_dbos_developer_preview,
)


def _load(path: str | None) -> Any:
    if path is None or path == "-":
        return json.load(sys.stdin)
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Read-only SAEE evaluation of the bounded DBOS Developer Preview envelope."
    )
    parser.add_argument(
        "--input",
        default="-",
        help="DBOS demo JSON path, envelope JSON path, or '-' for stdin.",
    )
    args = parser.parse_args()
    try:
        payload = _load(args.input)
        if isinstance(payload, dict) and "dbos_to_saee_envelope" in payload:
            payload = payload["dbos_to_saee_envelope"]
        result = evaluate_dbos_developer_preview(payload)
    except (OSError, json.JSONDecodeError, DBOSDeveloperPreviewInputError) as exc:
        code = getattr(exc, "code", "DBOS_PREVIEW_INPUT_READ_FAILED")
        print(json.dumps({"error": code, "detail": str(exc)}, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
