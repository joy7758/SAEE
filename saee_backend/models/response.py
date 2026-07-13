"""Public response models for the SAEE MVP API shell."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AgentScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    final_score: float = Field(ge=0.0, le=1.0)


class OverallStats(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mean_stability: float = Field(ge=0.0, le=1.0)
    mean_survival: float = Field(ge=0.0, le=1.0)
    divergence_index: float = Field(ge=0.0, le=1.0)


class EvaluationRunSummary(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    run_id: str
    status: Literal["completed", "running", "failed"]
    agents: list[AgentScore]
    overall_stats: OverallStats
    decision_result: DecisionResult | None = None
    recommended_agent: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class StabilityReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    stability_score: float = Field(ge=0.0, le=1.0)
    drift_rate: float = Field(ge=0.0)
    variance: float = Field(ge=0.0)
    convergence_status: Literal["stable", "unstable", "collapsing"]
    time_series: list[float]


class FailureMode(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: Literal["drift", "collapse", "oscillation", "degeneration"]
    step: int = Field(ge=0)
    severity: float = Field(ge=0.0, le=1.0)
    description: str


class FailureModeReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    failure_modes: list[FailureMode]


class SurvivalPoint(BaseModel):
    model_config = ConfigDict(extra="forbid")

    t: int = Field(ge=0)
    alive: bool
    score: float = Field(ge=0.0, le=1.0)


class SurvivalCurve(BaseModel):
    model_config = ConfigDict(extra="forbid")

    agent_id: str
    curve: list[SurvivalPoint]


class RankingItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int = Field(ge=1)
    agent_id: str
    score: float = Field(ge=0.0, le=1.0)


class ComparisonRanking(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    ranking: list[RankingItem]


class ExperimentListItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    status: Literal["created", "completed", "running", "failed"]
    recommended_agent: str | None = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)


class ExperimentListResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiments: list[ExperimentListItem]
    count: int = Field(ge=0)


class DecisionResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    recommended_agent: str | None
    confidence_score: float = Field(ge=0.0, le=1.0)
    ranking: list[RankingItem]
    failure_modes_summary: dict[str, list[str]]


class ExperimentCreateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    experiment_id: str
    status: Literal["created"]
