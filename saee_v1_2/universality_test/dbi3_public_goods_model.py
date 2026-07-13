"""DBI-3 public-goods imitation network for reviewer-proofing.

This architecture is intentionally different from DBI-1 and DBI-2:

- graph-local public-goods games,
- cooperate/defect/mutate policy actions,
- logit imitation and lineage replacement,
- ER/WS/BA graph presets,
- governance as an intervention policy rather than a controller claim.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import math
import random
from typing import Any

from saee_v1_2.universality_test.common_metrics import (
    CLAIM_BOUNDARIES,
    clamp,
    detect_transition,
    gini,
    normalized_entropy,
    phi_payload,
    phi_from_components,
)


@dataclass(frozen=True)
class DBI3Governance:
    name: str
    monopoly_tax: float
    mutation_damping: float
    lineage_share_threshold: float
    replacement_cap: int | None


DBI3_GOVERNANCE = {
    "none": DBI3Governance("none", 0.0, 0.0, 1.0, None),
    "weak": DBI3Governance("weak", 0.18, 0.30, 0.24, 2),
    "strong": DBI3Governance("strong", 0.42, 0.70, 0.16, 1),
}


@dataclass(frozen=True)
class DBI3Config:
    experiment_id: str
    governance: str
    graph_preset: str
    seed: int
    steps: int = 200
    node_count: int = 64
    er_p: float = 0.08
    ws_k: int = 4
    ws_beta: float = 0.10
    ba_m: int = 2
    public_goods_multiplier: float = 1.72
    mutation_rate: float = 0.055
    imitation_temperature: float = 0.55
    replication_threshold: float = 9.0
    phi_threshold: float = 0.60
    phi_weights: tuple[float, float, float] = (0.35, 0.35, 0.30)


@dataclass
class DBI3Agent:
    agent_id: str
    lineage_id: str
    node_id: int
    cooperation_prob: float
    mutation_drive: float
    local_gain: float
    baseline_cooperation: float
    baseline_mutation_drive: float
    baseline_local_gain: float
    capital: float = 4.0
    last_payoff: float = 0.0
    mutation_count: int = 0


@dataclass
class DBI3Result:
    config: DBI3Config
    metrics: list[dict[str, Any]]
    trace: list[dict[str, Any]]
    transition_event: dict[str, Any] | None

    @property
    def phase_transition_step(self) -> int | None:
        if self.transition_event is None:
            return None
        return int(self.transition_event["timestep"])

    def summary(self) -> dict[str, Any]:
        final = self.metrics[-1] if self.metrics else {}
        return {
            "schema": "saee.universality_test.dbi3_run_summary.v1",
            "system_id": "DBI-3",
            "dbi3_design": "public_goods_imitation_network",
            "experiment_id": self.config.experiment_id,
            "graph_preset": self.config.graph_preset,
            "governance": self.config.governance,
            "seed": self.config.seed,
            "steps": self.config.steps,
            "transition_step": self.phase_transition_step,
            "transition_event": self.transition_event,
            "final_phi": final.get("phi", 0.0),
            "final_entropy": final.get("entropy", 0.0),
            "final_dominance": final.get("agent_dominance", 0.0),
            "boundaries": CLAIM_BOUNDARIES,
        }


class DBI3Simulation:
    def __init__(self, config: DBI3Config) -> None:
        if config.governance not in DBI3_GOVERNANCE:
            raise ValueError(f"unknown DBI-3 governance: {config.governance}")
        self.config = config
        self.governance = DBI3_GOVERNANCE[config.governance]
        self.random = random.Random(config.seed)
        self.graph = self._make_graph()
        self.agents = self._initial_agents()

    def run(self) -> DBI3Result:
        metrics: list[dict[str, Any]] = []
        trace: list[dict[str, Any]] = []
        transition_event = None
        previous_phi = None
        previous_entropy = None
        for timestep in range(self.config.steps):
            record = self.step(timestep)
            metric = record["metrics"]
            if transition_event is None:
                event = detect_transition(
                    [previous_phi, metric["phi"]] if previous_phi is not None else [metric["phi"]],
                    [previous_entropy, metric["entropy"]]
                    if previous_entropy is not None
                    else [metric["entropy"]],
                    phi_threshold=self.config.phi_threshold,
                )
                if event is not None:
                    transition_event = {
                        **event,
                        "timestep": timestep,
                        "phi": metric["phi"],
                        "transition_slope": metric["delta_phi"],
                        "pre_transition_entropy": metric["entropy"]
                        if previous_entropy is None
                        else previous_entropy,
                    }
                    record["events"].append(transition_event)
            metrics.append(metric)
            trace.append(record)
            previous_phi = metric["phi"]
            previous_entropy = metric["entropy"]
        return DBI3Result(self.config, metrics, trace, transition_event)

    def step(self, timestep: int) -> dict[str, Any]:
        actions = []
        governance_actions = []
        replacement_actions = []
        payoffs = {node_id: 0.0 for node_id in self.graph}
        groups = [[node_id] + sorted(self.graph[node_id]) for node_id in self.graph]

        action_by_node: dict[int, str] = {}
        for agent in self.agents.values():
            action_roll = self.random.random()
            if action_roll < agent.mutation_drive * 0.20:
                action = "mutate_policy"
            elif self.random.random() < agent.cooperation_prob:
                action = "cooperate"
            else:
                action = "defect"
            action_by_node[agent.node_id] = action
            actions.append(
                {
                    "node_id": agent.node_id,
                    "agent_id": agent.agent_id,
                    "lineage_id": agent.lineage_id,
                    "action": action,
                    "cooperation_prob": round(agent.cooperation_prob, 6),
                    "mutation_drive": round(agent.mutation_drive, 6),
                }
            )

        for group in groups:
            contributors = [node for node in group if action_by_node.get(node) == "cooperate"]
            pool = len(contributors)
            benefit = self.config.public_goods_multiplier * pool / max(1, len(group))
            for node_id in group:
                payoff = benefit
                if action_by_node.get(node_id) == "cooperate":
                    payoff -= 0.72
                elif action_by_node.get(node_id) == "mutate_policy":
                    payoff -= 0.24
                payoffs[node_id] += payoff

        lineage_capital = self._lineage_capital()
        total_capital = sum(lineage_capital.values())
        for agent in self.agents.values():
            payoff = payoffs[agent.node_id] + 0.15 * agent.local_gain
            lineage_share = (
                lineage_capital.get(agent.lineage_id, 0.0) / total_capital
                if total_capital > 0
                else 0.0
            )
            if lineage_share > self.governance.lineage_share_threshold and self.governance.monopoly_tax > 0:
                before = payoff
                payoff *= 1.0 - self.governance.monopoly_tax
                governance_actions.append(
                    {
                        "type": "monopoly_tax",
                        "agent_id": agent.agent_id,
                        "lineage_id": agent.lineage_id,
                        "lineage_share": round(lineage_share, 6),
                        "payoff_before": round(before, 6),
                        "payoff_after": round(payoff, 6),
                    }
                )
            agent.last_payoff = payoff
            agent.capital = max(0.0, agent.capital * 0.965 + payoff)

        for agent in list(self.agents.values()):
            if action_by_node.get(agent.node_id) == "mutate_policy":
                self._mutate(agent, governance_actions)

        self._imitate()
        replacement_actions.extend(self._lineage_growth())
        metric = self._metrics()
        return {
            "timestep": timestep,
            "system_id": "DBI-3",
            "graph_preset": self.config.graph_preset,
            "governance": self.config.governance,
            "seed": self.config.seed,
            "agent_actions": actions,
            "governance_actions": governance_actions,
            "replacement_actions": replacement_actions,
            "metrics": metric,
            "events": [],
        }

    def _make_graph(self) -> dict[int, set[int]]:
        preset = self.config.graph_preset.upper()
        if preset == "ER":
            return self._er_graph()
        if preset == "WS":
            return self._ws_graph()
        if preset == "BA":
            return self._ba_graph()
        raise ValueError(f"unknown graph preset: {self.config.graph_preset}")

    def _er_graph(self) -> dict[int, set[int]]:
        graph = {node: set() for node in range(self.config.node_count)}
        for i in range(self.config.node_count):
            for j in range(i + 1, self.config.node_count):
                if self.random.random() < self.config.er_p:
                    graph[i].add(j)
                    graph[j].add(i)
        self._ensure_connectedish(graph)
        return graph

    def _ws_graph(self) -> dict[int, set[int]]:
        graph = {node: set() for node in range(self.config.node_count)}
        half = max(1, self.config.ws_k // 2)
        for node in range(self.config.node_count):
            for offset in range(1, half + 1):
                other = (node + offset) % self.config.node_count
                graph[node].add(other)
                graph[other].add(node)
        for node in range(self.config.node_count):
            for neighbor in list(graph[node]):
                if node < neighbor and self.random.random() < self.config.ws_beta:
                    graph[node].discard(neighbor)
                    graph[neighbor].discard(node)
                    candidates = [
                        item
                        for item in range(self.config.node_count)
                        if item != node and item not in graph[node]
                    ]
                    if candidates:
                        new_neighbor = self.random.choice(candidates)
                        graph[node].add(new_neighbor)
                        graph[new_neighbor].add(node)
        self._ensure_connectedish(graph)
        return graph

    def _ba_graph(self) -> dict[int, set[int]]:
        graph = {node: set() for node in range(self.config.node_count)}
        m = max(1, self.config.ba_m)
        for i in range(m + 1):
            for j in range(i + 1, m + 1):
                graph[i].add(j)
                graph[j].add(i)
        targets = list(range(m + 1))
        for node in range(m + 1, self.config.node_count):
            degrees = [len(graph[target]) + 1 for target in targets]
            chosen = set()
            while len(chosen) < m:
                total = sum(degrees)
                roll = self.random.uniform(0, total)
                acc = 0.0
                for target, degree in zip(targets, degrees):
                    acc += degree
                    if acc >= roll:
                        chosen.add(target)
                        break
            for target in chosen:
                graph[node].add(target)
                graph[target].add(node)
            targets.append(node)
        self._ensure_connectedish(graph)
        return graph

    def _ensure_connectedish(self, graph: dict[int, set[int]]) -> None:
        for node in range(self.config.node_count):
            if not graph[node]:
                other = (node + 1) % self.config.node_count
                graph[node].add(other)
                graph[other].add(node)

    def _initial_agents(self) -> dict[int, DBI3Agent]:
        agents = {}
        for node in range(self.config.node_count):
            coop = self.random.uniform(0.30, 0.78)
            mutation = self.random.uniform(0.04, 0.24)
            local_gain = self.random.uniform(0.20, 0.66)
            agents[node] = DBI3Agent(
                agent_id=f"dbi3-{node:04d}",
                lineage_id=f"dbi3-{node:04d}",
                node_id=node,
                cooperation_prob=coop,
                mutation_drive=mutation,
                local_gain=local_gain,
                baseline_cooperation=coop,
                baseline_mutation_drive=mutation,
                baseline_local_gain=local_gain,
                capital=self.random.uniform(3.0, 5.5),
            )
        return agents

    def _mutate(self, agent: DBI3Agent, governance_actions: list[dict[str, Any]]) -> None:
        raw_delta = self.config.mutation_rate * (1.0 + agent.local_gain + agent.mutation_drive)
        delta = raw_delta * (1.0 - self.governance.mutation_damping)
        if self.governance.mutation_damping > 0:
            governance_actions.append(
                {
                    "type": "mutation_damping",
                    "agent_id": agent.agent_id,
                    "lineage_id": agent.lineage_id,
                    "raw_delta": round(raw_delta, 6),
                    "damped_delta": round(delta, 6),
                }
            )
        agent.cooperation_prob = clamp(agent.cooperation_prob - 0.65 * delta, 0.01, 0.99)
        agent.local_gain = clamp(agent.local_gain + delta, 0.01, 0.99)
        agent.mutation_drive = clamp(agent.mutation_drive + 0.35 * delta, 0.01, 0.99)
        agent.mutation_count += 1

    def _imitate(self) -> None:
        for node, agent in list(self.agents.items()):
            if not self.graph[node]:
                continue
            other_node = self.random.choice(list(self.graph[node]))
            other = self.agents[other_node]
            diff = other.last_payoff - agent.last_payoff
            probability = 1.0 / (1.0 + math.exp(-diff / max(0.05, self.config.imitation_temperature)))
            if self.random.random() < probability:
                blend = 0.12
                agent.lineage_id = other.lineage_id
                agent.cooperation_prob = clamp((1 - blend) * other.cooperation_prob + blend * agent.cooperation_prob)
                agent.local_gain = clamp((1 - blend) * other.local_gain + blend * agent.local_gain)
                agent.mutation_drive = clamp((1 - blend) * other.mutation_drive + blend * agent.mutation_drive)

    def _lineage_growth(self) -> list[dict[str, Any]]:
        actions = []
        replacements_by_lineage: dict[str, int] = {}
        for node, agent in sorted(self.agents.items()):
            if agent.capital < self.config.replication_threshold:
                continue
            if not self.graph[node]:
                continue
            if (
                self.governance.replacement_cap is not None
                and replacements_by_lineage.get(agent.lineage_id, 0) >= self.governance.replacement_cap
            ):
                continue
            target_node = min(self.graph[node], key=lambda item: self.agents[item].capital)
            target = self.agents[target_node]
            if target.lineage_id == agent.lineage_id:
                continue
            old_lineage = target.lineage_id
            target.lineage_id = agent.lineage_id
            target.cooperation_prob = clamp(agent.cooperation_prob * self.random.uniform(0.96, 1.04))
            target.local_gain = clamp(agent.local_gain * self.random.uniform(0.97, 1.05))
            target.mutation_drive = clamp(agent.mutation_drive * self.random.uniform(0.96, 1.06))
            target.capital = max(target.capital, agent.capital * 0.35)
            agent.capital *= 0.72
            replacements_by_lineage[agent.lineage_id] = replacements_by_lineage.get(agent.lineage_id, 0) + 1
            actions.append(
                {
                    "type": "lineage_replacement",
                    "source_node": node,
                    "target_node": target_node,
                    "lineage_id": agent.lineage_id,
                    "old_lineage_id": old_lineage,
                }
            )
        return actions

    def _lineage_capital(self) -> dict[str, float]:
        output: dict[str, float] = {}
        for agent in self.agents.values():
            output[agent.lineage_id] = output.get(agent.lineage_id, 0.0) + max(0.0, agent.capital)
        return output

    def _metrics(self) -> dict[str, Any]:
        lineage_counts: dict[str, int] = {}
        lineage_capital = self._lineage_capital()
        drift_values = []
        for agent in self.agents.values():
            lineage_counts[agent.lineage_id] = lineage_counts.get(agent.lineage_id, 0) + 1
            drift = (
                abs(agent.cooperation_prob - agent.baseline_cooperation)
                + abs(agent.mutation_drive - agent.baseline_mutation_drive)
                + abs(agent.local_gain - agent.baseline_local_gain)
            ) / 1.6
            drift_values.append(clamp(drift))
        total_capital = sum(lineage_capital.values())
        dominance = 0.0
        dominant_lineage = None
        for lineage_id, count in lineage_counts.items():
            count_share = count / max(1, self.config.node_count)
            capital_share = lineage_capital.get(lineage_id, 0.0) / total_capital if total_capital > 0 else 0.0
            score = max(count_share, capital_share)
            if score > dominance:
                dominance = score
                dominant_lineage = lineage_id
        resource_concentration = gini([agent.capital for agent in self.agents.values()])
        reward_drift = sum(drift_values) / len(drift_values) if drift_values else 0.0
        entropy = normalized_entropy(lineage_capital)
        payload = phi_payload(resource_concentration, reward_drift, dominance, self.config.phi_weights)
        phi = phi_from_components(resource_concentration, reward_drift, dominance, self.config.phi_weights)
        previous_phi = getattr(self, "_previous_phi", None)
        delta_phi = 0.0 if previous_phi is None else phi - previous_phi
        self._previous_phi = phi
        return {
            "population": self.config.node_count,
            "resource_concentration": round(resource_concentration, 6),
            "reward_drift": round(reward_drift, 6),
            "agent_dominance": round(dominance, 6),
            "dominant_lineage_id": dominant_lineage,
            "entropy": round(entropy, 6),
            "phi": round(phi, 6),
            "delta_phi": round(delta_phi, 6),
            "phi_components": payload,
        }


def clone_config(config: DBI3Config, **overrides: Any) -> DBI3Config:
    data = asdict(config)
    data.update(overrides)
    return DBI3Config(**data)
