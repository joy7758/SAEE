#!/usr/bin/env python3
"""Shared commercial-review state semantics for SAEE scripts.

These helpers prevent local public-shell evidence from being represented as
production blocker closure. Local evidence can become a review candidate, but
production blocker satisfaction and closure stay at zero until separate
human-approved production evidence exists.
"""

from __future__ import annotations

from typing import Any


def local_public_shell_go_no_go_summary(go_no_go: dict[str, Any]) -> dict[str, Any]:
    """Return a review-only summary of a local-profile commercial go/no-go result."""

    total_checks = int(go_no_go["total_production_checks"])
    raw_satisfied = int(go_no_go["satisfied_production_checks"])
    raw_unsatisfied = int(go_no_go["production_blocker_count"])
    return {
        "commercial_status": go_no_go["commercial_status"],
        "production_launch_status": go_no_go["production_launch_status"],
        "satisfied_production_checks": 0,
        "production_blocker_count": total_checks,
        "total_production_checks": total_checks,
        "local_public_shell_review_candidate_count": raw_satisfied,
        "local_profile_unsatisfied_blocker_count": raw_unsatisfied,
        "boundary_violation_count": go_no_go["boundary_violation_count"],
        "open_blocker_ids": [item["blocker_id"] for item in go_no_go["blockers"]],
        "unsatisfied_blocker_ids": [
            item["blocker_id"] for item in go_no_go["unsatisfied_blockers"]
        ],
    }
