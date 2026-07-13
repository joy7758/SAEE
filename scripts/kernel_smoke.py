#!/usr/bin/env python3
"""Smoke test for SAEE Evolution Kernel v0.1."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kernel.runtime import SAEEKernel

SEED = ROOT / "kernel" / "examples" / "seed_genome.json"


def fail(message: str) -> None:
    raise SystemExit(f"KERNEL_SMOKE: FAIL: {message}")


def main() -> None:
    seed = json.loads(SEED.read_text(encoding="utf-8"))
    kernel = SAEEKernel(seed)
    record = kernel.run(3)

    if record["status"] != "local_v0_1_runnable":
        fail("unexpected run status")
    if len(record["lineage"]) != 3:
        fail("expected exactly 3 lineage events")
    if record["current_genome"]["version"] != 3:
        fail("expected selected genome version 3")
    if "no_external_repo_execution" not in record["boundaries"]:
        fail("missing safety boundary")

    print(f"KERNEL_SMOKE: PASS selected={record['current_genome']['id']}")


if __name__ == "__main__":
    main()
