#!/usr/bin/env python3
"""Validate the SAEE Global State Protocol snapshot."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STATE_DIR = ROOT / "saee_global_state"


REQUIRED_FILES = [
    "SAEE_GLOBAL_STATE.json",
    "STATE_SYNC_MAP.md",
    "DRIFT_ANALYSIS_REPORT.md",
    "IDENTITY_CONSTRAINT.md",
    "VERSION_UNIFICATION_TABLE.md",
]

REQUIRED_STATE_KEYS = [
    "theory_state",
    "engineering_state",
    "experimental_state",
    "lineage_state",
    "global_properties",
    "state_synchronization",
    "drift_analysis",
    "identity_constraint",
]


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_GLOBAL_STATE_CHECK: FAIL: {message}")


def main() -> None:
    missing = [name for name in REQUIRED_FILES if not (STATE_DIR / name).is_file()]
    if missing:
        fail("missing files: " + ", ".join(missing))

    state = json.loads((STATE_DIR / "SAEE_GLOBAL_STATE.json").read_text(encoding="utf-8"))
    missing_keys = [key for key in REQUIRED_STATE_KEYS if key not in state]
    if missing_keys:
        fail("missing state keys: " + ", ".join(missing_keys))

    if state.get("system") != "SAEE":
        fail("system must be SAEE")
    if state.get("single_source_of_truth") is not True:
        fail("single_source_of_truth must be true")
    if state["state_synchronization"].get("orphan_states") != []:
        fail("orphan_states must be empty")
    if state["state_synchronization"].get("bidirectional_traceability") is not True:
        fail("bidirectional_traceability must be true")
    score = float(state["drift_analysis"].get("consistency_score", 0.0))
    if score < 0.8:
        fail("consistency_score below 0.8")
    if state["global_properties"].get("external_validation_claim") is not False:
        fail("external validation claim must remain false")

    print(
        "SAEE_GLOBAL_STATE_CHECK: PASS "
        f"consistency_score={score:.2f} "
        f"layers={len(state['state_synchronization']['mapped_layers'])} "
        f"orphan_states=0"
    )


if __name__ == "__main__":
    main()
