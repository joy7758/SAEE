"""Runtime wrapper for the minimal SAEE empirical simulation."""

from __future__ import annotations

from saee_v1_2.simulator.minimal_evolution_model import MinimalEvolutionModel


def run_saee_simulation(generations: int = 24, population_size: int = 12, dimensions: int = 3, seed: int = 17) -> dict:
    model = MinimalEvolutionModel(population_size=population_size, dimensions=dimensions, seed=seed)
    return model.run(generations)

