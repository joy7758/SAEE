"""Public-safe JSONL logging helper for the SAEE toy abstraction release.

This module is intentionally independent from the private SAEE runtime. It
does not import kernel, fitness, selection, lineage, mutation, or reproduction
engines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Write toy observation rows as newline-delimited JSON."""

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Read toy observation rows from newline-delimited JSON."""

    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]

