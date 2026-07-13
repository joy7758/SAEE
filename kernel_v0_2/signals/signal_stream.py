"""Local abstract environmental signal layer for SAEE Kernel v0.2."""

from __future__ import annotations

from typing import Any


class AbstractSignalStream:
    """Produce local signal objects without external API calls."""

    def collect(self, generation_id: int) -> dict[str, Any]:
        signals = [
            self._signal("github", "repo_growth", 0.58 + (0.04 * (generation_id % 3)), ["technical", "evolvability"]),
            self._signal("github", "issue_cluster", 0.42 + (0.03 * (generation_id % 2)), ["technical", "safety"]),
            self._signal("news", "regulation_shift", 0.48 + (0.05 * (generation_id % 4)), ["safety"]),
            self._signal("news", "enterprise_adoption", 0.50 + (0.02 * generation_id), ["market"]),
            self._signal("history", "past_failure", 0.60 + (0.02 * (generation_id % 2)), ["safety", "rollback"]),
            self._signal("paper", "paper_trend", 0.52 + (0.03 * (generation_id % 5)), ["novelty", "evolvability"]),
        ]
        return {
            "generation_id": generation_id,
            "signal_mode": "abstract_local",
            "signals": signals,
            "boundaries": [
                "no_real_api_calls",
                "no_network_access",
                "abstract_signal_objects_only",
            ],
        }

    def _signal(self, source: str, signal_type: str, intensity: float, tags: list[str]) -> dict[str, Any]:
        return {
            "source": source,
            "signal_type": signal_type,
            "intensity": round(min(1.0, intensity), 4),
            "tags": tags,
        }


class SignalInterpreter:
    """Convert abstract signals into an environment state."""

    def interpret(self, packet: dict[str, Any]) -> dict[str, Any]:
        generation_id = int(packet["generation_id"])
        vector = {
            "technical": 0.0,
            "market": 0.0,
            "safety": 0.0,
            "novelty": 0.0,
            "evolvability": 0.0,
            "rollback": 0.0,
        }
        tag_counts = {key: 0 for key in vector}

        for signal in packet["signals"]:
            for tag in signal["tags"]:
                if tag in vector:
                    vector[tag] += float(signal["intensity"])
                    tag_counts[tag] += 1

        for key, value in vector.items():
            count = tag_counts[key]
            vector[key] = round(value / count, 4) if count else 0.0

        dominant = sorted(
            packet["signals"],
            key=lambda signal: (signal["intensity"], signal["signal_type"]),
            reverse=True,
        )[:4]

        return {
            "environment_id": f"env-g{generation_id:03d}",
            "generation_id": generation_id,
            "signal_mode": packet["signal_mode"],
            "signals": packet["signals"],
            "dominant_pressures": [signal["signal_type"] for signal in dominant],
            "pressure_vector": vector,
            "carrying_capacity": 4 + (generation_id % 2),
            "extinction_threshold": 0.50,
            "dormancy_threshold": 0.46,
            "revival_pressure": vector["rollback"] >= 0.60 or generation_id % 2 == 0,
            "boundaries": packet["boundaries"],
        }

