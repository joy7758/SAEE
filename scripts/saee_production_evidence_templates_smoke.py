#!/usr/bin/env python3
"""Smoke test the SAEE production evidence template pack."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings
from saee_backend.services.commercial_go_no_go import evaluate_commercial_go_no_go
from scripts.generate_production_evidence_templates import TEMPLATE_DIR, TEMPLATE_SPECS


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"SAEE_PRODUCTION_EVIDENCE_TEMPLATES_SMOKE: FAIL {message}")


def load_json(path: Path) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"SAEE_PRODUCTION_EVIDENCE_TEMPLATES_SMOKE: FAIL invalid json {path}: {exc}"
        ) from exc
    require(isinstance(data, dict), f"{path} must contain a JSON object")
    return data


def main() -> None:
    require(TEMPLATE_DIR.exists(), "template directory missing")
    required_files = [
        TEMPLATE_DIR / "README.md",
        TEMPLATE_DIR / "PRODUCTION_EVIDENCE_TEMPLATE_INDEX.json",
        TEMPLATE_DIR / "PRODUCTION_EVIDENCE_ENV.example",
    ]
    required_files.extend(TEMPLATE_DIR / spec.filename for spec in TEMPLATE_SPECS)
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    require(not missing, "missing files: " + ", ".join(missing))

    index = load_json(TEMPLATE_DIR / "PRODUCTION_EVIDENCE_TEMPLATE_INDEX.json")
    require(
        index.get("template_pack_type") == "saee_production_evidence_template_pack",
        "index template_pack_type mismatch",
    )
    require(index.get("template_status") == "placeholder_only", "index status mismatch")
    require(index.get("template_count") == len(TEMPLATE_SPECS), "template count mismatch")
    require(
        index.get("production_blockers_closed_by_templates") == 0,
        "placeholder templates must close zero production blockers",
    )

    for boundary_key in [
        "production_ready",
        "customer_validated",
        "product_launched",
        "public_sdk_released",
        "private_core_exposed",
        "runtime_modified",
        "backend_modified",
        "kernel_modified",
        "api_schema_modified",
        "external_calls_made",
        "customer_contacted",
    ]:
        require(index.get(boundary_key) is False, f"index {boundary_key} must be false")

    env_example = (TEMPLATE_DIR / "PRODUCTION_EVIDENCE_ENV.example").read_text(
        encoding="utf-8"
    )
    env = {
        "SAEE_ENV": "production",
        "SAEE_ALLOWED_ORIGINS": "https://example.invalid",
        "SAEE_REQUIRE_API_KEY": "true",
        "SAEE_API_KEY": "template-smoke-only",
        "SAEE_STORAGE_BACKEND": "sqlite",
        "SAEE_STORAGE_PATH": ".saee_data/template-smoke.sqlite3",
        "SAEE_REQUEST_AUDIT_ENABLED": "true",
        "SAEE_RETENTION_DAYS": "30",
        "SAEE_RETENTION_DRY_RUN": "true",
        "SAEE_REQUIRE_TENANT_ID": "true",
        "SAEE_ALLOWED_TENANT_IDS": "template-tenant",
        "SAEE_SECURITY_CONTACT": "security@example.invalid",
    }

    for spec in TEMPLATE_SPECS:
        template_path = TEMPLATE_DIR / spec.filename
        data = load_json(template_path)
        require(
            data.get("template_type") == "saee_production_evidence_template",
            f"{spec.filename} template_type mismatch",
        )
        require(
            data.get("template_status") == "placeholder_only",
            f"{spec.filename} template status mismatch",
        )
        require(data.get(spec.type_key) == spec.type_value, f"{spec.filename} type mismatch")
        require(spec.env_var in env_example, f"{spec.env_var} missing from env example")
        env[spec.env_var] = str(template_path)

        for _, keys in spec.groups:
            for key in keys:
                require(key in data, f"{spec.filename} missing required key {key}")
                require(data.get(key) is False, f"{spec.filename} {key} must default false")

        for key in spec.forbidden_true_keys:
            require(key in data, f"{spec.filename} missing forbidden key {key}")
            require(data.get(key) is False, f"{spec.filename} {key} must remain false")

    go_no_go = evaluate_commercial_go_no_go(load_settings(env))
    require(go_no_go["production_ready"] is False, "production_ready must remain false")
    require(go_no_go["customer_validated"] is False, "customer_validated must remain false")
    require(go_no_go["product_launched"] is False, "product_launched must remain false")
    require(go_no_go["private_core_exposed"] is False, "private_core_exposed must remain false")
    require(
        go_no_go["production_launch_status"] == "hold",
        "placeholder templates must not produce production launch go",
    )
    require(
        go_no_go["production_blocker_count"] == go_no_go["total_production_checks"],
        "placeholder templates must not satisfy production blockers",
    )

    print(
        "SAEE_PRODUCTION_EVIDENCE_TEMPLATES_SMOKE: PASS "
        f"templates={len(TEMPLATE_SPECS)} production_launch_status="
        f"{go_no_go['production_launch_status']} production_ready=false "
        "customer_validated=false private_core_exposed=false"
    )


if __name__ == "__main__":
    main()
