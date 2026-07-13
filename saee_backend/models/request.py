"""Public request models for the SAEE MVP API shell."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from saee_backend.services.public_input_contract import (
    validate_public_identifier,
    validate_secret_free_config,
)


class AgentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    agent_id: str = Field(min_length=1)
    config: str | dict[str, Any]
    type: Literal["llm", "rule", "workflow", "agent"]

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, value: str) -> str:
        return validate_public_identifier(value, field_name="agent_id")

    @field_validator("config")
    @classmethod
    def validate_config_secret_boundary(cls, value: str | dict[str, Any]):
        validate_secret_free_config(value)
        return value


class EnvironmentConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    scenario_type: str = Field(min_length=1)
    noise_level: float = Field(ge=0.0, le=1.0)
    competition_intensity: float = Field(ge=0.0, le=1.0)
    time_horizon: int = Field(ge=1, le=100_000)

    @field_validator("scenario_type")
    @classmethod
    def validate_scenario_type(cls, value: str) -> str:
        return validate_public_identifier(value, field_name="scenario_type")


class EvaluationConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    metrics: list[Literal["stability", "survival", "failure_mode", "ranking"]] = Field(
        min_length=1
    )
    repeat_runs: int = Field(ge=1, le=10_000)


class ScenarioBatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    experiment_id: str | None = Field(default=None, min_length=1)
    agents: list[AgentConfig] = Field(min_length=1, max_length=100)
    environment: EnvironmentConfig
    evaluation_config: EvaluationConfig

    @field_validator("experiment_id")
    @classmethod
    def validate_experiment_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_public_identifier(value, field_name="experiment_id")

    @model_validator(mode="after")
    def validate_unique_agents(self):
        agent_ids = [agent.agent_id for agent in self.agents]
        if len(agent_ids) != len(set(agent_ids)):
            raise ValueError("agent_id values must be unique")
        return self


class ExperimentCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)

    experiment_id: str | None = Field(default=None, min_length=1)
    name: str | None = Field(default=None, min_length=1, max_length=128)
    description: str | None = Field(default=None, max_length=128)
    owner_label: str | None = Field(default=None, max_length=128)
    created_by: str | None = Field(default=None, max_length=128)

    @field_validator("experiment_id")
    @classmethod
    def validate_create_experiment_id(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_public_identifier(value, field_name="experiment_id")

    @field_validator("name", "owner_label", "created_by")
    @classmethod
    def validate_create_public_label(cls, value: str | None, info) -> str | None:
        if value is None:
            return None
        return validate_public_identifier(value, field_name=info.field_name)

    @field_validator("description")
    @classmethod
    def validate_create_public_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return validate_public_identifier(value, field_name="description")
