#!/usr/bin/env python3
"""Generate the atomic independent-agent tenant review evidence record."""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from saee_backend.services.tenant_agent_review_evidence import (
    evaluate_tenant_agent_review_evidence,
)


OUTPUT = ROOT / "phase_b_product/commercial_readiness/tenant_agent_review/tenant_agent_review.local.json"


def atomic_write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> None:
    data = evaluate_tenant_agent_review_evidence(ROOT)
    atomic_write_json(OUTPUT, data)
    if data["status"] != "pass_agent_review_evidence":
        raise SystemExit("SAEE_TENANT_AGENT_REVIEW_EVIDENCE: HOLD")
    print(
        "SAEE_TENANT_AGENT_REVIEW_EVIDENCE: PASS reviews=2/2 "
        "human_validation_used=false agent_validation_primary=true "
        "security_review_completed=false privacy_legal_review_completed=false "
        "production_ready=false blockers_closed=0"
    )


if __name__ == "__main__":
    main()
