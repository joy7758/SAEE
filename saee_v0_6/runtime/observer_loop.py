"""Counter-observer loop for second-order self-observation."""

from __future__ import annotations

import hashlib
from typing import Any


class CounterObserverLoop:
    """Make observation state visible to the next observer pass."""

    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []
        self.current_feedback: dict[str, Any] | None = None

    def before_cycle(self) -> dict[str, Any] | None:
        return self.current_feedback

    def after_cycle(
        self,
        cycle: dict[str, Any],
        observation_event: dict[str, Any],
        self_description: dict[str, Any],
    ) -> dict[str, Any]:
        digest = hashlib.sha256(
            "|".join(
                [
                    cycle["generation_id"],
                    observation_event["event_id"],
                    self_description["description_id"],
                ]
            ).encode("utf-8")
        ).hexdigest()[:10]
        feedback = {
            "observer_event_id": f"observer_loop_g{cycle['generation_index']:03d}_{digest}",
            "generation_index": cycle["generation_index"],
            "observed_observer_event": observation_event["event_id"],
            "self_description_id": self_description["description_id"],
            "second_order_feedback": True,
            "feedback_statement": (
                f"Observer state from {observation_event['event_id']} becomes context "
                f"for the next observation cycle."
            ),
        }
        self.current_feedback = feedback
        self.events.append(feedback)
        return feedback

    def export(self) -> list[dict[str, Any]]:
        return list(self.events)
