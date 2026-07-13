#!/usr/bin/env python3
"""Fail-closed preflight and final artifact validation for Phase 7.3."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from scripts.saee_agent_reliability_research_report import MANIFEST,PHASE7_2_STATUS,README,REPORT,SCHEMA,SOURCE_REFS,STATUS,build_artifact


def main() -> int:
    phase= json.loads(PHASE7_2_STATUS.read_text(encoding="utf-8"))
    if phase["execution_complete"] is not True:
        try: build_artifact()
        except ValueError as exc: assert str(exc)=="PHASE7_2_EXTENDED_BENCHMARK_INCOMPLETE"
        else: raise AssertionError("incomplete Phase 7.2 accepted")
        status=json.loads(STATUS.read_text(encoding="utf-8")); assert status["research_artifact_generated"] is False and status["blocking_condition"]=="PHASE7_2_EXTENDED_BENCHMARK_INCOMPLETE"
        print("SAEE_AGENT_RELIABILITY_RESEARCH_REPORT_SMOKE: PASS_PRECONDITION_BLOCK")
        print("phase7_2_dependency_complete=false")
        print("research_artifact_generated=false")
        print("ranking_generated=false")
        print("production_ready=false")
        return 0
    assert all(path.exists() for path in (MANIFEST,README,REPORT,STATUS))
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8")); assert manifest["run_count"]==75 and len(manifest["sources"])==len(SOURCE_REFS)
    for item in manifest["sources"]: assert hashlib.sha256((ROOT/item["reference"]).read_bytes()).hexdigest()==item["sha256"]
    text=REPORT.read_text(encoding="utf-8"); assert not any(term in text for term in ("最佳模型是","已通过安全认证","生产部署已批准","总体可靠性概率为"))
    print("SAEE_AGENT_RELIABILITY_RESEARCH_REPORT_SMOKE: PASS")
    print("run_count=75/75")
    print(f"source_bindings={len(SOURCE_REFS)}/{len(SOURCE_REFS)}")
    print("ranking_generated=false")
    print("publicly_published=false")
    print("production_ready=false")
    return 0


if __name__=="__main__": raise SystemExit(main())
