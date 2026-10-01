import unittest
from unittest.mock import patch, MagicMock
import sys
from io import StringIO
from benchmark_evidence_adequacy import benchmark

class TestBenchmarkEvidenceAdequacy(unittest.TestCase):
    @patch("benchmark_evidence_adequacy._profile_valid")
    @patch("benchmark_evidence_adequacy._load_profile")
    @patch("benchmark_evidence_adequacy.time.time")
    @patch("sys.stdout", new_callable=StringIO)
    def test_benchmark_completes_and_outputs_correctly(
        self, mock_stdout, mock_time, mock_load_profile, mock_profile_valid
    ) -> None:
        """Test that the benchmark script runs without error and produces expected output."""
        # Mock time.time() to return a predictable start and end time
        mock_time.side_effect = [100.0, 105.0]

        # Mock the profile loading
        mock_profile = MagicMock()
        mock_load_profile.return_value = mock_profile

        # Run the benchmark
        benchmark()

        # Verify the target functions were called correctly
        mock_load_profile.assert_called_once_with("RESOURCE_AUTHENTICITY")
        self.assertEqual(mock_profile_valid.call_count, 1000)
        mock_profile_valid.assert_called_with(mock_profile)

        # Verify the output
        output = mock_stdout.getvalue()
        self.assertIn("Time for 1000 iterations: 5.0000 seconds", output)

if __name__ == "__main__":
    unittest.main()
