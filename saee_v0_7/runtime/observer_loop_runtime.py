"""Observer-loop runtime entrypoint for SAEE v0.7."""

from __future__ import annotations

from typing import Any

from .reflexive_kernel import ReflexiveEvolutionKernel


class ObserverLoopRuntime:
    """Expose the reflexive observer-in-the-loop runtime."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.kernel = ReflexiveEvolutionKernel(seed_genome, initial_population_size)

    def run(self, generations: int) -> dict[str, Any]:
        return self.kernel.run(generations)
