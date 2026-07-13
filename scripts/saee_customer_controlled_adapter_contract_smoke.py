#!/usr/bin/env python3
"""Validate the default-disabled customer Agent adapter contract."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "agent-interface/rehearsal/saee-customer-controlled-agent-adapter-contract.v0.1.schema.json"
EXAMPLE = ROOT / "agent-interface/rehearsal/customer-adapter-contracts/custom-agent-declared-disabled.v0.1.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_CUSTOMER_CONTROLLED_ADAPTER_CONTRACT_SMOKE: FAIL " + message)


def valid(value: dict, schema: dict) -> bool:
    return not list(Draft202012Validator(schema).iter_errors(value))


def main() -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    value = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    require(valid(value, schema), "canonical example")
    mutations = []
    for section, field in (
        ("activation", "enabled"),
        ("activation", "human_activation_approved"),
        ("data_boundary", "customer_data_allowed"),
        ("runtime_boundary", "provider_network_allowed"),
        ("runtime_boundary", "external_world_actions_allowed"),
        ("capability_claims", "adapter_implemented"),
        ("capability_claims", "customer_agent_compatible"),
        ("truth_boundary", "customer_agent_executed"),
    ):
        item = copy.deepcopy(value)
        item[section][field] = True
        mutations.append((f"{section}.{field}", item))
    for label, item in mutations:
        require(not valid(item, schema), "invalid enabled claim accepted: " + label)
    text = EXAMPLE.read_text(encoding="utf-8")
    for marker in ("api_key", "access_token", "Bearer ", "bce-v3/ALTAK-"):
        require(marker not in text, "credential marker: " + marker)
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    for _ in range(5):
        repeated = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        require(json.dumps(repeated, ensure_ascii=False, sort_keys=True, separators=(",", ":")) == encoded, "non-deterministic")
    print(
        "SAEE_CUSTOMER_CONTROLLED_ADAPTER_CONTRACT_SMOKE: PASS valid_cases=1/1 "
        "invalid_cases=8/8 deterministic_runs=5/5 enabled=false adapter_implemented=false "
        "customer_agent_executed=false external_world_actions_allowed=false production_ready=false"
    )


if __name__ == "__main__":
    main()

