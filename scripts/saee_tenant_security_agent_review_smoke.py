#!/usr/bin/env python3
"""Adversarial smoke for tenant security independent-agent review evidence."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.tenant_security_agent_review import (
    evaluate_tenant_security_agent_review,
)
from scripts.saee_tenant_security_agent_review_profile import OUTPUT, main as run_profile


VALIDATION = ROOT / "agent_recommendation/tenant_security_agent_review/run_001/independent_agent_validation.local.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_SECURITY_AGENT_REVIEW_SMOKE: FAIL: " + message)


def mutate_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    run_profile()
    canonical = evaluate_tenant_security_agent_review(ROOT)
    require(canonical["status"] == "pass_agent_security_review", "canonical status")
    require(canonical["security_review_completed"] is True, "security review")
    require(canonical["human_validation_used"] is False, "human boundary")
    require(canonical["formal_production_security_review_completed"] is False, "formal boundary")
    require(canonical["privacy_legal_review_completed"] is False, "privacy boundary")
    require(canonical["production_ready"] is False and canonical["blockers_closed"] == 0, "production boundary")

    variants = (
        ("validation", lambda d: d.update(verdict="conditional")),
        ("validation", lambda d: d["round_2"].update(blocker_count=1)),
        ("validation", lambda d: d.update(blockers=["synthetic"])),
        ("profile", lambda d: d.update(security_smokes_passed=6)),
        ("profile", lambda d: d["source_sha256"].update({next(iter(d["source_sha256"])): "0" * 64})),
        ("profile", lambda d: d["source_sha256"].pop(next(iter(d["source_sha256"])))),
        ("profile", lambda d: d.update(production_ready=True)),
        ("missing", lambda d: None),
    )
    for index, (target, mutate) in enumerate(variants, start=1):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            profile = tmp / "profile.json"
            validation = tmp / "validation.json"
            shutil.copy2(OUTPUT, profile)
            shutil.copy2(VALIDATION, validation)
            if target == "profile":
                mutate_json(profile, mutate)
            elif target == "validation":
                mutate_json(validation, mutate)
            else:
                validation.unlink()
            result = evaluate_tenant_security_agent_review(
                ROOT,
                profile_path=profile,
                validation_path=validation,
            )
            require(result["status"] == "hold_agent_security_review", f"case {index} status")
            require(result["security_review_completed"] is False, f"case {index} review")
            require(result["production_ready"] is False, f"case {index} production")

    print(
        "SAEE_TENANT_SECURITY_AGENT_REVIEW_SMOKE: PASS smokes=7/7 negatives=8/8 "
        "security_review_completed=true human_validation_used=false "
        "formal_production_security_review_completed=false privacy_legal_review_completed=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
