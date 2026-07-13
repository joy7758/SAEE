#!/usr/bin/env python3
"""Offline deterministic smoke for the 20-case Agent Readiness Benchmark."""

from __future__ import annotations

import ast
import copy
import json
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker, ValidationError


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_rehearsal_runtime import run_scenario_document
from saee_backend.services.agent_run_capability import evaluate_agent_run
from saee_backend.services.readiness_benchmark import (
    BENCHMARK_PATH,
    ReadinessBenchmarkError,
    _build_scenario,
    _digest,
    _validate_benchmark,
    run_benchmark,
)


BENCHMARK_SCHEMA = ROOT / "agent-interface/benchmarks/saee-agent-readiness-benchmark.schema.v0.1.json"
RESULT_SCHEMA = ROOT / "agent-interface/benchmarks/saee-agent-readiness-benchmark-result.v0.1.schema.json"
SERVICE = ROOT / "saee_backend/services/readiness_benchmark.py"
CLI = ROOT / "scripts/saee_agent_readiness_benchmark.py"
DOC = ROOT / "docs/architecture/SAEE_AGENT_READINESS_BENCHMARK_V0_1.md"
GATE = ROOT / "docs/strategy/SAEE_AGENT_READINESS_BENCHMARK_RECOMMENDATION_GATE.md"


class BenchmarkSmokeError(ValueError):
    pass


def require(condition: bool, detail: str) -> None:
    if not condition:
        raise BenchmarkSmokeError(detail)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    roots = {node.names[0].name.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.Import)}
    roots.update(node.module.split(".")[0] for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module)
    return roots


def expect_invalid(document: dict[str, Any], label: str) -> None:
    try:
        _validate_benchmark(document)
    except (ReadinessBenchmarkError, ValidationError, ValueError):
        return
    raise BenchmarkSmokeError(f"invalid benchmark accepted: {label}")


def main() -> None:
    for path in (BENCHMARK_PATH, BENCHMARK_SCHEMA, RESULT_SCHEMA, SERVICE, CLI, DOC, GATE):
        require(path.is_file(), f"required file missing: {path}")
    forbidden = {"socket", "subprocess", "urllib", "requests", "httpx", "importlib", "smtplib"}
    require(not imported_roots(SERVICE).intersection(forbidden), "network or external execution module imported")

    benchmark = load(BENCHMARK_PATH)
    Draft202012Validator(load(BENCHMARK_SCHEMA), format_checker=FormatChecker()).validate(benchmark)
    result = run_benchmark()
    Draft202012Validator(load(RESULT_SCHEMA), format_checker=FormatChecker()).validate(result)
    metrics = result["metrics"]
    require(metrics["total_cases"] == 20, "case count invalid")
    require(metrics["category_coverage"] == {"adversarial_input": 4, "baseline": 4, "context_drift": 4, "instruction_conflict": 4, "tool_failure": 4}, "category coverage invalid")
    require((metrics["completed"], metrics["abstained"], metrics["refused"]) == (4, 8, 8), "disposition counts invalid")
    require((metrics["supported"], metrics["insufficient_evidence"]) == (12, 8), "assessment counts invalid")
    require(metrics["denied_actions_supported"] == 0, "denied action incorrectly supported")
    require(metrics["expectation_matches"] == 20, "expectation mismatch")
    require(metrics["profile_support_rate"] == 0.6, "profile support rate invalid")
    require(metrics["profile_support_rate_is_agent_accuracy"] is False, "profile support promoted to accuracy")
    require(metrics["risk_probability_measured"] is False, "synthetic rate promoted to risk probability")
    require(all(item["task_success_established"] is False for item in result["case_results"]), "task success overclaim")

    invalid: list[tuple[dict[str, Any], str]] = []
    item = copy.deepcopy(benchmark); item["cases"].pop(); invalid.append((item, "missing case"))
    item = copy.deepcopy(benchmark); item["cases"][1]["case_id"] = item["cases"][0]["case_id"]; invalid.append((item, "duplicate id"))
    item = copy.deepcopy(benchmark); item["cases"][4]["category"] = "baseline"; invalid.append((item, "unbalanced categories"))
    item = copy.deepcopy(benchmark); item["truth_boundary"]["production_ready"] = True; invalid.append((item, "production overclaim"))
    item = copy.deepcopy(benchmark); item["truth_boundary"]["benchmark_accuracy_claim"] = True; invalid.append((item, "accuracy overclaim"))
    for item, label in invalid:
        expect_invalid(item, label)

    wrong = copy.deepcopy(benchmark["cases"][0])
    wrong["expected_assessment"] = "INSUFFICIENT_EVIDENCE"
    scenario = _build_scenario(wrong, 0)
    run = run_scenario_document(
        scenario,
        scenario_ref=f"agent-interface/benchmarks/saee-agent-readiness-benchmark.v0.1.json#{wrong['case_id']}",
        scenario_digest=_digest(scenario),
    )
    evaluation = evaluate_agent_run(run)
    require(evaluation["assessment"] != wrong["expected_assessment"], "semantic expectation mismatch not detected")

    overclaim = copy.deepcopy(result)
    overclaim["truth_boundary"]["production_ready"] = True
    try:
        Draft202012Validator(load(RESULT_SCHEMA)).validate(overclaim)
    except ValidationError:
        pass
    else:
        raise BenchmarkSmokeError("result production overclaim accepted")

    canonical = json.dumps(result, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = run_benchmark()
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == canonical, "Benchmark non-deterministic")

    doc = DOC.read_text(encoding="utf-8")
    for marker in ("20 个", "Context Drift", "profile_support_rate", "不是 Agent Accuracy", "固定内部合成 Agent"):
        require(marker in doc, f"documentation marker missing: {marker}")

    print("SAEE_AGENT_READINESS_BENCHMARK_SMOKE: PASS")
    print("benchmark_cases=20/20")
    print("categories=5/5")
    print("cases_per_category=4/4")
    print("expectation_matches=20/20")
    print("invalid_cases=7/7")
    print("deterministic_runs=5/5")
    print("supported=12")
    print("insufficient_evidence=8")
    print("denied_actions_supported=0")
    print("profile_support_rate=0.6")
    print("profile_support_rate_is_agent_accuracy=false")
    print("risk_probability_measured=false")
    print("real_external_agent_validated=false")
    print("production_ready=false")


if __name__ == "__main__":
    try:
        main()
    except (BenchmarkSmokeError, ReadinessBenchmarkError, json.JSONDecodeError, ValidationError, ValueError, KeyError) as exc:
        print(f"SAEE_AGENT_READINESS_BENCHMARK_SMOKE: FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
