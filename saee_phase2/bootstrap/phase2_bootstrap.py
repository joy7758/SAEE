#!/usr/bin/env python3
"""Bootstrap SAEE Phase II behavior science locally."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from saee_phase2.runtime.phase2_behavior_runtime import (
    Phase2BehaviorRuntime,
    generate_v08_observation,
    load_record,
    write_outputs,
)


DEFAULT_SEED = ROOT / "kernel" / "examples" / "seed_genome.json"
DEFAULT_OUTPUT = ROOT / "saee_phase2" / "output" / "latest"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SAEE Phase II behavior science analysis")
    parser.add_argument("--source-record", type=Path, default=None)
    parser.add_argument("--seed", type=Path, default=DEFAULT_SEED)
    parser.add_argument("--generations", type=int, default=6)
    parser.add_argument("--initial-population-size", type=int, default=5)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.source_record:
        source = load_record(args.source_record)
    else:
        source = generate_v08_observation(args.seed, args.generations, args.initial_population_size)
    runtime = Phase2BehaviorRuntime()
    record = runtime.analyze_record(source)
    write_outputs(record, args.output_dir)
    summary = record["phase2_summary"]
    if summary["evolution_modified"]:
        raise SystemExit("SAEE_PHASE2_BOOTSTRAP: FAIL evolution was modified")
    if summary["attractor_count"] < 1:
        raise SystemExit("SAEE_PHASE2_BOOTSTRAP: FAIL attractor not identified")
    if summary["dominant_regime"] == "unknown":
        raise SystemExit("SAEE_PHASE2_BOOTSTRAP: FAIL regime classification missing")
    if summary["lineage_node_count"] < 1 or summary["lineage_edge_count"] < 1:
        raise SystemExit("SAEE_PHASE2_BOOTSTRAP: FAIL lineage topology missing")
    if summary["law_count"] < 1:
        raise SystemExit("SAEE_PHASE2_BOOTSTRAP: FAIL evolution laws not extracted")
    print(
        "SAEE_PHASE2_BOOTSTRAP: PASS "
        f"generations={summary['generation_count']} "
        f"attractors={summary['attractor_count']} "
        f"regime={summary['dominant_regime']} "
        f"laws={summary['law_count']} "
        f"analysis_only={summary['analysis_only']} "
        f"output={args.output_dir}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

