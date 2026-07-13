"""Shared metrics for SAEE universality reviewer-proofing outputs."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
import random
import statistics
from typing import Any, Iterable


CLAIM_BOUNDARIES = {
    "synthetic_only": True,
    "real_world_validated": False,
    "production_ready": False,
    "universality_claim": False,
}


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def mean(values: Iterable[float]) -> float | None:
    items = list(values)
    if not items:
        return None
    return sum(items) / len(items)


def variance(values: Iterable[float]) -> float | None:
    items = list(values)
    if not items:
        return None
    if len(items) == 1:
        return 0.0
    return statistics.variance(items)


def median(values: Iterable[float]) -> float | None:
    items = list(values)
    if not items:
        return None
    return statistics.median(items)


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * q
    low = math.floor(position)
    high = math.ceil(position)
    if low == high:
        return ordered[int(position)]
    return ordered[low] * (high - position) + ordered[high] * (position - low)


def bootstrap_ci(
    values: list[float],
    resamples: int = 5000,
    seed: int = 20260706,
    statistic: str = "mean",
) -> list[float | None]:
    if not values:
        return [None, None]
    rng = random.Random(seed)
    stats = []
    for _ in range(resamples):
        sample = [values[rng.randrange(len(values))] for _ in values]
        if statistic == "median":
            stats.append(float(statistics.median(sample)))
        else:
            stats.append(sum(sample) / len(sample))
    low = percentile(stats, 0.025)
    high = percentile(stats, 0.975)
    return [
        None if low is None else round(low, 6),
        None if high is None else round(high, 6),
    ]


def bernoulli_bootstrap_ci(
    successes: int,
    total: int,
    resamples: int = 5000,
    seed: int = 20260706,
) -> list[float | None]:
    if total <= 0:
        return [None, None]
    values = [1.0] * successes + [0.0] * (total - successes)
    return bootstrap_ci(values, resamples=resamples, seed=seed, statistic="mean")


def gini(values: list[float]) -> float:
    if not values:
        return 0.0
    ordered = sorted(max(0.0, value) for value in values)
    total = sum(ordered)
    if total <= 0:
        return 0.0
    count = len(ordered)
    weighted = sum((index + 1) * value for index, value in enumerate(ordered))
    return clamp((2.0 * weighted) / (count * total) - (count + 1.0) / count)


def normalized_entropy(weight_by_lineage: dict[str, float]) -> float:
    total = sum(max(0.0, value) for value in weight_by_lineage.values())
    if total <= 0 or len(weight_by_lineage) <= 1:
        return 0.0
    entropy = 0.0
    for value in weight_by_lineage.values():
        probability = max(0.0, value) / total
        if probability > 0:
            entropy -= probability * math.log(probability)
    return clamp(entropy / math.log(len(weight_by_lineage)))


def phi_from_components(
    resource_concentration: float,
    reward_drift: float,
    agent_dominance: float,
    weights: tuple[float, float, float] = (0.35, 0.35, 0.30),
) -> float:
    positive = tuple(max(0.0, value) for value in weights)
    total = sum(positive)
    if total <= 0:
        normalized = (1 / 3, 1 / 3, 1 / 3)
    else:
        normalized = (positive[0] / total, positive[1] / total, positive[2] / total)
    return clamp(
        clamp(resource_concentration) * normalized[0]
        + clamp(reward_drift) * normalized[1]
        + clamp(agent_dominance) * normalized[2]
    )


def phi_payload(
    resource_concentration: float,
    reward_drift: float,
    agent_dominance: float,
    weights: tuple[float, float, float] = (0.35, 0.35, 0.30),
) -> dict[str, Any]:
    positive = tuple(max(0.0, value) for value in weights)
    total = sum(positive)
    if total <= 0:
        normalized = (1 / 3, 1 / 3, 1 / 3)
    else:
        normalized = (positive[0] / total, positive[1] / total, positive[2] / total)
    components = {
        "resource_concentration": clamp(resource_concentration),
        "reward_drift": clamp(reward_drift),
        "agent_dominance": clamp(agent_dominance),
    }
    weighted = {
        "resource_concentration": components["resource_concentration"] * normalized[0],
        "reward_drift": components["reward_drift"] * normalized[1],
        "agent_dominance": components["agent_dominance"] * normalized[2],
    }
    return {
        "normalized": True,
        "phi_bounds": [0.0, 1.0],
        "components": {key: round(value, 6) for key, value in components.items()},
        "weights": {
            "resource_concentration": round(normalized[0], 6),
            "reward_drift": round(normalized[1], 6),
            "agent_dominance": round(normalized[2], 6),
        },
        "weighted_contributions": {
            key: round(value, 6) for key, value in weighted.items()
        },
    }


def detect_transition(
    phi_curve: list[float],
    entropy_curve: list[float] | None = None,
    phi_threshold: float = 0.60,
    slope_threshold: float = 0.0,
) -> dict[str, Any] | None:
    previous_phi: float | None = None
    previous_entropy: float | None = None
    for timestep, phi in enumerate(phi_curve):
        delta = 0.0 if previous_phi is None else phi - previous_phi
        if phi > phi_threshold and delta > slope_threshold:
            return {
                "type": "transition_event",
                "phase": "parasitic_phase",
                "timestep": timestep,
                "phi": round(phi, 6),
                "phi_threshold": phi_threshold,
                "transition_slope": round(delta, 6),
                "pre_transition_entropy": (
                    None
                    if entropy_curve is None
                    else round(
                        entropy_curve[timestep]
                        if previous_entropy is None
                        else previous_entropy,
                        6,
                    )
                ),
            }
        previous_phi = phi
        if entropy_curve is not None:
            previous_entropy = entropy_curve[timestep]
    return None


def rank_correlation(a_values: list[float], b_values: list[float]) -> float | None:
    if len(a_values) != len(b_values) or len(a_values) < 2:
        return None

    def ranks(values: list[float]) -> list[float]:
        order = sorted(range(len(values)), key=lambda index: values[index])
        output = [0.0] * len(values)
        for rank, index in enumerate(order):
            output[index] = float(rank)
        return output

    return pearson(ranks(a_values), ranks(b_values))


def pearson(a_values: list[float], b_values: list[float]) -> float | None:
    if len(a_values) != len(b_values) or len(a_values) < 2:
        return None
    mean_a = sum(a_values) / len(a_values)
    mean_b = sum(b_values) / len(b_values)
    numerator = sum((a - mean_a) * (b - mean_b) for a, b in zip(a_values, b_values))
    denom_a = sum((a - mean_a) ** 2 for a in a_values)
    denom_b = sum((b - mean_b) ** 2 for b in b_values)
    if denom_a <= 0 or denom_b <= 0:
        return None
    return numerator / math.sqrt(denom_a * denom_b)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def svg_line_chart(
    path: Path,
    title: str,
    panels: list[dict[str, Any]],
    width: int = 980,
    panel_height: int = 150,
) -> None:
    margin_left = 72
    margin_top = 58
    gap = 54
    height = margin_top + len(panels) * (panel_height + gap) + 34
    plot_width = width - margin_left - 34
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:18px;font-weight:700}.axis{font-size:11px;fill:#374151}.panel{font-size:13px;font-weight:700}.grid{stroke:#e5e7eb;stroke-width:1}.axisline{stroke:#9ca3af;stroke-width:1}.boundary{stroke:#111827;stroke-width:1.2;stroke-dasharray:6 5}</style>',
        f'<text class="title" x="{margin_left}" y="28">{title}</text>',
    ]
    for panel_index, panel in enumerate(panels):
        y0 = margin_top + panel_index * (panel_height + gap)
        y1 = y0 + panel_height
        x0 = margin_left
        x1 = x0 + plot_width
        lines.append(f'<text class="panel" x="{x0}" y="{y0 - 14}">{panel["label"]}</text>')
        for tick in [0.0, 0.25, 0.50, 0.75, 1.0]:
            y = y1 - panel_height * tick
            lines.append(f'<line class="grid" x1="{x0}" y1="{y:.2f}" x2="{x1}" y2="{y:.2f}"/>')
            lines.append(f'<text class="axis" x="{x0 - 34}" y="{y + 4:.2f}">{tick:.2f}</text>')
        if panel.get("threshold") is not None:
            threshold = float(panel["threshold"])
            y = y1 - panel_height * clamp(threshold)
            lines.append(f'<line class="boundary" x1="{x0}" y1="{y:.2f}" x2="{x1}" y2="{y:.2f}"/>')
            lines.append(f'<text class="axis" x="{x1 - 64}" y="{y - 7:.2f}">Phi_c={threshold:.2f}</text>')
        lines.append(f'<line class="axisline" x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}"/>')
        lines.append(f'<line class="axisline" x1="{x0}" y1="{y0}" x2="{x0}" y2="{y1}"/>')
        max_len = max((len(series["values"]) for series in panel["series"]), default=1)
        max_step = max(1, max_len - 1)
        legend_x = x0
        for series in panel["series"]:
            values = series["values"]
            points = []
            for index, value in enumerate(values):
                x = x0 + plot_width * index / max_step
                y = y1 - panel_height * clamp(float(value))
                points.append(f"{x:.2f},{y:.2f}")
            color = series.get("color", "#111827")
            lines.append(
                f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(points)}"/>'
            )
            lines.append(f'<line x1="{legend_x}" y1="{y1 + 22}" x2="{legend_x + 18}" y2="{y1 + 22}" stroke="{color}" stroke-width="3"/>')
            lines.append(f'<text class="axis" x="{legend_x + 24}" y="{y1 + 26}">{series["name"]}</text>')
            legend_x += 190
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
