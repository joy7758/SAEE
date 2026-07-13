"""Regime metrics for local empirical SAEE traces."""

from __future__ import annotations

from typing import Any


def classify_generation(state: dict[str, Any], previous: dict[str, Any] | None = None) -> str:
    masses = [item["mass"] for item in state["population"].values()]
    max_mass = max(masses) if masses else 0.0
    pressure = state["observer"]["reflexive_pressure"]
    population_count = len(masses)
    if population_count <= 3 or max_mass > 0.72:
        return "collapse"
    if pressure > 0.68 and max_mass < 0.25:
        return "chaotic"
    if pressure > 0.45:
        return "exploratory"
    return "stable"


def regime_series(trace: list[dict[str, Any]]) -> list[dict[str, Any]]:
    series = []
    previous = None
    for state in trace:
        regime = classify_generation(state, previous)
        series.append({"generation": state["generation"], "regime": regime})
        previous = state
    return series


def regime_stability_index(series: list[dict[str, Any]]) -> float:
    if len(series) <= 1:
        return 1.0
    transitions = sum(
        1
        for index in range(1, len(series))
        if series[index]["regime"] != series[index - 1]["regime"]
    )
    return round(1.0 - transitions / (len(series) - 1), 6)


def transition_counts(series: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for index in range(1, len(series)):
        key = f"{series[index - 1]['regime']}->{series[index]['regime']}"
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))

