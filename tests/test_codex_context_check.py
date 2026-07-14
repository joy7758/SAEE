from __future__ import annotations

import unittest
from pathlib import Path

from scripts import codex_context_check


ROOT = Path(__file__).resolve().parents[1]


class CodexContextContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.context = (ROOT / ".codex/context.md").read_text(encoding="utf-8")

    def test_current_context_contract_passes(self) -> None:
        codex_context_check.validate_context_contract(self.context)

    def test_deprecated_identity_is_rejected(self) -> None:
        candidate = self.context + "\nAI agent long-term stability evaluation\n"
        with self.assertRaisesRegex(SystemExit, "deprecated identity phrase"):
            codex_context_check.validate_context_contract(candidate)

    def test_agent_readiness_cannot_replace_project_identity(self) -> None:
        candidate = self.context + "\nSAEE is an Agent Readiness Infrastructure\n"
        with self.assertRaisesRegex(SystemExit, "deprecated identity phrase"):
            codex_context_check.validate_context_contract(candidate)

    def test_duplicate_authority_claim_is_rejected(self) -> None:
        candidate = self.context + "\nDevelopment authority:\n"
        with self.assertRaisesRegex(SystemExit, "authority markers must occur exactly once"):
            codex_context_check.validate_context_contract(candidate)


if __name__ == "__main__":
    unittest.main()
