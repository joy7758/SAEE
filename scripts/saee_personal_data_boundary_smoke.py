#!/usr/bin/env python3
"""Adversarial smoke for the local no-personal-data request boundary."""

from __future__ import annotations

import sys
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.core.runner import run_scenario_batch
from saee_backend.models.request import ExperimentCreateRequest, ScenarioBatchRequest
from saee_backend.services.public_input_contract import validate_secret_free_config


SENTINELS = {
    "email_value": "synthetic.person@example.invalid",
    "phone_value": "13800138000",
    "id_card_value": "11010519900101123X",
    "email_key": "synthetic-safe-value",
    "phone_key": "synthetic-safe-value",
    "name_key": "synthetic-safe-value",
    "id_card_key": "synthetic-safe-value",
    "address_key": "synthetic-safe-value",
}


def payload() -> dict:
    return {
        "experiment_id": "privacy-boundary",
        "agents": [
            {"agent_id": "agent-a", "config": {"policy": "bounded"}, "type": "llm"},
            {"agent_id": "agent-b", "config": "guarded-stable", "type": "workflow"},
        ],
        "environment": {
            "scenario_type": "privacy_boundary",
            "noise_level": 0.2,
            "competition_intensity": 0.4,
            "time_horizon": 20,
        },
        "evaluation_config": {
            "metrics": ["stability", "survival", "failure_mode", "ranking"],
            "repeat_runs": 3,
        },
    }


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: " + message)


def rejected(data: dict, sentinel: str) -> None:
    try:
        ScenarioBatchRequest.model_validate(data)
    except ValueError as exc:
        require(sentinel not in str(exc), "personal data reflected in validation error")
        return
    raise SystemExit("SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: personal data accepted")


def main() -> None:
    for case_id, sentinel in SENTINELS.items():
        data = payload()
        if case_id.endswith("_value"):
            data["agents"][0]["config"] = {"policy": sentinel}
        else:
            data["agents"][0]["config"] = {case_id.removesuffix("_key"): sentinel}
        rejected(data, sentinel)

    create_metadata_cases = {
        "name": SENTINELS["email_value"],
        "description": SENTINELS["phone_value"],
        "owner_label": SENTINELS["id_card_value"],
        "created_by": SENTINELS["email_value"],
    }
    for field_name, sentinel in create_metadata_cases.items():
        try:
            ExperimentCreateRequest.model_validate({field_name: sentinel})
        except ValueError as exc:
            require(sentinel not in str(exc), "create metadata reflected personal data")
        else:
            raise SystemExit(
                "SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: "
                f"create metadata {field_name} accepted personal data"
            )

    free_text_cases = {
        "name": "张三",
        "description": "北京市朝阳区某街道88号",
        "owner_label": "李四",
        "created_by": "上海市浦东新区某路66号",
    }
    for field_name, sentinel in free_text_cases.items():
        try:
            ExperimentCreateRequest.model_validate({field_name: sentinel})
        except ValueError as exc:
            require(sentinel not in str(exc), "create metadata reflected Chinese personal data")
        else:
            raise SystemExit(
                "SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: "
                f"create metadata {field_name} accepted free text"
            )

    closed_contract_cases = (
        {"applicant_name": "张三"},
        {"联系地址": "北京市朝阳区某街道88号"},
        {"policy": ["bounded"]},
        {"policy": b"opaque"},
    )
    for value in closed_contract_cases:
        try:
            validate_secret_free_config(value)
        except ValueError:
            pass
        else:
            raise SystemExit(
                "SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: closed config contract accepted unsafe shape"
            )

    config_value_cases = (
        "张三",
        "北京市朝阳区某街道88号",
        "１３８００１３８０００",
        "ｐｅｒｓｏｎ＠ｅｘａｍｐｌｅ．ｃｏｍ",
    )
    for sentinel in config_value_cases:
        data = payload()
        data["agents"][0]["config"] = {"policy": sentinel}
        rejected(data, sentinel)

        valid_for_bypass = ScenarioBatchRequest.model_validate(payload())
        bypassed_value = ScenarioBatchRequest.model_construct(
            experiment_id=valid_for_bypass.experiment_id,
            agents=deepcopy(valid_for_bypass.agents),
            environment=valid_for_bypass.environment,
            evaluation_config=valid_for_bypass.evaluation_config,
        )
        bypassed_value.agents[0].config = {"policy": sentinel}
        try:
            run_scenario_batch(bypassed_value)
        except ValueError as exc:
            require(sentinel not in str(exc), "runner reflected normalized personal data")
        else:
            raise SystemExit(
                "SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: runner accepted unsafe config value"
            )

    valid = ScenarioBatchRequest.model_validate(payload())
    bypassed = ScenarioBatchRequest.model_construct(
        experiment_id=valid.experiment_id,
        agents=deepcopy(valid.agents),
        environment=valid.environment,
        evaluation_config=valid.evaluation_config,
    )
    bypassed.agents[0].config = {"policy": SENTINELS["phone_value"]}
    try:
        run_scenario_batch(bypassed)
    except ValueError as exc:
        require(SENTINELS["phone_value"] not in str(exc), "runner reflected phone")
    else:
        raise SystemExit("SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: FAIL: runner bypass accepted")

    print(
        "SAEE_PERSONAL_DATA_BOUNDARY_SMOKE: PASS negative_cases=29/29 "
        "email_rejected=true phone_rejected=true id_card_rejected=true "
        "personal_data_keys_rejected=true create_metadata_rejected=true "
        "chinese_free_text_rejected=true unknown_keys_rejected=true "
        "arrays_and_bytes_rejected=true "
        "unicode_nfkc_bypass_rejected=true config_values_identifier_only=true "
        "runner_revalidation=true "
        "human_validation_used=false privacy_legal_review_completed=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
