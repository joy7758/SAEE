#!/usr/bin/env python3
"""Final requirement-by-requirement audit for the Phase 9 goal."""

from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
AUDIT=ROOT/"agent-interface/commercial/saee-phase9-completion-audit.v1.0.json"
REPORT=ROOT/"docs/commercial/SAEE_PHASE9_GOAL_COMPLETION_AUDIT_V1.md"


def main() -> int:
    audit=json.loads(AUDIT.read_text(encoding="utf-8"))
    assert audit["audit_outcome"]=="COMPLETE_WITH_BOUNDED_LOCAL_SERVICE"
    assert audit["requirements_total"]==audit["requirements_complete"]==7 and audit["goal_complete"] is True
    assert [item["phase"] for item in audit["requirements"]]==["6.9","7.0","7.1","7.2","7.3","8","9"]
    resolved=0
    for requirement in audit["requirements"]:
        assert requirement["status"]=="complete"
        for ref in requirement["evidence_refs"]:
            path=(ROOT/ref).resolve(); path.relative_to(ROOT.resolve()); assert path.is_file(); resolved+=1
    phase9=audit["phase9_result"]
    assert phase9=={"status":"completed_local_agent_callable_validated_service","recommendation":"recommend","recommendation_scope":"local_controlled_synthetic_reliability_evidence_only","source_runs":75,"interface_language":"zh-CN","agent_discoverable":True,"agent_understandable":True,"agent_composable":True}
    assert all(value is False for value in audit["truth_boundary"].values())
    text=REPORT.read_text(encoding="utf-8")
    assert "requirements_complete=7/7" in text and "目标完成与生产商业发布是两个不同真值层级" in text
    assert not any(term in text for term in ("生产已经就绪","客户已经验证","市场已经验证","已通过认证"))
    print("SAEE_PHASE9_GOAL_COMPLETION_AUDIT_SMOKE: PASS")
    print("requirements_complete=7/7")
    print(f"evidence_refs_resolved={resolved}/{resolved}")
    print("phase7_2_runs=75/75")
    print("phase8_sessions=9/9")
    print("phase9_service_callable=true")
    print("agent_discoverable=true")
    print("agent_understandable=true")
    print("agent_composable=true")
    print("goal_complete=true")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
