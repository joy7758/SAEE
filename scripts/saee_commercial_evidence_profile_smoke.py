#!/usr/bin/env python3
"""Smoke check for the SAEE commercial evidence profile."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROFILE_DIR = ROOT / "phase_b_product/commercial_readiness/commercial_evidence_profile"
PROFILE_JSON = PROFILE_DIR / "local_evidence_profile.json"
PROFILE_RESULT_JSON = PROFILE_DIR / "local_evidence_profile_result.json"
PROFILE_ENV = PROFILE_DIR / "local_evidence_profile.env.example"
PROFILE_MD = PROFILE_DIR / "local_evidence_profile.md"
README_PATH = PROFILE_DIR / "README.md"
DOC_PATH = ROOT / "phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_PROFILE_V0_1.md"
GATE_PATH = ROOT / "docs/strategy/SAEE_COMMERCIAL_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md"
COMBINED_DATA_OPS_EVIDENCE_PATH = (
    "phase_b_product/commercial_readiness/data_operations_evidence/"
    "production_data_operations_evidence.combined_profile.local.json"
)
COMBINED_OPERATIONS_EVIDENCE_PATH = (
    "phase_b_product/commercial_readiness/operations_evidence/"
    "production_operations_evidence.combined_profile.local.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        print(f"SAEE_COMMERCIAL_EVIDENCE_PROFILE_SMOKE: FAIL {message}")
        sys.exit(1)


def main() -> None:
    for path in [
        PROFILE_JSON,
        PROFILE_RESULT_JSON,
        PROFILE_ENV,
        PROFILE_MD,
        README_PATH,
        DOC_PATH,
        GATE_PATH,
    ]:
        require(path.exists(), f"missing {path.relative_to(ROOT)}")

    profile = json.loads(PROFILE_JSON.read_text(encoding="utf-8"))
    result = json.loads(PROFILE_RESULT_JSON.read_text(encoding="utf-8"))

    expected_false = [
        "evidence_profile_default_enabled",
        "profile_closes_blockers_by_default",
        "task_candidates_executed",
        "development_permission_granted",
        "production_ready",
        "customer_validated",
        "product_launched",
        "customer_contacted",
        "public_sdk_released",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "external_model_api_called",
        "external_ai_assistant_tested",
    ]
    for key in expected_false:
        require(profile.get(key) is False, f"profile {key} must be false")

    require(profile.get("profile_type") == "saee_commercial_evidence_profile", "wrong profile_type")
    require(
        profile.get("profile_scope") == "local_public_shell_evidence_path_profile",
        "wrong profile_scope",
    )
    require(profile.get("explicit_env_configuration_required") is True, "explicit env required")
    require(profile.get("human_review_required") is True, "human review required")
    require(profile.get("local_evidence_categories") == 8, "must map 8 evidence categories")
    require(profile.get("all_profile_paths_present") is True, "profile paths must exist")
    require(profile.get("all_profile_paths_configured") is True, "profile paths configured")
    require(profile.get("all_evidence_categories_ready") is False, "evidence must not all be ready")
    require(
        profile.get("data_operations_combined_profile_integrated") is True,
        "combined data-operations profile must be integrated",
    )
    require(
        profile.get("data_operations_evidence_path") == COMBINED_DATA_OPS_EVIDENCE_PATH,
        "data operations evidence path must use combined profile",
    )
    require(
        profile.get("operations_combined_profile_integrated") is True,
        "combined operations profile must be integrated",
    )
    require(
        profile.get("operations_evidence_path") == COMBINED_OPERATIONS_EVIDENCE_PATH,
        "operations evidence path must use combined profile",
    )
    require(profile.get("profile_status") == "local_evidence_profile_ready_hold", "wrong status")

    go = profile.get("commercial_go_no_go", {})
    require(go == result, "result JSON must mirror commercial_go_no_go subset")
    require(go.get("production_launch_status") == "hold", "production launch must remain hold")
    require(go.get("production_blocker_count") == 24, "24 production blockers must remain")
    require(go.get("total_production_checks") == 24, "24 production checks expected")
    require(go.get("blockers_satisfied_by_profile") == 0, "profile must not satisfy blockers")
    require(go.get("blockers_closed_by_profile") == 0, "profile closes zero blockers")
    require(
        go.get("local_public_shell_review_candidate_count") == 1,
        "one local public-shell evidence check should be a review candidate",
    )
    require(
        go.get("local_profile_unsatisfied_blocker_count") == 23,
        "23 local-profile blocker checks remain unsatisfied",
    )
    require(
        len(go.get("unsatisfied_blocker_ids", [])) == 23,
        "23 local-profile blocker checks remain unsatisfied",
    )
    require(len(go.get("open_blocker_ids", [])) == 24, "24 blockers remain open")

    paths = profile.get("profile_paths", [])
    require(len(paths) == 8, "profile must record 8 paths")
    for item in paths:
        require(item.get("file_exists") is True, "profile path file must exist")
        require(item.get("env_var", "").startswith("SAEE_PRODUCTION_"), "env var boundary")
    data_ops_paths = [
        item.get("local_path")
        for item in paths
        if item.get("env_var") == "SAEE_PRODUCTION_DATA_OPERATIONS_EVIDENCE_PATH"
    ]
    operations_paths = [
        item.get("local_path")
        for item in paths
        if item.get("env_var") == "SAEE_PRODUCTION_OPERATIONS_EVIDENCE_PATH"
    ]
    require(
        data_ops_paths == [COMBINED_DATA_OPS_EVIDENCE_PATH],
        "data operations env path must point to combined profile",
    )
    require(
        operations_paths == [COMBINED_OPERATIONS_EVIDENCE_PATH],
        "operations env path must point to combined profile",
    )

    env_text = PROFILE_ENV.read_text(encoding="utf-8")
    for item in paths:
        require(item["env_var"] in env_text, f"env missing {item['env_var']}")
        require(item["local_path"] in env_text, f"env missing {item['local_path']}")

    combined_docs = "\n".join(
        [
            PROFILE_MD.read_text(encoding="utf-8"),
            README_PATH.read_text(encoding="utf-8"),
            DOC_PATH.read_text(encoding="utf-8"),
            GATE_PATH.read_text(encoding="utf-8"),
        ]
    )
    required_tokens = [
        "local_public_shell_evidence_path_profile",
        "production_launch_status: hold",
        "production_blocker_count: 24",
        "total_production_checks: 24",
        "data_operations_combined_profile_integrated: true",
        "operations_combined_profile_integrated: true",
        COMBINED_DATA_OPS_EVIDENCE_PATH,
        COMBINED_OPERATIONS_EVIDENCE_PATH,
        "blockers_satisfied_by_profile: 0",
        "blockers_closed_by_profile: 0",
        "local_public_shell_review_candidate_count: 1",
        "production_ready: false",
        "customer_validated: false",
        "product_launched: false",
        "private_core_exposed: false",
    ]
    for token in required_tokens:
        require(token in combined_docs, f"docs missing {token}")

    forbidden_tokens = [
        "production_ready: true",
        '"production_ready": true',
        "customer_validated: true",
        '"customer_validated": true',
        "product_launched: true",
        '"product_launched": true',
        "private_core_exposed: true",
        '"private_core_exposed": true',
        "blockers_satisfied_by_profile: 1",
        '"blockers_satisfied_by_profile": 1',
        "blockers_closed_by_profile: 1",
        '"blockers_closed_by_profile": 1',
        "external_calls_made: true",
        '"external_calls_made": true',
    ]
    found = [token for token in forbidden_tokens if token in combined_docs]
    require(not found, "forbidden claims found: " + ", ".join(found))

    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    required_llms = [
        "/phase_b_product/commercial_readiness/COMMERCIAL_EVIDENCE_PROFILE_V0_1.md",
        "/docs/strategy/SAEE_COMMERCIAL_EVIDENCE_PROFILE_RECOMMENDATION_GATE.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_profile/README.md",
        "/phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.env.example",
        "/phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.json",
        "/phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile_result.json",
        "/phase_b_product/commercial_readiness/commercial_evidence_profile/local_evidence_profile.md",
        "/scripts/saee_commercial_evidence_profile.py",
        "/scripts/saee_commercial_evidence_profile_smoke.py",
    ]
    missing = [path for path in required_llms if path not in llms]
    require(not missing, "llms missing " + ", ".join(missing))

    index = json.loads((ROOT / "agent-index.json").read_text(encoding="utf-8"))
    entry = index.get("commercial_evidence_profile_v0_1", {})
    expected_entry = {
        "status": "local_evidence_profile_ready_hold",
        "commercial_evidence_profile_v0_1": True,
        "profile_scope": "local_public_shell_evidence_path_profile",
        "local_evidence_categories": 8,
        "data_operations_combined_profile_integrated": True,
        "data_operations_evidence_path": COMBINED_DATA_OPS_EVIDENCE_PATH,
        "operations_combined_profile_integrated": True,
        "operations_evidence_path": COMBINED_OPERATIONS_EVIDENCE_PATH,
        "production_launch_status": "hold",
        "production_blocker_count": 24,
        "blockers_satisfied_by_profile": 0,
        "blockers_closed_by_profile": 0,
        "local_public_shell_review_candidate_count": 1,
        "production_ready": False,
        "customer_validated": False,
        "product_launched": False,
        "private_core_exposed": False,
        "external_calls_made": False,
        "runtime_modified": False,
        "backend_modified": False,
        "kernel_modified": False,
        "api_schema_modified": False,
    }
    for key, value in expected_entry.items():
        require(entry.get(key) == value, f"agent-index {key} must be {value}")

    print(
        "SAEE_COMMERCIAL_EVIDENCE_PROFILE_SMOKE: PASS "
        "categories=8 production_launch_status=hold production_blockers=24 "
        "blockers_satisfied_by_profile=0 blockers_closed_by_profile=0 "
        "local_public_shell_review_candidate_count=1 "
        "production_ready=false customer_validated=false"
    )


if __name__ == "__main__":
    main()
