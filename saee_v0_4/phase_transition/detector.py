"""Detect ecological phase transitions in population behavior."""

from __future__ import annotations

from statistics import mean
from typing import Any


class EcologicalPhaseTransitionDetector:
    """Classify population-level shifts across mutable fitness geometry."""

    def __init__(self) -> None:
        self.previous: dict[str, Any] | None = None

    def detect(
        self,
        projections: list[dict[str, Any]],
        environment: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        scores = [float(item["fitness_geometry"]["geometry_score"]) for item in projections]
        niches = {item["fitness_geometry"]["niche"] for item in projections}
        dispersion = (max(scores) - min(scores)) if scores else 0.0
        average = mean(scores) if scores else 0.0
        previous_niche_count = int(self.previous.get("niche_count", 0)) if self.previous else 0
        vector = environment.get("pressure_vector", {})

        if vector.get("safety", 0.0) >= 0.78 and vector.get("cost", 0.0) >= 0.55:
            phase_type = "collapse_pressure"
        elif len(niches) >= 3 and previous_niche_count < 3:
            phase_type = "single_niche_to_multi_niche_emergence"
        elif dispersion >= 0.16 or vector.get("novelty", 0.0) + vector.get("market", 0.0) >= 1.20:
            phase_type = "convergence_to_divergence_shift"
        elif dispersion <= 0.055 and generation_index > 1:
            phase_type = "divergence_to_convergence_shift"
        else:
            phase_type = "stability"

        transition = {
            "generation_index": generation_index,
            "phase_type": phase_type,
            "metrics": {
                "population_count": len(projections),
                "niche_count": len(niches),
                "score_average": round(average, 6),
                "score_dispersion": round(dispersion, 6),
                "dominant_dimension": environment.get("dominant_dimension"),
            },
            "previous_phase_type": self.previous.get("phase_type") if self.previous else None,
            "is_phase_shift": self.previous is None or self.previous.get("phase_type") != phase_type,
        }
        self.previous = {
            "phase_type": phase_type,
            "niche_count": len(niches),
            "score_dispersion": dispersion,
        }
        return transition
