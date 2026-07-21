"""Tests for the SAEE Project Memory governance boundary."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "saee_project_memory_check.py"
SPEC = importlib.util.spec_from_file_location("saee_project_memory_check", MODULE_PATH)
assert SPEC and SPEC.loader
CHECK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK)


class ProjectMemoryTest(unittest.TestCase):
    def test_01_required_files_exist(self) -> None:
        for name in CHECK.REQUIRED_FILES:
            self.assertTrue((CHECK.MEMORY_DIR / name).is_file(), name)

    def test_02_full_validation_passes(self) -> None:
        self.assertEqual(CHECK.validate_project_memory(ROOT), [])

    def test_03_frozen_decisions_are_complete(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "frozen-decisions.md")
        entries = CHECK.sections(text, "F")
        self.assertEqual(set(entries), CHECK.REQUIRED_FROZEN_IDS)
        self.assertEqual(CHECK.validate_frozen_text(text), [])

    def test_04_empty_frozen_decision_is_rejected(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "frozen-decisions.md")
        mutated = text.replace(
            "决定：\n\nAgent Evidence Receipt",
            "决定：\n\n主题：\n\nAgent Evidence Receipt",
            1,
        )
        errors = CHECK.validate_frozen_text(mutated)
        self.assertTrue(any("F-001 has empty or missing 决定" in error for error in errors))

    def test_05_memory_policy_has_change_gate(self) -> None:
        policy = CHECK.read_text(CHECK.MEMORY_DIR / "memory-policy.md")
        self.assertIn("Decision Change Proposal", policy)
        self.assertIn("AI 不得自行解除冻结", policy)
        self.assertIn("AI 不得把推断升级为事实", policy)

    def test_06_governance_readme_routes_to_memory_first(self) -> None:
        readme = CHECK.read_text(CHECK.GOVERNANCE_README)
        self.assertIn("1. `project-memory/`", readme)
        self.assertIn("scripts/saee_project_memory_check.py", readme)

    def test_07_validator_command_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(MODULE_PATH)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("SAEE_PROJECT_MEMORY_CHECK: PASS", result.stdout)

    def test_08_v2_decisions_are_approved_design_directions(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "v2-transition-decisions.md")
        entries = CHECK.sections(text, "V2-F")
        self.assertEqual(set(entries), CHECK.REQUIRED_V2_DECISION_IDS)
        self.assertEqual(CHECK.validate_v2_transition_text(text), [])
        for section in entries.values():
            self.assertEqual(
                CHECK.field_value(section, "状态："),
                CHECK.APPROVED_DESIGN_DIRECTION,
            )
            self.assertEqual(
                CHECK.field_value(section, "Human Confirmation："), "CONFIRMED"
            )

    def test_09_v2_principles_have_approval_evidence(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "v2-transition-decisions.md")
        entries = CHECK.sections(text, "V2-P")
        self.assertEqual(set(entries), CHECK.REQUIRED_V2_PRINCIPLE_IDS)
        for section in entries.values():
            self.assertEqual(
                CHECK.field_value(section, "状态："),
                CHECK.APPROVED_DESIGN_DIRECTION,
            )
            self.assertIsNotNone(CHECK.field_value(section, "批准证据："))

    def test_10_active_authority_transition_is_rejected(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "v2-transition-decisions.md")
        mutated = text.replace(
            "状态：\n\n```text\nAPPROVED_DESIGN_DIRECTION",
            "状态：\n\n```text\nACTIVE_AUTHORITY",
            1,
        )
        errors = CHECK.validate_v2_transition_text(mutated)
        self.assertTrue(
            any("V2-F-001 status must be APPROVED_DESIGN_DIRECTION" in error for error in errors)
        )

    def test_11_unapproved_freeze_transition_is_rejected(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "v2-transition-decisions.md")
        mutated = text.replace(
            "状态：\n\n```text\nAPPROVED_DESIGN_DIRECTION",
            "状态：\n\n```text\nFROZEN",
            1,
        )
        errors = CHECK.validate_v2_transition_text(mutated)
        self.assertTrue(
            any("V2-F-001 status must be APPROVED_DESIGN_DIRECTION" in error for error in errors)
        )

    def test_12_q_v2_001_is_resolved_and_q_v2_002_remains_blocked(self) -> None:
        active_text = CHECK.read_text(CHECK.MEMORY_DIR / "active-questions.md")
        decision_text = CHECK.read_text(CHECK.MEMORY_DIR / "decision-log.md")
        entries = CHECK.sections(active_text, "Q-V2")
        self.assertEqual(set(entries), CHECK.REQUIRED_ACTIVE_V2_IDS)
        self.assertNotIn("Q-V2-001", entries)
        self.assertEqual(
            CHECK.field_value(entries["Q-V2-002"], "状态："), "BLOCKED"
        )
        self.assertEqual(
            CHECK.validate_v2_question_alignment(active_text, decision_text), []
        )

    def test_13_d_006_preserves_v2_resolution_evidence(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "decision-log.md")
        entries = CHECK.sections(text, "D")
        self.assertEqual(set(entries), CHECK.REQUIRED_DECISION_IDS)
        d_006 = entries["D-006"]
        self.assertIn("question_id=Q-V2-001", d_006)
        self.assertIn(
            "resolution_status=RESOLVED_BY_HUMAN_DESIGN_APPROVAL", d_006
        )
        self.assertIn("active_authority=false", d_006)

    def test_14_legacy_id_sets_remain_unchanged(self) -> None:
        frozen = CHECK.sections(
            CHECK.read_text(CHECK.MEMORY_DIR / "frozen-decisions.md"), "F"
        )
        rejected = CHECK.sections(
            CHECK.read_text(CHECK.MEMORY_DIR / "rejected-options.md"), "R"
        )
        self.assertEqual(set(frozen), CHECK.REQUIRED_FROZEN_IDS)
        self.assertEqual(set(rejected), CHECK.REQUIRED_REJECTED_IDS)

    def test_15_current_state_keeps_v1_1_active_and_v2_inactive(self) -> None:
        text = CHECK.read_text(CHECK.MEMORY_DIR / "current-state.md")
        self.assertIn(
            "current_authority=SAEE_Development_Constitution_v1.1", text
        )
        self.assertIn("v2_design_direction_status=APPROVED_DESIGN_DIRECTION", text)
        self.assertIn("v2_authority_status=INACTIVE", text)
        self.assertIn("g1_effective=false", text)
        self.assertIn("authority_switch_executed=false", text)


if __name__ == "__main__":
    unittest.main()
