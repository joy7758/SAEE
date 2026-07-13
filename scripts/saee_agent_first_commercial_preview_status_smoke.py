#!/usr/bin/env python3
"""Verify the bounded agent-first commercial-preview contract."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "agent-interface/agent-first-commercial-preview-status.json"
SCHEMA = ROOT / "agent-interface/schemas/agent-first-commercial-preview-status.schema.json"


def require(value: bool, message: str) -> None:
    if not value:
        raise SystemExit("SAEE_AGENT_FIRST_COMMERCIAL_PREVIEW_STATUS_SMOKE: FAIL " + message)


def main() -> None:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        import jsonschema
        jsonschema.validate(data, schema)
    except Exception as exc:
        raise SystemExit("SAEE_AGENT_FIRST_COMMERCIAL_PREVIEW_STATUS_SMOKE: FAIL schema=" + type(exc).__name__) from exc
    require(len(data["production_blockers"]) == 24, "blocker count")
    require(len(set(data["production_blockers"])) == 24, "blocker uniqueness")
    require(data["production_readiness"]["production_blocker_count"] == 24, "production count")
    require(data["production_readiness"]["open_production_blocker_count"] == 24, "open count")
    require(data["production_readiness"]["blockers_closed_by_contract"] == 0, "closure boundary")
    require(data["truth_boundary"]["production_ready"] is False, "production boundary")
    require(data["truth_boundary"]["customer_validated"] is False, "customer boundary")
    require(data["truth_boundary"]["qianfan_native_mcp_support_proven"] is False, "native MCP boundary")
    require(data["preview_capabilities"]["commercial_walkthroughs"]["real_customer_evidence"] is False, "walkthrough boundary")
    tenant = data["preview_capabilities"]["tenant_preview_storage"]
    require(tenant["verdict"] == "conditional" and tenant["same_experiment_id_partitioned"] is True, "tenant preview evidence")
    require(tenant["production_tenant_storage_isolated"] is False and tenant["multi_tenant_production_ready"] is False, "tenant production boundary")
    auth = data["preview_capabilities"]["preview_auth"]
    require(auth["default_off"] is True and auth["jwt_preview_available"] is True and auth["production_auth_ready"] is False, "preview auth boundary")
    restore = data["preview_capabilities"]["restore_drill"]
    require(restore["integrity_checks_passed"] is True and restore["restore_to_live_path"] is False, "restore drill evidence")
    require(restore["production_restore_policy_available"] is False and restore["production_data_operations_ready"] is False, "restore production boundary")
    support = data["preview_capabilities"]["agent_support_intake"]
    require(support["support_status"] == "owner_support_channel_required", "support status")
    require(support["external_dispatch_performed"] is False and support["customer_contacted"] is False, "support dispatch/contact boundary")
    require(support["production_ready"] is False and support["blockers_closed"] == 0, "support production boundary")
    phase1 = data["preview_capabilities"]["phase_1_local_hardening"]
    require(len(phase1["target_blockers"]) == 4, "Phase 1 target count")
    require(phase1["rbac_negative_cases"] == "5/5", "Phase 1 RBAC negative cases")
    require(phase1["tenant_required_storage_guard"] is True, "Phase 1 tenant-required storage guard")
    require(
        phase1["memory_store_unscoped_operations_denied"] is True
        and phase1["sqlite_store_unscoped_operations_denied"] is True,
        "Phase 1 unscoped storage denial",
    )
    require(phase1["default_local_unscoped_mode_preserved"] is True, "Phase 1 default local compatibility")
    require(phase1["production_tenant_storage_isolated"] is False, "Phase 1 production tenant boundary")
    require(phase1["local_development_authorized"] is True, "Phase 1 local development")
    require(phase1["external_execution_authorized"] is False and phase1["production_deployment_authorized"] is False, "Phase 1 external boundary")
    require(phase1["production_data_migration_authorized"] is False and phase1["blockers_closed"] == 0, "Phase 1 migration/closure boundary")
    require(data["local_fixture_or_human_profile_promoted_to_production_truth"] is False, "fixture promotion")
    for ref in data["evidence_refs"].values():
        require((ROOT / ref).is_file(), "evidence ref=" + ref)
    for key, ref in (("current_action_sha256", data["evidence_refs"]["current_action"]), ("blocker_matrix_sha256", data["evidence_refs"]["blocker_matrix"]), ("qianfan_validation_sha256", data["evidence_refs"]["qianfan_validation"])):
        require(hashlib.sha256((ROOT / ref).read_bytes()).hexdigest() == data["source_hashes"][key], "source hash=" + key)
    print("SAEE_AGENT_FIRST_COMMERCIAL_PREVIEW_STATUS_SMOKE: PASS recommendation=recommend production_hold=true blockers=24 closed=0 schema=valid")


if __name__ == "__main__":
    main()
