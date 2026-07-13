"""Generate long-horizon experiment reports."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class ExperimentReportGenerator:
    """Write reports required by the long-horizon experiment layer."""

    def write_reports(
        self,
        output_dir: Path,
        experiment_record: dict[str, Any],
        stability: dict[str, Any],
        drift: dict[str, Any],
        emergence: dict[str, Any],
    ) -> None:
        reports_dir = output_dir / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        lineage_statistics = self._lineage_statistics(experiment_record)
        (reports_dir / "stability_report.json").write_text(
            json.dumps(stability, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (reports_dir / "lineage_statistics.json").write_text(
            json.dumps(lineage_statistics, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        collapse_lines = [
            json.dumps(event, sort_keys=True)
            for event in stability["collapse_events"]
        ]
        (reports_dir / "collapse_events.log").write_text(
            "\n".join(collapse_lines) + ("\n" if collapse_lines else ""),
            encoding="utf-8",
        )
        (reports_dir / "evolution_summary.md").write_text(
            self._summary_markdown(experiment_record, stability, drift, emergence, lineage_statistics),
            encoding="utf-8",
        )

    def _lineage_statistics(self, experiment_record: dict[str, Any]) -> dict[str, Any]:
        lineage = experiment_record["kernel_record"]["lineage_dag"]
        node_ids = {node["id"] for node in lineage["nodes"]}
        edge_endpoints_exist = all(edge["from"] in node_ids and edge["to"] in node_ids for edge in lineage["edges"])
        return {
            "graph_type": lineage["graph_type"],
            "node_count": len(lineage["nodes"]),
            "edge_count": len(lineage["edges"]),
            "branching_density": round(len(lineage["edges"]) / max(1, len(lineage["nodes"])), 6),
            "lineage_integrity_preserved": lineage["graph_type"] == "lineage_dag" and edge_endpoints_exist,
            "single_lineage_dag": lineage["graph_type"] == "lineage_dag",
        }

    def _summary_markdown(
        self,
        experiment_record: dict[str, Any],
        stability: dict[str, Any],
        drift: dict[str, Any],
        emergence: dict[str, Any],
        lineage_statistics: dict[str, Any],
    ) -> str:
        kernel = experiment_record["kernel_record"]
        return (
            "# SAEE v1.0 Long-Horizon Evolution Experiment\n\n"
            "Status: local-only observational experiment.\n\n"
            "## Constitution\n\n"
            "- Kernel modified: false\n"
            "- New evolution mechanics: false\n"
            "- Observer feedback into kernel: false\n"
            f"- Core loop count: {kernel['loop_count']}\n"
            f"- Fitness model: {kernel['fitness_model']}\n"
            f"- Lineage model: {kernel['lineage_model']}\n\n"
            "## Results\n\n"
            f"- Generations: {kernel['generation_count']}\n"
            f"- Final population: {len(kernel['population'])}\n"
            f"- Collapse events: {stability['collapse_event_count']}\n"
            f"- Fitness variance tendency: {stability['convergence_tendency']}\n"
            f"- Lineage nodes: {lineage_statistics['node_count']}\n"
            f"- Lineage edges: {lineage_statistics['edge_count']}\n"
            f"- Mean population turnover: {drift['mean_population_turnover']}\n"
            f"- Emergence patterns: {len(emergence['repeated_patterns'])}\n\n"
            "## Boundary\n\n"
            "This experiment layer is passive. It records and analyzes the v1.0 runtime; it does not feed results back into the kernel.\n"
        )
