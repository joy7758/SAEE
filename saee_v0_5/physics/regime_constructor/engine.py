"""Construct regimes from attractor signatures instead of enum names."""

from __future__ import annotations

import hashlib
from typing import Any


def _digest(parts: list[str], size: int = 10) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:size]


class RegimeSelfConstructionEngine:
    """Generate emergent regimes from laws, dimensions, and phase signals."""

    def __init__(self) -> None:
        self.current: dict[str, Any] | None = None
        self.regimes: list[dict[str, Any]] = []
        self.events: list[dict[str, Any]] = []

    def construct(
        self,
        law: dict[str, Any],
        dimensions: dict[str, Any],
        phase_event: dict[str, Any],
        observation: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        active_dimensions = [item for item in dimensions.values() if item.get("state") == "active"]
        attractor_terms = [
            phase_event["phase_id"],
            law["law_id"],
            *[dimension["dimension_id"] for dimension in active_dimensions[:4]],
        ]
        digest = _digest(attractor_terms)
        event_type = "regime_construct"
        parents = [self.current["regime_id"]] if self.current else []
        if self.current and phase_event.get("irreversible"):
            self.events.append(
                {
                    "event_type": "regime_collapse",
                    "generation_index": generation_index,
                    "regime_id": self.current["regime_id"],
                    "reason": phase_event["transition_id"],
                }
            )
            event_type = "regime_regeneration"
        regime = {
            "regime_id": f"regime_g{generation_index:03d}_{digest}",
            "generation_index": generation_index,
            "parents": parents,
            "origin_law": law["law_id"],
            "origin_phase": phase_event["phase_id"],
            "attractor_vector": {
                "active_dimension_count": len(active_dimensions),
                "collapse_pressure": observation["phase_signal"]["collapse_pressure"],
                "novelty_score": observation["novelty"]["novelty_score"],
                "branching_factor": observation["population_metrics"]["branching_factor"],
            },
            "construction_event": event_type,
        }
        self.current = regime
        self.regimes.append(regime)
        self.events.append(
            {
                "event_type": event_type,
                "generation_index": generation_index,
                "regime_id": regime["regime_id"],
                "parents": parents,
            }
        )
        return regime

    def export(self) -> dict[str, Any]:
        return {
            "regimes": list(self.regimes),
            "events": list(self.events),
        }
