"""Local Agent Capability Alpha for evaluating a SAEE rehearsal run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.evidence_adequacy import evaluate_evidence_adequacy


ROOT = Path(__file__).resolve().parents[2]
RUN_SCHEMA = ROOT / "agent-interface/rehearsal/saee-agent-rehearsal-run.v0.1.schema.json"
OUTPUT_SCHEMA = ROOT / "agent-interface/capabilities/saee-evaluate-agent-run-output.v0.1.schema.json"


class AgentRunCapabilityError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise AgentRunCapabilityError(code, detail)


def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def evaluate_agent_run(run: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one validated rehearsal run's claim candidate."""

    validator = Draft202012Validator(_load_schema(RUN_SCHEMA), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(run), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        path = "/" + "/".join(str(part) for part in first.absolute_path)
        raise AgentRunCapabilityError("AGENT_RUN_SCHEMA_INVALID", f"{path}: {first.message}")

    trace = run["trace"]
    export = run["evidence_export"]
    actual_trace_digest = _digest(trace["events"])
    _require(trace["trace_digest"] == actual_trace_digest, "AGENT_RUN_TRACE_DIGEST_INVALID", run["run_id"])
    _require(export["trace_ref"] == trace["trace_id"], "AGENT_RUN_TRACE_REFERENCE_UNBOUND", run["run_id"])
    _require(export["trace_digest"] == actual_trace_digest, "AGENT_RUN_EVIDENCE_EXPORT_UNBOUND", run["run_id"])
    _require(export["claim_type"] == "AUTHORIZED_AGENT_ACTION", "AGENT_RUN_CLAIM_UNSUPPORTED", export["claim_type"])
    _require(export["evidence_established"] is False, "AGENT_RUN_PRETENDS_EVIDENCE_ESTABLISHED", run["run_id"])
    _require(export["adequacy_evaluated"] is False, "AGENT_RUN_PRETENDS_PREVIOUS_EVALUATION", run["run_id"])

    adequacy = evaluate_evidence_adequacy(export["claim_type"], export["claim_candidate"])
    passed = adequacy["result"] == "PASS"
    output = {
        "saee_evaluate_rehearsal_run_output_v0_1": True,
        "schema_version": "0.1.0",
        "capability_id": "internal.saee.evaluate_rehearsal_run",
        "run_ref": run["run_id"],
        "trace_ref": trace["trace_id"],
        "claim_type": export["claim_type"],
        "assessment": "SUPPORTED" if passed else "INSUFFICIENT_EVIDENCE",
        "profile_result": adequacy["result"],
        "missing_requirements": adequacy["missing_requirements"],
        "failed_relationships": adequacy["failed_relationships"],
        "reason_codes": adequacy["reason_codes"],
        "limitations": [
            "SUPPORTED means only that the fixed Evidence Adequacy profile requirements were satisfied.",
            "The result does not establish that the Agent completed its task successfully.",
            "The result does not establish Agent safety, legal compliance, certification, or production readiness.",
            "The result does not authorize deployment or another external action.",
            "The current upstream Runtime uses a fixed internal synthetic Agent, not a validated external Agent.",
        ],
        "boundary_statement": "Evidence adequacy assessment is not task success, safety certification, compliance determination, or deployment authority.",
        "truth_boundary": {
            "profile_requirements_evaluated": True,
            "accountability_claim_established": False,
            "task_success_established": False,
            "agent_safety_established": False,
            "compliance_established": False,
            "deployment_authorized": False,
            "real_external_agent_validated": False,
            "customer_validated": False,
            "production_ready": False,
        },
    }
    Draft202012Validator(_load_schema(OUTPUT_SCHEMA), format_checker=FormatChecker()).validate(output)
    return output
