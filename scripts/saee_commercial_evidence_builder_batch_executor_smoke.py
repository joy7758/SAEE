#!/usr/bin/env python3
"""Smoke test the bounded four-builder executor without real builder execution."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts/saee_commercial_evidence_builder_batch_executor.py"
OUT = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_builder_batch_request"
PREFLIGHT = OUT / "batch_execution_preflight.local.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_EXECUTOR_SMOKE: FAIL " + message)


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def load_module():
    spec = importlib.util.spec_from_file_location("saee_batch_executor", RUNNER)
    require(spec is not None and spec.loader is not None, "executor import spec unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    module = load_module()
    require(module.TARGET_IDS == [
        "production_monitoring",
        "production_restore_policy",
        "formal_security_review",
        "pricing_page",
    ], "target scope or order changed")

    outputs = [ROOT / target["output"] for target in module.TARGETS]
    before = {str(path): digest(path) for path in outputs}
    completed = subprocess.run(
        [sys.executable, str(RUNNER)],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    require("mode=dry_run" in completed.stdout, "default mode must be dry-run")
    data = json.loads(PREFLIGHT.read_text(encoding="utf-8"))
    require(data.get("apply_requested") is False, "default must not request apply")
    require(data.get("builders_executed") == 0, "default must execute zero builders")
    require(data.get("builders_succeeded") == 0, "default must succeed zero builders")
    require(data.get("blockers_closed") == 0, "executor must close zero blockers")
    require(data.get("production_ready") is False, "executor must not claim production ready")
    after = {str(path): digest(path) for path in outputs}
    require(after == before, "default dry-run changed a builder output")

    valid_approval = {
        "commercial_evidence_builder_batch_human_approval_v0_1": True,
        "status": "approved_four_local_builders_pending_separate_execution",
        "human_reviewer_name": "smoke-human",
        "approval_reference": "smoke-reference",
        "approval_date": "2026-07-10",
        "exact_approval_phrase": module.EXACT_PHRASE,
        "approve_four_local_builders_only": True,
        "approved_target_blocker_ids": module.TARGET_IDS,
        "confirm_no_blocker_closure": True,
        "confirm_no_external_contact": True,
        "confirm_no_publication": True,
        "confirm_no_production_readiness_claim": True,
        "confirm_separate_execution_step_required": True,
        "batch_builder_execution_approved": True,
        "builder_execution_authorized": True,
        "builders_executed": 0,
        **module.FALSE_FLAGS,
    }
    require(module.validate_approval(valid_approval) == [], "valid exact approval fixture rejected")
    bad_approval = dict(valid_approval)
    bad_approval["exact_approval_phrase"] = "批准执行"
    require(module.validate_approval(bad_approval), "generic approval phrase accepted")

    fake_calls: list[list[str]] = []

    def fake_runner(command, **kwargs):
        fake_calls.append(command)
        return subprocess.CompletedProcess(command, 99, "", "smoke no-op runner")

    simulated_apply = module.build_summary(True, runner=fake_runner)
    require(simulated_apply.get("blockers_closed") == 0, "simulated apply changed blocker truth")
    require(simulated_apply.get("production_ready") is False, "simulated apply changed production truth")
    require(len(fake_calls) <= 1, "failure must stop later fixed builders")
    if fake_calls:
        require(fake_calls[0][1] == module.TARGETS[0]["builder"], "unexpected first fixed builder")

    source = RUNNER.read_text(encoding="utf-8")
    for forbidden in ["shell=True", "os.system", "requests.", "urllib.", "httpx."]:
        require(forbidden not in source, f"executor contains forbidden path {forbidden}")
    for name in [
        "batch_execution_preflight.local.json",
        "batch_execution_preflight.md",
        "batch_execution_boundary_audit.md",
    ]:
        require((OUT / name).is_file(), f"missing {name}")
    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_builder_batch_executor_v0_1", {})
    require(entry.get("execution_mode") == "dry_run", "agent-index must record dry-run")
    require(entry.get("builders_executed") == 0, "agent-index must record zero execution")
    print(
        "SAEE_COMMERCIAL_EVIDENCE_BUILDER_BATCH_EXECUTOR_SMOKE: PASS "
        f"status={data.get('status')} builders_executed=0 blockers_closed=0 production_ready=false"
    )


if __name__ == "__main__":
    main()
