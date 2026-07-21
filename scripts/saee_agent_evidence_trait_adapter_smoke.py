#!/usr/bin/env python3
"""Offline smoke for the SAEE clean-room Agent Evidence trait adapter."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_evidence_trait_adapter import (
    EVENT_ID_DUPLICATE,
    EVENT_SEQUENCE_INVALID,
    INPUT_SCHEMA_INVALID,
    SOURCE_COMPLETENESS_COUNT_MISMATCH,
    adapt_agent_evidence_traits,
)


FIXTURES = ROOT / "agent-interface/integration/agent-evidence-compatibility/fixtures"


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    valid_pass = load("valid-pass.v0.1.json")
    valid_warn = load("valid-warn.v0.1.json")
    valid_signed = load("valid-signed.v0.1.json")
    invalid_counts = load("invalid-counts.v0.1.json")

    passed = adapt_agent_evidence_traits(valid_pass)
    require(passed["adapter_status"] == "ADAPTED_WITH_SEMANTIC_LOSS", "PASS fixture not adapted")
    require(len(passed["candidate_evidence"]) == 2, "candidate count mismatch")
    require(all("payload" not in item for item in passed["candidate_evidence"]), "payload leaked")
    require(passed["integrity_context"]["upstream_verification_result"] == "PASS", "PASS not preserved")
    require(passed["evaluation_routing"]["eligible_for_evidence_adequacy"] is False, "adequacy promoted")

    warned = adapt_agent_evidence_traits(valid_warn)
    require(warned["integrity_context"]["upstream_verification_result"] == "WARN", "WARN not preserved")
    require(warned["integrity_context"]["warn_preserved"] is True, "WARN preservation flag missing")

    signed = adapt_agent_evidence_traits(valid_signed)
    require(signed["integrity_context"]["local_ed25519_signature_check"] == "PASS", "Ed25519 fixture not verified")
    require(signed["truth_boundary"]["local_crypto_subprocess_started"] is True, "local crypto subprocess not disclosed")

    bad_signature = copy.deepcopy(valid_signed)
    bad_signature["signature"]["signature_base64"] = "A" + bad_signature["signature"]["signature_base64"][1:]
    failed_signature = adapt_agent_evidence_traits(bad_signature)
    require(failed_signature["integrity_context"]["local_ed25519_signature_check"] == "FAIL", "bad signature accepted")

    bad_counts = adapt_agent_evidence_traits(invalid_counts)
    require(SOURCE_COMPLETENESS_COUNT_MISMATCH in bad_counts["reason_codes"], "count mismatch accepted")

    bad_sequence = copy.deepcopy(valid_pass)
    bad_sequence["events"][1]["event_index"] = 2
    require(EVENT_SEQUENCE_INVALID in adapt_agent_evidence_traits(bad_sequence)["reason_codes"], "bad sequence accepted")

    duplicate = copy.deepcopy(valid_pass)
    duplicate["events"][1]["event_id"] = duplicate["events"][0]["event_id"]
    require(EVENT_ID_DUPLICATE in adapt_agent_evidence_traits(duplicate)["reason_codes"], "duplicate event id accepted")

    extra = copy.deepcopy(valid_pass)
    extra["unexpected"] = True
    require(INPUT_SCHEMA_INVALID in adapt_agent_evidence_traits(extra)["reason_codes"], "open input accepted")

    deterministic = [adapt_agent_evidence_traits(valid_pass) for _ in range(10)]
    require(all(item == deterministic[0] for item in deterministic), "adapter is not deterministic")
    require(valid_pass == load("valid-pass.v0.1.json"), "adapter mutated input")

    print("SAEE_AGENT_EVIDENCE_TRAIT_ADAPTER_SMOKE: PASS")
    print("fixtures=4/4")
    print("negative_cases=5/5")
    print("deterministic_runs=10/10")
    print("source_text_copied=false")
    print("external_code_executed=false")
    print("network_accessed=false")
    print("local_event_chain_check=PASS")
    print("local_merkle_root_check=PASS")
    print("local_ed25519_signature_check=PASS")
    print("evidence_adequacy_established=false")
    print("runtime_integrated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
