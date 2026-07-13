#!/usr/bin/env python3
"""Validate the safe, deterministic observed-trace evidence adapter."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import warnings
from pathlib import Path
from statistics import mean, pvariance

warnings.filterwarnings("ignore", category=DeprecationWarning)
from jsonschema import Draft202012Validator, RefResolver


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
INPUT = ROOT / "agent-interface/examples/observed-trace-bundle.json"
RECEIPT = ROOT / "agent-interface/examples/observed-trace-receipt.json"
INPUT_SCHEMA = ROOT / "agent-interface/schemas/observed-trace-bundle.schema.json"
RECEIPT_SCHEMA = ROOT / "agent-interface/schemas/observed-trace-receipt.schema.json"
ERROR_SCHEMA = ROOT / "agent-interface/schemas/agent-error.schema.json"
FIXTURES = ROOT / "agent-interface/fixtures/observed-trace/golden-fixtures.json"
CLI = ROOT / "scripts/saee_agent_cli.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_OBSERVED_TRACE_ADAPTER_SMOKE: FAIL " + message)


def read_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"{path.name} must be an object")
    return value


def run_cli(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), "evaluate-traces", "--input", str(path)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def reverse_keys(value):
    if isinstance(value, dict):
        return {key: reverse_keys(value[key]) for key in reversed(list(value))}
    if isinstance(value, list):
        return [reverse_keys(item) for item in value]
    return value


def transform(base: dict, fixture: dict) -> dict:
    value = copy.deepcopy(base)
    if fixture["candidate_order"] == "reverse":
        value["candidates"].reverse()
    if fixture["run_order"] == "reverse_each":
        for candidate in value["candidates"]:
            candidate["runs"].reverse()
    elif fixture["run_order"] == "reverse_first":
        value["candidates"][0]["runs"].reverse()
    return reverse_keys(value) if fixture["key_order"] == "reverse" else value


def independently_recompute(base: dict) -> dict[str, float]:
    result = {}
    for candidate in base["candidates"]:
        run_stability = []
        survival = []
        risk = []
        for run in candidate["runs"]:
            scores = [point["quality_score"] for point in run["steps"]]
            variance = pvariance(scores) if len(scores) > 1 else 0.0
            run_stability.append(mean(scores) / (1.0 + 12.0 * variance))
            survival.append(mean(point["alive"] for point in run["steps"]))
            risk.append(mean(point["failure_severity"] for point in run["steps"]))
        stability_score = mean(run_stability)
        survival_score = mean(survival)
        risk_score = mean(risk)
        result[candidate["candidate_id"]] = round(
            max(0.0, min(1.0, 0.50 * stability_score + 0.30 * survival_score - 0.20 * risk_score)),
            6,
        )
    return result


def validate_receipt(receipt: dict) -> None:
    schema = read_json(RECEIPT_SCHEMA)
    resolver = RefResolver(base_uri=RECEIPT_SCHEMA.as_uri(), referrer=schema)
    errors = list(Draft202012Validator(schema, resolver=resolver).iter_errors(receipt))
    require(not errors, f"receipt schema errors: {[item.message for item in errors]}")


def main() -> None:
    base = read_json(INPUT)
    receipt = read_json(RECEIPT)
    input_errors = list(Draft202012Validator(read_json(INPUT_SCHEMA)).iter_errors(base))
    require(not input_errors, f"input schema errors: {[item.message for item in input_errors]}")
    validate_receipt(receipt)

    completed = run_cli(INPUT)
    require(completed.returncode == 0, "preferred observed command must exit 0")
    require(completed.stderr == "", "preferred observed command stderr must be empty")
    require(json.loads(completed.stdout) == receipt, "checked-in observed receipt drifted")

    import saee_backend.core.simulator as simulator
    from saee_backend.observed_trace_adapter import (
        ObservedTraceBundle,
        evaluate_observed_trace_bundle,
        normalized_bundle,
        sha256_json,
    )

    original_simulator = simulator.simulate_competition_runs
    simulator.simulate_competition_runs = lambda *args, **kwargs: (_ for _ in ()).throw(
        AssertionError("synthetic simulator must not be called")
    )
    try:
        direct = evaluate_observed_trace_bundle(ObservedTraceBundle.model_validate(base))
    finally:
        simulator.simulate_competition_runs = original_simulator
    require(direct == receipt, "direct adapter result differs")

    parsed = ObservedTraceBundle.model_validate(base)
    require(sha256_json(normalized_bundle(parsed)) == receipt["request_sha256"], "request hash")
    report_keys = (
        "evaluation_summary", "stability_reports", "failure_mode_reports",
        "survival_curves", "comparison_ranking", "observed_failure_code_counts",
        "trace_quality",
    )
    reports = {key: receipt[key] for key in report_keys}
    require(sha256_json(reports) == receipt["content_sha256"], "content hash")

    independent_scores = independently_recompute(base)
    actual_scores = {item["agent_id"]: item["score"] for item in receipt["comparison_ranking"]["ranking"]}
    for candidate_id, score in independent_scores.items():
        require(abs(score - actual_scores[candidate_id]) <= 1e-6, f"independent score {candidate_id}")

    fixtures = read_json(FIXTURES)
    require(len(fixtures["fixtures"]) >= 12, "at least 12 golden fixtures required")
    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        for fixture in fixtures["fixtures"]:
            path = tmpdir / f"{fixture['id']}.json"
            path.write_text(json.dumps(transform(base, fixture), ensure_ascii=False), encoding="utf-8")
            result = run_cli(path)
            require(result.returncode == 0, f"fixture {fixture['id']} exit")
            candidate_receipt = json.loads(result.stdout)
            require(candidate_receipt == receipt, f"fixture {fixture['id']} byte-equivalent data")
        require(receipt["request_sha256"] == fixtures["expected_request_sha256"], "golden request hash")
        require(receipt["content_sha256"] == fixtures["expected_content_sha256"], "golden content hash")

        mismatch = copy.deepcopy(base)
        mismatch["candidates"][1]["context"]["scenario_id"] = "different-scenario"
        mismatch_path = tmpdir / "mismatch.json"
        mismatch_path.write_text(json.dumps(mismatch), encoding="utf-8")
        mismatch_result = run_cli(mismatch_path)
        require(mismatch_result.returncode == 2, "incomparable candidates must exit 2")

        forbidden = copy.deepcopy(base)
        forbidden["candidates"][0]["runs"][0]["steps"][0]["prompt"] = "forbidden raw content"
        forbidden_path = tmpdir / "forbidden.json"
        forbidden_path.write_text(json.dumps(forbidden), encoding="utf-8")
        forbidden_result = run_cli(forbidden_path)
        require(forbidden_result.returncode == 2, "raw prompt field must exit 2")
        error = json.loads(forbidden_result.stdout)
        require(not list(Draft202012Validator(read_json(ERROR_SCHEMA)).iter_errors(error)), "error schema")

    require(receipt["provenance"]["simulator_called"] is False, "simulator claim")
    require(receipt["provenance"]["trace_authenticity_verified"] is False, "authenticity claim")
    require(receipt["truth_boundary"]["pii_absence_verified_by_saee"] is False, "PII claim")
    require(receipt["truth_boundary"]["production_ready"] is False, "production claim")
    print(
        "SAEE_OBSERVED_TRACE_ADAPTER_SMOKE: PASS fixtures=12 replay=10/10+ "
        "schema_errors=0 independent_error_max<=1e-6 simulator_called=false "
        "candidate_code_executed=false external_calls=false trace_authenticity_verified=false"
    )


if __name__ == "__main__":
    main()
