"""Independent DBI-2 environment for cross-system parasitic phase testing.

DBI-2 intentionally differs from DBI-1:

- randomized policy vectors instead of fixed cooperative/selfish/mutating types,
- per-agent replication thresholds,
- non-uniform resource nodes,
- small-world interaction graph,
- node-local competition instead of one shared resource pool.

The output schema keeps Phi comparable with DBI-1, but the environment dynamics
are independently implemented.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from typing import Any


REWARD_DRIFT_NORMALIZER = 0.45


@dataclass(frozen=True)
class DBI2Governance:
    name: str
    replication_cap: int | None
    monopoly_penalty: float
    drift_damping: float
    node_claim_cap: float | None


DBI2_GOVERNANCE: dict[str, DBI2Governance] = {
    "none": DBI2Governance(
        name="none",
        replication_cap=None,
        monopoly_penalty=0.0,
        drift_damping=0.0,
        node_claim_cap=None,
    ),
    "weak": DBI2Governance(
        name="weak",
        replication_cap=3,
        monopoly_penalty=0.20,
        drift_damping=0.35,
        node_claim_cap=5.8,
    ),
    "strong": DBI2Governance(
        name="strong",
        replication_cap=1,
        monopoly_penalty=0.55,
        drift_damping=0.82,
        node_claim_cap=3.4,
    ),
}


@dataclass(frozen=True)
class PolicyVector:
    exploration: float
    local_gain: float
    reciprocity: float
    mutation_drive: float

    def normalized(self) -> "PolicyVector":
        total = self.exploration + self.local_gain + self.reciprocity + self.mutation_drive
        if total <= 0:
            return PolicyVector(0.25, 0.25, 0.25, 0.25)
        return PolicyVector(
            self.exploration / total,
            self.local_gain / total,
            self.reciprocity / total,
            self.mutation_drive / total,
        )

    def drift_from(self, baseline: "PolicyVector") -> float:
        current = self.normalized()
        base = baseline.normalized()
        return clamp(
            (
                abs(current.exploration - base.exploration)
                + abs(current.local_gain - base.local_gain)
                + abs(current.reciprocity - base.reciprocity)
                + abs(current.mutation_drive - base.mutation_drive)
            )
            / 2.0
        )

    def to_dict(self) -> dict[str, float]:
        item = self.normalized()
        return {
            "exploration": round(item.exploration, 6),
            "local_gain": round(item.local_gain, 6),
            "reciprocity": round(item.reciprocity, 6),
            "mutation_drive": round(item.mutation_drive, 6),
        }


@dataclass
class ResourceNode:
    node_id: int
    capacity: float
    resources: float
    replenish_rate: float


@dataclass
class DBI2Agent:
    agent_id: str
    lineage_id: str
    node_id: int
    resources: float
    baseline_policy: PolicyVector
    policy: PolicyVector
    replication_threshold: float
    survival_cost: float
    mutation_count: int = 0
    age: int = 0
    parent_id: str | None = None


@dataclass(frozen=True)
class DBI2Config:
    experiment_id: str
    governance: str
    steps: int = 160
    seed: int = 7301
    node_count: int = 34
    initial_agents: int = 42
    neighborhood_degree: int = 4
    rewire_probability: float = 0.18
    initial_agent_resources: float = 4.8
    base_claim: float = 2.25
    mutation_rate: float = 0.075
    phi_threshold: float = 0.60
    transition_slope_threshold: float = 0.0
    max_agents: int = 260
    phi_weights: tuple[float, float, float] = (0.35, 0.35, 0.30)


@dataclass
class DBI2SimulationResult:
    config: DBI2Config
    metrics: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    phase_transition_step: int | None
    transition_event: dict[str, Any] | None

    def summary(self) -> dict[str, Any]:
        final = self.metrics[-1] if self.metrics else {}
        return {
            "schema": "saee.universality_test.dbi2.summary.v1",
            "system": "DBI-2",
            "experiment_id": self.config.experiment_id,
            "governance": self.config.governance,
            "steps": self.config.steps,
            "seed": self.config.seed,
            "phi_threshold": self.config.phi_threshold,
            "phase_transition_step": self.phase_transition_step,
            "transition_event": self.transition_event,
            "final_phi": final.get("phi", 0.0),
            "final_entropy": final.get("entropy", 0.0),
            "final_agent_dominance": final.get("agent_dominance", 0.0),
            "final_resource_concentration": final.get("resource_concentration", 0.0),
            "final_reward_drift": final.get("reward_drift", 0.0),
            "final_population": final.get("population", 0),
            "local_only": True,
            "external_validation_claim": False,
            "production_claim": False,
        }


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def gini(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(max(0.0, value) for value in values)
    total = sum(sorted_values)
    if total <= 0:
        return 0.0
    count = len(sorted_values)
    weighted = sum((index + 1) * value for index, value in enumerate(sorted_values))
    return clamp((2.0 * weighted) / (count * total) - (count + 1.0) / count)


def normalized_entropy(weight_by_lineage: dict[str, float]) -> float:
    total = sum(max(0.0, value) for value in weight_by_lineage.values())
    if total <= 0 or len(weight_by_lineage) <= 1:
        return 0.0
    entropy = 0.0
    for value in weight_by_lineage.values():
        probability = max(0.0, value) / total
        if probability > 0:
            entropy -= probability * math.log(probability)
    return clamp(entropy / math.log(len(weight_by_lineage)))


def normalized_phi_weights(weights: tuple[float, float, float]) -> tuple[float, float, float]:
    positive = tuple(max(0.0, value) for value in weights)
    total = sum(positive)
    if total <= 0:
        return (1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0)
    return (positive[0] / total, positive[1] / total, positive[2] / total)


def phi_payload(
    resource_concentration: float,
    reward_drift: float,
    agent_dominance: float,
    weights: tuple[float, float, float],
) -> dict[str, Any]:
    w_resource, w_reward, w_dominance = normalized_phi_weights(weights)
    components = {
        "resource_concentration": clamp(resource_concentration),
        "reward_drift": clamp(reward_drift),
        "agent_dominance": clamp(agent_dominance),
    }
    weighted = {
        "resource_concentration": w_resource * components["resource_concentration"],
        "reward_drift": w_reward * components["reward_drift"],
        "agent_dominance": w_dominance * components["agent_dominance"],
    }
    return {
        "normalized": True,
        "phi_bounds": [0.0, 1.0],
        "components": {key: round(value, 6) for key, value in components.items()},
        "weights": {
            "resource_concentration": round(w_resource, 6),
            "reward_drift": round(w_reward, 6),
            "agent_dominance": round(w_dominance, 6),
        },
        "weighted_contributions": {
            key: round(value, 6) for key, value in weighted.items()
        },
    }


def phi_from_payload(payload: dict[str, Any]) -> float:
    return clamp(sum(float(value) for value in payload["weighted_contributions"].values()))


class DBI2Simulation:
    def __init__(self, config: DBI2Config) -> None:
        if config.governance not in DBI2_GOVERNANCE:
            raise ValueError(f"unknown DBI-2 governance preset: {config.governance}")
        self.config = config
        self.governance = DBI2_GOVERNANCE[config.governance]
        self.random = random.Random(config.seed)
        self.graph = self._small_world_graph()
        self.nodes = self._resource_nodes()
        self.agents = self._initial_agents()
        self.next_agent_number = len(self.agents) + 1
        self.previous_phi: float | None = None
        self.previous_entropy: float | None = None
        self.phase_transition_step: int | None = None
        self.transition_event: dict[str, Any] | None = None

    def run(self) -> DBI2SimulationResult:
        trace: list[dict[str, Any]] = []
        metrics: list[dict[str, Any]] = []
        for timestep in range(self.config.steps):
            record = self.step(timestep)
            trace.append(record)
            metrics.append(record["metrics"])
        return DBI2SimulationResult(
            config=self.config,
            metrics=metrics,
            trace=trace,
            phase_transition_step=self.phase_transition_step,
            transition_event=self.transition_event,
        )

    def step(self, timestep: int) -> dict[str, Any]:
        replenished = self._replenish_nodes()
        agent_actions: list[dict[str, Any]] = []
        resource_allocations: list[dict[str, Any]] = []
        reward_updates: list[dict[str, Any]] = []
        governance_actions: list[dict[str, Any]] = []
        events: list[dict[str, Any]] = []

        self._move_agents(agent_actions)
        claims_by_node: dict[int, list[tuple[DBI2Agent, float, float]]] = {}
        lineage_resources = self._lineage_resources()
        total_agent_resources = sum(lineage_resources.values())
        for agent in self.agents:
            raw_claim = self._claim(agent)
            claim = raw_claim
            lineage_share = (
                lineage_resources.get(agent.lineage_id, 0.0) / total_agent_resources
                if total_agent_resources > 0
                else 0.0
            )
            if self.governance.monopoly_penalty > 0 and lineage_share > 0.24:
                claim *= 1.0 - self.governance.monopoly_penalty
                governance_actions.append(
                    {
                        "type": "lineage_monopoly_penalty",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "lineage_share": round(lineage_share, 6),
                        "claim_before": round(raw_claim, 6),
                        "claim_after": round(claim, 6),
                    }
                )
            if self.governance.node_claim_cap is not None and claim > self.governance.node_claim_cap:
                governance_actions.append(
                    {
                        "type": "node_claim_cap",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "claim_before": round(claim, 6),
                        "claim_after": round(self.governance.node_claim_cap, 6),
                    }
                )
                claim = self.governance.node_claim_cap
            claims_by_node.setdefault(agent.node_id, []).append((agent, claim, raw_claim))
            agent_actions.append(
                {
                    "agent_id": agent.agent_id,
                    "lineage_id": agent.lineage_id,
                    "node_id": agent.node_id,
                    "claim": round(claim, 6),
                    "raw_claim": round(raw_claim, 6),
                    "policy": agent.policy.to_dict(),
                }
            )

        for node_id, claims in claims_by_node.items():
            total_claim = sum(claim for _, claim, _ in claims)
            node = self.nodes[node_id]
            available = min(node.resources, max(0.0, total_claim))
            node.resources -= available
            for agent, claim, _ in claims:
                allocated = available * claim / total_claim if total_claim > 0 else 0.0
                agent.resources += allocated
                resource_allocations.append(
                    {
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "node_id": node_id,
                        "allocated": round(allocated, 6),
                    }
                )

        survivors = []
        for agent in self.agents:
            agent.resources -= agent.survival_cost
            agent.age += 1
            if agent.resources > 0:
                survivors.append(agent)
            else:
                events.append(
                    {
                        "type": "agent_extinction",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                    }
                )
        self.agents = survivors

        for agent in list(self.agents):
            update = self._adapt_policy(agent, governance_actions)
            if update:
                reward_updates.append(update)

        for agent in list(self.agents):
            children, replication_actions = self._replicate(agent)
            self.agents.extend(children)
            governance_actions.extend(replication_actions)

        metrics = self._metrics()
        if (
            self.phase_transition_step is None
            and metrics["phi"] > self.config.phi_threshold
            and metrics["delta_phi"] > self.config.transition_slope_threshold
        ):
            self.phase_transition_step = timestep
            self.transition_event = {
                "type": "transition_event",
                "phase": "parasitic_phase",
                "timestep": timestep,
                "phi": metrics["phi"],
                "phi_threshold": self.config.phi_threshold,
                "transition_slope": metrics["delta_phi"],
                "slope_threshold": self.config.transition_slope_threshold,
                "pre_transition_entropy": (
                    metrics["entropy"] if self.previous_entropy is None else self.previous_entropy
                ),
                "detector": "phi_above_phi_c_and_positive_slope",
                "rule": "phi > phi_threshold and delta_phi > transition_slope_threshold",
            }
            events.append(self.transition_event)

        self.previous_phi = metrics["phi"]
        self.previous_entropy = metrics["entropy"]
        return {
            "timestep": timestep,
            "environment": {
                "replenished": round(replenished, 6),
                "node_resource_gini": round(gini([node.resources for node in self.nodes]), 6),
            },
            "agent_actions": agent_actions,
            "resource_allocations": resource_allocations,
            "reward_updates": reward_updates,
            "metrics": metrics,
            "governance_actions": governance_actions,
            "events": events,
        }

    def _small_world_graph(self) -> dict[int, set[int]]:
        graph: dict[int, set[int]] = {node_id: set() for node_id in range(self.config.node_count)}
        half_degree = max(1, self.config.neighborhood_degree // 2)
        for node_id in range(self.config.node_count):
            for offset in range(1, half_degree + 1):
                other = (node_id + offset) % self.config.node_count
                graph[node_id].add(other)
                graph[other].add(node_id)
        for node_id in range(self.config.node_count):
            for neighbor in list(graph[node_id]):
                if node_id < neighbor and self.random.random() < self.config.rewire_probability:
                    graph[node_id].discard(neighbor)
                    graph[neighbor].discard(node_id)
                    candidates = [
                        item
                        for item in range(self.config.node_count)
                        if item != node_id and item not in graph[node_id]
                    ]
                    if candidates:
                        new_neighbor = self.random.choice(candidates)
                        graph[node_id].add(new_neighbor)
                        graph[new_neighbor].add(node_id)
        return graph

    def _resource_nodes(self) -> list[ResourceNode]:
        nodes = []
        for node_id in range(self.config.node_count):
            hotspot = 1.0 + (2.2 if node_id % 11 == 0 else 0.0) + self.random.random() * 0.9
            capacity = self.random.uniform(8.0, 18.0) * hotspot
            replenish = self.random.uniform(0.12, 0.56) * hotspot
            nodes.append(
                ResourceNode(
                    node_id=node_id,
                    capacity=capacity,
                    resources=capacity * self.random.uniform(0.45, 0.92),
                    replenish_rate=replenish,
                )
            )
        return nodes

    def _initial_agents(self) -> list[DBI2Agent]:
        agents = []
        for number in range(1, self.config.initial_agents + 1):
            baseline = PolicyVector(
                exploration=self.random.uniform(0.12, 0.42),
                local_gain=self.random.uniform(0.20, 0.56),
                reciprocity=self.random.uniform(0.12, 0.44),
                mutation_drive=self.random.uniform(0.05, 0.26),
            ).normalized()
            agent_id = f"dbi2-{number:04d}"
            agents.append(
                DBI2Agent(
                    agent_id=agent_id,
                    lineage_id=agent_id,
                    node_id=self.random.randrange(self.config.node_count),
                    resources=self.config.initial_agent_resources * self.random.uniform(0.72, 1.35),
                    baseline_policy=baseline,
                    policy=baseline,
                    replication_threshold=self.random.uniform(7.0, 12.5),
                    survival_cost=self.random.uniform(0.82, 1.34),
                )
            )
        return agents

    def _replenish_nodes(self) -> float:
        replenished = 0.0
        for node in self.nodes:
            before = node.resources
            node.resources = min(node.capacity, node.resources + node.replenish_rate)
            replenished += node.resources - before
        return replenished

    def _move_agents(self, agent_actions: list[dict[str, Any]]) -> None:
        for agent in self.agents:
            policy = agent.policy.normalized()
            neighborhood = list(self.graph[agent.node_id]) + [agent.node_id]
            if self.random.random() < policy.exploration:
                target = self.random.choice(neighborhood)
            else:
                target = max(neighborhood, key=lambda node_id: self.nodes[node_id].resources)
            if target != agent.node_id:
                agent_actions.append(
                    {
                        "type": "move",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "from_node": agent.node_id,
                        "to_node": target,
                    }
                )
                agent.node_id = target

    def _claim(self, agent: DBI2Agent) -> float:
        policy = agent.policy.normalized()
        local_resource_pressure = self.nodes[agent.node_id].resources / max(0.01, self.nodes[agent.node_id].capacity)
        multiplier = (
            0.45
            + 1.55 * policy.local_gain
            + 0.95 * policy.mutation_drive
            - 0.25 * policy.reciprocity
            + 0.42 * local_resource_pressure
            + min(0.75, agent.mutation_count * 0.028)
        )
        return max(0.05, self.config.base_claim * multiplier * self.random.uniform(0.90, 1.13))

    def _adapt_policy(
        self,
        agent: DBI2Agent,
        governance_actions: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        policy = agent.policy.normalized()
        pressure = 1.0 + min(2.0, agent.resources / max(0.01, agent.replication_threshold))
        raw_delta = self.config.mutation_rate * pressure * (0.35 + policy.mutation_drive + policy.local_gain)
        delta = raw_delta * (1.0 - self.governance.drift_damping)
        if delta <= 0:
            return None
        if self.governance.drift_damping > 0:
            governance_actions.append(
                {
                    "type": "policy_drift_damping",
                    "agent_id": agent.agent_id,
                    "lineage_id": agent.lineage_id,
                    "raw_delta": round(raw_delta, 6),
                    "damped_delta": round(delta, 6),
                }
            )
        before = policy
        agent.policy = PolicyVector(
            exploration=max(0.01, before.exploration - 0.18 * delta),
            local_gain=before.local_gain + 0.85 * delta,
            reciprocity=max(0.01, before.reciprocity - 0.62 * delta),
            mutation_drive=before.mutation_drive + 0.58 * delta,
        ).normalized()
        agent.mutation_count += 1
        return {
            "agent_id": agent.agent_id,
            "lineage_id": agent.lineage_id,
            "policy_before": before.to_dict(),
            "policy_after": agent.policy.to_dict(),
            "mutation_delta": round(delta, 6),
            "mutation_count": agent.mutation_count,
        }

    def _replicate(self, agent: DBI2Agent) -> tuple[list[DBI2Agent], list[dict[str, Any]]]:
        if len(self.agents) >= self.config.max_agents:
            return [], []
        if agent.resources <= agent.replication_threshold:
            return [], []
        pressure = (agent.resources - agent.replication_threshold) / agent.replication_threshold
        policy = agent.policy.normalized()
        desired = 1 + int(max(0.0, pressure * (0.9 + 1.8 * policy.local_gain + policy.mutation_drive)))
        allowed = desired
        actions: list[dict[str, Any]] = []
        if self.governance.replication_cap is not None:
            allowed = min(allowed, self.governance.replication_cap)
            if allowed < desired:
                actions.append(
                    {
                        "type": "replication_cap",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "desired_children": desired,
                        "allowed_children": allowed,
                    }
                )
        allowed = max(0, min(allowed, self.config.max_agents - len(self.agents)))
        children = []
        for _ in range(allowed):
            child_resources = min(agent.resources * 0.30, agent.replication_threshold * 0.62)
            if child_resources <= 0.1:
                break
            agent.resources -= child_resources
            child_id = f"dbi2-{self.next_agent_number:04d}"
            self.next_agent_number += 1
            child_threshold = max(5.5, agent.replication_threshold * self.random.uniform(0.94, 1.08))
            child = DBI2Agent(
                agent_id=child_id,
                lineage_id=agent.lineage_id,
                node_id=agent.node_id,
                resources=child_resources,
                baseline_policy=agent.baseline_policy,
                policy=agent.policy,
                replication_threshold=child_threshold,
                survival_cost=max(0.55, agent.survival_cost * self.random.uniform(0.96, 1.05)),
                mutation_count=agent.mutation_count,
                parent_id=agent.agent_id,
            )
            children.append(child)
            actions.append(
                {
                    "type": "replication",
                    "parent_id": agent.agent_id,
                    "child_id": child_id,
                    "lineage_id": agent.lineage_id,
                    "node_id": agent.node_id,
                    "child_resources": round(child_resources, 6),
                }
            )
        return children, actions

    def _lineage_resources(self) -> dict[str, float]:
        lineage_resources: dict[str, float] = {}
        for agent in self.agents:
            lineage_resources[agent.lineage_id] = (
                lineage_resources.get(agent.lineage_id, 0.0) + max(0.0, agent.resources)
            )
        return lineage_resources

    def _metrics(self) -> dict[str, Any]:
        lineage_counts: dict[str, int] = {}
        lineage_resources: dict[str, float] = {}
        drift_values = []
        node_occupancy = {node.node_id: 0 for node in self.nodes}
        for agent in self.agents:
            lineage_counts[agent.lineage_id] = lineage_counts.get(agent.lineage_id, 0) + 1
            lineage_resources[agent.lineage_id] = (
                lineage_resources.get(agent.lineage_id, 0.0) + max(0.0, agent.resources)
            )
            drift_values.append(agent.policy.drift_from(agent.baseline_policy))
            node_occupancy[agent.node_id] = node_occupancy.get(agent.node_id, 0) + 1

        population = len(self.agents)
        total_resources = sum(lineage_resources.values())
        dominant_lineage = None
        dominance = 0.0
        dominant_count = 0
        for lineage_id, count in lineage_counts.items():
            count_share = count / population if population else 0.0
            resource_share = lineage_resources.get(lineage_id, 0.0) / total_resources if total_resources > 0 else 0.0
            lineage_dominance = max(count_share, resource_share)
            if lineage_dominance > dominance:
                dominance = lineage_dominance
                dominant_lineage = lineage_id
                dominant_count = count

        agent_resource_gini = gini([agent.resources for agent in self.agents])
        node_resource_gini = gini([node.resources for node in self.nodes])
        occupancy_gini = gini([float(value) for value in node_occupancy.values()])
        resource_concentration = clamp(0.50 * agent_resource_gini + 0.32 * node_resource_gini + 0.18 * occupancy_gini)
        raw_reward_drift = sum(drift_values) / len(drift_values) if drift_values else 0.0
        reward_drift = clamp(raw_reward_drift / REWARD_DRIFT_NORMALIZER)
        entropy = normalized_entropy(lineage_resources)
        phi_components = phi_payload(
            resource_concentration=resource_concentration,
            reward_drift=reward_drift,
            agent_dominance=dominance,
            weights=self.config.phi_weights,
        )
        phi = phi_from_payload(phi_components)
        delta_phi = 0.0 if self.previous_phi is None else phi - self.previous_phi
        return {
            "population": population,
            "resource_concentration": round(resource_concentration, 6),
            "agent_resource_gini": round(agent_resource_gini, 6),
            "node_resource_gini": round(node_resource_gini, 6),
            "occupancy_gini": round(occupancy_gini, 6),
            "reward_drift": round(reward_drift, 6),
            "agent_dominance": round(dominance, 6),
            "dominant_lineage_id": dominant_lineage,
            "dominant_lineage_count": dominant_count,
            "entropy": round(entropy, 6),
            "phi": round(phi, 6),
            "delta_phi": round(delta_phi, 6),
            "phi_components": phi_components,
        }


def run_dbi2_experiment(config: DBI2Config) -> DBI2SimulationResult:
    return DBI2Simulation(config).run()


def clone_config(config: DBI2Config, **overrides: Any) -> DBI2Config:
    data = asdict(config)
    data.update(overrides)
    return DBI2Config(**data)
