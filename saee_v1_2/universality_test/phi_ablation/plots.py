"""SVG plots for Phi ablation outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def write_ablation_heatmap(path: Path, ablations: list[dict[str, Any]]) -> None:
    systems = sorted(ablations[0]["transition_probability_by_system"]) if ablations else []
    cell_w = 118
    cell_h = 34
    left = 210
    top = 64
    width = left + cell_w * len(systems) + 40
    height = top + cell_h * len(ablations) + 64
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:17px;font-weight:700}.label{font-size:12px}.small{font-size:10px;fill:#374151}</style>',
        '<text class="title" x="24" y="30">Phi ablation transition probability heatmap</text>',
    ]
    for index, system in enumerate(systems):
        x = left + index * cell_w + 8
        lines.append(f'<text class="label" x="{x}" y="{top - 18}">{system}</text>')
    for row_index, ablation in enumerate(ablations):
        y = top + row_index * cell_h
        lines.append(f'<text class="label" x="24" y="{y + 22}">{ablation["name"]}</text>')
        for col_index, system in enumerate(systems):
            value = float(ablation["transition_probability_by_system"].get(system, 0.0))
            intensity = int(245 - 165 * value)
            color = f"rgb(254,{max(78, intensity)},{max(78, intensity)})"
            x = left + col_index * cell_w
            lines.append(f'<rect x="{x}" y="{y}" width="{cell_w - 8}" height="{cell_h - 6}" fill="{color}" stroke="#e5e7eb"/>')
            lines.append(f'<text class="small" x="{x + 12}" y="{y + 20}">{value:.3f}</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

