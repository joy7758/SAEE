"""Interpretation pressure engine."""

from __future__ import annotations

from typing import Any


class InterpretationPressureEngine:
    """Transform feedback and self-model uncertainty into pressure."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    def compute(self, feedback: dict[str, Any], self_model: dict[str, Any], generation_index: int) -> dict[str, Any]:
        pressure = round(
            max(
                0.0,
                min(
                    1.0,
                    feedback["interpretation_pressure"] * 0.60
                    + (1.0 - feedback["semantic_coherence"]) * 0.20
                    + (1.0 - self_model["understanding_quality"]) * 0.20,
                ),
            ),
            6,
        )
        event = {
            "pressure_id": f"interpretation_pressure_g{generation_index:03d}",
            "generation_index": generation_index,
            "feedback_input_id": feedback["feedback_id"],
            "self_model_id": self_model["self_model_id"],
            "interpretation_pressure": pressure,
        }
        self.events.append(event)
        return event

    def export(self) -> list[dict[str, Any]]:
        return list(self.events)
