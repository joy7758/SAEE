"""Public v0.5 open-ended evolution kernel wrapper."""

from __future__ import annotations

from typing import Any

from .physics_loop import OpenEndedPhysicsLoop


class OpenEndedEvolutionKernel:
    """Thin wrapper around the generated evolution physics loop."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.loop = OpenEndedPhysicsLoop(seed_genome, initial_population_size)

    def run(self, generations: int) -> dict[str, Any]:
        return self.loop.run(generations)
