"""Shared baseline metrics and graph helpers."""

from __future__ import annotations

from collections import deque
import random
from typing import Any

from saee_v1_2.universality_test.common_metrics import (
    CLAIM_BOUNDARIES,
    clamp,
    detect_transition,
    gini,
    mean,
    pearson,
)


def er_graph(node_count: int, p: float, rng: random.Random) -> dict[int, set[int]]:
    graph = {node: set() for node in range(node_count)}
    for i in range(node_count):
        for j in range(i + 1, node_count):
            if rng.random() < p:
                graph[i].add(j)
                graph[j].add(i)
    for node in range(node_count):
        if not graph[node]:
            other = (node + 1) % node_count
            graph[node].add(other)
            graph[other].add(node)
    return graph


def ws_graph(node_count: int, degree: int, beta: float, rng: random.Random) -> dict[int, set[int]]:
    graph = {node: set() for node in range(node_count)}
    half = max(1, degree // 2)
    for node in range(node_count):
        for offset in range(1, half + 1):
            other = (node + offset) % node_count
            graph[node].add(other)
            graph[other].add(node)
    for node in range(node_count):
        for neighbor in list(graph[node]):
            if node < neighbor and rng.random() < beta:
                graph[node].discard(neighbor)
                graph[neighbor].discard(node)
                candidates = [
                    candidate
                    for candidate in range(node_count)
                    if candidate != node and candidate not in graph[node]
                ]
                if candidates:
                    target = rng.choice(candidates)
                    graph[node].add(target)
                    graph[target].add(node)
    return graph


def component_sizes(graph: dict[int, set[int]]) -> list[int]:
    seen = set()
    sizes = []
    for start in graph:
        if start in seen:
            continue
        queue = deque([start])
        seen.add(start)
        size = 0
        while queue:
            node = queue.popleft()
            size += 1
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.append(neighbor)
        sizes.append(size)
    return sizes


def transition_summary(curve: list[float], threshold: float = 0.60) -> dict[str, Any]:
    event = detect_transition(curve, phi_threshold=threshold, slope_threshold=0.0)
    return {
        "transition_step": None if event is None else event["timestep"],
        "transition_probability": 0 if event is None else 1,
        "transition_event": event,
    }


def mean_curve(curves: list[list[float]]) -> list[float]:
    if not curves:
        return []
    width = min(len(curve) for curve in curves)
    return [
        round(sum(curve[index] for curve in curves) / len(curves), 6)
        for index in range(width)
    ]


def model_similarity(curves_by_model: dict[str, list[float]]) -> list[dict[str, Any]]:
    rows = []
    models = sorted(curves_by_model)
    for left in models:
        for right in models:
            left_curve = curves_by_model[left]
            right_curve = curves_by_model[right]
            width = min(len(left_curve), len(right_curve))
            value = pearson(left_curve[:width], right_curve[:width])
            rows.append(
                {
                    "model_a": left,
                    "model_b": right,
                    "curve_similarity": None if value is None else round(value, 6),
                }
            )
    return rows


def summarize_binary_runs(rows: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(rows)
    transitioned = [row for row in rows if row["transition_step"] is not None]
    steps = [float(row["transition_step"]) for row in transitioned]
    return {
        "num_runs": total,
        "transition_probability": round(len(transitioned) / total, 6) if total else 0.0,
        "mean_transition_step": None if mean(steps) is None else round(mean(steps) or 0.0, 6),
        "native_final_mean": None if mean([row["native_final"] for row in rows]) is None else round(mean([row["native_final"] for row in rows]) or 0.0, 6),
        "claim_boundaries": CLAIM_BOUNDARIES,
    }


def bounded_phi(resource_concentration: float, reward_drift: float, dominance: float) -> float:
    return clamp(0.35 * resource_concentration + 0.35 * reward_drift + 0.30 * dominance)


def concentration_from_values(values: list[float]) -> float:
    return gini([max(0.0, value) for value in values])

