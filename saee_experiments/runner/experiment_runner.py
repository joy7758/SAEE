"""Long-horizon experiment runner for SAEE v1.0.

The runner is observation-only. It executes the immutable v1.0 runtime and
returns the resulting record without mutating kernel code or feeding analysis
back into the evolution loop.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from saee_v1_0.runtime.saee_runtime import load_seed, run_runtime


class ExperimentRunner:
    """Execute SAEE v1.0 for a configured number of generations."""

    def run(self, config: dict[str, Any], root: Path) -> dict[str, Any]:
        generation_count = int(config["generation_count"])
        if generation_count < 100 or generation_count > 10000:
            raise ValueError("generation_count must be between 100 and 10000")
        if config.get("deterministic_seed") != "enabled":
            raise ValueError("deterministic_seed must be enabled")
        if config.get("logging_level") != "full_trace":
            raise ValueError("logging_level must be full_trace")
        population_size = int(config["population_size"])
        seed_path = root / str(config["seed_path"])
        seed = load_seed(seed_path)
        record = run_runtime(seed, generation_count, population_size)
        return {
            "experiment_type": "saee_v1_0_long_horizon",
            "constitution": {
                "kernel": "saee_v1_0",
                "kernel_modified": False,
                "single_loop_only": record["loop_count"] == 1,
                "single_fitness_function_only": record["fitness_model"] == "single_unified_fitness",
                "single_population_pool_only": record["population_model"] == "single_population_pool",
                "single_lineage_dag_only": record["lineage_model"] == "single_lineage_dag",
                "observer_feedback_into_kernel": False,
                "new_evolution_mechanics": False,
            },
            "config": dict(config),
            "kernel_record": record,
        }


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the constrained key-value YAML used by experiment configs."""

    config: dict[str, Any] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"invalid config line: {line}")
        key, raw_value = stripped.split(":", 1)
        value = raw_value.strip()
        if value.isdigit():
            config[key.strip()] = int(value)
        else:
            config[key.strip()] = value
    required = {"generation_count", "population_size", "deterministic_seed", "logging_level", "seed_path", "output_dir"}
    missing = required - set(config)
    if missing:
        raise ValueError("missing config keys: " + ", ".join(sorted(missing)))
    return config
