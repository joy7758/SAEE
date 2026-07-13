#!/usr/bin/env python3
"""Bootstrap SAEE v0.3 meta-evolution in one local reproducible pass."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from saee_v0_3.kernel.runtime import SAEEV03Runtime, load_seed, write_outputs


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_v0_3" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE v0.3 bootstrap")
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=3)
    parser.add_argument("--initial-population-size", type=int, default=4)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    seed = load_seed(args.seed)
    runtime = SAEEV03Runtime(seed, initial_population_size=args.initial_population_size)
    record = runtime.run(args.generations)
    write_outputs(record, args.output_dir)
    if not record["drift_guard"]["passed"]:
        print(json.dumps(record["drift_guard"], indent=2, sort_keys=True))
        raise SystemExit("SAEE_V0_3_BOOTSTRAP: FAIL drift guard rejected output")
    print(
        "SAEE_V0_3_BOOTSTRAP: PASS "
        f"generation={record['generation_id']} "
        f"population={len(record['population'])} "
        f"rule={record['rule_genome']['id']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

