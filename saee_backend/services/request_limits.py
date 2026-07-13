"""Request resource limits for the SAEE MVP API shell."""

from __future__ import annotations

import json

from saee_backend.config import SETTINGS, SaeeBackendSettings
from saee_backend.models.request import ScenarioBatchRequest


class RequestLimitViolation(ValueError):
    """Raised when a public-shell request exceeds configured bounds."""


def scenario_payload_bytes(req: ScenarioBatchRequest) -> int:
    payload = json.dumps(
        req.model_dump(mode="json"),
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )
    return len(payload.encode("utf-8"))


def validate_scenario_limits(
    req: ScenarioBatchRequest,
    settings: SaeeBackendSettings = SETTINGS,
) -> None:
    agent_count = len(req.agents)
    repeat_runs = req.evaluation_config.repeat_runs
    time_horizon = req.environment.time_horizon
    payload_size = scenario_payload_bytes(req)

    violations: list[str] = []
    if agent_count > settings.max_agents:
        violations.append(f"agents={agent_count} exceeds max_agents={settings.max_agents}")
    if repeat_runs > settings.max_repeat_runs:
        violations.append(
            f"repeat_runs={repeat_runs} exceeds max_repeat_runs={settings.max_repeat_runs}"
        )
    if time_horizon > settings.max_time_horizon:
        violations.append(
            f"time_horizon={time_horizon} exceeds max_time_horizon={settings.max_time_horizon}"
        )
    if payload_size > settings.max_payload_bytes:
        violations.append(
            f"payload_bytes={payload_size} exceeds max_payload_bytes={settings.max_payload_bytes}"
        )
    if violations:
        raise RequestLimitViolation("; ".join(violations))

