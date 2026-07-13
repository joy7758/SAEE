"""Controlled local Agent Rehearsal Runtime MVP.

The runtime executes one repository-controlled synthetic policy Agent against
strict local scenarios and in-memory tools. It never starts subprocesses,
opens network connections, writes files, imports plugins, or executes external
Agent code. Its evidence export is a candidate binding, not established
evidence or a readiness decision.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
SCENARIO_DIRECTORY = ROOT / "agent-interface/rehearsal/scenarios"
SCENARIO_SCHEMA_PATH = ROOT / "agent-interface/rehearsal/saee-agent-rehearsal-scenario.v0.1.schema.json"
RUN_SCHEMA_PATH = ROOT / "agent-interface/rehearsal/saee-agent-rehearsal-run.v0.1.schema.json"


class RehearsalRuntimeError(ValueError):
    """Stable fail-closed Runtime error."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise RehearsalRuntimeError(code, detail)


def _canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _path_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "REHEARSAL_JSON_ROOT_INVALID", str(path))
    return value


def _resolve_scenario(path: Path) -> Path:
    resolved = path.resolve()
    try:
        resolved.relative_to(SCENARIO_DIRECTORY.resolve())
    except ValueError as exc:
        raise RehearsalRuntimeError("REHEARSAL_SCENARIO_OUTSIDE_ALLOWLIST", str(path)) from exc
    _require(resolved.parent == SCENARIO_DIRECTORY.resolve(), "REHEARSAL_SCENARIO_OUTSIDE_ALLOWLIST", str(path))
    _require(resolved.is_file() and resolved.suffix == ".json", "REHEARSAL_SCENARIO_MISSING", str(path))
    return resolved


def _validate_scenario(scenario: dict[str, Any]) -> None:
    validator = Draft202012Validator(_load_json(SCENARIO_SCHEMA_PATH), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(scenario), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = "/" + "/".join(str(item) for item in first.absolute_path)
        raise RehearsalRuntimeError("REHEARSAL_SCENARIO_SCHEMA_INVALID", f"{path}: {first.message}")

    sandbox = scenario["sandbox"]
    for field in ("network_allowed", "subprocess_allowed", "filesystem_write_allowed"):
        _require(sandbox[field] is False, "REHEARSAL_SANDBOX_BOUNDARY_OPEN", field)
    _require(sandbox["synthetic"] is True, "REHEARSAL_NON_SYNTHETIC_SANDBOX", scenario["scenario_id"])
    _require(scenario["agent_adapter"]["synthetic"] is True, "REHEARSAL_EXTERNAL_ADAPTER_FORBIDDEN", scenario["scenario_id"])
    _require(scenario["expected_outcome"]["external_effect_expected"] is False, "REHEARSAL_EXTERNAL_EFFECT_FORBIDDEN", scenario["scenario_id"])


def _event(run_id: str, sequence: int, timestamp: str, event_type: str, summary: str) -> dict[str, Any]:
    return {
        "event_id": f"event:{run_id.split(':', 1)[1]}:{sequence}",
        "sequence": sequence,
        "timestamp": timestamp,
        "event_type": event_type,
        "summary": summary,
        "summary_digest": hashlib.sha256(summary.encode("utf-8")).hexdigest(),
    }


def _timestamps(created_at: str, count: int) -> list[str]:
    base = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone(timezone.utc)
    return [(base + timedelta(milliseconds=index * 100)).isoformat(timespec="milliseconds").replace("+00:00", "Z") for index in range(count)]


def _policy_decision(scenario: dict[str, Any]) -> str:
    requested = scenario["task"]["requested_scope"]
    policy = scenario["policy"]
    if requested in policy["forbidden_scopes"]:
        return "deny"
    return "allow" if requested == policy["allowed_scope"] else "deny"


def _run_fixed_internal_agent(scenario: dict[str, Any]) -> tuple[str, str, list[tuple[str, str]]]:
    """Execute the only allowlisted, deterministic, in-memory Agent adapter."""

    decision = _policy_decision(scenario)
    category = scenario["scenario_category"]
    tool_behavior = scenario["environment"]["tool_behavior"]
    events: list[tuple[str, str]] = [
        ("TASK_RECEIVED", f"Task {scenario['task']['task_id']} received for scope {scenario['task']['requested_scope']}."),
        ("POLICY_DECISION", f"Policy {scenario['policy']['decision_id']} returned {decision} for the requested scope."),
    ]

    if decision == "deny":
        disposition = "refused"
        events.append(("AGENT_OUTPUT", "The fixed internal Agent refused the request because the declared policy denied the scope."))
    elif category == "baseline" and tool_behavior == "success":
        tool = "synthetic_metadata_reader"
        _require(tool in scenario["sandbox"]["allowed_tools"], "REHEARSAL_TOOL_NOT_ALLOWLISTED", tool)
        events.append(("TOOL_CALL", f"The Agent invoked allowlisted in-memory tool {tool}."))
        events.append(("TOOL_RESULT", f"The tool returned synthetic label {scenario['environment']['fixture_label']}."))
        events.append(("AGENT_OUTPUT", "The Agent completed the bounded metadata inspection without an external effect."))
        disposition = "completed"
    elif category in {"tool_failure", "context_drift"} and tool_behavior in {
        "timeout", "invalid_response", "missing_dependency", "partial_result", "stale_context", "state_mismatch"
    }:
        tool_by_behavior = {
            "timeout": "synthetic_timeout_tool",
            "invalid_response": "synthetic_invalid_response_tool",
            "missing_dependency": "synthetic_missing_dependency_tool",
            "partial_result": "synthetic_partial_result_tool",
            "stale_context": "synthetic_context_reader",
            "state_mismatch": "synthetic_context_reader",
        }
        result_by_behavior = {
            "timeout": "timeout",
            "invalid_response": "invalid response",
            "missing_dependency": "missing dependency",
            "partial_result": "partial result",
            "stale_context": "stale context",
            "state_mismatch": "state mismatch",
        }
        tool = tool_by_behavior[tool_behavior]
        _require(tool in scenario["sandbox"]["allowed_tools"], "REHEARSAL_TOOL_NOT_ALLOWLISTED", tool)
        events.append(("TOOL_CALL", f"The Agent invoked allowlisted in-memory tool {tool}."))
        events.append(("TOOL_RESULT", f"The in-memory tool returned the declared {result_by_behavior[tool_behavior]} condition."))
        events.append(("FAILURE_SIGNAL", f"The Agent recorded {result_by_behavior[tool_behavior]} and did not infer a successful result."))
        events.append(("AGENT_OUTPUT", "The Agent abstained after the controlled incomplete-information condition."))
        disposition = "abstained"
    else:
        raise RehearsalRuntimeError("REHEARSAL_SCENARIO_BEHAVIOR_UNSUPPORTED", scenario["scenario_id"])

    expected = scenario["expected_outcome"]
    _require(disposition == expected["agent_disposition"], "REHEARSAL_DISPOSITION_MISMATCH", disposition)
    _require(decision == expected["policy_decision"], "REHEARSAL_POLICY_RESULT_MISMATCH", decision)
    _require(len(events) <= scenario["sandbox"]["max_steps"] + 2, "REHEARSAL_STEP_LIMIT_EXCEEDED", scenario["scenario_id"])
    return disposition, decision, events


def run_scenario_document(
    scenario: dict[str, Any],
    *,
    scenario_ref: str,
    scenario_digest: str,
) -> dict[str, Any]:
    """Run one already-bound strict scenario document.

    The caller must provide a stable repository reference and digest. This is
    used by the checked-in Benchmark corpus; it is not an arbitrary plugin or
    external scenario execution entrypoint.
    """

    _validate_scenario(scenario)
    disposition, decision, raw_events = _run_fixed_internal_agent(scenario)

    scenario_slug = scenario["scenario_id"].split(":", 1)[1]
    run_id = f"rehearsal-run:{scenario_slug}"
    trace_id = f"trace:{scenario_slug}"
    stamps = _timestamps(scenario["task"]["created_at"], len(raw_events))
    events = [_event(run_id, index, stamps[index], kind, summary) for index, (kind, summary) in enumerate(raw_events)]
    trace_digest = _canonical_digest(events)

    action_id = f"action:{scenario_slug}"
    claim_candidate = {
        "saee_evidence_adequacy_input_v0_1": True,
        "schema_version": "0.1.0",
        "claim_type": "AUTHORIZED_AGENT_ACTION",
        "evidence": {
            "action": {
                "action_id": action_id,
                "agent_id": scenario["agent_adapter"]["agent_id"],
                "requested_scope": scenario["task"]["requested_scope"],
                "timestamp": scenario["task"]["created_at"],
            },
            "policy_decision": {
                "decision_id": scenario["policy"]["decision_id"],
                "decision": decision,
                "agent_id": scenario["agent_adapter"]["agent_id"],
                "action_id": action_id,
                "authority_scope": scenario["policy"]["allowed_scope"],
                "valid_from": scenario["policy"]["valid_from"],
                "valid_until": scenario["policy"]["valid_until"],
            },
        },
        "truth_boundary": {
            "event_occurrence_proven": False,
            "identity_independently_verified": False,
            "authorization_externally_verified": False,
            "legal_finding_established": False,
            "production_ready": False,
        },
    }
    run = {
        "saee_agent_rehearsal_run_v0_1": True,
        "schema_version": "0.1.0",
        "run_id": run_id,
        "scenario_ref": scenario_ref,
        "scenario_digest": scenario_digest,
        "run_status": "COMPLETED",
        "agent_disposition": disposition,
        "policy_decision": decision,
        "trace": {"trace_id": trace_id, "events": events, "trace_digest": trace_digest},
        "evidence_export": {
            "evidence_export_id": f"evidence-export:{scenario_slug}",
            "trace_ref": trace_id,
            "trace_digest": trace_digest,
            "claim_type": "AUTHORIZED_AGENT_ACTION",
            "claim_candidate": claim_candidate,
            "evidence_established": False,
            "adequacy_evaluated": False,
        },
        "limitations": [
            "The executed Agent is a fixed internal synthetic policy Agent, not an external model or customer Agent.",
            "The tools are in-memory fixtures and do not establish real-world execution behavior.",
            "The evidence export is a candidate binding and is not an adequacy result, readiness decision, or deployment approval.",
        ],
        "truth_boundary": {
            "local_rehearsal_runtime_executed": True,
            "fixed_internal_agent_executed": True,
            "real_external_agent_executed": False,
            "external_tool_executed": False,
            "network_accessed": False,
            "subprocess_started": False,
            "customer_data_used": False,
            "evidence_established": False,
            "readiness_decision_made": False,
            "deployment_authorized": False,
            "production_ready": False,
        },
    }
    Draft202012Validator(_load_json(RUN_SCHEMA_PATH), format_checker=FormatChecker()).validate(run)
    return run


def run_task(path: Path) -> dict[str, Any]:
    """Run one allowlisted local rehearsal scenario and return a trace-bound export."""

    scenario_path = _resolve_scenario(path)
    scenario = _load_json(scenario_path)
    return run_scenario_document(
        scenario,
        scenario_ref=str(scenario_path.relative_to(ROOT)),
        scenario_digest=_path_digest(scenario_path),
    )
