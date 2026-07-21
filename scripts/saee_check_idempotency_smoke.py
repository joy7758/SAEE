#!/usr/bin/env python3
"""Validate the clean-check contract without relying on ignored artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.saee_check_isolation import generated_differences, normalize_generated, run_isolated


CONTRACT = ROOT / "agent-interface/validation/saee-check-idempotency-contract.v1.json"
PROVIDER_SMOKE = ROOT / "scripts/saee_controlled_reasoning_live_evidence_smoke.py"
STATUS = ROOT / "agent-interface/rehearsal/saee-controlled-reasoning-live-validation.v0.2.json"
PRICING_OUTPUT = Path(
    "phase_b_product/commercial_readiness/billing_revenue_evidence/"
    "pricing_page_closure_review_packet.local.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CHECK_IDEMPOTENCY_SMOKE: FAIL " + message)


def run_provider(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(PROVIDER_SMOKE), *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def main() -> None:
    contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
    require(contract["saee_check_idempotency_contract_v1"] is True, "contract marker")
    require(contract["normal_check"]["tracked_paths_writable"] is False, "normal check writable")
    require(contract["normal_check"]["ignored_runtime_inputs_copied"] is False, "ignored input copied")
    require(contract["generation"]["explicit_only"] is True, "generation not explicit")

    old = b'{"generated_at":"old","value":1,"local_trial_started_by_manager":true}\n'
    new = b'{"local_trial_started_by_manager":false,"value":1,"generated_at":"new"}\n'
    changed = b'{"generated_at":"new","value":2,"local_trial_started_by_manager":false}\n'
    require(
        normalize_generated(Path("sample.json"), old)
        == normalize_generated(Path("sample.json"), new),
        "volatile JSON normalization",
    )
    require(
        normalize_generated(Path("sample.json"), old)
        != normalize_generated(Path("sample.json"), changed),
        "substantive JSON drift hidden",
    )
    raw, substantive = generated_differences(
        {Path("sample.json"): old}, {Path("sample.json"): new}
    )
    require(raw == [Path("sample.json")] and substantive == [], "volatile diff classification")
    _, substantive = generated_differences(
        {Path("sample.json"): old}, {Path("sample.json"): changed}
    )
    require(substantive == [Path("sample.json")], "substantive diff not detected")

    with tempfile.TemporaryDirectory(prefix="saee-evidence-missing-") as directory:
        optional = run_provider("--evidence-root", directory)
        require(optional.returncode == 0, "missing optional evidence failed")
        require(
            "external_provider_evidence_status=NOT_REQUIRED" in optional.stdout,
            "NOT_REQUIRED missing",
        )
        strict = run_provider("--require-evidence", "--evidence-root", directory)
        require(strict.returncode != 0, "missing strict evidence accepted")
        require(
            "external_provider_evidence_status=NOT_AVAILABLE" in strict.stdout,
            "NOT_AVAILABLE missing",
        )
        require("EXTERNAL_EVIDENCE_NOT_AVAILABLE" in strict.stderr, "strict missing diagnostic")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    with tempfile.TemporaryDirectory(prefix="saee-evidence-invalid-") as directory:
        root = Path(directory)
        for record in status["live_runs"]:
            path = root / record["run_ref"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")
        invalid = run_provider("--require-evidence", "--evidence-root", directory)
        require(invalid.returncode != 0, "invalid evidence accepted")
        require(
            "external_provider_evidence_status=INVALID" in invalid.stdout,
            "INVALID missing",
        )

    pricing_before = (ROOT / PRICING_OUTPUT).read_bytes()
    isolated = run_isolated(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; Path("
            + repr(PRICING_OUTPUT.as_posix())
            + ").write_text('isolated\\n')",
        ],
        source=ROOT,
    )
    require(isolated == 0, "isolated write command failed")
    require((ROOT / PRICING_OUTPUT).read_bytes() == pricing_before, "isolated write reached caller")

    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    for target in (
        "check:",
        "check-in-place:",
        "generate:",
        "check-generated:",
        "check-provider-evidence:",
    ):
        require(target in makefile, "missing Make target " + target)
    combined = makefile + (ROOT / "scripts/saee_check_isolation.py").read_text(encoding="utf-8")
    for forbidden in ("git restore", "git checkout --", "git reset --hard"):
        require(forbidden not in combined, "hidden cleanup command " + forbidden)

    print(
        "SAEE_CHECK_IDEMPOTENCY_SMOKE: PASS "
        "normal_missing=NOT_REQUIRED strict_missing=NOT_AVAILABLE invalid=INVALID "
        "substantive_drift_detected=true isolated_write_preserved_caller=true"
    )


if __name__ == "__main__":
    main()
