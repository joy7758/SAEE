import unittest
from unittest.mock import patch, MagicMock

import benchmark_evidence_adequacy

class BenchmarkEvidenceAdequacyTest(unittest.TestCase):
    @patch("benchmark_evidence_adequacy._profile_valid")
    @patch("benchmark_evidence_adequacy._load_profile")
    def test_benchmark_runs_successfully(
        self,
        mock_load_profile: MagicMock,
        mock_profile_valid: MagicMock
    ) -> None:
        # Arrange
        mock_profile = MagicMock()
        mock_load_profile.return_value = mock_profile

        # Act
        benchmark_evidence_adequacy.benchmark()

        # Assert
        mock_load_profile.assert_called_once_with("RESOURCE_AUTHENTICITY")
        self.assertEqual(mock_profile_valid.call_count, 1000)
        mock_profile_valid.assert_called_with(mock_profile)

if __name__ == "__main__":
    unittest.main()
