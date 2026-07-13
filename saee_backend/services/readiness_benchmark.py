"""Execute the local 20-case SAEE Agent Readiness Benchmark v0.1."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from saee_backend.services.agent_rehearsal_runtime import run_scenario_document
from saee_backend.services.agent_run_capability import evaluate_agent_run


ROOT = Path(__file__).resolve().parents[2]
BENCHMARK_PATH = ROOT / "agent-interface/benchmarks/saee-agent-readiness-benchmark.v0.1.json"
BENCHMARK_SCHEMA = ROOT / "agent-interface/benchmarks/saee-agent-readiness-benchmark.schema.v0.1.json"
RESULT_SCHEMA = ROOT / "agent-interface/benchmarks/saee-agent-readiness-benchmark-result.v0.1.schema.json"
CATEGORIES = {"baseline", "context_drift", "tool_failure", "instruction_conflict", "adversarial_input"}


class ReadinessBenchmarkError(ValueError):
    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code


def _require(condition: bool, code: str, detail: str) -> None:
    if not condition:
        raise ReadinessBenchmarkError(code, detail)


def _load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(value, dict), "BENCHMARK_JSON_ROOT_INVALID", str(path))
    return value


def _digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _path_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _validate_benchmark(benchmark: dict[str, Any]) -> None:
    validator = Draft202012Validator(_load(BENCHMARK_SCHEMA), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(benchmark), key=lambda item: list(item.absolute_path))
    if errors:
        first = errors[0]
        pointer = "/" + "/".join(str(part) for part in first.absolute_path)
        raise ReadinessBenchmarkError("BENCHMARK_SCHEMA_INVALID", f"{pointer}: {first.message}")
    cases = benchmark["cases"]
    ids = [case["case_id"] for case in cases]
    _require(len(ids) == len(set(ids)), "BENCHMARK_CASE_ID_DUPLICATE", "case_id")
    coverage = Counter(case["category"] for case in cases)
    _require(set(coverage) == CATEGORIES, "BENCHMARK_CATEGORY_MISSING", str(sorted(CATEGORIES - set(coverage))))
    _require(all(coverage[category] == 4 for category in CATEGORIES), "BENCHMARK_CATEGORY_UNBALANCED", str(dict(coverage)))


def _build_scenario(case: dict[str, Any], index: int) -> dict[str, Any]:
    requested_scope = case["requested_scope"]
    denied = case["expected_policy_decision"] == "deny"
    forbidden_scopes = sorted({"deployment:approve", requested_scope} if denied else {"deployment:approve", "resource:write"})
    created_at = f"2026-07-12T02:{index:02d}:00Z"
    return {
        "saee_agent_rehearsal_scenario_v0_1": True,
        "schema_version": "0.1.0",
        "scenario_id": f"rehearsal:{case['case_id']}",
        "scenario_category": case["category"],
        "task": {
            "task_id": f"task:{case['case_id']}",
            "objective": case["objective"],
            "requested_scope": requested_scope,
            "created_at": created_at,
        },
        "agent_adapter": {
            "adapter_id": "adapter:saee-fixed-policy-agent-v0.1",
            "adapter_version": "0.1.0",
            "adapter_type": "fixed_internal_policy_agent",
            "agent_id": "agent:saee-benchmark-policy-v0.1",
            "synthetic": True,
        },
        "sandbox": {
            "sandbox_id": f"sandbox:{case['case_id']}",
            "synthetic": True,
            "network_allowed": False,
            "subprocess_allowed": False,
            "filesystem_write_allowed": False,
            "allowed_tools": [case["allowed_tool"]],
            "max_steps": 6,
        },
        "policy": {
            "decision_id": f"policy:{case['case_id']}",
            "allowed_scope": "resource:inspect-metadata",
            "forbidden_scopes": forbidden_scopes,
            "valid_from": f"2026-07-12T01:{index:02d}:00Z",
            "valid_until": f"2026-07-12T03:{index:02d}:00Z",
            "human_stop_authority_ref": "human:saee-benchmark-operator",
        },
        "environment": {
            "environment_id": f"environment:{case['case_id']}",
            "tool_behavior": case["tool_behavior"],
            "fixture_label": case["case_id"],
            "fixture_digest": hashlib.sha256(case["case_id"].encode("utf-8")).hexdigest(),
        },
        "expected_outcome": {
            "run_status": "COMPLETED",
            "agent_disposition": case["expected_disposition"],
            "policy_decision": case["expected_policy_decision"],
            "external_effect_expected": False,
        },
        "truth_boundary": {
            "synthetic_scenario": True,
            "external_agent": False,
            "customer_data": False,
            "network": False,
            "external_execution": False,
            "deployment_authorized": False,
            "production_ready": False,
        },
    }


def run_benchmark(path: Path = BENCHMARK_PATH) -> dict[str, Any]:
    resolved = path.resolve()
    _require(resolved == BENCHMARK_PATH.resolve(), "BENCHMARK_PATH_NOT_CANONICAL", str(path))
    benchmark = _load(resolved)
    _validate_benchmark(benchmark)

    case_results: list[dict[str, Any]] = []
    for index, case in enumerate(benchmark["cases"]):
        scenario = _build_scenario(case, index)
        scenario_ref = f"agent-interface/benchmarks/saee-agent-readiness-benchmark.v0.1.json#{case['case_id']}"
        run = run_scenario_document(scenario, scenario_ref=scenario_ref, scenario_digest=_digest(scenario))
        evaluation = evaluate_agent_run(run)
        matches = (
            run["agent_disposition"] == case["expected_disposition"]
            and run["policy_decision"] == case["expected_policy_decision"]
            and evaluation["assessment"] == case["expected_assessment"]
        )
        _require(matches, "BENCHMARK_EXPECTATION_MISMATCH", case["case_id"])
        case_results.append({
            "case_id": case["case_id"],
            "category": case["category"],
            "run_ref": run["run_id"],
            "trace_ref": run["trace"]["trace_id"],
            "trace_digest": run["trace"]["trace_digest"],
            "agent_disposition": run["agent_disposition"],
            "policy_decision": run["policy_decision"],
            "assessment": evaluation["assessment"],
            "task_success_established": evaluation["truth_boundary"]["task_success_established"],
            "expectation_match": matches,
        })

    category_coverage = Counter(item["category"] for item in case_results)
    disposition = Counter(item["agent_disposition"] for item in case_results)
    assessments = Counter(item["assessment"] for item in case_results)
    denied_actions_supported = sum(1 for item in case_results if item["policy_decision"] == "deny" and item["assessment"] == "SUPPORTED")
    result = {
        "saee_agent_readiness_benchmark_result_v0_1": True,
        "benchmark_id": benchmark["benchmark_id"],
        "benchmark_digest": _path_digest(resolved),
        "status": "PASS",
        "case_results": case_results,
        "metrics": {
            "total_cases": len(case_results),
            "category_coverage": dict(sorted(category_coverage.items())),
            "completed": disposition["completed"],
            "abstained": disposition["abstained"],
            "refused": disposition["refused"],
            "supported": assessments["SUPPORTED"],
            "insufficient_evidence": assessments["INSUFFICIENT_EVIDENCE"],
            "denied_actions_supported": denied_actions_supported,
            "expectation_matches": sum(1 for item in case_results if item["expectation_match"]),
            "profile_support_rate": assessments["SUPPORTED"] / len(case_results),
            "profile_support_rate_is_agent_accuracy": False,
            "risk_probability_measured": False,
        },
        "limitations": [
            "All 20 cases execute the same fixed internal synthetic policy Agent.",
            "Category coverage does not establish external Agent generalization.",
            "Profile support rate is not Agent accuracy, task success rate, or a risk probability.",
            "The Benchmark does not authorize deployment or establish production readiness.",
        ],
        "truth_boundary": {
            "fixed_internal_agent_only": True,
            "real_external_agent_validated": False,
            "customer_data_used": False,
            "external_validation_completed": False,
            "deployment_authorized": False,
            "production_ready": False,
        },
    }
    Draft202012Validator(_load(RESULT_SCHEMA), format_checker=FormatChecker()).validate(result)
    return result

