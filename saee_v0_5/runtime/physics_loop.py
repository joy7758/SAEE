"""Open-ended evolution physics loop for SAEE v0.5.

Agent-readable loop:
Novelty detection -> Dimension birth / merge / collapse
-> Evolution law generation -> Phase emergence detection
-> Regime self-construction -> Fitness function generation
-> Generated variation and composition -> Selection mechanism evolution
-> Selection resolution -> Hypergraph lineage update.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from saee_v0_5.emergence.novelty_detector import NoveltyDetector
from saee_v0_5.emergence.phase_emergence_engine import PhaseEmergenceEngine
from saee_v0_5.lineage import HyperGraphLineage
from saee_v0_5.physics.dimension_birth import EvolutionDimensionBirthSystem
from saee_v0_5.physics.evolution_laws import EvolutionLawGenerator
from saee_v0_5.physics.fitness_generators import SelfGeneratedFitnessEngine
from saee_v0_5.physics.regime_constructor import RegimeSelfConstructionEngine
from saee_v0_5.physics.selection_evolution import SelectionMechanismEvolutionLayer


def stable_digest(parts: list[str], size: int = 10) -> str:
    return hashlib.sha256("|".join(str(part) for part in parts).encode("utf-8")).hexdigest()[:size]


class OpenEndedPhysicsLoop:
    """Generate laws, dimensions, fitness, selection, and regimes from observations."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 5) -> None:
        self.population = self._initialize_population(seed_genome, initial_population_size)
        self.novelty = NoveltyDetector()
        self.dimensions = EvolutionDimensionBirthSystem()
        self.law_generator = EvolutionLawGenerator()
        self.fitness_engine = SelfGeneratedFitnessEngine()
        self.selection_evolution = SelectionMechanismEvolutionLayer()
        self.phase_engine = PhaseEmergenceEngine()
        self.regime_constructor = RegimeSelfConstructionEngine()
        self.hypergraph = HyperGraphLineage()
        self.cycles: list[dict[str, Any]] = []
        self.generation_index = 0

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()
        return self.record()

    def step(self) -> dict[str, Any]:
        self.generation_index += 1
        environment = self._abstract_environment(self.generation_index)
        novelty = self.novelty.detect(self.population, environment, self.generation_index)
        observation = self._observe(environment, novelty)
        dimension_state = self.dimensions.update(observation, self.generation_index)
        law = self.law_generator.generate(observation, dimension_state["dimensions"], self.generation_index)
        phase = self.phase_engine.detect(observation, dimension_state["dimensions"], self.generation_index)
        regime = self.regime_constructor.construct(
            law,
            dimension_state["dimensions"],
            phase,
            observation,
            self.generation_index,
        )
        generated_fitness = self.fitness_engine.generate(
            law,
            dimension_state["dimensions"],
            observation,
            self.generation_index,
        )
        candidates, variation_events = self._generate_population_variants(
            law,
            dimension_state["dimensions"],
            regime,
        )
        scored = self.fitness_engine.score(candidates, generated_fitness)
        selection = self.selection_evolution.evolve(
            law,
            generated_fitness,
            observation,
            self.generation_index,
        )
        decision = self.selection_evolution.resolve(scored, selection, observation)
        self.population = self._reconfigure_population(decision)

        cycle = {
            "generation_id": f"v05-generation-{self.generation_index:03d}",
            "generation_index": self.generation_index,
            "environment_state": environment,
            "observation": observation,
            "dimension_state": dimension_state,
            "generated_evolution_law": law,
            "phase_emergence": phase,
            "constructed_regime": regime,
            "generated_fitness_function": generated_fitness,
            "selection_mechanism": selection,
            "variation_events": variation_events,
            "selection_decision": {
                "mechanism_id": decision["mechanism_id"],
                "survival_set": [genome["id"] for genome in decision["survival_set"]],
                "dormant_set": [genome["id"] for genome in decision["dormant_set"]],
                "extinction_set": [genome["id"] for genome in decision["extinction_set"]],
                "revival_set": [genome["id"] for genome in decision["revival_set"]],
            },
            "population": self.population,
        }
        self.cycles.append(cycle)
        self.hypergraph.record_cycle(cycle)
        return cycle

    def record(self) -> dict[str, Any]:
        dimension_events = self.dimensions.export_events()
        regime_data = self.regime_constructor.export()
        phase_events = self.phase_engine.export()
        return {
            "kernel": "SAEE v0.5 Open-Ended Evolution Physics Kernel",
            "version": "0.5.0",
            "status": "local_v0_5_open_ended_physics",
            "generation_id": f"v05-generation-{self.generation_index:03d}",
            "population": self.population,
            "cycles": self.cycles,
            "generated_evolution_laws": self.law_generator.export(),
            "generated_fitness_functions": self.fitness_engine.export(),
            "selection_mechanisms": self.selection_evolution.export(),
            "dimension_state": self.dimensions.snapshot(),
            "dimension_events": dimension_events,
            "regime_construction": regime_data,
            "phase_events": phase_events,
            "hyper_graph": self.hypergraph.export(),
            "open_ended_physics_summary": {
                "generated_law_count": len(self.law_generator.export()),
                "generated_fitness_function_count": len(self.fitness_engine.export()),
                "selection_mechanism_count": len(self.selection_evolution.export()),
                "dimension_birth_count": sum(1 for event in dimension_events if event["event_type"] == "dimension_birth"),
                "dimension_merge_count": sum(1 for event in dimension_events if event["event_type"] == "dimension_merge"),
                "dimension_collapse_count": sum(1 for event in dimension_events if event["event_type"] == "dimension_collapse"),
                "regime_construct_count": sum(1 for event in regime_data["events"] if event["event_type"] == "regime_construct"),
                "regime_regeneration_count": sum(1 for event in regime_data["events"] if event["event_type"] == "regime_regeneration"),
                "regime_collapse_count": sum(1 for event in regime_data["events"] if event["event_type"] == "regime_collapse"),
                "irreversible_phase_count": sum(1 for event in phase_events if event["irreversible"]),
            },
            "boundaries": [
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_external_code_as_genome",
                "no_publication_claim",
                "not_production_runtime",
                "not_verified_true_open_ended_evolution",
                "local_reproducible_simulation_only",
            ],
        }

    def _initialize_population(self, seed_genome: dict[str, Any], size: int) -> list[dict[str, Any]]:
        if size < 4:
            raise ValueError("v0.5 population size must be >= 4")
        founder = self._normalize_genome(seed_genome)
        founder["selection_events"].append({"generation_index": 0, "event": "founder"})
        tokens = self._seed_tokens(founder)
        population = [founder]
        for index, token in enumerate(tokens[: size - 1], start=1):
            child = copy.deepcopy(founder)
            child["id"] = f"{founder['id']}_v05_seed_{stable_digest([token, str(index)], 6)}"
            child["parents"] = [founder["id"]]
            child["version"] = int(founder.get("version", 0)) + 1
            child["selection_events"] = []
            child["traits"].setdefault("generated_traits", [])
            child["traits"]["generated_traits"].append(f"seed_expression::{token}")
            child["mutation_history"] = [
                {
                    "generation_index": 0,
                    "event": "seed_expression_birth",
                    "expression_token": token,
                }
            ]
            population.append(child)
        return population

    def _normalize_genome(self, genome: dict[str, Any]) -> dict[str, Any]:
        normalized = copy.deepcopy(genome)
        normalized.setdefault("id", "saee_seed")
        normalized.setdefault("version", 0)
        normalized.setdefault("parents", [])
        normalized.setdefault("mutation_history", [])
        normalized.setdefault("selection_events", [])
        normalized.setdefault("status", "active")
        normalized.setdefault("traits", {})
        normalized["traits"].setdefault("mutation_scope", [])
        normalized["traits"].setdefault("generated_traits", [])
        normalized["traits"].setdefault("sensing", ["abstract_signal_objects"])
        normalized["traits"].setdefault(
            "constraints",
            ["no_permission_escalation", "no_external_code_execution"],
        )
        return normalized

    def _seed_tokens(self, genome: dict[str, Any]) -> list[str]:
        traits = genome.get("traits", {})
        raw = []
        raw.extend(traits.get("mutation_scope", []))
        raw.extend(traits.get("sensing", []))
        raw.append(str(traits.get("niche_target", "seed")))
        return [
            "".join(ch if ch.isalnum() else "_" for ch in token.lower()).strip("_")
            for token in raw
            if token
        ] or ["seed"]

    def _abstract_environment(self, generation_index: int) -> dict[str, Any]:
        base_signals = [
            ("github", "branch_density", ["branching", f"g{generation_index}_lineage"]),
            ("paper", "method_discontinuity", ["theory_shift", f"novelty_{generation_index % 5}"]),
            ("history", "failure_memory", ["rollback_shadow", f"collapse_{generation_index % 4}"]),
            ("news", "constraint_flux", ["market_pressure", f"pressure_{generation_index % 3}"]),
        ]
        rotation = generation_index % len(base_signals)
        selected = base_signals[rotation:] + base_signals[:rotation]
        signals = [
            {
                "source": source,
                "signal": signal,
                "intensity": round(0.42 + ((generation_index + index) % 5) * 0.11, 2),
                "tags": tags,
            }
            for index, (source, signal, tags) in enumerate(selected[:3])
        ]
        return {
            "environment_id": f"abstract_environment_v05_g{generation_index:03d}",
            "generation_index": generation_index,
            "signal_model": "abstract_signal_objects_only",
            "signal_objects": signals,
        }

    def _observe(self, environment: dict[str, Any], novelty: dict[str, Any]) -> dict[str, Any]:
        active = [genome for genome in self.population if genome.get("status") == "active"]
        scores = [float(genome.get("selection_score", 0.5)) for genome in self.population]
        lineage_span = max((len(genome.get("mutation_history", [])) for genome in self.population), default=0)
        parent_count = Counter(parent for genome in self.population for parent in genome.get("parents", []))
        dominant_tokens = novelty["novel_tokens"][:3] or novelty["tokens"][:3] or ["seed"]
        collapse_pressure = 1.0 if any("collapse_0" in token for token in novelty["tokens"]) else 0.0
        signature = stable_digest([*dominant_tokens, str(lineage_span), f"{novelty['novelty_score']:.4f}"], 12)
        return {
            "observation_id": f"obs_g{self.generation_index:03d}_{signature}",
            "generation_index": self.generation_index,
            "environment_id": environment["environment_id"],
            "novelty": novelty,
            "population_metrics": {
                "population_size": len(self.population),
                "active_ratio": round(len(active) / max(1, len(self.population)), 6),
                "lineage_span": lineage_span,
                "branching_factor": round(sum(parent_count.values()) / max(1, len(parent_count) or 1), 6),
                "score_spread_hint": round((max(scores) - min(scores)) if scores else 0.0, 6),
            },
            "phase_signal": {
                "signature": signature,
                "dominant_tokens": dominant_tokens,
                "collapse_pressure": collapse_pressure,
            },
        }

    def _generate_population_variants(
        self,
        law: dict[str, Any],
        dimensions: dict[str, Any],
        regime: dict[str, Any],
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        candidates = [copy.deepcopy(genome) for genome in self.population if genome.get("status") != "extinct"]
        active = [genome for genome in self.population if genome.get("status") == "active"]
        active_dimensions = [dimension for dimension in dimensions.values() if dimension.get("state") == "active"]
        clauses = law.get("clauses", [])
        events: list[dict[str, Any]] = []
        for index, parent in enumerate(active):
            clause = clauses[index % len(clauses)] if clauses else {"clause_id": "seed_clause", "expression": "seed_expression"}
            dimension = active_dimensions[index % len(active_dimensions)] if active_dimensions else {"dimension_id": "generated_seed_dimension", "source_token": "seed"}
            child = copy.deepcopy(parent)
            expression = f"{clause['clause_id']}::{dimension['source_token']}::{regime['regime_id']}"
            child["id"] = f"{parent['id']}_v05_g{self.generation_index}_{stable_digest([expression, str(index)], 8)}"
            child["parents"] = [parent["id"]]
            child["version"] = int(parent.get("version", 0)) + 1
            child["status"] = "active"
            child["selection_events"] = []
            child.setdefault("mutation_history", [])
            child["mutation_history"].append(
                {
                    "generation_index": self.generation_index,
                    "event": "generated_variation",
                    "source_law": law["law_id"],
                    "source_clause": clause["clause_id"],
                    "source_dimension": dimension["dimension_id"],
                    "source_regime": regime["regime_id"],
                }
            )
            child["traits"].setdefault("generated_traits", [])
            child["traits"]["generated_traits"].append(expression)
            candidates.append(child)
            events.append(
                {
                    "event_type": "generated_variation",
                    "generation_index": self.generation_index,
                    "parent": parent["id"],
                    "child": child["id"],
                    "source_law": law["law_id"],
                    "source_clause": clause["clause_id"],
                    "source_dimension": dimension["dimension_id"],
                }
            )
        if len(active) >= 2 and clauses:
            left, right = active[0], active[-1]
            clause = clauses[-1]
            child = copy.deepcopy(left)
            expression = f"composition::{clause['clause_id']}::{right['id']}::{regime['regime_id']}"
            child["id"] = f"{left['id']}_v05_comp_{stable_digest([expression], 8)}"
            child["parents"] = [left["id"], right["id"]]
            child["version"] = max(int(left.get("version", 0)), int(right.get("version", 0))) + 1
            child["status"] = "active"
            child["selection_events"] = []
            child["traits"].setdefault("generated_traits", [])
            child["traits"]["generated_traits"] = sorted(
                set(left["traits"].get("generated_traits", []))
                | set(right["traits"].get("generated_traits", []))
                | {expression}
            )
            child["mutation_history"] = [
                *left.get("mutation_history", []),
                *right.get("mutation_history", []),
                {
                    "generation_index": self.generation_index,
                    "event": "generated_composition",
                    "source_law": law["law_id"],
                    "source_clause": clause["clause_id"],
                    "source_regime": regime["regime_id"],
                },
            ]
            candidates.append(child)
            events.append(
                {
                    "event_type": "generated_composition",
                    "generation_index": self.generation_index,
                    "parents": child["parents"],
                    "child": child["id"],
                    "source_law": law["law_id"],
                    "source_clause": clause["clause_id"],
                }
            )
        return candidates, events

    def _reconfigure_population(self, decision: dict[str, Any]) -> list[dict[str, Any]]:
        retained: dict[str, dict[str, Any]] = {}
        for key in ("survival_set", "dormant_set", "revival_set"):
            for genome in decision.get(key, []):
                retained[genome["id"]] = copy.deepcopy(genome)
        active = sorted(
            [genome for genome in retained.values() if genome.get("status") == "active"],
            key=lambda genome: (float(genome.get("selection_score", 0.0)), genome["id"]),
            reverse=True,
        )[:12]
        dormant = sorted(
            [genome for genome in retained.values() if genome.get("status") == "dormant"],
            key=lambda genome: genome["id"],
        )[:4]
        return sorted(active + dormant, key=lambda genome: genome["id"])


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "population.json": record["population"],
        "hyper_graph.json": record["hyper_graph"],
        "generated_laws.json": record["generated_evolution_laws"],
        "generated_fitness_functions.json": record["generated_fitness_functions"],
        "selection_mechanisms.json": record["selection_mechanisms"],
        "dimensions.json": {
            "dimensions": record["dimension_state"],
            "events": record["dimension_events"],
        },
        "regimes.json": record["regime_construction"],
        "emergence_report.json": {
            "phase_events": record["phase_events"],
            "summary": record["open_ended_physics_summary"],
        },
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
