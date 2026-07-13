"""Evolutionary Strategy style baseline comparison."""

from __future__ import annotations

from saee_v1_2.baseline.common import run_baseline


def run_es_comparison(
    generations: int = 24,
    population_size: int = 12,
    dimensions: int = 3,
    seed: int = 37,
) -> dict:
    return run_baseline(
        "es",
        generations=generations,
        population_size=population_size,
        dimensions=dimensions,
        seed=seed,
    )
