#!/usr/bin/env python3
"""Smoke check for the SAEE v1.2 parasitic phase experiment."""

from __future__ import annotations

from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_v1_2.parasitic_phase.model import run_experiment_set, write_outputs


def fail(message: str) -> None:
    raise SystemExit(f"SAEE_PARASITIC_PHASE_SMOKE: FAIL: {message}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="saee-parasitic-phase-") as tmp:
        output_dir = Path(tmp)
        results = run_experiment_set(steps=160)
        write_outputs(results, output_dir)
        by_id = {result.config.experiment_id: result for result in results}
        a = by_id["A_no_governance"]
        b = by_id["B_weak_governance"]
        c = by_id["C_strong_governance"]

        if a.phase_transition_step is None:
            fail("experiment A should enter parasitic phase")
        if b.phase_transition_step is not None and b.phase_transition_step <= a.phase_transition_step:
            fail("weak governance should delay or suppress crossing relative to A")
        if c.phase_transition_step is not None and c.phase_transition_step <= a.phase_transition_step:
            fail("strong governance should delay or suppress crossing relative to A")
        if float(a.metrics[-1]["phi"]) <= float(c.metrics[-1]["phi"]):
            fail("strong governance should reduce final phi relative to no governance")
        for experiment_id in by_id:
            for filename in ("metrics.csv", "trace.jsonl", "summary.json"):
                if not (output_dir / experiment_id / filename).is_file():
                    fail(f"missing {filename} for {experiment_id}")
        if not (output_dir / "parasitic_phase_curves.svg").is_file():
            fail("missing SVG curve output")

    print(
        "SAEE_PARASITIC_PHASE_SMOKE: PASS "
        f"A_crossing={a.phase_transition_step} "
        f"B_crossing={b.phase_transition_step} "
        f"C_crossing={c.phase_transition_step} "
        f"A_final_phi={a.metrics[-1]['phi']} "
        f"C_final_phi={c.metrics[-1]['phi']}"
    )


if __name__ == "__main__":
    main()
