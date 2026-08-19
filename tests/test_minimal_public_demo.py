import io
import unittest
from unittest.mock import patch

from public_abstraction.demo.minimal_public_demo import main


class TestMinimalPublicDemo(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main_execution(self, mock_stdout: io.StringIO) -> None:
        main()
        output = mock_stdout.getvalue()
        self.assertIn("SAEE_PUBLIC_ABSTRACTION_DEMO: PASS", output)
        self.assertIn(
            "summary={'regime': 'stable_regime', 'basin': 'stable_lineage_basin', 'count': 10}",
            output,
        )


if __name__ == "__main__":
    unittest.main()
