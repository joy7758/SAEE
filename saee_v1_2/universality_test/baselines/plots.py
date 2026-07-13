"""SVG plots for baseline comparison outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from saee_v1_2.universality_test.common_metrics import clamp


def write_baseline_comparison(path: Path, curves: dict[str, list[float]]) -> None:
    width = 900
    height = 360
    left = 70
    top = 54
    plot_w = width - 110
    plot_h = 230
    colors = {
        "marl_public_goods_q_learning": "#b91c1c",
        "bond_percolation": "#1d4ed8",
        "sir_epidemic": "#047857",
    }
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:18px;font-weight:700}.axis{font-size:11px;fill:#374151}.label{font-size:12px}</style>',
        '<text class="title" x="70" y="30">Baseline transition comparison</text>',
    ]
    for tick in [0, 0.25, 0.50, 0.75, 1.0]:
        y = top + plot_h * (1 - tick)
        lines.append(f'<line x1="{left}" y1="{y:.2f}" x2="{left + plot_w}" y2="{y:.2f}" stroke="#e5e7eb"/>')
        lines.append(f'<text class="axis" x="{left - 36}" y="{y + 4:.2f}">{tick:.2f}</text>')
    legend_x = left
    for name, values in curves.items():
        points = []
        max_step = max(1, len(values) - 1)
        for index, value in enumerate(values):
            x = left + plot_w * index / max_step
            y = top + plot_h * (1 - clamp(float(value)))
            points.append(f"{x:.2f},{y:.2f}")
        color = colors.get(name, "#111827")
        lines.append(f'<polyline fill="none" stroke="{color}" stroke-width="2" points="{" ".join(points)}"/>')
        lines.append(f'<line x1="{legend_x}" y1="{height - 42}" x2="{legend_x + 18}" y2="{height - 42}" stroke="{color}" stroke-width="3"/>')
        lines.append(f'<text class="label" x="{legend_x + 24}" y="{height - 38}">{name}</text>')
        legend_x += 255
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_baseline_heatmaps(path: Path, summary: dict[str, Any]) -> None:
    baselines = list(summary["baselines"])
    fields = ["transition_probability", "native_final_mean"]
    width = 760
    height = 240
    left = 230
    top = 60
    cell_w = 190
    cell_h = 38
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:17px;font-weight:700}.label{font-size:12px}.small{font-size:10px;fill:#374151}</style>',
        '<text class="title" x="24" y="30">Baseline native/transition heatmap</text>',
    ]
    for col, field in enumerate(fields):
        lines.append(f'<text class="label" x="{left + col * cell_w}" y="{top - 16}">{field}</text>')
    for row, baseline in enumerate(baselines):
        y = top + row * cell_h
        lines.append(f'<text class="label" x="24" y="{y + 23}">{baseline}</text>')
        for col, field in enumerate(fields):
            value = summary["baselines"][baseline].get(field)
            numeric = 0.0 if value is None else float(value)
            color = f"rgb({240 - int(100 * numeric)},{248 - int(80 * numeric)},255)"
            x = left + col * cell_w
            lines.append(f'<rect x="{x}" y="{y}" width="{cell_w - 10}" height="{cell_h - 7}" fill="{color}" stroke="#e5e7eb"/>')
            lines.append(f'<text class="small" x="{x + 12}" y="{y + 22}">{numeric:.3f}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

