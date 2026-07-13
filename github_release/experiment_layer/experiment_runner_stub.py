"""Public-safe toy experiment runner for the SAEE abstraction release.

This is not the SAEE kernel. It generates a tiny deterministic observation
sequence for examples and documentation without exposing private evolution
logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ToyExperimentConfig:
    generations: int = 12
    population_size: int = 6


def run_toy_experiment(config: ToyExperimentConfig) -> list[dict[str, float | int | str]]:
    """Return deterministic toy observations.

    The values are illustrative only. They do not expose private evolution logic.
    """

    rows: list[dict[str, float | int | str]] = []
    diversity = 1.0
    signal = 0.2
    for generation in range(config.generations):
        diversity = max(0.25, diversity * 0.88)
        signal = min(1.0, signal + 0.05)
        rows.append(
            {
                "generation": generation,
                "population_size": config.population_size,
                "diversity_proxy": round(diversity, 6),
                "stability_proxy": round(signal, 6),
                "regime_hint": "stable" if diversity < 0.55 else "exploratory",
            }
        )
    return rows
