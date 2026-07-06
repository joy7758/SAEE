#!/usr/bin/env python3
"""Run a public-safe SAEE abstraction demo.

This demo is intentionally toy-level. It does not import or reproduce private
SAEE runtime, kernel, fitness, selection, mutation, lineage, or reproduction
logic.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from abstraction_layer.phase_space_stub import summarize_phase_space


def main() -> None:
    rows = [
        {"generation": idx, "stability_proxy": min(1.0, 0.25 + idx * 0.08)}
        for idx in range(10)
    ]
    summary = summarize_phase_space(rows)
    print("SAEE_PUBLIC_ABSTRACTION_DEMO: PASS")
    print(f"summary={summary}")


if __name__ == "__main__":
    main()

