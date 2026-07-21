#!/usr/bin/env python3
"""Offline smoke for the Agent Evidence to SAEE Evaluation bridge."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.agent_evidence_evaluation_bridge import (
    ADEQUACY_NOT_SATISFIED,
    BINDING_DIGEST_MISMATCH,
    BINDING_EVENT_UNKNOWN,
    ED25519_NOT_VERIFIED,
    INPUT_SCHEMA_INVALID,
    UPSTREAM_NOT_PASS,
    route_agent_evidence_to_evaluation,
)
from saee_backend.services.agent_evidence_trait_adapter import (
    adapt_agent_evidence_traits,
)


FIXTURES = ROOT / "agent-interface/integration/agent-evidence-compatibility/fixtures"
ADEQUACY_EXAMPLES = ROOT / "agent-interface/examples/evidence-adequacy"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def make_input(source_fixture: str = "valid-signed.v0.1.json") -> dict:
    adapter = adapt_agent_evidence_traits(load_json(FIXTURES / source_fixture))
    return {
        "saee_agent_evidence_evaluation_bridge_input_v0_1": True,
        "schema_version": "0.1.0",
        "adapter_result": adapter,
        "claim_type": "EXECUTION_BOUNDARY",
        "adequacy_package": load_json(ADEQUACY_EXAMPLES / "execution_boundary_pass.json"),
        "binding": {
            "adapter_receipt_digest": adapter["adapter_receipt_digest"],
            "event_ids": [item["event_id"] for item in adapter["candidate_evidence"]],
            "binding_status": "declared_only_not_independently_verified",
        },
        "truth_boundary": {
            "source_event_authenticity_verified": False,
            "binding_independently_verified": False,
            "authorization_verified": False,
            "action_authorized": False,
            "production_ready": False,
        },
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    signed_input = make_input()
    routed = route_agent_evidence_to_evaluation(signed_input)
    require(routed["bridge_status"] == "ROUTED", "signed bridge not routed")
    require(routed["decision"] == "HUMAN_REVIEW", "strongest decision boundary changed")
    require(routed["adequacy_result"]["result"] == "PASS", "adequacy PASS missing")
    require(all(value is False for value in routed["truth_boundary"].values()), "truth upgraded")

    unsigned = route_agent_evidence_to_evaluation(make_input("valid-pass.v0.1.json"))
    require(unsigned["decision"] == "REPLAN", "unsigned bridge promoted")
    require(ED25519_NOT_VERIFIED in unsigned["reason_codes"], "unsigned reason missing")

    warned = route_agent_evidence_to_evaluation(make_input("valid-warn.v0.1.json"))
    require(warned["decision"] == "REPLAN", "WARN bridge promoted")
    require(UPSTREAM_NOT_PASS in warned["reason_codes"], "WARN reason missing")

    failed_adequacy_input = make_input()
    del failed_adequacy_input["adequacy_package"]["evidence"]["causal_link"]
    failed_adequacy = route_agent_evidence_to_evaluation(failed_adequacy_input)
    require(ADEQUACY_NOT_SATISFIED in failed_adequacy["reason_codes"], "adequacy FAIL promoted")

    bad_digest_input = make_input()
    bad_digest_input["binding"]["adapter_receipt_digest"] = "sha256:" + "0" * 64
    bad_digest = route_agent_evidence_to_evaluation(bad_digest_input)
    require(BINDING_DIGEST_MISMATCH in bad_digest["reason_codes"], "digest mismatch accepted")
    require(bad_digest["saee_evaluator_called"] is False, "evaluator called after digest mismatch")

    unknown_event_input = make_input()
    unknown_event_input["binding"]["event_ids"] = ["event:unknown"]
    unknown_event = route_agent_evidence_to_evaluation(unknown_event_input)
    require(BINDING_EVENT_UNKNOWN in unknown_event["reason_codes"], "unknown event accepted")

    open_input = make_input()
    open_input["unexpected"] = True
    rejected = route_agent_evidence_to_evaluation(open_input)
    require(INPUT_SCHEMA_INVALID in rejected["reason_codes"], "open bridge input accepted")

    repeated = [route_agent_evidence_to_evaluation(signed_input) for _ in range(10)]
    require(all(result == repeated[0] for result in repeated), "bridge is not deterministic")
    require(signed_input == make_input(), "bridge mutated input")

    print("SAEE_AGENT_EVIDENCE_EVALUATION_BRIDGE_SMOKE: PASS")
    print("positive_cases=1/1")
    print("negative_cases=6/6")
    print("deterministic_runs=10/10")
    print("strongest_decision=HUMAN_REVIEW")
    print("existing_adequacy_evaluator_reused=true")
    print("source_event_authenticity_verified=false")
    print("binding_independently_verified=false")
    print("action_authorized=false")
    print("external_action_performed=false")
    print("runtime_integrated=false")
    print("production_ready=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
