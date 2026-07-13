"""Abstract local sensorium for SAEE v0.3."""

from __future__ import annotations

from typing import Any


class AbstractSensorium:
    """Produce deterministic signal objects without external API calls."""

    def sense(self, generation_index: int) -> dict[str, Any]:
        signals = [
            self._signal("github", "repo_growth", 0.55 + 0.03 * (generation_index % 4), ["technical", "evolvability"]),
            self._signal("github", "pr_pattern", 0.45 + 0.02 * (generation_index % 3), ["technical", "coordination"]),
            self._signal("news", "regulation_shift", 0.50 + 0.04 * (generation_index % 3), ["safety"]),
            self._signal("news", "market_pull", 0.52 + 0.03 * (generation_index % 5), ["market"]),
            self._signal("history", "past_failure", 0.58 + 0.02 * (generation_index % 2), ["rollback", "safety"]),
            self._signal("paper", "framework_trend", 0.51 + 0.04 * (generation_index % 4), ["novelty", "evolvability"]),
        ]
        return {
            "signal_mode": "abstract_local",
            "generation_index": generation_index,
            "signals": signals,
            "boundaries": [
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "abstract_signal_objects_only",
            ],
        }

    def interpret(self, packet: dict[str, Any], rule_genome: dict[str, Any]) -> dict[str, Any]:
        vector = {
            "technical": 0.0,
            "market": 0.0,
            "safety": 0.0,
            "novelty": 0.0,
            "evolvability": 0.0,
            "rollback": 0.0,
            "coordination": 0.0,
        }
        counts = {key: 0 for key in vector}
        for signal in packet["signals"]:
            for tag in signal["tags"]:
                if tag in vector:
                    vector[tag] += signal["intensity"]
                    counts[tag] += 1
        for key in vector:
            vector[key] = round(vector[key] / counts[key], 4) if counts[key] else 0.0

        dominant = sorted(
            packet["signals"],
            key=lambda signal: (signal["intensity"], signal["signal_type"]),
            reverse=True,
        )[:4]
        selection = rule_genome["selection"]
        return {
            "environment_id": f"v03-env-{packet['generation_index']:03d}",
            "generation_index": packet["generation_index"],
            "signal_mode": packet["signal_mode"],
            "signals": packet["signals"],
            "pressure_vector": vector,
            "dominant_pressures": [signal["signal_type"] for signal in dominant],
            "carrying_capacity": int(selection["carrying_capacity"]),
            "extinction_threshold": float(selection["extinction_threshold"]),
            "dormancy_threshold": float(selection["dormancy_threshold"]),
            "revival_pressure": vector["rollback"] >= 0.58,
            "boundaries": packet["boundaries"],
        }

    def _signal(self, source: str, signal_type: str, intensity: float, tags: list[str]) -> dict[str, Any]:
        return {
            "source": source,
            "signal_type": signal_type,
            "intensity": round(min(1.0, intensity), 4),
            "tags": tags,
        }

