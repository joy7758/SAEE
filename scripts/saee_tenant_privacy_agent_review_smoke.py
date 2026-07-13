#!/usr/bin/env python3
"""Adversarial smoke for narrow tenant privacy independent-agent evidence."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.tenant_privacy_agent_review import evaluate_tenant_privacy_agent_review
from scripts.saee_tenant_privacy_data_flow_profile import main as run_data_flow
from scripts.saee_tenant_privacy_agent_review_profile import OUTPUT, main as run_profile


VALIDATION = ROOT / "agent_recommendation/tenant_privacy_agent_review/run_001/independent_agent_validation.local.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_PRIVACY_AGENT_REVIEW_SMOKE: FAIL: " + message)


def mutate_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main() -> None:
    run_data_flow()
    run_profile()
    canonical = evaluate_tenant_privacy_agent_review(ROOT)
    require(canonical["status"] == "pass_agent_privacy_boundary_review", "canonical status")
    require(canonical["agent_privacy_boundary_review_completed"] is True, "review completion")
    require(canonical["human_validation_used"] is False, "human boundary")
    for key in (
        "general_dlp_available",
        "deidentification_proven",
        "real_customer_data_allowed",
        "privacy_legal_review_completed",
        "data_processing_agreement_completed",
        "qianfan_provider_legal_approval_completed",
        "qianfan_retention_terms_verified",
        "customer_data_processing_ready",
        "production_ready",
        "customer_validated",
        "product_launched",
    ):
        require(canonical[key] is False, f"canonical {key}")

    variants = (
        ("validation", lambda d: d.update(verdict="conditional")),
        ("validation", lambda d: d["round_2"].update(verdict="recommend")),
        ("validation", lambda d: d["round_2"].update(blocker_count=0)),
        ("validation", lambda d: d["round_3"].update(verdict="conditional")),
        ("validation", lambda d: d["round_3"].update(blocker_count=1)),
        ("validation", lambda d: d["round_4"].update(verdict="conditional")),
        ("validation", lambda d: d["round_4"].update(blocker_count=1)),
        ("validation", lambda d: d.update(blockers=["synthetic"])),
        ("profile", lambda d: d.update(privacy_smokes_passed=9)),
        ("profile", lambda d: d.update(personal_data_boundary_cases_passed=28)),
        ("profile", lambda d: d["source_sha256"].update({next(iter(d["source_sha256"])): "0" * 64})),
        ("profile", lambda d: d.update(production_ready=True)),
        ("validation", lambda d: d.update(deidentification_proven=True)),
        ("validation", lambda d: d.pop("real_customer_data_allowed")),
        ("missing", lambda d: None),
        ("corrupt", lambda d: None),
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
            elif target == "missing":
                validation.unlink()
            else:
                profile.write_text("{not-json", encoding="utf-8")
            result = evaluate_tenant_privacy_agent_review(
                ROOT, profile_path=profile, validation_path=validation
            )
            require(result["status"] == "hold_agent_privacy_boundary_review", f"case {index} status")
            require(result["agent_privacy_boundary_review_completed"] is False, f"case {index} review")
            require(result["production_ready"] is False, f"case {index} production")

    print(
        "SAEE_TENANT_PRIVACY_AGENT_REVIEW_SMOKE: PASS smokes=10/10 "
        "personal_data_cases=29/29 negatives=16/16 "
        "agent_privacy_boundary_review_completed=true human_validation_used=false "
        "general_dlp=false deidentification_proven=false real_customer_data_allowed=false "
        "privacy_legal_review_completed=false production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
