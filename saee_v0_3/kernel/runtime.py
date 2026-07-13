"""SAEE v0.3 meta-evolution runtime.

Final goal:
sense environment -> generate variations -> simulate futures -> select survivors
-> update lineage -> modify its own evolution rules under drift guards.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

from saee_v0_3.evolution_engine.counterfactual import CounterfactualRuleSimulator
from saee_v0_3.fitness.landscape import V03FitnessLandscape
from saee_v0_3.genome.contracts import default_rule_genome
from saee_v0_3.lineage.dag import V03LineageDAG
from saee_v0_3.meta_evolution.drift_guard import DriftGuard
from saee_v0_3.meta_evolution.rule_engine import MetaEvolutionRuleEngine
from saee_v0_3.population.pool import PopulationPoolV03
from saee_v0_3.selection.pressure import V03SelectionPressure
from saee_v0_3.sensors.abstract_sensorium import AbstractSensorium


class SAEEV03Runtime:
    """Closed-loop local meta-evolution kernel."""

    def __init__(self, seed_genome: dict[str, Any], initial_population_size: int = 4) -> None:
        self.population_pool = PopulationPoolV03()
        self.sensorium = AbstractSensorium()
        self.fitness = V03FitnessLandscape()
        self.selection = V03SelectionPressure()
        self.lineage = V03LineageDAG()
        self.rule_engine = MetaEvolutionRuleEngine()
        self.counterfactual = CounterfactualRuleSimulator()
        self.drift_guard = DriftGuard()
        self.rule_genome = default_rule_genome()
        self.population = self.population_pool.initialize(seed_genome, size=initial_population_size)
        self.cycles: list[dict[str, Any]] = []
        self.generation_index = 0
        self.lineage.record_population(self.population, self.generation_index)
        self.lineage.record_rule(self.rule_genome, self.generation_index)

    def run(self, generations: int) -> dict[str, Any]:
        if generations < 1:
            raise ValueError("generations must be >= 1")
        for _ in range(generations):
            self.step()
        record = self._record(status="local_v0_3_meta_evolution")
        record["drift_guard"] = self.drift_guard.validate(record, self.rule_genome)
        return record

    def step(self) -> dict[str, Any]:
        self.generation_index += 1
        packet = self.sensorium.sense(self.generation_index)
        environment = self.sensorium.interpret(packet, self.rule_genome)
        candidates, branch_events = self.population_pool.expand(self.population, environment, self.rule_genome)
        self.lineage.record_events(branch_events)
        scored = self.fitness.score(candidates, environment, self.rule_genome)
        decision = self.selection.resolve(scored, environment, self.population)
        self.lineage.record_selection(decision, self.generation_index)
        self.population = self.population_pool.reconfigure(decision)

        meta_event = self._meta_evolve(environment)
        cycle = {
            "generation_id": f"v03-generation-{self.generation_index:03d}",
            "environment_state": environment,
            "active_rule_genome": self.rule_genome["id"],
            "branch_events": branch_events,
            "fitness_scores": [
                {
                    "genome_id": item["genome"]["id"],
                    "fitness": item["fitness"],
                }
                for item in scored
            ],
            "selection_pressure": {
                "survival_set": [genome["id"] for genome in decision["survival_set"]],
                "extinction_set": [genome["id"] for genome in decision["extinction_set"]],
                "dormant_set": [genome["id"] for genome in decision["dormant_set"]],
                "revival_set": [genome["id"] for genome in decision["revival_set"]],
            },
            "meta_evolution": meta_event,
            "population_size": len(self.population),
        }
        self.cycles.append(cycle)
        return cycle

    def _meta_evolve(self, environment: dict[str, Any]) -> dict[str, Any]:
        candidate_rule = self.rule_engine.propose(self.rule_genome, self.generation_index, environment)
        baseline_record = self._counterfactual_record(self.rule_genome, environment, "baseline_rule_trial")
        candidate_record = self._counterfactual_record(candidate_rule, environment, "candidate_rule_trial")
        comparison = self.counterfactual.compare(baseline_record, candidate_record)
        adopted = comparison["adopt_candidate"]
        if adopted:
            self.rule_genome = candidate_rule
            self.lineage.record_rule(self.rule_genome, self.generation_index)
        return {
            "candidate_rule_id": candidate_rule["id"],
            "adopted": adopted,
            "comparison": comparison,
        }

    def _counterfactual_record(self, rule: dict[str, Any], environment: dict[str, Any], label: str) -> dict[str, Any]:
        trial_population = copy.deepcopy(self.population)
        candidates, events = self.population_pool.expand(trial_population, environment, rule)
        scored = self.fitness.score(candidates, environment, rule)
        decision = self.selection.resolve(scored, environment, trial_population)
        next_population = self.population_pool.reconfigure(decision)
        lineage_edges = len(events) + sum(len(genome.get("parents", [])) for genome in next_population)
        return {
            "label": label,
            "population": next_population,
            "lineage_graph": {
                "edges": [{} for _ in range(lineage_edges)],
            },
            "cycles": [
                {
                    "environment_state": environment,
                    "fitness_scores": [
                        {
                            "genome_id": item["genome"]["id"],
                            "fitness": item["fitness"],
                        }
                        for item in scored
                    ],
                    "selection_pressure": {
                        "survival_set": [genome["id"] for genome in decision["survival_set"]],
                        "extinction_set": [genome["id"] for genome in decision["extinction_set"]],
                        "dormant_set": [genome["id"] for genome in decision["dormant_set"]],
                        "revival_set": [genome["id"] for genome in decision["revival_set"]],
                    },
                }
            ],
        }

    def _record(self, status: str) -> dict[str, Any]:
        return {
            "kernel": "SAEE v0.3 Meta-Evolution Kernel",
            "version": "0.3.0",
            "status": status,
            "generation_id": f"v03-generation-{self.generation_index:03d}",
            "population": self.population,
            "rule_genome": self.rule_genome,
            "lineage_graph": self.lineage.export(),
            "cycles": self.cycles,
            "boundaries": [
                "abstract_signal_objects_only",
                "no_real_api_calls",
                "no_network_access",
                "no_external_repo_execution",
                "no_permission_expansion",
                "no_publication_claim",
                "not_production_runtime",
                "not_unbounded_self_modification",
            ],
        }


def load_seed(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_outputs(record: dict[str, Any], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        "run_record.json": record,
        "population.json": record["population"],
        "lineage_graph.json": record["lineage_graph"],
        "rule_genome.json": record["rule_genome"],
        "drift_guard.json": record["drift_guard"],
    }
    for name, payload in outputs.items():
        (output_dir / name).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

