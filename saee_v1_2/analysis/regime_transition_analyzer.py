"""Regime transition analysis."""

from __future__ import annotations

from typing import Any

from saee_v1_2.metrics.regime_metrics import regime_series, regime_stability_index, transition_counts


class RegimeTransitionAnalyzer:
    """Measure transition frequencies and probabilities."""

    def analyze(self, trace: list[dict[str, Any]]) -> dict[str, Any]:
        series = regime_series(trace)
        counts = transition_counts(series)
        total = sum(counts.values())
        probabilities = {
            transition: round(count / total, 6) if total else 0.0
            for transition, count in counts.items()
        }
        regimes = sorted({item["regime"] for item in series})
        return {
            "analysis_type": "regime_transition_analysis",
            "regime_series": series,
            "regimes_observed": regimes,
            "transition_counts": counts,
            "transition_probabilities": probabilities,
            "transition_frequency": total,
            "regime_stability_index": regime_stability_index(series),
        }

