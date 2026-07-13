"""Switch between evolutionary regimes under phase-transition pressure."""

from __future__ import annotations

from typing import Any


class MetaRegimeSwitchSystem:
    """Map detected phases to distinct evolution-space regimes."""

    def __init__(self) -> None:
        self.history: list[dict[str, Any]] = []

    def resolve(self, phase: dict[str, Any], generation_index: int) -> dict[str, Any]:
        phase_type = phase["phase_type"]
        if phase_type == "collapse_pressure":
            regime = "collapse_reset"
        elif phase_type == "single_niche_to_multi_niche_emergence":
            regime = "diversification"
        elif phase_type == "convergence_to_divergence_shift":
            regime = "exploration"
        elif phase_type == "divergence_to_convergence_shift":
            regime = "optimization"
        elif generation_index % 3 == 0:
            regime = "exploration"
        else:
            regime = "optimization"

        event = {
            "generation_index": generation_index,
            "phase_type": phase_type,
            "regime": regime,
            "reason": self._reason(phase_type, regime),
        }
        self.history.append(event)
        return event

    def export(self) -> list[dict[str, Any]]:
        return list(self.history)

    def _reason(self, phase_type: str, regime: str) -> str:
        if regime == "collapse_reset":
            return "safety_cost_pressure_requires_stability_basin"
        if regime == "diversification":
            return "new_niche_count_requires_multi_niche_manifold"
        if regime == "exploration":
            return "divergent_pressure_requires_operator_discovery"
        return f"{phase_type}_supports_local_refinement"
