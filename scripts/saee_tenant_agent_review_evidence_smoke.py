#!/usr/bin/env python3
"""Adversarial smoke for the atomic tenant agent-review evidence adapter."""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.tenant_agent_review_evidence import (
    AUTH_SOURCE_SET,
    SECRET_SOURCE_SET,
    TenantAgentReviewPaths,
    canonical_paths,
    evaluate_tenant_agent_review_evidence,
)


NEGATIVE_CASE_IDS = (
    "top_level_verdict_conditional",
    "final_round_blocker_nonzero",
    "blockers_array_nonempty",
    "test_count_reduced",
    "source_content_hash_mismatch",
    "source_manifest_missing_key",
    "scope_mismatch",
    "production_flag_true",
    "input_missing",
    "input_corrupt_json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_AGENT_REVIEW_EVIDENCE_SMOKE: FAIL: " + message)


def copy_fixture(tmp: Path) -> TenantAgentReviewPaths:
    for relative in AUTH_SOURCE_SET | SECRET_SOURCE_SET:
        target = tmp / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    canonical = canonical_paths(ROOT)
    paths = TenantAgentReviewPaths(
        auth_profile=tmp / "inputs/auth_profile.json",
        auth_validation=tmp / "inputs/auth_validation.json",
        secret_profile=tmp / "inputs/secret_profile.json",
        secret_validation=tmp / "inputs/secret_validation.json",
    )
    paths.auth_profile.parent.mkdir(parents=True, exist_ok=True)
    for source, target in (
        (canonical.auth_profile, paths.auth_profile),
        (canonical.auth_validation, paths.auth_validation),
        (canonical.secret_profile, paths.secret_profile),
        (canonical.secret_validation, paths.secret_validation),
    ):
        shutil.copy2(source, target)
    return paths


def mutate_json(path: Path, mutate) -> None:
    data = json.loads(path.read_text(encoding="utf-8"))
    mutate(data)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def require_atomic_hold(root: Path, paths: TenantAgentReviewPaths, label: str) -> None:
    data = evaluate_tenant_agent_review_evidence(root, paths)
    require(data["status"] == "hold_agent_review_evidence", label + " status")
    require(data["tenant_authorization_policy_reviewed"] is False, label + " auth")
    require(data["tenant_secret_boundary_reviewed"] is False, label + " secret")
    require(data["security_review_completed"] is False, label + " security")
    require(data["privacy_legal_review_completed"] is False, label + " privacy")
    require(data["production_ready"] is False and data["blockers_closed"] == 0, label + " boundary")


def main() -> None:
    canonical = evaluate_tenant_agent_review_evidence(ROOT)
    require(canonical["status"] == "pass_agent_review_evidence", "canonical status")
    require(canonical["tenant_authorization_policy_reviewed"] is True, "auth review")
    require(canonical["tenant_secret_boundary_reviewed"] is True, "secret review")
    require(canonical["human_validation_used"] is False, "human boundary")
    require(canonical["agent_validation_primary"] is True, "agent primary")
    require(canonical["security_review_completed"] is False, "security boundary")
    require(canonical["privacy_legal_review_completed"] is False, "privacy boundary")

    variants = (
        lambda root, p: mutate_json(p.auth_validation, lambda d: d.update(verdict="conditional")),
        lambda root, p: mutate_json(p.auth_validation, lambda d: d["round_3"].update(blocker_count=1)),
        lambda root, p: mutate_json(p.auth_validation, lambda d: d.update(blockers=["synthetic"])),
        lambda root, p: mutate_json(p.auth_profile, lambda d: d.update(negative_cases_passed=13)),
        lambda root, p: (root / next(iter(AUTH_SOURCE_SET))).write_text("tampered\n", encoding="utf-8"),
        lambda root, p: mutate_json(p.auth_profile, lambda d: d["source_sha256"].pop(next(iter(d["source_sha256"])))),
        lambda root, p: mutate_json(p.auth_validation, lambda d: d.update(recommendation_scope="wrong")),
        lambda root, p: mutate_json(p.secret_profile, lambda d: d.update(production_ready=True)),
        lambda root, p: p.secret_validation.unlink(),
        lambda root, p: p.secret_profile.write_text("{not-json", encoding="utf-8"),
    )
    for case_id, mutate in zip(NEGATIVE_CASE_IDS, variants, strict=True):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            paths = copy_fixture(root)
            mutate(root, paths)
            require_atomic_hold(root, paths, case_id)

    print(
        "SAEE_TENANT_AGENT_REVIEW_EVIDENCE_SMOKE: PASS "
        "reviews=2/2 negative_cases=10/10 atomic_fail_closed=true "
        "human_validation_used=false agent_validation_primary=true "
        "security_review_completed=false privacy_legal_review_completed=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
