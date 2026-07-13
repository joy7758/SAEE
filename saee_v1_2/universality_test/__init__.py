"""Cross-system universality tests for SAEE v1.2 parasitic phase research.

This package is intentionally separate from ``saee_v1_2.parasitic_phase``.
It imports DBI-1 as an unchanged reference system and implements DBI-2 as an
independent synthetic environment for invariance testing.
"""

from saee_v1_2.universality_test.dbi2_model import (
    DBI2Config,
    DBI2Simulation,
    DBI2SimulationResult,
)

__all__ = [
    "DBI2Config",
    "DBI2Simulation",
    "DBI2SimulationResult",
]
