#!/usr/bin/env python3
"""Generate TikZ figures from frozen SAEE JSON artifacts only."""

from __future__ import annotations

import json
import math
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PAPER_DIR = SCRIPT_DIR.parent if SCRIPT_DIR.name == "supplement" else SCRIPT_DIR
DATA = SCRIPT_DIR if SCRIPT_DIR.name == "supplement" else PAPER_DIR / "supplement"
OUT = PAPER_DIR / "figures"


def load(path: str):
    return json.loads((DATA / path).read_text(encoding="utf-8"))


def scale(value: float, low: float, high: float, size: float) -> float:
    return (value - low) / (high - low) * size


def coords(points):
    return " ".join(f"({x:.4f},{y:.4f})" for x, y in points)


def write_long_horizon() -> None:
    stability = load("stability_report.json")
    drift = load("drift_report.json")
    fitness = stability["fitness_over_time"]
    turnover = drift["population_divergence"]

    width = 12.0
    height = 2.2
    x = lambda generation: scale(generation, 1, 100, width)

    min_fit = min(row["min_fitness"] for row in fitness)
    max_fit = max(row["max_fitness"] for row in fitness)
    pad = (max_fit - min_fit) * 0.04
    fit_low, fit_high = min_fit - pad, max_fit + pad
    fit_y = lambda value: scale(value, fit_low, fit_high, height)

    upper = [(x(row["generation_index"]), fit_y(row["max_fitness"])) for row in fitness]
    lower = [(x(row["generation_index"]), fit_y(row["min_fitness"])) for row in reversed(fitness)]
    mean = [(x(row["generation_index"]), fit_y(row["mean_fitness"])) for row in fitness]

    variances = [max(row["fitness_variance"], 1e-10) for row in fitness]
    log_low = math.floor(math.log10(min(variances)))
    log_high = math.ceil(math.log10(max(variances)))
    var_y = lambda value: scale(math.log10(max(value, 1e-10)), log_low, log_high, height)
    var_points = [(x(row["generation_index"]), var_y(row["fitness_variance"])) for row in fitness]
    turnover_points = [
        (x(row["generation_index"]), scale(row["population_turnover"], 0, 1, height))
        for row in turnover
    ]

    lines = [
        "\\begin{tikzpicture}[x=0.68cm,y=0.68cm,font=\\sffamily\\scriptsize]",
        "% Panel A",
        "\\begin{scope}[shift={(0,6.1)}]",
        "\\draw[->] (0,0) -- (12.35,0);",
        "\\draw[->] (0,0) -- (0,2.45);",
        f"\\fill[blue!12] {coords(upper + lower)} -- cycle;",
        f"\\draw[blue!75!black,thick] plot[smooth] coordinates {{{coords(mean)}}};",
        "\\node[anchor=west,font=\\sffamily\\bfseries\\scriptsize] at (0,2.55) {(a) fitness range and mean};",
        f"\\node[anchor=east] at (-0.12,0) {{{fit_low:.3f}}};",
        f"\\node[anchor=east] at (-0.12,2.2) {{{fit_high:.3f}}};",
        "\\end{scope}",
        "% Panel B",
        "\\begin{scope}[shift={(0,3.05)}]",
        "\\draw[->] (0,0) -- (12.35,0);",
        "\\draw[->] (0,0) -- (0,2.45);",
        f"\\draw[red!75!black,thick] plot coordinates {{{coords(var_points)}}};",
        "\\node[anchor=west,font=\\sffamily\\bfseries\\scriptsize] at (0,2.55) {(b) fitness variance (log scale)};",
        f"\\node[anchor=east] at (-0.12,0) {{$10^{{{log_low}}}$}};",
        f"\\node[anchor=east] at (-0.12,2.2) {{$10^{{{log_high}}}$}};",
        "\\end{scope}",
        "% Panel C",
        "\\begin{scope}[shift={(0,0)}]",
        "\\draw[->] (0,0) -- (12.35,0);",
        "\\draw[->] (0,0) -- (0,2.45);",
        f"\\draw[teal!70!black,thick] plot coordinates {{{coords(turnover_points)}}};",
        "\\draw[densely dashed,gray] (0,1.2) -- (12,1.2);",
        "\\node[anchor=west,font=\\sffamily\\bfseries\\scriptsize] at (0,2.55) {(c) genome-set turnover};",
        "\\node[anchor=east] at (-0.12,0) {0};",
        "\\node[anchor=east] at (-0.12,2.2) {1};",
        "\\foreach \\g in {1,25,50,75,100} {\\pgfmathsetmacro{\\gx}{(\\g-1)/99*12} \\draw (\\gx,0) -- (\\gx,-0.08) node[below]{\\g};}",
        "\\end{scope}",
        "\\end{tikzpicture}",
        "",
    ]
    (OUT / "long_horizon_trace.tex").write_text("\n".join(lines), encoding="utf-8")


def write_lineage_phase2() -> None:
    projection = load("lineage_plot_projection.json")
    phase2 = load("cross_generation_drift.json")

    width, height = 8.0, 5.0

    lines = [
        "\\begin{tikzpicture}[x=0.72cm,y=0.72cm,font=\\sffamily\\scriptsize]",
        "\\begin{scope}",
        "\\draw[->] (0,0) -- (8.25,0);",
        "\\draw[->] (0,0) -- (0,5.25);",
        "\\node[anchor=west,font=\\sffamily\\bfseries\\scriptsize] at (0,5.38) {(a) 808-node / 1,590-edge lineage surface};",
    ]
    for source_x, source_y, target_x, target_y in projection["edges"]:
        lines.append(
            f"\\draw[gray!55,opacity=0.10,line width=0.12pt] ({source_x:.4f},{source_y:.4f}) -- ({target_x:.4f},{target_y:.4f});"
        )
    for point_set, color, size in (
        (projection["other_nodes"], "gray!55", "0.25pt"),
        (projection["survivor_nodes"], "blue!80!black", "0.42pt"),
    ):
        for px, py in point_set:
            lines.append(f"\\fill[{color},opacity=0.72] ({px:.4f},{py:.4f}) circle ({size});")
    lines.extend([
        "\\foreach \\g in {1,25,50,75,100} {\\pgfmathsetmacro{\\gx}{(\\g-1)/99*8} \\draw (\\gx,0) -- (\\gx,-0.08) node[below]{\\g};}",
        "\\end{scope}",
        "\\begin{scope}[shift={(9.6,0)}]",
        "\\draw[->] (0,0) -- (5.3,0);",
        "\\draw[->] (0,0) -- (0,5.25);",
        "\\node[anchor=west,font=\\sffamily\\bfseries\\scriptsize] at (0,5.38) {(b) six-point Phase II record};",
    ])
    drift_points = []
    for row in phase2["semantic_drift"]:
        drift_points.append((scale(row["generation_index"], 1, 6, 5.0), scale(row["semantic_drift_after"], 0, 0.4, height)))
    threshold_y = scale(0.32, 0, 0.4, height)
    lines.extend([
        f"\\draw[densely dashed,red!70!black] (0,{threshold_y:.4f}) -- (5,{threshold_y:.4f}) node[right]{{bound 0.32}};",
        f"\\draw[blue!80!black,thick] plot coordinates {{{coords(drift_points)}}};",
    ])
    for px, py in drift_points:
        lines.append(f"\\fill[blue!80!black] ({px:.4f},{py:.4f}) circle (1.7pt);")
    lines.extend([
        "\\foreach \\g in {1,...,6} {\\pgfmathsetmacro{\\gx}{(\\g-1)/5*5} \\draw (\\gx,0) -- (\\gx,-0.08) node[below]{\\g};}",
        "\\foreach \\v/\\label in {0/0,2.5/0.2,5/0.4} {\\draw (0,\\v) -- (-0.08,\\v) node[left]{\\label};}",
        "\\node[align=left,anchor=north west] at (0.15,1.85) {signature support: 6/6\\\\regime labels: stable 6/6\\\\cross-regime transitions: 0};",
        "\\end{scope}",
        "\\end{tikzpicture}",
        "",
    ])
    (OUT / "lineage_phase2.tex").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    write_long_horizon()
    write_lineage_phase2()


if __name__ == "__main__":
    main()
