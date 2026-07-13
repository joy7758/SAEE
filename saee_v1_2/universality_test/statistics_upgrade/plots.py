"""SVG plots for statistical upgrade outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from saee_v1_2.universality_test.common_metrics import clamp


def write_sensitivity_surface(path: Path, rows: list[dict[str, Any]]) -> None:
    systems = sorted({row["system_id"] for row in rows})
    thresholds = sorted({row["phi_c_multiplier"] for row in rows})
    width = 760
    height = 100 + 42 * len(systems) * len(thresholds)
    left = 170
    top = 58
    cell_w = 150
    cell_h = 30
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:17px;font-weight:700}.label{font-size:12px}.small{font-size:10px;fill:#374151}</style>',
        '<text class="title" x="24" y="30">Sensitivity surface: transition probability by Phi_c multiplier</text>',
    ]
    for col, threshold in enumerate(thresholds):
        lines.append(f'<text class="label" x="{left + col * cell_w}" y="{top - 16}">Phi_c x {threshold:.2f}</text>')
    row_index = 0
    for system in systems:
        for delay in [0, 2, 5]:
            y = top + row_index * cell_h
            lines.append(f'<text class="label" x="24" y="{y + 20}">{system} delay={delay}</text>')
            for col, threshold in enumerate(thresholds):
                values = [
                    float(row["transition_probability"])
                    for row in rows
                    if row["system_id"] == system
                    and row["governance_delay"] == delay
                    and row["phi_c_multiplier"] == threshold
                ]
                value = sum(values) / len(values) if values else 0.0
                red = 255
                green = int(245 - 150 * clamp(value))
                blue = int(245 - 150 * clamp(value))
                x = left + col * cell_w
                lines.append(f'<rect x="{x}" y="{y}" width="{cell_w - 10}" height="{cell_h - 5}" fill="rgb({red},{green},{blue})" stroke="#e5e7eb"/>')
                lines.append(f'<text class="small" x="{x + 12}" y="{y + 18}">{value:.3f}</text>')
            row_index += 1
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_transition_step_violin(path: Path, grouped: dict[str, dict[str, Any]]) -> None:
    width = 920
    height = 420
    left = 90
    top = 52
    plot_h = 270
    plot_w = width - 150
    items = sorted(grouped)
    max_step = max(
        [
            float(item.get("transition_step_median") or 0.0)
            for item in grouped.values()
        ]
        + [1.0]
    )
    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#111827}.title{font-size:17px;font-weight:700}.axis{font-size:11px;fill:#374151}.label{font-size:10px}</style>',
        '<text class="title" x="70" y="30">Transition-step bootstrap summary</text>',
    ]
    for index, key in enumerate(items):
        x = left + plot_w * (index + 0.5) / max(1, len(items))
        item = grouped[key]
        median = float(item.get("transition_step_median") or 0.0)
        ci = item.get("transition_step_bootstrap_95_ci") or [None, None]
        low = 0.0 if ci[0] is None else float(ci[0])
        high = median if ci[1] is None else float(ci[1])
        y_med = top + plot_h * (1 - median / max_step)
        y_low = top + plot_h * (1 - low / max_step)
        y_high = top + plot_h * (1 - high / max_step)
        lines.append(f'<line x1="{x}" y1="{y_high:.2f}" x2="{x}" y2="{y_low:.2f}" stroke="#6b7280" stroke-width="2"/>')
        lines.append(f'<circle cx="{x}" cy="{y_med:.2f}" r="5" fill="#1d4ed8"/>')
        lines.append(f'<text class="label" x="{x - 34}" y="{top + plot_h + 24}" transform="rotate(35 {x - 34},{top + plot_h + 24})">{key}</text>')
    lines.append(f'<text class="axis" x="30" y="{top + 4}">max {max_step:.0f}</text>')
    lines.append(f'<text class="axis" x="46" y="{top + plot_h + 4}">0</text>')
    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

