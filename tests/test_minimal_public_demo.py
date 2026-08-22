import unittest
import io
from unittest.mock import patch
from public_abstraction.demo.minimal_public_demo import main

class MinimalPublicDemoTest(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_main(self, mock_stdout: io.StringIO) -> None:
        main()
        output = mock_stdout.getvalue()
        self.assertIn("SAEE_PUBLIC_ABSTRACTION_DEMO: PASS", output)
        self.assertIn("summary=", output)

if __name__ == "__main__":
    unittest.main()
