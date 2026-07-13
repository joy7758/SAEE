"""Bound semantic drift against the identity kernel."""

from __future__ import annotations

import copy
from typing import Any


class SemanticDriftController:
    """Constrain explanation feedback so meaning cannot drift unboundedly."""

    def __init__(self) -> None:
        self.records: list[dict[str, Any]] = []

    def control(
        self,
        feedback: dict[str, Any],
        identity_snapshot: dict[str, Any],
        generation_index: int,
    ) -> dict[str, Any]:
        bounded = copy.deepcopy(feedback)
        invariant = identity_snapshot["invariant_model"]
        anchor = identity_snapshot["identity_anchor"]
        threshold = invariant["semantic_drift_threshold"]
        terms = [term.lower() for term in bounded.get("dominant_terms", [])]
        reference_terms = [term.lower() for term in anchor["anchor_terms"]]
        overlap = sorted(set(terms) & set(reference_terms))
        drift_before = round(1.0 - len(overlap) / max(1, len(reference_terms)), 6)
        intervention = drift_before > threshold
        if intervention:
            bounded["dominant_terms"] = list(dict.fromkeys(reference_terms[:8] + terms))[:8]
            bounded["semantic_coherence"] = round(max(float(bounded["semantic_coherence"]), 1.0 - threshold), 6)
            bounded["interpretation_pressure"] = round(min(float(bounded["interpretation_pressure"]), 0.72), 6)
            bounded["identity_boundary_applied"] = True
            bounded["identity_anchor_id"] = anchor["identity_anchor_id"]
        bounded_terms = [term.lower() for term in bounded.get("dominant_terms", [])]
        bounded_overlap = sorted(set(bounded_terms) & set(reference_terms))
        drift_after = round(1.0 - len(bounded_overlap) / max(1, len(reference_terms)), 6)
        record = {
            "generation_index": generation_index,
            "feedback_id": feedback["feedback_id"],
            "identity_anchor_id": anchor["identity_anchor_id"],
            "drift_before": drift_before,
            "drift_after": drift_after,
            "threshold": threshold,
            "intervention_applied": intervention,
            "bounded_feedback": bounded,
            "status": "bounded" if drift_after <= threshold else "needs_identity_review",
        }
        self.records.append(record)
        return record

    def export(self) -> list[dict[str, Any]]:
        return list(self.records)
