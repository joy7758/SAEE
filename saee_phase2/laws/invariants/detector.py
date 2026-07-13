"""Detect empirical invariants in observed runs."""

from __future__ import annotations

from typing import Any


class InvariantDetector:
    """Detect invariants without claiming universal proof."""

    def detect(self, record: dict[str, Any], behavior: dict[str, Any]) -> dict[str, Any]:
        summary = record["stability_summary"]
        invariants = []
        if summary["identity_anchor_hash_count"] == 1:
            invariants.append(
                {
                    "invariant": "single_identity_anchor",
                    "evidence": "identity_anchor_hash_count == 1",
                    "scope": "observed_local_run",
                }
            )
        if summary["max_semantic_drift_after"] <= summary["semantic_drift_threshold"]:
            invariants.append(
                {
                    "invariant": "bounded_semantic_drift",
                    "evidence": "max_semantic_drift_after <= semantic_drift_threshold",
                    "scope": "observed_local_run",
                }
            )
        if all(point["observer_feedback_bounded"] for point in behavior["trajectory"]):
            invariants.append(
                {
                    "invariant": "observer_feedback_bounded_each_generation",
                    "evidence": "all trajectory points record observer_feedback_bounded",
                    "scope": "observed_local_run",
                }
            )
        if summary["continuity_break_count"] == 0:
            invariants.append(
                {
                    "invariant": "lineage_continuity_preserved",
                    "evidence": "continuity_break_count == 0",
                    "scope": "observed_local_run",
                }
            )
        return {
            "analysis_type": "invariant_detection",
            "invariants": invariants,
            "invariant_count": len(invariants),
        }

