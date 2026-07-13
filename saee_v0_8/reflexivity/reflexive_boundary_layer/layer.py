"""Constrain reflexive feedback against identity invariants."""

from __future__ import annotations

import copy
from typing import Any


class ReflexiveBoundaryLayer:
    """Prevent observer feedback from destabilizing identity."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def apply(
        self,
        feedback: dict[str, Any],
        self_model: dict[str, Any],
        identity_snapshot: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        invariant = identity_snapshot["invariant_model"]
        anchor = identity_snapshot["identity_anchor"]
        bounded_feedback = copy.deepcopy(feedback)
        bounded_self_model = copy.deepcopy(self_model)
        anchor_terms = anchor["anchor_terms"]
        bounded_feedback["dominant_terms"] = list(dict.fromkeys(bounded_feedback.get("dominant_terms", []) + anchor_terms[:3]))[:8]
        bounded_feedback["semantic_coherence"] = round(max(float(bounded_feedback["semantic_coherence"]), 0.62), 6)
        bounded_feedback["identity_anchor_id"] = anchor["identity_anchor_id"]
        bounded_feedback["reflexive_boundary"] = "identity_bounded"
        bounded_self_model["dominant_meaning_terms"] = list(
            dict.fromkeys(bounded_self_model.get("dominant_meaning_terms", []) + anchor_terms[:4])
        )[:8]
        bounded_self_model["understanding_quality"] = round(max(float(bounded_self_model["understanding_quality"]), 0.45), 6)
        bounded_self_model["model_history"] = bounded_self_model.get("model_history", [])[-invariant["maximum_recursion_depth"] :]
        bounded_self_model["identity_anchor_id"] = anchor["identity_anchor_id"]
        record = {
            "generation_index": generation_index,
            "identity_anchor_id": anchor["identity_anchor_id"],
            "observer_feedback_bounded": True,
            "maximum_recursion_depth": invariant["maximum_recursion_depth"],
            "bounded_feedback": bounded_feedback,
            "bounded_self_model": bounded_self_model,
            "status": "observer_feedback_identity_bounded",
        }
        self.records.append(record)
        return record

    def export(self) -> list[dict[str, Any]]:
        return list(self.records)

