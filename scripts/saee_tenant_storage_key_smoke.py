#!/usr/bin/env python3
"""Check the tenant storage key namespace against prefix-confusion attacks.

This is a local public-shell protection test. It does not claim production
multi-tenancy, authorization, customer-data processing, or external review.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.storage.tenant_key import (
    RESERVED_TENANT_STORAGE_PREFIX,
    tenant_public_experiment_id,
    tenant_storage_key,
    validate_experiment_id,
    validate_required_storage_tenant_id,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit("SAEE_TENANT_STORAGE_KEY_SMOKE: FAIL " + message)


def main() -> None:
    require(RESERVED_TENANT_STORAGE_PREFIX == "tenant:", "reserved prefix drift")
    require(validate_experiment_id("experiment-1") == "experiment-1", "valid ID")
    require(
        validate_required_storage_tenant_id(
            "tenant-a",
            required=True,
            allowed_tenant_ids=("tenant-a", "tenant-b"),
        )
        == "tenant-a",
        "required tenant accepted",
    )
    try:
        validate_required_storage_tenant_id(
            None,
            required=True,
            allowed_tenant_ids=("tenant-a", "tenant-b"),
        )
    except ValueError:
        pass
    else:
        raise SystemExit("SAEE_TENANT_STORAGE_KEY_SMOKE: FAIL missing required tenant accepted")
    require(validate_required_storage_tenant_id(None, required=False) is None, "optional tenant preserved")
    for tenant_id, allowlist in (
        ("tenant-c", ("tenant-a", "tenant-b")),
        ("tenant-a", ()),
        ("tenant-a", (" tenant-a",)),
    ):
        try:
            validate_required_storage_tenant_id(
                tenant_id,
                required=True,
                allowed_tenant_ids=allowlist,
            )
        except ValueError:
            pass
        else:
            raise SystemExit(
                "SAEE_TENANT_STORAGE_KEY_SMOKE: FAIL tenant membership boundary accepted invalid input"
            )

    for invalid in ("", "tenant:tenant-b:experiment-1"):
        try:
            validate_experiment_id(invalid)
        except ValueError:
            pass
        else:
            raise SystemExit(
                "SAEE_TENANT_STORAGE_KEY_SMOKE: FAIL reserved or empty ID accepted"
            )

    tenant_a_key = tenant_storage_key("same-experiment", "tenant-a")
    tenant_b_key = tenant_storage_key("same-experiment", "tenant-b")
    unscoped_key = tenant_storage_key("same-experiment")
    require(tenant_a_key != tenant_b_key, "tenant keys must differ")
    require(tenant_a_key != unscoped_key, "scoped and unscoped keys must differ")
    require(
        tenant_public_experiment_id(tenant_a_key, "tenant-a") == "same-experiment",
        "tenant A must read only its own public ID",
    )
    require(
        tenant_public_experiment_id(tenant_a_key, "tenant-b") is None,
        "tenant B must not read tenant A key",
    )
    require(
        tenant_public_experiment_id(unscoped_key, "tenant-a") is None,
        "scoped listing must not expose unscoped record",
    )
    require(
        tenant_public_experiment_id(tenant_a_key) is None,
        "unscoped listing must not expose tenant record",
    )
    require(
        tenant_public_experiment_id(unscoped_key) == "same-experiment",
        "unscoped record must remain visible only in unscoped scope",
    )
    print(
        "SAEE_TENANT_STORAGE_KEY_SMOKE: PASS "
        "reserved_prefix_rejected=true "
        "scoped_unscoped_collision_blocked=true "
        "cross_tenant_public_id_hidden=true "
        "required_tenant_missing_denied=true "
        "unlisted_tenant_denied=true "
        "strict_allowlist_fail_closed=true "
        "production_multi_tenant_claim=false"
    )


if __name__ == "__main__":
    main()
