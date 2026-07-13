#!/usr/bin/env python3
"""Smoke check for fail-closed synthetic-data-only controlled preview mode."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.config import load_settings


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_SYNTHETIC_DATA_ONLY_MODE_SMOKE: FAIL: " + message)


def main() -> None:
    local = load_settings({})
    require(local.synthetic_data_only is True, "local default must stay synthetic only")
    require(local.ready is True, "local synthetic-only default must remain ready")

    preview_missing = load_settings({"SAEE_ENV": "preview"})
    require(preview_missing.synthetic_data_only is False, "preview must require explicit mode")
    require(preview_missing.ready is False, "preview without synthetic mode must fail closed")

    preview_disabled = load_settings(
        {"SAEE_ENV": "preview", "SAEE_SYNTHETIC_DATA_ONLY": "false"}
    )
    require(preview_disabled.ready is False, "disabled synthetic mode must fail closed")

    preview_enabled = load_settings(
        {"SAEE_ENV": "preview", "SAEE_SYNTHETIC_DATA_ONLY": "true"}
    )
    payload = preview_enabled.readiness_payload()
    require(preview_enabled.ready is True, "explicit synthetic-only preview must be ready")
    require(payload["synthetic_data_only"] is True, "readiness must expose mode")
    require(payload["real_customer_data_allowed"] is False, "real data must remain forbidden")
    require(payload["deidentification_proven"] is False, "deidentification must not be claimed")
    require(payload["general_dlp_available"] is False, "general DLP must remain false")

    print(
        "SAEE_SYNTHETIC_DATA_ONLY_MODE_SMOKE: PASS preview_missing_fail_closed=true "
        "explicit_mode_required=true real_customer_data_allowed=false "
        "deidentification_proven=false general_dlp_available=false production_ready=false"
    )


if __name__ == "__main__":
    main()
